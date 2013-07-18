from __future__ import absolute_import

import csv
import datetime
import hashlib
from itertools import izip
import logging
from operator import itemgetter
import string
import struct
import urllib2

from django.db import models, transaction
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.defaultfilters import slugify, truncatechars

from dateutil.parser import parse
import fiona
from suds.client import Client
import jsonfield
import xlrd
from model_utils.managers import InheritanceManager
from pyproj import Proj, transform

from lock_manager import Lock, LockError

from .exceptions import Http400
from .job_processing import Job
from .literals import (DEFAULT_LIMIT, DEFAULT_SHEET, DATA_TYPE_CHOICES, DATA_TYPE_FUNCTIONS,
    DATA_TYPE_NUMBER, JOIN_TYPE_AND, JOIN_TYPE_CHOICES, JOIN_TYPE_OR, LQL_DELIMITER,
    RENDERER_BROWSEABLE_API, RENDERER_JSON, RENDERER_XML, RENDERER_YAML, RENDERER_LEAFLET)
from .utils import parse_range

HASH_FUNCTION = lambda x: hashlib.sha256(x).hexdigest()
logger = logging.getLogger(__name__)


class Source(models.Model):
    renderers = (RENDERER_BROWSEABLE_API, RENDERER_JSON, RENDERER_XML, RENDERER_YAML,
    RENDERER_LEAFLET)

    name = models.CharField(max_length=128, verbose_name=_('name'), help_text=('Human readable name for this source.'))
    slug = models.SlugField(blank=True, max_length=48, verbose_name=_('slug'), help_text=('URL friendly description of this source. If none is specified the name will be used.'))
    description = models.TextField(blank=True, verbose_name=_('description'))

    objects = InheritanceManager()

    @staticmethod
    def add_row_id(row, id):
        return dict(row, **{'_id': id})

    def get_type(self):
        return self.__class__.source_type

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Source, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('source-detail', [self.pk])

    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')


class SourceWS(Source):
    source_type = _('SOAP web service')
    wsdl_url = models.URLField(verbose_name=_('WSDL URL'))
    endpoint = models.CharField(max_length=64, verbose_name=_('endpoint'), help_text=_('Endpoint, function or method to call.'))

    def get_parameters(self, parameters=None):
        result = parameters.copy()

        for argument in self.wsargument_set.all():
            if argument.name not in result:
                if argument.default:
                    result[argument.name] = argument.default

        return result

    def get_one(self, id, timestamp=None, parameters=None):
        # ID are all base 1
        if id == 0:
            raise Http400('Invalid ID; IDs are base 1')

        return self.get_all(timestamp, parameters)[id-1]

    def get_all(self, timestamp=None, parameters=None):
        if not parameters:
            parameters = {}

        client = Client(self.wsdl_url)

        result = []
        try:
            row_id = 1
            for data in getattr(client.service, self.endpoint)(**self.get_parameters(parameters)):
                entry = {'_id': row_id}
                for field in self.wsresultfield_set.all():
                    entry[field.name] = getattr(data, field.name, field.default)

                result.append(entry)
                row_id += 1
        except IndexError:
            result = []

        return result

    class Meta:
        verbose_name = _('web service source')
        verbose_name_plural = _('web service sources')


class WSArgument(models.Model):
    source_ws = models.ForeignKey(SourceWS, verbose_name=_('web service source'))
    name = models.CharField(max_length=32, verbose_name=_('name'))
    default = models.CharField(max_length=32, blank=True, verbose_name=_('default'))

    class Meta:
        verbose_name = _('argument')
        verbose_name_plural = _('arguments')


class WSResultField(models.Model):
    source_ws = models.ForeignKey(SourceWS, verbose_name=_('web service source'))
    name = models.CharField(max_length=32, verbose_name=_('name'))
    default = models.CharField(max_length=32, blank=True, verbose_name=_('default'))

    class Meta:
        verbose_name = _('result field')
        verbose_name_plural = _('result fields')


class SourceFileBased(models.Model):
    limit = models.PositiveIntegerField(default=DEFAULT_LIMIT, verbose_name=_('limit'), help_text=_('Maximum number of items to show when all items are requested.'))
    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=_('Location to a file in the filesystem.'))
    file = models.FileField(blank=True, null=True, upload_to='spreadsheets', verbose_name=_('uploaded file'))
    url = models.URLField(blank=True, verbose_name=_('URL'), help_text=_('Import a file from an URL.'))

    def get_stream_type(self):
        if self.file:
            return _('Uploaded file')
        elif self.path:
            return _('Filesystem path')
        elif self.url:
            return _('URL')
        else:
            return _('None')
    get_stream_type.short_description = 'stream type'

    def clear_versions(self):
        for version in self.versions.all():
            version.delete()

    def check_file(self):
        try:
            lock_id = u'check_file-%d' % self.pk
            logger.debug('trying to acquire lock: %s' % lock_id)
            lock = Lock.acquire_lock(lock_id, 60)
            logger.debug('acquired lock: %s' % lock_id)
            try:
                self._check_file()
            except Exception as exception:
                logger.debug('unhandled exception: %s' % exception)
                raise
            finally:
                lock.release()
        except LockError:
            logger.debug('unable to obtain lock')
            pass

    def _check_file(self):
        if self.path:
            try:
                with open(self.path) as handle:
                    new_hash = HASH_FUNCTION(handle.read())
            except IOError as exception:
                logger.error('Unable to open file for source id: %s ;%s' % (self.id, exception))
                raise
        elif self.file:
            new_hash = HASH_FUNCTION(self.file.read())
            self.file.seek(0)
        elif self.url:
            handle = urllib2.urlopen(self.url)
            new_hash = HASH_FUNCTION(handle.read())
            handle.close()

        logger.debug('new_hash: %s' % new_hash)

        try:
            source_data_version = self.versions.get(checksum=new_hash)
        except SourceDataVersion.DoesNotExist:
            source_data_version = SourceDataVersion.objects.create(source=self, checksum=new_hash)
            job = Job(target=self.import_data, args=(source_data_version,))
            job.submit()
            logger.debug('launching import job: %s' % job)
        else:
            source_data_version.active = True
            source_data_version.save()

    def analyze_request(self, parameters=None):
        kwargs = {}
        if not parameters:
            parameters = {}
        else:
            for i in parameters:
                if not i.startswith('_'):
                    kwargs[i] = parameters[i]

        timestamp = parameters.get('_timestamp', None)

        return timestamp, parameters

    def get_one(self, id, parameters=None):
        # ID are all base 1
        if id == 0:
            raise Http400('Invalid ID; IDs are base 1')

        # TODO: return a proper response when no sourcedataversion is found
        timestamp, parameters = self.analyze_request(parameters)
        if timestamp:
            source_data_version = self.versions.get(timestamp=timestamp)
        else:
            source_data_version = self.versions.get(active=True)

        try:
            return SourceData.objects.get(source_data_version=source_data_version, row_id=id).row
        except SourceData.DoesNotExist:
            raise Http404

    def get_all(self, parameters=None):
        timestamp, parameters = self.analyze_request(parameters)

        try:
            if timestamp:
                source_data_version = self.versions.get(timestamp=timestamp)
            else:
                source_data_version = self.versions.get(active=True)
        except SourceDataVersion.DoesNotExist:
            return []

        queryset = SourceData.objects.filter(source_data_version=source_data_version)

        if not parameters:
            parameters = {}

        post_filters = []
        join_type = JOIN_TYPE_AND
        DOUBLE_DELIMITER = LQL_DELIMITER + LQL_DELIMITER
        fields_to_return = []
        get_all_fields = True

        for parameter, value in parameters.items():
            logger.debug('parameter: %s' % parameter)
            logger.debug('value: %s' % value)
            valid = True
            # If value is quoted is a string else try to see if it is a number
            # TODO: clean up this mess!
            # Only interpret values for filters
            try:
                if value[0] == '"' and value[-1] == '"':
                    # Strip quotes
                    value = unicode(value[1:-1])
                else:
                    if ',' in value:
                        result = []
                        value = value.split(',')
                        # List
                        for n in value:
                            if n[0] == '"' and n[-1] == '"':
                                # Strip quotes
                                result.append(unicode(n[1:-1]))
                            else:
                                try:
                                    result.append(DATA_TYPE_FUNCTIONS[DATA_TYPE_NUMBER](n))
                                except ValueError:
                                    raise Http400('Invalid value')

                        value = result
                    else:
                        try:
                            value = DATA_TYPE_FUNCTIONS[DATA_TYPE_NUMBER](value)
                        except ValueError:
                            raise Http400('Invalid value')
            except IndexError:
                raise Http400('Malformed query')

            if valid:
                if not parameter.startswith(LQL_DELIMITER):
                    if DOUBLE_DELIMITER not in parameter:
                        post_filters.append({'key': parameter, 'operation': 'equals', 'value': value})
                    else:
                        key, operation = parameter.split(DOUBLE_DELIMITER)
                        post_filters.append({'key': key, 'operation': operation, 'value': value})
                else:
                    # Determine query join type
                    if parameter == LQL_DELIMITER + 'join':
                        if value.upper() == 'OR':
                            join_type = JOIN_TYPE_OR
                    # Determine fields to return
                    elif parameter == LQL_DELIMITER + 'fields':
                        try:
                            fields_to_return = value.split(',')
                        except AttributeError:
                            # Already a list
                            fields_to_return = value

                        get_all_fields = False

        logger.debug('join type: %s' % JOIN_TYPE_CHOICES[join_type])
        kwargs = {}
        query_results = set()
        if post_filters:
            for post_filter in post_filters:
                filter_results = []
                for row_id, item in enumerate(queryset):
                    try:
                        real_value = item.row
                        for part in post_filter['key'].split('.'):
                            try:
                                real_value = real_value[part]
                            except KeyError:
                                raise Http400('Invalid element: %s' % post_filter['key'])
                    except AttributeError:
                        # A dotted attribute is not found
                        raise Http400('Invalid element: %s' % post_filter['key'])
                    else:
                        if post_filter['operation'] == 'icontains':
                            if post_filter['value'].upper() in real_value.upper():
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'contains':
                            if post_filter['value'] in real_value:
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'startswith':
                            if real_value.startswith(post_filter['value']):
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'istartswith':
                            if real_value.upper().startswith(post_filter['value'].upper()):
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'endswith':
                            if real_value.endswith(post_filter['value']):
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'iendswith':
                            if real_value.upper().endswith(post_filter['value'].upper()):
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'in':
                            try:
                                if real_value in post_filter['value']:
                                    filter_results.append(row_id)
                            except TypeError:
                                # Asking for in, with a non list value
                                if real_value in [post_filter['value']]:
                                    filter_results.append(row_id)
                        elif post_filter['operation'] == 'equals':
                            if post_filter['value'] == real_value:
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'lt':
                            if real_value < post_filter['value']:
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'lte':
                            if real_value <= post_filter['value']:
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'gt':
                            if real_value > post_filter['value']:
                                filter_results.append(row_id)
                        elif post_filter['operation'] == 'gte':
                            if real_value >= post_filter['value']:
                                filter_results.append(row_id)

                        # Date

                        elif post_filter['operation'] == 'year':
                            try:
                                if parse(real_value).year == post_filter['value']:
                                    filter_results.append(row_id)
                            except (ValueError, AttributeError):
                                raise Http400('field: %s, is not a date or time field' % post_filter['key'])
                        elif post_filter['operation'] == 'month':
                            try:
                                if parse(real_value).month == post_filter['value']:
                                    filter_results.append(row_id)
                            except (ValueError, AttributeError):
                                raise Http400('field: %s, is not a date or time field' % post_filter['key'])

                if query_results:
                    if join_type == JOIN_TYPE_AND:
                        query_results &= set(filter_results)
                    else:
                        query_results |= set(filter_results)
                else:
                    query_results = set(filter_results)

        if get_all_fields:
            fields_lambda = lambda x: x
        else:
            fields_lambda = self.__class__.make_fields_filter(fields_to_return)

        if post_filters:
            if len(query_results) == 1:
                # Special case because itemgetter doesn't returns a list but a value
                return (fields_lambda(item.row) for item in [itemgetter(*list(query_results))(queryset)])
            elif len(query_results) == 0:
                return []
            else:
                return (fields_lambda(item.row) for item in itemgetter(*list(query_results))(queryset)[0:self.limit])
        else:
            return (fields_lambda(item.row) for item in queryset[0:self.limit])

    class Meta:
        abstract = True

    @staticmethod
    def make_fields_filter(fields_to_return):
        """
        Fabricate a function tailored made to return a number of fields
        for each row.
        """
        # TODO: support multilevel dot '.', and index '[]' notation
        if len(fields_to_return) == 1:
            # Special because itemgetter with a single element doesn't return a list
            field_extract_lambda = lambda x: [itemgetter(*fields_to_return)(x)]
        else:
            field_extract_lambda = lambda x: itemgetter(*fields_to_return)(x)

        def _function(row):
            try:
                return dict(izip(fields_to_return, field_extract_lambda(row)))
            except KeyError as exception:
                raise Http400('Could not find a field named in the current row: %s' % exception)
        return _function


class SourceTabularBased(models.Model):
    import_rows = models.TextField(blank=True, null=True, verbose_name=_('import rows'), help_text=_('Range of rows to import can use dashes to specify a continuous range or commas to specify individual rows or ranges. Leave blank to import all rows.'))

    def get_column_names(self):
        if self.columns.count():
            return self.columns.all().values_list('name', flat=True)
        else:
            return string.ascii_uppercase

    class Meta:
        abstract = True


class SourceCSV(Source, SourceFileBased, SourceTabularBased):
    source_type = _('CSV file')

    delimiter = models.CharField(blank=True, max_length=1, default=',', verbose_name=_('delimiter'))
    quote_character = models.CharField(blank=True, max_length=1, verbose_name=_('quote character'))

    def _get_items(self, file_handle):
        column_names = self.get_column_names()

        functions = ColumnBase.get_functions_map(self.columns.all())

        kwargs = {}
        if self.delimiter:
            kwargs['delimiter'] = str(self.delimiter)
        if self.quote_character:
            kwargs['quotechar'] = str(self.quote_character)

        reader = csv.reader(file_handle, **kwargs)

        logger.debug('column_names: %s' % column_names)

        if self.import_rows:
            parsed_range = map(lambda x: x-1, parse_range(self.import_rows))
        else:
            parsed_range = None

        logger.debug('parsed_range: %s' % parsed_range)

        for i, row in enumerate(reader):
            if parsed_range and i in parsed_range:
                yield dict(zip(column_names, ColumnBase.zip_functions(functions, row)))
            elif not parsed_range:
                yield dict(zip(column_names, ColumnBase.zip_functions(functions, row)))

    @transaction.commit_on_success
    def import_data(self, source_data_version):
        # Reload data in case this is executed in another thread
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        if self.path:
            file_handle = open(self.path)
        elif self.file:
            file_handle = self.file
        elif self.url:
            file_handle = urllib2.urlopen(self.url)

        logger.debug('file_handle: %s' % file_handle)

        row_id = 1
        for row in self._get_items(file_handle):
            SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=Source.add_row_id(row, row_id))
            row_id = row_id + 1

        file_handle.close()

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

    class Meta:
        verbose_name = _('CSV source')
        verbose_name_plural = _('CSV sources')


class SourceFixedWidth(Source, SourceFileBased, SourceTabularBased):
    source_type = _('Fixed width column file')

    def _get_items(self):
        column_names = self.get_column_names()
        column_widths = self.columns.all().values_list('size', flat=True)

        fmtstring = ''.join('%ds' % f for f in map(int, column_widths))
        parse = struct.Struct(fmtstring).unpack_from

        functions = ColumnBase.get_functions_map(self.columns.all())

        if self.import_rows:
            parsed_range = map(lambda x: x-1, parse_range(self.import_rows))
        else:
            parsed_range = None

        for i, row in enumerate(self._file_handle):
            if parsed_range:
                if i in parsed_range:
                    yield dict(zip(column_names, ColumnBase.zip_functions(functions, parse(row))))
            else:
                yield dict(zip(column_names, ColumnBase.zip_functions(functions, parse(row))))

    @transaction.commit_on_success
    def import_data(self, source_data_version):
        # Reload data in case this is executed in another thread
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        if self.path:
            self._file_handle = open(self.path)
        elif self.file:
            self._file_handle = self.file
        elif self.url:
            self._file_handle = urllib2.urlopen(self.url)

        row_id = 1
        for row in self._get_items():
            SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=Source.add_row_id(row, row_id))
            row_id = row_id + 1

        self._file_handle.close()

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

        if self._file_handle:
            self._file_handle.close()

    class Meta:
        verbose_name = _('Fixed width source')
        verbose_name_plural = _('Fixed width sources')


class SourceSpreadsheet(Source, SourceFileBased, SourceTabularBased):
    source_type = _('Spreadsheet file')

    sheet = models.CharField(max_length=32, default=DEFAULT_SHEET, verbose_name=_('sheet'), help_text=('Worksheet of the spreadsheet file to use.'))

    def _convert_value(self, item):
        """
        Handle different value types for XLS. Item is a cell object.
        """
        # Thx to Augusto C Men to point fast solution for XLS/XLSX dates
        if item.ctype == 3: #XL_CELL_DATE:
            try:
                return datetime.datetime(*xlrd.xldate_as_tuple(item.value, self._book.datemode))
            except ValueError:
                # TODO: make toggable
                # Invalid date
                return item.value

        if item.ctype == 2: #XL_CELL_NUMBER:
            if item.value % 1 == 0:  # integers
                return int(item.value)
            else:
                return item.value

        return item.value

    def _get_items(self):
        column_names = self.get_column_names()

        logger.debug('column_names: %s' % column_names)

        if self.import_rows:
            parsed_range = map(lambda x: x-1, parse_range(self.import_rows))
        else:
            parsed_range = xrange(0, self._sheet.nrows)

        #if self.name_row:
        #    parsed_range = (i for i in set(parsed_range) - set([self.name_row - 1]))

        for i in parsed_range:
            yield dict(zip(column_names, [self._convert_value(cell) for cell in self._sheet.row(i)]))

    @transaction.commit_on_success
    def import_data(self, source_data_version):
        # Reload data in case this is executed in another thread
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        logger.debug('opening workbook')
        if self.path:
            self._book = xlrd.open_workbook(self.path)
            file_handle = None
        elif self.file:
            file_handle = self.file
            self._book = xlrd.open_workbook(file_contents=file_handle.read())
        elif self.url:
            file_handle = urllib2.urlopen(self.url)
            self._book = xlrd.open_workbook(file_contents=file_handle.read())

        logger.debug('opening sheet: %s' % self.sheet)
        try:
            self._sheet = self._book.sheet_by_name(self.sheet)
        except xlrd.XLRDError:
            self._sheet = self._book.sheet_by_index(int(self.sheet))

        logger.debug('importing rows')
        row_id = 1
        for row in self._get_items():
            SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=Source.add_row_id(row, row_id))
            row_id = row_id + 1

        if file_handle:
            file_handle.close()

        logger.debug('finished importing rows')

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()
        logger.debug('exiting')

        if file_handle:
            file_handle.close()

    class Meta:
        verbose_name = _('spreadsheet source')
        verbose_name_plural = _('spreadsheet sources')


class SourceShape(Source, SourceFileBased):
    source_type = _('Shapefile')
    renderers = (RENDERER_JSON, RENDERER_LEAFLET)
    popup_template = models.TextField(blank=True, verbose_name=_('popup template'), help_text=_('Template for rendering the features when displaying them on a map.'))
    new_projection = models.CharField(max_length=32, blank=True, verbose_name=_('new projection'), help_text=_('Specify the EPSG number of the new projection to transform the geometries, leave blank otherwise.'))

    @staticmethod
    def transform(old_projection, new_projection, geometry):
        # TODO: Support all types
        # Point (A single (x, y) tuple) - DONE
        # LineString (A list of (x, y) tuple vertices) - DONE
        # Polygon (A list of rings (each a list of (x, y) tuples)) - DONE
        # MultiPoint (A list of points (each a single (x, y) tuple))
        # MultiLineString (A list of lines (each a list of (x, y) tuples))
        # MultiPolygon (A list of polygons (see above))
        # GeometryCollection
        # 3D Point
        # 3D LineString
        # 3D Polygon
        # 3D MultiPoint
        # 3D MultiLineString
        # 3D MultiPolygon
        # 3D GeometryCollection

        if geometry['type'] == 'Point':
            return transform(old_projection, new_projection, *geometry['coordinates'])
        elif geometry['type'] == 'LineString':
            result = []
            for x, y in geometry['coordinates']:
                result.append(transform(old_projection, new_projection, x, y))
            return result
        elif geometry['type'] == 'Polygon':
            result = []
            for ring in geometry['coordinates']:
                element_result = []
                for x, y in ring:
                    element_result.append(transform(old_projection, new_projection, x, y))
                result.append(element_result)
            return result
        else:
            # Unsuported geometry type, return coordinates as is
            return geometry['coordinates']

    @transaction.commit_on_success
    def import_data(self, source_data_version):
        # Reload data in case this is executed in another thread
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        if self.path:
            self._file_handle = open(self.path)
        elif self.file:
            self._file_handle = self.file
        elif self.url:
            self._file_handle = urllib2.urlopen(self.url)

        # TODO: only works with paths, fix

        with fiona.collection(self.path, 'r') as source:
            source_data_version.metadata = source.crs
            if self.new_projection:
                new_projection = Proj(init='epsg:%s' % self.new_projection)
                old_projection = Proj(**source.crs)
            else:
                new_projection = False

            row_id = 1
            for feature in source:
                feature['properties'] = Source.add_row_id(self.apply_datatypes(feature.get('properties', {})), row_id)
                if new_projection:
                    feature['geometry']['coordinates'] = SourceShape.transform(old_projection, new_projection, feature['geometry'])
                SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=feature)
                row_id = row_id + 1

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

        if self._file_handle:
            self._file_handle.close()

    def get_functions_map(self):
        return dict([(column, DATA_TYPE_FUNCTIONS[data_type]) for column, data_type in self.columns.values_list('name', 'data_type')])

    def apply_datatypes(self, properties):
        functions_map = self.get_functions_map()
        result = {}

        for key, value in properties.items():
            if key in functions_map:
                result[key] = functions_map[key](value)
            else:
                result[key] = value

        return result
        #return [functions_map(key)(value) for key, value in properties.items() if key in functions_map else value]

    class Meta:
        verbose_name = _('shape source')
        verbose_name_plural = _('shape sources')


class SourceDataVersion(models.Model):
    source = models.ForeignKey(Source, verbose_name=_('source'), related_name='versions')
    datetime = models.DateTimeField(default=lambda: now())
    timestamp = models.CharField(blank=True, max_length=20, verbose_name=_('timestamp'))
    # MySQL doesn't like BLOB/TEXT columns used in key specification without a key length; DatabaseError 1170
    checksum = models.CharField(max_length=64, verbose_name=_('checksum'))
    ready = models.BooleanField(default=False, verbose_name=_('ready'))
    active = models.BooleanField(default=False, verbose_name=_('active'))
    metadata = jsonfield.JSONField(blank=True, verbose_name=_('metadata'))

    def save(self, *args, **kwargs):
        self.timestamp = datetime.datetime.strftime(self.datetime, '%Y%m%d%H%M%S%f')
        if self.active:
            SourceDataVersion.objects.filter(source=self.source).update(active=False)
        super(self.__class__, self).save(*args, **kwargs)

    def truncated_checksum(self):
        return truncatechars(self.checksum, 10)

    class Meta:
        verbose_name = _('source data version')
        verbose_name_plural = _('sources data versions')
        unique_together = (('source', 'datetime'), ('source', 'timestamp'), ('source', 'checksum'))


class SourceData(models.Model):
    source_data_version = models.ForeignKey(SourceDataVersion, verbose_name=_('source data version'), related_name='data')
    row = jsonfield.JSONField(verbose_name=_('row'))
    row_id = models.PositiveIntegerField(verbose_name=_('row id'), db_index=True)

    def __unicode__(self):
        return unicode(self.row)

    class Meta:
        verbose_name = _('source data')
        verbose_name_plural = _('sources data')


class ColumnBase(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('name'))
    default = models.CharField(max_length=32, blank=True, verbose_name=_('default'))

    @staticmethod
    # TODO: rename to get_funtions_list
    def get_functions_map(columns):
        return [DATA_TYPE_FUNCTIONS[i] for i in columns.values_list('data_type', flat=True)]

    @staticmethod
    def zip_functions(functions, values):
        return [x(y) for x, y in zip(functions, values)]

    class Meta:
        abstract = True


class CSVColumn(ColumnBase):
    source = models.ForeignKey(SourceCSV, verbose_name=_('CSV source'), related_name='columns')
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))

    class Meta:
        verbose_name = _('CSV column')
        verbose_name_plural = _('CSV columns')


class FixedWidthColumn(ColumnBase):
    source = models.ForeignKey(SourceFixedWidth, verbose_name=_('fixed width source'), related_name='columns')
    size = models.PositiveIntegerField(verbose_name=_('size'))
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))

    class Meta:
        verbose_name = _('fixed width column')
        verbose_name_plural = _('fixed width columns')


class SpreadsheetColumn(ColumnBase):
    source = models.ForeignKey(SourceSpreadsheet, verbose_name=_('spreadsheet source'), related_name='columns')

    class Meta:
        verbose_name = _('spreadsheet column')
        verbose_name_plural = _('spreadsheet columns')


class ShapefileColumn(ColumnBase):
    source = models.ForeignKey(SourceShape, verbose_name=_('shapefile source'), related_name='columns')
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))

    class Meta:
        verbose_name = _('shapefile column')
        verbose_name_plural = _('shapefile columns')

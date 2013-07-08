from __future__ import absolute_import

import csv
import datetime
import hashlib
import json
import logging
import string
import struct
import re
import urllib2

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.defaultfilters import slugify

import fiona
from suds.client import Client
import jsonfield
import xlrd
from model_utils.managers import InheritanceManager

from lock_manager import Lock, LockError

from .exceptions import Http400
from .job_processing import Job
from .literals import DEFAULT_LIMIT, DEFAULT_SHEET
from .utils import parse_range

HASH_FUNCTION = lambda x: hashlib.sha256(x).hexdigest()
logger = logging.getLogger(__name__)


class Source(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('name'), help_text=('Human readable name for this source.'))
    slug = models.SlugField(blank=True, max_length=48, verbose_name=_('slug'), help_text=('URL friendly description of this source. If none is specified the name will be used.'))
    description = models.TextField(blank=True, verbose_name=_('description'))

    objects = InheritanceManager()

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
            raise Http404  # TODO: may be return HTTP INVALID REQUEST?

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
            source_data_version = self.sourcedataversion_set.get(checksum=new_hash)
        except SourceDataVersion.DoesNotExist:
            source_data_version = SourceDataVersion.objects.create(source=self, checksum=new_hash)
            job = Job(target=self.import_data, args=(source_data_version,))
            job.submit()
            logger.debug('launching import job: %s' % job)
        else:
            source_data_version.active = True
            source_data_version.save()

    def analyze_request(self, parameters):
        kwargs = {}
        for i in parameters:
            if not i.startswith('_'):
                kwargs[i] = parameters[i]

        timestamp = parameters.get('_timestamp', None)

        return timestamp, parameters

    def get_one(self, id, parameters=None):
        # TODO: return a proper response when no sourcedataversion is found
        timestamp, parameters = self.analyze_request(parameters)
        if timestamp:
            source_data_version = self.sourcedataversion_set.get(timestamp=timestamp)
        else:
            source_data_version = self.sourcedataversion_set.get(active=True)

        instance = SourceData.objects.get(source_data_version=source_data_version, row_id=id)
        return dict(instance.row, **{'_id': instance.row_id})

    def get_all(self, parameters=None):
        timestamp, parameters = self.analyze_request(parameters)

        try:
            if timestamp:
                source_data_version = self.sourcedataversion_set.get(timestamp=timestamp)
            else:
                source_data_version = self.sourcedataversion_set.get(active=True)
        except SourceDataVersion.DoesNotExist:
            return []

        queryset = SourceData.objects.filter(source_data_version=source_data_version)

        if not parameters:
            parameters = {}

        post_filters = []

        for parameter, value in parameters.items():
            valid = True
            # If value is quoted is a string else try to see if it is a number
            try:
                if value[0] == '"' and value[-1] == '"':
                    # Strip quotes
                    value = str(value[1:-1])
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        valid = False
            except IndexError:
                raise Http400('Malformed query')

            if valid:
                if not parameter.startswith('_'):
                    if '__' not in parameter:
                        post_filters.append({'key': parameter, 'operation': 'equals', 'value': value})
                    else:
                        key, operation = parameter.split('__')
                        post_filters.append({'key': key, 'operation': operation, 'value': value})

        kwargs = {}
        if post_filters:
            results = []
            for post_filter in post_filters:
                for item in queryset:
                    try:
                        real_value = item.row
                        for part in post_filter['key'].split('.'):
                            real_value = real_value.get(part)
                            if not real_value:
                                raise Http400('Invalid element: %s' % post_filter['key'])
                    except AttributeError:
                        # A dotted attribute is not found
                        raise Http400('Invalid element: %s' % post_filter['key'])
                    else:
                        if post_filter['operation'] == 'icontains':
                            if post_filter['value'].upper() in real_value.upper():
                                results.append(item.pk)
                        elif post_filter['operation'] == 'contains':
                            if post_filter['value'] in real_value:
                                results.append(item.pk)
                        elif post_filter['operation'] == 'equals':
                            if post_filter['value'] == real_value:
                                results.append(item.pk)
                        elif post_filter['operation'] == 'lt':
                            if real_value < post_filter['value']:
                                results.append(item.pk)
                        elif post_filter['operation'] == 'lte':
                            if real_value <= post_filter['value']:
                                results.append(item.pk)
                        elif post_filter['operation'] == 'gt':
                            if real_value > post_filter['value']:
                                results.append(item.pk)
                        elif post_filter['operation'] == 'gte':
                            if real_value >= post_filter['value']:
                                results.append(item.pk)

            # TODO: convert to Q objects
            # TODO: query terms are inclusive, move to chain filtering
            # TODO: implement _join=OR modifier
            kwargs['pk__in'] = results

        if kwargs:
            queryset = queryset.filter(**kwargs)

        return [dict(item.row, **{'_id': item.row_id}) for item in queryset[0:self.limit]]

    class Meta:
        abstract = True


class SourceTabularBased(models.Model):
    column_names = models.TextField(blank=True, verbose_name=_('column names'), help_text=_('Specify the column names to use. Enclose names with quotes and separate with commas.'))
    name_row = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('name row'), help_text=_('Use the values of this row as the column names. A typical value is 1, meaning the first row. Leave blank to disable.'))
    import_rows = models.TextField(blank=True, null=True, verbose_name=_('import rows'), help_text=_('Range of rows to import can use dashes to specify a continuous range or commas to specify individual rows or ranges. Leave blank to import all rows.'))

    def get_column_names(self):
        """
        Split column names by comma but obeying quoted names
        """
        if self.column_names:
            pattern = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
            return map(lambda x: x.replace('"', '').replace("'", '').strip(), pattern.split(self.column_names)[1::2])
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

        kwargs = {}
        if self.delimiter:
            kwargs['delimiter'] = str(self.delimiter)
        if self.quote_character:
            kwargs['quotechar'] = str(self.quote_character)

        reader = csv.reader(file_handle, **kwargs)

        if self.name_row:
            for i, row in enumerate(reader):
                if i == self.name_row - 1:
                    column_names = row
                    file_handle.seek(0)
                    break

        logger.debug('column_names: %s' % column_names)

        if self.import_rows:
            parsed_range = map(lambda x: x-1, parse_range(self.import_rows))
        else:
            parsed_range = None

        logger.debug('parsed_range: %s' % parsed_range)

        for i, row in enumerate(reader):
            if self.name_row and i == self.name_row - 1:
                pass
            else:
                if parsed_range and i in parsed_range:
                    yield dict(zip(column_names, row))
                elif not parsed_range:
                    yield dict(zip(column_names, row))

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
            SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=row)
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

    column_widths = models.TextField(blank=True, null=True, verbose_name=_('column widths'), help_text=_('The column widths separated by a comma.'))

    def _get_items(self):
        column_names = self.get_column_names()

        fmtstring = ''.join('%ds' % f for f in map(int, self.column_widths.split(',')))
        parse = struct.Struct(fmtstring).unpack_from

        if self.name_row:
            for i, row in enumerate(self._file_handle):
                if i == self.name_row - 1:
                    column_names = map(string.strip, parse(row))
                    self._file_handle.seek(0)
                    break

        if self.import_rows:
            parsed_range = map(lambda x: x-1, parse_range(self.import_rows))
        else:
            parsed_range = None

        for i, row in enumerate(self._file_handle):
            if self.name_row and i == self.name_row - 1:
                pass
            else:
                if parsed_range and i in parsed_range:
                    yield dict(zip(column_names, map(string.strip, parse(row))))
                elif not parsed_range:
                    yield dict(zip(column_names, map(string.strip, parse(row))))


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
            SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=row)
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

        if self.name_row:
            column_names = [cell.value for cell in self._sheet.row(self.name_row - 1)]

        logger.debug('column_names: %s' % column_names)

        if self.import_rows:
            parsed_range = map(lambda x: x-1, parse_range(self.import_rows))
        else:
            parsed_range = xrange(0, self._sheet.nrows)

        if self.name_row:
            parsed_range = (i for i in set(parsed_range) - set([self.name_row - 1]))

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
            SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=row)
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
        # TODO: store crs in a special record?

        #crs = None
        with fiona.collection(self.path, 'r') as source:
            row_id = 1
            for feature in source:
                 SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=json.dumps(feature))
                 row_id = row_id + 1

            #crs = " ".join("+%s=%s" % (k,v) for k,v in source.crs.items())

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

        if self._file_handle:
            self._file_handle.close()

    class Meta:
        verbose_name = _('shape source')
        verbose_name_plural = _('shape sources')


class SourceDataVersion(models.Model):
    source = models.ForeignKey(Source, verbose_name=_('source'))
    datetime = models.DateTimeField(default=lambda: now())
    timestamp = models.CharField(blank=True, max_length=20, verbose_name=_('timestamp'))
    checksum = models.TextField(verbose_name=_('checksum'))
    ready = models.BooleanField(default=False, verbose_name=_('ready'))
    active = models.BooleanField(default=False, verbose_name=_('active'))

    def save(self, *args, **kwargs):
        self.timestamp = datetime.datetime.strftime(self.datetime, '%Y%m%d%H%M%S%f')
        if self.active:
            SourceDataVersion.objects.filter(source=self.source).update(active=False)
        super(self.__class__, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('source data version')
        verbose_name_plural = _('sources data versions')
        unique_together = (('source', 'datetime'), ('source', 'timestamp'), ('source', 'checksum'))


class SourceData(models.Model):
    source_data_version = models.ForeignKey(SourceDataVersion, verbose_name=_('source data version'))
    row = jsonfield.JSONField(verbose_name=_('row'))
    row_id = models.PositiveIntegerField(verbose_name=_('row id'), db_index=True)

    def __unicode__(self):
        return unicode(self.row)

    class Meta:
        verbose_name = _('source data')
        verbose_name_plural = _('sources data')


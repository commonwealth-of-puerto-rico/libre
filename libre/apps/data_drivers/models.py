from __future__ import absolute_import

import datetime
from itertools import islice
import logging
import os
import re
import struct

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.defaultfilters import slugify, truncatechars

import fiona
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToCover, ResizeToFill, ResizeToFit
from model_utils.managers import InheritanceManager
from picklefield.fields import PickledObjectField
from pyproj import Proj, transform
from shapely import geometry
from unicodecsv import DictReader
import xlrd

from icons.models import Icon
from lock_manager import Lock, LockError
from origins.models import Origin

from .exceptions import LIBREAPIError
from .job_processing import Job
from .literals import (DEFAULT_LIMIT, DEFAULT_SHEET, DATA_TYPE_CHOICES,
    RENDERER_BROWSEABLE_API, RENDERER_JSON, RENDERER_XML, RENDERER_YAML, RENDERER_LEAFLET)
from .managers import SourceAccessManager
from .query import Query
from .utils import DATA_TYPE_FUNCTIONS

logger = logging.getLogger(__name__)

class Source(models.Model):
    source_type = _('Base source class')
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML)
    support_column_regex = False

    # Base data
    name = models.CharField(max_length=128, verbose_name=_('name'), help_text=('Human readable name for this source.'))
    slug = models.SlugField(unique=True, blank=True, max_length=48, verbose_name=_('slug'), help_text=('URL friendly description of this source. If none is specified the name will be used.'))
    description = models.TextField(blank=True, verbose_name=_('description'))

    # Images
    image = models.ImageField(null=True, blank=True, upload_to='images', verbose_name=_('image'))
    showcase_image = ImageSpecField(source='image', processors=[ResizeToCover(140, 140)], format='PNG', options={'quality': 90})
    thumbnail_image = ImageSpecField(source='image', processors=[ResizeToFit(50, 50)], format='PNG', options={'quality': 60})

    # Data engine
    published = models.BooleanField(default=False, verbose_name=_('published'))
    allowed_groups = models.ManyToManyField(Group, verbose_name=_('allowed groups'), blank=True, null=True)
    limit = models.PositiveIntegerField(default=DEFAULT_LIMIT, verbose_name=_('limit'), help_text=_('Maximum number of items to show when all items are requested.'))
    origin = models.ForeignKey(Origin, verbose_name=_('origin'))

    # Scheduling
    schedule_string = models.CharField(max_length=128, blank=True, verbose_name=_('schedule string'), help_text=_('Use CRON style format.'))
    schedule_enabled = models.BooleanField(default=False, verbose_name=_('schedule enabled'), help_text=_('Enabled scheduled check for source\' origin updates.'))

    # Managers
    objects = InheritanceManager()
    allowed = SourceAccessManager()

    def check_source_data(self):
        logger.info('Checking for new data for source: %s' % self.slug)

        try:
            lock_id = u'check_source_data-%d' % self.pk
            logger.debug('trying to acquire lock: %s' % lock_id)
            lock = Lock.acquire_lock(lock_id, 60)
            logger.debug('acquired lock: %s' % lock_id)
            try:
                self.check_origin_data()
                pass
            except Exception as exception:
                logger.debug('unhandled exception: %s' % exception)
                logger.error('Error when checking data for source: %s; %s' % (self.slug, exception))
                raise
            finally:
                lock.release()
        except LockError:
            logger.debug('unable to obtain lock')
            logger.info('Unable to obtain lock to check for new data for source: %s' % self.slug)
            pass

    def check_origin_data(self):
        self.origin_subclass_instance = Origin.objects.get_subclass(pk=self.origin.pk)
        self.origin_subclass_instance.copy_data()

        logger.debug('new_hash: %s' % self.origin_subclass_instance.new_hash)

        try:
            source_data_version = self.versions.get(checksum=self.origin_subclass_instance.new_hash)
        except SourceDataVersion.DoesNotExist:
            logger.info('New origin data version found for source: %s' % self.slug)
            source_data_version = SourceDataVersion.objects.create(source=self, checksum=self.origin_subclass_instance.new_hash)
            job = Job(target=self.import_origin_data, args=[source_data_version])
            job.submit()
            logger.debug('launching import job: %s' % job)
        else:
            source_data_version.active = True
            source_data_version.save()

    def _get_metadata(self):
        """Source models are responsible for overloading this method"""
        return ''

    @transaction.commit_on_success
    def import_origin_data(self, source_data_version):
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        source_data_version.metadata = self._get_metadata()
        source_data_version.save()

        if self.support_column_regex:
            self.get_regex_maps()

        logger.info('Importing new data for source: %s' % self.slug)

        row_count = 0
        try:
            for row_id, row in enumerate(self._get_rows(), 1):
                SourceData.objects.create(source_data_version=source_data_version, row_id=row_id, row=dict(row, **{'_id': row_id}))
                row_count += 1
        except Exception as exception:
            transaction.rollback()
            logger.error('Error importing rows; %s' % exception)
            if getattr(settings, 'DEBUG', False):
                raise
            else:
                return

        logger.debug('finished importing rows')

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

        self.origin_subclass_instance.discard_copy()
        logger.info('Imported %d rows for source: %s' % (row_count, self.slug))

    class AlwaysFalseSearch(object):
        def search(self, string):
            return False

    class AlwaysTrueSearch(object):
        def search(self, string):
            return True

    def get_regex_maps(self):
        self.skip_regex_map = {}
        for name, skip_regex in self.columns.values_list('name', 'skip_regex'):
            if skip_regex:
                self.skip_regex_map[name] = re.compile(skip_regex)
            else:
                self.skip_regex_map[name] = self.__class__.AlwaysFalseSearch()

        self.import_regex_map = {}
        for name, import_regex in self.columns.values_list('name', 'import_regex'):
            if import_regex:
                self.import_regex_map[name] = re.compile(import_regex)
            else:
                self.import_regex_map[name] = self.__class__.AlwaysTrueSearch()

    def process_regex(self, row):
        skip_result = [True if self.skip_regex_map[name].search(unicode(value)) else False for name, value in row.items() if name in self.skip_regex_map]
        import_result = [True if self.import_regex_map[name].search(unicode(value)) else False for name, value in row.items() if name in self.import_regex_map]

        return all(cell_skip is False for cell_skip in skip_result) and all(import_result)

    def get_all(self, id=None, parameters=None):
        logger.debug('parameters: %s' % parameters)
        initial_datetime = datetime.datetime.now()
        timestamp, parameters = Source.analyze_request(parameters)
        logger.debug('timestamp: %s', timestamp)

        try:
            if timestamp:
                source_data_version = self.versions.get(timestamp=timestamp)
            else:
                source_data_version = self.versions.get(active=True)
        except SourceDataVersion.DoesNotExist:
            return []

        self.base_iterator = (item.row for item in SourceData.objects.filter(source_data_version=source_data_version).iterator())

        if id:
            self.base_iterator = islice(self.base_iterator, id - 1, id)

        results = Query(self).execute(parameters)
        logger.debug('query elapsed time: %s' % (datetime.datetime.now() - initial_datetime))

        return results

    def get_one(self, id, parameters=None):
        # ID are all base 1
        if id == 0:
            raise LIBREAPIError('Invalid ID; IDs are base 1')
        return self.get_all(id, parameters)

    @staticmethod
    def analyze_request(parameters=None):
        kwargs = {}
        if not parameters:
            parameters = {}
        else:
            for i in parameters:
                if not i.startswith('_'):
                    kwargs[i] = parameters[i]

        timestamp = parameters.get('_timestamp', None)

        return timestamp, parameters

    def get_functions_map(self):
        """Calculate the column name to data type conversion map"""
        return dict([(column, DATA_TYPE_FUNCTIONS[data_type]) for column, data_type in self.columns.values_list('name', 'data_type')])

    def apply_datatypes(self, properties, functions_map):
        result = {}

        for key, value in properties.items():
            try:
                result[key] = functions_map[key](value)
            except KeyError:
                # Is not to be converted
                result[key] = value
            except ValueError:
                # Fallback for failed conversion
                logger.error('Unable to apply data type for field: %s' % key)
                result[key] = value

        return result

    def clear_versions(self):
        """Delete all the versions of this source"""
        for version in self.versions.all():
            version.delete()

    def __unicode__(self):
        return self.name

    def clean(self):
        """Validation method, to avoid adding a source without a slug value"""
        if not self.slug:
            self.slug = slugify(self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('source_view', [self.slug])

    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')
        ordering = ['name', 'slug']


class SourceCSV(Source):
    source_type = _('CSV file')
    support_column_regex = True

    delimiter = models.CharField(blank=True, max_length=1, default=',', verbose_name=_('delimiter'))
    quote_character = models.CharField(blank=True, max_length=1, verbose_name=_('quote character'))
    encoding = models.CharField(default='ascii', max_length=32, verbose_name=_('encoding'), help_text=_('File encoding. Check http://docs.python.org/2/library/codecs.html#standard-encodings for a list of valid encodings.'))

    def _get_rows(self):
        functions_map = self.get_functions_map()

        kwargs = {}
        if self.delimiter:
            kwargs['delimiter'] = str(self.delimiter)
        if self.quote_character:
            kwargs['quotechar'] = str(self.quote_character)

        column_names = self.columns.values_list('name', flat=True)

        logger.debug('column_names: %s' % column_names)

        for row_dict in DictReader(self.origin_subclass_instance.copy_file, encoding=self.encoding, errors='replace', fieldnames=column_names, **kwargs):
            if self.process_regex(row_dict):
                fields = {}
                for field in self.columns.filter(import_column=True):
                    fields[field.name] = functions_map[field.name](row_dict[field.name])
                yield fields

    class Meta:
        verbose_name = _('CSV source')
        verbose_name_plural = _('CSV sources')


class SourceFixedWidth(Source):
    source_type = _('Fixed width column file')
    support_column_regex = True

    def _get_rows(self):
        column_names = self.columns.values_list('name', flat=True)
        column_widths = self.columns.values_list('size', flat=True)

        fmtstring = ''.join('%ds' % f for f in map(int, column_widths))
        parse = struct.Struct(fmtstring).unpack_from

        functions_map = self.get_functions_map()

        for row_id, row in enumerate(self.origin_subclass_instance.copy_file, 1):
            try:
                row_dict = dict(zip(column_names, parse(row)))
            except struct.error as exception:
                logger.error('Error importing row # %d of source: %s' % (row_id, self.slug))
            else:
                if self.process_regex(row_dict):
                    fields = {}
                    for field_num, field in enumerate(self.columns.filter(import_column=True), 1):
                        try:
                            fields[field.name] = functions_map[field.name](row_dict[field.name])
                        except ValueError as exception:
                            logger.error('Error converting field # %d, of row # %d, of source: %s; %s' % (field_num, row_id, self.slug, exception))
                    yield fields

    class Meta:
        verbose_name = _('Fixed width source')
        verbose_name_plural = _('Fixed width sources')


class SourceSpreadsheet(Source):
    source_type = _('Spreadsheet file')
    support_column_regex = True

    sheet = models.CharField(max_length=32, default=DEFAULT_SHEET, verbose_name=_('sheet'), help_text=('Worksheet of the spreadsheet file to use.'))

    def _convert_value(self, item):
        """
        Handle different value types for XLS. Item is a cell object.
        """
        # Types:
        # 0 = empty u''
        # 1 = unicode text
        # 2 = float (convert to int if possible, then convert to string)
        # 3 = date (convert to unambiguous date/time string)
        # 4 = boolean (convert to string "0" or "1")
        # 5 = error (convert from code to error text)
        # 6 = blank u''

        # Thx to Augusto C Men to point fast solution for XLS/XLSX dates
        if item.ctype == 3:  # XL_CELL_DATE:
            try:
                return datetime.datetime(*xlrd.xldate_as_tuple(item.value, self._book.datemode))
            except ValueError:
                # TODO: make toggable
                # Invalid date
                return item.value

        if item.ctype == 2:  # XL_CELL_NUMBER:
            if item.value % 1 == 0:  # integers
                return int(item.value)
            else:
                return item.value

        return item.value

    def _get_rows(self):
        logger.debug('opening workbook')

        self._book = xlrd.open_workbook(file_contents=self.origin_subclass_instance.copy_file.read())

        logger.debug('opening sheet: %s' % self.sheet)

        try:
            self._sheet = self._book.sheet_by_name(self.sheet)
        except xlrd.XLRDError:
            self._sheet = self._book.sheet_by_index(int(self.sheet))

        for i in xrange(0, self._sheet.nrows):
            cells = self._sheet.row(i)

            fields = {}
            for cell_number, field in enumerate(self.columns.filter(import_column=True), 0):
                fields[field.name] = self._convert_value(cells[cell_number])

            if self.process_regex(fields):
                yield fields

    class Meta:
        verbose_name = _('spreadsheet source')
        verbose_name_plural = _('spreadsheet sources')


class LeafletMarker(models.Model):
    slug = models.SlugField(blank=True, verbose_name=_(u'slug'), unique=True)
    label = models.CharField(max_length=48, verbose_name=_(u'label'), blank=True)
    icon = models.ForeignKey(Icon, verbose_name=_('icon'), related_name='leafletmarker-icon')
    shadow = models.ForeignKey(Icon, null=True, blank=True, verbose_name=_('shadow'), related_name='leafletmarker-shadow')
    icon_anchor_x = models.IntegerField(verbose_name=_('icon anchor (horizontal)'), default=0)
    icon_anchor_y = models.IntegerField(verbose_name=_('icon anchor (vertical)'), default=0)
    shadow_anchor_x = models.IntegerField(verbose_name=_('shadow anchor (horizontal)'), default=0)
    shadow_anchor_y = models.IntegerField(verbose_name=_('shadow anchor (vertical)'), default=0)
    popup_anchor_x = models.IntegerField(verbose_name=_('popup anchor (horizontal)'), default=0)
    popup_anchor_y = models.IntegerField(verbose_name=_('popup anchor (vertical)'), default=0)

    def __unicode__(self):
        return '%s%s' % (self.slug, ' (%s)' % self.label if self.label else '')

    def clean(self):
        """Validation method, to avoid adding a new marker without a slug value"""
        if not self.slug:
            self.slug = slugify(self.label)

    class Meta:
        verbose_name = _('leaflet marker')
        verbose_name_plural = _('leaflet marker')
        ordering = ['label', 'slug']


class SourceShape(Source):
    source_type = _('Shapefile')
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML, RENDERER_LEAFLET)
    support_column_regex = True

    popup_template = models.TextField(blank=True, verbose_name=_('popup template'), help_text=_('Template for rendering the features when displaying them on a map.'))
    new_projection = models.CharField(max_length=32, blank=True, verbose_name=_('new projection'), help_text=_('Specify the EPSG number of the new projection to transform the geometries, leave blank otherwise.'))
    markers = models.ManyToManyField(LeafletMarker, blank=True, null=True)
    marker_template = models.TextField(blank=True, verbose_name=_('marker template'), help_text=_('Template to determine what marker each respective feature will use.'))
    template_header = models.TextField(blank=True, verbose_name=_('template header'), help_text=_('Place here custom styles, javascript or asset loading.'))

    @staticmethod
    def _transform(old_projection, new_projection, geometry, forced_geometry_type=None):
        # TODO: Support all types
        # Point (A single (x, y) tuple) - DONE
        # LineString (A list of (x, y) tuple vertices) - DONE
        # Polygon (A list of rings (each a list of (x, y) tuples)) - DONE
        # MultiPoint (A list of points (each a single (x, y) tuple))- DONE
        # MultiLineString (A list of lines (each a list of (x, y) tuples)) - DONE
        # MultiPolygon (A list of polygons (see above)) - DONE
        # GeometryCollection
        # 3D Point
        # 3D LineString
        # 3D Polygon
        # 3D MultiPoint
        # 3D MultiLineString
        # 3D MultiPolygon
        # 3D GeometryCollection

        if forced_geometry_type:
            geometry_type = forced_geometry_type
            coordinates = geometry
        else:
            geometry_type = geometry['type']
            coordinates = geometry['coordinates']

        logger.debug('geometry_type: %s' % geometry_type)

        if geometry_type == 'Point':
            return _transform(old_projection, new_projection, *coordinates)
        elif geometry_type == 'LineString':
            result = []
            for x, y in coordinates:
                result.append(transform(old_projection, new_projection, x, y))
            return result
        elif geometry_type == 'Polygon':
            result = []
            for ring in coordinates:
                element_result = []
                for x, y in ring:
                    element_result.append(transform(old_projection, new_projection, x, y))
                result.append(element_result)
            return result
        elif geometry['type'] == 'MultiPolygon':
            result = []
            for polygon in coordinates:
                result.append(SourceShape._transform(old_projection, new_projection, polygon, forced_geometry_type='Polygon'))
            return result
        elif geometry['type'] == 'MultiPoint':
            result = []
            for point in coordinates:
                result.append(SourceShape._transform(old_projection, new_projection, point, forced_geometry_type='Point'))
            return result
        elif geometry['type'] == 'MultiLineString':
            result = []
            for line in coordinates:
                result.append(SourceShape._transform(old_projection, new_projection, line, forced_geometry_type='LineString'))
            return result
        else:
            # Unsuported geometry type, return coordinates as is
            return geometry['coordinates']

    def _get_metadata(self):
        old_filename = self.origin_subclass_instance.copy_file.name
        self.filename = old_filename + '.zip'
        os.rename(old_filename, self.filename)
        self.origin_subclass_instance.copy_file.name = self.filename

        self.source = fiona.open('', vfs='zip://%s' % self.filename)
        return self.source.meta

    def _get_rows(self):
        if self.new_projection:
            new_projection = Proj(init='epsg:%s' % self.new_projection)
            old_projection = Proj(**self.source.crs)
        else:
            new_projection = False

        functions_map = self.get_functions_map()

        feature_number = 1
        for feature in self.source:
            logger.debug('importing feature number: %d' % feature_number)
            feature_number += 1

            try:
                fields = {}
                for field in self.columns.filter(import_column=True):
                    fields[field.new_name] = functions_map[field.name](feature['properties'].get(field.name, field.default))

                feature['properties'] = fields

                if new_projection:
                    feature['geometry']['coordinates'] = SourceShape._transform(old_projection, new_projection, feature['geometry'])

                if self.process_regex(fields):
                    feature['geometry'] = geometry.shape(feature['geometry'])
                    yield feature
            except Exception as exception:
                logging.exception('Error processing feature %s; %s', (feature['id'], exception))

    class Meta:
        verbose_name = _('shape source')
        verbose_name_plural = _('shape sources')


class SourceDirect(Source):
    source_type = _('Direct')
    support_column_regex = False

    def _get_rows(self):
        return self.origin_subclass_instance.copy_file

    class Meta:
        verbose_name = _('direct source')
        verbose_name_plural = _('direct sources')


class SourceSimple(Source):
    source_type = _('Simple')
    support_column_regex = True

    def _get_rows(self):
        functions_map = self.get_functions_map()

        for row in self.origin_subclass_instance.copy_file:
            fields = {}
            for field in self.columns.filter(import_column=True):
                fields[field.new_name] = functions_map[field.name](row.get(field.name, field.default))

            if self.process_regex(fields):
                yield fields

    class Meta:
        verbose_name = _('simple source')
        verbose_name_plural = _('simple sources')


# Version and data models


class SourceDataVersion(models.Model):
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML)

    source = models.ForeignKey(Source, verbose_name=_('source'), related_name='versions')
    datetime = models.DateTimeField(default=lambda: now())
    timestamp = models.CharField(blank=True, max_length=20, verbose_name=_('timestamp'))
    # MySQL doesn't like BLOB/TEXT columns used in key specification without a key length; DatabaseError 1170
    checksum = models.CharField(max_length=64, verbose_name=_('checksum'))
    ready = models.BooleanField(default=False, verbose_name=_('ready'))
    active = models.BooleanField(default=False, verbose_name=_('active'))
    metadata = PickledObjectField(blank=True, verbose_name=_('metadata'))

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
        get_latest_by = 'datetime'


class SourceData(models.Model):
    source_data_version = models.ForeignKey(SourceDataVersion, verbose_name=_('source data version'), related_name='data')
    row = PickledObjectField(verbose_name=_('row'))
    row_id = models.PositiveIntegerField(verbose_name=_('row id'), db_index=True)

    def __unicode__(self):
        return unicode(self.row)

    class Meta:
        verbose_name = _('source data')
        verbose_name_plural = _('sources data')


# Column models


class ColumnBase(models.Model):
    import_column = models.BooleanField(default=True, verbose_name=_('import'))
    name = models.CharField(max_length=32, verbose_name=_('name'))
    default = models.CharField(max_length=32, blank=True, verbose_name=_('default'))

    class Meta:
        abstract = True


class CSVColumn(ColumnBase):
    source = models.ForeignKey(SourceCSV, verbose_name=_('CSV source'), related_name='columns')
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))
    skip_regex = models.TextField(blank=True, verbose_name=_('skip expression'))
    import_regex = models.TextField(blank=True, verbose_name=_('import expression'))

    class Meta:
        verbose_name = _('CSV column')
        verbose_name_plural = _('CSV columns')


class FixedWidthColumn(ColumnBase):
    source = models.ForeignKey(SourceFixedWidth, verbose_name=_('fixed width source'), related_name='columns')
    size = models.PositiveIntegerField(verbose_name=_('size'))
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))
    skip_regex = models.TextField(blank=True, verbose_name=_('skip expression'))
    import_regex = models.TextField(blank=True, verbose_name=_('import expression'))

    class Meta:
        verbose_name = _('fixed width column')
        verbose_name_plural = _('fixed width columns')


class SpreadsheetColumn(ColumnBase):
    source = models.ForeignKey(SourceSpreadsheet, verbose_name=_('spreadsheet source'), related_name='columns')
    skip_regex = models.TextField(blank=True, verbose_name=_('skip expression'))
    import_regex = models.TextField(blank=True, verbose_name=_('import expression'))

    class Meta:
        verbose_name = _('spreadsheet column')
        verbose_name_plural = _('spreadsheet columns')


class ShapefileColumn(ColumnBase):
    source = models.ForeignKey(SourceShape, verbose_name=_('shapefile source'), related_name='columns')
    new_name = models.CharField(max_length=32, verbose_name=_('new name'), blank=True)
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))
    skip_regex = models.TextField(blank=True, verbose_name=_('skip expression'))
    import_regex = models.TextField(blank=True, verbose_name=_('import expression'))

    def clean(self):
        """Validation method, to avoid adding a column without a new_name value"""
        if not self.new_name:
            self.new_name = self.name

    class Meta:
        verbose_name = _('shapefile column')
        verbose_name_plural = _('shapefile columns')


class SimpleSourceColumn(ColumnBase):
    source = models.ForeignKey(SourceSimple, verbose_name=_('simple source'), related_name='columns')
    new_name = models.CharField(max_length=32, verbose_name=_('new name'), blank=True)
    data_type = models.PositiveIntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_('data type'))
    skip_regex = models.TextField(blank=True, verbose_name=_('skip expression'))
    import_regex = models.TextField(blank=True, verbose_name=_('import expression'))

    def clean(self):
        """Validation method, to avoid adding a column without a new_name value"""
        if not self.new_name:
            self.new_name = self.name

    class Meta:
        verbose_name = _('simple source column')
        verbose_name_plural = _('simple source columns')

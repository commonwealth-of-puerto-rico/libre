from __future__ import absolute_import

import csv
import datetime
import hashlib
from multiprocessing import Process
import string
import struct

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

import jsonfield
import xlrd
from model_utils.managers import InheritanceManager

from .literals import DEFAULT_FIRST_ROW_NAMES, DEFAULT_LIMIT, DEFAULT_SHEET

HASH_FUNCTION = lambda x: hashlib.sha256(x).hexdigest()


class Source(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('name'), help_text=('Human readable name for this source.'))
    slug = models.SlugField(blank=True, max_length=48, verbose_name=_('slug'), help_text=('URL friendly description of this source. If none is specified the name will be used.'))

    objects = InheritanceManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name
        super(Source, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('resource_get_all', [self.slug])

    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')


class SourceFileBased(Source):
    limit = models.PositiveIntegerField(default=DEFAULT_LIMIT, verbose_name=_('limit'), help_text=('Maximum number of items to show when all items are requested.'))
    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=('Location to a file in the filesystem.'))
    file = models.FileField(blank=True, null=True, upload_to='spreadsheets', verbose_name=_('uploaded file'))

    def check_file(self):
        if self.path:
            new_hash = HASH_FUNCTION(open(self.path).read())
        else:
            return

        try:
            source_data_version = self.sourcedataversion_set.get(checksum=new_hash)
        except SourceDataVersion.DoesNotExist:
            source_data_version = SourceDataVersion.objects.create(source=self, checksum=new_hash)
            self.import_data(source_data_version)
            p = Process(target=self.import_data, args=(source_data_version,))
            p.start()
        else:
            source_data_version.active = True
            source_data_version.save()

    def get_one(self, id, timestamp=None):
        if timestamp:
            source_data_version = self.sourcedataversion_set.get(timestamp=timestamp)
        else:
            source_data_version = self.sourcedataversion_set.get(active=True)

        return SourceData.objects.get(source_data_version=source_data_version, row_id=id).row

    def get_all(self, timestamp=None):
        try:
            if timestamp:
                source_data_version = self.sourcedataversion_set.get(timestamp=timestamp)
            else:
                source_data_version = self.sourcedataversion_set.get(active=True)
        except SourceDataVersion.DoesNotExist:
            return []

        return [item.row for item in SourceData.objects.filter(source_data_version=source_data_version)[0:self.limit]]

    class Meta:
        abstract = True


class SourceCSV(SourceFileBased):
    column_names = models.TextField(blank=True, verbose_name=_('column names'), help_text=('Specify the column names to use.'))
    first_row_names = models.BooleanField(default=DEFAULT_FIRST_ROW_NAMES, verbose_name=_('first row names'), help_text=('Use the values of the first row as the column names.'))
    delimiter = models.CharField(blank=True, max_length=1, default=',', verbose_name=_('delimiter'))
    quote_character = models.CharField(blank=True, max_length=1, verbose_name=_('quote character'))
    column_widths = models.TextField(blank=True, null=True, verbose_name=_('column widths'), help_text=_('The column widths separated by a comma.'))

    def _get_items(self):
        column_names = self.column_names or string.ascii_uppercase

        if self.column_widths:
            fmtstring = ''.join('%ds' % f for f in map(int, self.column_widths.split(',')))
            parse = struct.Struct(fmtstring).unpack_from

            if self.first_row_names:
                column_names = map(string.strip, parse(self._file_handle.next()))

            for row in self._file_handle:
                yield dict(zip(column_names, map(string.strip, parse(row))))
        else:
            kwargs = {}
            if self.delimiter:
                kwargs['delimiter'] = str(self.delimiter)
            if self.quote_character:
                kwargs['quotechar'] = str(self.quote_character)

            reader = csv.reader(self._file_handle, **kwargs)

            if self.first_row_names:
                column_names = reader.next()

            for row in reader:
                yield dict(zip(column_names, row))

    def import_data(self, source_data_version):
        # Reload data in case this is executed in another thread
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        if self.path:
            self._file_handle = open(self.path)
        else:
            self._file_handle = self.file.open()

        id = 1
        for row in self._get_items():
            SourceData.objects.create(source_data_version=source_data_version, row_id=id, row=row)
            id = id + 1

        self._file_handle.close()

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

    class Meta:
        verbose_name = _('CSV source')
        verbose_name_plural = _('CSV sources')


class SourceSpreadsheet(SourceFileBased):
    sheet = models.CharField(max_length=32, default=DEFAULT_SHEET, verbose_name=_('sheet'), help_text=('Worksheet of the spreadsheet file to use.'))
    column_names = models.TextField(blank=True, verbose_name=_('column names'), help_text=('Specify the column names to use.'))
    first_row_names = models.BooleanField(default=DEFAULT_FIRST_ROW_NAMES, verbose_name=_('first row names'), help_text=('Use the values of the first row as the column names.'))

    def _convert_value(self, item):
        """
        Handle different value types for XLS. Item is a cell object.
        """
        # Thx to Augusto C Men to point fast solution for XLS/XLSX dates
        if item.ctype == 3: #XL_CELL_DATE:
            try:
                return datetime.datetime(*xlrd.xldate_as_tuple(item.value, self._book.datemode))
            except ValueError:
                # TODO: make togglable
                # Invalid date
                return item.value

        if item.ctype == 2: #XL_CELL_NUMBER:
            if item.value % 1 == 0:  # integers
                return int(item.value)
            else:
                return item.value

        return item.value

    def _get_items(self):
        column_names = self.column_names or string.ascii_uppercase

        if self.first_row_names:
            column_names = [cell.value for cell in self._sheet.row(0)]

        for i in range(1 if self.first_row_names else 0, self._sheet.nrows):
            #values = [self.convert_value(cell) for cell in self._sheet.row(i)]
            #if not any(values):
            #    continue  # empty lines are ignored
            #yield values

            result = {}
            column_count = 0

            for cell in self._sheet.row(i):
                result[column_names[column_count]] = self._convert_value(cell)
                column_count += 1

            yield result

    def import_data(self, source_data_version):
        # Reload data in case this is executed in another thread
        source_data_version = SourceDataVersion.objects.get(pk=source_data_version.pk)

        if self.path:
            self._book = xlrd.open_workbook(self.path)
            file_handle = None
        else:
            file_handle = self.file.open()
            self._book = xlrd.open_workbook(file_contents=file_handle.read())

        try:
            self._sheet = self._book.sheet_by_name(self.sheet)
        except xlrd.XLRDError:
            self._sheet = self._book.sheet_by_index(int(self.sheet))

        id = 1
        for row in self._get_items():
            SourceData.objects.create(source_data_version=source_data_version, row_id=id, row=row)
            id = id + 1

        if file_handle:
            file_handle.close()

        source_data_version.ready = True
        source_data_version.active = True
        source_data_version.save()

    class Meta:
        verbose_name = _('spreadsheet source')
        verbose_name_plural = _('spreadsheet sources')


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


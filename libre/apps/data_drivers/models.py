from __future__ import absolute_import

import string
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

import jsonfield
import xlrd
from model_utils.managers import InheritanceManager

from .literals import DEFAULT_FIRST_ROW_NAMES, DEFAULT_LIMIT, DEFAULT_SHEET


class Source(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('name'), help_text=('Human readable name for this source.'))
    slug = models.SlugField(blank=True, max_length=32, verbose_name=_('slug'), help_text=('URL friendly description of this source. If none is specified the name will be used.'))

    objects = InheritanceManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name
        super(Source, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')


class SourceSpreadsheet(Source):
    limit = models.PositiveIntegerField(default=DEFAULT_LIMIT, verbose_name=_('limit'), help_text=('Maximum number of items to show when all items are requested.'))
    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=('Location to a file in the filesystem.'))
    file = models.FileField(blank=True, null=True, upload_to='spreadsheets', verbose_name=_('upload a file'))
    sheet = models.CharField(max_length=32, default=DEFAULT_SHEET, verbose_name=_('sheet'), help_text=('Worksheet of the spreadsheet file to use.'))
    column_names = models.TextField(blank=True, verbose_name=_('column names'), help_text=('Specify the column names to use.'))
    first_row_names = models.BooleanField(default=DEFAULT_FIRST_ROW_NAMES, verbose_name=_('first row names'), help_text=('Use the values of the first row as the column names.'))

    def _convert_value(self, item):
        """
        Handle different value types for XLS. Item is a cell object.
        """
        # Thx to Augusto C Men to point fast solution for XLS/XLSX dates
        if item.ctype == 3: #XL_CELL_DATE:
            return datetime.datetime(*xlrd.xldate_as_tuple(item.value, self._book.datemode))

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

    def import_data(self):
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
            instance, created = SourceData.objects.get_or_create(source=self, id=id, defaults={'row': row})
            if not created:
                instance.row = row
                instance.save()
            id = id + 1
            print row

        if file_handle:
            file_handle.close()

    def get_one(self, id):
        return self.sourcedata_set.get(id=id).row

    def get_all(self):
        return [item.row for item in SourceData.objects.all()]

    class Meta:
        verbose_name = _('spreadsheet source')
        verbose_name_plural = _('spreadsheet sources')

'''
class SourceDataVersion(models.Model):
    datetime = models.DateTimeField()
    checksum = models.CharField(



'''

class SourceData(models.Model):
    source = models.ForeignKey(Source, verbose_name=_('source'))
    row = jsonfield.JSONField(verbose_name=_('row'))

    def __unicode__(self):
        return unicode(self.row)

    class Meta:
        verbose_name = _('source data')
        verbose_name_plural = _('sources data')

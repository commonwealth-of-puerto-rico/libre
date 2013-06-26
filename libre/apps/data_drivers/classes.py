from __future__ import absolute_import

import os
import string

from django.conf import settings

import xlrd

from .literals import DEFAULT_FIRST_ROW_NAMES, DEFAULT_LIMIT, DEFAULT_ZERO_BASE


class Resource(object):
    def __init__(self, obj):
        self.obj = obj

    def __unicode__(self):
        return unicode(self.obj)


class Source(object):
    limit = DEFAULT_LIMIT
    zero_base = DEFAULT_ZERO_BASE

    def __init__(self):
        pass


class Excel(Source):
    # file_path: Excel file path
    # sheet: Interger or string
    # column_names: List
    # first_row_names: Boolean

    first_row_names = DEFAULT_FIRST_ROW_NAMES

    def __init__(self):
        self._book = xlrd.open_workbook(self.file_path)
        try:
            self._sheet = self._book.sheet_by_index(self.sheet)
        except TypeError:
            self._sheet = self._book.sheet_by_name(self.sheet)

        if self.first_row_names:
            self.column_names = [cell.value for cell in self._sheet.row(0)]

    def get(self, id):
        if not self.zero_base and id == 0:
            raise Exception  # TODO: And id of 0 was specified and this resource don't allow them

        if self.first_row_names:
            id = id + 1

        if not self.zero_base:
            id = id - 1

        result = {}
        column_count = 0
        column_names = getattr(self, 'column_names', string.ascii_uppercase)

        for cell in self._sheet.row(id):
            result[column_names[column_count]] = cell.value
            column_count += 1

        return Resource(result)

    def all(self):
        result = []
        for id in xrange(0 if self.zero_base else 1, self.limit):
            try:
                result.append(self.get(id))
            except IndexError:
                break

        return result


class SampleExcel(Excel):
    file_path = os.path.join(settings.PROJECT_ROOT, 'contrib', 'sample.xls')
    #file_path = os.path.join(settings.PROJECT_ROOT, '..', 'CorpsBAK.xlsx')
    sheet = 0
    column_names = ['First name', 'Last name', 'Region', 'Office']
    first_row_names = True

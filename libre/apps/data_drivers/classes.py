import os
import string

from django.conf import settings

import xlrd


class Resource(object):
    def __init__(self, obj):
        self.obj = obj

    def __unicode__(self):
        return unicode(self.obj)


class Source(object):
    # limit

    def __init__(self):
        pass


class Excel(Source):
    # file_path
    # sheet
    # column names

    def __init__(self):
        self._book = xlrd.open_workbook(self.file_path)
        try:
            self._sheet = self._book.sheet_by_index(self.sheet)
        except TypeError:
            self._sheet = self._book.sheet_by_name(self.sheet)

    def get(self, id):
        result = {}
        column_count = 0
        column_names = getattr(self, 'column_names', string.ascii_uppercase)

        for cell in self._sheet.row(id):
            result[column_names[column_count]] = cell.value
            column_count += 1

        return Resource(result)


class SampleExcel(Excel):
    file_path = os.path.join(settings.PROJECT_ROOT, 'contrib', 'sample.xls')
    sheet = 0
    column_names = ['First name', 'Last name', 'Region', 'Office']

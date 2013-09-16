from __future__ import absolute_import

import os

from django.test import TestCase

from .models import OriginURLFile


class SourceTestCase(TestCase):
    def temp_path_status(self, path):
        if not os.path.exists(path):
            return 'File does not exist'
        if not os.path.isfile(path):
            return 'Not a file'
        if not os.access(path, os.R_OK):
            return 'File is not readable'
        return 'File exists'

    def setUp(self):
        self.origin_url = OriginURLFile.objects.create(label='test origin', url='http://www.census.gov/population/estimates/puerto-rico/prmunnet.txt')
        self.origin_url.copy_data()

    def tearDown(self):
        self.origin_url.discard_copy()

    def test_temp_file_creation(self):
        print self.temp_path_status(self.origin_url.temporary_file.name)

    def test_copy_file_creation(self):
        print self.temp_path_status(self.origin_url.copy_file.name)

    def test_hash(self):
        self.assertEqual(self.origin_url.new_hash, 'df0cfc653167d570a6aecfbab0f33e89377a0430dd74d92338a1802567a12621')

    def test_iterator(self):
        self.assertEqual(self.origin_url.data_iterator.next(), 'PR-99-1 Estimates of the Population of Puerto Rico Municipios, July 1, 1999, and')
        self.assertEqual(self.origin_url.data_iterator.next(), 'Demographic Components of Population Change: April 1, 1990 to July 1, 1999')
        self.origin_url.temporary_file.seek(0)
        self.assertEqual(self.origin_url.data_iterator.next(), 'PR-99-1 Estimates of the Population of Puerto Rico Municipios, July 1, 1999, and')

    def test_copy_file(self):
        self.assertEqual(len(self.origin_url.copy_file.read()), 10523)
        self.assertEqual(len(self.origin_url.copy_file.read()), 0)


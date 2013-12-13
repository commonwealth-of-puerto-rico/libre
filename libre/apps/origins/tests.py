from __future__ import absolute_import

import os

from django.conf import settings
from django.test import TestCase

from .models import OriginPath, OriginURLFile

TEST_FIXED_WIDTH_FILE = 'prmunnet.txt'


def temp_path_status(path):
    if not os.path.exists(path):
        return 'File does not exist'
    if not os.path.isfile(path):
        return 'Not a file'
    if not os.access(path, os.R_OK):
        return 'File is not readable'
    return 'File exists'


class URLFileTestCase(TestCase):
    def setUp(self):
        self.origin_url = OriginURLFile.objects.create(label='test origin', url='http://www.census.gov/population/estimates/puerto-rico/prmunnet.txt')
        self.origin_url.copy_data()

    def tearDown(self):
        self.origin_url.discard_copy()

    def test_copy_file_creation(self):
        self.assertEqual(temp_path_status(self.origin_url.copy_file.name), 'File exists')

    def test_hash(self):
        self.assertEqual(self.origin_url.new_hash, '81f81877c664b9863628e253ebfdff2cc53b05cbf8020735cb37eef46901ebe8')

    def test_iterator(self):
        self.assertEqual(self.origin_url.copy_file.next(), 'PR-99-1 Estimates of the Population of Puerto Rico Municipios, July 1, 1999, and\r\n')
        self.assertEqual(self.origin_url.copy_file.next(), 'Demographic Components of Population Change: April 1, 1990 to July 1, 1999\r\n')
        self.origin_url.copy_file.seek(0)
        self.assertEqual(self.origin_url.copy_file.next(), 'PR-99-1 Estimates of the Population of Puerto Rico Municipios, July 1, 1999, and\r\n')

    def test_copy_file(self):
        self.assertEqual(len(self.origin_url.copy_file.read()), 10713)
        self.assertEqual(len(self.origin_url.copy_file.read()), 0)


class OriginPathTestCase(TestCase):
    def setUp(self):
        self.origin_url = OriginPath.objects.create(label='test origin', path=os.path.join(settings.PROJECT_ROOT, 'contrib', 'sample_data', TEST_FIXED_WIDTH_FILE))
        self.origin_url.copy_data()

    def tearDown(self):
        self.origin_url.discard_copy()

    def test_copy_file_creation(self):
        self.assertEqual(temp_path_status(self.origin_url.copy_file.name), 'File exists')

    def test_hash(self):
        self.assertEqual(self.origin_url.new_hash, '81f81877c664b9863628e253ebfdff2cc53b05cbf8020735cb37eef46901ebe8')

    def test_iterator(self):
        self.assertEqual(self.origin_url.copy_file.next(), 'PR-99-1 Estimates of the Population of Puerto Rico Municipios, July 1, 1999, and\r\n')
        self.assertEqual(self.origin_url.copy_file.next(), 'Demographic Components of Population Change: April 1, 1990 to July 1, 1999\r\n')
        self.origin_url.copy_file.seek(0)
        self.assertEqual(self.origin_url.copy_file.next(), 'PR-99-1 Estimates of the Population of Puerto Rico Municipios, July 1, 1999, and\r\n')

    def test_copy_file(self):
        self.assertEqual(len(self.origin_url.copy_file.read()), 10713)
        self.assertEqual(len(self.origin_url.copy_file.read()), 0)

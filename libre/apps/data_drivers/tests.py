from __future__ import absolute_import

from django.test import TestCase

from origins.models import OriginURLFile

from .literals import DATA_TYPE_STRING, DATA_TYPE_NUMBER
from .models import SourceCSV, SourceFixedWidth


class SourceTestCase(TestCase):
    def format_path_status(self, path):
        if not os.path.exists(path):
            return "File does not exist"
        if not os.path.isfile(path):
            return "Not a file"
        if not os.access(path, os.R_OK):
            return "File is not readable"
        return "File exists"

    def setUp(self):
        self.origin_url = OriginURLFile.objects.create(label='test origin', url='http://www.census.gov/population/estimates/puerto-rico/prmunnet.txt')
        self.fw_source = SourceFixedWidth.objects.create(name='test fixed width source', origin=self.origin_url, limit=200)

    def test_fw_source_clear_versions(self):
        self.fw_source.check_source_data()
        self.assertEqual(self.fw_source.versions.count(), 1)
        version = self.fw_source.versions.all()[0]
        self.assertEqual(version.data.count(), 95)
        self.fw_source.clear_versions()
        self.assertEqual(self.fw_source.versions.count(), 0)

    def test_fw_source_simple_import(self):
        self.fw_source.check_source_data()
        self.assertEqual(self.fw_source.versions.count(), 1)
        version = self.fw_source.versions.all()[0]
        self.assertEqual(version.data.count(), 95)

    def test_fw_source_column_skip_regex(self):
        self.fw_source.columns.create(name='city', size=18, data_type=DATA_TYPE_STRING, skip_regex=r'(?:Municipio.*|\||-.*|Puerto Rico)')
        self.fw_source.columns.create(name='1999_estimate', size=15, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='1990_census', size=16, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='percent_change', size=17, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='births', size=10, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='deaths', size=10, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='natural_increase', size=18, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='net_migration', size=15, data_type=DATA_TYPE_NUMBER)
        self.fw_source.check_source_data()
        self.assertEqual(self.fw_source.versions.count(), 1)
        version = self.fw_source.versions.all()[0]
        self.assertEqual(version.data.count(), 78)


class QueryTestCase(TestCase):
    def setUp(self):
        self.origin_url = OriginURLFile.objects.create(label='test origin', url='http://www.census.gov/population/estimates/puerto-rico/prmunnet.txt')
        self.fw_source = SourceFixedWidth.objects.create(name='test fixed width source', origin=self.origin_url, limit=200)

    def test_aggregate_count(self):
        self.fw_source.columns.create(name='city', size=18, data_type=DATA_TYPE_STRING, skip_regex=r'(?:Municipio.*|\||-.*|Puerto Rico)')
        self.fw_source.columns.create(name='1999_estimate', size=15, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='1990_census', size=16, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='percent_change', size=17, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='births', size=10, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='deaths', size=10, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='natural_increase', size=18, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='net_migration', size=15, data_type=DATA_TYPE_NUMBER)
        self.fw_source.check_source_data()
        result = list(self.fw_source.get_all(parameters={'_aggregate__total' :'Count(*)'}))
        self.assertEqual(result, [{'total': 78}])

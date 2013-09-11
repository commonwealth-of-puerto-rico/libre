from __future__ import absolute_import

from django.test import TestCase

from origins.models import OriginURLFile

from .literals import DATA_TYPE_STRING, DATA_TYPE_NUMBER
from .models import SourceCSV, SourceFixedWidth


class SourceTestCase(TestCase):
    def setUp(self):
        origin_url = OriginURLFile.objects.create(label='test origin', url='http://www.census.gov/population/estimates/puerto-rico/prmunnet.txt')
        SourceFixedWidth.objects.create(name='test fixed width source', origin=origin_url)

    def test_source_slug_creation(self):
        fw_source = SourceFixedWidth.objects.get(name='test fixed width source')
        self.assertEqual(fw_source.slug, 'test-fixed-width-source')

    def test_fw_source_simple_import(self):
        fw_source = SourceFixedWidth.objects.get(name='test fixed width source')
        fw_source.check_source_data()
        self.assertEqual(fw_source.versions.count(), 1)
        version = fw_source.versions.all()[0]
        self.assertEqual(version.data.count(), 95)

    def test_fw_source_column_skip_regex(self):
        fw_source = SourceFixedWidth.objects.get(name='test fixed width source')
        fw_source.clear_versions()
        fw_source.columns.create(name='city', size=18, data_type=DATA_TYPE_STRING, skip_regex=r'(?:Municipio.*|\||-.*|Puerto Rico)')
        fw_source.columns.create(name='1999_estimate', size=15, data_type=DATA_TYPE_NUMBER)
        fw_source.columns.create(name='1990_census', size=16, data_type=DATA_TYPE_NUMBER)
        fw_source.columns.create(name='percent_change', size=17, data_type=DATA_TYPE_NUMBER)
        fw_source.columns.create(name='births', size=10, data_type=DATA_TYPE_NUMBER)
        fw_source.columns.create(name='deaths', size=10, data_type=DATA_TYPE_NUMBER)
        fw_source.columns.create(name='natural_increase', size=18, data_type=DATA_TYPE_NUMBER)
        fw_source.columns.create(name='net_migration', size=15, data_type=DATA_TYPE_NUMBER)
        fw_source.check_source_data()
        self.assertEqual(fw_source.versions.count(), 1)
        version = fw_source.versions.all()[0]
        self.assertEqual(version.data.count(), 78)

    def test_fw_source_queries_aggregate_count(self):
        fw_source = SourceFixedWidth.objects.get(name='test fixed width source')
        result = list(fw_source.get_all(parameters={'_aggregate__total' :'Count(*)'}))
        self.assertEqual(result, [{'total': 78}])

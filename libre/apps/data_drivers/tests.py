from __future__ import absolute_import

import datetime
import os

from django.conf import settings
from django.test import TestCase

from origins.models import OriginPath

from .literals import DATA_TYPE_STRING, DATA_TYPE_NUMBER
from .models import SourceFixedWidth
from .utils import parse_value, parse_request

TEST_FIXED_WIDTH_FILE = 'prmunnet.txt'


class SourceTestCase(TestCase):
    def setUp(self):
        self.origin_url = OriginPath.objects.create(label='test origin', path=os.path.join(settings.PROJECT_ROOT, 'contrib', 'sample_data', TEST_FIXED_WIDTH_FILE))
        self.fw_source = SourceFixedWidth.objects.create(name='test fixed width source', origin=self.origin_url, limit=100)

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
        self.origin_url = OriginPath.objects.create(label='test origin', path=os.path.join(settings.PROJECT_ROOT, 'contrib', 'sample_data', TEST_FIXED_WIDTH_FILE))
        self.fw_source = SourceFixedWidth.objects.create(name='test fixed width source', slug='test-fixed-width-source', origin=self.origin_url, limit=200)
        self.fw_source.columns.create(name='city', size=18, data_type=DATA_TYPE_STRING, skip_regex=r'(?:Municipio.*|\||-.*|Puerto Rico)')
        self.fw_source.columns.create(name='1999_estimate', size=15, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='1990_census', size=16, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='percent_change', size=17, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='births', size=10, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='deaths', size=10, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='natural_increase', size=18, data_type=DATA_TYPE_NUMBER)
        self.fw_source.columns.create(name='net_migration', size=15, data_type=DATA_TYPE_NUMBER)
        self.fw_source.check_source_data()

    # Aggregations
    def test_aggregate_count(self):
        result = list(self.fw_source.get_all(parameters={'_aggregate__total' :'Count(*)'}))
        self.assertEqual(result, [{'total': 78}])

    def test_aggregate_sum(self):
        result = list(self.fw_source.get_all(parameters={'_aggregate__births' :'Sum(births)'}))
        self.assertEqual(result, [{'births': 585532}])

    # Groupping
    def test_groupping_aggregate_sum_and_json_path(self):
        result = list(self.fw_source.get_all(parameters={'_group_by': 'city', '_aggregate__births' :'Sum(births)', '_json_path': '[*]..(births)'}))
        self.assertEqual(result, [3282, 3282, 5884, 5884, 8960, 8960, 4298,
            4298, 4352, 4352, 4080, 4080, 14693, 14693, 3222, 3222, 3669,
            3669, 5436, 5436, 34563, 34563, 5820, 5820, 22474, 22474, 5133,
            5133, 7901, 7901, 26830, 26830, 5690, 5690, 7660, 7660, 3085,
            3085, 3310, 3310, 5901, 5901, 6100, 6100, 3336, 3336, 6026,
            6026, 294, 294, 5066, 5066, 6719, 6719, 1782, 1782, 3270, 3270,
            7461, 7461, 3575, 3575, 15007, 15007, 5155, 5155, 5215, 5215,
            1936, 1936, 9438, 9438, 6129, 6129, 3018, 3018, 8525, 8525, 5185,
            5185, 3583, 3583, 5005, 5005, 1465, 1465, 4901, 4901, 4803, 4803,
            3249, 3249, 7374, 7374, 1090, 1090, 2008, 2008, 14154, 14154, 5610,
            5610, 5157, 5157, 3608, 3608, 5080, 5080, 4313, 4313, 3302, 3302,
            4310, 4310, 32206, 32206, 3714, 3714, 2103, 2103, 7989, 7989, 3859,
            3859, 5452, 5452, 5346, 5346, 66452, 66452, 5816, 5816, 5797, 5797,
            4070, 4070, 8901, 8901, 14125, 14125, 10377, 10377, 5320, 5320,
            5750, 5750, 10371, 10371, 1539, 1539, 5021, 5021, 5907, 5907, 6925, 6925])

    def test_groupping_and_json_path(self):
        result = list(self.fw_source.get_all(parameters={'_group_by': 'city', '_json_path': '[*]..(value)'}))
        self.assertEqual(result, ['Adjuntas', 'Aguada', 'Aguadilla', 'Aguas Buenas',
            'Aibonito', 'Anasco', 'Arecibo', 'Arroyo', 'Barceloneta', 'Barranquitas',
            'Bayamon', 'Cabo Rojo', 'Caguas', 'Camuy', 'Canovanas', 'Carolina',
            'Catano', 'Cayey', 'Ceiba', 'Ciales', 'Cidra', 'Coamo', 'Comerio',
            'Corozal', 'Culebra', 'Dorado', 'Fajardo', 'Florida', 'Guanica',
            'Guayama', 'Guayanilla', 'Guaynabo', 'Gurabo', 'Hatillo', 'Hormigueros',
            'Humacao', 'Isabela', 'Jayuya', 'Juana Diaz', 'Juncos', 'Lajas',
            'Lares', 'Las Marias', 'Las Piedras', 'Loiza', 'Luquillo', 'Manati',
            'Maricao', 'Maunabo', 'Mayaguez', 'Moca', 'Morovis', 'Naguabo',
            'Naranjito', 'Orocovis', 'Patillas', 'Penuelas', 'Ponce', 'Quebradillas',
            'Rincon', 'Rio Grande', 'Sabana Grande', 'Salinas', 'San German',
            'San Juan', 'San Lorenzo', 'San Sebastian', 'Santa Isabel', 'Toa Alta',
            'Toa Baja', 'Trujillo Alto', 'Utuado', 'Vega Alta', 'Vega Baja',
            'Vieques', 'Villalba', 'Yabucoa', 'Yauco'])

    def test_groupping_aggregate_sum_and_json_path(self):
        result = list(self.fw_source.get_all(parameters={'_group_by': 'city',
            '_aggregate__births' :'Sum(births)', '_aggregate__deaths' :'Sum(deaths)',
            '_json_path': '[*]..(births,deaths)', '_as_nested_list': ''}))
        self.assertEqual(result, [(3282, 1344), (3282, 1344), (5884, 2189),
        (5884, 2189), (8960, 4727), (8960, 4727), (4298, 1634), (4298, 1634),
        (4352, 1731), (4352, 1731), (4080, 1869), (4080, 1869), (14693, 8049),
        (14693, 8049), (3222, 1388), (3222, 1388), (3669, 1642), (3669, 1642),
        (5436, 1615), (5436, 1615), (34563, 15190), (34563, 15190), (5820, 3321),
        (5820, 3321), (22474, 9913), (22474, 9913), (5133, 2145), (5133, 2145),
        (7901, 2722), (7901, 2722), (26830, 11672), (26830, 11672), (5690, 2459),
        (5690, 2459), (7660, 3540), (7660, 3540), (3085, 1036), (3085, 1036),
        (3310, 1205), (3310, 1205), (5901, 2070), (5901, 2070), (6100, 2493),
        (6100, 2493), (3336, 1289), (3336, 1289), (6026, 2066), (6026, 2066),
        (294, 107), (294, 107), (5066, 1920), (5066, 1920), (6719, 3135), (6719, 3135),
        (1782, 730), (1782, 730), (3270, 1688), (3270, 1688), (7461, 3159), (7461, 3159),
        (3575, 1546), (3575, 1546), (15007, 6194), (15007, 6194), (5155, 2034),
        (5155, 2034), (5215, 2449), (5215, 2449), (1936, 1099), (1936, 1099),
        (9438, 3973), (9438, 3973), (6129, 3169), (6129, 3169), (3018, 1053),
        (3018, 1053), (8525, 3121), (8525, 3121), (5185, 2294), (5185, 2294),
        (3583, 1869), (3583, 1869), (5005, 2161), (5005, 2161), (1465, 589),
        (1465, 589), (4901, 1829), (4901, 1829), (4803, 1694), (4803, 1694),
        (3249, 1423), (3249, 1423), (7374, 3186), (7374, 3186), (1090, 393),
        (1090, 393), (2008, 894), (2008, 894), (14154, 8088), (14154, 8088),
        (5610, 1953), (5610, 1953), (5157, 1452), (5157, 1452), (3608, 1857),
        (3608, 1857), (5080, 1677), (5080, 1677), (4313, 1350), (4313, 1350),
        (3302, 1463), (3302, 1463), (4310, 1455), (4310, 1455), (32206, 14762),
        (32206, 14762), (3714, 1540), (3714, 1540), (2103, 972), (2103, 972),
        (7989, 3133), (7989, 3133), (3859, 1884), (3859, 1884), (5452, 2190),
        (5452, 2190), (5346, 2764), (5346, 2764), (66452, 41557), (66452, 41557),
        (5816, 2616), (5816, 2616), (5797, 3006), (5797, 3006), (4070, 1529),
        (4070, 1529), (8901, 2330), (8901, 2330), (14125, 5301), (14125, 5301),
        (10377, 3579), (10377, 3579), (5320, 2538), (5320, 2538), (5750, 2196),
        (5750, 2196), (10371, 4129), (10371, 4129), (1539, 820), (1539, 820),
        (5021, 1367), (5021, 1367), (5907, 2483), (5907, 2483), (6925, 2979),
        (6925, 2979)])

    # Filters
    def test_filtering_equal(self):
        result = list(self.fw_source.get_all(parameters={'city' :'"Aguada"'}))
        self.assertEqual(result, [{'city': 'Aguada', 'percent_change': 11.4,
        'deaths': 2189, 'births': 5884, 'net_migration': 404, '1999_estimate': 40010,
        'natural_increase': 3695, '_id': 2, '1990_census': 35911}])

    def test_filtering_contains(self):
        result = list(self.fw_source.get_all(parameters={'city__contains' :'"uad"', '_json_path': '[*].(city)'}))
        self.assertEqual(result, ['Aguada', 'Aguadilla', 'Utuado'])
        result = list(self.fw_source.get_all(parameters={'city__contains' :'"Agu"', '_json_path': '[*].(city)'}))
        self.assertEqual(result, ['Aguada', 'Aguadilla', 'Aguas Buenas'])

    def test_filtering_icontains(self):
        result = list(self.fw_source.get_all(parameters={'city__icontains' :'"Agu"', '_json_path': '[*].(city)'}))
        self.assertEqual(result, ['Aguada', 'Aguadilla', 'Aguas Buenas', 'Caguas', 'Mayaguez', 'Naguabo'])

    def test_filtering_endswith(self):
        result = list(self.fw_source.get_all(parameters={'city__endswith' :'"abo"', '_json_path': '[*].(city)'}))
        self.assertEqual(result, ['Guaynabo', 'Gurabo', 'Maunabo', 'Naguabo'])


class UtilitiesTestCase(TestCase):
    def test_query_parsing(self):
        class Request():
            META = {'QUERY_STRING': 'a=1&b="2"&c=Subquery(a=1&b=2)&d="&"'}

        self.assertEqual(parse_request(Request()), {'a': '1', 'c': 'Subquery(a=1&b=2)', 'b': '"2"', 'd': '"&"'})

    def test_value_parsing(self):
        self.assertEqual(parse_value('1'), 1)  # Number
        self.assertEqual(parse_value('(5)'), -5)  # Negative number
        self.assertEqual(parse_value('-5'), -5)  # Negative number
        self.assertEqual(parse_value('1.10'), 1.10)  # Float
        self.assertEqual(parse_value('"1.10"'), u'1.10')  # String
        self.assertEqual(parse_value('[1.10, "a"]'), [1.10, u'a'])  #List
        self.assertEqual(parse_value('Date(2013-01-01)'), datetime.date(2013, 1, 1))  #Date
        self.assertEqual(parse_value('Time(10:55PM)'), datetime.time(22, 55))  #Time
        self.assertEqual(parse_value('DateTime(2013-02-02 14:55)'), datetime.datetime(2013, 2, 2, 14, 55))  #Datetime
        self.assertEqual(parse_value('Point([1,1])').__geo_interface__, {'type': 'Point', 'coordinates': (1.0, 1.0)})  # Point
        self.assertEqual(parse_value('Point([1,1]).buffer(0.01)').simplify(1).__geo_interface__, {'type': 'Polygon', 'coordinates': (((1.01, 1.0), (1.0, 0.99), (0.99, 1.0), (1.0, 1.01), (1.01, 1.0)),)})  #buffer method

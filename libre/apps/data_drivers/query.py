from __future__ import absolute_import

from itertools import groupby, izip, tee
import logging
from operator import itemgetter
import types

from shapely import geometry
import jsonpath_rw

from .aggregates import Count, Sum
from .exceptions import Http400
from .filters import FILTER_CLASS_MAP, FILTER_NAMES
from .literals import (DOUBLE_DELIMITER, JOIN_TYPE_AND, JOIN_TYPE_CHOICES,
    JOIN_TYPE_OR, LQL_DELIMITER)
from .utils import parse_value

logger = logging.getLogger(__name__)


class Query():
    def __init__(self, source, source_class):
        self.source = source
        self.source_class = source_class
        self.json_path = None
        self.aggregates = []
        self.filters = []
        self.groups = []
        self.join_type = JOIN_TYPE_AND
        self.filters_function_map = []

    def execute(self, parameters):
        if not parameters:
            parameters = {}

        self.parse_parameters(parameters)
        self.get_filter_functions_map()

        logger.debug('join type: %s' % JOIN_TYPE_CHOICES[self.join_type])

        query_results = set()

        logger.debug('self.filters_function_map: %s' % self.filters_function_map)

        for filter_entry in self.filters_function_map:
            filter_results = []

            filter_operation = filter_entry['operation']

            for row_id, item in enumerate(self.source.queryset):
                try:
                    value = item.row

                    for index, part in enumerate(filter_entry['field'].split('.')):
                        if part == '_length':
                            value = geometry.shape(value).length
                        elif part == '_area':
                            value = geometry.shape(value).area
                        elif part == '_type':
                            value = geometry.shape(value).geom_type
                        else:
                            value = value[part]
                except (AttributeError, TypeError):
                    # A dotted attribute is not found
                    raise Http400('Invalid element: %s' % filter_entry['field'])
                else:
                    # Evaluate row values against the established filters
                    if filter_operation.evaluate(value):
                        filter_results.append(row_id)

            if query_results:
                if self.join_type == JOIN_TYPE_AND:
                    query_results &= set(filter_results)
                else:
                    query_results |= set(filter_results)
            else:
                query_results = set(filter_results)

        logger.debug('query_results: %s' % query_results)
        self.get_data(query_results)
        self.process_groups()
        self.process_aggregates()
        self.process_json_path()

        return self.data

    def process_json_path(self):
        if self.json_path:
            try:
                expression = jsonpath_rw.parse(self.json_path)

                if isinstance(self.data, (types.GeneratorType)):
                    self.data = [match.value for match in expression.find(list(self.data))]
                else:
                    self.data = [match.value for match in expression.find(self.data)]
            except Exception as exception:
                raise Http400('JSON query error; %s' % exception)

    def process_aggregates(self):
        if self.aggregates:
            if self.groups:
                new_result = {}
                for group in self.groups:
                    new_result.setdefault(group, {})
                    for group_result in self.data[group]:
                        for aggregate in self.aggregates:
                            new_result[group].setdefault(group_result, {})
                            new_result[group][group_result][aggregate['name']] = aggregate['function'].execute(self.data[group][group_result])
                self.data = new_result
            else:
                new_result = {}
                for aggregate in self.aggregates:
                    # Make a backup of the generator
                    self.data, backup = tee(self.data)
                    new_result[aggregate['name']] = aggregate['function'].execute(backup)
                self.data = new_result

    def process_groups(self):
        if self.groups:
            result = {}
            for group in self.groups:
                self.data, backup = tee(self.data)
                # Make a backup of the generator
                result[group] = {}
                sorted_data = sorted(backup, key=itemgetter(group))

                for key, group_data in groupby(sorted_data, lambda x: x[group]):
                    result[group][key] = list(group_data)

            self.data = result

    def get_data(self, query_results):
        if self.filters:
            if len(query_results) == 1:
                # Special case because itemgetter doesn't returns a list but a value
                self.data = (item.row for item in [itemgetter(*list(query_results))(self.source.queryset)])
            elif len(query_results) == 0:
                self.data = []
            else:
                self.data = (item.row for item in itemgetter(*list(query_results))(self.source.queryset)[0:self.source.limit])
        else:
            self.data = (item.row for item in self.source.queryset[0:self.source.limit])

    def parse_parameters(self, parameters):
        for parameter, value in parameters.items():
            logger.debug('parameter: %s' % parameter)
            logger.debug('value: %s' % value)

            if parameter.startswith(LQL_DELIMITER):
                # Single delimiter? It is a predicate

                if parameter == LQL_DELIMITER + 'join':
                # Determine query join type
                    if value.upper() == 'OR':
                        join_type = JOIN_TYPE_OR
                elif parameter == LQL_DELIMITER + 'json_path':
                # Determine fields to return
                    self.json_path = value
                elif parameter == LQL_DELIMITER + 'group_by':
                    self.groups = value.split(',')
                elif parameter.startswith(LQL_DELIMITER + 'aggregate'):
                    # TODO: Use QueryDict lists instead of Regex
                    # example: _aggregate__count=Count(*)
                    name = parameter.split(DOUBLE_DELIMITER)[1]
                    aggregate_string = value

                    if value.startswith('Count('):
                        self.aggregates.append({
                            'name': name,
                            'function': Count(value.replace('Count(', '').replace(')', ''))
                        })
                    elif value.startswith('Sum('):
                        self.aggregates.append({
                            'name': name,
                            'function': Sum(value.replace('Sum(', '').replace(')', ''))
                        })
                    else:
                        raise Http400('Unkown aggregate: %s' % value)
            elif DOUBLE_DELIMITER in parameter:
                # Not an aggregate? Then it is a filter
                try:
                    field, filter_name = parameter.split(DOUBLE_DELIMITER)
                except ValueError:
                    # Trying more than one filter per field
                    # This could be supported eventually, for now it's an error
                    raise Http400('Only one filter per field is supported')
                else:
                    try:
                        value = parse_value(value)
                    except Exception as exception:
                        raise Http400('Malformed query: %s' % exception)
                    else:
                        self.filters.append({'field': field, 'filter_name': filter_name, 'filter_value': value})
            else:
                # Otherwise it is an 'equality (=)' filter
                try:
                    value = parse_value(value)
                except Exception as exception:
                    raise Http400('Malformed query; %s' % exception)
                else:
                    self.filters.append({'field': parameter, 'filter_name': 'equals', 'filter_value': value})

    def get_filter_functions_map(self):
        for filter_entry in self.filters:
            filters_dictionary = {'field': filter_entry['field'], 'filter_name': filter_entry['filter_name'], 'filter_value': filter_entry['filter_value']}
            try:
                filter_identifier = FILTER_NAMES[filter_entry['filter_name']]
            except KeyError:
                raise Http400('Unknown filter: %s' % filter_entry['filter_name'])
            else:
                filters_dictionary['operation'] = FILTER_CLASS_MAP[filter_identifier](filter_entry['field'], filter_entry['filter_value'])
                self.filters_function_map.append(filters_dictionary)

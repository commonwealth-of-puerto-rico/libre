from __future__ import absolute_import

from itertools import groupby, izip, tee
import logging
from operator import itemgetter

from shapely import geometry

from .aggregates import Count, Sum
from .exceptions import Http400
from .filters import FILTER_CLASS_MAP, FILTER_NAMES
from .jsonq import JSONq
from .literals import (DOUBLE_DELIMITER, JOIN_TYPE_AND, JOIN_TYPE_CHOICES,
    JOIN_TYPE_OR, LQL_DELIMITER)
from .utils import parse_value

logger = logging.getLogger(__name__)


class Query():
    def __init__(self, data, limit, klass):
        self.data = data
        self.limit = limit
        self.klass = klass

    def execute(self, parameters):
        if not parameters:
            parameters = {}

        self.parse_parameters(parameters)
        self.get_filter_functions_map()

        logger.debug('join type: %s' % JOIN_TYPE_CHOICES[self.join_type])

        query_results = set()

        for post_filter in self.filters_function_map:
            filter_results = []

            filter_operation = post_filter['operation']

            for row_id, item in enumerate(self.data):
                try:
                    value = item.row

                    for index, part in enumerate(post_filter['field'].split('.')):
                        if part == '_length':
                            value = geometry.shape(value).length
                        elif part == '_area':
                            value = geometry.shape(value).area
                        elif part == '_type':
                            value = geometry.shape(value).geom_type
                        else:
                            try:
                                value = value[part]
                            except KeyError:
                                # Error in the first part of the field name
                                # Check to see if it is a source slug reference
                                if index == 0:
                                    if part != self.slug:
                                        try:
                                            source = self.klass.objects.get_subclass(slug=part)
                                        except self.klass.DoesNotExist:
                                            raise Http400('Unknown source: %s' % part)
                                        else:
                                            return source.get_all(parameters=parameters)
                                else:
                                    raise Http400('Invalid element: %s' % post_filter['field'])
                except (AttributeError, TypeError):
                    # A dotted attribute is not found
                    raise Http400('Invalid element: %s' % post_filter['field'])
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

        data = self.get_data(self.data, query_results)

        data = self.process_groups(data)

        data = self.process_aggregates(data)

        data = self.process_field_filtering(data)

        return data

    def process_field_filtering(self, data):
        if not self.field_query:
            return data
        else:
            jsonq = JSONq(data)
            try:
                return jsonq.query(self.field_query, do_filter=True)
            except ValueError as exception:
                raise Http400('Filter query error; %s' % exception)


    def process_aggregates(self, data):
        if self.aggregates:
            if not self.groups:
                new_result = {}
                for aggregate in self.aggregates:
                    # Make a backup of the generator
                    data, backup = tee(data)
                    new_result[aggregate['name']] = aggregate['function'].execute(backup)
                return new_result
            else:
                new_result = {}
                for group in self.groups:
                    new_result.setdefault(group, {})
                    for group_result in data[group]:
                        for aggregate in self.aggregates:
                            new_result[group].setdefault(group_result, {})
                            new_result[group][group_result][aggregate['name']] = aggregate['function'].execute(data[group][group_result])

                return new_result
        else:
            return data

    def process_groups(self, data):
        if self.groups:
            result = {}
            for group in self.groups:
                data, backup = tee(data)
                # Make a backup of the generator
                result[group] = {}
                sorted_data = sorted(backup, key=itemgetter(group))

                for key, group_data in groupby(sorted_data, lambda x: x[group]):
                    result[group][key] = list(group_data)

            return result
        else:
            return data

    def get_data(self, queryset, query_results):
        if self.filters:
            if len(query_results) == 1:
                # Special case because itemgetter doesn't returns a list but a value
                return (item.row for item in [itemgetter(*list(query_results))(queryset)])
            elif len(query_results) == 0:
                return []
            else:
                return (item.row for item in itemgetter(*list(query_results))(queryset)[0:self.limit])
        else:
            return (item.row for item in queryset[0:self.limit])

    def parse_parameters(self, parameters):
        aggregates = []
        field_query = None
        filters = []
        groups = []

        join_type = JOIN_TYPE_AND

        for parameter, value in parameters.items():
            logger.debug('parameter: %s' % parameter)
            logger.debug('value: %s' % value)

            if parameter.startswith(LQL_DELIMITER):
                # Single delimiter? It is a predicate

                if parameter == LQL_DELIMITER + 'join':
                # Determine query join type
                    if value.upper() == 'OR':
                        join_type = JOIN_TYPE_OR
                elif parameter == LQL_DELIMITER + 'fields':
                # Determine fields to return
                    field_query = value.split(',')
                elif parameter == LQL_DELIMITER + 'group_by':
                    groups = value.split(',')
                elif parameter.startswith(LQL_DELIMITER + 'aggregate'):
                    # TODO: Use QueryDict lists instead of Regex
                    # example: _aggregate__count=Count(*)
                    name = parameter.split(DOUBLE_DELIMITER)[1]
                    aggregate_string = value

                    if value.startswith('Count('):
                        aggregates.append({
                            'name': name,
                            'function': Count(value.replace('Count(', '').replace(')', '').split(','))
                        })
                    elif value.startswith('Sum('):
                        aggregates.append({
                            'name': name,
                            'function': Sum(value.replace('Sum(', '').replace(')', '').split(','))
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
                    filters.append({'field': field, 'filter_name': filter_name, 'value': value})
            else:
                # Otherwise it is an equal filter
                filters.append({'field': parameter, 'filter_name': 'equals', 'value': value})

                try:
                    value = parse_value(value)
                except IndexError:
                    raise Http400('Malformed query')







        self.filters = filters
        self.field_query = field_query
        self.join_type = join_type
        self.aggregates = aggregates
        self.groups = groups


    def get_filter_functions_map(self):
        for post_filter in self.filters:
            try:
                filter_identifier = FILTER_NAMES[post_filter['filter_name']]
            except KeyError:
                raise Http400('Unknown filter: %s' % post_filter['filter_name'])
            else:
                post_filter['operation'] = FILTER_CLASS_MAP[filter_identifier](post_filter['field'], post_filter['value'])

        self.filters_function_map = self.filters

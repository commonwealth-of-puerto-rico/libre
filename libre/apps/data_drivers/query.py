from __future__ import absolute_import

from itertools import groupby, izip, tee
import logging
from operator import itemgetter

from shapely import geometry

from .aggregates import Count, Sum
from .exceptions import Http400
from .filters import FILTER_CLASS_MAP, FILTER_NAMES
from .literals import (DOUBLE_DELIMITER, JOIN_TYPE_AND, JOIN_TYPE_CHOICES, JOIN_TYPE_OR, LQL_DELIMITER)

from .utils import parse_value

logger = logging.getLogger(__name__)


class Query():
    def __init__(self, data, limit):
        self.data = data
        self.limit = limit

    def execute(self, parameters):
        if not parameters:
            parameters = {}

        filters, fields_to_return, join_type, aggregates, groups = parse_parameters(parameters)
        filters_function_map = get_filter_functions_map(filters)

        logger.debug('join type: %s' % JOIN_TYPE_CHOICES[join_type])

        query_results = set()
        for post_filter in filters_function_map:
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
                                            source = Source.objects.get_subclass(slug=part)
                                        except Source.DoesNotExist:
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
                if join_type == JOIN_TYPE_AND:
                    query_results &= set(filter_results)
                else:
                    query_results |= set(filter_results)
            else:
                query_results = set(filter_results)

        if not fields_to_return:
            fields_lambda = lambda x: x
        else:
            fields_lambda = make_fields_filter(fields_to_return)

        data = self.get_data(self.data, filters, query_results, fields_lambda)
        if groups:
            result = {}
            for group in groups:
                data, backup = tee(data)
                # Make a backup of the generator
                result[group] = {}
                sorted_data = sorted(backup, key=itemgetter(group))

                for key, group_data in groupby(sorted_data, lambda x: x[group]):
                    result[group][key] = list(group_data)
        else:
            result = data

        if aggregates:
            if not groups:
                new_result = {}
                for aggregate in aggregates:
                    # Make a backup of the generator
                    data, backup = tee(data)
                    new_result[aggregate['name']] = aggregate['function'].execute(backup)
                return new_result
            else:
                new_result = {}
                for group in groups:
                    new_result.setdefault(group, {})
                    for group_result in result[group]:
                        for aggregate in aggregates:
                            new_result[group].setdefault(group_result, {})
                            new_result[group][group_result][aggregate['name']] = aggregate['function'].execute(result[group][group_result])

                return new_result
        return result

    def get_data(self, queryset, filters, query_results, fields_lambda):
        if filters:
            if len(query_results) == 1:
                # Special case because itemgetter doesn't returns a list but a value
                return (fields_lambda(item.row) for item in [itemgetter(*list(query_results))(queryset)])
            elif len(query_results) == 0:
                return []
            else:
                return (fields_lambda(item.row) for item in itemgetter(*list(query_results))(queryset)[0:self.limit])
        else:
            return (fields_lambda(item.row) for item in queryset[0:self.limit])


def parse_parameters(parameters):
    aggregates = []
    fields_to_return = []
    filters = []
    groups = []

    join_type = JOIN_TYPE_AND

    for parameter, value in parameters.items():
        logger.debug('parameter: %s' % parameter)
        logger.debug('value: %s' % value)

        if not parameter.startswith(LQL_DELIMITER):
            try:
                value = parse_value(value)
            except IndexError:
                raise Http400('Malformed query')

            if not parameter.startswith(LQL_DELIMITER):
                if DOUBLE_DELIMITER not in parameter:
                    filters.append({'field': parameter, 'filter_name': 'equals', 'value': value})
                else:
                    try:
                        field, filter_name = parameter.split(DOUBLE_DELIMITER)
                    except ValueError:
                        # Trying more than one filter per field
                        # This could be supported eventually, for now it's an error
                        raise Http400('Only one filter per field is supported')
                    else:
                        filters.append({'field': field, 'filter_name': filter_name, 'value': value})
        else:
            if parameter == LQL_DELIMITER + 'join':
            # Determine query join type
                if value.upper() == 'OR':
                    join_type = JOIN_TYPE_OR
            elif parameter == LQL_DELIMITER + 'fields':
            # Determine fields to return
                fields_to_return = value.split(',')
            elif parameter == LQL_DELIMITER + 'group_by':
                groups = value.split(',')
            elif parameter == LQL_DELIMITER + 'aggregate':
                # TODO: switch to regular expression
                # Use QueryDict lists instead of Regex
                for element in value.strip()[1:-1].split(','):
                    name, aggregate_string = element.split(':')
                    if aggregate_string.startswith('Count('):
                        aggregates.append({
                            'name': name.strip()[1:-1],
                            'function': Count(aggregate_string.replace('Count(', '').replace(')', '').split(','))
                        })
                    elif aggregate_string.startswith('Sum('):
                        aggregates.append({
                            'name': name.strip()[1:-1],
                            'function': Sum(aggregate_string.replace('Sum(', '').replace(')', '').split(','))
                        })

    return filters, fields_to_return, join_type, aggregates, groups


def get_filter_functions_map(filter_names):
    for post_filter in filter_names:
        try:
            filter_identifier = FILTER_NAMES[post_filter['filter_name']]
        except KeyError:
            raise Http400('Unknown filter: %s' % post_filter['filter_name'])
        else:
            post_filter['operation'] = FILTER_CLASS_MAP[filter_identifier](post_filter['field'], post_filter['value'])

    return filter_names


def make_fields_filter(fields_to_return):
    """
    Fabricate a function tailored made to return a number of fields
    for each row.
    """
    # TODO: support multilevel dot '.', and index '[]' notation
    if len(fields_to_return) == 1:
        # Special because itemgetter with a single element doesn't return a list
        field_extract_lambda = lambda x: [itemgetter(*fields_to_return)(x)]
    else:
        field_extract_lambda = lambda x: itemgetter(*fields_to_return)(x)

    def _function(row):
        try:
            return dict(izip(fields_to_return, field_extract_lambda(row)))
        except KeyError as exception:
            raise Http400('Could not find a field named in the current row: %s' % exception)
    return _function

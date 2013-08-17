from __future__ import absolute_import

from itertools import groupby, imap, islice, izip, tee
import logging
from operator import itemgetter
import types

from django.conf import settings

import jsonpath_rw

from .aggregates import AGGREGATES_NAMES
from .exceptions import Http400
from .filters import FILTER_CLASS_MAP, FILTER_NAMES
from .literals import (DOUBLE_DELIMITER, JOIN_TYPE_AND, JOIN_TYPE_CHOICES,
    JOIN_TYPE_OR)
from .settings import LQL_DELIMITER
from .utils import attrib_sorter, parse_value, return_attrib

logger = logging.getLogger(__name__)


class Query():
    def __init__(self, source):
        self.source = source
        self.json_path = None
        self.aggregates = []
        self.filters = []
        self.groups = []
        self.join_type = JOIN_TYPE_AND
        self.filters_function_map = []
        self.as_dict_list = self.as_nested_list = False

    def execute(self, parameters):
        if not parameters:
            parameters = {}

        self.parse_query(parameters)
        self.get_filter_functions_map()

        logger.debug('join type: %s' % JOIN_TYPE_CHOICES[self.join_type])

        query_results = set()

        logger.debug('self.filters_function_map: %s' % self.filters_function_map)

        for filter_entry in self.filters_function_map:
            filter_results = []

            filter_operation = filter_entry['operation']

            for row_id, item in enumerate(self.source.queryset.iterator()):
                try:
                    value = return_attrib(item.row, filter_entry['field'])
                except (AttributeError, TypeError, KeyError):
                    # A dotted attribute is not found
                    raise Http400('Invalid element: %s' % filter_entry['field'])
                else:
                    # Evaluate row values against the established filters
                    if filter_operation.evaluate(value):
                        filter_results.append(row_id)

            # Store filter results as a list of row id numbers
            # Not a generator based system, but shouldn't use too much memory
            # up to several millions ids
            if query_results:
                if self.join_type == JOIN_TYPE_AND:
                    query_results &= set(filter_results)
                else:
                    query_results |= set(filter_results)
            else:
                query_results = set(filter_results)

        iterator = self.process_transform(
            self.process_json_path(
                self.process_aggregates(
                    self.process_groups(
                        self.data_iterator(query_results)
                    )
                )
            )
        )

        return iterator

    def parse_query(self, parameters):
        for parameter, value in parameters.items():
            logger.debug('parameter: %s' % parameter)
            logger.debug('value: %s' % value)

            if parameter.startswith(LQL_DELIMITER):
                # Single delimiter? It is a predicate

                if parameter == LQL_DELIMITER + 'join':
                # Determine query join type
                    if value.upper() == 'OR':
                        self.join_type = JOIN_TYPE_OR
                elif parameter == LQL_DELIMITER + 'json_path':
                # Determine fields to return
                    self.json_path = value
                elif parameter == LQL_DELIMITER + 'as_dict_list':
                # Flatten result set as list of dictionaries
                    self.as_dict_list = True
                elif parameter == LQL_DELIMITER + 'as_nested_list':
                # Flatten result set as nested list
                    self.as_nested_list = True
                elif parameter == LQL_DELIMITER + 'group_by':
                    self.groups = value.split(',')
                elif parameter.startswith(LQL_DELIMITER + 'aggregate'):
                    # example: _aggregate__count=Count(*)
                    try:
                        output_name = parameter.split(DOUBLE_DELIMITER, 1)[1]
                    except IndexError:
                        raise Http400('Must specify a result name separated by a double delimiter')

                    if any(map(value.startswith, AGGREGATES_NAMES)):  # Is it any of the known aggregate names?
                        aggregate_name, value = value.split('(', 1)
                        value = value[:-1]  # remove last parentheses from value

                        self.aggregates.append({
                            'name': output_name,
                            'function': AGGREGATES_NAMES[aggregate_name](value)
                        })
                    else:
                        raise Http400('Unknown aggregate: %s' % value)
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
                        if getattr(settings, 'DEBUG', False):
                            raise
                        else:
                            raise Http400('Malformed query: %s' % exception)
                    else:
                        self.filters.append({'field': field, 'filter_name': filter_name, 'filter_value': value})
            else:
                # Otherwise it is an 'equality (=)' filter
                try:
                    value = parse_value(value)
                except Exception as exception:
                    if getattr(settings, 'DEBUG', False):
                        raise
                    else:
                        raise Http400('Malformed query: %s' % exception)
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

    def data_iterator(self, query_results):
        count = 0
        for row_id, item in enumerate(self.source.queryset.iterator()):
            if row_id in query_results or not self.filters_function_map:
                count += 1
                yield item.row
                if count >= self.source.limit:
                    break

    def process_groups(self, iterator):
        if self.groups:
            return self._group_generator(iterator)
        else:
            return iterator

    def _group_generator(self, iterator):
        for group in self.groups:
            iterator, backup = tee(iterator)
            # Make a backup of the generator
            sorted_data = attrib_sorter(backup, key=group)
            group_dictionary = {'name': group, 'values': []}

            for key, group_data in groupby(sorted_data, lambda x: x[group]):
                group_dictionary['values'].append({'value': key, 'elements': list(group_data)})

            yield group_dictionary

    def process_aggregates(self, iterator):
        if self.aggregates:
            return self._aggregates_generator(iterator)
        else:
            return iterator

    def _aggregates_generator(self, iterator):
        if self.groups:
            result = []
            for group in iterator:
                for group_value in group['values']:
                    group_value['aggregates'] = []
                    for aggregate in self.aggregates:
                        group_value['aggregates'].append({aggregate['name']: aggregate['function'].execute(group_value['elements'])})
                yield group
        else:
            result = {}
            for aggregate in self.aggregates:
                # Make a backup of the generator
                iterator, backup = tee(iterator)
                result[aggregate['name']] = aggregate['function'].execute(backup)
            yield result

    def process_json_path(self, iterator):
        if self.json_path:
            try:
                expression = jsonpath_rw.parse(self.json_path)

                # TODO: test this with the new iterator based pipeline
                if isinstance(iterator, (types.GeneratorType)):
                    results = [match.value for match in expression.find(list(iterator))]
                else:
                    results = [match.value for match in expression.find(iterator)]
            except Exception as exception:
                raise Http400('JSON query error; %s' % exception)
            else:
                if len(results) == 1:
                    return results[0]
                else:
                    return results
        else:
            return iterator

    def process_transform(self, iterator):
        if self.as_dict_list:
            data_iterable = iter(iterator)
            return imap(lambda x: {x[0]: x[1]}, izip(data_iterable, data_iterable))
        elif self.as_nested_list:
            data_iterable = iter(iterator)
            return izip(data_iterable, data_iterable)
        else:
            return iterator

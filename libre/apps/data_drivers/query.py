from __future__ import absolute_import

import logging

from dateutil.parser import parse
from shapely import geometry

from .filters import FILTER_CLASS_MAP, FILTER_NAMES
from .literals import DOUBLE_DELIMITER, JOIN_TYPE_AND, LQL_DELIMITER
from .utils import parse_value

logger = logging.getLogger(__name__)


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
    result = []
    for post_filter in filter_names:
        filter_results = []

        try:
            filter_identifier = FILTER_NAMES[post_filter['filter_name']]
        except KeyError:
            raise Http400('Unknown filter: %s' % post_filter['filter_name'])
        else:
            post_filter['operation'] = FILTER_CLASS_MAP[filter_identifier](post_filter['field'], post_filter['value'])

    return filter_names

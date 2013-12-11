from __future__ import absolute_import

from HTMLParser import HTMLParser
import logging
from operator import itemgetter
import types
from urllib import unquote_plus

from dateutil.parser import parse
import pyparsing
from shapely import geometry

from .literals import (DATA_TYPE_DATE, DATA_TYPE_DATETIME, DATA_TYPE_NUMBER, DATA_TYPE_STRING,
    DATA_TYPE_TIME, THOUSAND_SYMBOL, DECIMAL_SYMBOL)
from .exceptions import LIBREValueError

logger = logging.getLogger(__name__)

enclosed_parser = pyparsing.Forward()
nestedBrackets = pyparsing.nestedExpr('[', ']', content=enclosed_parser)
enclosed_parser << (pyparsing.Word(pyparsing.alphanums + '-' + '.' + '(' + ')') | ',' | nestedBrackets)

DATA_TYPE_FUNCTIONS = {
    DATA_TYPE_STRING: lambda x: unicode(x).strip(),
    DATA_TYPE_NUMBER: lambda x: convert_to_number(x),
    DATA_TYPE_DATETIME: lambda x: parse(x),
    DATA_TYPE_DATE: lambda x: parse(x).date(),
    DATA_TYPE_TIME: lambda x: parse(x).time(),
}
html_parser = HTMLParser()


def parse_enclosed(string):
    return enclosed_parser.parseString(string).asList()


def convert_to_number(data):
    if isinstance(data, (types.IntType, types.FloatType, types.LongType)):
        # Is already a number
        return data
    else:
        # Must be a string or unicode
        # Get rid of dollar signs and thousand separators
        data = data.replace(THOUSAND_SYMBOL, '').replace('$', '')

        if '(' and ')' in data:
            # Is a negative number
            return -convert_to_number(data.replace(')', '').replace('(', ''))
        else:
            if DECIMAL_SYMBOL in data:
                # It is a decimal number
                return float(data)
            else:
                # Otherwise it is an integer
                return int(data)


def parse_value(string):
    # Hidden import to avoid circular imports between model.py <- query.py <- this module <- model.py
    from .models import Source

    string = html_parser.unescape(string).strip()

    logger.debug('parsing: %s' % string)
    if string[0] == '"' and string[-1] == '"':
        # Strip quotes
        return unicode(string[1:-1])

    elif string == 'True':
        return True

    elif string == 'False':
        return False

    elif any(map(string.startswith, ['Point', 'LineString', 'LinearRings', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 'Geometry'])):
        logger.debug('is a geometry')
        return parse_as_geometry(string)

    elif string[0] == '[' and string[-1] == ']':
        # Is a list of values
        logger.debug('Is a list')

        result = []

        for string in parse_enclosed(string)[0]:
            if string != ',':  # Single comma, don't process
                if ',' in string:
                    # is a nested list, recompose
                    result.append(parse_value('[%s]' % (''.join(string))))
                else:
                    # is a single element, parse as is
                    result.append(parse_value(string))

        return list(result)
    elif string.startswith('DateTime'):
        # Is a datetime
        logger.debug('Is a datetime')
        date_string = string.replace('DateTime(', '').replace(')', '')
        return parse(date_string)
    elif string.startswith('Date'):
        # Is a date
        logger.debug('Is a date')
        date_string = string.replace('Date(', '').replace(')', '')
        return parse(date_string).date()
    elif string.startswith('Time'):
        # Is a time
        logger.debug('Is a time')
        date_string = string.replace('Time(', '').replace(')', '')
        return parse(date_string).time()
    elif string[0] == '<' and string[-1] == '>':
        # Is a subquery
        logger.debug('Is a subquery')
        string = string[1:-1]
        # Check for reference
        parts = string.split('&')
        source_slug = parts[0]

        try:
            new_source = Source.objects.get_subclass(slug=source_slug)
        except Source.DoesNotExist:
            logger.error('no source named: %s' % source_slug)
            raise LIBREValueError('no source named: %s' % source_slug)
        else:
            logger.debug('got new source named: %s' % source_slug)
            # Rebuild the parameters for this enclosed value, omitting the source slug
            new_string = u'&'.join(parts[1:])

            parameters = {}
            for part in new_string.split('&'):
                try:
                    key, value = part.split('=')
                except ValueError:
                    pass
                else:
                    parameters[key] = value

            return new_source.get_all(parameters=parameters)
    else:
        logger.debug('Is a number')
        try:
            return convert_to_number(string)
        except ValueError:
            logger.error('Invalid value or unknown source: %s' % string)
            raise LIBREValueError('Invalid value or unknown source: %s' % string)


def parse_as_geometry(string):
    geometry_name, value = string.split('(', 1)
    logger.debug('geometry name: %s' % geometry_name)

    # Get the geometry class from the 'shapely.geometry' module
    geometry_class = getattr(geometry, geometry_name, geometry.shape)

    # Check if the geometry data is also specifing a buffer
    buffer_size = None
    if '.buffer(' in value:
        value, buffer_size = value.split('.buffer(')
        buffer_size = buffer_size[:-1]  # Strip closing parenthesis

    value = value[:-1]  # Strip closing parenthesis

    try:
        value = geometry_class(parse_value(value))
    except Exception as exception:
        raise LIBREValueError('Unable to parse value: %s as a geometry; %s' % (value, exception))

    if buffer_size:
        value = value.buffer(float(buffer_size))

    return value


def split_qs(string, delimiter='&'):
    """Split a string by the specified unquoted, not enclosed delimiter"""

    open_list = '[<{('
    close_list = ']>})'
    quote_chars = '"\''

    level = index = last_index = 0
    quoted = False
    result = []

    for index, letter in enumerate(string):
        if letter in quote_chars:
            if not quoted:
                quoted = True
                level += 1
            else:
                quoted = False
                level -= 1
        elif letter in open_list:
            level += 1
        elif letter in close_list:
                level -= 1
        elif letter == delimiter and level == 0:
            # Split here
            element = string[last_index: index]
            if element:
                result.append(element)
            last_index = index + 1

    if index:
        element = string[last_index: index + 1]
        if element:
            result.append(element)

    return result


def parse_qs(string):
    """Intelligently parse the query string"""
    result = {}

    for item in split_qs(string):
        # Split the query string by unquotes ampersants ('&')
        try:
            # Split the item by unquotes equal signs
            key, value = split_qs(item, delimiter='=')
        except ValueError:
            # Single value without equals sign
            result[item] = ''
        else:
            result[key] = value

    return result


def parse_request(request):
    return parse_qs(unquote_plus(request.META['QUERY_STRING']))


def get_value(obj, attrib):
    try:
        return obj[attrib]
    except (KeyError, TypeError):
        try:
            return getattr(obj, attrib)
        except AttributeError:
            raise LIBREValueError('field has no attribute: %s' % attrib)


def return_attrib(obj, attrib):
    return reduce(get_value, attrib.split(u'.'), obj)


def attrib_sorter(data, key):
    try:
        if '.' in key:
            # Sort by an element property
            logger.debug('has point')
            variable, properties = key.split('.', 1)
            logger.debug('variable, properties: %s, %s' % (variable, properties))
            data = (dict(item, **{key: return_attrib(itemgetter(variable)(item), properties)}) for item in data)
        return sorted(data, key=itemgetter(key))
    except KeyError:
        raise LIBREValueError('Unknown field name or field property: %s' % key)

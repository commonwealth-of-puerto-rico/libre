from __future__ import absolute_import

from shapely.prepared import prep

from .exceptions import LQLFilterError

# Discreet values
FILTER_CONTAINS = 1
FILTER_ICONTAINS = 2
FILTER_STARTSWITH = 3
FILTER_ISTARTSWITH = 4
FILTER_ENDSWITH = 5
FILTER_IENDSWITH = 6
FILTER_LT = 7
FILTER_LTE = 8
FILTER_GT = 9
FILTER_GTE = 10
FILTER_IN = 11
FILTER_EQUALS = 12
FILTER_RANGE = 13
FILTER_HAS = 17
FILTER_DISJOINT = 18
FILTER_INTERSECTS = 19
FILTER_TOUCHES = 20
FILTER_WITHIN = 21
FILTER_IEQUALS = 22

FILTER_NAMES = {
    'contains': FILTER_CONTAINS,
    'icontains': FILTER_ICONTAINS,
    'startswith': FILTER_STARTSWITH,
    'istartswith': FILTER_ISTARTSWITH,
    'endswith': FILTER_ENDSWITH,
    'iendswith': FILTER_IENDSWITH,
    'iequals': FILTER_IEQUALS,
    'lt': FILTER_LT,
    'lte': FILTER_LTE,
    'gt': FILTER_GT,
    'gte': FILTER_GTE,
    'in': FILTER_IN,
    'equals': FILTER_EQUALS,  # TODO: Add support for aliases  '='
    'range': FILTER_RANGE,
    'has': FILTER_HAS,
    'disjoint': FILTER_DISJOINT,
    'intersects': FILTER_INTERSECTS,
    'touches': FILTER_TOUCHES,
    'within': FILTER_WITHIN,
}


class Filter():
    def __init__(self, field, filter_value, negation):
        self.field = field
        self.filter_value = filter_value
        self.negation = negation
        if negation:
            self.evaluate = lambda x: not(self._evaluate(x))
        else:
            self.evaluate = self._evaluate


# String filters
class Contains(Filter):
    def _evaluate(self, value):
        try:
            return self.filter_value in value
        except TypeError:
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


class IContains(Filter):
    def _evaluate(self, value):
        try:
            return self.filter_value.upper() in value.upper()
        except (TypeError, AttributeError):
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


class Startswith(Filter):
    def _evaluate(self, value):
        try:
            return value.startswith(self.filter_value)
        except TypeError:
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


class IStartswith(Filter):
    def _evaluate(self, value):
        try:
            return value.upper().startswith(self.filter_value.upper())
        except (TypeError, AttributeError):
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


class Endswith(Filter):
    def _evaluate(self, value):
        try:
            return value.endswith(self.filter_value)
        except TypeError:
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


class IEndswith(Filter):
    def _evaluate(self, value):
        try:
            return value.upper().endswith(self.filter_value.upper())
        except (TypeError, AttributeError):
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


class IEquals(Filter):
    def _evaluate(self, value):
        try:
            return value.upper() == self.filter_value.upper()
        except (TypeError, AttributeError):
            if not isinstance(self.filter_value, basestring):
                raise LQLFilterError('This filter is meant to be used with string data type values.')


# Number filters
class LessThan(Filter):
    def _evaluate(self, value):
        return value < self.filter_value


class LessThanOrEqual(Filter):
    def _evaluate(self, value):
        return value <= self.filter_value


class GreaterThan(Filter):
    def _evaluate(self, value):
        return value > self.filter_value


class GreaterThanOrEqual(Filter):
    def _evaluate(self, value):
        return value >= self.filter_value


# Other
class In(Filter):
    def _evaluate(self, value):
        try:
            return value in self.filter_value
        except TypeError:
            raise LQLFilterError('Invalid value type for specified filter or field.')


class Equals(Filter):
    def _evaluate(self, value):
        return self.filter_value == value


class Range(Filter):
    def _evaluate(self, value):
        try:
            return value >= self.filter_value[0] and value <= self.filter_value[1]
        except (TypeError, IndexError):
            raise LQLFilterError('Range filter value must be a list of 2 values.')


# Spatial filters
class Has(Filter):
    def _evaluate(self, value):
        try:
            return value.contains(self.filter_value)
        except AttributeError:
            raise LQLFilterError('field: %s, is not a geometry' % self.field)


class Disjoint(Filter):
    def _evaluate(self, value):
        try:
            return value.disjoint(self.filter_value)
        except AttributeError:
            raise LQLFilterError('field: %s, is not a geometry' % self.field)


class Intersects(Filter):
    def _evaluate(self, value):
        try:
            return value.intersects(self.filter_value)
        except AttributeError:
            raise LQLFilterError('field: %s, is not a geometry' % self.field)


class Touches(Filter):
    def _evaluate(self, value):
        try:
            return value.touches(self.filter_value)
        except AttributeError:
            raise LQLFilterError('field: %s, is not a geometry' % self.field)


class Within(Filter):
    def __init__(self, field, filter_value, negation):
        self.field = field
        self.filter_value = filter_value
        self.prepared = prep(self.filter_value)
        self.negation = negation
        if negation:
            self.evaluate = lambda x: not(self._evaluate(x))
        else:
            self.evaluate = self._evaluate

    def _evaluate(self, value):
        try:
            return self.prepared.contains(value)
        except AttributeError:
            raise LQLFilterError('field: %s, is not a geometry' % self.field)


FILTER_CLASS_MAP = {
    # String
    FILTER_CONTAINS: Contains,
    FILTER_ICONTAINS: IContains,
    FILTER_STARTSWITH: Startswith,
    FILTER_ISTARTSWITH: IStartswith,
    FILTER_ENDSWITH: Endswith,
    FILTER_IENDSWITH: IEndswith,
    FILTER_IEQUALS: IEquals,
    # Number
    FILTER_LT: LessThan,
    FILTER_LTE: LessThanOrEqual,
    FILTER_GT: GreaterThan,
    FILTER_GTE: GreaterThanOrEqual,
    # Other
    FILTER_IN: In,
    FILTER_EQUALS: Equals,
    FILTER_RANGE: Range,
    # Spatial
    FILTER_HAS: Has,
    FILTER_DISJOINT: Disjoint,
    FILTER_INTERSECTS: Intersects,
    FILTER_TOUCHES: Touches,
    FILTER_WITHIN: Within,
}

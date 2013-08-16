from __future__ import absolute_import

from operator import itemgetter

from .exceptions import LIBREFieldError
from .utils import return_attrib


class Aggregate(object):
    def __init__(self, argument):
        self.argument = argument
        self.field = argument
        self.properties = None

        if '.' in self.argument:
            # Aggregate by an element property
            self.field, self.properties = self.argument.split('.', 1)

    def execute(self, elements):
        try:
            return self._execute(elements)
        except KeyError:
            raise LIBREFieldError('Unknown field: %s' % self.argument)
        except AttributeError as exception:
            raise LIBREFieldError('Field property error; %s' % exception)
        except TypeError as exception:
            raise LIBREFieldError('Field aggregation error; %s' % exception)


class Count(Aggregate):
    def _execute(self, elements):
        if self.argument == '*':
            return len(list(elements))
        else:
            if self.properties:
                return len(set([return_attrib(itemgetter(self.field)(element), self.properties) for element in elements]))
            else:
                return len(set([element[self.argument] for element in elements if element[self.argument]]))


class Sum(Aggregate):
    def _execute(self, elements):
        if self.properties:
            return sum([return_attrib(itemgetter(self.field)(element), self.properties) for element in elements])
        else:
            return sum([element[self.argument] for element in elements if element[self.argument]])


class Max(Aggregate):
    def _execute(self, elements):
        if self.properties:
            return max([return_attrib(itemgetter(self.field)(element), self.properties) for element in elements])
        else:
            return max([element[self.argument] for element in elements if element[self.argument]])


class Min(Aggregate):
    def _execute(self, elements):
        if self.properties:
            return min([return_attrib(itemgetter(self.field)(element), self.properties) for element in elements])
        else:
            return min([element[self.argument] for element in elements if element[self.argument]])


class Average(Aggregate):
    def _execute(self, elements):
        total = float(0)

        count = 0
        if self.properties:
            for count, element in enumerate(elements, 1):
                total = total + return_attrib(itemgetter(self.field)(element), self.properties)
        else:
            for count, element in enumerate(elements, 1):
                total = total + element[self.argument]

        if count == 0:
            return float('nan')
        else:
            return total / float(count)


AGGREGATES_NAMES = {
    'Count': Count,
    'Sum': Sum,
    'Max': Max,
    'Min': Min,
    'Average': Average,
}

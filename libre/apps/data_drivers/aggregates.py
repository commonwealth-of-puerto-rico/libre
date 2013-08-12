from __future__ import absolute_import

from collections import Counter
from itertools import tee

from .exceptions import Http400


class Aggregate(object):
    def __init__(self, argument):
        self.argument = argument


class Count(Aggregate):
    def execute(self, elements):
        if self.argument == '*':
            return len(list(elements))
        else:
            try:
                return len(Counter([element[self.argument] for element in elements if element[self.argument]]).values())
            except KeyError:
                raise Http400('Unknown field: %s' % self.argument)


class Sum(Aggregate):
    def execute(self, elements):
        try:
            return sum([element[self.argument] for element in elements if element[self.argument]])
        except KeyError:
            raise Http400('Unknown field: %s' % self.argument)


class Max(Aggregate):
    def execute(self, elements):
        try:
            return max([element[self.argument] for element in elements if element[self.argument]])
        except KeyError:
            raise Http400('Unknown field: %s' % self.argument)


class Min(Aggregate):
    def execute(self, elements):
        try:
            return min([element[self.argument] for element in elements if element[self.argument]])
        except KeyError:
            raise Http400('Unknown field: %s' % self.argument)


class Average(Aggregate):
    def execute(self, elements):
        total = float(0)

        count = 0
        for count, element in enumerate(elements, 1):
            try:
                total = total + element[self.argument]
            except KeyError:
                raise Http400('Unknown field: %s' % self.argument)

        if count == 0:
            return float('nan')
        else:
            return total / float(count)



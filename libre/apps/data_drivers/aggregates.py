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
            # Make a backup of the generator
            elements, backup = tee(elements)
            try:
                return len(Counter([element[self.argument] for element in backup if element[self.argument]]).values())
            except KeyError:
                raise Http400('Unknown field: %s' % self.argument)


class Sum(Aggregate):
    def execute(self, elements):
        result = {}
        for field in self.fields:
            # Make a backup of the generator
            elements, backup = tee(elements)
            try:
                # TODO: do type convertion
                result[field] = sum([element[field] for element in backup if element[field]])
            except KeyError:
                raise Http400('Unknown field: %s' % field)
        return result

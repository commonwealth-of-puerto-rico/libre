from __future__ import absolute_import

from collections import Counter
from itertools import tee

from .exceptions import Http400


class Aggregate(object):
    def __init__(self, fields):
        self.fields = fields


class Count(Aggregate):
    def execute(self, elements):
        result = {}
        if len(self.fields) == 1 and self.fields[0] == '*':
            return len(list(elements))
        else:
            for field in self.fields:
                # Make a backup of the generator
                elements, backup = tee(elements)
                try:
                    result[field] = len(Counter([element[field] for element in backup if element[field]]).values())
                except KeyError:
                    raise Http400('Unknown field: %s' % field)
            return result


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

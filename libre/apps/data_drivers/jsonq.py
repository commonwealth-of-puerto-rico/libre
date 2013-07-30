#!/usr/bin/python

# Check out the README:
# https://github.com/edmund-huber/jsonq/blob/master/README.md

import copy
from optparse import OptionParser
import re
import sys

try:
    # simplejson is typically faster than standard-library json
    import simplejson as json
except ImportError:
    import json

class FilteredJSONObject(object):
    """Represents an incrementally built query-filtered JSON object.

    >>> f = FilteredJSONObject()
    >>> f.add_map('narf'); f.add_list(); f.add_map('zoop'); f.add_val(1);
    >>> f.get_result()
    {'narf': [{'zoop': 1}]}
    """

    def __init__(self):
        # this is the object we're building
        self.result = None

        # next place to assign is always self.tip[self.last_subscript]
        self.tip = None
        self.last_subscript = None

    def add_map(self, key):
        """Set the current object tip to be a dictionary key."""
        if self.result is None:
            self.result = self.tip = {}
            self.last_subscript = key
        else:
            new_tip = {}
            self.tip[self.last_subscript] = new_tip
            self.tip = new_tip
            self.last_subscript = key
        return self

    def add_list(self):
        """Set the current object tip to be an array of length 1."""
        if self.result is None:
            self.result = self.tip = [None]
            self.last_subscript = 0
        else:
            new_tip = [None]
            self.tip[self.last_subscript] = new_tip
            self.tip = new_tip
            self.last_subscript = 0
        return self

    def finish(self, val):
        """Set the current object tip to be an arbitrary value and
        return the skeleton that we traversed. """
        if self.result is None:
            self.result = val
        else:
            self.tip[self.last_subscript] = val
        return self.result


class JSONq():
    def __init__(self, json_data):
        self.json_data = json_data

    def parse_queries(self, query_strs):
        """Convert `query_str` (the command-line arguments) to parsed queries."""

        # parse the given queries. Each parsed query is a list of
        # tuples. The first element of each tuple, if not None, is a
        # dictionary key. The second element " " " ", is an array index.
        queries = []
        for query_s in query_strs:
            original_query_s = query_s
            query = []
            while True:
                # dictionary keys may contain anything except ., [, or ], so [^.\[\]]+
                # maybe allow these chars also when backslash-escaped? meh.
                # array indices are digits, i.e., \d+
                m = re.match(r'((?P<select>\.[^.\[\]]+)|(?P<index>\[\d+\])|(?P<star>\[\*\]))', query_s)
                if m:
                    query_s = query_s[len(m.group(0)):]
                    if m.group('select'):
                        q = m.group('select')[1:]
                        i = None
                    elif m.group('index'):
                        q = None
                        i = int(m.group('index')[1:-1])
                    elif m.group('star'):
                        q = None
                        i = True
                    else:
                        assert False
                    query.append((q, i))
                elif query_s == '':
                    break
                else:
                    raise ValueError("Could not parse the query", original_query_s)
            queries.append(query)
        return queries

    def query(self, query_strs, do_filter=False):
        queries = self.parse_queries(query_strs)
        return self._query(queries, do_filter)

    def _query(self, queries, do_filter):
        """Run `queries` against the data on stdin."""

        def q(query, tip, filtered):
            if len(query) > 0:
                s, i = query[0]
                if s is not None and i is None:
                    # this query item is an dictionary key:
                    if type(tip) == dict:
                        if s in tip:
                            return q(query[1:], tip[s], copy.deepcopy(filtered).add_map(s))
                        else:
                            return []
                    else:
                        return []
                elif s is None and i is not None:
                    if type(tip) == list:
                        if i is True:
                            # we're dealing with an unpack query, [*]
                            matches = []
                            for i in range(len(tip)):
                                matches.extend(q(query[1:], tip[i], copy.deepcopy(filtered).add_list()))
                            return matches
                        else:
                            # this query item is an array subscript
                            if len(tip) > i:
                                return q(query[1:], tip[i], copy.deepcopy(filtered).add_list())
                            else:
                                return []
                    else:
                        return []
                else:
                    assert False
            else:
                return [(tip, filtered.finish(tip))]

        try:
            json_obj = json.loads(self.json_data)
        except TypeError:
            json_obj = self.json_data

        result = []
        for query in queries:
            for value, filtered in q(query, copy.deepcopy(json_obj), FilteredJSONObject()):
                if do_filter:
                    result.append(filtered)
                else:
                    result.append(value)

        return result


def main():
    parser = OptionParser(usage="%prog [options] queries")
    parser.add_option('-f', '--filter', dest='do_filter', default=False, action='store_true',
                      help='Show the original object filtered by the query, not just the result.')
    parser.add_option('-d', '--delimiter', dest='delimiter', default=' ', action='store',
                      help='The string to be printed between results for a single input and query.')
    options, args = parser.parse_args()
    json_q = JSONq(sys.stdin.read())
    for line in json_q.query(args, options.do_filter):
        print json.dumps(line) + options.delimiter.decode('string_escape')
    if options.delimiter.decode('string_escape') != '\n':
        print

if __name__ == '__main__':
    sys.exit(main())

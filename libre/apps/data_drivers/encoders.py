from __future__ import unicode_literals

import datetime
import decimal
import json

from django.utils.functional import Promise

from rest_framework.compat import timezone, force_text

from shapely import geometry


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time/timedelta,
    decimal types, and generators.
    """
    def default(self, o):
        # A dictionary may have a date as it's key, explicitly handle this
        if isinstance(o, dict):
            result = {}
            for key, value in o.iteritems():
                result[self.default(key)] = self.default(value)
            return result
        # For Date Time string spec, see ECMA 262
        # http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
        elif isinstance(o, Promise):
            return force_text(o)
        elif isinstance(o, (geometry.LineString, geometry.MultiLineString, geometry.MultiPoint, geometry.MultiPolygon, geometry.Point, geometry.Polygon)):
            return o.__geo_interface__
        elif isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if timezone and timezone.is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return str(o.total_seconds())
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif hasattr(o, 'tolist'):
            return o.tolist()
        elif hasattr(o, '__iter__'):
            return [self.default(i) for i in o]
        else:
            return o

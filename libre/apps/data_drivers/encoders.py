from __future__ import unicode_literals

import datetime
import decimal
import types
import json

from django.utils.datastructures import SortedDict
from django.utils.functional import Promise

import geojson

from rest_framework.compat import timezone, force_text
from rest_framework.serializers import DictWithMetadata, SortedDictWithMetadata

from shapely import geometry


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time/timedelta,
    decimal types, and generators.
    """
    def default(self, o):
        # For Date Time string spec, see ECMA 262
        # http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
        if isinstance(o, Promise):
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
        elif hasattr(o, '__iter__'):
            return [i for i in o]
        return super(JSONEncoder, self).default(o)

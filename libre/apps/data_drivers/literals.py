from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

from rest_framework import renderers

from .renderers import CustomJSONRenderer, CustomXMLRenderer, LeafletRenderer
from .settings import LQL_DELIMITER

# Row based
DEFAULT_LIMIT = 50

# Excel
DEFAULT_SHEET = '0'

DATA_TYPE_STRING = 1
DATA_TYPE_NUMBER = 2
DATA_TYPE_DATETIME = 3
DATA_TYPE_DATE = 4
DATA_TYPE_TIME = 5
# TODO: DATA_TYPE_AUTO = 3
# TODO: Boolean

DATA_TYPE_CHOICES = (
    (DATA_TYPE_STRING, _('String')),
    (DATA_TYPE_NUMBER, _('Number')),
    (DATA_TYPE_DATETIME, _('Date & time')),
    (DATA_TYPE_DATE, _('Date')),
    (DATA_TYPE_TIME, _('Time')),
)

RENDERER_BROWSEABLE_API = 1
RENDERER_JSON = 2
RENDERER_XML = 3
RENDERER_YAML = 4
RENDERER_LEAFLET = 5

RENDERER_MAPPING = {
    RENDERER_BROWSEABLE_API: renderers.BrowsableAPIRenderer,
    RENDERER_JSON: CustomJSONRenderer,
    RENDERER_XML: CustomXMLRenderer,
    RENDERER_YAML: renderers.YAMLRenderer,
    RENDERER_LEAFLET: LeafletRenderer,
}

JOIN_TYPE_OR = 1
JOIN_TYPE_AND = 2

JOIN_TYPES = {
    JOIN_TYPE_OR: 'OR',
    JOIN_TYPE_AND: 'AND'
}

JOIN_TYPE_CHOICES = (
    (JOIN_TYPE_OR, _('OR')),
    (JOIN_TYPE_AND, _('AND'))
)

DOUBLE_DELIMITER = LQL_DELIMITER + LQL_DELIMITER

THOUSAND_SYMBOL = ','
DECIMAL_SYMBOL = '.'

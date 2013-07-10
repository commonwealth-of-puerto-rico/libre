from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

from rest_framework import renderers

from .renderers import LeafletRenderer
from .utils import convert_to_number

# Row based
DEFAULT_LIMIT = 50

# Excel
DEFAULT_SHEET = '0'

DATA_TYPE_STRING = 1
DATA_TYPE_NUMBER = 2
# TODO: DATA_TYPE_AUTO = 3
# TODO: Boolean

DATA_TYPE_CHOICES = (
    (DATA_TYPE_STRING, _('String')),
    (DATA_TYPE_NUMBER, _('Number')),
)

DATA_TYPE_FUNCTIONS = {
    DATA_TYPE_STRING: lambda x: str(x).strip(),
    DATA_TYPE_NUMBER: lambda x: convert_to_number(x),
}

RENDERER_BROWSEABLE_API = 1
RENDERER_JSON = 2
RENDERER_XML = 3
RENDERER_YAML = 4
RENDERER_LEAFLET = 5

RENDERER_MAPPING = {
    RENDERER_BROWSEABLE_API: renderers.BrowsableAPIRenderer,
    RENDERER_JSON: renderers.JSONRenderer,
    RENDERER_XML: renderers.XMLRenderer,
    RENDERER_YAML: renderers.YAMLRenderer,
    RENDERER_LEAFLET: LeafletRenderer,
}

JOIN_TYPE_OR = 1
JOIN_TYPE_AND = 2

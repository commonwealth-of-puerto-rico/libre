from __future__ import absolute_import

import logging

from rest_framework import renderers


class LeafletRenderer(renderers.TemplateHTMLRenderer):
    template_name = 'leaflet.html'
    format = 'leaflet'

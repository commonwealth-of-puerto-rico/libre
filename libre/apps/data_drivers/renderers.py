from __future__ import absolute_import

from itertools import islice
import logging
import json
import types

from django.template import Context, Template, TemplateSyntaxError

from rest_framework import renderers
from rest_framework.compat import StringIO, smart_text, six
from shapely import geometry

from icons.models import Icon


class LeafletRenderer(renderers.TemplateHTMLRenderer):
    template_name = 'leaflet.html'
    format = 'map_leaflet'
    exception_template_names = ['leaflet_exception.html']

    def process_feature(self, feature, template):
        new_feature = {'type': 'Feature'}
        new_feature.update(feature)
        new_feature['properties'] = {}
        new_feature['properties']['popup'] = template.render(
            Context(
                {
                    'feature': feature,
                    'icons': self.icons_dict
                }
            )
        )
        return new_feature

    def setup_icons_dict(self):
        self.icons_dict = dict([(icon.name, icon) for icon in Icon.objects.all()])

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders data to HTML, using Django's standard template rendering.

        The template name is determined by (in order of preference):

        1. An explicit .template_name set on the response.
        2. An explicit .template_name set on this class.
        3. The return result of calling view.get_template_names().
        """
        renderer_context = renderer_context or {}
        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']
        extra_context = renderer_context['extra_context']

        if response.exception:
            template = self.get_exception_template(response)
        else:
            template_names = self.get_template_names(response, view)
            template = self.resolve_template(template_names)

        context = self.resolve_context(data, request, response)

        if response.exception:
            # If there is an exception don't bother calculating data or geometries
            context.update({'template_extra_context': extra_context})
            return template.render(context)

        new_data = {
            "type": "FeatureCollection",
        }

        features = []

        self.setup_icons_dict()

        try:
            popup_template = Template(getattr(view.get_object(), 'popup_template', None))
        except TemplateSyntaxError as exception:
            popup_template = Template(exception)

        # TODO: fix this, use isinstace
        if type(data) == type({}):
            features.append(self.process_feature(data, popup_template))
        else:
            for feature in data:
                features.append(self.process_feature(feature, popup_template))

        new_data['features'] = features
        if 'latitude' and 'longitude' not in extra_context:
            # User didn't specified which latitude and longitude to move the map,
            # determine where to move the map ourselves
            extra_context['extents'] = self.determine_extents(features)

        context.update({'data': json.dumps(new_data)})
        if 'geometry' in extra_context:
            extra_context['geometry'] = json.dumps(extra_context['geometry'].__geo_interface__)
        context.update({'template_extra_context': extra_context})
        return template.render(context)

    def determine_extents(self, features):
        bounds_generator = (geometry.shape(feature['geometry']).bounds for feature in features)
        iterator = iter(bounds_generator)

        first_feature_bounds = iterator.next()

        min_x, min_y, max_x, max_y = first_feature_bounds
        for bounds in bounds_generator:
            min_x = min(min_x, bounds[0])
            min_y = min(min_y, bounds[1])
            max_x = max(max_x, bounds[2])
            max_y = max(max_y, bounds[3])

        return min_x, min_y, max_x, max_y


class CustomXMLRenderer(renderers.XMLRenderer):
    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple, types.GeneratorType, islice)):
            for item in data:
                xml.startElement("list-item", {})
                self._to_xml(xml, item)
                xml.endElement("list-item")

        elif isinstance(data, dict):
            for key, value in six.iteritems(data):
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_text(data))

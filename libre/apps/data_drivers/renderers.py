from __future__ import absolute_import

import logging
import json

from django.template import Context, Template, TemplateSyntaxError

from rest_framework import renderers


class LeafletRenderer(renderers.TemplateHTMLRenderer):
    template_name = 'leaflet.html'
    format = 'map_leaflet'

    def _process_feature(self, feature, template):
        new_feature = {'type': 'Feature'}
        new_feature.update(feature)
        new_feature['properties']['popup'] = template.render(Context(feature))
        return new_feature

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

        if response.exception:
            template = self.get_exception_template(response)
        else:
            template_names = self.get_template_names(response, view)
            template = self.resolve_template(template_names)

        context = self.resolve_context(data, request, response)

        new_data = {
            "type": "FeatureCollection",
        }

        features = []

        try:
            popup_template = Template(view.get_object().popup_template)
        except TemplateSyntaxError as exception:
            popup_template = Template(exception)

        if type(data) == type({}):
            features.append(self._process_feature(data, popup_template))
        else:
            for feature in data:
                features.append(self._process_feature(feature, popup_template))

        new_data['features'] = features

        context.update({'data': json.dumps(new_data)})
        return template.render(context)

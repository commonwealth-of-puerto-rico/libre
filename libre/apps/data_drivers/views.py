from __future__ import absolute_import

import logging
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404
from django.views.generic import TemplateView

from rest_framework import generics, renderers
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import api_view

import main

from .literals import DOUBLE_DELIMITER, LQL_DELIMITER, RENDERER_MAPPING
from .models import Source, SourceDataVersion
from .serializers import SourceDataVersionSerializer, SourceSerializer

logger = logging.getLogger(__name__)


class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context=context)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'sources': reverse('source-list', request=request, format=format),
        'libre': reverse('libremetadata-list', request=request, format=format)
    })


class SourceList(generics.ListAPIView):
    queryset = Source.objects.filter(published=True)
    serializer_class = SourceSerializer


class SourceDetail(generics.RetrieveAPIView):
    queryset = Source.objects.filter(published=True)
    serializer_class = SourceSerializer


class SourceDataVersionList(generics.ListAPIView):
    queryset = SourceDataVersion.objects.filter(ready=True)
    serializer_class = SourceDataVersionSerializer


class SourceDataVersionDetail(generics.RetrieveAPIView):
    queryset = SourceDataVersion.objects.filter(ready=True)
    serializer_class = SourceDataVersionSerializer


class SourceGetAll(generics.GenericAPIView):
    queryset = Source.objects.filter(published=True).select_subclasses()

    def get_renderers(self):
        """
        Instantiates and returns the list of renderers that this view can use.
        """
        source = self.get_object()
        return [RENDERER_MAPPING[i]() for i in source.__class__.renderers]

    def get(self, request, *args, **kwargs):
        source = self.get_object()

        result = {}
        for key, value in request.GET.items():
            if key.startswith(LQL_DELIMITER + 'renderer'):
                try:
                    result[key.split(DOUBLE_DELIMITER)[1]] = value
                except IndexError:
                    # Badly encoded renderer values, ignore the exception
                    pass

        self.renderer_extra_context = result#request.GET.get(LQL_DELIMITER + 'renderer')
        return Response(source.get_all(parameters=request.GET))

    def get_renderer_context(self):
        """
        Returns a dict that is passed through to Renderer.render(),
        as the `renderer_context` keyword argument.
        """
        # Note: Additionally 'response' will also be added to the context,
        #       by the Response object.
        return {
            'view': self,
            'args': getattr(self, 'args', ()),
            'kwargs': getattr(self, 'kwargs', {}),
            'request': getattr(self, 'request', None),
            'extra_context': getattr(self, 'renderer_extra_context', {})
        }

class SourceGetOne(generics.GenericAPIView):
    queryset = Source.objects.filter(published=True).select_subclasses()

    def get_renderers(self):
        """
        Instantiates and returns the list of renderers that this view can use.
        """
        source = self.get_object()
        return [RENDERER_MAPPING[i]() for i in source.__class__.renderers]

    def get(self, request, *args, **kwargs):
        source = self.get_object()
        return Response(source.get_one(int(kwargs['id']), parameters=request.GET))


class LibreMetadataList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(dict([(i, getattr(main, i)) for i in ['__author__', '__copyright__', '__credits__', '__email__', '__license__', '__maintainer__', '__status__', '__version__', '__version_info__']]))

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

from .models import Source
from .serializers import SourceSerializer

logger = logging.getLogger(__name__)


class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context=context)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        #'users': reverse('user-list', request=request, format=format),
        'sources': reverse('source-list', request=request, format=format)
    })


class SourceList(generics.ListAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class SourceDetail(generics.RetrieveAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class SourceGetAll(generics.GenericAPIView):
    queryset = Source.objects.all().select_subclasses()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        parameters = {}
        for i in request.GET:
            if not i.startswith('_'):
                parameters[i] = request.GET[i]

        timestamp = request.GET.get('_timestamp', None)

        source = self.get_object()
        return Response(source.get_all(timestamp=timestamp, parameters=parameters))


class SourceGetOne(generics.GenericAPIView):
    queryset = Source.objects.all().select_subclasses()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        parameters = {}
        for i in request.GET:
            if not i.startswith('_'):
                parameters[i] = request.GET[i]

        timestamp = request.GET.get('_timestamp', None)

        source = self.get_object()
        return Response(source.get_one(int(kwargs['id']), timestamp=timestamp, parameters=parameters))

from __future__ import absolute_import

import datetime
import logging
from urllib import unquote_plus

from django.views.generic import TemplateView

from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import api_view

import main

from .exceptions import Http400
from .literals import DOUBLE_DELIMITER, LQL_DELIMITER, RENDERER_MAPPING, RENDERER_BROWSEABLE_API, RENDERER_JSON, RENDERER_XML, RENDERER_YAML
from .models import Source, SourceDataVersion
from .serializers import SourceDataVersionSerializer, SourceSerializer
from .utils import parse_value, parse_qs

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


class CustomAPIView(generics.GenericAPIView):
    def get_renderers(self):
        """
        Instantiates and returns the list of renderers that this view can use.
        """
        self.renderer_classes = [RENDERER_MAPPING[i] for i in self.__class__.renderers]
        return [RENDERER_MAPPING[i]() for i in self.__class__.renderers]


class CustomListAPIView(CustomAPIView, generics.ListAPIView):
    pass


class CustomRetrieveAPIView(CustomAPIView, generics.RetrieveAPIView):
    pass


class SourceList(CustomListAPIView):
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML)
    queryset = Source.objects.filter(published=True).select_subclasses()
    serializer_class = SourceSerializer


class SourceDetail(CustomRetrieveAPIView):
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML)
    queryset = Source.objects.filter(published=True).select_subclasses()
    serializer_class = SourceSerializer


class SourceDataVersionList(CustomListAPIView):
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML)
    queryset = SourceDataVersion.objects.filter(ready=True)
    serializer_class = SourceDataVersionSerializer


class SourceDataVersionDetail(CustomRetrieveAPIView):
    renderers = (RENDERER_JSON, RENDERER_BROWSEABLE_API, RENDERER_XML, RENDERER_YAML)
    queryset = SourceDataVersion.objects.filter(ready=True)
    serializer_class = SourceDataVersionSerializer


class LIBREView(generics.GenericAPIView):
    queryset = Source.objects.filter(published=True).select_subclasses()

    def get_renderers(self):
        """
        Instantiates and returns the list of renderers that this view can use.
        """
        source = self.get_object()
        self.renderer_classes = [RENDERER_MAPPING[i] for i in source.__class__.renderers]
        return [RENDERER_MAPPING[i]() for i in source.__class__.renderers]

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

    def get_renderer_extra_variables(self, request):
        result = {}
        for key, value in request.GET.items():
            if key.startswith(LQL_DELIMITER + 'renderer'):
                try:
                    renderer_variables = key.split(DOUBLE_DELIMITER)[1]
                except IndexError:
                    # Badly encoded renderer values, ignore the exception
                    pass
                else:
                    try:
                        result[renderer_variables] = parse_value(value)
                    except Exception as exception:
                        raise
                        raise Http400('Invalid renderer value; %s' % exception)

        self.renderer_extra_context = result


class SourceGetAll(LIBREView):
    def get(self, request, *args, **kwargs):
        initial_datetime = datetime.datetime.now()

        source = self.get_object()
        self.get_renderer_extra_variables(request)
        result = source.get_all(parameters=parse_qs(unquote_plus(request.META['QUERY_STRING'])))
        logger.debug('Total view elapsed time: %s' % (datetime.datetime.now() - initial_datetime))

        return Response(result)


class SourceGetOne(LIBREView):
    def get(self, request, *args, **kwargs):
        initial_datetime = datetime.datetime.now()

        source = self.get_object()
        self.get_renderer_extra_variables(request)
        result = source.get_one(int(kwargs['id']), parameters=parse_qs(unquote_plus(request.META['QUERY_STRING'])))
        logger.debug('Total view elapsed time: %s' % (datetime.datetime.now() - initial_datetime))

        return Response(result)


class LibreMetadataList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(dict([(i, getattr(main, i)) for i in ['__author__', '__copyright__', '__credits__', '__email__', '__license__', '__maintainer__', '__status__', '__version__', '__version_info__']]))

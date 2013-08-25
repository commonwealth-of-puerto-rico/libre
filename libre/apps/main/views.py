from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext

from rest_framework import renderers
from rest_framework.authtoken.views import ObtainAuthToken


def home(request):
    return render_to_response('home.html', {},
        context_instance=RequestContext(request))


class CustomObtainAuthToken(ObtainAuthToken):
    renderer_classes = (renderers.JSONRenderer,renderers.BrowsableAPIRenderer)

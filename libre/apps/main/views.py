from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView

from rest_framework import renderers
from rest_framework.authtoken.views import ObtainAuthToken


def home(request):
    return render_to_response('home.html', {},
        context_instance=RequestContext(request))


class CustomObtainAuthToken(ObtainAuthToken):
    renderer_classes = (renderers.JSONRenderer,renderers.BrowsableAPIRenderer)


class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context=context)

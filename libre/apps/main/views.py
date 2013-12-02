from __future__ import absolute_import

import os

import docutils.core
import docutils.writers.html4css1

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView

from rest_framework import renderers
from rest_framework.authtoken.views import ObtainAuthToken

from data_drivers.models import Source


def about_view(request):
    with open(os.path.join(getattr(settings, 'SITE_ROOT'), 'AUTHORS.rst')) as f:
        authors = f.read()

    writer = docutils.writers.html4css1.Writer()
    docutils.core.publish_string(authors, 'body', writer=writer)

    return render_to_response('about.html', {'authors': writer.parts['body'].replace('h1', 'h3')},
        context_instance=RequestContext(request))


def home(request):
    return render_to_response('home.html', {'sources': Source.allowed.for_user(request.user).filter(published=True).order_by('?')[0:3]},
        context_instance=RequestContext(request))


class CustomObtainAuthToken(ObtainAuthToken):
    renderer_classes = (renderers.JSONRenderer,renderers.BrowsableAPIRenderer)


class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context=context)

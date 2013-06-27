from __future__ import absolute_import

import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse

from .models import Source, SourceData

'''
def namespace_list(request):
    object_list = [namespace]

    return render_to_response('generic_list.html', {
        'object_list': object_list,
    }, context_instance=RequestContext(request))


def namespace_view(request, endpoint):
    object_list = namespace.get_sources()

    return render_to_response('generic_list.html', {
        'object_list': object_list,
    }, context_instance=RequestContext(request))
'''

def resource_get_all(request, resource_slug):
    source = get_object_or_404(Source.objects.select_subclasses(), slug=resource_slug)
    data = source.get_all()

    return HttpResponse(json.dumps(data), content_type='application/json')


def resource_get_one(request, resource_slug, id):
    source = get_object_or_404(Source.objects.select_subclasses(), slug=resource_slug)
    data = source.get_one(int(id))

    return HttpResponse(json.dumps(data), content_type='application/json')

from __future__ import absolute_import

import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from data_drivers.models import Source

logger = logging.getLogger(__name__)


def sources_view(request):
    return render_to_response('data_sets/sources.html', {'sources': Source.allowed.for_user(request.user).filter(published=True)},
        context_instance=RequestContext(request))


def source_view(request, source_slug):
    source = get_object_or_404(Source, slug=source_slug)
    source = Source.objects.get_subclass(pk=source.pk)

    return render_to_response('data_sets/source_details.html', {'source': source},
        context_instance=RequestContext(request))

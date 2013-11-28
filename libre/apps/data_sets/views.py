from __future__ import absolute_import

import logging

from django.shortcuts import render_to_response
from django.template import RequestContext

from data_drivers.models import Source

logger = logging.getLogger(__name__)


def sources_view(request):
    return render_to_response('data_sets/sources.html', {'sources': Source.objects.filter(published=True)},
        context_instance=RequestContext(request))

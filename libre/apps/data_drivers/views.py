from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from .classes import SampleExcel


def resource_get(request, endpoint, resource, id):
    source = SampleExcel()
    data = source.get(int(id))

    return render_to_response('data.html', {
        'data': data,
    }, context_instance=RequestContext(request))

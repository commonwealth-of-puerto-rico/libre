from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext

from data_drivers.utils import parse_request, parse_qs

from .forms import ClientForm


def libre_client(request):
    if request.POST:
        form = ClientForm(data=request.POST)
    else:
        form = ClientForm()

    context = {
        'form': form,
    }

    return render_to_response('client.html', context,
        context_instance=RequestContext(request))

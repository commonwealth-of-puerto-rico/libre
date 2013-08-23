from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import ClientForm


def libre_client(request):
    if request.POST:
        form = ClientForm(data=request.POST)
    else:
        form = ClientForm(initial={'server': request.get_host()})

    context = {
        'form': form,
    }

    return render_to_response('client.html', context,
        context_instance=RequestContext(request))

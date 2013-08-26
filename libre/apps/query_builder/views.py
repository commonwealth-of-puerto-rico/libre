from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import ClientForm


def index(request):
    if request.POST:
        form = ClientForm(data=request.POST)
    else:
        form = ClientForm(initial={'server': request.get_host()})

    context = {
        'form': form,
    }

    return render_to_response('query_builder.html', context,
        context_instance=RequestContext(request))

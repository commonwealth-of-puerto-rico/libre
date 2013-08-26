from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import ClientForm


def query_builder_index_view(request):
    if request.POST:
        form = ClientForm(data=request.POST, request=request)
    else:
        form = ClientForm(initial={'server': request.get_host()}, request=request)

    context = {
        'form': form,
    }

    return render_to_response('query_builder.html', context,
        context_instance=RequestContext(request))

from __future__ import absolute_import

from django.shortcuts import HttpResponse

from .models import Icon


def display(request, slug, as_base64=False):
    data = Icon.objects.get(name=slug).compose(as_base64=as_base64)
    response = HttpResponse(data, mimetype='image/png', content_type='image/png')
    response['Content-Length'] = len(data)
    return response

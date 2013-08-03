from __future__ import absolute_import

from django.shortcuts import HttpResponse

from .models import Icon


def display(request, slug):
    icon = Icon.objects.get(name=slug)
    return HttpResponse(icon.display())

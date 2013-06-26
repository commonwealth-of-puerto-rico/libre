from __future__ import absolute_import

import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from .classes import SampleExcel

source = SampleExcel()


def resource_get_all(request, endpoint, resource):
    data = source.all()

    return HttpResponse(json.dumps(data), content_type="application/json")


def resource_get_one(request, endpoint, resource, id):
    data = source.get(int(id))

    return HttpResponse(json.dumps(data), content_type="application/json")

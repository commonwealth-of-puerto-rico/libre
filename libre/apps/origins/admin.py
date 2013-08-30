from __future__ import absolute_import

from django.contrib import admin, messages
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .models import OriginURL, OriginPath, OriginFile, OriginDatabase

from __future__ import absolute_import

from django.contrib import admin

from .models import Source, SourceData, SourceSpreadsheet

admin.site.register(SourceData)
admin.site.register(SourceSpreadsheet)

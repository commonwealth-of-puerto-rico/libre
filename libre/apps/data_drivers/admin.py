from __future__ import absolute_import

from django.contrib import admin

from .models import Source, SourceData, SourceDataVersion, SourceSpreadsheet


class SourceDataVersionInline(admin.StackedInline):
    model = SourceDataVersion
    readonly_fields = ('datetime', 'timestamp', 'checksum', 'ready')
    extra = 0

class SourceSpreadsheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'limit', 'path', 'file', 'sheet', 'column_names', 'first_row_names')
    inlines = [SourceDataVersionInline]


admin.site.register(SourceData)
admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)

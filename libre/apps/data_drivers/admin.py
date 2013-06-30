from __future__ import absolute_import

from django.contrib import admin

from .models import SourceCSV, SourceDataVersion, SourceSpreadsheet


class SourceDataVersionInline(admin.StackedInline):
    model = SourceDataVersion
    readonly_fields = ('datetime', 'timestamp', 'checksum', 'ready')
    extra = 0


class SourceSpreadsheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'limit', 'path', 'file', 'sheet', 'column_names', 'first_row_names')
    inlines = [SourceDataVersionInline]


class SourceCSVAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'limit', 'path', 'file', 'column_names', 'first_row_names', 'delimiter', 'quote_character')
    inlines = [SourceDataVersionInline]


admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)

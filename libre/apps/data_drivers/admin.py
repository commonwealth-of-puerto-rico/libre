from __future__ import absolute_import

from django.contrib import admin

from .models import SourceCSV, SourceDataVersion, SourceSpreadsheet


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    readonly_fields = ('datetime', 'timestamp', 'checksum', 'ready')
    extra = 0


class SourceSpreadsheetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('name', 'slug'),)
        }),
        ('Result limiting', {
            'fields': ('limit',)
        }),
        ('File source', {
            'fields': (('path', 'file'), 'sheet')
        }),
        ('Column identifiers', {
            'fields': (('column_names', 'first_row_names'),)
        }),
    )

    list_display = ('name', 'slug', 'limit', 'path', 'file', 'sheet', 'column_names', 'first_row_names')
    inlines = [SourceDataVersionInline]


class SourceCSVAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('name', 'slug'),)
        }),
        ('Result limiting', {
            'fields': ('limit',)
        }),
        ('File source', {
            'fields': (('path', 'file'),)
        }),
        ('Column identifiers', {
            'fields': (('column_names', 'first_row_names'),)
        }),
        ('Comma delimited files', {
            'fields': (('delimiter', 'quote_character'),)
        }),
        ('Fixed width column files', {
            'fields': ('column_widths',)
        }),
    )
    list_display = ('name', 'slug', 'limit', 'path', 'file', 'column_names', 'first_row_names', 'delimiter', 'quote_character', 'column_widths')
    inlines = [SourceDataVersionInline]


admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)

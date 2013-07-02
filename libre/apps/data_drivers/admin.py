from __future__ import absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import SourceCSV, SourceDataVersion, SourceSpreadsheet


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    readonly_fields = ('datetime', 'timestamp', 'checksum', 'ready')
    extra = 0


def check_updated(modeladmin, request, queryset):
    for source in queryset:
        source.check_file()

    if len(queryset) == 1:
        message_bit = 'Source file was checked for update.'
    else:
        message_bit = '%s sources were checked for update.' % len(queryset)
    modeladmin.message_user(request, message_bit)
check_updated.short_description = _('Check for updated source file')


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
    actions = [check_updated]


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
    actions = [check_updated]


admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)

from __future__ import absolute_import

from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _

from .models import SourceCSV, SourceDataVersion, SourceSpreadsheet, SourceWS, WSArgument, WSResultField


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    readonly_fields = ('datetime', 'timestamp', 'checksum', 'ready')
    extra = 0


def check_updated(modeladmin, request, queryset):
    count = 0
    for source in queryset:
        try:
            source.check_file()
        except IOError:
            messages.error(request, _('Error opening file for source: %s') % source)
        else:
            count += 1

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


class WSArgumentInline(admin.TabularInline):
    model = WSArgument
    extra = 1


class WSResultFieldInline(admin.TabularInline):
    model = WSResultField
    extra = 1


class SourceWSAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'wsdl_url')
    inlines = [WSArgumentInline, WSResultFieldInline]


admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)
admin.site.register(SourceWS, SourceWSAdmin)

from __future__ import absolute_import

from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _

from .forms import (SourceDatabaseForm, CSVColumnForm, ShapefileColumnForm,
    SourceSpreadsheetForm, SourceCSVForm, SourceFixedWidthForm, SourceWSForm, SourceShapeForm)
from .models import (CSVColumn, DatabaseResultColumn, FixedWidthColumn, SourceDatabase, LeafletMarker,
    ShapefileColumn, SourceCSV, SourceDataVersion, SourceFixedWidth, SourceShape,
    SourceSpreadsheet, SpreadsheetColumn, SourceWS, WSArgument, WSResultField)


class DatabaseResultColumnInline(admin.TabularInline):
    model = DatabaseResultColumn
    extra = 1
    suit_classes = 'suit-tab suit-tab-configuration'


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    fields = ('active', 'datetime', 'timestamp', 'truncated_checksum', 'metadata', 'ready')
    readonly_fields = ('datetime', 'timestamp', 'truncated_checksum', 'metadata', 'ready')
    extra = 0
    max_num = 0  # Don't allowing adding new versions by hand
    suit_classes = 'suit-tab suit-tab-versions'


class FixedWidthColumnInline(admin.TabularInline):
    model = FixedWidthColumn
    extra = 1
    suit_classes = 'suit-tab suit-tab-configuration'


class CSVColumnInline(admin.TabularInline):
    model = CSVColumn
    extra = 1
    suit_classes = 'suit-tab suit-tab-configuration'
    form = CSVColumnForm


class SpreadsheetColumnInline(admin.TabularInline):
    model = SpreadsheetColumn
    extra = 1
    suit_classes = 'suit-tab suit-tab-configuration'


class ShapefileColumnInline(admin.TabularInline):
    model = ShapefileColumn
    extra = 1
    suit_classes = 'suit-tab suit-tab-configuration'
    form = ShapefileColumnForm


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


def clear_versions(modeladmin, request, queryset):
    count = 0
    for source in queryset:
        try:
            source.clear_versions()
        except IOError:
            messages.error(request, _('Error opening file for source: %s') % source)
        else:
            count += 1

    if len(queryset) == 1:
        message_bit = 'Source versions were deleted.'
    else:
        message_bit = '%s sources versions were deleted.' % len(queryset)
    modeladmin.message_user(request, message_bit)
clear_versions.short_description = _('Clear all source versions')


class SourceDatabaseAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')),)

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'database_connection', 'query', 'limit', 'published')
        }),
    )
    list_display = ('name', 'slug', 'description', 'published')
    list_editable = ('published',)
    inlines = [DatabaseResultColumnInline]
    form = SourceDatabaseForm


class SourceSpreadsheetAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Result limiting'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('limit',)
        }),
        (_('Source data (choose one)'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('path', 'file', 'url')
        }),
        (_('In-file location'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('sheet',)
        }),
        (_('Row related'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('import_rows',)
        }),
    )

    list_display = ('name', 'slug', 'description', 'get_stream_type', 'published')
    list_editable = ('published',)
    inlines = [SourceDataVersionInline, SpreadsheetColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceSpreadsheetForm


class SourceCSVAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Result limiting'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('limit',)
        }),
        (_('Source data (choose one)'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('path', 'file', 'url',)
        }),
        (_('Row related'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('import_rows',)
        }),
        (_('Comma delimited files'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('delimiter', 'quote_character',)
        }),
    )
    list_display = ('name', 'slug', 'description', 'get_stream_type', 'published')
    list_editable = ('published',)
    inlines = [SourceDataVersionInline, CSVColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceCSVForm


class SourceFixedWidthAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Result limiting'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('limit',)
        }),
        (_('Source data (choose one)'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('path', 'file', 'url',)
        }),
        (_('Row related'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('import_rows',)
        }),
    )
    list_display = ('name', 'slug', 'description', 'get_stream_type', 'published')
    list_editable = ('published',)
    inlines = [SourceDataVersionInline, FixedWidthColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceFixedWidthForm


class WSArgumentInline(admin.TabularInline):
    suit_classes = 'suit-tab suit-tab-configuration'
    model = WSArgument
    extra = 1


class WSResultFieldInline(admin.TabularInline):
    suit_classes = 'suit-tab suit-tab-configuration'
    model = WSResultField
    extra = 1


class SourceWSAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')),)

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Source data'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('wsdl_url', 'endpoint')
        }),
    )
    list_display = ('name', 'slug', 'wsdl_url', 'endpoint', 'published')
    list_editable = ('published',)
    inlines = [WSArgumentInline, WSResultFieldInline]
    form = SourceWSForm


class SourceShapeAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')), ('renderers', _('Renderers')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Result limiting'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('limit',)
        }),
        (_('Source data (choose one)'), {
            'classes': ('suit-tab suit-tab-configuration',),
            #'fields': ('path', 'file', 'url') #Disables until file handle support is added
            'fields': ('path',)
        }),
        (_('Source data transformation'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('new_projection',)
        }),
        (_('Leaflet renderer'), {
            'classes': ('suit-tab suit-tab-renderers',),
            'fields': ('popup_template', 'markers', 'marker_template')
        }),
    )

    list_display = ('name', 'slug', 'description', 'get_stream_type', 'published')
    list_editable = ('published',)
    filter_horizontal = ['markers']
    inlines = [SourceDataVersionInline, ShapefileColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceShapeForm


admin.site.register(SourceDatabase, SourceDatabaseAdmin)
admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)
admin.site.register(SourceShape, SourceShapeAdmin)
admin.site.register(SourceFixedWidth, SourceFixedWidthAdmin)
admin.site.register(SourceWS, SourceWSAdmin)
admin.site.register(LeafletMarker)

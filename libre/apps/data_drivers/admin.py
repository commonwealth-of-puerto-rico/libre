from __future__ import absolute_import

from django.contrib import admin, messages
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .actions import check_updated, clear_versions, clone
from .forms import (SourceDatabaseForm, CSVColumnForm, LeafletMarkerForm, ShapefileColumnForm,
    SpreadsheetColumnForm, SourceSpreadsheetForm, SourceCSVForm, SourceFixedWidthForm,
    SourceWSForm, SourceShapeForm)
from .models import (CSVColumn, DatabaseResultColumn, FixedWidthColumn, SourceDatabase, LeafletMarker,
    ShapefileColumn, SourceCSV, SourceDataVersion, SourceFixedWidth, SourceRESTAPI, SourceShape,
    SourceSpreadsheet, SpreadsheetColumn, SourceWS, WSArgument, WSResultField)


class SourceColumnInline(admin.TabularInline):
    extra = 1
    suit_classes = 'suit-tab suit-tab-fields'


class DatabaseResultColumnInline(SourceColumnInline):
    model = DatabaseResultColumn


class FixedWidthColumnInline(SourceColumnInline):
    model = FixedWidthColumn


class CSVColumnInline(SourceColumnInline):
    model = CSVColumn
    form = CSVColumnForm


class SpreadsheetColumnInline(SourceColumnInline):
    model = SpreadsheetColumn
    form = SpreadsheetColumnForm


class ShapefileColumnInline(SourceColumnInline):
    model = ShapefileColumn
    form = ShapefileColumnForm


class WSArgumentInline(SourceColumnInline):
    model = WSArgument


class WSResultFieldInline(SourceColumnInline):
    model = WSResultField


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    fields = ('active', 'datetime', 'timestamp', 'truncated_checksum', 'metadata', 'ready')
    readonly_fields = ('datetime', 'timestamp', 'truncated_checksum', 'metadata', 'ready')
    extra = 0
    max_num = 0  # Don't allowing adding new versions by hand
    suit_classes = 'suit-tab suit-tab-versions'


class SourceAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('fields', _('Fields')), ('authorization', _('Authorization')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Result limiting'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('limit',)
        }),
        (_('Authorized groups'), {
            'classes': ('suit-tab suit-tab-authorization',),
            'fields': ('allowed_groups',)
        }),
    )

    list_display = ('name', 'slug', 'description', 'get_stream_type', 'published')
    list_editable = ('published',)
    filter_horizontal = ['allowed_groups']

    actions = [clone]


class SourceDatabaseAdmin(SourceAdmin):
    fieldsets = SourceAdmin.fieldsets + (
        (_('Source information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('database_connection',)
        }),
        (_('Specific information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('query',)
        }),
    )
    inlines = [DatabaseResultColumnInline]
    form = SourceDatabaseForm


class SourceSpreadsheetAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (
        ('versions', _('Versions')),
    )

    fieldsets = SourceAdmin.fieldsets + (
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

    inlines = [SourceDataVersionInline, SpreadsheetColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceSpreadsheetForm


class SourceCSVAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (
        ('versions', _('Versions')),
    )

    fieldsets = SourceAdmin.fieldsets + (
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
    inlines = [SourceDataVersionInline, CSVColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceCSVForm


class SourceFixedWidthAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (
        ('versions', _('Versions')),
    )

    fieldsets = SourceAdmin.fieldsets + (
        (_('Source data (choose one)'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('path', 'file', 'url',)
        }),
        (_('Row related'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('import_rows',)
        }),
    )
    inlines = [SourceDataVersionInline, FixedWidthColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceFixedWidthForm


class SourceWSAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Source data'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('wsdl_url', 'endpoint')
        }),
        (_('Authorized groups'), {
            'classes': ('suit-tab suit-tab-authorization',),
            'fields': ('allowed_groups',)
        }),
    )
    list_display = ('name', 'slug', 'wsdl_url', 'endpoint', 'published')
    inlines = [WSArgumentInline, WSResultFieldInline]
    form = SourceWSForm


class SourceRESTAPIAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'published')
        }),
        (_('Source data'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('url',)
        }),
        (_('Authorized groups'), {
            'classes': ('suit-tab suit-tab-authorization',),
            'fields': ('allowed_groups',)
        }),
    )
    list_display = ('name', 'slug', 'url', 'published')
    #inlines = [WSArgumentInline, WSResultFieldInline]
    #form = SourceWSForm


class SourceShapeAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (
        ('versions', _('Versions')),
        ('renderers', _('Renderers')),
    )

    fieldsets = SourceAdmin.fieldsets + (
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
            'fields': ('template_header', 'popup_template', 'markers', 'marker_template')
        }),
    )

    filter_horizontal = SourceAdmin.filter_horizontal + ['markers']
    inlines = [SourceDataVersionInline, ShapefileColumnInline]
    actions = [check_updated, clear_versions]
    form = SourceShapeForm


class LeafletMarkerAdmin(admin.ModelAdmin):
    list_display = ('slug', 'label', 'icon', 'shadow', 'icon_anchor_x', 'icon_anchor_y', 'shadow_anchor_x', 'shadow_anchor_y', 'popup_anchor_x', 'popup_anchor_y')
    list_display_links = ('slug',)
    list_editable = ('icon', 'shadow', 'icon_anchor_x', 'icon_anchor_y', 'shadow_anchor_x', 'shadow_anchor_y', 'popup_anchor_x', 'popup_anchor_y')
    form = LeafletMarkerForm


admin.site.register(LeafletMarker, LeafletMarkerAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)
admin.site.register(SourceDatabase, SourceDatabaseAdmin)
admin.site.register(SourceFixedWidth, SourceFixedWidthAdmin)
admin.site.register(SourceRESTAPI, SourceRESTAPIAdmin)
admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceShape, SourceShapeAdmin)
admin.site.register(SourceWS, SourceWSAdmin)

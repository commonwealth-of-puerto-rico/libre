from __future__ import absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .actions import check_updated, clear_versions, clone
from .forms import (FixedWidthColumnForm, CSVColumnForm, LeafletMarkerForm, ShapefileColumnForm,
    SpreadsheetColumnForm, SourceSpreadsheetForm, SourceCSVForm, SourceFixedWidthForm,
    SourceShapeForm, SimpleSourceColumnForm)
from .models import (CSVColumn, SimpleSourceColumn, FixedWidthColumn, SourceDirect, LeafletMarker,
    ShapefileColumn, SourceCSV, SourceDataVersion, SourceFixedWidth, SourceShape,
    SourceSpreadsheet, SourceSimple, SpreadsheetColumn)


# Column inlines


class SourceColumnInline(admin.TabularInline):
    extra = 1
    suit_classes = 'suit-tab suit-tab-fields'


class FixedWidthColumnInline(SourceColumnInline):
    model = FixedWidthColumn
    form = FixedWidthColumnForm


class CSVColumnInline(SourceColumnInline):
    model = CSVColumn
    form = CSVColumnForm


class SpreadsheetColumnInline(SourceColumnInline):
    model = SpreadsheetColumn
    form = SpreadsheetColumnForm


class ShapefileColumnInline(SourceColumnInline):
    model = ShapefileColumn
    form = ShapefileColumnForm


class SimpleSourceColumnInline(SourceColumnInline):
    model = SimpleSourceColumn
    form = SimpleSourceColumnForm


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    fields = ('active', 'datetime', 'timestamp', 'truncated_checksum', 'metadata', 'ready')
    readonly_fields = ('datetime', 'timestamp', 'truncated_checksum', 'metadata', 'ready')
    extra = 0
    max_num = 0  # Don't allowing adding new versions by hand
    suit_classes = 'suit-tab suit-tab-versions'


# Source admins

class SourceAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('authorization', _('Authorization')), ('versions', _('Versions')), ('schedule', _('Schedule')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description', 'image', 'published', 'origin')
        }),
        (_('Result limiting'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('limit',)
        }),
        (_('Authorized groups'), {
            'classes': ('suit-tab suit-tab-authorization',),
            'fields': ('allowed_groups',)
        }),
        (_('Origin check schedule'), {
            'classes': ('suit-tab suit-tab-schedule',),
            'fields': ('schedule_enabled', 'schedule_string',)
        }),
    )

    list_display = ('name', 'slug', 'description', 'origin', 'published')
    list_editable = ('published',)
    filter_horizontal = ['allowed_groups']
    actions = [clone, check_updated, clear_versions]


class SourceDirectAdmin(SourceAdmin):
    #form = SourceDirectForm
    inlines = [SourceDataVersionInline]


class SourceCSVAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (('fields', _('Fields')),)

    fieldsets = SourceAdmin.fieldsets + (
        (_('Comma delimited files'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('delimiter', 'quote_character', 'encoding')
        }),
    )
    inlines = [SourceDataVersionInline, CSVColumnInline]
    form = SourceCSVForm


class SourceFixedWidthAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (('fields', _('Fields')),)
    inlines = [SourceDataVersionInline, FixedWidthColumnInline]
    form = SourceFixedWidthForm


class SourceSimpleAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (('fields', _('Fields')),)
    inlines = [SourceDataVersionInline, SimpleSourceColumnInline]


class SourceShapeAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (
        ('fields', _('Fields')), ('renderers', _('Renderers')),
    )

    fieldsets = SourceAdmin.fieldsets + (
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
    form = SourceShapeForm


class SourceSpreadsheetAdmin(SourceAdmin):
    suit_form_tabs = SourceAdmin.suit_form_tabs + (('fields', _('Fields')),)
    fieldsets = SourceAdmin.fieldsets + (
        (_('In-file location'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('sheet',)
        }),
    )

    inlines = [SourceDataVersionInline, SpreadsheetColumnInline]
    form = SourceSpreadsheetForm


class LeafletMarkerAdmin(admin.ModelAdmin):
    list_display = ('slug', 'label', 'icon', 'shadow', 'icon_anchor_x', 'icon_anchor_y', 'shadow_anchor_x', 'shadow_anchor_y', 'popup_anchor_x', 'popup_anchor_y')
    list_display_links = ('slug',)
    list_editable = ('icon', 'shadow', 'icon_anchor_x', 'icon_anchor_y', 'shadow_anchor_x', 'shadow_anchor_y', 'popup_anchor_x', 'popup_anchor_y')
    form = LeafletMarkerForm


admin.site.register(LeafletMarker, LeafletMarkerAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)
admin.site.register(SourceDirect, SourceDirectAdmin)
admin.site.register(SourceFixedWidth, SourceFixedWidthAdmin)
admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceShape, SourceShapeAdmin)
admin.site.register(SourceSimple, SourceSimpleAdmin)

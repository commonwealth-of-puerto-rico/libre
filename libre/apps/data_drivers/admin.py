from __future__ import absolute_import

from django.contrib import admin, messages
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from suit.widgets import AutosizedTextarea, EnclosedInput, NumberInput, SuitSplitDateTimeWidget

from .models import (SourceCSV, SourceDataVersion, SourceFixedWidth, SourceSpreadsheet,
    SourceWS, WSArgument, WSResultField)


class SourceSpreadsheetForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
            'sheet': NumberInput(attrs={'class': 'input-mini'}),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'column_names': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'name_row': NumberInput(attrs={'class': 'input-mini'}),
        }


class SourceFixedWidthForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'column_names': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'name_row': NumberInput(attrs={'class': 'input-mini'}),
            'column_widths': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceCSVForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'column_names': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'name_row': NumberInput(attrs={'class': 'input-mini'}),
        }


class SourceWSForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'wsdl_url': EnclosedInput(prepend='icon-globe'),
        }


class SourceDataVersionInline(admin.TabularInline):
    model = SourceDataVersion
    readonly_fields = ('datetime', 'timestamp', 'checksum', 'ready')
    extra = 0
    max_num = 0  # Don't allowing adding new versions by hand
    suit_classes = 'suit-tab suit-tab-versions'


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
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description')
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
        (_('Column identifiers'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('column_names', 'name_row',)
        }),
    )

    list_display = ('name', 'slug', 'description', 'get_stream_type')
    inlines = [SourceDataVersionInline]
    actions = [check_updated]
    form = SourceSpreadsheetForm


class SourceCSVAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description')
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
        (_('Column identifiers'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('column_names', 'name_row',)
        }),
        (_('Comma delimited files'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('delimiter', 'quote_character',)
        }),
    )
    list_display = ('name', 'slug', 'description', 'get_stream_type')
    inlines = [SourceDataVersionInline]
    actions = [check_updated]
    form = SourceCSVForm


class SourceFixedWidthAdmin(admin.ModelAdmin):
    suit_form_tabs = (('configuration', _('Configuration')), ('versions', _('Versions')))

    fieldsets = (
        (_('Basic information'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('name', 'slug', 'description')
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
        (_('Column identifiers'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('column_names', 'name_row', 'column_widths',)
        }),
    )
    list_display = ('name', 'slug', 'description', 'get_stream_type')
    inlines = [SourceDataVersionInline]
    actions = [check_updated]
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
            'fields': ('name', 'slug', 'description')
        }),
        (_('Source data'), {
            'classes': ('suit-tab suit-tab-configuration',),
            'fields': ('wsdl_url',)
        }),
    )
    list_display = ('name', 'slug', 'wsdl_url')
    inlines = [WSArgumentInline, WSResultFieldInline]
    form = SourceWSForm


admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)
admin.site.register(SourceCSV, SourceCSVAdmin)
admin.site.register(SourceFixedWidth, SourceFixedWidthAdmin)
admin.site.register(SourceWS, SourceWSAdmin)

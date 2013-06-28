from __future__ import absolute_import

from django.contrib import admin

from .models import Source, SourceData, SourceSpreadsheet


class SourceSpreadsheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'limit', 'path', 'file', 'sheet', 'column_names', 'first_row_names')


admin.site.register(SourceData)
admin.site.register(SourceSpreadsheet, SourceSpreadsheetAdmin)


#    limit = models.PositiveIntegerField(default=DEFAULT_LIMIT, verbose_name=_('limit'), help_text=('Maximum number of items to show when all items are requested.'))
#    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=('Location to a file in the filesystem.'))
#    file = models.FileField(blank=True, null=True, upload_to='spreadsheets', verbose_name=_('upload a file'))
#    sheet = models.CharField(max_length=32, default=DEFAULT_SHEET, verbose_name=_('sheet'), help_text=('Worksheet of the spreadsheet file to use.'))
#    column_names = models.TextField(blank=True, verbose_name=_('column names'), help_text=('Specify the column names to use.'))
#    first_row_names = models.BooleanField(default=DEFAULT_FIRST_ROW_NAMES, verbose_name=_('first row names'), help_text=('Use the values of the first row as the column names.'))

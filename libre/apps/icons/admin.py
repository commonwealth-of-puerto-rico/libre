from __future__ import absolute_import

from django.contrib import admin

from .models import Icon


class IconAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'icon_file')


admin.site.register(Icon, IconAdmin)

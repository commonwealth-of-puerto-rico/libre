from __future__ import absolute_import

from django.contrib import admin

from .models import DatabaseConnection


class DatabaseConnectionAdmin(admin.ModelAdmin):
    list_display = ('label', 'backend', 'name', 'user')


admin.site.register(DatabaseConnection, DatabaseConnectionAdmin)

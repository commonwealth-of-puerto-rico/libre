from __future__ import absolute_import

from django.contrib import messages
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .exceptions import SourceFileError


def check_updated(modeladmin, request, queryset):
    count = 0
    for source in queryset:
        try:
            source.check_source_data()
        except SourceFileError as exception:
            messages.error(request, _('Error opening file for source: %s; %s') % (source, str(exception)))
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


#clone_objects Copyright (C) 2009  Rune Bromer
#http://www.bromer.eu/2009/05/23/a-generic-copyclone-action-for-django-11/
def clone_objects(objects, title_fieldnames):
    def clone(from_object, title_fieldnames):
        args = dict([(fld.name, getattr(from_object, fld.name))
                     for fld in from_object._meta.fields
                     if fld is not from_object._meta.pk])

        args.pop('id')

        for field in from_object._meta.fields:
            if field.name in title_fieldnames:
                if isinstance(field, models.CharField):
                    args[field.name] = getattr(from_object, field.name) + (' (%s) ' % unicode(_('copy')))

        return from_object.__class__.objects.create(**args)

    if not hasattr(objects, '__iter__'):
        objects = [objects]

    # We always have the objects in a list now
    objs = []
    for obj in objects:
        obj = clone(obj, title_fieldnames)
        obj.save()
        objs.append(obj)


def clone(self, request, queryset):
    clone_objects(queryset, ('name', 'slug'))

    if queryset.count() == 1:
        message_bit = _('1 source was')
    else:
        message_bit = _('%s sources were') % queryset.count()
    self.message_user(request, _('%s copied.') % message_bit)

clone.short_description = _('Copy the selected source')

from __future__ import absolute_import

from ast import literal_eval
import datetime
import hashlib
from itertools import islice, izip
import logging
import re
import string
import struct
import tempfile
import urllib2

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import FieldError, ValidationError
from django.db import models, transaction
from django.db import load_backend as django_load_backend
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.defaultfilters import slugify, truncatechars

from picklefield.fields import dbsafe_encode, dbsafe_decode
import requests
from suds.client import Client

from db_drivers.models import DatabaseConnection
from lock_manager import Lock, LockError

from .exceptions import OriginDataError
from .literals import BACKEND_CHOICES, BACKEND_CLASSES

logger = logging.getLogger(__name__)


class ContainerOrigin(models.Model):
    uncompress = models.BooleanField(verbose_name=_('uncompress'))
    contained_file_list = models.TextField(verbose_name=_('contained file list'), blank=True)

    def __unicode__(self):
        return self.label

    class Meta:
        abstract = True
        verbose_name = _('compressed origin')
        verbose_name_plural = _('compressed origins')


class Origin(models.Model):
    origin_type = _('base origin')

    label = models.CharField(max_length=128, verbose_name=_('label'), help_text=_('A text by which this origin will be identified.'))
    description = models.TextField(verbose_name=_('description'), blank=True)

    def copy_data(self):
        hash_function = hashlib.sha256()

        temporary_file = tempfile.TemporaryFile(mode='w+')
        for row in self.get_data_iteraror():
            data = dbsafe_encode(row)
            temporary_file.write(dbsafe_encode(row))
            temporary_file.write('\n')
            hash_function.update(data)

        temporary_file.seek(0)
        return temporary_file, hash_function.hexdigest()

    class Meta:
        abstract = True
        verbose_name = _('origin')
        verbose_name_plural = _('origins')


class OriginURL(Origin):
    origin_type = _('URL origin')

    url = models.URLField(verbose_name=_('URL'), help_text=_('URL from which to read the data.'))
    # TODO Add support for credentials

    def get_data_iteraror(self):
        return (item for item in requests.get(self.url).iter_lines)

    class Meta:
        abstract = True
        verbose_name = _('URL origin')
        verbose_name_plural = _('URL origins')


class OriginURLFile(OriginURL, ContainerOrigin):
    origin_type = _('URL file origin')

    class Meta:
        verbose_name = _('URL file origin')
        verbose_name_plural = _('URL file origins')


class OriginPath(OriginURL, ContainerOrigin):
    origin_type = _('disk path origin')

    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=_('Location to a file in the filesystem.'))

    def get_data_iteraror(self):
        return open(self.path)

    class Meta:
        verbose_name = _('disk path origin')
        verbose_name_plural = _('disk path origins')


class OriginFTPFile(OriginURL, ContainerOrigin):
    origin_type = _('FTP file origin')

    def get_data_iteraror(self):
        return (data for data in requests.get(self.url).text)

    class Meta:
        verbose_name = _('FTP file origin')
        verbose_name_plural = _('FTP file origins')


class OriginUploadedFile(Origin, ContainerOrigin):
    origin_type = _('uploaded file origin')

    file = models.FileField(blank=True, null=True, upload_to='uploaded_files', verbose_name=_('uploaded file'))

    def get_data_iteraror(self):
        self.file.seek(0)
        return self.file

    class Meta:
        verbose_name = _('uploaded file origin')
        verbose_name_plural = _('uploaded file origins')


class OriginDatabase(Origin):
    origin_type = _('database origin')

    db_backend = models.PositiveIntegerField(choices=BACKEND_CHOICES, verbose_name=_('database backend'))
    db_name = models.CharField(max_length=128, blank=True, verbose_name=_('name'), help_text=_('Name or path to database.'))
    db_user = models.CharField(max_length=64, blank=True, verbose_name=_('user'), help_text=_('Not used with sqlite3.'))
    db_password = models.CharField(max_length=64, blank=True, verbose_name=_('password'), help_text=_('Not used with sqlite3.'))
    db_host = models.CharField(max_length=64, blank=True, verbose_name=_('host'), help_text=_('Set to empty string for localhost. Not used with sqlite3.'))
    db_port = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('port'))
    db_query = models.TextField(verbose_name=_('query'))

    def get_data_iteraror(self):
        cursor = self.load_backend().cursor()
        cursor.execute(self.db_query)

        columns_names = [description[0] for description in cursor.description]
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            row_dictionary = dict(izip(columns_names, row))
            yield row_dictionary

    def load_backend(self):
        database_settings = {}

        database_settings['ENGINE'] = BACKEND_CLASSES[self.db_backend]
        database_settings.setdefault('OPTIONS', {})
        database_settings.setdefault('TIME_ZONE', 'UTC' if settings.USE_TZ else settings.TIME_ZONE)
        database_settings['NAME'] = self.db_name
        database_settings['USER'] = self.db_user
        database_settings['PASSWORD'] = self.db_password
        database_settings['HOST'] = self.db_host
        database_settings['PORT'] = self.db_port if self.db_port else ''

        backend = django_load_backend(database_settings['ENGINE'])
        connection = backend.DatabaseWrapper(database_settings, 'data_source')

        return connection

    class Meta:
        verbose_name = _('database origin')
        verbose_name_plural = _('database origins')


class OriginRESTAPI(OriginURL):
    origin_type = _('REST API origin')

    # TODO Add support for parameters

    def get_data_iteraror(self):
        return (item for item in requests.get(self.url).json())

    class Meta:
        verbose_name = _('REST API origin')
        verbose_name_plural = _('REST API origins')


class OriginSOAPWebService(OriginURL):
    origin_type = _('SOAP webservice origin')

    endpoint = models.CharField(max_length=64, verbose_name=_('endpoint'), help_text=_('Endpoint, function or method to call.'))
    parameters = models.TextField(blank=True, verbose_name=_('parameters'))
    # TODO: Implemente 'fields to return'

    def get_data_iteraror(self):
        client = Client(self.url)
        return (item for item in getattr(client.service, self.endpoint)(**literal_eval(self.parameters)))

    class Meta:
        verbose_name = _('SOAP webservice origin')
        verbose_name_plural = _('SOAP webservice origins')

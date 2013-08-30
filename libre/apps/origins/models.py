from __future__ import absolute_import

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from ast import literal_eval
import datetime
import hashlib
from itertools import islice
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

import requests
from suds.client import Client

from db_drivers.models import DatabaseConnection
from lock_manager import Lock, LockError

from .exceptions import OriginDataError
from .literals import BACKEND_CHOICES, BACKEND_CLASSES

HASH_FUNCTION = lambda x: hashlib.sha256(x).hexdigest()
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

    def get_data(self):
        tempfile = tempfile.TemporaryFile()
        with self.get_handle() as handle:
            for data in handle.next():
                tempfile.write(data)

        tempfile.seek(0)
        new_hash = HASH_FUNCTION(tempfile.read())

    class Meta:
        abstract = True
        verbose_name = _('origin')
        verbose_name_plural = _('origins')


class OriginURL(Origin):
    origin_type = _('URL origin')

    url = models.URLField(verbose_name=_('URL'), help_text=_('URL from which to read the data.'))
    # TODO Add support for credentials

    def get_handle(self):
        try:
            handle = urllib2.urlopen(self.url)
        except urllib2.URLError as exception:
            logger.error('Unable to open file for origin: %s ;%s' % (self.name, exception))
            raise OriginDataError(unicode(exception))
        else:
            return handle

    class Meta:
        abstract = True
        verbose_name = _('URL origin')
        verbose_name_plural = _('URL origins')


class OriginURLFile(Origin, ContainerOrigin):
    origin_type = _('URL file origin')

    class Meta:
        verbose_name = _('URL file origin')
        verbose_name_plural = _('URL file origins')


class OriginPath(Origin, ContainerOrigin):
    origin_type = _('disk path origin')

    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=_('Location to a file in the filesystem.'))

    def get_handle(self):
        try:
            with open(self.path) as handle:
                handle.read(1)
        except IOError as exception:
            logger.error('Unable to open file for origin: %s ;%s' % (self.name, exception))
            raise OriginDataError(unicode(exception))

    class Meta:
        verbose_name = _('disk path origin')
        verbose_name_plural = _('disk path origins')


class OriginFTPFile(OriginURL, ContainerOrigin):
    origin_type = _('FTP file origin')

    def get_handle(self):
        return requests.get(self.url)

    class Meta:
        verbose_name = _('FTP file origin')
        verbose_name_plural = _('FTP file origins')


class OriginUploadedFile(Origin, ContainerOrigin):
    origin_type = _('uploaded file origin')

    file = models.FileField(blank=True, null=True, upload_to='uploaded_files', verbose_name=_('uploaded file'))

    def get_handle(self):
        try:
            self.file.read(1)
        except IOError as exception:
            logger.error('Unable to open file for origin: %s ;%s' % (self.name, exception))
            raise OriginDataError(unicode(exception))
        else:
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

    def get_handle(self):
        cursor = self.database_connection.load_backend().cursor()
        cursor.execute(self.db_query, {})

        return cursor

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

    def get_handle(self):
        return (item for item in requests.get(self.url).json())

    class Meta:
        verbose_name = _('REST API origin')
        verbose_name_plural = _('REST API origins')


class OriginSOAPWebService(OriginURL):
    origin_type = _('SOAP webservice origin')

    endpoint = models.CharField(max_length=64, verbose_name=_('endpoint'), help_text=_('Endpoint, function or method to call.'))
    parameters = models.TextField(blank=True, verbose_name=_('parameters'))
    # TODO: Implemente 'fields to return'

    def get_handle(self):
        client = Client(self.url)
        return (item for item in getattr(client.service, self.endpoint)(**literal_eval(self.parameters)))

    class Meta:
        verbose_name = _('SOAP webservice origin')
        verbose_name_plural = _('SOAP webservice origins')

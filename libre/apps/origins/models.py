from __future__ import absolute_import

import datetime
import hashlib
from itertools import islice
import logging
import re
import string
import struct
import urllib2

from django.contrib.auth.models import Group
from django.core.exceptions import FieldError, ValidationError
from django.db import models, transaction
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.defaultfilters import slugify, truncatechars

from django.conf import settings
from django.db import models, load_backend as django_load_backend
from django.utils.translation import ugettext_lazy as _

import fiona
from model_utils.managers import InheritanceManager
from picklefield.fields import PickledObjectField
from pyproj import Proj, transform
import requests
from shapely import geometry
from suds.client import Client
import xlrd

from db_drivers.models import DatabaseConnection
from icons.models import Icon
from lock_manager import Lock, LockError

from .exceptions import LIBREAPIError, SourceFileError
from .job_processing import Job
from .literals import (DEFAULT_LIMIT, DEFAULT_SHEET, DATA_TYPE_CHOICES,
    RENDERER_BROWSEABLE_API, RENDERER_JSON, RENDERER_XML, RENDERER_YAML, RENDERER_LEAFLET)
from .managers import SourceAccessManager
from .query import Query
from .utils import DATA_TYPE_FUNCTIONS, UnicodeReader, parse_range

HASH_FUNCTION = lambda x: hashlib.sha256(x).hexdigest()
logger = logging.getLogger(__name__)


class Origin(models.Model):
    label = models.CharField(max_length=128, verbose_name=_('label'), help_text=_('A text by which this origin will be identified.'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    is_compressed = models.BooleanField(verbose_name=_('compressed'))
    contained_file_list = models.TextField(verbose_name=_('contained file list'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _('origin')
        verbose_name_plural = _('origins')


class OriginURL(Origin):
    url = models.URLField(blank=True, verbose_name=_('URL'), help_text=_('Import a file from an URL.'))

    def check_origin(self):
        try:
            handle = urllib2.urlopen(self.url)
        except urllib2.URLError as exception:
            logger.error('Unable to open file for source id: %s ;%s' % (self.id, exception))
            raise SourceFileError(unicode(exception))
        else:
            new_hash = HASH_FUNCTION(handle.read())
            handle.close()

    class Meta:
        verbose_name = _('URL origin')
        verbose_name_plural = _('URL origins')


class OriginPath(Origin):
    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=_('Location to a file in the filesystem.'))

    def check_origin(self):
        try:
            with open(self.path) as handle:
                new_hash = HASH_FUNCTION(handle.read())
        except IOError as exception:
            logger.error('Unable to open file for source id: %s ;%s' % (self.id, exception))
            raise SourceFileError(unicode(exception))

    class Meta:
        verbose_name = _('path origin')
        verbose_name_plural = _('path origins')


class OriginFile(Origin):
    file = models.FileField(blank=True, null=True, upload_to='spreadsheets', verbose_name=_('uploaded file'))

    def check_origin(self):
        try:
            new_hash = HASH_FUNCTION(self.file.read())
        except IOError as exception:
            logger.error('Unable to open file for source id: %s ;%s' % (self.id, exception))
            raise SourceFileError(unicode(exception))
        else:
            self.file.seek(0)

    class Meta:
        verbose_name = _('file origin')
        verbose_name_plural = _('file origins')


BACKEND_POSTGRESQL_PSYCOPG2 = 1
BACKEND_POSTGRESQL = 2
BACKEND_MYSQL = 3
BACKEND_SQLITE3 = 4
BACKEND_ORACLE = 5

BACKEND_CHOICES = (
    (BACKEND_POSTGRESQL_PSYCOPG2, _('PostgreSQL (psycopg2)')),
    (BACKEND_POSTGRESQL, _('PostgreSQL')),
    (BACKEND_MYSQL, _('MySQL')),
    (BACKEND_SQLITE3, _('SQLite')),
    (BACKEND_ORACLE, _('Oracle')),
)

BACKEND_CLASSES = {
    BACKEND_POSTGRESQL_PSYCOPG2: 'django.db.backends.postgresql_psycopg2',
    BACKEND_POSTGRESQL: 'django.db.backends.postgresql',
    BACKEND_MYSQL: 'django.db.backends.mysql',
    BACKEND_SQLITE3: 'django.db.backends.sqlite3',
    BACKEND_ORACLE: 'django.db.backends.oracle',
}


class OriginDatabase(Origin):
    db_backend = models.PositiveIntegerField(choices=BACKEND_CHOICES, verbose_name=_('database backend'))
    db_name = models.CharField(max_length=128, blank=True, verbose_name=_('name'), help_text=_('Name or path to database.'))
    db_user = models.CharField(max_length=64, blank=True, verbose_name=_('user'), help_text=_('Not used with sqlite3.'))
    db_password = models.CharField(max_length=64, blank=True, verbose_name=_('password'), help_text=_('Not used with sqlite3.'))
    db_host = models.CharField(max_length=64, blank=True, verbose_name=_('host'), help_text=_('Set to empty string for localhost. Not used with sqlite3.'))
    db_port = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('port'))
    db_query = models.TextField(verbose_name=_('query'))

    def check_origin(self):
        cursor = self.database_connection.load_backend().cursor()
        cursor.execute(self.db_query, {})
        return cursor.fetchall()

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

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _('database origin')
        verbose_name_plural = _('database origins')

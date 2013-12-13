from __future__ import absolute_import

from ast import literal_eval
import hashlib
from itertools import izip
import logging
import tempfile
import types

from django.conf import settings
from django.db import models
from django.db import load_backend as django_load_backend
from django.utils.translation import ugettext_lazy as _

from model_utils.managers import InheritanceManager
import requests
from suds.client import Client

from .literals import BACKEND_CHOICES, BACKEND_CLASSES

logger = logging.getLogger(__name__)


class ContainerOrigin(models.Model):
    uncompress = models.BooleanField(verbose_name=_('uncompress'))
    contained_file_list = models.TextField(verbose_name=_('contained file list'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _('compressed origin')
        verbose_name_plural = _('compressed origins')


class Origin(models.Model):
    origin_type = _('base origin')

    label = models.CharField(max_length=128, verbose_name=_('label'), help_text=_('A text by which this origin will be identified.'))
    description = models.TextField(verbose_name=_('description'), blank=True)

    objects = InheritanceManager()

    def copy_data(self):
        """
        Copy the data from the it's point of origin, serializing it,
        storing it serialized as well as in it's raw form and calculate
        a running hash of the serialized representation
        """
        HASH_FUNCTION = hashlib.sha256()

        self.copy_file = tempfile.NamedTemporaryFile(mode='w+b')

        for row in self.get_data_iteraror():
            self.copy_file.write(row)
            HASH_FUNCTION.update(row)

        self.copy_file.seek(0)
        self.new_hash = HASH_FUNCTION.hexdigest()

    def discard_copy(self):
        """
        Close all the TemporaryFile handles so that the space on disk
        can be garbage collected
        """
        #self.temporary_file.close()
        self.copy_file.close()

    @property
    def identifier(self):
        return self.label

    def __unicode__(self):
        subclass = Origin.objects.get_subclass(pk=self.pk)
        return u'%s (%s)' % (subclass.label, subclass.origin_type)

    class Meta:
        verbose_name = _('origin')
        verbose_name_plural = _('origins')
        ordering = ('label',)


class OriginURL(Origin):
    origin_type = _('URL')

    url = models.URLField(verbose_name=_('URL'), help_text=_('URL from which to read the data.'))
    # TODO Add support for credentials

    def get_data_iteraror(self):
        """
        Generator to stream the remote file piece by piece.
        """
        CHUNK_SIZE = 1024
        return (item for item in requests.get(self.url).iter_content(CHUNK_SIZE))

    @property
    def identifier(self):
        return self.url

    class Meta:
        abstract = True
        verbose_name = _('URL origin')
        verbose_name_plural = _('URL origins')


class OriginURLFile(OriginURL, ContainerOrigin):
    origin_type = _('URL file')

    class Meta:
        verbose_name = _('URL file origin')
        verbose_name_plural = _('URL file origins')


class OriginPath(Origin, ContainerOrigin):
    origin_type = _('disk path')

    path = models.TextField(blank=True, null=True, verbose_name=_('path to file'), help_text=_('Location to a file in the filesystem.'))

    def get_data_iteraror(self):
        """
        Generator to read a file piece by piece.
        """
        CHUNK_SIZE = 1024
        file_object = open(self.path)

        while True:
            data = file_object.read(CHUNK_SIZE)
            if not data:
                break
            yield data

        file_object.close()

    @property
    def identifier(self):
        return self.path

    class Meta:
        verbose_name = _('disk path origin')
        verbose_name_plural = _('disk path origins')


class OriginFTPFile(OriginURL, ContainerOrigin):
    origin_type = _('FTP file')

    class Meta:
        verbose_name = _('FTP file origin')
        verbose_name_plural = _('FTP file origins')


class OriginUploadedFile(Origin, ContainerOrigin):
    origin_type = _('uploaded file')

    file = models.FileField(blank=True, null=True, upload_to='uploaded_files', verbose_name=_('uploaded file'))

    def get_data_iteraror(self):
        self.file.seek(0)
        return self.file

    @property
    def identifier(self):
        return self.file

    class Meta:
        verbose_name = _('uploaded file origin')
        verbose_name_plural = _('uploaded file origins')


class OriginDatabase(Origin):
    origin_type = _('database')

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
    origin_type = _('REST API')

    # TODO Add support for parameters

    def get_data_iteraror(self):
        return (item for item in requests.get(self.url).json())

    class Meta:
        verbose_name = _('REST API origin')
        verbose_name_plural = _('REST API origins')


class OriginSOAPWebService(OriginURL):
    origin_type = _('SOAP webservice')

    endpoint = models.CharField(max_length=64, verbose_name=_('endpoint'), help_text=_('Endpoint, function or method to call.'))
    parameters = models.TextField(blank=True, verbose_name=_('parameters'))

    def get_data_iteraror(self):
        client = Client(self.url)
        if self.parameters:
            parameters = literal_eval(self.parameters)
        else:
            parameters = {}

        return (dict(item) for item in getattr(client.service, self.endpoint)(**parameters))

    class Meta:
        verbose_name = _('SOAP webservice origin')
        verbose_name_plural = _('SOAP webservice origins')


class OriginPythonScript(Origin):
    origin_type = _('Python script')

    script_text = models.TextField(verbose_name=_('script text'), help_text=_('Assign resulting values to the _results variable. Ideally it should be a list of dictionaries.'))

    def get_data_iteraror(self):
        _results = []
        code = compile(self.script_text, '<string>', 'exec')
        exec code

        return (item for item in _results)

    class Meta:
        verbose_name = _('python script origin')
        verbose_name_plural = _('python script origin')

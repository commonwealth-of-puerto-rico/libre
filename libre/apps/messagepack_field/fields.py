from __future__ import unicode_literals

import base64
import datetime

from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

import six
import msgpack


def default_decoder(obj):
    if b'__datetime__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    elif b'__date__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%d").date()
    elif b'__time__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%H:%M:%S.%f").time()
    return obj


def default_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    elif isinstance(obj, datetime.date):
        return {'__date__': True, 'as_str': obj.strftime("%Y%m%d")}
    elif isinstance(obj, datetime.time):
        return {'__time__': True, 'as_str': obj.strftime("%H:%M:%S.%f")}
    return obj


class Creator(object):
    """
    Taken from https://github.com/derek-schaefer/django-json-field/blob/master/json_field/fields.py
    """

    _state_key = '_messagepack_field_state'

    def __init__(self, field, lazy):
        self.field = field
        self.lazy = lazy

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')

        if self.lazy:
            state = getattr(obj, self._state_key, None)
            if state is None:
                state = {}
                setattr(obj, self._state_key, state)

            if state.get(self.field.name, False):
                return obj.__dict__[self.field.name]

            value = self.field.to_python(obj.__dict__[self.field.name])
            obj.__dict__[self.field.name] = value
            state[self.field.name] = True
        else:
            value = obj.__dict__[self.field.name]

        return value

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value if self.lazy else self.field.to_python(value)


class MessagePackField(models.TextField):
    """ Stores and loads data in the MessagePack format. """

    description = _('MessagePack')

    def __init__(self, *args, **kwargs):
        self.default_error_messages = {
            'invalid': _('Enter a valid MessagePack object')
        }
        self._db_type = kwargs.pop('db_type', None)
        self.lazy = kwargs.pop('lazy', True)
        self.encoder = kwargs.pop('encoder', default_encoder)
        self.decoder = kwargs.pop('decoder', default_decoder)

        super(MessagePackField, self).__init__(*args, **kwargs)

    def db_type(self, *args, **kwargs):
        if self._db_type:
            return self._db_type
        return super(MessagePackField, self).db_type(*args, **kwargs)

    def to_python(self, value):
        if value == '':
            if self.null:
                return None
            if self.blank:
                return ''
        #try:
        return msgpack.loads(base64.b64decode(value), object_hook=self.decoder)
        #except (msgpack.ExtraData, msgpack.UnpackValueError, TypeError):
        #    return value
        #    msg = self.error_messages['invalid'] % value
        #    raise ValidationError(msg)

    def get_prep_value(self, value):
        return base64.b64encode(msgpack.dumps(value, default=self.encoder))

    def contribute_to_class(self, cls, name):
        super(MessagePackField, self).contribute_to_class(cls, name)

        #setattr(cls, name, Creator(self, lazy=self.lazy)) # deferred deserialization


try:
    from south.modelsinspector import add_introspection_rules
    rules = [
        (
            (MessagePackField,),
            [],
            {
                'db_type': ['_db_type', {'default': None}]
            }
        )
    ]
    add_introspection_rules(rules, ['^messagepack_field\.fields\.MessagePackField'])
except ImportError:
    pass

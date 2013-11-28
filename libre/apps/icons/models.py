from __future__ import absolute_import

import base64

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import logging

import PIL
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)


class Icon(models.Model):
    _cache = {}

    name = models.CharField(max_length=48, verbose_name=_(u'name'), unique=True)
    label = models.CharField(max_length=48, verbose_name=_(u'label'), blank=True)
    icon_file = models.FileField(upload_to='icons', verbose_name='file')

    def __unicode__(self):
        return self.label or self.name

    def compose(self, as_base64=False):
        try:
            self.__class__._cache.setdefault(self.pk, {})
            return self.__class__._cache[self.pk][as_base64]
        except KeyError:
            image = PIL.Image.open(self.icon_file.file)
            output = StringIO()
            image.save(output, 'PNG')
            contents = output.getvalue()
            output.close()
            if as_base64:
                contents = 'data:image/png;base64,%s' % base64.b64encode(contents)
            self.__class__._cache.setdefault(self.pk, {})
            self.__class__._cache[self.pk][as_base64] = contents
            return contents

    def compose_base64(self):
        return self.compose(as_base64=True)

    def get_absolute_url(self):
        return reverse('display', args=[self.name])

    class Meta:
        verbose_name = _(u'icon')
        verbose_name_plural = _(u'icons')
        ordering = ['label', 'name']

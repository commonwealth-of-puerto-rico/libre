from __future__ import absolute_import

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import logging

import PIL

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class Icon(models.Model):
    _cache = {}

    name = models.CharField(max_length=48, verbose_name=_(u'name'), unique=True)
    label = models.CharField(max_length=48, verbose_name=_(u'label'), blank=True)
    icon_file = models.FileField(upload_to='icons', verbose_name='file')

    def __unicode__(self):
        return self.label or self.name

    def display(self): # TODO: move to widgets?
        try:
            result = self.__class__._cache[self.name]
        except KeyError:
            result = self._compose(self)
            self.__class__._cache[self.name] = result

        return mark_safe('<img style="vertical-align: middle;" src="%s" />' % result)

    def _compose(self, icon):
        image = PIL.Image.open(self.icon_file.file)
        output = StringIO()
        image.save(output, 'PNG')
        contents = output.getvalue().encode('base64')
        output.close()
        return 'data:image/png;base64,%s' % contents

    class Meta:
        verbose_name = _(u'icon')
        verbose_name_plural = _(u'icons')

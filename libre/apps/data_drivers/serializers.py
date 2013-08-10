from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .models import Source, SourceDataVersion


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    data = serializers.HyperlinkedIdentityField(view_name='source-get_all', format='html')
    limits_field = serializers.SerializerMethodField('get_limits')

    class Meta:
        model = Source
        fields = ('id', 'name', 'slug', 'description', 'limits_field', 'url', 'data', 'versions')

    def get_limits(self, obj):
        return getattr(obj, 'limit', _('None'))


class SourceDataVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SourceDataVersion
        fields = ('url', 'id', 'source', 'timestamp', 'datetime', 'checksum', 'metadata', 'ready')

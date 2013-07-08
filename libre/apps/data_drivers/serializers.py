from __future__ import absolute_import

from django.core.urlresolvers import reverse

from rest_framework import serializers

from .models import Source


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    data = serializers.HyperlinkedIdentityField(view_name='source-get_all', format='html')

    class Meta:
        model = Source
        fields = ('id', 'name', 'slug', 'description', 'url', 'data')

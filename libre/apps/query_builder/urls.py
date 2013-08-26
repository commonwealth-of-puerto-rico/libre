from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url

from .views import query_builder_index_view

urlpatterns = patterns('',
    url(r'^$', query_builder_index_view, name='index'),
)

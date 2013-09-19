from django.conf.urls.defaults import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns


from .views import (LibreMetadataList, SourceDataVersionList, SourceDataVersionDetail,
    SourceDetail, SourceList, SourceGetAll, SourceGetOne)


urlpatterns = patterns('data_drivers.views',
    url(r'^$', 'api_root', name='api_root'),

    url(r'^libre/$', LibreMetadataList.as_view(), name='libremetadata-list'),

    url(r'^sources/$', SourceList.as_view(), name='source-list'),
    url(r'^sources/(?P<slug>[-\w]+)/$', SourceDetail.as_view(), name='source-detail'),
    url(r'^sources/(?P<slug>[-\w]+)/data/$', SourceGetAll.as_view(), name='source-get_all'),
    url(r'^sources/(?P<slug>[-\w]+)/data/(?P<id>[0-9]+)/$', SourceGetOne.as_view(), name='source-get_one'),

    url(r'^sources/data_version/$', SourceDataVersionList.as_view(), name='sourcedataversion-list'),
    url(r'^sources/data_versions/(?P<pk>[0-9]+)/$', SourceDataVersionDetail.as_view(), name='sourcedataversion-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

from django.conf.urls.defaults import patterns, url, include

from rest_framework.urlpatterns import format_suffix_patterns

from .views import SourceList, SourceDetail, SourceGetAll, SourceGetOne

urlpatterns = patterns('data_drivers.views',
    url(r'^$', 'api_root', name='api_root'),
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^sources/$', SourceList.as_view(), name='source-list'),
    url(r'^sources/(?P<pk>[0-9]+)/$', SourceDetail.as_view(), name='source-detail'),
    url(r'^sources/(?P<pk>[0-9]+)/data/$', SourceGetAll.as_view(), name='source-get_all'),
    url(r'^sources/(?P<pk>[0-9]+)/data/(?P<id>[0-9]+)/$', SourceGetOne.as_view(), name='source-get_one'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

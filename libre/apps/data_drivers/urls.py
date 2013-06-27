from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('data_drivers.views',
    #url(r'^namespace/all/$', 'namespace_list', (), 'namespace_list'),
    #url(r'^namespace/(?P<endpoint>\w+)/$', 'namespace_view', (), 'namespace_view'),
    url(r'^resource/(?P<resource_slug>\w+)/all/$', 'resource_get_all', (), 'resource_get_all'),
    url(r'^resource/(?P<resource_slug>\w+)/(?P<id>\w+)/$', 'resource_get_one', (), 'resource_get_one'),
)

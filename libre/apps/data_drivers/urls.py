from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('data_drivers.views',
    url(r'^(?P<endpoint>\w+)/(?P<resource>\w+)/all/$', 'resource_get_all', (), 'resource_get_all'),
    url(r'^(?P<endpoint>\w+)/(?P<resource>\w+)/(?P<id>\w+)/$', 'resource_get_one', (), 'resource_get_one'),
)

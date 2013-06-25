from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('data_drivers.views',
    url(r'^(?P<endpoint>\w+)/(?P<resource>\w+)/(?P<id>\w+)/$', 'resource_get', (), 'resource_get'),
)

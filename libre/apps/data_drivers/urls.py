from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('data_drivers.views',
    url(r'^all/$', 'resource_list', (), 'resource_list'),
    url(r'^(?P<resource_slug>[-\w]+)/$', 'resource_get_all', (), 'resource_get_all'),
    url(r'^(?P<resource_slug>[-\w]+)/(?P<id>\w+)/$', 'resource_get_one', (), 'resource_get_one'),
)

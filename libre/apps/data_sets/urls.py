from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('data_sets.views',
    url(r'^$', 'sources_view', name='sources_view'),
    url(r'^(?P<source_slug>[-a-zA-Z0-9_]+)/$', 'source_view', (), 'source_view'),
)

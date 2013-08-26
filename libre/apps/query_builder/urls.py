from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('query_builder.views',
    url(r'^$', 'index', name='index'),
)

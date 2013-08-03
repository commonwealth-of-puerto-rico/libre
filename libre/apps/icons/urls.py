from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('icons.views',
    url(r'^display/(?P<slug>[-\w]+)/$', 'display', name='display'),
)

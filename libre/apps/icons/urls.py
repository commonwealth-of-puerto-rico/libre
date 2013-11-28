from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('icons.views',
    url(r'^(?P<slug>[-\w]+)/base64/$', 'display', {'as_base64': True}, name='display_base64'),
    url(r'^(?P<slug>[-\w]+)/$', 'display', name='display'),
)

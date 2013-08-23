from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('client.views',
    url(r'^$', 'libre_client', name='libre_client'),
)

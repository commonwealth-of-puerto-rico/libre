from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from data_drivers.sites import SitePlus

admin.site = SitePlus()
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('main.urls')),
    url(r'^api/', include('data_drivers.urls')),
)

if settings.DEVELOPMENT:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()


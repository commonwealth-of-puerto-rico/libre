from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns('main.views',
    url(r'^$', 'home', (), 'home'),
    url(r'^about/$', 'about_view', (), 'about_view'),
)

urlpatterns += patterns('',
    url(r'^favicon\.ico$', RedirectView.as_view(url='%simages/favicon.ico' % settings.STATIC_URL), name='favicon'),
)

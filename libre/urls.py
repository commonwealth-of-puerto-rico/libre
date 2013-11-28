from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from main.sites import SitePlus
from main.views import CustomObtainAuthToken

admin.site = SitePlus()
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('main.urls')),
    url(r'^api/', include('data_drivers.urls')),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^auth/token/obtain/', CustomObtainAuthToken.as_view(), name='auth_token_obtain'),
    url(r'^data/', include('data_sets.urls')),
    url(r'^icons_app/', include('icons.urls')),
    url(r'^query_builder/', include('query_builder.urls', namespace='query_builder')),
)

if settings.DEVELOPMENT:
    from django.conf import settings
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += patterns('',
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

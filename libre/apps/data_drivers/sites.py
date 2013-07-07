# from: https://coderwall.com/p/ieh-sg
from django.contrib.admin.sites import AdminSite


class AdminMixin(object):
    """Mixin for AdminSite to allow custom dashboard views."""

    def __init__(self, *args, **kwargs):
        return super(AdminMixin, self).__init__(*args, **kwargs)

    def get_urls(self):
        """Add our dashboard view to the admin urlconf. Deleted the default index."""
        from django.conf.urls import patterns, url
        from views import DashboardWelcomeView

        urls = super(AdminMixin, self).get_urls()
        del urls[0]
        custom_url = patterns('',
               url(r'^$', self.admin_view(DashboardWelcomeView.as_view()),
                    name="index")
        )

        return custom_url + urls


class SitePlus(AdminMixin, AdminSite):
    """
    A Django AdminSite with the AdminMixin to allow registering custom
    dashboard view.
    """

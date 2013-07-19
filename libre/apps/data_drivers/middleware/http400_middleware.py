from django.conf import settings
from django.http import HttpResponseForbidden
from django.template import RequestContext, Template, loader, TemplateDoesNotExist
from django.utils.importlib import import_module

from data_drivers.exceptions import Http400


#http://mitchfournier.com/2010/07/12/show-a-custom-403-forbidden-error-page-in-django/
class Http400Middleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, Http400):
            try:
                # Handle import error but allow any type error from view
                callback = getattr(import_module(settings.ROOT_URLCONF), 'handler400')
                return callback(request, exception)
            except (ImportError, AttributeError):
                # Try to get a 400 template
                try:
                    # First look for a user-defined template named "400.html"
                    template = loader.get_template('400.html')
                except TemplateDoesNotExist:
                    # If a template doesn't exist in the project, use the following hardcoded template
                    template = Template('''{% load i18n %}
                     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                            "http://www.w3.org/TR/html4/strict.dtd">
                     <html>
                     <head>
                         <title>{% trans "400 ERROR: Bad request" %}</title>
                     </head>
                     <body>
                         <h1>{% trans "Bad request (400)" %}</h1>
                         {% trans "Please check your request syntax." %}<br/>
                         {% trans "Exception message" %}: {{ exception }}
                     </body>
                     </html>''')

                # Now use context and render template
                context = RequestContext(request)
                context.update({'exception': exception})

                return HttpResponseForbidden(template.render(context))

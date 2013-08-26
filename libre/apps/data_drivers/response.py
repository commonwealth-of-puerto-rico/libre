from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import status, exceptions
from rest_framework.compat import six
from rest_framework.response import Response
from rest_framework.settings import api_settings


class CustomResponse(Response):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES

    @property
    def rendered_content(self):
        renderer = getattr(self, 'accepted_renderer', None)
        media_type = getattr(self, 'accepted_media_type', None)
        context = getattr(self, 'renderer_context', None)

        assert renderer, ".accepted_renderer not set on Response"
        assert media_type, ".accepted_media_type not set on Response"
        assert context, ".renderer_context not set on Response"
        context['response'] = self

        charset = renderer.charset
        content_type = self.content_type

        if content_type is None and charset is not None:
            content_type = "{0}; charset={1}".format(media_type, charset)
        elif content_type is None:
            content_type = media_type
        self['Content-Type'] = content_type

        try:
            ret = renderer.render(self.data, media_type, context)
        except Exception as exception:
            content = self.handle_exception(exception)
            self.request = context['request']
            ret = renderer.render(content, media_type, context)

        if isinstance(ret, six.text_type):
            assert charset, 'renderer returned unicode, and did not specify ' \
            'a charset value.'
            return bytes(ret.encode(charset))
        return ret

    def handle_exception(self, exc):
        if isinstance(exc, exceptions.Throttled):
            # Throttle wait header
            self['X-Throttle-Wait-Seconds'] = '%d' % exc.wait

        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                self.headers['WWW-Authenticate'] = auth_header
            else:
                self.status_code = status.HTTP_403_FORBIDDEN

        if isinstance(exc, exceptions.APIException):
            self.status_code = exc.status_code
            self.exception = True
            return {'detail': exc.detail}
        elif isinstance(exc, Http404):
            self.status_code = status.HTTP_404_NOT_FOUND
            self.exception = True
            return {'detail': 'Not found'}
        elif isinstance(exc, PermissionDenied):
            self.status_code = status.HTTP_403_FORBIDDEN
            self.exception = True
            return {'detail': 'Permission denied'}
        raise

    def get_authenticate_header(self, request):
        """
        If a request is unauthenticated, determine the WWW-Authenticate
        header to use for 401 responses, if any.
        """
        authenticators = self.get_authenticators()
        if authenticators:
            return authenticators[0].authenticate_header(request)

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        return [auth() for auth in self.authentication_classes]

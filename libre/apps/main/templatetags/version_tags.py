from __future__ import absolute_import

from django.template import Library

from .. import __version__

register = Library()


@register.assignment_tag
def project_version():
    """Tag to return the current project's version"""
    return __version__

from __future__ import absolute_import

VERSION = (1, 0, 0, 'final', 0)


def get_version(*args, **kwargs):
    # Don't litter libre/__init__.py with all the get_version stuff.
    # Only import if it's actually called.
    from django.utils.version import get_version
    return get_version(*args, **kwargs)


__author__ = 'Roberto Rosario'
__copyright__ = 'Copyright 2013 Office of the Chief Information Officer, Commonwealth of Puerto Rico'
__credits__ = ['Roberto Rosario']
__email__ = 'roberto.rosario.gonzalez@gmail.com'
__license__ = 'GPL'
__maintainer__ = 'Roberto Rosario'
__status__ = 'Production'
__title__ = 'libre'
__version__ = get_version(VERSION)

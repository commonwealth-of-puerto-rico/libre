from __future__ import absolute_import


__author__ = 'Roberto Rosario'
__copyright__ = 'Copyright 2013 Office of the Chief Information Officer, Commonwealth of Puerto Rico'
__credits__ = ['Roberto Rosario']
__license__ = 'GPL'
__maintainer__ = 'Roberto Rosario'
__email__ = 'roberto.rosario.gonzalez@gmail.com'
__status__ = 'Production'

__version_info__ = {
    'major': 0,
    'minor': 7,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 0
}


def get_version():
    '''
    Return the formatted version information
    '''
    vers = ['%(major)i.%(minor)i' % __version_info__, ]

    if __version_info__['micro']:
        vers.append('.%(micro)i' % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s%(serial)i' % __version_info__)
    return ''.join(vers)


__version__ = get_version()

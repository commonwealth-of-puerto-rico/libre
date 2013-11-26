#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import libre

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()
with open('LICENSE') as f:
    license = f.read()
with open('libre/requirements/common.txt') as f:
    requires = f.readlines()

packages=['libre', 'libre.management', 'libre.apps', 'libre.management.commands',
    'libre.apps.origins', 'libre.apps.icons', 'libre.apps.main', 'libre.apps.query_builder',
    'libre.apps.data_drivers', 'libre.apps.scheduler', 'libre.apps.lock_manager',
    'libre.apps.origins.migrations', 'libre.apps.icons.migrations', 'libre.apps.icons.templatetags',
    'libre.apps.main.templatetags', 'libre.apps.data_drivers.migrations', 'libre.apps.lock_manager.migrations']

setup(
    author='Roberto Rosario',
    author_email='rrosario@ogp.pr.gov',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Communications :: File Sharing',
    ],
    description='Large Information Batch Restructuring Engine.',
    include_package_data=True,
    install_requires=requires,
    license=license,
    long_description=readme + '\n\n' + history,
    name='libre',
    packages=packages,
    platforms=['any'],
    scripts=['libre/bin/libre-admin.py'],
    url='https://github.com/commonwealth-of-puerto-rico/libre',
    version=libre.__version__,
    zip_safe=False,
)

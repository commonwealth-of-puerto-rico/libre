.. _development:

Development
===========

**LIBRE** is under active development, and contributions are welcome.

If you have a feature request, suggestion, or bug reports, please open a new
issue on the `GitHub issue tracker`_. To submit patches, please send a pull request on GitHub_.  Contributors are credited accordingly on the :ref:`contributors` section.


.. _GitHub: https://github.com/commonwealth-of-puerto-rico/libre
.. _`GitHub issue tracker`: https://github.com/commonwealth-of-puerto-rico/libre/issues

.. _scm:


Source Control
--------------


**LIBRE** source is controlled with Git_

The project is publicly accessible, hosted and can be cloned from **GitHub** using::

    $ git clone https://github.com/commonwealth-of-puerto-rico/libre.git


Git branch structure
--------------------

**LIBRE** follows the model layout by Vincent Driessen in his `Successful Git Branching Model`_ blog post. Git-flow_ is a great tool for managing the repository in this way.

``develop``
    The "next release" branch, likely unstable.
``master``
    Current production release (|version|).
``feature/``
    Unfinished/ummerged feature.


Each release is tagged and available for download on the Downloads_ section of the **LIBRE** repository on GitHub_

When submitting patches, please place your feature/change in its own branch prior to opening a pull request on GitHub_.
To familiarize yourself with the technical details of the project read the :ref:`internals` section.

.. _Git: http://git-scm.org
.. _`Successful Git Branching Model`: http://nvie.com/posts/a-successful-git-branching-model/
.. _git-flow: http://github.com/nvie/gitflow
.. _Downloads:  https://github.com/commonwealth-of-puerto-rico/libre/releases

.. _docs:

Versioning
----------
**LIBRE** follows the `Semantic Versioning specification <http://semver.org/>`_.

Summary:

Given a version number ``MAJOR.MINOR.PATCH``, increment the:

``MAJOR`` version when you make incompatible API changes,
``MINOR`` version when you add functionality in a backwards-compatible manner, and
``PATCH`` version when you make backwards-compatible bug fixes.
Additional labels for pre-release and build metadata are available as extensions
to the ``MAJOR.MINOR.PATCH`` format.


How To Contribute
-----------------

.. include:: contributing.rst


Debugging
---------

**LIBRE** makes extensive use of Django's new `logging capabilities`_.
To enable debug logging for the ``data_drivers`` app for example add the following
lines to your ``settings_local.py`` file::

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(name)s %(process)d %(thread)d %(message)s'
            },
            'intermediate': {
                'format': '%(name)s <%(process)d> [%(levelname)s] "%(funcName)s() %(message)s"'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console':{
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'formatter': 'intermediate'
            }
        },
        'loggers': {
            'data_drivers': {
                'handlers':['console'],
                'propagate': True,
                'level':'DEBUG',
            },
        }
    }


Likewise, to see the debug output of the ``origins`` app, just add the following inside the ``loggers`` block::


    'origins': {
        'handlers':['console'],
        'propagate': True,
        'level':'DEBUG',
    },


.. _`logging capabilities`: https://docs.djangoproject.com/en/dev/topics/logging

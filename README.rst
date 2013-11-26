
LIBRE: Libre Information Batch Restructuring Engine
===================================================


.. image:: https://travis-ci.org/commonwealth-of-puerto-rico/libre.png?branch=master
    :target: https://travis-ci.org/commonwealth-of-puerto-rico/libre

.. image:: https://coveralls.io/repos/commonwealth-of-puerto-rico/libre/badge.png?branch=master
        :target: https://coveralls.io/r/commonwealth-of-puerto-rico/libre?branch=master


The engine that's powering the liberation of government data for island of Puerto Rico.

.. image:: https://raw.github.com/commonwealth-of-puerto-rico/libre/master/docs/_static/libre_logo.png


.. image:: https://raw.github.com/commonwealth-of-puerto-rico/libre/master/docs/_static/main_diagram.png



Turn this:
----------

.. image:: https://raw.github.com/commonwealth-of-puerto-rico/libre/master/docs/_static/before.png


Into this!
----------

.. image:: https://raw.github.com/commonwealth-of-puerto-rico/libre/master/docs/_static/after.png


Query your data afterwards too!
-------------------------------


.. image:: https://raw.github.com/commonwealth-of-puerto-rico/libre/master/docs/_static/math_query.png



INSTALLATION
============

Install OS dependencies first.

On Linux
--------

.. code-block:: bash

    $ sudo apt-get install libgdal-dev -y

On OSX using MacPorts
---------------------

.. code-block:: bash

    $ sudo port install geos
    $ sudo port install gdal

Github installation
-------------------

.. code-block:: bash

    $ git clone https://github.com/commonwealth-of-puerto-rico/libre.git
    $ cd libre
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r libre/requirements.txt
    $ ./manage.py syncdb --migrate
    $ cat <<'EOF' > settings_local.py
    DEBUG=True
    DEVELOPMENT=True
    ALLOWED_HOSTS = ['*']
    EOF
    $ ./manage.py runserver

Point your browser to 127.0.0.1:8000

PyPI installation
-----------------

.. code-block:: bash

    $ virtualenv libre-venv
    $ source libre-venv/bin/activate
    $ pip install libre==1.0
    $ ./manage.py syncdb --migrate
    $ cat <<'EOF' > settings_local.py
    DEBUG=True
    DEVELOPMENT=True
    ALLOWED_HOSTS = ['*']
    EOF
    $ libre-admin.py runserver --pythonpath=.

Point your browser to 127.0.0.1:8000


.. image:: https://d2weczhvl823v0.cloudfront.net/commonwealth-of-puerto-rico/libre/trend.png
    :target: https://bitdeli.com/free

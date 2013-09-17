![Logo](https://raw.github.com/commonwealth-of-puerto-rico/libre/master/libre/docs/_static/libre_logo.png)


LIBRE
=====

LIBRE = Libre Information Batch Restructuring Engine


The engine that will power the liberation of government data for island of Puerto Rico.


![Logo](https://raw.github.com/commonwealth-of-puerto-rico/libre/master/libre/docs/_static/main_diagram.png)

Turn this:
----------

![Logo](https://raw.github.com/commonwealth-of-puerto-rico/libre/master/libre/docs/_static/before.png)

Into this!
----------

![Logo](https://raw.github.com/commonwealth-of-puerto-rico/libre/master/libre/docs/_static/after.png)

Query your data afterwards too!
-------------------------------

![Logo](https://raw.github.com/commonwealth-of-puerto-rico/libre/master/libre/docs/_static/math_query.png)

INSTALLATION
============

    $ sudo apt-get install libgdal-dev -y
    $ git clone https://github.com/commonwealth-of-puerto-rico/libre.git
    $ cd libre
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r libre/requirements.txt
    $ ./manage.py syncdb --migrate
    $ cat <<'EOF' > settings_local.py
    DEBUG=True
    DEVELOPMENT=True
    EOF
    $ ./manage.py runserver

Point your browser to 127.0.0.1:8000


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/commonwealth-of-puerto-rico/libre/trend.png)](https://bitdeli.com/free "Bitdeli Badge")


========================
LQL LIBRE Query Language
========================

Draft 1.0 of the LIBRE Query Language specification.
LQL is a mixture of SQL, Django's ORM, Python's syntax and geospatial queries constructs using the URL query strings to create a RESTful query language.


Values
======
LQL accepts as input, strings, numbers, lists and geometries. Any value enclosed in double quotes will be interpreted as a string, a value or set of values enclosed in the geometry specifier Point is interpreted as a point geometry, otherwise it will be parsed as a number.
The only exception to this convention are special query directive values, such as those of the **join** directive, which are specified unquoted.
Geospacial geometries also have special attributes which can be accesed and used for filtering, these are: _length, _area and _type

Examples:

A string: ``"hello word"``

A number: ``42``

A list: ``['hello', 'world']`` or ``[1, 2, 3]``

A geometry: ``Point(longitude, laitude)``



Addressing fields
=================
Field names are prepended by a namespace and separated by dots on each new child element.
Example: ``properties.City``

When referencing data from a separate endpoint the namespace will be the name of the endpoint following a dot and the string "data".
Example: ``dataset-25.data.properties.City``

To address a specific element from a collection the Python list addressing notation is used, that is, the index number inside open and closed brackets.
Example: ``[10]``
All indexes are 1 based, meaning that the first element in an endpoint collection is element number 1 and not number 0.

So to address the ``last_name`` property of the **25th** element in an endpoint collection called ``employees`` the syntax would be: ``employees.data[25].last_name``

Filtering
=========
To filter a collection by a field, specify the field name appending a double underscore '__' (or the specified delimiter if overrided) appending again one of the following filters.
Multiple filters can be specified on a single query.

Strings filters
~~~~~~~~~~~~~~~

contains
--------

``contains=<string>``

Return the elements whose field values includes the specified string.

Example: ``first_name__contains="John"``


icontains
---------
``icontains=<string>``

Return the elements whose field values includes the specified string. Matches upper and lower cases.

Example: ``last_name__icontains="smith"``


startswith
----------

``startswith=<string>``

Return the elements whose field values start with the specified string.

Example: ``state__startswith="North"``


istartswith
-----------

``istartswith=<string>``

Return the elements whose field values start with the specified string. Matches upper and lower cases.

Example: ``city__istartswith="John"``


endswith
--------

``endswith=<string>``

Return the elements whose field values end with the specified string.

Example: ``state__startswith="Carolina"``


iendswith
---------

``iendswith=<string>``

Return the elements whose field values end with the specified string. Matches upper and lower cases.

Example: ``company_name__iendswith="corp"``



Number filters
~~~~~~~~~~~~~~


lt
--

``lt=<number>``

Return the elements whose field values are less than the specified number.

Example: ``ytd_sales__lt=1000000``


lte
---

``lte=<number>``

Return the elements whose field values are less than or equal than the specified number.

Example: ``employees_count__lte=1000``


gt
--

``gt=<number>``

Return the elements whose field values are greater than the specified number.

Example: ``spare_rooms__gt=3``


gte
---

``gte=<number>``

Return the elements whose field values are greater than or equal than the specified number.

Example: ``month_sales__gte=200000``


Date filters
~~~~~~~~~~~~

year
----

``year=<number>``

Return the elements whose field values's years are the same as the specified number.

Example: ``crimes__year=2012``


month
-----

``month=<number>``

Return the elements whose field values's months are the same as the specified number.

Example: ``travels__month=3``


range
-----

``range=<list or 2 dates>``

Return the elements whose field values's months are the same as the specified number.

Example: ``purchases__range=["2013-01-01", "2013-03-01"]``


Spatial filters
~~~~~~~~~~~~~~~

has
---

``has=<geometry>``

Return the elements whose interior geometry contains the boundary and interior of the geometry specified, and their boundaries do not touch at all.

Example: ``city__has=Point(-66.16918303705927,18.40250894588894)``


disjoint
--------

``disjoint=<geometry>``

Return the elements whose boundary and interior geometry do not intersect at all with the geometry specified.

Example: ``country__disjoint=Point(-66.16918303705927,18.40250894588894)``


intersects
----------

``intersects=<geometry>``

Return the elements whose boundary and interior geometry intersects the geometry specified in any way.

Example: ``county__intersects=Point(-66.16918303705927,18.40250894588894).buffer(0.5)``


touches
-------

``touches=<geometry>``

Return the elements who have at least one point in common with and whose interiors do not intersect with the geometry specified.

Example: ``river__touches=LineString([-66.16918303705927,18.40250894588894])``


within
------

``within=<geometry>``

boundary and interior intersect only with the interior of the other (not its boundary or exterior).

Return the elements whose boundary and interior intersect only with the interior of the specified geometry (not its boundary or exterior).

Example: ``crime__within=Polygon([[-66.16918303705927,18.40250894588894]])``



Other filters
~~~~~~~~~~~~~


in
--

``in=<list of strings or numbers>``

Return the elements whose field values match one entry in the specified list of strings or numbers.

Example: ``crime_type__in=[1,4,8]``


Directives
~~~~~~~~~~
All directive are prepended by the underscore delimiter '_'.


join
----

``join=<OR | AND>``

When multiple filters are specified per query the results of each filter are ``ANDed`` by default, this directive changes that behaviour so that results are ``ORed`` together.


fields
------

``fields=<list of fields to return>``

Return only the fields specified.

**Note**: Works only for single level element collections (multilevel dot and index notations not yet supported).


Coming soon
===========
* Subqueries
* Sorting
* Grouping
* Sum
* Pagination

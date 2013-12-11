LQL LIBRE Query Language
========================

Version 1.1 of the **LIBRE** Query Language specification.
LQL is a mixture of SQL, Django's ORM, Python's syntax and geospatial queries constructs using the URL query strings to create a RESTful query language.

Changelog
---------
* 2013-12-11 Added support for boolean values
* 2013-12-11 Bump version to 1.1

Values
------
LQL accepts as input:

* numbers - Any value not enclosed in double quotes.
* boolean - Any of the following two values, not enclosed in double quotes: ``True`` or ``False``.
* strings - Any value enclosed in double quotes.
* lists - Any value enclosed with brackets.
* geometries - Any value enclosed in the geometry specifier ``Point(coordinates)``, ``LineStrings(coordinates)``, ``LinearRings(coordinates)``, ``Polygon(exterior[, interiors=None])``, ``MultiPoint(points)``, ``MultiLineString(lines)``, ``MultiPolygon(polygons)`` or ``Geometry(GeoJSON)``.
* dates - Any value enclosed with the ``Date`` specifier.
* time - Any value enclosed with the ``Time`` specifier.
* date & time - Any value enclosed with the ``DateTime`` specifier.
* subqueries - Any string enclosed with the less than (``<``) and more than (``>``) simbols.

The only exception to this convention are special query directive values, such as those of the **join** directive, which are specified unquoted.
Geospacial geometries also have special attributes which can be accesed and used for filtering, these are: _length, _area and _type

Examples:

A string: ``"hello word"``

A number: ``42``

A list: ``['hello', 'world']`` or ``[1, 2, 3]``

A geometry: ``Point(longitude, laitude)``

A date: ``Date(2013-01-01)``

A time: ``Time(10:00pm)`` or ``Time(22:00)``

A date and time: ``DateTime(2013-01-01 1:00pm)``

A subquery: ``births=<census-prmunnet&_aggregate__aggregated_most_births=Max(births)&_json_path=most_births>``

A boolean: ``_format=map_leaflet&_join_type=AND&_renderer__enable_clustering=True``


Filtering
---------
To filter a collection by a field, specify the field name appending a double underscore '__' (or the specified delimiter if overrided) appending again one of the following filters.
Multiple filters can be specified on a single query.

Strings filters
~~~~~~~~~~~~~~~

contains
^^^^^^^^

``contains=<string>``

Return the elements whose field values includes the specified string.

Example: ``first_name__contains="John"``


icontains
^^^^^^^^^
``icontains=<string>``

Return the elements whose field values includes the specified string. Matches upper and lower cases.

Example: ``last_name__icontains="smith"``


startswith
^^^^^^^^^^

``startswith=<string>``

Return the elements whose field values start with the specified string.

Example: ``state__startswith="North"``


istartswith
^^^^^^^^^^^

``istartswith=<string>``

Return the elements whose field values start with the specified string. Matches upper and lower cases.

Example: ``city__istartswith="John"``


endswith
^^^^^^^^

``endswith=<string>``

Return the elements whose field values end with the specified string.

Example: ``state__startswith="Carolina"``


iendswith
^^^^^^^^^

``iendswith=<string>``

Return the elements whose field values end with the specified string. Matches upper and lower cases.

Example: ``company_name__iendswith="corp"``


iequals
^^^^^^^

``iequals=<string>``

Return the elements whose field values match the specified string, matches upper and lower cases.

Example: ``full_name__iequals="john carter"``


Number filters
~~~~~~~~~~~~~~


lt
^^

``lt=<number>``

Return the elements whose field values are less than the specified number.

Example: ``ytd_sales__lt=1000000``


lte
^^^

``lte=<number>``

Return the elements whose field values are less than or equal than the specified number.

Example: ``employees_count__lte=1000``


gt
^^

``gt=<number>``

Return the elements whose field values are greater than the specified number.

Example: ``spare_rooms__gt=3``


gte
^^^

``gte=<number>``

Return the elements whose field values are greater than or equal than the specified number.

Example: ``month_sales__gte=200000``


Spatial filters
~~~~~~~~~~~~~~~

has
^^^

``has=<geometry>``

Return the elements whose interior geometry contains the boundary and interior of the geometry specified, and their boundaries do not touch at all.

Example: ``city__has=Point(-66.16918303705927,18.40250894588894)``


disjoint
^^^^^^^^

``disjoint=<geometry>``

Return the elements whose boundary and interior geometry do not intersect at all with the geometry specified.

Example: ``country__disjoint=Point(-66.16918303705927,18.40250894588894)``


intersects
^^^^^^^^^^

``intersects=<geometry>``

Return the elements whose boundary and interior geometry intersects the geometry specified in any way.

Example: ``county__intersects=Point(-66.16918303705927,18.40250894588894).buffer(0.5)``


touches
^^^^^^^

``touches=<geometry>``

Return the elements who have at least one point in common with and whose interiors do not intersect with the geometry specified.

Example: ``river__touches=LineString([-66.16918303705927,18.40250894588894])``


within
^^^^^^

``within=<geometry>``

boundary and interior intersect only with the interior of the other (not its boundary or exterior).

Return the elements whose boundary and interior intersect only with the interior of the specified geometry (not its boundary or exterior).

Example: ``crime__within=Polygon([[-66.16918303705927,18.40250894588894]])``



Other filters
~~~~~~~~~~~~~


in
^^

``in=<list of strings or numbers>``

Return the elements whose field values match one entry in the specified list of strings or numbers.

Example: ``crime_type_id__in=[1,4,8]``


range
^^^^^

``range=<list of two dates, two times, two date and times, two numbers or two strings>``

Return the elements whose field values's months are within the the specified values.

Example: ``purchases_date__range=[Date(2013-01-01), Date(2013-03-01)]``


Negation
~~~~~~~~

All filter can be negated by adding ``__not`` before the filter name, this will cause their logic to be inverted.

Return the elements whose field values do not match one entry in the specified list of strings or numbers.

Example: ``city_id__not_in=[41,3,142]``


Directives
~~~~~~~~~~
All directive are prepended by the underscore delimiter '_'.


join
^^^^

``_join=<OR | AND>``

When multiple filters are specified per query the results of each filter are ``ANDed`` by default, this directive changes that behaviour so that results are ``ORed`` together.


json_path
^^^^^^^^^

Reduce the result set using JSON Path

``_json_path=JSON Path syntax``

JSON Path syntax: https://github.com/kennknowles/python-jsonpath-rw


renderer
^^^^^^^^

Pass renderer specific key value pairs. The key and values are dependent on the renderer being used.

Values for the map_leaflet renderer:

* zoom_level
* longitude
* latitude
* geometry

Example: ``_renderer__zoom_level=13&_renderer__longitude=-66.116079&_renderer__latitude=18.464386``


Aggregation
~~~~~~~~~~~
Aggregates asssist with the summarization of data.

Example: ``api/sources/crimes/data/?properties.date__month=2&geometry__intersects=Point(-67,18.3).buffer(0.05)&_aggregate__total=Count(*)&_format=json``

Return a count of all crimes committed in February and which occurred within the selected geographical area.


Count
^^^^^

Return the count of rows or occurences of a value in the specified list, returned as an alias.

``Count(<field to count> or <*>)``

Example: ``_aggregate__total=Count(*)``


Sum
^^^

Return the sum of the values of the specified field.

``Sum(<field to sum>)``

Example: ``_aggregate__total_score=Sum(score)``


Min
^^^

Return the minimum value of the specified field in the elements.

``Min(<field>)``

Example: ``_aggregate__least_deaths=Min(deaths)``


Max
^^^

Return the maximun value of the specified field in the elements.

``Max(<field>)``

Example: ``_aggregate__most_births=Max(births)``


Average
^^^^^^^

Return the average value of the specified field in the elements.

``Average(<field>)``

Example: ``_aggregate__point_average=Average(points)``


Grouping
~~~~~~~~

``_group_by=<comma delimited list of fields by which to group data>``

Example: ``_group_by=city,region``


Transformations
~~~~~~~~~~~~~~~

_as_dict_list
^^^^^^^^^^^^^

Return the current values as a list of key value dictionaries


_as_nested_list
^^^^^^^^^^^^^^^

Return the current values as a nested list (list of lists)



Coming soon
-----------
* Sorting
* Pagination

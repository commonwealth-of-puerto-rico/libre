========================
LQL LIBRE Query Language
========================

Draft 1.0 of the LIBRE Query Language specification.
LQL is a mixture of SQL, Django's ORM and geospatial queries constructs using the URL Query string to create a RESTful query language.


Values
======
LQL accepts as input, strings and numbers. Any value enclosed in double quotes will be interpreted as a string, otherwise it will be parsed as a number.
The only exception to this convention are special query directive values, such as those of the **join** directive, which are specified unquoted.


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

contains=<string>
-----------------
Return the elements whose field values includes the specified string.

Example: ``first_name__contains="John"``


icontains=<string>
------------------
Return the elements whose field values includes the specified string. Matches upper and lower cases.

Example: ``last_name__icontains="smith"``


startswith=<string>
-------------------
Return the elements whose field values start with the specified string.

Example: ``state__startswith="North"``


istartswith=<string>
--------------------
Return the elements whose field values start with the specified string. Matches upper and lower cases.

Example: ``city__istartswith="John"``


endswith=<string>
-----------------
Return the elements whose field values end with the specified string.

Example: ``state__startswith="Carolina"``


iendswith=<string>
------------------
Return the elements whose field values end with the specified string. Matches upper and lower cases.

Example: ``company_name__iendswith="corp"``


in=<list of strings or numbers>
-------------------------------
Return the elements whose field values match one entry in the specified list of strings or numbers.

Example: ``crime_type__in=1,4,8``


lt=<number>
-----------
Return the elements whose field values are less than the specified number.

Example: ``ytd_sales__lt=1000000``


lte=<number>
------------
Return the elements whose field values are less than or equal than the specified number.

Example: ``employees_count__lte=1000``


gt=<number>
-----------
Return the elements whose field values are greater than the specified number.

Example: ``spare_rooms__gt=3``


gte=<number>
------------
Return the elements whose field values are greater than or equal than the specified number.

Example: ``month_sales__gte=200000``


Directives
==========

join=<OR | AND>
---------------
When multiple filters are specified per query the results of each filter are ``ANDed`` by default, this directive changes that behaviour so that results are ``ORed`` together.

Coming soon
===========
* Subqueries
* Sorting
* Geospatial filtering

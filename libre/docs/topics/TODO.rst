PENDING
-------
* Filebased sources

  * Add compressed file support
  * Skip blank lines?
  * Switch from column widths to column ranges
  * Toggable auto update via inotify, polling or python-watchdog
  * Add internal support for open ranges for rows "10-"
  * Migrate Spreadsheet regex import and skip solution to other filebased sources
  * Add row number exclusion support during import

* Database sources

  * Add DB Source support

    * Pony ORM


* Documentation

  * Release notes
  * Getting started
  * Add better sample source files

    * http://www.census.gov/population/estimates/puerto-rico/prmunnet.txt

  * Examples using existing public data


* General

  * Parse values

    * Parse dates (using dateutil) - DONE
    * True values, False values

  * Add Relationship support
  * Specify number of versions to keep, deleting old ones
  * Add instructions to sources, per source type
  * Add row number exclusion support during import
  * Stored JSON data index support
  * JSON source descriptor export and import
  * Rename timestamp to version and allow user defined version strings
  * Data translation
  * Remap JSON names


* Geographical sources

  * <No task remains>


* Job processing

  * Add Celery support or subprocess


* LQL

  * LQL based pagination (size and page number) (Andres Colón)
  * Expand the _fields directive to support dot and index notations
  * Sorting

    * _order=<field name>,<field name>
    * Ascending (field name)
    * Descending (-field name)

  * Subqueries
  * Aggregation

    * Grouping
    * Sum

  * Pagination
  * Limiting

    * _limit=<soft limit of elements>

  * Skipping results

    * _skip=<number of elements>

  * Joins between datasets

    * _join=<data set name>,<join type>,<current set field>__<foreign set field>,<current set field>__<foreign set field>


* Output

  * Add support for generating output formats other than JSON

    * Shapefiles
    * GeoJSON - DONE
    * CSV
    * Excel
    * XML - DONE
    * NIEM
    * Fixed width

* Web services sources

  * Add caching support to WS Sources

    * TTL support

* Unsorted

  * Improve output logging - INPROGRES
  * Empty but valid queries should return HTTP404 or HTTP200 with '{"status": "Not found"}'
  * Show required argument for WS
  * Interpret WS arguments
  * Result count
  * Fix upload_to
  * Allow skiping/importing rows that match a regex per field
  * Calculate geometries area, size, lenghts in pin template
  * Delete stored source files when a source is deleted
  * Delete stored source files when a new file is uploaded
  * Fix JsonField not returning dates or times only datetimes
  * Return a {'status': } dictionary with error message
  * Fix XML renderer
  * Move _renderer and _fields parsing to allow being parsed on get_one method
  * Optimize AND type join
  * Use islice
  * Dataset browser

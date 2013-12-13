.. :changelog:

Release History
---------------

1.1.0 (2013-12-13)
++++++++++++++++++

- New frontend for non technical users, dataset browser, dataset showcase
- Support for boolean values to LQL
- Support for clustering map features
- Fix handling of dates as key when using _as_dict_list
- Increased required version of Fiona to 1.0.2
- Updated Leaflet version used to 0.7
- Added boolean values support to LQL
- Added Leaflet marker clustering plugin support
- Optimize Leaflet's marker's use by encode markers as base64 PNG images and embedding them in the renderer's HTML output
- Menu reorganization and cleanup
- Add support to add an image to a source dataset
- Documentation updates
- Update required version of djangorestframework
- Origins module now copies local files in chunks and streams remote HTTP files improving memory usage during imports


1.0.0 (2013-11-19)
++++++++++++++++++

- Accepted: Added Command Line Interface (CLI) for update_admin_user (#10)
- Accepted: Added Pre-Installation Steps necessary to run on OSX (#9)
- Closed: Added missing docutils requirement (#8)
- Closed: Missing dependency on requirements (#4)
- Closed: inotify is not available on macosx-10.8-intel (#2)
- Accepted: Add slugify method for automatic slugs (#1)
- Fix CSV source issues with CSV file encodings (utf-8, iso-8859-1) by allowing users to specify the file encoding.
- Increased required version to Django to 1.5.5
- Add scheduling support to Sources
- Reduce the data source origin data check resolution to 45 seconds
- Fail gracefully when GIS features have no bounds
- Add new PythonScript origin


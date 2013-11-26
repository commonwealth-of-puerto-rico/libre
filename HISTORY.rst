.. :changelog:

Release History
---------------


1.0.0 (2013-09-19)
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

# ArcGIS Utilities

🚧 Work in progress 🚧

Utilities for working with ArcGIS files.

## Design philosophy

* Only use `arcpy` when there is no other alternative. Importing the `arcpy` module takes several seconds, so its use should be avoided if there are any other alternatives. Many ArcGIS file binary file formats are actually just ZIP or 7-Zip archive files with specific files in them. Because of this, these files can be examined without using `arcpy`.

## Tools

These script files contain more detailed documentation in their docstrings. You can also run the tools and pass them the `-h` or `--help` option to get help.

### dump_arcgis

Dumps ArcGIS binary files to a textual representation whenever possible. This provides more useful information when using diff tools, such as when git compares two versions of files. Instead of just telling you that "binary files are different", you can get a better idea of what was changed.

### create_gp_package_folders.py

Creates folder structure recommended by Esri when creating Geoprocessing tool package.

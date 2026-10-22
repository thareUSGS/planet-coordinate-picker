# Planet Coordinate Picker

A QGIS plug-in for live latitude/longitude readout and click-to-capture using the map canvas CRS's associated geographic CRS. It supports planetary coordinate systems when QGIS provides a valid associated geographic CRS, and offers planetographic or planetocentric latitude for ellipsoidal bodies.

See the [plug-in guide](coordinate_picker_plugin/README.md) for installation and usage, the [changelog](coordinate_picker_plugin/CHANGELOG.md) for changes, and the [GPL-3.0-only license](coordinate_picker_plugin/LICENSE) for licensing and attribution.

The plug-in is distributed from this repository as a ZIP and is not listed in the QGIS Plugin Repository. Follow the installation instructions in the plug-in guide.

## Development

Run the longitude and latitude conversion tests with Python:

```powershell
python -m unittest discover -s tests -v
```

The installable QGIS plug-in package is in `coordinate_picker_plugin/`.

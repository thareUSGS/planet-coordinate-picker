# Changelog

Notable changes to Planet Coordinate Picker are documented here.

This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

## [0.3.1] - 2026-10-22

### Fixed

- Fix a syntax error in copied-coordinate text formatting that prevented the plug-in from loading.

## [0.3.0] - 2026-10-22

### Changed

- Remove planetocentric/planetographic latitude selection and conversion. Latitude is now reported directly from the associated geographic CRS.
- Remove ellipsoid validation used only for latitude convention selection.

## [0.2.2] - 2026-10-22

### Changed

- Use NumPy tangent-based formulas for planetocentric-to-planetographic and inverse latitude conversion.
- Add original plug-in author attribution to the metadata.

## [0.2.1] - 2026-10-22

### Fixed

- Use planetocentric latitude as the default and apply oc2og only to latitude when planetographic display is selected.

## [0.2.0] - 2026-10-22

### Added

- Add planetographic/planetocentric latitude selection for ellipsoidal bodies; disable the option for spherical bodies and refresh availability when the project CRS changes.
- Resolve latitude and longitude using the map canvas CRS's associated geographic CRS instead of assuming WGS 84, supporting planetary coordinate systems where QGIS provides a geographic CRS.
- Make longitude range (-180 to 180 or 0 to 360) and positive direction (east or west) independent options.
- Publish a QGIS installation ZIP named with the plug-in name and release tag (for example, `PlanetCoordinatePicker-v0.2.0.zip`) when a `v*` tag is pushed.

### Changed

- Improve source formatting and add concise code documentation.

### Fixed

- Report an explicit error when the map CRS has no valid associated geographic CRS.

## [0.1.0] - 2026-10-22

### Added

- Live latitude and longitude readout from the map cursor.
- Click-to-capture coordinates with a table, clipboard copy, and CSV export.
- Configurable decimal precision and signed or 0-to-360 longitude display.
- GPL-3.0-only licensing and attribution to the Coordinate Picker reference project.

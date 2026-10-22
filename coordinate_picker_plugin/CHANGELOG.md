# Changelog

Notable changes to Planet Coordinate Picker are documented here.

This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

## [Unreleased]

## [0.2.0] - 2026-10-22

### Added

- Add planetographic/planetocentric latitude selection for ellipsoidal bodies; disable the option for spherical bodies and refresh availability when the project CRS changes.
- Resolve latitude and longitude using the map canvas CRS's associated geographic CRS instead of assuming WGS 84, supporting planetary coordinate systems where QGIS provides a geographic CRS.
- Make longitude range (-180 to 180 or 0 to 360) and positive direction (east or west) independent options.
- Publish versioned QGIS installation ZIPs as GitHub Release assets when a `v*` tag is pushed.

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

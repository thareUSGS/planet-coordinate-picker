# Planet Coordinate Picker

Planet Coordinate Picker displays latitude and longitude while you move the cursor over the map. It transforms from the map canvas CRS to that CRS's associated geographic CRS, rather than assuming Earth/WGS 84. This supports planetary CRSs when QGIS identifies their associated geographic CRS. If no valid geographic CRS is associated, the picker reports the problem instead of displaying misleading coordinates. Start picking to capture clicked points in a table, then copy selected/all rows or export them as CSV.

## Coordinate display

- **Longitude range** is selected independently as either **-180 to 180** or **0 to 360**.
- **Positive direction** is selected independently as either **East** or **West**. The other direction is negative in the -180 to 180 range; in the 0 to 360 range, values wrap around the full circle.

Latitude is reported directly from the map CRS's associated geographic CRS. Planetocentric/planetographic selection and ellipsoid-based latitude conversion are not available.

Captured coordinates are kept internally in the associated geographic CRS and are reformatted when you change the longitude range, positive direction, or decimal precision.

## Install

Planet Coordinate Picker is distributed from this GitHub repository and is not listed in the QGIS Plugin Repository.

1. Download `PlanetCoordinatePicker-v<version>.zip` from the [latest GitHub release](https://github.com/thareUSGS/planet-coordinate-picker/releases/latest), replacing `<version>` with the release version (for example, `0.3.0`).
2. In QGIS, choose **Plugins > Manage and Install Plugins > Install from ZIP**, select the downloaded ZIP, and confirm installation.

The release ZIP contains the `coordinate_picker_plugin` folder with `metadata.txt` inside it.

Do not search the QGIS Plugin Repository for this plug-in.

## Use

1. Open **Planet Coordinate Picker** from the Plugins menu or toolbar.
2. Set the longitude range, positive direction, and decimal precision.
3. Click **Start picking** and move the cursor over the map for a live readout.
4. Left-click on the map to add coordinates to the table. Click **Stop picking** to return to the previous map tool.
5. Select table rows and click **Copy selected**, use **Copy all**, or export the table as CSV.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history and unreleased changes.

Author: Copilot A.I. (as defined by Trent Hare)

## License and attribution

This plug-in is distributed under the GNU General Public License, version 3.0 only; see [LICENSE](LICENSE). Its workflow was informed by [Coordinate Picker](https://github.com/mellow2334/coordinate-picker) by Shyam Mishra, which is also licensed under GPL-3.0. This implementation was written independently and does not copy source files from the original project.

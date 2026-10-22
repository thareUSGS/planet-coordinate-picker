import math
import os.path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    QgsCoordinateTransform,
    QgsCsException,
    QgsEllipsoidUtils,
    QgsProject,
)

from .dock_widget import CoordinatePickerDock
from .map_tool import CoordinateMapTool


class CoordinatePicker:
    """QGIS plug-in entry point and controller for the map tool and dock."""

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.dock = None
        self.map_tool = None
        self._previous_map_tool = None
        self._picking = False

    def initGui(self):
        """Create the toolbar action, dock, and map interaction tool."""
        self.action = QAction(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "icons",
                    "planet_coordinate_picker.svg",
                )
            ),
            "Planet Coordinate Picker",
            self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Planet Coordinate Picker", self.action)

        self.dock = CoordinatePickerDock(self.iface.mainWindow())
        self._project = QgsProject.instance()
        self._project.crsChanged.connect(self._refresh_coordinate_crs)
        self._refresh_coordinate_crs()
        self.map_tool = CoordinateMapTool(self.canvas)
        self.map_tool.mouseMoved.connect(self._update_live_coordinate)
        self.map_tool.pointCaptured.connect(self._capture_coordinate)
        self.dock.pickingToggled.connect(self._set_picking)
        self.dock.visibilityChanged.connect(self._dock_visibility_changed)
        dock_area = getattr(Qt, "RightDockWidgetArea", None)
        if dock_area is None:
            dock_area = Qt.DockWidgetArea.RightDockWidgetArea
        self.iface.addDockWidget(dock_area, self.dock)
        self.dock.hide()
        self.canvas.mapToolSet.connect(self._map_tool_changed)

    def unload(self):
        """Restore the previous map tool and release plug-in UI resources."""
        self._set_picking(False)
        self.canvas.mapToolSet.disconnect(self._map_tool_changed)
        self._project.crsChanged.disconnect(self._refresh_coordinate_crs)
        if self.action is not None:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("&Planet Coordinate Picker", self.action)
            self.action = None
        if self.dock is not None:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None
        if self.map_tool is not None:
            self.map_tool.deleteLater()
            self.map_tool = None

    def run(self):
        """Show the coordinate picker dock."""
        if self.dock is None:
            return
        self.dock.show()
        self.dock.raise_()
        self.dock.activateWindow()

    def _set_picking(self, active):
        """Activate the picker, restoring the prior tool when it stops."""
        if self.dock is None or self.map_tool is None:
            return
        if active and not self._picking:
            self._previous_map_tool = self.canvas.mapTool()
            self._picking = True
            self.canvas.setMapTool(self.map_tool)
            self.dock.set_picking(True)
            self.dock.set_status(
                "Move over the map to preview coordinates; left-click to capture."
            )
        elif not active and self._picking:
            self._picking = False
            self.dock.set_picking(False)
            if self.canvas.mapTool() is self.map_tool:
                if self._previous_map_tool is not None:
                    self.canvas.setMapTool(self._previous_map_tool)
                else:
                    self.canvas.unsetMapTool(self.map_tool)
            self._previous_map_tool = None

    def _dock_visibility_changed(self, visible):
        """Stop picking when the user closes or hides the dock."""
        if not visible and self._picking:
            self._set_picking(False)

    def _map_tool_changed(self, new_tool, _old_tool):
        """Keep the button state in sync if the user switches map tools."""
        if self._picking and new_tool is not self.map_tool:
            self._picking = False
            self._previous_map_tool = None
            self.dock.set_picking(False)
            self.dock.set_status(
                "Picking stopped because another map tool was activated."
            )

    def _refresh_coordinate_crs(self, *_args):
        """Update the latitude selector when the project's body CRS changes."""
        if self.dock is None:
            return
        try:
            target_crs, semi_major, semi_minor = (
                self._geographic_crs_details()
            )
        except (QgsCsException, ValueError) as error:
            message = "Could not determine the geographic CRS: {}".format(error)
            self.dock.set_geographic_crs_error(message)
            self.dock.set_status(message)
            return
        self.dock.set_coordinate_crs(
            target_crs.description(),
            semi_major,
            semi_minor,
        )

    def _geographic_crs_details(self):
        """Return the geographic CRS and its ellipsoid axes."""
        source_crs = self.canvas.mapSettings().destinationCrs()
        if not source_crs.isValid():
            raise ValueError("The map canvas CRS is not valid.")
        # Use the CRS's own geographic base; never assume the data is Earth.
        target_crs = source_crs.toGeographicCrs()
        if not target_crs.isValid():
            raise ValueError(
                "The map canvas CRS has no associated geographic CRS. "
                "Choose a CRS with a valid geographic base."
            )
        ellipsoid = QgsEllipsoidUtils.ellipsoidParameters(
            target_crs.ellipsoidAcronym()
        )
        if not ellipsoid.valid:
            raise ValueError(
                "The geographic CRS does not define a valid ellipsoid."
            )
        semi_major = ellipsoid.semiMajor
        semi_minor = ellipsoid.semiMinor
        if (
            not math.isfinite(semi_major)
            or not math.isfinite(semi_minor)
            or semi_major <= 0
            or semi_minor <= 0
        ):
            raise ValueError("The geographic CRS has invalid ellipsoid axes.")
        return target_crs, semi_major, semi_minor

    def _transform_to_geographic(self, point):
        """Transform a canvas point to its CRS's associated geographic CRS."""
        project = self._project
        source_crs = self.canvas.mapSettings().destinationCrs()
        target_crs, semi_major, semi_minor = self._geographic_crs_details()
        transform = QgsCoordinateTransform(
            source_crs,
            target_crs,
            project,
        )
        transformed = transform.transform(point)
        latitude = transformed.y()
        longitude = transformed.x()
        if not math.isfinite(latitude) or not math.isfinite(longitude):
            raise ValueError("The transformed coordinates are not finite.")
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("The transformed latitude is outside -90 to 90.")
        return (
            latitude,
            longitude,
            target_crs.description(),
            semi_major,
            semi_minor,
        )

    def _update_live_coordinate(self, point):
        """Update the readout as the cursor moves over the map."""
        if self.dock is None:
            return
        try:
            (
                latitude,
                longitude,
                crs_description,
                semi_major,
                semi_minor,
            ) = (
                self._transform_to_geographic(point)
            )
        except (QgsCsException, ValueError) as error:
            self.dock.set_status(
                "Could not transform cursor coordinates: {}".format(error)
            )
            return
        self.dock.set_coordinate_crs(crs_description, semi_major, semi_minor)
        self.dock.update_live_coordinate(latitude, longitude)

    def _capture_coordinate(self, point):
        """Transform a clicked point and add it to the captured-coordinate table."""
        if self.dock is None:
            return
        try:
            (
                latitude,
                longitude,
                crs_description,
                semi_major,
                semi_minor,
            ) = (
                self._transform_to_geographic(point)
            )
        except (QgsCsException, ValueError) as error:
            self.dock.set_status("Could not capture coordinates: {}".format(error))
            return
        self.dock.set_coordinate_crs(crs_description, semi_major, semi_minor)
        self.dock.add_coordinate(latitude, longitude)

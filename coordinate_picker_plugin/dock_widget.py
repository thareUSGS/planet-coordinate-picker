import csv

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .coordinates import (
    EAST_POSITIVE,
    PLANETOCENTRIC,
    PLANETOGRAPHIC,
    RANGE_360,
    RANGE_SIGNED,
    WEST_POSITIVE,
    convert_latitude,
    normalize_longitude,
)


class CoordinatePickerDock(QDockWidget):
    """Dock UI for live coordinates, captured points, and export controls."""

    pickingToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__("Planet Coordinate Picker", parent)
        self._coordinates = []
        self._last_coordinate = None
        self._ellipsoid_axes = (1.0, 1.0)
        self._build_ui()
        self.latitude_type.setEnabled(False)

    def _build_ui(self):
        """Build the dock controls and captured-coordinate table."""
        content = QWidget(self)
        layout = QVBoxLayout(content)

        self.crs_label = QLabel(
            "Latitude and longitude use the project CRS's associated "
            "geographic CRS."
        )
        self.crs_label.setWordWrap(True)
        layout.addWidget(self.crs_label)

        options = QHBoxLayout()
        options.addWidget(QLabel("Longitude range:"))
        self.longitude_range = QComboBox()
        self.longitude_range.addItem("-180 to 180", RANGE_SIGNED)
        self.longitude_range.addItem("0 to 360", RANGE_360)
        self.longitude_range.currentIndexChanged.connect(self._refresh_display)
        options.addWidget(self.longitude_range)
        options.addWidget(QLabel("Positive direction:"))
        self.longitude_direction = QComboBox()
        self.longitude_direction.addItem("East", EAST_POSITIVE)
        self.longitude_direction.addItem("West", WEST_POSITIVE)
        self.longitude_direction.currentIndexChanged.connect(self._refresh_display)
        options.addWidget(self.longitude_direction)
        options.addWidget(QLabel("Latitude type:"))
        self.latitude_type = QComboBox()
        self.latitude_type.addItem("Planetographic", PLANETOGRAPHIC)
        self.latitude_type.addItem("Planetocentric", PLANETOCENTRIC)
        self.latitude_type.setToolTip(
            "Planetocentric latitude is available only for ellipsoidal bodies."
        )
        self.latitude_type.currentIndexChanged.connect(self._refresh_display)
        options.addWidget(self.latitude_type)
        options.addWidget(QLabel("Decimal places:"))
        self.precision = QSpinBox()
        self.precision.setRange(0, 12)
        self.precision.setValue(6)
        self.precision.valueChanged.connect(self._refresh_display)
        options.addWidget(self.precision)
        layout.addLayout(options)

        self.live_readout = QLabel(
            "Start picking to see the live cursor coordinates."
        )
        self.live_readout.setWordWrap(True)
        layout.addWidget(self.live_readout)

        self.pick_button = QPushButton("Start picking")
        self.pick_button.setCheckable(True)
        self.pick_button.toggled.connect(self.pickingToggled)
        layout.addWidget(self.pick_button)

        self.table = QTableWidget(0, 3, content)
        self.table.setHorizontalHeaderLabels(["ID", "Latitude", "Longitude"])
        self.table.setSelectionBehavior(
            _enum(QAbstractItemView, "SelectionBehavior", "SelectRows")
        )
        self.table.setSelectionMode(
            _enum(QAbstractItemView, "SelectionMode", "ExtendedSelection")
        )
        self.table.setEditTriggers(
            _enum(QAbstractItemView, "EditTrigger", "NoEditTriggers")
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.copy_selected_button = QPushButton("Copy selected")
        self.copy_selected_button.clicked.connect(self.copy_selected)
        buttons.addWidget(self.copy_selected_button)
        self.copy_all_button = QPushButton("Copy all")
        self.copy_all_button.clicked.connect(self.copy_all)
        buttons.addWidget(self.copy_all_button)
        self.export_button = QPushButton("Export CSV...")
        self.export_button.clicked.connect(self.export_csv)
        buttons.addWidget(self.export_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_coordinates)
        buttons.addWidget(self.clear_button)
        layout.addLayout(buttons)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.setWidget(content)

    def set_picking(self, active):
        """Synchronize the checkable button with the map tool state."""
        self.pick_button.blockSignals(True)
        self.pick_button.setChecked(active)
        self.pick_button.setText("Stop picking" if active else "Start picking")
        self.pick_button.blockSignals(False)
        if not active:
            self.live_readout.setText(
                "Start picking to see the live cursor coordinates."
            )

    def set_status(self, message):
        """Show a status or error message below the table."""
        self.status.setText(message)

    def set_coordinate_crs(self, description, semi_major, semi_minor):
        """Show the geographic CRS used for the displayed coordinates."""
        self._ellipsoid_axes = (semi_major, semi_minor)
        self.latitude_type.setEnabled(semi_major != semi_minor)
        self.crs_label.setText(
            "Latitude and longitude CRS: {}".format(description)
        )

    def set_geographic_crs_error(self, message):
        """Disable latitude-type selection when the body CRS is unavailable."""
        self.latitude_type.setEnabled(False)
        self.crs_label.setText(message)

    def update_live_coordinate(self, latitude, longitude):
        """Store raw geographic coordinates and refresh the live readout."""
        semi_major, semi_minor = self._ellipsoid_axes
        self._last_coordinate = (
            latitude,
            longitude,
            semi_major,
            semi_minor,
        )
        self._refresh_live_readout()

    def add_coordinate(self, latitude, longitude):
        """Append a point and refresh the table."""
        semi_major, semi_minor = self._ellipsoid_axes
        self._coordinates.append(
            (latitude, longitude, semi_major, semi_minor)
        )
        self._refresh_table()
        self.status.setText("Captured point {}.".format(len(self._coordinates)))

    def clear_coordinates(self):
        """Remove all captured coordinates."""
        self._coordinates.clear()
        self._refresh_table()
        self.status.setText("Captured points cleared.")

    def _longitude(self, longitude):
        """Format longitude according to the independent range and direction."""
        return normalize_longitude(
            longitude,
            self.longitude_range.currentData(),
            self.longitude_direction.currentData(),
        )

    def _format(self, value):
        """Format a coordinate using the selected decimal precision."""
        return "{:.{}f}".format(value, self.precision.value())

    def _latitude(self, latitude, semi_major, semi_minor):
        """Apply the selected latitude convention for a point's body."""
        return convert_latitude(
            latitude,
            self.latitude_type.currentData(),
            semi_major,
            semi_minor,
        )

    def _refresh_display(self, *_args):
        """Reformat the readout and table after a display option changes."""
        self._refresh_live_readout()
        self._refresh_table()

    def _refresh_live_readout(self):
        """Update the cursor readout using the currently selected options."""
        if self._last_coordinate is None:
            return
        latitude, longitude, semi_major, semi_minor = self._last_coordinate
        try:
            latitude = self._latitude(latitude, semi_major, semi_minor)
            longitude = self._longitude(longitude)
        except ValueError as error:
            self.live_readout.setText(str(error))
            return
        self.live_readout.setText(
            "Latitude: {}    Longitude: {}".format(
                self._format(latitude), self._format(longitude)
            )
        )

    def _refresh_table(self):
        """Rebuild the table from raw coordinates and current display options."""
        self.table.setHorizontalHeaderLabels(
            ["ID", self._latitude_header(), "Longitude"]
        )
        self.table.setRowCount(len(self._coordinates))
        for row, (latitude, longitude, semi_major, semi_minor) in enumerate(
            self._coordinates
        ):
            values = (
                str(row + 1),
                self._format(self._latitude(latitude, semi_major, semi_minor)),
                self._format(self._longitude(longitude)),
            )
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()

    def _rows_to_text(self, rows):
        """Return selected rows as tab-separated text for spreadsheet pasting."""
        lines = ["ID\t{}\tLongitude".format(self._latitude_header())]
        for row in rows:
            latitude, longitude, semi_major, semi_minor = self._coordinates[row]
            lines.append(
                "{}\t{}\t{}".format(
                    row + 1,
                    self._format(
                        self._latitude(latitude, semi_major, semi_minor)
                    ),
                    self._format(self._longitude(longitude)),
                )
            )
        return "\n".join(lines)

    def copy_selected(self):
        """Copy selected table rows to the clipboard."""
        rows = sorted({item.row() for item in self.table.selectedItems()})
        if not rows:
            self.status.setText("Select one or more captured points to copy.")
            return
        QApplication.clipboard().setText(self._rows_to_text(rows))
        self.status.setText("Copied {} selected point(s).".format(len(rows)))

    def copy_all(self):
        """Copy all captured rows to the clipboard."""
        if not self._coordinates:
            self.status.setText("There are no captured points to copy.")
            return
        QApplication.clipboard().setText(
            self._rows_to_text(range(len(self._coordinates)))
        )
        self.status.setText("Copied all {} point(s).".format(len(self._coordinates)))

    def export_csv(self):
        """Export all captured points using the current display settings."""
        if not self._coordinates:
            self.status.setText("There are no captured points to export.")
            return
        filename, _filter = QFileDialog.getSaveFileName(
            self, "Export coordinates", "", "CSV files (*.csv)"
        )
        if not filename:
            return
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as output:
                writer = csv.writer(output)
                writer.writerow(["ID", self._latitude_header(), "Longitude"])
                for row, (latitude, longitude, semi_major, semi_minor) in enumerate(
                    self._coordinates, start=1
                ):
                    writer.writerow(
                        [
                            row,
                            self._format(
                                self._latitude(latitude, semi_major, semi_minor)
                            ),
                            self._format(self._longitude(longitude)),
                        ]
                    )
        except OSError as error:
            QMessageBox.critical(self, "Planet Coordinate Picker", str(error))
            self.status.setText("Could not write the CSV file.")
            return
        self.status.setText("Exported {} point(s).".format(len(self._coordinates)))

    def _latitude_header(self):
        """Name the latitude convention used by the current display."""
        return "Latitude ({})".format(
            self.latitude_type.currentText().lower()
        )


def _enum(container, group_name, value_name):
    """Resolve a Qt enum across the Qt 5 and Qt 6 APIs."""
    value = getattr(container, value_name, None)
    if value is not None:
        return value
    return getattr(getattr(container, group_name), value_name)

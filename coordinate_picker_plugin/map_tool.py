from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QCursor
from qgis.gui import QgsMapTool


class CoordinateMapTool(QgsMapTool):
    """Emit map coordinates for cursor movement and left-clicks."""

    mouseMoved = pyqtSignal(object)
    pointCaptured = pyqtSignal(object)

    def __init__(self, canvas):
        super().__init__(canvas)
        cursor_shape = getattr(Qt, "CrossCursor", None)
        if cursor_shape is None:
            cursor_shape = Qt.CursorShape.CrossCursor
        self.setCursor(QCursor(cursor_shape))

    def canvasMoveEvent(self, event):
        """Publish the map coordinate under the cursor."""
        self.mouseMoved.emit(self.toMapCoordinates(event.pos()))

    def canvasReleaseEvent(self, event):
        """Capture a point only when the user releases the left mouse button."""
        left_button = getattr(Qt, "LeftButton", None)
        if left_button is None:
            left_button = Qt.MouseButton.LeftButton
        if event.button() == left_button:
            self.pointCaptured.emit(self.toMapCoordinates(event.pos()))

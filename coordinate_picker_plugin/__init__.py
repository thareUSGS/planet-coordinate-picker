def classFactory(iface):
    """Create the plug-in instance expected by QGIS."""
    from .coordinate_picker import CoordinatePicker

    return CoordinatePicker(iface)

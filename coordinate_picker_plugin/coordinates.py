import math


RANGE_SIGNED = "signed"
RANGE_360 = "0_360"
EAST_POSITIVE = "east_positive"
WEST_POSITIVE = "west_positive"


def normalize_longitude(longitude, longitude_range, direction):
    """Apply a positive direction, then wrap longitude to the chosen range."""
    if not math.isfinite(longitude):
        raise ValueError("Longitude must be a finite number.")

    if direction == EAST_POSITIVE:
        directed_longitude = longitude
    elif direction == WEST_POSITIVE:
        directed_longitude = -longitude
    else:
        raise ValueError("Unknown longitude direction.")

    if longitude_range == RANGE_360:
        normalized = directed_longitude % 360.0
        return 0.0 if normalized == 0 else normalized
    if longitude_range == RANGE_SIGNED:
        normalized = directed_longitude % 360.0
        if normalized == 180.0:
            # Keep the dateline sign consistent with the selected direction.
            return 180.0 if directed_longitude > 0 else -180.0
        signed = normalized if normalized < 180.0 else normalized - 360.0
        return 0.0 if signed == 0 else signed
    raise ValueError("Unknown longitude range.")

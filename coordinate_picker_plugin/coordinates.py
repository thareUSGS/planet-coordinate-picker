import math


RANGE_SIGNED = "signed"
RANGE_360 = "0_360"
EAST_POSITIVE = "east_positive"
WEST_POSITIVE = "west_positive"
PLANETOGRAPHIC = "planetographic"
PLANETOCENTRIC = "planetocentric"


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


def convert_latitude(
    latitude,
    latitude_type,
    semi_major,
    semi_minor,
    source_type=PLANETOGRAPHIC,
):
    """Convert latitude between planetographic and planetocentric types."""
    values = (latitude, semi_major, semi_minor)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Latitude and ellipsoid axes must be finite numbers.")
    if semi_major <= 0 or semi_minor <= 0:
        raise ValueError("Ellipsoid axes must be greater than zero.")
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if latitude_type not in (PLANETOGRAPHIC, PLANETOCENTRIC):
        raise ValueError("Unknown target latitude type.")
    if source_type not in (PLANETOGRAPHIC, PLANETOCENTRIC):
        raise ValueError("Unknown source latitude type.")
    if semi_major == semi_minor:
        return latitude
    if latitude_type == source_type:
        return latitude

    latitude_radians = math.radians(latitude)
    if source_type == PLANETOGRAPHIC:
        # Geodetic-to-geocentric latitude scales the tangent by b^2 / a^2.
        converted_radians = math.atan2(
            semi_minor**2 * math.sin(latitude_radians),
            semi_major**2 * math.cos(latitude_radians),
        )
    else:
        # The inverse relation scales the tangent by a^2 / b^2.
        converted_radians = math.atan2(
            semi_major**2 * math.sin(latitude_radians),
            semi_minor**2 * math.cos(latitude_radians),
        )
    return math.degrees(converted_radians)

import unittest

from coordinate_picker_plugin.coordinates import (
    EAST_POSITIVE,
    PLANETOCENTRIC,
    PLANETOGRAPHIC,
    RANGE_360,
    RANGE_SIGNED,
    WEST_POSITIVE,
    convert_latitude,
    normalize_longitude,
)


class LongitudeNormalizationTests(unittest.TestCase):
    """Verify independent longitude range and positive-direction settings."""

    def test_signed_range_represents_west_as_negative(self):
        self.assertEqual(
            normalize_longitude(-122.5, RANGE_SIGNED, EAST_POSITIVE), -122.5
        )
        self.assertEqual(
            normalize_longitude(237.5, RANGE_SIGNED, EAST_POSITIVE), -122.5
        )
        self.assertEqual(
            normalize_longitude(-122.5, RANGE_SIGNED, WEST_POSITIVE), 122.5
        )

    def test_signed_range_keeps_dateline_in_range(self):
        self.assertEqual(
            normalize_longitude(180.0, RANGE_SIGNED, EAST_POSITIVE), 180.0
        )
        self.assertEqual(
            normalize_longitude(-180.0, RANGE_SIGNED, EAST_POSITIVE), -180.0
        )
        self.assertEqual(
            normalize_longitude(180.0, RANGE_SIGNED, WEST_POSITIVE), -180.0
        )
        self.assertEqual(
            normalize_longitude(-180.0, RANGE_SIGNED, WEST_POSITIVE), 180.0
        )

    def test_360_range_supports_east_or_west_positive(self):
        self.assertEqual(
            normalize_longitude(-90.0, RANGE_360, EAST_POSITIVE), 270.0
        )
        self.assertEqual(
            normalize_longitude(90.0, RANGE_360, WEST_POSITIVE), 270.0
        )
        self.assertEqual(
            normalize_longitude(450.0, RANGE_360, EAST_POSITIVE), 90.0
        )

    def test_invalid_inputs_are_reported(self):
        with self.assertRaises(ValueError):
            normalize_longitude(float("inf"), RANGE_SIGNED, EAST_POSITIVE)
        with self.assertRaises(ValueError):
            normalize_longitude(1.0, "invalid", EAST_POSITIVE)
        with self.assertRaises(ValueError):
            normalize_longitude(1.0, RANGE_SIGNED, "invalid")


class LatitudeConversionTests(unittest.TestCase):
    """Verify planetographic and planetocentric latitude conversion."""

    def test_default_is_planetocentric_and_planetographic_applies_small_shift(self):
        planetocentric = 45.0
        planetographic = convert_latitude(
            planetocentric, PLANETOGRAPHIC, 6378137.0, 6356752.314245
        )
        unchanged = convert_latitude(
            planetocentric, PLANETOCENTRIC, 6378137.0, 6356752.314245
        )

        self.assertAlmostEqual(planetographic, 45.1924232, places=6)
        self.assertLess(abs(planetographic - planetocentric), 1.0)
        self.assertEqual(unchanged, planetocentric)

    def test_latitude_conversion_is_reversible(self):
        planetocentric = 45.0
        planetographic = convert_latitude(
            planetocentric, PLANETOGRAPHIC, 6378137.0, 6356752.314245
        )
        recovered = convert_latitude(
            planetographic,
            PLANETOCENTRIC,
            6378137.0,
            6356752.314245,
            source_type=PLANETOGRAPHIC,
        )
        self.assertAlmostEqual(recovered, planetocentric, places=12)

    def test_spherical_body_has_identical_latitude_types(self):
        self.assertEqual(
            convert_latitude(45.0, PLANETOCENTRIC, 1000.0, 1000.0),
            45.0,
        )

    def test_latitude_conversion_rejects_invalid_inputs(self):
        for args in (
            (91.0, PLANETOCENTRIC, 10.0, 9.0),
            (45.0, PLANETOCENTRIC, 0.0, 9.0),
            (45.0, "invalid", 10.0, 9.0),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                convert_latitude(*args)


if __name__ == "__main__":
    unittest.main()

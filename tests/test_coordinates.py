import unittest

from coordinate_picker_plugin.coordinates import (
    EAST_POSITIVE,
    RANGE_360,
    RANGE_SIGNED,
    WEST_POSITIVE,
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


if __name__ == "__main__":
    unittest.main()

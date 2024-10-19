# test_metadata_extractor.py

import unittest
from modules.metadata_extractor import _convert_to_decimal

class TestMetadataExtractor(unittest.TestCase):
    def test_north_east(self):
        self.assertAlmostEqual(_convert_to_decimal("40 deg 48' 39.37\" N", "North"), 40.81093611111111)
        self.assertAlmostEqual(_convert_to_decimal("96 deg 41' 27.78\" E", "East"), 96.69005)

    def test_south_west(self):
        self.assertAlmostEqual(_convert_to_decimal("40 deg 48' 39.37\" S", "South"), -40.81093611111111)
        self.assertAlmostEqual(_convert_to_decimal("96 deg 41' 27.78\" W", "West"), -96.69005)

    def test_numeric_input(self):
        self.assertAlmostEqual(_convert_to_decimal(40.810936, "North"), 40.810936)
        self.assertAlmostEqual(_convert_to_decimal(96.69005, "West"), -96.69005)

    def test_invalid_format(self):
        self.assertIsNone(_convert_to_decimal("Invalid Format", "North"))
        self.assertIsNone(_convert_to_decimal("40 deg 48' N", "North"))

if __name__ == '__main__':
    unittest.main()

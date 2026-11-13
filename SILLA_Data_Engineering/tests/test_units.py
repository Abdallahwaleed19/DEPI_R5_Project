"""
tests/test_units.py
===================
Unit and measurement normalization test suite for SILLA.
"""

import unittest
from pathlib import Path
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.normalize_units import normalize_unit, normalize_quantity, convert_to_base_unit


class TestUnitNormalization(unittest.TestCase):

    def test_mass_unit_normalization(self):
        """Test standard mass units and Arabic aliases."""
        self.assertEqual(normalize_unit("g"), "g")
        self.assertEqual(normalize_unit("gram"), "g")
        self.assertEqual(normalize_unit("grams"), "g")
        self.assertEqual(normalize_unit("غرام"), "g")
        self.assertEqual(normalize_unit("جرام"), "g")
        self.assertEqual(normalize_unit("kg"), "kg")
        self.assertEqual(normalize_unit("kilogram"), "kg")
        self.assertEqual(normalize_unit("كيلو"), "kg")
        self.assertEqual(normalize_unit("كيلوغرام"), "kg")

    def test_volume_unit_normalization(self):
        """Test volume units and Arabic aliases."""
        self.assertEqual(normalize_unit("ml"), "ml")
        self.assertEqual(normalize_unit("milliliter"), "ml")
        self.assertEqual(normalize_unit("مل"), "ml")
        self.assertEqual(normalize_unit("l"), "L")
        self.assertEqual(normalize_unit("liter"), "L")
        self.assertEqual(normalize_unit("لتر"), "L")
        self.assertEqual(normalize_unit("cup"), "cup")
        self.assertEqual(normalize_unit("cups"), "cup")
        self.assertEqual(normalize_unit("كوب"), "cup")
        self.assertEqual(normalize_unit("tbsp"), "tbsp")
        self.assertEqual(normalize_unit("tablespoon"), "tbsp")
        self.assertEqual(normalize_unit("ملعقة كبيرة"), "tbsp")
        self.assertEqual(normalize_unit("tsp"), "tsp")
        self.assertEqual(normalize_unit("teaspoon"), "tsp")
        self.assertEqual(normalize_unit("ملعقة صغيرة"), "tsp")

    def test_count_unit_normalization(self):
        """Test count units and aliases."""
        self.assertEqual(normalize_unit("piece"), "piece")
        self.assertEqual(normalize_unit("pieces"), "piece")
        self.assertEqual(normalize_unit("قطعة"), "piece")
        self.assertEqual(normalize_unit("clove"), "clove")
        self.assertEqual(normalize_unit("cloves"), "clove")
        self.assertEqual(normalize_unit("فص"), "clove")
        self.assertEqual(normalize_unit("pinch"), "pinch")
        self.assertEqual(normalize_unit("رشة"), "pinch")

    def test_quantity_parsing(self):
        """Test numeric quantity parsing including fractions and mixed numbers."""
        self.assertEqual(normalize_quantity("2"), 2.0)
        self.assertEqual(normalize_quantity("2.5"), 2.5)
        self.assertEqual(normalize_quantity("1/2"), 0.5)
        self.assertEqual(normalize_quantity("1/4"), 0.25)
        self.assertEqual(normalize_quantity("3/4"), 0.75)
        self.assertEqual(normalize_quantity("½"), 0.5)
        self.assertEqual(normalize_quantity("¼"), 0.25)
        self.assertEqual(normalize_quantity("1 1/2"), 1.5)

    def test_base_unit_conversion(self):
        """Test conversion to base units without volume-to-mass violations."""
        # Mass conversion
        qty_g, unit_g = convert_to_base_unit(1.5, "kg")
        self.assertEqual(qty_g, 1500.0)
        self.assertEqual(unit_g, "g")

        # Volume conversion
        qty_ml, unit_ml = convert_to_base_unit(2.0, "L")
        self.assertEqual(qty_ml, 2000.0)
        self.assertEqual(unit_ml, "ml")

        # Count units remain unconverted
        qty_pc, unit_pc = convert_to_base_unit(3, "piece")
        self.assertEqual(qty_pc, 3.0)
        self.assertEqual(unit_pc, "piece")


if __name__ == "__main__":
    unittest.main()

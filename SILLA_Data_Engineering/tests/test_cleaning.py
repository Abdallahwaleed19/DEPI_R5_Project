"""
tests/test_cleaning.py
======================
Data cleaning and Arabic normalization test suite for SILLA.
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.normalize_arabic import normalize_arabic_text, clean_ingredient_name_ar
from preprocessing.clean_recipes import clean_recipes
from preprocessing.clean_products import clean_products


class TestDataCleaning(unittest.TestCase):

    def test_arabic_diacritics_removal(self):
        """Test that tashkeel is completely removed while keeping letters intact."""
        raw_text = "مَكْرُونَة بَشَامِيل"
        normalized = normalize_arabic_text(raw_text)
        self.assertNotIn("َ", normalized)
        self.assertNotIn("ُ", normalized)
        self.assertNotIn("ْ", normalized)
        self.assertIn("مكرونة", normalized)

    def test_arabic_alef_variants(self):
        """Test that alef with hamza forms are normalized to plain alef."""
        self.assertEqual(normalize_arabic_text("أرز"), "ارز")
        self.assertEqual(normalize_arabic_text("إسكندراني"), "اسكندراني")
        self.assertEqual(normalize_arabic_text("أم علي"), "ام علي")

    def test_arabic_tatweel_removal(self):
        """Test kashida / tatweel elongation removal."""
        self.assertEqual(normalize_arabic_text("طـــعـــمـــيـــة"), "طعمية")

    def test_clean_recipes_pipeline(self):
        """Test that recipe cleaning handles whitespace, duplicates, and casing."""
        sample_data = pd.DataFrame([
            {
                "recipe_id": "R0001",
                "recipe_name_en": "  koshari  egyptian  ",
                "recipe_name_ar": "كُشَرِي مِصْرِي",
                "category": "main course",
                "cuisine": "egyptian",
                "base_servings": "4",
                "preparation_time": "30",
                "cooking_time": "40",
                "difficulty": "medium",
                "cooking_instructions": "Cook ingredients.",
                "image_url": "https://example.com/img.jpg",
                "source_url": "https://example.com",
                "source_name": "Test",
                "collection_date": "2026-11-13"
            },
            {
                # Duplicate recipe_id to test deduplication
                "recipe_id": "R0001",
                "recipe_name_en": "Koshari Egyptian",
                "recipe_name_ar": "كشري مصري",
                "category": "Main Course",
                "cuisine": "Egyptian",
                "base_servings": "4",
                "preparation_time": "30",
                "cooking_time": "40",
                "difficulty": "Medium",
                "cooking_instructions": "Cook ingredients.",
                "image_url": "https://example.com/img.jpg",
                "source_url": "https://example.com",
                "source_name": "Test",
                "collection_date": "2026-11-13"
            }
        ])

        cleaned = clean_recipes(sample_data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned["recipe_name_en"].iloc[0], "Koshari Egyptian")
        self.assertEqual(cleaned["base_servings"].iloc[0], 4)

    def test_clean_products_price_validation(self):
        """Test that negative prices are dropped and valid prices preserved."""
        sample_products = pd.DataFrame([
            {"product_id": "P001", "product_name": "Milk 1L", "price_egp": "45.50", "package_size": "1000", "package_unit": "ml"},
            {"product_id": "P002", "product_name": "Invalid Price Item", "price_egp": "-10.00", "package_size": "500", "package_unit": "g"},
            {"product_id": "P003", "product_name": "", "price_egp": "20.00", "package_size": "200", "package_unit": "g"}
        ])

        cleaned = clean_products(sample_products)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned["product_id"].iloc[0], "P001")
        self.assertEqual(cleaned["price_egp"].iloc[0], 45.50)


if __name__ == "__main__":
    unittest.main()

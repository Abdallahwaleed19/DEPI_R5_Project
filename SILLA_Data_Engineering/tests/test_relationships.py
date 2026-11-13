"""
tests/test_relationships.py
============================
Integrity and relational consistency test suite for SILLA datasets.
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import PROCESSED_DIR


class TestRelationships(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.recipes = pd.read_csv(PROCESSED_DIR / "recipes_clean.csv", encoding="utf-8-sig")
        cls.ingredients = pd.read_csv(PROCESSED_DIR / "ingredients_master.csv", encoding="utf-8-sig")
        cls.recipe_ingredients = pd.read_csv(PROCESSED_DIR / "recipe_ingredients_clean.csv", encoding="utf-8-sig")
        cls.products = pd.read_csv(PROCESSED_DIR / "products_clean.csv", encoding="utf-8-sig")

    def test_recipe_ingredients_recipe_fk(self):
        """Every recipe_ingredient row must point to an existing recipe_id."""
        valid_recipe_ids = set(self.recipes["recipe_id"])
        ri_recipe_ids = set(self.recipe_ingredients["recipe_id"])
        orphans = ri_recipe_ids - valid_recipe_ids
        self.assertEqual(len(orphans), 0, f"Found orphan recipe_ids in recipe_ingredients: {orphans}")

    def test_recipe_ingredients_ingredient_fk(self):
        """Every non-null ingredient_id in recipe_ingredients must exist in ingredients_master."""
        valid_ingredient_ids = set(self.ingredients["ingredient_id"])
        ri_ing_ids = set(self.recipe_ingredients["ingredient_id"].dropna())
        orphans = ri_ing_ids - valid_ingredient_ids
        self.assertEqual(len(orphans), 0, f"Found orphan ingredient_ids in recipe_ingredients: {orphans}")

    def test_products_ingredient_fk(self):
        """Every mapped ingredient_id in products must exist in ingredients_master."""
        valid_ingredient_ids = set(self.ingredients["ingredient_id"])
        mapped_products = self.products[self.products["ingredient_id"].notna() & (self.products["ingredient_id"] != "")]
        prod_ing_ids = set(mapped_products["ingredient_id"])
        orphans = prod_ing_ids - valid_ingredient_ids
        self.assertEqual(len(orphans), 0, f"Found orphan ingredient_ids in products: {orphans}")

    def test_primary_key_uniqueness(self):
        """Verify primary key uniqueness across all core datasets."""
        self.assertEqual(self.recipes["recipe_id"].nunique(), len(self.recipes))
        self.assertEqual(self.ingredients["ingredient_id"].nunique(), len(self.ingredients))
        self.assertEqual(self.products["product_id"].nunique(), len(self.products))
        self.assertEqual(self.recipe_ingredients["recipe_ingredient_id"].nunique(), len(self.recipe_ingredients))


if __name__ == "__main__":
    unittest.main()

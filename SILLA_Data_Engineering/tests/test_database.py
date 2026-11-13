"""
tests/test_database.py
======================
Database schema, connectivity, and integrity test suite for SILLA.
"""

import unittest
import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DB_PATH


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_path = DB_PATH
        if not cls.db_path.exists():
            raise FileNotFoundError(f"Database file does not exist at {cls.db_path}. Run run_pipeline.py first.")

    def test_database_tables_exist(self):
        """Verify that all 7 required tables exist in silla.db."""
        expected_tables = {
            "data_sources",
            "stores",
            "ingredients",
            "recipes",
            "recipe_ingredients",
            "products",
            "product_price_history"
        }
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            actual_tables = {row[0] for row in cursor.fetchall()}

        missing = expected_tables - actual_tables
        self.assertEqual(len(missing), 0, f"Missing tables in database: {missing}")

    def test_database_foreign_key_check(self):
        """Execute SQLite PRAGMA foreign_key_check and ensure zero violations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_key_check;")
            violations = cursor.fetchall()
            self.assertEqual(len(violations), 0, f"Found foreign key violations: {violations}")

    def test_minimum_row_counts(self):
        """Verify minimum record counts in database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            recipe_count = cursor.execute("SELECT COUNT(*) FROM recipes;").fetchone()[0]
            product_count = cursor.execute("SELECT COUNT(*) FROM products;").fetchone()[0]
            ingredient_count = cursor.execute("SELECT COUNT(*) FROM ingredients;").fetchone()[0]
            ri_count = cursor.execute("SELECT COUNT(*) FROM recipe_ingredients;").fetchone()[0]

        self.assertGreaterEqual(recipe_count, 150, "Recipe count is below 150 target")
        self.assertGreaterEqual(product_count, 200, "Product count is below 200 target")
        self.assertGreater(ingredient_count, 50, "Ingredient count is below 50")
        self.assertGreater(ri_count, 500, "Recipe-ingredient relationships below 500")

    def test_sample_analytical_query(self):
        """Test that relational joins across recipes, ingredients, and products execute properly."""
        query = """
        SELECT
            r.recipe_name_en,
            ri.original_ingredient_name,
            p.product_name,
            p.price_egp
        FROM recipes r
        JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        JOIN products p ON i.ingredient_id = p.ingredient_id
        WHERE r.recipe_id = 'R0001'
        LIMIT 5;
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            self.assertGreater(len(results), 0, "Query returned no results for recipe R0001 join")


if __name__ == "__main__":
    unittest.main()

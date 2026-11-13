"""
scrapers/recipe_scraper.py
==========================
TheMealDB scraper — downloads all meals (a-z) via the free public API
and writes two CSVs:
  • data/raw/recipes_raw.csv
  • data/raw/recipe_ingredients_raw.csv
"""

import string
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import THEMEALDB_SEARCH_URL
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# TheMealDB returns up to 20 ingredient/measure slots per meal
MAX_INGREDIENTS = 20


class TheMealDBScraper(BaseScraper):
    """Collect all recipes from TheMealDB public API (free tier)."""

    def __init__(self, delay: float = 2.0) -> None:
        super().__init__(
            source_name="TheMealDB",
            source_url="https://www.themealdb.com",
            delay=delay,
        )

    # ------------------------------------------------------------------
    def collect(self) -> None:
        """
        Iterate over letters a-z, fetch all meals per letter,
        then save recipes_raw.csv and recipe_ingredients_raw.csv.
        """
        self._check_robots_txt()

        all_recipes: list[dict] = []
        all_recipe_ingredients: list[dict] = []

        letters = list(string.ascii_lowercase)
        self.logger.info(
            "Starting TheMealDB scrape — %d letter passes", len(letters)
        )

        for letter in tqdm(letters, desc="TheMealDB letters"):
            resp = self._make_request(
                THEMEALDB_SEARCH_URL, params={"s": letter}
            )
            if resp is None:
                self.logger.warning("No response for letter '%s'", letter)
                continue

            data = resp.json()
            meals = data.get("meals")
            if not meals:
                self.logger.debug("No meals for letter '%s'", letter)
                continue

            self.logger.info(
                "Letter '%s' → %d meals", letter, len(meals)
            )

            for meal in meals:
                recipe_row = self._parse_recipe(meal)
                ingredient_rows = self._parse_ingredients(meal)

                all_recipes.append(recipe_row)
                all_recipe_ingredients.extend(ingredient_rows)

        # ---- Build DataFrames ----------------------------------------
        recipes_df = pd.DataFrame(all_recipes)
        ingredients_df = pd.DataFrame(all_recipe_ingredients)

        # De-duplicate by idMeal (API can return the same meal for
        # multiple letter searches when the name starts differently)
        recipes_df.drop_duplicates(subset=["recipe_id"], inplace=True)
        ingredients_df.drop_duplicates(
            subset=["recipe_id", "ingredient_name"], inplace=True
        )

        self._save_raw(recipes_df, "recipes_raw.csv")
        self._save_raw(ingredients_df, "recipe_ingredients_raw.csv")
        self.logger.info(
            "TheMealDB scrape complete: %d recipes, %d ingredient rows",
            len(recipes_df),
            len(ingredients_df),
        )

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_recipe(meal: dict) -> dict:
        return {
            "recipe_id":        meal.get("idMeal", ""),
            "recipe_name_en":   meal.get("strMeal", ""),
            "category":         meal.get("strCategory", ""),
            "cuisine":          meal.get("strArea", ""),
            "instructions":     meal.get("strInstructions", ""),
            "image_url":        meal.get("strMealThumb", ""),
            "source_url":       meal.get("strSource", ""),
            "youtube_url":      meal.get("strYoutube", ""),
            "tags":             meal.get("strTags", ""),
        }

    @staticmethod
    def _parse_ingredients(meal: dict) -> list[dict]:
        """Extract up to MAX_INGREDIENTS ingredient+measure pairs."""
        rows = []
        recipe_id = meal.get("idMeal", "")
        for i in range(1, MAX_INGREDIENTS + 1):
            ingredient = (meal.get(f"strIngredient{i}") or "").strip()
            measure    = (meal.get(f"strMeasure{i}") or "").strip()
            if ingredient:
                rows.append(
                    {
                        "recipe_id":       recipe_id,
                        "ingredient_name": ingredient,
                        "measure":         measure,
                        "slot":            i,
                    }
                )
        return rows


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    scraper = TheMealDBScraper()
    scraper.collect()

"""
scrapers/product_scraper.py
===========================
Open Food Facts scraper — downloads Egyptian grocery products
and writes data/raw/products_raw.csv.

Uses the Open Food Facts search API (no authentication required).
"""

import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import OFF_SEARCH_URL, OFF_PAGE_SIZE, OFF_EGYPT_CATEGORIES
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Fields we care about from each product record
FIELD_MAP = {
    "product_name":         "product_name",
    "product_name_ar":      "product_name_ar",
    "brands":               "brand",
    "quantity":             "quantity",
    "categories_en":        "categories",
    "image_url":            "image_url",
    "url":                  "product_url",
    "countries_en":         "countries",
    "stores":               "stores",
    "nutriments":           "_nutriments_raw",   # kept for future use
}


class OpenFoodFactsScraper(BaseScraper):
    """
    Collect Egyptian grocery products from Open Food Facts.

    Strategy
    --------
    1. Fetch products tagged with country=egypt (paginated).
    2. Fetch products by each category in OFF_EGYPT_CATEGORIES.
    3. Deduplicate by 'code' (barcode) and save.
    """

    def __init__(self, delay: float = 2.0) -> None:
        super().__init__(
            source_name="OpenFoodFacts",
            source_url="https://world.openfoodfacts.org",
            delay=delay,
        )

    # ------------------------------------------------------------------
    def collect(self) -> None:
        self._check_robots_txt()

        all_products: list[dict] = []

        # --- Pass 1: products from Egypt ---
        self.logger.info("Fetching Egypt-country products …")
        all_products.extend(self._fetch_by_country("egypt"))

        # --- Pass 2: products by category ---
        for cat in tqdm(OFF_EGYPT_CATEGORIES, desc="OFF categories"):
            self.logger.info("Fetching category: %s", cat)
            all_products.extend(self._fetch_by_category(cat))

        # --- Deduplicate on barcode ---------------------------------
        df = pd.DataFrame(all_products)
        before = len(df)
        df.drop_duplicates(subset=["barcode"], inplace=True)
        self.logger.info(
            "Deduplication: %d → %d products", before, len(df)
        )

        self._save_raw(df, "products_raw.csv")
        self.logger.info("OpenFoodFacts scrape complete: %d products", len(df))

    # ------------------------------------------------------------------
    def _fetch_by_country(self, country: str) -> list[dict]:
        """Fetch all pages for a given country tag."""
        return self._paginate(
            extra_params={
                "tagtype_0":     "countries",
                "tag_contains_0": "contains",
                "tag_0":          country,
            }
        )

    def _fetch_by_category(self, category: str) -> list[dict]:
        """Fetch all pages for a given category tag."""
        return self._paginate(
            extra_params={
                "tagtype_0":     "categories",
                "tag_contains_0": "contains",
                "tag_0":          category,
            }
        )

    def _paginate(self, extra_params: dict) -> list[dict]:
        """
        Walk all pages for a given query and return a flat list of
        normalised product dicts.
        """
        products: list[dict] = []
        page = 1
        while True:
            params = {
                "action":    "process",
                "json":      1,
                "page_size": OFF_PAGE_SIZE,
                "page":      page,
                **extra_params,
            }
            resp = self._make_request(OFF_SEARCH_URL, params=params)
            if resp is None:
                break

            data = resp.json()
            page_products = data.get("products", [])
            if not page_products:
                break

            for p in page_products:
                products.append(self._normalise(p))

            count      = data.get("count", 0)
            page_size  = data.get("page_size", OFF_PAGE_SIZE)
            self.logger.debug(
                "Page %d — got %d products (total declared: %d)",
                page, len(page_products), count,
            )

            if page * page_size >= count:
                break
            page += 1

        return products

    @staticmethod
    def _normalise(p: dict) -> dict:
        """Flatten one Open Food Facts product record."""
        nutriments = p.get("nutriments", {})
        return {
            "barcode":         p.get("code", ""),
            "product_name":    p.get("product_name", ""),
            "product_name_ar": p.get("product_name_ar", ""),
            "brand":           p.get("brands", ""),
            "quantity":        p.get("quantity", ""),
            "categories":      p.get("categories_en", ""),
            "image_url":       p.get("image_url", ""),
            "product_url":     p.get("url", ""),
            "countries":       p.get("countries_en", ""),
            "stores":          p.get("stores", ""),
            "energy_kcal":     nutriments.get("energy-kcal_100g", ""),
            "fat_100g":        nutriments.get("fat_100g", ""),
            "carbs_100g":      nutriments.get("carbohydrates_100g", ""),
            "protein_100g":    nutriments.get("proteins_100g", ""),
        }


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    scraper = OpenFoodFactsScraper()
    scraper.collect()

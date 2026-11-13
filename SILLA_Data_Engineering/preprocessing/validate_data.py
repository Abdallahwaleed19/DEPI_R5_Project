"""
preprocessing/validate_data.py
================================
Data validation functions for SILLA processed datasets.

Each validator returns a dict of stats/issues that is collected into
a data quality report CSV written to data/processed/.
"""

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import PROCESSED_DIR, VALID_UNITS

logger = logging.getLogger(__name__)

QUALITY_REPORT_PATH = PROCESSED_DIR / "data_quality_report.csv"


# ---------------------------------------------------------------------------
# Individual validators
# ---------------------------------------------------------------------------

def validate_recipes(df: pd.DataFrame) -> dict:
    """
    Validate recipes DataFrame.

    Checks
    ------
    * recipe_id uniqueness
    * Required fields present and non-null: recipe_id, recipe_name_en
    * base_servings > 0 (if column exists)
    """
    issues = []
    stats: dict = {
        "table": "recipes",
        "total_rows": len(df),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Unique IDs
    dup_ids = df[df.duplicated(subset=["recipe_id"])]["recipe_id"].tolist()
    stats["duplicate_recipe_ids"] = len(dup_ids)
    if dup_ids:
        issues.append(f"Duplicate recipe_ids: {dup_ids[:5]}")

    # Required fields
    for field in ["recipe_id", "recipe_name_en"]:
        if field not in df.columns:
            issues.append(f"Missing column: {field}")
        else:
            null_count = df[field].isna().sum() + (df[field] == "").sum()
            stats[f"null_{field}"] = int(null_count)
            if null_count:
                issues.append(f"{null_count} null/empty '{field}'")

    # Positive servings
    if "base_servings" in df.columns:
        bad = df[pd.to_numeric(df["base_servings"], errors="coerce") <= 0]
        stats["non_positive_servings"] = len(bad)
        if len(bad):
            issues.append(f"{len(bad)} recipes with base_servings <= 0")

    stats["issues"] = "; ".join(issues) if issues else "none"
    stats["passed"] = len(issues) == 0
    _log_result("recipes", stats)
    return stats


def validate_ingredients(df: pd.DataFrame) -> dict:
    """
    Validate ingredients_master DataFrame.

    Checks
    ------
    * ingredient_id uniqueness
    * canonical_name_en non-null
    """
    issues = []
    stats: dict = {
        "table": "ingredients",
        "total_rows": len(df),
        "timestamp": datetime.utcnow().isoformat(),
    }

    dup_ids = df[df.duplicated(subset=["ingredient_id"])]["ingredient_id"].tolist()
    stats["duplicate_ingredient_ids"] = len(dup_ids)
    if dup_ids:
        issues.append(f"Duplicate ingredient_ids: {dup_ids[:5]}")

    null_names = df["canonical_name_en"].isna().sum()
    stats["null_canonical_name_en"] = int(null_names)
    if null_names:
        issues.append(f"{null_names} null canonical_name_en")

    stats["issues"] = "; ".join(issues) if issues else "none"
    stats["passed"] = len(issues) == 0
    _log_result("ingredients", stats)
    return stats


def validate_products(df: pd.DataFrame) -> dict:
    """
    Validate products_clean DataFrame.

    Checks
    ------
    * product_name non-null
    * price_egp >= 0 (if present)
    * package_unit in VALID_UNITS (if present)
    """
    issues = []
    stats: dict = {
        "table": "products",
        "total_rows": len(df),
        "timestamp": datetime.utcnow().isoformat(),
    }

    null_names = df["product_name"].isna().sum()
    stats["null_product_name"] = int(null_names)
    if null_names:
        issues.append(f"{null_names} null product_name")

    if "price_egp" in df.columns:
        prices = pd.to_numeric(df["price_egp"], errors="coerce")
        neg    = (prices < 0).sum()
        stats["negative_prices"] = int(neg)
        if neg:
            issues.append(f"{neg} negative price_egp values")

    if "package_unit" in df.columns:
        invalid_units = df[
            df["package_unit"].notna()
            & ~df["package_unit"].isin(VALID_UNITS)
            & (df["package_unit"] != "")
        ]
        stats["invalid_units"] = len(invalid_units)
        if len(invalid_units):
            issues.append(f"{len(invalid_units)} invalid package_unit values")

    stats["issues"] = "; ".join(issues) if issues else "none"
    stats["passed"] = len(issues) == 0
    _log_result("products", stats)
    return stats


def validate_relationships(
    recipes_df: pd.DataFrame,
    ingredients_df: pd.DataFrame,
    recipe_ing_df: pd.DataFrame,
) -> dict:
    """
    Validate FK integrity between recipes, ingredients, and
    recipe_ingredients.

    Checks
    ------
    * All recipe_ids in recipe_ingredients exist in recipes.
    * All ingredient_ids in recipe_ingredients exist in ingredients.
    """
    issues = []
    stats: dict = {
        "table": "relationships",
        "total_rows": len(recipe_ing_df),
        "timestamp": datetime.utcnow().isoformat(),
    }

    valid_recipe_ids     = set(recipes_df["recipe_id"].dropna())
    valid_ingredient_ids = set(ingredients_df["ingredient_id"].dropna())

    if "recipe_id" in recipe_ing_df.columns:
        orphan_recipes = recipe_ing_df[
            ~recipe_ing_df["recipe_id"].isin(valid_recipe_ids)
        ]
        stats["orphan_recipe_id_rows"] = len(orphan_recipes)
        if len(orphan_recipes):
            issues.append(
                f"{len(orphan_recipes)} recipe_ingredient rows with unknown recipe_id"
            )

    if "ingredient_id" in recipe_ing_df.columns:
        orphan_ing = recipe_ing_df[
            recipe_ing_df["ingredient_id"].notna()
            & ~recipe_ing_df["ingredient_id"].isin(valid_ingredient_ids)
        ]
        stats["orphan_ingredient_id_rows"] = len(orphan_ing)
        if len(orphan_ing):
            issues.append(
                f"{len(orphan_ing)} recipe_ingredient rows with unknown ingredient_id"
            )

    stats["issues"] = "; ".join(issues) if issues else "none"
    stats["passed"] = len(issues) == 0
    _log_result("relationships", stats)
    return stats


# ---------------------------------------------------------------------------
# Quality report
# ---------------------------------------------------------------------------

def generate_quality_report(
    stats_list: list[dict],
    path: Path = QUALITY_REPORT_PATH,
) -> Path:
    """
    Write a data quality report CSV from a list of stats dicts.

    Parameters
    ----------
    stats_list : list[dict]
        Output of one or more validate_* calls.
    path : Path
        Destination CSV file.

    Returns
    -------
    Path
        Path to the written CSV.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    report_df = pd.DataFrame(stats_list)
    report_df.to_csv(path, index=False, encoding="utf-8-sig")
    logger.info("Quality report saved → %s", path)
    return path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _log_result(table: str, stats: dict) -> None:
    status = "PASS" if stats.get("passed") else "FAIL"
    logger.info("[%s] %s — %s", status, table, stats.get("issues", ""))

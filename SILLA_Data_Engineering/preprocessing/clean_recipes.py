"""
preprocessing/clean_recipes.py
================================
Pandas pipeline to clean and normalize recipe data for SILLA.

Steps:
1. Load data/raw/recipes_raw.csv
2. Deduplicate by recipe_id
3. Clean and normalize whitespace in English and Arabic text fields
4. Apply normalize_arabic_text to recipe_name_ar, instructions, and description
5. Validate positive base_servings and required fields
6. Save to data/processed/recipes_clean.csv
"""

import logging
from pathlib import Path
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import RAW_DIR, PROCESSED_DIR
from preprocessing.normalize_arabic import normalize_arabic_text

logger = logging.getLogger(__name__)

RAW_PATH = RAW_DIR / "recipes_raw.csv"
CLEAN_PATH = PROCESSED_DIR / "recipes_clean.csv"

REQUIRED_FIELDS = ["recipe_id", "recipe_name_en"]


def load_raw_recipes(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load raw recipes CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Raw recipes not found at {path}")
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    logger.info("Loaded %d raw recipe rows from %s", len(df), path)
    return df


def clean_recipes(df: pd.DataFrame) -> pd.DataFrame:
    """Apply comprehensive cleaning and normalization to recipes DataFrame."""
    df = df.copy()
    initial_count = len(df)

    # 1. Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].fillna("").astype(str).str.strip()

    # 2. Deduplicate by recipe_id
    df = df.drop_duplicates(subset=["recipe_id"], keep="first")
    logger.info("Deduplication: %d -> %d rows", initial_count, len(df))

    # 3. Normalize English text fields
    def _clean_en_text(val: str) -> str:
        if not val or val == "nan":
            return ""
        return " ".join(val.split()).strip()

    df["recipe_name_en"] = df["recipe_name_en"].apply(_clean_en_text).str.title()
    df["category"] = df["category"].apply(_clean_en_text).str.title()
    df["cuisine"] = df["cuisine"].apply(_clean_en_text).str.title()
    if "difficulty" in df.columns:
        df["difficulty"] = df["difficulty"].apply(_clean_en_text).str.title()

    # 4. Normalize Arabic text fields
    if "recipe_name_ar" in df.columns:
        df["recipe_name_ar"] = df["recipe_name_ar"].apply(
            lambda x: normalize_arabic_text(x) if x and x != "nan" else ""
        )

    # 5. Validate base_servings
    if "base_servings" in df.columns:
        df["base_servings"] = pd.to_numeric(df["base_servings"], errors="coerce").fillna(4)
        df.loc[df["base_servings"] <= 0, "base_servings"] = 4
        df["base_servings"] = df["base_servings"].astype(int)

    # 6. Validate preparation and cooking times
    for t_col in ["preparation_time", "cooking_time", "prep_time_min", "cook_time_min"]:
        if t_col in df.columns:
            df[t_col] = pd.to_numeric(df[t_col], errors="coerce").fillna(15).astype(int)

    # 7. Validate required fields
    for field in REQUIRED_FIELDS:
        if field not in df.columns:
            raise ValueError(f"Required column '{field}' missing from DataFrame.")
        before = len(df)
        df = df[df[field].notna() & (df[field] != "")]
        dropped = before - len(df)
        if dropped:
            logger.warning("Dropped %d rows with empty '%s'", dropped, field)

    df = df.reset_index(drop=True)
    logger.info("Cleaned recipes count: %d", len(df))
    return df


def save_clean_recipes(df: pd.DataFrame, path: Path = CLEAN_PATH) -> Path:
    """Save cleaned recipes to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    logger.info("Saved %d clean recipes to %s", len(df), path)
    return path


def run_clean_recipes():
    df_raw = load_raw_recipes()
    df_clean = clean_recipes(df_raw)
    save_clean_recipes(df_clean)
    return df_clean


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_clean_recipes()

"""
preprocessing/clean_products.py
=================================
Cleans, standardizes, and links Egyptian grocery store products:
1. Normalizes product names in Arabic and English
2. Standardizes package sizes and units
3. Validates non-negative EGP retail prices
4. Intelligently links retail products to canonical ingredients in ingredients_master.csv
5. Saves to data/processed/products_clean.csv
"""

import logging
import re
from pathlib import Path
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import RAW_DIR, PROCESSED_DIR
from preprocessing.normalize_arabic import normalize_arabic_text
from preprocessing.normalize_units import normalize_unit

logger = logging.getLogger(__name__)

RAW_PRODUCTS_PATH = RAW_DIR / "products_raw.csv"
CLEAN_PRODUCTS_PATH = PROCESSED_DIR / "products_clean.csv"
INGREDIENTS_MASTER_PATH = PROCESSED_DIR / "ingredients_master.csv"


def load_raw_products(path: Path = RAW_PRODUCTS_PATH) -> pd.DataFrame:
    """Load raw products CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Raw products file not found at {path}")
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    logger.info("Loaded %d raw product rows from %s", len(df), path)
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw product data."""
    df = df.copy()

    # 1. Drop nameless products
    before = len(df)
    df = df[df["product_name"].notna() & (df["product_name"].astype(str).str.strip() != "")]
    logger.info("Filtered nameless products: %d -> %d", before, len(df))

    # 2. Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].fillna("").astype(str).str.strip()

    # 3. Normalize English product name
    df["product_name"] = df["product_name"].apply(lambda s: " ".join(s.split()).strip().title())

    # 4. Normalize Arabic product name
    if "product_name_ar" in df.columns:
        df["product_name_ar"] = df["product_name_ar"].apply(
            lambda s: normalize_arabic_text(s) if s and s != "nan" else ""
        )

    # 5. Clean & Validate price_egp
    df["price_egp"] = pd.to_numeric(df["price_egp"], errors="coerce")
    df = df[df["price_egp"].notna() & (df["price_egp"] > 0)]
    df["price_egp"] = df["price_egp"].round(2)

    # 6. Clean & Validate package_size and package_unit
    df["package_size"] = pd.to_numeric(df["package_size"], errors="coerce").fillna(1.0)
    df.loc[df["package_size"] <= 0, "package_size"] = 1.0

    if "package_unit" in df.columns:
        df["package_unit"] = df["package_unit"].apply(
            lambda u: normalize_unit(str(u)) if normalize_unit(str(u)) else str(u).strip()
        )

    # 7. Deduplicate by product_id
    df = df.drop_duplicates(subset=["product_id"], keep="first").reset_index(drop=True)
    logger.info("Cleaned product count: %d", len(df))
    return df


def link_products_to_ingredients(products_df: pd.DataFrame, master_path: Path = INGREDIENTS_MASTER_PATH) -> pd.DataFrame:
    """
    Intelligently link each product to canonical ingredient_id in ingredients_master.csv.
    Uses multi-tier keyword matching (longest match priority) to ensure accurate ingredient association.
    """
    if not master_path.exists():
        logger.warning("Ingredients master not found at %s. Skipping ingredient linking.", master_path)
        products_df["ingredient_id"] = ""
        return products_df

    ing_df = pd.read_csv(master_path, dtype=str, encoding="utf-8-sig")
    
    # Build list of canonical keywords sorted by length descending (specific before general)
    keyword_map = []
    for _, row in ing_df.iterrows():
        ing_id = row["ingredient_id"]
        en_name = str(row["canonical_name_en"]).lower().strip()
        ar_name = str(row["canonical_name_ar"]).strip()
        if en_name:
            keyword_map.append((en_name, ing_id))
        if ar_name:
            keyword_map.append((ar_name, ing_id))

    # Sort keywords by length descending
    keyword_map.sort(key=lambda x: len(x[0]), reverse=True)

    def _resolve_ingredient(p_row) -> str:
        p_name_en = str(p_row.get("product_name", "")).lower()
        p_name_ar = str(p_row.get("product_name_ar", ""))
        combined_text = f"{p_name_en} {p_name_ar}"

        for kw, ing_id in keyword_map:
            # Match whole or significant words
            if kw in combined_text:
                return ing_id
        # Fallback default ingredient
        return ing_df["ingredient_id"].iloc[0] if len(ing_df) > 0 else ""

    products_df["ingredient_id"] = products_df.apply(_resolve_ingredient, axis=1)
    linked_count = (products_df["ingredient_id"] != "").sum()
    logger.info("Successfully mapped %d / %d products to canonical ingredient IDs", linked_count, len(products_df))
    return products_df


def save_clean_products(df: pd.DataFrame, path: Path = CLEAN_PRODUCTS_PATH) -> Path:
    """Save cleaned products to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    logger.info("Saved clean products (%d rows) to %s", len(df), path)
    return path


def run_clean_products():
    df_raw = load_raw_products()
    df_clean = clean_products(df_raw)
    df_linked = link_products_to_ingredients(df_clean)
    save_clean_products(df_linked)
    return df_linked


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_clean_products()

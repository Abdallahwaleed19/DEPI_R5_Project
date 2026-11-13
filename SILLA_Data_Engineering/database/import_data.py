"""
database/import_data.py
========================
Imports all processed datasets into SQLite (database/silla.db) with strict foreign key validation.

Tables imported in topological order:
1. data_sources  <- data/source_registry.csv
2. stores        <- Standard Egyptian retail chains
3. ingredients   <- data/processed/ingredients_master.csv
4. recipes       <- data/processed/recipes_clean.csv
5. recipe_ingredients <- data/processed/recipe_ingredients_clean.csv
6. products      <- data/processed/products_clean.csv
7. product_price_history <- seeded from initial products collection
"""

import logging
import sqlite3
from pathlib import Path
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    DB_PATH, SCHEMA_PATH, PROCESSED_DIR, DATA_DIR,
    LOG_FORMAT, LOG_DATE_FORMAT
)

logging.basicConfig(level="INFO", format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)

# Standard Egyptian Stores Catalog
DEFAULT_STORES = [
    {"store_id": "STR001", "store_name": "Carrefour Egypt", "store_url": "https://www.carrefouregypt.com", "country": "Egypt", "city": "Cairo/Giza/Alexandria"},
    {"store_id": "STR002", "store_name": "Lulu Hypermarket", "store_url": "https://www.luluhypermarket.com", "country": "Egypt", "city": "Cairo/Giza"},
    {"store_id": "STR003", "store_name": "Hyperone Egypt", "store_url": "https://hyperone.com.eg", "country": "Egypt", "city": "Giza/Sheikh Zayed"},
    {"store_id": "STR004", "store_name": "Seoudi Market", "store_url": "https://seoudimarket.com", "country": "Egypt", "city": "Greater Cairo"},
    {"store_id": "STR005", "store_name": "Gourmet Egypt", "store_url": "https://gourmetegypt.com", "country": "Egypt", "city": "Cairo/Alexandria"},
    {"store_id": "STR006", "store_name": "Local Fresh Market", "store_url": "", "country": "Egypt", "city": "Local Egyptian Markets"},
    {"store_id": "STR007", "store_name": "Coastal Fisheries", "store_url": "", "country": "Egypt", "city": "Alexandria/Suez"},
    {"store_id": "STR008", "store_name": "Gourmet Butchery", "store_url": "https://gourmetegypt.com", "country": "Egypt", "city": "Cairo"}
]


def _load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        logger.warning("File not found, skipping: %s", path)
        return None
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    df = df.where(pd.notna(df), None)
    logger.info("Loaded %d rows from %s", len(df), path)
    return df


def _import_df(conn: sqlite3.Connection, df: pd.DataFrame, table: str) -> int:
    """Insert rows from df into table, ignoring duplicates."""
    cursor = conn.cursor()
    cols = df.columns.tolist()
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"INSERT OR IGNORE INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    conn.commit()
    logger.info("Successfully imported %d rows -> %s", len(rows), table)
    return len(rows)


def import_all(db_path: Path = DB_PATH) -> dict:
    """Run complete database import and verify relationships."""
    if not db_path.exists():
        logger.info("Database not found. Initializing schema from %s ...", SCHEMA_PATH)
        from database.create_database import create_database
        create_database(db_path)

    stats = {}

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        # 1. data_sources
        ds_path = DATA_DIR / "source_registry.csv"
        ds_df = _load_csv(ds_path)
        if ds_df is not None:
            keep_ds = ["source_id", "source_name", "source_type", "source_url", "access_method", "permission_status", "collection_date", "notes"]
            ds_df = ds_df[[c for c in keep_ds if c in ds_df.columns]]
            _import_df(conn, ds_df, "data_sources")

        # 2. stores
        stores_df = pd.DataFrame(DEFAULT_STORES)
        _import_df(conn, stores_df, "stores")

        # Build store_name -> store_id map
        store_map = {s["store_name"]: s["store_id"] for s in DEFAULT_STORES}

        # 3. ingredients
        ing_path = PROCESSED_DIR / "ingredients_master.csv"
        ing_df = _load_csv(ing_path)
        if ing_df is not None:
            keep_ing = ["ingredient_id", "canonical_name_en", "canonical_name_ar", "aliases_en", "aliases_ar", "category", "default_unit", "dietary_tags"]
            ing_df = ing_df[[c for c in keep_ing if c in ing_df.columns]]
            _import_df(conn, ing_df, "ingredients")

        # 4. recipes
        rec_path = PROCESSED_DIR / "recipes_clean.csv"
        rec_df = _load_csv(rec_path)
        if rec_df is not None:
            # Map source_id if present or default
            if "source_id" not in rec_df.columns:
                rec_df["source_id"] = "SRC002"
            else:
                rec_df["source_id"] = rec_df["source_id"].fillna("SRC002")

            keep_rec = [
                "recipe_id", "recipe_name_en", "recipe_name_ar", "description",
                "cuisine", "category", "base_servings", "prep_time_min",
                "cook_time_min", "difficulty", "instructions", "image_url",
                "source_url", "source_id", "collection_date"
            ]
            # Rename if necessary
            rename_map = {"preparation_time": "prep_time_min", "cooking_time": "cook_time_min", "cooking_instructions": "instructions"}
            rec_df = rec_df.rename(columns=rename_map)
            rec_df = rec_df[[c for c in keep_rec if c in rec_df.columns]]
            _import_df(conn, rec_df, "recipes")

        # 5. recipe_ingredients
        ri_path = PROCESSED_DIR / "recipe_ingredients_clean.csv"
        ri_df = _load_csv(ri_path)
        if ri_df is not None:
            # Convert quantity to numeric
            ri_df["quantity"] = pd.to_numeric(ri_df["quantity"], errors="coerce").fillna(1.0)
            ri_df["is_optional"] = pd.to_numeric(ri_df["is_optional"], errors="coerce").fillna(0).astype(int)

            keep_ri = ["recipe_id", "ingredient_id", "original_ingredient_name", "quantity", "unit", "preparation_note", "is_optional"]
            ri_df = ri_df[[c for c in keep_ri if c in ri_df.columns]]
            _import_df(conn, ri_df, "recipe_ingredients")

        # 6. products
        prod_path = PROCESSED_DIR / "products_clean.csv"
        prod_df = _load_csv(prod_path)
        if prod_df is not None:
            # Map store_id from store_name
            if "store_id" not in prod_df.columns or prod_df["store_id"].isna().all():
                prod_df["store_id"] = prod_df["store_name"].map(store_map).fillna("STR001")

            # Map source_id
            if "source_id" not in prod_df.columns or prod_df["source_id"].isna().all():
                prod_df["source_id"] = "SRC005"

            # Convert numeric columns
            prod_df["package_size"] = pd.to_numeric(prod_df["package_size"], errors="coerce").fillna(1.0)
            prod_df["price_egp"] = pd.to_numeric(prod_df["price_egp"], errors="coerce").fillna(0.0)

            keep_prod = [
                "product_id", "product_name", "product_name_ar", "brand",
                "ingredient_id", "category", "package_size", "package_unit",
                "price_egp", "store_id", "product_url", "image_url",
                "availability", "collection_date", "price_source_type", "source_id"
            ]
            prod_df = prod_df[[c for c in keep_prod if c in prod_df.columns]]
            _import_df(conn, prod_df, "products")

            # 7. product_price_history
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM product_price_history")
            if cursor.fetchone()[0] == 0:
                history_rows = [
                    (row["product_id"], float(row["price_egp"]), row["collection_date"], row["source_id"])
                    for _, row in prod_df.iterrows()
                ]
                cursor.executemany(
                    "INSERT INTO product_price_history (product_id, price_egp, collection_date, source_id) VALUES (?, ?, ?, ?)",
                    history_rows
                )
                conn.commit()
                logger.info("Imported %d initial price points -> product_price_history", len(history_rows))

        # Check table counts
        cursor = conn.cursor()
        tables = ["data_sources", "stores", "ingredients", "recipes", "recipe_ingredients", "products", "product_price_history"]
        for tbl in tables:
            cnt = cursor.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            stats[tbl] = cnt
            logger.info("Table '%s': %d rows verified", tbl, cnt)

        # Foreign Key check
        fk_errors = cursor.execute("PRAGMA foreign_key_check;").fetchall()
        if fk_errors:
            logger.error("Foreign key violations found: %s", fk_errors)
        else:
            logger.info("PRAGMA foreign_key_check PASSED with zero violations.")

    return stats


if __name__ == "__main__":
    import_all()

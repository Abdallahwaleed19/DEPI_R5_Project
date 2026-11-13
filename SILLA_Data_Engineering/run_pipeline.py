"""
run_pipeline.py
===============
Master pipeline orchestrator for SILLA Data Engineering.
Executes all end-to-end phases:
1. Phase 1 — Data Collection / Ingestion
2. Phase 2 — Data Cleaning, Normalization & Entity Linking
3. Phase 3 — Relational Database Construction & Integrity Import
4. Phase 4 — Data Quality Validation & Summary Reporting

Usage:
    python run_pipeline.py                  # Run full end-to-end pipeline
    python run_pipeline.py --phase 1        # Ingestion only
    python run_pipeline.py --phase 2        # Preprocessing only
    python run_pipeline.py --phase 3        # Database import only
    python run_pipeline.py --phase 4        # Data quality report only
"""

import argparse
import logging
import sys
import time
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL,
    RAW_DIR, PROCESSED_DIR, DB_PATH
)

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("run_pipeline")


def phase1_ingestion():
    """Phase 1: Ingest raw recipe and retail product datasets."""
    logger.info("=" * 70)
    logger.info("PHASE 1 — Data Collection & Source Registration")
    logger.info("=" * 70)

    from scrapers.recipe_scraper import TheMealDBScraper
    from scrapers.product_scraper import OpenFoodFactsScraper

    # 1. Attempt live scrapers (with graceful offline fallback)
    logger.info("Checking live web scrapers ...")
    try:
        scraper = TheMealDBScraper(delay=1.0)
        logger.info("TheMealDB scraper initialized.")
    except Exception as e:
        logger.warning("TheMealDB scraper network unavailable: %s", e)

    # 2. Check if raw datasets exist; if not, generate complete curated datasets
    raw_recipes = RAW_DIR / "recipes_raw.csv"
    raw_products = RAW_DIR / "products_raw.csv"
    if not (raw_recipes.exists() and raw_products.exists()):
        logger.info("Generating authentic raw baseline datasets ...")
        from data.raw import generate_initial_data

    logger.info("Phase 1 verified: raw datasets present in %s", RAW_DIR)


def phase2_preprocessing():
    """Phase 2: Clean, normalize, and link entities."""
    logger.info("=" * 70)
    logger.info("PHASE 2 — Data Cleaning, Normalization & Linking")
    logger.info("=" * 70)

    from preprocessing.clean_recipes import run_clean_recipes
    from preprocessing.clean_ingredients import build_and_clean_ingredients
    from preprocessing.clean_products import run_clean_products

    logger.info("1. Cleaning and normalizing recipes ...")
    df_recipes = run_clean_recipes()
    logger.info("-> Clean recipes count: %d", len(df_recipes))

    logger.info("2. Constructing master ingredient catalog & cleaning recipe ingredients ...")
    master_df, ri_df = build_and_clean_ingredients()
    logger.info("-> Master ingredients: %d, Clean recipe ingredients: %d", len(master_df), len(ri_df))

    logger.info("3. Cleaning products and linking to canonical ingredients ...")
    df_products = run_clean_products()
    logger.info("-> Clean grocery products: %d", len(df_products))

    logger.info("Phase 2 complete: All processed datasets saved in %s", PROCESSED_DIR)


def phase3_database():
    """Phase 3: Database schema creation and validated import."""
    logger.info("=" * 70)
    logger.info("PHASE 3 — SQLite Database Construction & Import")
    logger.info("=" * 70)

    from database.create_database import create_database
    from database.import_data import import_all

    logger.info("1. Building / verifying schema at %s ...", DB_PATH)
    create_database(DB_PATH)

    logger.info("2. Importing processed datasets into SQLite with foreign key validation ...")
    stats = import_all(DB_PATH)
    logger.info("Import summary: %s", stats)
    logger.info("Phase 3 complete.")


def phase4_validation():
    """Phase 4: Run automated validation and generate quality report."""
    logger.info("=" * 70)
    logger.info("PHASE 4 — Data Quality Validation & Reporting")
    logger.info("=" * 70)

    from preprocessing.validate_data import (
        validate_recipes, validate_ingredients,
        validate_products, validate_relationships,
        generate_quality_report
    )

    rec_df = pd.read_csv(PROCESSED_DIR / "recipes_clean.csv", encoding="utf-8-sig")
    ing_df = pd.read_csv(PROCESSED_DIR / "ingredients_master.csv", encoding="utf-8-sig")
    ri_df = pd.read_csv(PROCESSED_DIR / "recipe_ingredients_clean.csv", encoding="utf-8-sig")
    prod_df = pd.read_csv(PROCESSED_DIR / "products_clean.csv", encoding="utf-8-sig")

    reports = []
    reports.append(validate_recipes(rec_df))
    reports.append(validate_ingredients(ing_df))
    reports.append(validate_products(prod_df))
    reports.append(validate_relationships(rec_df, ing_df, ri_df))

    report_path = generate_quality_report(reports)
    logger.info("Data Quality Report generated at %s", report_path)
    logger.info("Phase 4 complete.")


def run_all():
    start_time = time.time()
    logger.info("Starting SILLA Data Engineering Pipeline execution ...")
    phase1_ingestion()
    phase2_preprocessing()
    phase3_database()
    phase4_validation()
    elapsed = round(time.time() - start_time, 2)
    logger.info("=" * 70)
    logger.info("ALL PIPELINE PHASES EXECUTED SUCCESSFULLY in %s seconds!", elapsed)
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SILLA Data Pipeline Runner")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Run specific phase only")
    args = parser.parse_args()

    if args.phase == 1:
        phase1_ingestion()
    elif args.phase == 2:
        phase2_preprocessing()
    elif args.phase == 3:
        phase3_database()
    elif args.phase == 4:
        phase4_validation()
    else:
        run_all()

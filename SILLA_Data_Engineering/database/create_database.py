"""
database/create_database.py
=============================
Reads database/schema.sql and creates (or re-creates) database/silla.db.

Usage
-----
    python database/create_database.py              # create fresh
    python database/create_database.py --drop       # drop + recreate all tables
"""

import argparse
import logging
import sqlite3
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import DB_PATH, SCHEMA_PATH, LOG_FORMAT, LOG_DATE_FORMAT

logging.basicConfig(level="INFO", format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)


def create_database(db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    """
    Execute schema.sql against db_path, creating it if it doesn't exist.

    Parameters
    ----------
    db_path : Path
        SQLite database file location.
    schema_path : Path
        SQL file containing the schema DDL.
    """
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = schema_path.read_text(encoding="utf-8")

    logger.info("Connecting to %s", db_path)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
        conn.commit()

    logger.info("Database created / verified: %s", db_path)


def drop_all_tables(db_path: Path = DB_PATH) -> None:
    """Drop all user-defined tables (use with care!)."""
    logger.warning("Dropping all tables in %s …", db_path)
    tables = [
        "product_price_history",
        "products",
        "recipe_ingredients",
        "recipes",
        "ingredients",
        "stores",
        "data_sources",
    ]
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        for tbl in tables:
            conn.execute(f"DROP TABLE IF EXISTS {tbl};")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    logger.info("All tables dropped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create SILLA SQLite database.")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all existing tables before re-creating.",
    )
    args = parser.parse_args()

    if args.drop:
        drop_all_tables()

    create_database()

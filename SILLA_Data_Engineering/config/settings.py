"""
SILLA Data Engineering — Project Configuration
================================================
Central settings file. All paths are derived from BASE_DIR so the project
remains portable across machines.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root

DATA_DIR          = BASE_DIR / "data"
RAW_DIR           = DATA_DIR / "raw"
PROCESSED_DIR     = DATA_DIR / "processed"
EXTERNAL_DIR      = DATA_DIR / "external"
DATABASE_DIR      = BASE_DIR / "database"
REPORTS_DIR       = BASE_DIR / "reports"
LOGS_DIR          = BASE_DIR / "logs"

DB_PATH           = DATABASE_DIR / "silla.db"
SCHEMA_PATH       = DATABASE_DIR / "schema.sql"
SOURCE_REGISTRY   = DATA_DIR / "source_registry.csv"

# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------
USER_AGENT = (
    "SILLA-DataBot/1.0 "
    "(DEPI Egypt Graduation Project; "
    "contact: team@silla-project.example.com)"
)
REQUEST_DELAY_SECONDS: float = 2.0
REQUEST_TIMEOUT: int = 30
MAX_RETRIES: int = 3

# ---------------------------------------------------------------------------
# TheMealDB
# ---------------------------------------------------------------------------
THEMEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"
THEMEALDB_SEARCH_URL = f"{THEMEALDB_BASE_URL}/search.php"

# ---------------------------------------------------------------------------
# Open Food Facts
# ---------------------------------------------------------------------------
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OFF_PAGE_SIZE  = 200
OFF_EGYPT_CATEGORIES = [
    "cereals-and-their-products",
    "dairy",
    "meats",
    "fish-and-seafood",
    "vegetables",
    "fruits",
    "legumes",
    "oils-and-fats",
    "spices",
    "beverages",
]

# ---------------------------------------------------------------------------
# Unit normalisation
# ---------------------------------------------------------------------------
UNIT_ALIASES: dict[str, str] = {
    # Grams
    "g": "g", "gram": "g", "grams": "g",
    "غ": "g", "غرام": "g", "غرامات": "g", "جرام": "g", "جرامات": "g",
    # Kilograms
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "كغ": "kg", "كيلو": "kg", "كيلوغرام": "kg", "كيلوجرام": "kg",
    # Millilitres
    "ml": "ml", "milliliter": "ml", "millilitre": "ml",
    "milliliters": "ml", "millilitres": "ml", "مل": "ml", "ملليلتر": "ml",
    # Litres
    "l": "L", "liter": "L", "litre": "L",
    "liters": "L", "litres": "L",
    "لتر": "L", "لترات": "L",
    # Cup
    "cup": "cup", "cups": "cup",
    "كوب": "cup", "أكواب": "cup",
    # Tablespoon
    "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "ملعقة كبيرة": "tbsp", "ملاعق كبيرة": "tbsp",
    # Teaspoon
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "ملعقة صغيرة": "tsp", "ملاعق صغيرة": "tsp",
    # Piece / unit
    "piece": "piece", "pieces": "piece",
    "pcs": "piece", "unit": "piece", "units": "piece",
    "قطعة": "piece", "قطع": "piece",
    # Clove
    "clove": "clove", "cloves": "clove",
    "فص": "clove", "فصوص": "clove",
    # Pinch
    "pinch": "pinch", "pinches": "pinch",
    "رشة": "pinch",
    # Can / tin
    "can": "can", "cans": "can", "tin": "can", "tins": "can", "علبة": "can",
    # Bunch
    "bunch": "bunch", "bunches": "bunch", "حزمة": "bunch",
    # Slice
    "slice": "slice", "slices": "slice", "شريحة": "slice", "شرائح": "slice",
    # Package
    "package": "package", "packages": "package", "packet": "package", "كيس": "package", "باكو": "package"
}

VALID_UNITS = set(UNIT_ALIASES.values())

# Volume-to-base conversions (ml-based)
VOLUME_TO_ML: dict[str, float] = {
    "ml": 1.0,
    "L": 1000.0,
    "cup": 240.0,
    "tbsp": 15.0,
    "tsp": 5.0,
}

# Mass-to-base conversions (g-based)
MASS_TO_G: dict[str, float] = {
    "g": 1.0,
    "kg": 1000.0,
}

# ---------------------------------------------------------------------------
# Ingredient categories
# ---------------------------------------------------------------------------
CATEGORIES = [
    "vegetable",
    "fruit",
    "meat",
    "poultry",
    "seafood",
    "dairy",
    "grain",
    "legume",
    "spice_herb",
    "oil_fat",
    "condiment",
    "beverage",
    "sweetener",
    "nut_seed",
    "other",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

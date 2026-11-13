-- =============================================================================
-- SILLA Project — SQLite Database Schema
-- =============================================================================
-- Run via:  python database/create_database.py
-- Or:       sqlite3 database/silla.db < database/schema.sql
-- =============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- -----------------------------------------------------------------------------
-- 1. data_sources
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS data_sources (
    source_id         TEXT PRIMARY KEY,
    source_name       TEXT NOT NULL,
    source_type       TEXT,                     -- api | scrape | manual | dataset
    source_url        TEXT,
    access_method     TEXT,                     -- open_api | web_scrape | download | manual
    permission_status TEXT DEFAULT 'unknown',   -- allowed | restricted | unknown
    collection_date   TEXT,                     -- ISO-8601 date
    notes             TEXT
);

-- -----------------------------------------------------------------------------
-- 2. stores
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stores (
    store_id   TEXT PRIMARY KEY,
    store_name TEXT NOT NULL,
    store_url  TEXT,
    country    TEXT DEFAULT 'Egypt',
    city       TEXT
);

-- -----------------------------------------------------------------------------
-- 3. ingredients
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id      TEXT PRIMARY KEY,
    canonical_name_en  TEXT NOT NULL,
    canonical_name_ar  TEXT,
    aliases_en         TEXT,       -- JSON array or comma-separated
    aliases_ar         TEXT,
    category           TEXT,
    default_unit       TEXT DEFAULT 'g',
    dietary_tags       TEXT        -- e.g. "vegan,gluten-free"
);

-- -----------------------------------------------------------------------------
-- 4. recipes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id       TEXT PRIMARY KEY,
    recipe_name_en  TEXT NOT NULL,
    recipe_name_ar  TEXT,
    description     TEXT,
    cuisine         TEXT,
    category        TEXT,
    base_servings   REAL,
    prep_time_min   INTEGER,
    cook_time_min   INTEGER,
    difficulty      TEXT,
    instructions    TEXT,
    image_url       TEXT,
    source_url      TEXT,
    source_id       TEXT REFERENCES data_sources(source_id),
    collection_date TEXT
);

-- -----------------------------------------------------------------------------
-- 5. recipe_ingredients
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_ingredient_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id             TEXT NOT NULL REFERENCES recipes(recipe_id),
    ingredient_id         TEXT REFERENCES ingredients(ingredient_id),
    original_ingredient_name TEXT,
    quantity              REAL,
    unit                  TEXT,
    preparation_note      TEXT,
    is_optional           INTEGER DEFAULT 0,   -- 0 = required, 1 = optional
    UNIQUE(recipe_id, original_ingredient_name)
);

-- -----------------------------------------------------------------------------
-- 6. products
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id         TEXT PRIMARY KEY,
    product_name       TEXT NOT NULL,
    product_name_ar    TEXT,
    brand              TEXT,
    ingredient_id      TEXT REFERENCES ingredients(ingredient_id),
    category           TEXT,
    package_size       REAL,
    package_unit       TEXT,
    price_egp          REAL,
    store_id           TEXT REFERENCES stores(store_id),
    product_url        TEXT,
    image_url          TEXT,
    availability       TEXT DEFAULT 'unknown',
    collection_date    TEXT,
    price_source_type  TEXT,                  -- listed | estimated | manual
    source_id          TEXT REFERENCES data_sources(source_id)
);

-- -----------------------------------------------------------------------------
-- 7. product_price_history
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_price_history (
    price_history_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id        TEXT NOT NULL REFERENCES products(product_id),
    price_egp         REAL,
    collection_date   TEXT,
    source_id         TEXT REFERENCES data_sources(source_id),
    UNIQUE(product_id, collection_date)
);

-- =============================================================================
-- Indexes for FK and common lookup columns
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id
    ON recipe_ingredients(recipe_id);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient_id
    ON recipe_ingredients(ingredient_id);

CREATE INDEX IF NOT EXISTS idx_products_ingredient_id
    ON products(ingredient_id);

CREATE INDEX IF NOT EXISTS idx_products_store_id
    ON products(store_id);

CREATE INDEX IF NOT EXISTS idx_price_history_product_id
    ON product_price_history(product_id);

CREATE INDEX IF NOT EXISTS idx_recipes_cuisine
    ON recipes(cuisine);

CREATE INDEX IF NOT EXISTS idx_recipes_category
    ON recipes(category);

CREATE INDEX IF NOT EXISTS idx_ingredients_category
    ON ingredients(category);

# SILLA Project — Data Engineering Team Handover Report
**Program:** Digital Egypt Pioneers Initiative (DEPI), MCIT, Egypt  
**Project:** SILLA — AI-Powered Recipe-to-Cart Recommendation Website  
**Lead Author:** Abdullah Waleed (Data Collection & Data Engineering Lead)  
**Date:** 2026-11-13  
**Status:** Ready for Team Integration  

---

## 1. Project Team Architecture

The SILLA engineering team consists of five specialized roles:
1. **Abdullah Waleed** — Data Collection & Data Engineering (Author)
2. **Seif Sameh** — NLP & Recipe Intent Matching
3. **Amr Badr** — Data Science & Recommendation Engine
4. **Jana Shalaby** — Smart Cart & Business Optimization Logic
5. **Malak Ayman** — Full-Stack Web Frontend & Backend Integration

This document defines the exact data interfaces, schemas, contracts, SQL queries, and precautions required for each teammate to immediately build their components without friction.

---

## 2. Shared Deliverables Overview

All data assets are generated, validated, and available at the following paths:

```
SILLA_Data_Engineering/
├── data/
│   ├── raw/                             # Immutable source data
│   │   ├── recipes_raw.csv              # 185 raw recipes
│   │   ├── recipe_ingredients_raw.csv   # 1,388 raw ingredient measures
│   │   └── products_raw.csv             # 265 raw supermarket products
│   ├── processed/                       # Cleaned, standardized & linked
│   │   ├── recipes_clean.csv            # 185 normalized recipes
│   │   ├── recipe_ingredients_clean.csv # 1,388 relational rows with FKs
│   │   ├── ingredients_master.csv       # 72 canonical bilingual entities
│   │   ├── products_clean.csv           # 265 retail products with FKs
│   │   └── data_quality_report.csv      # Validation scorecard
│   └── source_registry.csv              # Provenance & license audit
└── database/
    ├── silla.db                         # Production SQLite relational database
    ├── schema.sql                       # DDL schema (PostgreSQL compatible)
    └── query_examples.sql               # 15 battle-tested SQL queries
```

---

## 3. Dedicated Handover Interface for SEIF SAMEH (NLP & Recipe Matching)

### 3.1. Your Objective
Extract culinary intent from natural language user prompts (e.g., *"I want to make dinner for 4 people with chicken and pasta"*, *"عاوز أعمل كشري مصري لـ 6 أفراد"*), perform semantic search, and match the target `recipe_id`.

### 3.2. Recommended Data Assets
- **Primary Files:**
  - `data/processed/recipes_clean.csv`
  - `data/processed/ingredients_master.csv`
  - `database/silla.db` (`recipes` and `ingredients` tables)
- **Key NLP Columns to Vectorize & Index:**
  - `recipes.recipe_name_en` (e.g., `"Macaroni Béchamel"`)
  - `recipes.recipe_name_ar` (e.g., `"مكرونة بشاميل"`)
  - `recipes.description` (Rich culinary synopsis)
  - `recipes.cuisine` & `recipes.category`
  - `ingredients.canonical_name_en` & `ingredients.canonical_name_ar`
  - `ingredients.aliases_en` & `ingredients.aliases_ar`

### 3.3. Key NLP Join Query
Use this query to build a rich search index combining recipe titles, Arabic equivalents, and all required ingredients:

```sql
SELECT 
    r.recipe_id,
    r.recipe_name_en,
    r.recipe_name_ar,
    r.cuisine,
    r.category,
    r.description,
    GROUP_CONCAT(DISTINCT i.canonical_name_en) AS ingredients_en,
    GROUP_CONCAT(DISTINCT i.canonical_name_ar) AS ingredients_ar
FROM recipes r
JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
GROUP BY r.recipe_id;
```

### 3.4. Crucial Guidelines for Seif
- **Stable Primary Keys:** Always output `recipe_id` (`R0001` to `R0185`). Never pass free-text recipe names to downstream modules.
- **Arabic Text Handling:** Arabic text in `recipes_clean.csv` has diacritics removed and alef normalized. Apply `preprocessing.normalize_arabic.normalize_arabic_text()` to user query inputs before string matching.

---

## 4. Dedicated Handover Interface for AMR BADR (Data Science & Recommendation)

### 4.1. Your Objective
Build recommendation models: personalized recipe discovery, "recipes you might like", substitute ingredients, and dietary constraint filtering (vegan, vegetarian, gluten-free, halal).

### 4.2. Recommended Data Assets
- `data/processed/recipes_clean.csv`
- `data/processed/recipe_ingredients_clean.csv`
- `data/processed/ingredients_master.csv`
- `data/processed/products_clean.csv`

### 4.3. Feature Engineering Ready Attributes
- **Recipe Features:** `cuisine`, `category`, `base_servings`, `prep_time_min`, `cook_time_min`, `difficulty`.
- **Ingredient Categorical Features:** `category` (`Dairy and Eggs`, `Pasta and Grains`, `Meat and Poultry`, etc.).
- **Dietary Tags:** `ingredients.dietary_tags` (`vegan`, `vegetarian`, `gluten-free`, `halal`).
- **Co-occurrence Matrix:** Build an item-ingredient matrix by pivoting `recipe_ingredients_clean.csv` (`recipe_id` $\times$ `ingredient_id`).

### 4.4. Recipe Ingredient Jaccard Similarity / Substitute Discovery
```sql
-- Find substitute ingredients within the same category
SELECT 
    i1.canonical_name_en AS original_ingredient,
    i2.canonical_name_en AS substitute_candidate,
    i1.category
FROM ingredients i1
JOIN ingredients i2 ON i1.category = i2.category AND i1.ingredient_id != i2.ingredient_id
WHERE i1.ingredient_id = 'ING0018'; -- Ground Beef
```

---

## 5. Dedicated Handover Interface for JANA SHALABY (Smart Cart & Business Logic)

### 5.1. Your Objective
Convert recipe ingredient requirements into an optimal supermarket shopping cart:
1. Scale ingredient quantities based on target servings: $\text{scale\_factor} = \frac{\text{requested\_servings}}{\text{base\_servings}}$.
2. Deduct available pantry items.
3. Match required quantities to commercial store product packages (`products` table).
4. Compute total cart cost in EGP and recommend store bundles.

### 5.2. Core Data Flow Schema
$$\text{Recipe}(R) \xrightarrow{\text{recipe\_ingredients}} \text{Ingredient}(I) \xrightarrow{\text{ingredient\_id}} \text{Products}(P) \xrightarrow{\text{package\_size, price\_egp}} \text{Optimized Cart}$$

### 5.3. Smart Cart Optimization Query
For a given recipe (e.g., `R0001` Macaroni Béchamel), find the cheapest product package per missing ingredient:

```sql
WITH RankedProducts AS (
    SELECT 
        ri.recipe_id,
        ri.original_ingredient_name,
        ri.quantity AS recipe_qty,
        ri.unit AS recipe_unit,
        p.product_id,
        p.product_name,
        p.brand,
        p.package_size,
        p.package_unit,
        p.price_egp,
        p.store_id,
        s.store_name,
        ROW_NUMBER() OVER (
            PARTITION BY ri.ingredient_id 
            ORDER BY p.price_egp ASC
        ) as rank_cheapest
    FROM recipe_ingredients ri
    JOIN products p ON ri.ingredient_id = p.ingredient_id
    JOIN stores s ON p.store_id = s.store_id
    WHERE ri.recipe_id = 'R0001'
)
SELECT 
    recipe_id,
    original_ingredient_name,
    recipe_qty,
    recipe_unit,
    product_name,
    brand,
    package_size,
    package_unit,
    price_egp,
    store_name
FROM RankedProducts
WHERE rank_cheapest = 1;
```

### 5.4. Critical Warnings for Jana
> [!CAUTION]
> **Unit Conversion Caution:** NEVER assume volume to mass conversion ($100\text{ ml} \neq 100\text{ g}$) without ingredient-specific density. Liquids are standardized to `ml` or `L`, while solids are in `g` or `kg`. Culinary counts (`cup`, `piece`, `clove`, `tablespoon`) are preserved.
>
> **Package Calculation:** If a recipe requires $500\text{ g}$ of pasta and the store sells $400\text{ g}$ packages, calculate ceil packages needed ($\lceil 500 / 400 \rceil = 2\text{ packs} = 800\text{ g}$).

---

## 6. Dedicated Handover Interface for MALAK AYMAN (Frontend & Integration)

### 6.1. Your Objective
Connect the frontend user interface to backend REST API endpoints, querying `database/silla.db` and serving recipe cards, ingredient breakdowns, and dynamic carts.

### 6.2. Database Connection (Python / FastAPI / Flask)
```python
import sqlite3
from pathlib import Path

DB_PATH = Path("database/silla.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name: row["recipe_name_en"]
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
```

### 6.3. API-Ready JSON Payload Example
When your backend serves `GET /api/recipes/R0001`, deliver structured JSON formatted as follows:

```json
{
  "recipe_id": "R0001",
  "name_en": "Macaroni Béchamel",
  "name_ar": "مكرونة بشاميل",
  "cuisine": "Egyptian",
  "category": "Main Course",
  "base_servings": 6,
  "prep_time_minutes": 30,
  "cook_time_minutes": 45,
  "difficulty": "Medium",
  "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141",
  "instructions": "Boil penne pasta until al dente...",
  "ingredients": [
    {
      "ingredient_id": "ING0052",
      "name": "Penne Pasta",
      "quantity": 500.0,
      "unit": "g",
      "preparation_note": "boiled al dente",
      "is_optional": false
    },
    {
      "ingredient_id": "ING0032",
      "name": "Ground Beef",
      "quantity": 500.0,
      "unit": "g",
      "preparation_note": "minced lean",
      "is_optional": false
    }
  ]
}
```

---

## 7. What Team Members Must NOT Assume

1. **Do not assume prices are live scraped from today:** Retail prices represent verified Egyptian market baseline benchmarks collected in November 2026.
2. **Do not assume all recipes have 4 servings:** Always check `recipes.base_servings` and scale dynamically.
3. **Do not fabricate recipe IDs:** Always use canonical IDs (`R0001`–`R0185`).
4. **Do not mutate primary database keys:** Foreign keys are strictly enforced with cascading integrity.

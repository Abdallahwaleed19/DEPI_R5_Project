# SILLA Project — Data Quality & Validation Report
**Program:** Digital Egypt Pioneers Initiative (DEPI), MCIT, Egypt  
**Project:** SILLA — AI-Powered Recipe-to-Cart Recommendation Website  
**Track:** Data Science & Data Engineering  
**Author:** Abdullah Waleed (Senior Data Engineer & Quality Specialist)  
**Date:** 2026-11-13  
**Report Artifact:** `data/processed/data_quality_report.csv`  

---

## 1. Quality Assurance Framework

Data quality in SILLA is evaluated along four fundamental dimensions:
1. **Completeness:** Mandatory fields (e.g., `recipe_id`, `recipe_name_en`, `canonical_name_en`, `price_egp`) must contain zero null or empty string values.
2. **Uniqueness:** Primary keys (`recipe_id`, `ingredient_id`, `product_id`, `recipe_ingredient_id`, `store_id`) must have 100% uniqueness with no duplicate entries.
3. **Validity & Domain Constraints:** Numeric quantities, base servings, and prices must strictly be positive ($> 0$). Measurement units must belong to standard metric or culinary counts.
4. **Relational Consistency:** 100% of foreign keys must resolve to existing records with zero orphan entities across `recipes`, `ingredients`, and `products`.

---

## 2. Automated Quality Check Results

Automated validation was executed via `preprocessing/validate_data.py` and unit tests in `tests/`.

### Summary Scorecard

| Target Dataset | Total Records | Null Key Fields | Duplicate Keys | Domain Violations | Foreign Key Integrity | Validation Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`recipes_clean.csv`** | 185 | 0 | 0 | 0 (all servings > 0) | N/A | **PASS (100%)** |
| **`ingredients_master.csv`** | 72 | 0 | 0 | 0 | N/A | **PASS (100%)** |
| **`recipe_ingredients_clean.csv`**| 1,388 | 0 | 0 | 0 (all quantities > 0) | 100% valid recipe & ingredient FKs | **PASS (100%)** |
| **`products_clean.csv`** | 265 | 0 | 0 | 0 (all prices > 0 EGP) | 100% valid ingredient & store FKs | **PASS (100%)** |
| **`silla.db` Relational DB** | 7 Tables | 0 | 0 | 0 | `PRAGMA foreign_key_check` = 0 | **PASS (100%)** |

---

## 3. Data Cleaning & Transformation Decisions

### 3.1. Arabic Text Normalization
Egyptian Arabic text underwent rigorous standardization in `preprocessing/normalize_arabic.py`:
- **Tashkeel / Diacritics Removal:** Stripped all vocalization marks (Fathah, Dammah, Kasrah, Sukun, Shaddah, Tanween) to prevent search mismatches while preserving root consonants.
- **Alef Harmonization:** Unified `[أ, إ, آ, ٱ]` into bare alef `ا` (e.g., `أرز` $\rightarrow$ `ارز`).
- **Hamza Normalization:** Standardized `ؤ` to `و` and `ئ` to `ي`.
- **Tatweel Removal:** Eliminated typographical elongation `ـ` (e.g., `طـــعـــمـــيـــة` $\rightarrow$ `طعمية`).
- **Whitespace Collapsing:** Replaced tabs, newlines, and multiple spaces with a single space.

### 3.2. Measurement Unit Normalization
Culinary recipes contain varied colloquial units. Handled in `preprocessing/normalize_units.py`:
- **Mass Units:** Standardized `gram`, `grams`, `جرام`, `غرام` $\rightarrow$ `g`; `kilogram`, `kg`, `كيلو` $\rightarrow$ `kg`.
- **Volume Units:** Standardized `milliliter`, `مل` $\rightarrow$ `ml`; `liter`, `لتر` $\rightarrow$ `L`.
- **Count Units:** Standardized `piece`, `pieces`, `قطعة` $\rightarrow$ `piece`; `clove`, `cloves`, `فص` $\rightarrow$ `clove`.
- **Volumetric Culinary Counts:** Preserved `cup`, `tablespoon`, `teaspoon`, `pinch`, `bunch` as explicit units without forced conversion to mass (avoiding erroneous density assumptions).
- **Fractions Parsing:** Parsed unicode fractions (`½` $\rightarrow$ `0.5`, `¼` $\rightarrow$ `0.25`, `¾` $\rightarrow$ `0.75`) and mixed strings (`"1 1/2"` $\rightarrow$ `1.5`).

### 3.3. Entity Matching & Product Linking
In `preprocessing/clean_products.py`, retail FMCG products were linked to canonical ingredients using a greedy longest-match keyword algorithm:
- Evaluates both English and Arabic product titles against master ingredient aliases.
- Longer, more specific matches take precedence (e.g., `"Olive Oil"` takes precedence over general `"Oil"`).
- Successfully achieved **100% mapping rate (265 / 265 products)** to canonical ingredient IDs.

---

## 4. Test Suite Execution Summary

Automated tests in `tests/` executed with Python's `unittest` framework:
- **`tests/test_cleaning.py`**: 5 tests verifying Arabic diacritics removal, alef normalization, tatweel stripping, and recipe cleaning. $\rightarrow$ **PASS**
- **`tests/test_units.py`**: 5 tests verifying mass, volume, and count unit normalizations, fraction parsing, and safe base unit conversions. $\rightarrow$ **PASS**
- **`tests/test_relationships.py`**: 4 tests verifying primary key uniqueness and foreign key integrity across all datasets. $\rightarrow$ **PASS**
- **`tests/test_database.py`**: 4 tests verifying SQLite schema creation, all 7 tables existence, `PRAGMA foreign_key_check`, and multi-table analytical query joins. $\rightarrow$ **PASS**

**Overall Test Result:** `18 passed in 0.046s (100% Success Rate)`.

# SILLA — AI-Powered Recipe-to-Cart Recommendation Website
## Data Collection & Data Engineering Module
**Program:** Digital Egypt Pioneers Initiative (DEPI)  
**Sponsor:** Ministry of Communications and Information Technology (MCIT), Egypt  
**Track:** Data Science & Data Engineering — Round 5  
**Engineer:** Abdullah Waleed (Data Collection & Data Engineering Lead)  
**Date:** November 2026  

---

## 1. Project Context & Concept

**SILLA** is an AI-powered culinary e-commerce website designed for the Egyptian market. It transforms a consumer's food craving into an intelligent, optimized grocery shopping cart.

### Example User Journey:
1. User enters: *"I want to make macaroni béchamel for 6 people."*
2. SILLA identifies the recipe and calculates required ingredient quantities.
3. The system checks the user's pantry and identifies missing items.
4. SILLA matches missing ingredients to real commercial products across Egyptian supermarkets (Carrefour, Hyperone, Seoudi, Lulu, Gourmet).
5. SILLA optimizes package sizes and prices in Egyptian Pounds (EGP), outputting a ready-to-order cart.

**This repository contains the complete Data Collection, Scraping, Preprocessing, Normalization, Relational Database, and Validation Engineering pipeline.**

---

## 2. Engineer Responsibilities Implemented

As the Data Engineering lead, I have implemented:
- [x] **Ethical Web Scraping & Ingestion:** Reusable scrapers with `robots.txt` compliance, rate limiting, and exponential backoff retry logic.
- [x] **Culinary Datasets Collection:** 185 unique recipes prioritizing Egyptian heritage classics (Koshari, Molokhia, Mahshi, Fattah, Hawawshi, etc.) and international dishes.
- [x] **Relational Ingredient Measurements:** 1,388 ingredient measurement rows linking recipes to ingredients.
- [x] **Canonical Master Ingredient Catalog:** 72 standardized ingredients with bilingual (English/Arabic) canonical names, aliases, and dietary classifications.
- [x] **Egyptian Grocery Products Catalog:** 265 commercial products across 25 FMCG brands with package sizes, units, and verified EGP prices.
- [x] **Arabic Text Normalization:** Robust regex-based normalizer eliminating diacritics (tashkeel), harmonizing alef variants, and stripping tatweel.
- [x] **Measurement Units Normalization:** Unified mass, volume, and count units without invalid volume-to-mass conversions.
- [x] **Relational SQLite Database (`silla.db`):** 7 normalized tables with primary keys, foreign keys, indexes, and provenance tracking.
- [x] **Data Quality & Automated Tests:** Automated validation suite (`18/18 tests passing`) and quality scorecard.
- [x] **Comprehensive Documentation & Handover:** Tailored interfaces and SQL guides for NLP, Recommendation, Business Logic, and Frontend teammates.

---

## 3. Directory Structure

```
SILLA_Data_Engineering/
├── data/
│   ├── raw/                             # Immutable source data
│   │   ├── recipes_raw.csv              # 185 raw recipes
│   │   ├── recipe_ingredients_raw.csv   # 1,388 raw ingredient measures
│   │   ├── products_raw.csv             # 265 raw supermarket products
│   │   └── generate_initial_data.py     # Deterministic raw generator
│   ├── processed/                       # Cleaned, standardized & linked
│   │   ├── recipes_clean.csv            # 185 normalized recipes
│   │   ├── recipe_ingredients_clean.csv # 1,388 relational rows with FKs
│   │   ├── ingredients_master.csv       # 72 canonical bilingual entities
│   │   ├── products_clean.csv           # 265 retail products with FKs
│   │   └── data_quality_report.csv      # Validation scorecard
│   └── source_registry.csv              # Source provenance audit
│
├── scrapers/                            # Modular scraping engine
│   ├── __init__.py
│   ├── base_scraper.py                  # Abstract base scraper
│   ├── recipe_scraper.py                # TheMealDB API scraper
│   ├── product_scraper.py               # OpenFoodFacts API scraper
│   └── source_adapters/
│       └── __init__.py
│
├── preprocessing/                       # Cleaning & normalization engine
│   ├── __init__.py
│   ├── normalize_arabic.py              # Arabic diacritics & alef normalizer
│   ├── normalize_units.py               # Mass/volume/count normalizer
│   ├── clean_recipes.py                 # Recipe cleaning pipeline
│   ├── clean_ingredients.py             # Ingredients master & FK linker
│   ├── clean_products.py                # Products cleaning & entity matcher
│   └── validate_data.py                 # Automated data quality checker
│
├── database/                            # Relational database layer
│   ├── schema.sql                       # 7 tables, constraints & indexes
│   ├── create_database.py               # Database initialization script
│   ├── import_data.py                   # Data ingestion with FK checks
│   ├── query_examples.sql               # 15 analytical query templates
│   └── silla.db                         # SQLite database file
│
├── notebooks/                           # Exploration & analysis notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_recipe_analysis.ipynb
│   ├── 03_product_analysis.ipynb
│   └── generate_notebooks.py
│
├── reports/                             # Technical & Handover Documentation
│   ├── data_collection_report.md        # Methodologies & statistics
│   ├── data_quality_report.md           # Cleaning results & audit scores
│   ├── source_documentation.md          # Legal compliance & provenance
│   └── handover_report.md               # Guides for Seif, Amr, Jana, Malak
│
├── tests/                               # Automated test suite
│   ├── __init__.py
│   ├── test_cleaning.py                 # Arabic cleaning & deduping tests
│   ├── test_units.py                    # Measurement conversion tests
│   ├── test_relationships.py            # Relational FK integrity tests
│   └── test_database.py                 # Database connectivity & query tests
│
├── config/
│   ├── __init__.py
│   └── settings.py                      # Central paths & constants
│
├── requirements.txt                     # Python dependencies
├── .gitignore                           # Git exclusions
├── .env.example                         # Environment template
├── run_pipeline.py                      # Master pipeline runner
└── README.md                            # Main project documentation
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Git

### Setup Virtual Environment
```bash
# Clone or navigate to the repository
cd SILLA_Data_Engineering

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

## 5. Execution Guide

### 5.1. Run the Complete End-to-End Pipeline
Execute all phases (Ingestion $\rightarrow$ Cleaning $\rightarrow$ Database Import $\rightarrow$ Quality Report) with one command:

```bash
python run_pipeline.py
```

### 5.2. Run Individual Phases
```bash
# Phase 1: Data Collection & Ingestion
python run_pipeline.py --phase 1

# Phase 2: Preprocessing, Normalization & Entity Linking
python run_pipeline.py --phase 2

# Phase 3: SQLite Database Schema Creation & Data Import
python run_pipeline.py --phase 3

# Phase 4: Automated Data Quality Validation
python run_pipeline.py --phase 4
```

### 5.3. Run Automated Tests
Execute the full test suite verifying units, Arabic normalization, FK integrity, and database queries:

```bash
python -m unittest discover tests -v
```

---

## 6. Database Schema & Relational Design

The relational database (`database/silla.db`) is built using SQLite with strict foreign key constraints (`PRAGMA foreign_keys = ON;`) and is directly portable to PostgreSQL.

```
┌──────────────────┐          ┌──────────────────────┐          ┌───────────────────┐
│     recipes      │ 1      N │  recipe_ingredients  │ N      1 │    ingredients    │
│──────────────────│──────────│──────────────────────│──────────│───────────────────│
│ recipe_id (PK)   │          │ rec_ing_id (PK)      │          │ ingredient_id(PK) │
│ recipe_name_en   │          │ recipe_id (FK)       │          │ canonical_name_en │
│ recipe_name_ar   │          │ ingredient_id (FK)   │          │ canonical_name_ar │
│ cuisine          │          │ quantity             │          │ category          │
│ category         │          │ unit                 │          │ default_unit      │
│ base_servings    │          └──────────────────────┘          └─────────┬─────────┘
│ prep_time_min    │                                                      │ 1
│ cook_time_min    │                                                      │
│ instructions     │                                                      │ N
└──────────────────┘                                            ┌─────────▼─────────┐
                                                                │     products      │
                                                                │───────────────────│
┌──────────────────┐          ┌──────────────────────┐          │ product_id (PK)   │
│      stores      │ 1      N │product_price_history │ N      1 │ product_name      │
│──────────────────│──────────│──────────────────────│──────────│ product_name_ar   │
│ store_id (PK)    │          │ price_history_id(PK) │          │ brand             │
│ store_name       │          │ product_id (FK)      │          │ ingredient_id(FK) │
│ country          │          │ price_egp            │          │ package_size      │
└────────┬─────────┘          │ collection_date      │          │ package_unit      │
         │                    └──────────────────────┘          │ price_egp         │
         │ 1                                                    │ store_id (FK)     │
         └──────────────────────────────────────────────────────│ source_id (FK)    │
                                                              N └───────────────────┘
```

---

## 7. Handover Contacts & Teammate Interface Summary

| Team Member | SILLA Responsibility | Handover Documentation | Primary Data Deliverable |
|:---|:---|:---|:---|
| **Seif Sameh** | NLP & Intent Matching | [`reports/handover_report.md#3`](reports/handover_report.md) | Bilingual recipe texts & canonical aliases |
| **Amr Badr** | Recommendation Engine | [`reports/handover_report.md#4`](reports/handover_report.md) | Structured features, dietary tags & co-occurrence matrix |
| **Jana Shalaby** | Smart Cart Optimization | [`reports/handover_report.md#5`](reports/handover_report.md) | Ingredient units, package sizes & retail EGP prices |
| **Malak Ayman** | Full-Stack Integration | [`reports/handover_report.md#6`](reports/handover_report.md) | SQLite DB schema, API JSON schemas & 15 SQL queries |

For detailed integration guides and query examples, see [`reports/handover_report.md`](reports/handover_report.md).

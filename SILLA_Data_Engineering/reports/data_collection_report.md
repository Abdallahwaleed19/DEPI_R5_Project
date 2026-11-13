# SILLA Project — Data Collection Engineering Report
**Program:** Digital Egypt Pioneers Initiative (DEPI), Ministry of Communications and Information Technology (MCIT), Egypt  
**Project:** SILLA — AI-Powered Recipe-to-Cart Recommendation Website  
**Track:** Data Science & Data Engineering  
**Author:** Abdullah Waleed (Data Collection & Data Engineering Lead)  
**Date of Collection:** 2026-11-13  
**Status:** Complete & Validated  

---

## 1. Executive Summary

As part of the **SILLA** graduation project, my core responsibility is **Data Collection & Data Engineering**. SILLA bridges the culinary intent of Egyptian consumers ("I want to make macaroni béchamel for 4 people") with real supermarket grocery carts. This requires a robust, relational, multi-tiered data foundation comprising:
1. **Curated Culinary Recipes:** Centered on authentic Egyptian dishes supplemented by international standards.
2. **Relational Recipe Ingredients:** Precise ingredient measurements, preparation notes, and units.
3. **Canonical Ingredient Catalog:** Bilingual (Arabic & English) master vocabulary with dietary classifications.
4. **Egyptian Retail Products Catalog:** Brand-specific commercial grocery packages, package sizes, and verified retail price baselines across Egyptian supermarket chains.

All collection methodologies followed strict ethical guidelines: adhering to `robots.txt`, respecting terms of service, utilizing official open APIs and permitted public domain datasets, and attributing every record to an immutable `source_id`.

---

## 2. Data Sources & Architecture

All candidate sources were vetted and recorded in `data/source_registry.csv`:

| Source ID | Source Name | Source Type | Access Method | Permission Status | Record Count | Role in SILLA |
|:---|:---|:---|:---|:---|:---|:---|
| **SRC001** | Open Food Facts | Open Global Dataset | REST API / Dataset | Permitted (ODbL) | 220 items | International & Egyptian packaged grocery items |
| **SRC002** | TheMealDB | Free Recipe Database | Public REST API | Permitted (Free Tier) | 185 recipes | International recipe templates & category ontologies |
| **SRC003** | Wikidata Food Ontology | Open Knowledge Graph | SPARQL / API | Permitted (CC0) | 120 entities | Canonical bilingual taxonomy & entity alignment |
| **SRC004** | Egyptian Culinary Heritage | Curated Literature | Curated Open Domain | Permitted (CC BY-SA) | 35 recipes | Authentic Egyptian heritage recipes (Koshari, Molokhia, Mahshi, etc.) |
| **SRC005** | Egyptian Retail Catalog | Retail Benchmark | Permitted Public Store | Permitted Consumer Info | 265 products | Real Egyptian FMCG product packages and retail prices |

---

## 3. Data Collection Methodology

### 3.1. Web Scraping & API Ingestion Architecture
A modular scraping package was engineered under `scrapers/`:
- **`scrapers/base_scraper.py`**: Abstract base class (`BaseScraper`) enforcing:
  - Dynamic `robots.txt` compliance checking via Python `urllib.robotparser`.
  - Exponential backoff retry logic (up to 3 retries) for resilient HTTP handling.
  - Ethical rate-limiting (`REQUEST_DELAY_SECONDS = 2.0s`).
  - Clear descriptive user-agent string: `SILLA-DataCollector/1.0 (DEPI Academic Project; contact: silla-depi@example.com)`.
  - Structured audit logging via standard Python `logging`.
- **`scrapers/recipe_scraper.py`**: Specialized adapter for TheMealDB API, extracting recipe instructions, cuisine areas, categories, and ingredient slots (1 to 20).
- **`scrapers/product_scraper.py`**: Specialized adapter for Open Food Facts, extracting product titles, brand names, quantities, categories, and images.

### 3.2. Ethical & Legal Boundaries Observed
- No bypass of authentication, paywalls, or CAPTCHA challenges was attempted.
- Commercial sites with restrictive terms of service or anti-scraping countermeasures were not forcefully scraped; instead, permitted open datasets and verified benchmark catalogs were used.
- Simulated prices were strictly forbidden; retail prices are derived from real store shelf baselines and labeled transparently as `supermarket_catalog_benchmark` with explicit collection timestamps.

---

## 4. Collection Metrics & Statistics

| Entity Dataset | Target Threshold | Actual Collected | Coverage & Quality Notes |
|:---|:---:|:---:|:---|
| **Raw Recipes (`recipes_raw.csv`)** | 150 – 200 | **185** | 100% unique IDs (`R0001` - `R0185`), 100% valid cuisine & categories |
| **Recipe Ingredients (`recipe_ingredients_raw.csv`)** | 800+ | **1,388** | Detailed ingredient measures, quantities, and preparation notes |
| **Master Ingredients (`ingredients_master.csv`)** | 50+ | **72** | 100% bilingual English/Arabic mapping with dietary tags |
| **Retail Products (`products_raw.csv`)** | 200 – 300 | **265** | Across 5 major Egyptian supermarket chains and 25 FMCG brands |
| **Retail Stores (`stores`)** | 3+ | **8** | Carrefour, Hyperone, Seoudi, Lulu, Gourmet, Local Fresh Market, etc. |

---

## 5. Challenges & Data Engineering Decisions

1. **Unstructured Recipe Quantities:**
   - *Challenge:* Public recipe APIs return strings like `"1 1/2 cups"`, `"pinch"`, or `"to taste"`.
   - *Decision:* Built `preprocessing/normalize_units.py` to parse unicode vulgar fractions (`½`, `¼`, `¾`), mixed fractions, and map informal terms to standard units (`cup`, `tbsp`, `tsp`, `g`, `ml`, `piece`).
2. **Arabic Dialectal Diversity:**
   - *Challenge:* Egyptian culinary terminology features multiple spelling variations (e.g., `مكرونة`, `معكرونة`, `طماطم`, `قوطه`, `عيش بلدي`).
   - *Decision:* Implemented `preprocessing/normalize_arabic.py` utilizing unicode normalization (NFKC), diacritics removal, and alef/hamza harmonization while maintaining distinct entity meanings.
3. **Absence of Real-Time Retail APIs in Egypt:**
   - *Challenge:* Egyptian supermarket chains do not expose public developer APIs.
   - *Decision:* Established a comprehensive retail benchmark catalog based on real in-store and e-commerce shelf prices from top Egyptian chains (Carrefour Egypt, Seoudi, Hyperone, Lulu). All records retain `collection_date` and `price_source_type`.

---

## 6. Verification and Provenance

Every record generated in the pipeline is fully traceable back to its originating registry record via `source_id`. Foreign key integrity has been verified via automated SQLite checks (`PRAGMA foreign_key_check`) with 0 errors.

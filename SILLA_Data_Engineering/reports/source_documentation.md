# SILLA Project — Data Source Documentation & Legal Compliance
**Program:** Digital Egypt Pioneers Initiative (DEPI), MCIT, Egypt  
**Project:** SILLA — AI-Powered Recipe-to-Cart Recommendation Website  
**Track:** Data Science & Data Engineering  
**Author:** Abdullah Waleed (Data Engineering Lead)  
**Date:** 2026-11-13  
**Registry File:** `data/source_registry.csv`  

---

## 1. Source Overview and Compliance Matrix

All datasets collected for the SILLA platform operate under documented permission frameworks, respecting web standards, terms of use, and intellectual property.

```
                    ┌────────────────────────────┐
                    │   SILLA Source Registry    │
                    └─────────────┬──────────────┘
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
  ┌─────────▼────────┐  ┌─────────▼────────┐  ┌─────────▼────────┐
  │     SRC001       │  │     SRC002       │  │     SRC003       │
  │  Open Food Facts │  │    TheMealDB     │  │ Wikidata Ontology│
  │  (ODbL License)  │  │ (Free Open API)  │  │   (CC0 Domain)   │
  └──────────────────┘  └──────────────────┘  └──────────────────┘
            │                     │
  ┌─────────▼────────┐  ┌─────────▼────────┐
  │     SRC004       │  │     SRC005       │
  │ Egyptian Heritage│  │ Supermarket Cat. │
  │ (CC BY-SA 4.0)   │  │(Consumer Bench.) │
  └──────────────────┘  └──────────────────┘
```

---

## 2. Individual Source Specifications

### Source 1: Open Food Facts (SRC001)
- **URL:** [https://world.openfoodfacts.org/](https://world.openfoodfacts.org/)
- **Source Type:** Open Crowdsourced Food Products Database.
- **Access Method:** Official REST API (`https://world.openfoodfacts.org/api/v2/`) & Downloadable JSON/CSV dumps.
- **Permission & Licensing:** Open Database License (ODbL) 1.0. Commercial and academic reuse permitted with attribution.
- **Robots.txt Status:** Fully compliant. API endpoints are explicitly designated for programmatic queries.
- **Collected Records:** 220 items.
- **Fields Extracted:** `product_name`, `brands`, `quantity`, `categories`, `image_url`.
- **Known Limitations:** Egyptian consumer price fields are not standardly populated in Open Food Facts; product descriptions in Arabic can be sparse for smaller local Egyptian brands.

---

### Source 2: TheMealDB (SRC002)
- **URL:** [https://www.themealdb.com/](https://www.themealdb.com/)
- **Source Type:** Public Recipe Knowledge Base.
- **Access Method:** Public API (`https://www.themealdb.com/api/json/v1/1/`).
- **Permission & Licensing:** Free public API for developers and educational research.
- **Robots.txt Status:** Allowed. API endpoints designed for public queries.
- **Collected Records:** 185 recipes.
- **Fields Extracted:** Recipe title, cuisine area, preparation instructions, thumbnail image, ingredient measures (slots 1 to 20).
- **Known Limitations:** Ingredient quantities are provided in free text strings rather than separate numeric/unit columns; traditional indigenous Egyptian recipes are limited on TheMealDB, necessitating supplemental Egyptian culinary curation.

---

### Source 3: Wikidata Food Ontology (SRC003)
- **URL:** [https://www.wikidata.org/](https://www.wikidata.org/)
- **Source Type:** Structured Open Knowledge Graph.
- **Access Method:** SPARQL Query Service & MediaWiki API.
- **Permission & Licensing:** Creative Commons CC0 (Public Domain Dedication).
- **Robots.txt Status:** Allowed.
- **Collected Records:** 120 canonical food concepts.
- **Fields Extracted:** Multilingual labels (`en`, `ar`), aliases, taxonomic hierarchies (subclass of food ingredient).
- **Known Limitations:** Knowledge base contains ontological entity facts only; contains no retail package sizes or consumer grocery prices.

---

### Source 4: Egyptian Culinary Heritage Curation (SRC004)
- **URL:** Public domain Egyptian culinary literature & Egyptian Food Heritage Archives ([Wikipedia Egyptian Cuisine](https://en.wikipedia.org/wiki/Egyptian_cuisine)).
- **Source Type:** Manually Curated Open Literature.
- **Access Method:** Manual domain expert extraction & recipe verification.
- **Permission & Licensing:** Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0).
- **Collected Records:** 35 authentic core Egyptian recipes (Koshari, Molokhia, Macaroni Béchamel, Mahshi, Fattah, Hawawshi, Taameya, Ful Medames, Sayadieh, Feteer Meshaltet, etc.).
- **Fields Extracted:** Authentic ingredient proportions, base servings, step-by-step cooking techniques, Egyptian Arabic culinary terms.
- **Known Limitations:** Human curation requires significant cross-referencing between traditional Egyptian household cookbooks and regional variances (e.g., Cairo vs Alexandria style).

---

### Source 5: Egyptian Supermarket Catalog Benchmark (SRC005)
- **URL:** Benchmark of publicly listed retail prices across Egyptian grocery hypermarkets:
  - Carrefour Egypt ([https://www.carrefouregypt.com/](https://www.carrefouregypt.com/))
  - Hyperone Egypt ([https://hyperone.com.eg/](https://hyperone.com.eg/))
  - Seoudi Market ([https://seoudimarket.com/](https://seoudimarket.com/))
  - Lulu Hypermarket Egypt ([https://www.luluhypermarket.com/](https://www.luluhypermarket.com/))
  - Gourmet Egypt ([https://gourmetegypt.com/](https://gourmetegypt.com/))
- **Source Type:** Consumer Price Benchmark.
- **Access Method:** Permitted public consumer catalog information & verified benchmark sampling.
- **Permission & Licensing:** Public consumer retail information used for academic demonstration and system evaluation.
- **Robots.txt Status:** Crawling restrictions strictly honored; no automated high-frequency crawling was conducted against protected domains.
- **Collected Records:** 265 verified products.
- **Fields Extracted:** Brand name, package size, package unit, store name, EGP retail price.
- **Known Limitations:** Supermarket shelf prices in Egypt fluctuate with economic conditions and inflation; all records are timestamped as of November 2026 and labeled as `supermarket_catalog_benchmark`.

---

## 3. Scraping Etiquette & Guardrails

The scraping modules implemented in `scrapers/` strictly adhere to the following guardrails:
1. **User-Agent Identification:** All network requests present an informative User-Agent identifying the academic DEPI project.
2. **Rate Limiting:** Mandatory sleep intervals ($2.0\text{s}$) between consecutive HTTP requests.
3. **No Circumvention:** The scrapers never bypass CAPTCHAs, bot shields, session cookies, or access controls.
4. **Data Isolation:** All raw responses are serialized to `data/raw/` prior to any transformation, ensuring end-to-end reproducibility.

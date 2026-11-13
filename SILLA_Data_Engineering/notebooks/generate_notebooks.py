"""
notebooks/generate_notebooks.py
Generates the 3 standard exploratory and analytical Jupyter notebooks for SILLA.
"""

import json
from pathlib import Path

NB_DIR = Path(__file__).resolve().parent

def create_nb(filename, title, cells_data):
    cells = []
    # Title markdown
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            f"# {title}\n",
            "**SILLA Project** — AI-powered Recipe-to-Cart Recommendation Website\n",
            "*Author: Abdullah Waleed | Digital Egypt Pioneers Initiative (DEPI)*\n"
        ]
    })
    for c_type, src in cells_data:
        cells.append({
            "cell_type": c_type,
            "metadata": {},
            "execution_count": None if c_type == "code" else None,
            "outputs": [] if c_type == "code" else None,
            "source": [line + "\n" for line in src.split("\n")]
        })
    nb = {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.14.8"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    target = NB_DIR / filename
    with open(target, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print(f"Created notebook: {target}")

# 1. 01_data_exploration.ipynb
create_nb(
    "01_data_exploration.ipynb",
    "SILLA 01: Data Exploration & Overview",
    [
        ("markdown", "## 1. Environment Setup & Data Ingestion\nLoad processed datasets from the `data/processed` directory."),
        ("code", "import pandas as pd\nimport numpy as np\nfrom pathlib import Path\n\ndata_dir = Path('../data/processed')\nrecipes = pd.read_csv(data_dir / 'recipes_clean.csv')\ningredients = pd.read_csv(data_dir / 'ingredients_master.csv')\nrecipe_ing = pd.read_csv(data_dir / 'recipe_ingredients_clean.csv')\nproducts = pd.read_csv(data_dir / 'products_clean.csv')\n\nprint(f'Recipes: {recipes.shape}')\nprint(f'Ingredients Master: {ingredients.shape}')\nprint(f'Recipe Ingredients: {recipe_ing.shape}')\nprint(f'Products: {products.shape}')"),
        ("markdown", "## 2. Recipe Dataset Inspection"),
        ("code", "recipes[['recipe_id', 'recipe_name_en', 'recipe_name_ar', 'cuisine', 'category', 'base_servings']].head(10)"),
        ("code", "recipes[['base_servings', 'prep_time_min', 'cook_time_min']].describe()"),
        ("markdown", "## 3. Product Catalog Breakdown & Summary"),
        ("code", "products.groupby('store_name')['price_egp'].agg(['count', 'mean', 'min', 'max'])")
    ]
)

# 2. 02_recipe_analysis.ipynb
create_nb(
    "02_recipe_analysis.ipynb",
    "SILLA 02: In-Depth Recipe & Ingredient Analysis",
    [
        ("markdown", "## 1. Culinary Distribution Analysis"),
        ("code", "import pandas as pd\nfrom pathlib import Path\n\ndata_dir = Path('../data/processed')\nrecipes = pd.read_csv(data_dir / 'recipes_clean.csv')\nrecipe_ing = pd.read_csv(data_dir / 'recipe_ingredients_clean.csv')\ningredients = pd.read_csv(data_dir / 'ingredients_master.csv')"),
        ("markdown", "## 2. Recipes by Cuisine & Category"),
        ("code", "cuisine_counts = recipes['cuisine'].value_counts()\nprint(cuisine_counts)"),
        ("code", "category_counts = recipes['category'].value_counts()\nprint(category_counts)"),
        ("markdown", "## 3. Most Common Recipe Ingredients in Egyptian Dishes"),
        ("code", "top_ingredients = recipe_ing['original_ingredient_name'].value_counts().head(15)\nprint(top_ingredients)")
    ]
)

# 3. 03_product_analysis.ipynb
create_nb(
    "03_product_analysis.ipynb",
    "SILLA 03: Retail Products & Shopping Cart Optimization",
    [
        ("markdown", "## 1. Relational Database Connection"),
        ("code", "import sqlite3\nimport pandas as pd\nfrom pathlib import Path\n\ndb_path = Path('../database/silla.db')\nconn = sqlite3.connect(db_path)"),
        ("markdown", "## 2. Product Brand Price Distribution"),
        ("code", "query_brands = '''\nSELECT brand, category, COUNT(*) as product_count, ROUND(AVG(price_egp), 2) as avg_price, MIN(price_egp) as min_price, MAX(price_egp) as max_price\nFROM products\nGROUP BY brand, category\nORDER BY product_count DESC\nLIMIT 20;\n'''\npd.read_sql(query_brands, conn)"),
        ("markdown", "## 3. Recipe-to-Cart Demonstration: Macaroni Béchamel (R0001)"),
        ("code", "query_cart = '''\nSELECT \n    r.recipe_name_en,\n    ri.original_ingredient_name,\n    ri.quantity as needed_qty,\n    ri.unit as recipe_unit,\n    p.product_name,\n    p.brand,\n    p.package_size,\n    p.package_unit,\n    p.price_egp,\n    p.store_name\nFROM recipes r\nJOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id\nJOIN ingredients i ON ri.ingredient_id = i.ingredient_id\nJOIN products p ON i.ingredient_id = p.ingredient_id\nWHERE r.recipe_id = 'R0001'\nGROUP BY ri.original_ingredient_name\nORDER BY p.price_egp ASC;\n'''\npd.read_sql(query_cart, conn)")
    ]
)

if __name__ == "__main__":
    print("All notebooks created successfully.")

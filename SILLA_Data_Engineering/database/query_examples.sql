-- =============================================================================
-- SILLA Project — Query Examples
-- =============================================================================
-- Use these in SQLite CLI:   sqlite3 database/silla.db < database/query_examples.sql
-- Or paste individual queries into DB Browser for SQLite / DBeaver.
-- =============================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Q1: List all recipes with their cuisine and category
-- ---------------------------------------------------------------------------
SELECT
    recipe_id,
    recipe_name_en,
    recipe_name_ar,
    cuisine,
    category
FROM recipes
ORDER BY cuisine, category, recipe_name_en
LIMIT 20;

-- ---------------------------------------------------------------------------
-- Q2: All ingredients for a specific recipe (by name)
-- ---------------------------------------------------------------------------
SELECT
    r.recipe_name_en,
    ri.original_ingredient_name,
    ri.quantity,
    ri.unit,
    i.canonical_name_ar
FROM recipe_ingredients ri
JOIN recipes     r ON ri.recipe_id     = r.recipe_id
LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
WHERE r.recipe_name_en LIKE '%Chicken%'
ORDER BY ri.recipe_ingredient_id;

-- ---------------------------------------------------------------------------
-- Q3: Products available for a given ingredient
-- ---------------------------------------------------------------------------
SELECT
    p.product_name,
    p.brand,
    p.package_size,
    p.package_unit,
    p.price_egp,
    s.store_name
FROM products p
LEFT JOIN ingredients i ON p.ingredient_id = i.ingredient_id
LEFT JOIN stores      s ON p.store_id      = s.store_id
WHERE i.canonical_name_en = 'Chicken'
ORDER BY p.price_egp ASC;

-- ---------------------------------------------------------------------------
-- Q4: Cheapest product per ingredient category
-- ---------------------------------------------------------------------------
SELECT
    i.category,
    i.canonical_name_en,
    MIN(p.price_egp) AS min_price_egp
FROM products p
JOIN ingredients i ON p.ingredient_id = i.ingredient_id
WHERE p.price_egp IS NOT NULL
GROUP BY i.category, i.canonical_name_en
ORDER BY i.category, min_price_egp;

-- ---------------------------------------------------------------------------
-- Q5: Recipes that use only vegetable and grain ingredients (vegan proxy)
-- ---------------------------------------------------------------------------
SELECT DISTINCT r.recipe_id, r.recipe_name_en
FROM recipes r
WHERE NOT EXISTS (
    SELECT 1
    FROM recipe_ingredients ri
    JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
    WHERE ri.recipe_id = r.recipe_id
      AND i.category NOT IN ('vegetable', 'grain', 'spice_herb',
                              'oil_fat', 'condiment', 'sweetener',
                              'legume', 'fruit', 'nut_seed')
)
LIMIT 20;

-- ---------------------------------------------------------------------------
-- Q6: Top 10 most-used ingredients across all recipes
-- ---------------------------------------------------------------------------
SELECT
    i.canonical_name_en,
    i.canonical_name_ar,
    COUNT(DISTINCT ri.recipe_id) AS recipe_count
FROM recipe_ingredients ri
JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
GROUP BY i.ingredient_id
ORDER BY recipe_count DESC
LIMIT 10;

-- ---------------------------------------------------------------------------
-- Q7: Full shopping cart for a recipe (ingredients → cheapest product)
-- ---------------------------------------------------------------------------
SELECT
    ri.original_ingredient_name,
    ri.quantity,
    ri.unit,
    p.product_name    AS suggested_product,
    p.price_egp,
    s.store_name
FROM recipe_ingredients ri
LEFT JOIN (
    SELECT
        p2.*,
        ROW_NUMBER() OVER (
            PARTITION BY p2.ingredient_id
            ORDER BY p2.price_egp ASC NULLS LAST
        ) AS rn
    FROM products p2
) p ON ri.ingredient_id = p.ingredient_id AND p.rn = 1
LEFT JOIN stores s ON p.store_id = s.store_id
WHERE ri.recipe_id = 'MEAL_ID_HERE';   -- replace with actual recipe_id

-- ---------------------------------------------------------------------------
-- Q8: Price history for a product
-- ---------------------------------------------------------------------------
SELECT
    p.product_name,
    ph.price_egp,
    ph.collection_date,
    ds.source_name
FROM product_price_history ph
JOIN products    p  ON ph.product_id = p.product_id
JOIN data_sources ds ON ph.source_id  = ds.source_id
WHERE p.product_name LIKE '%rice%'
ORDER BY ph.collection_date DESC;

-- ---------------------------------------------------------------------------
-- Q9: Data source coverage — how many recipes / products per source
-- ---------------------------------------------------------------------------
SELECT
    ds.source_name,
    ds.source_type,
    COUNT(DISTINCT r.recipe_id)  AS recipe_count,
    COUNT(DISTINCT p.product_id) AS product_count
FROM data_sources ds
LEFT JOIN recipes  r ON r.source_id = ds.source_id
LEFT JOIN products p ON p.source_id = ds.source_id
GROUP BY ds.source_id
ORDER BY recipe_count DESC;

-- ---------------------------------------------------------------------------
-- Q10: Ingredients with no matching product in the database
-- ---------------------------------------------------------------------------
SELECT
    i.ingredient_id,
    i.canonical_name_en,
    i.canonical_name_ar,
    i.category,
    COUNT(ri.recipe_id) AS used_in_recipes
FROM ingredients i
LEFT JOIN products p ON p.ingredient_id = i.ingredient_id
JOIN recipe_ingredients ri ON ri.ingredient_id = i.ingredient_id
WHERE p.product_id IS NULL
GROUP BY i.ingredient_id
ORDER BY used_in_recipes DESC
LIMIT 20;

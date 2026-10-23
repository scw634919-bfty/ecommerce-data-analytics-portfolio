-- B2B pricing & margin project: analysis queries (SIMULATED data)
-- Run after 01_schema.sql and loading data/ (see run_sql.sh).

-- ---------------------------------------------------------------------------
-- 0. One view with every line's revenue, cost and margin in USD.
--    Everything else builds on it, so the margin logic lives in one place.
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS line_margin;
CREATE VIEW line_margin AS
SELECT
    o.*,
    s.category,
    c.target_margin,
    c.floor_margin,
    o.qty * o.list_price_local   / o.fx_book    AS rev_list_book_fx,   -- list price, book FX
    o.qty * o.quoted_price_local / o.fx_book    AS rev_book_fx,        -- quoted price, book FX
    o.qty * o.quoted_price_local / o.fx_actual  AS revenue_usd,        -- what we really earned
    o.qty * o.book_landed_cost_usd              AS cogs_book,
    o.qty * o.actual_landed_cost_usd            AS cogs_actual,
    o.qty * o.quoted_price_local / o.fx_actual
      - o.qty * o.actual_landed_cost_usd        AS gross_profit_usd
FROM orders o
JOIN sku_master s ON s.sku = o.sku
JOIN categories c ON c.category = s.category;


-- ---------------------------------------------------------------------------
-- 1. Margin bridge: list price -> discounts -> cost drift -> FX -> actual GP
--    The four parts add up exactly to actual gross profit.
-- ---------------------------------------------------------------------------
SELECT
    ROUND(SUM(rev_list_book_fx - cogs_book))    AS gp_at_list_price,
    ROUND(SUM(rev_book_fx - rev_list_book_fx))  AS discount_impact,
    ROUND(SUM(cogs_book - cogs_actual))         AS cost_drift_impact,
    ROUND(SUM(revenue_usd - rev_book_fx))       AS fx_impact,
    ROUND(SUM(gross_profit_usd))                AS actual_gp,
    ROUND(SUM(gross_profit_usd) / SUM(revenue_usd) * 100, 2) AS actual_margin_pct
FROM line_margin;


-- ---------------------------------------------------------------------------
-- 2. Region scorecard: actual vs revenue-weighted target margin
-- ---------------------------------------------------------------------------
SELECT
    region,
    ROUND(SUM(revenue_usd))                                        AS revenue_usd,
    ROUND(SUM(gross_profit_usd) / SUM(revenue_usd) * 100, 2)       AS margin_pct,
    ROUND(SUM(revenue_usd * target_margin) / SUM(revenue_usd) * 100, 2) AS target_pct,
    ROUND((SUM(gross_profit_usd) - SUM(revenue_usd * target_margin))
          / SUM(revenue_usd) * 100, 2)                             AS gap_pts,
    ROUND(SUM(cogs_book - cogs_actual))                            AS cost_drift_usd,
    ROUND(SUM(revenue_usd - rev_book_fx))                          AS fx_impact_usd
FROM line_margin
GROUP BY region
ORDER BY gap_pts;


-- ---------------------------------------------------------------------------
-- 3. Guardrail breaks: below-floor lines with no approval, by sales rep
--    Conditional aggregation (FILTER) = one scan, no self-join.
-- ---------------------------------------------------------------------------
WITH rep_stats AS (
    SELECT
        rep,
        COUNT(*)                                                         AS lines,
        COUNT(*) FILTER (WHERE gross_profit_usd < revenue_usd * floor_margin)   AS below_floor,
        COUNT(*) FILTER (WHERE gross_profit_usd < revenue_usd * floor_margin
                           AND approval_logged = 'N')                    AS unapproved_below_floor,
        SUM(revenue_usd)                                                 AS revenue,
        SUM(gross_profit_usd)                                            AS gp,
        SUM(rev_list_book_fx - rev_book_fx) / SUM(rev_list_book_fx)      AS avg_discount
    FROM line_margin
    GROUP BY rep
)
SELECT
    rep,
    lines,
    below_floor,
    unapproved_below_floor,
    ROUND(avg_discount * 100, 2)  AS avg_discount_pct,
    ROUND(gp / revenue * 100, 2)  AS margin_pct,
    RANK() OVER (ORDER BY unapproved_below_floor DESC) AS risk_rank
FROM rep_stats
ORDER BY risk_rank;


-- ---------------------------------------------------------------------------
-- 4. Stale price book: SKUs whose actual cost rose above the book cost.
--    These need a list-price update (or a cost negotiation) now.
--    India is excluded here: its gap is freight, checked in query 7.
-- ---------------------------------------------------------------------------
SELECT
    sku,
    MIN(month)                                                     AS first_month_seen,
    ROUND(AVG(actual_landed_cost_usd / book_landed_cost_usd - 1) * 100, 1) AS avg_cost_increase_pct,
    SUM(qty)                                                       AS units_affected,
    ROUND(SUM(cogs_actual - cogs_book))                            AS margin_lost_usd
FROM line_margin
WHERE actual_landed_cost_usd > book_landed_cost_usd
  AND region <> 'IN'
GROUP BY sku
ORDER BY margin_lost_usd DESC;


-- ---------------------------------------------------------------------------
-- 5. Month-over-month margin by region (LAG) — spot when erosion started
-- ---------------------------------------------------------------------------
WITH monthly AS (
    SELECT region, month,
           SUM(gross_profit_usd) / SUM(revenue_usd) AS margin
    FROM line_margin
    GROUP BY region, month
)
SELECT
    region,
    month,
    ROUND(margin * 100, 2)                                              AS margin_pct,
    ROUND((margin - LAG(margin) OVER (PARTITION BY region ORDER BY month)) * 100, 2) AS mom_change_pts
FROM monthly
WHERE region IN ('UK', 'IN')
ORDER BY region, month;


-- ---------------------------------------------------------------------------
-- 6. Assortment: ABC within each category (running share with a window frame)
-- ---------------------------------------------------------------------------
WITH sku_rev AS (
    SELECT s.sku, s.model, s.category, s.tier, s.lifecycle, c.target_margin,
           COALESCE(SUM(l.qty), 0)              AS units,
           COALESCE(SUM(l.revenue_usd), 0)      AS revenue,
           COALESCE(SUM(l.gross_profit_usd), 0) AS gp
    FROM sku_master s
    JOIN categories c ON c.category = s.category
    LEFT JOIN line_margin l ON l.sku = s.sku
    GROUP BY s.sku, s.model, s.category, s.tier, s.lifecycle, c.target_margin
),
ranked AS (
    SELECT *,
           SUM(revenue) OVER (PARTITION BY category ORDER BY revenue DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
             / SUM(revenue) OVER (PARTITION BY category)            AS share_before,
           units * 1.0 / SUM(units) OVER (PARTITION BY category)    AS unit_share,
           COUNT(*) OVER (PARTITION BY category, tier)              AS skus_in_tier
    FROM sku_rev
)
SELECT
    category, sku, model, units,
    ROUND(revenue)                          AS revenue,
    ROUND(gp / NULLIF(revenue, 0) * 100, 1) AS margin_pct,
    CASE WHEN COALESCE(share_before, 0) < 0.80 THEN 'A'
         WHEN share_before < 0.95 THEN 'B'
         ELSE 'C' END                       AS abc,
    CASE
        WHEN lifecycle = 'EOL' THEN 'Phase out'
        WHEN COALESCE(share_before, 0) >= 0.95 AND skus_in_tier > 1 AND unit_share < 0.02
             THEN 'Consolidate'
        WHEN gp / NULLIF(revenue, 0) < target_margin - 0.01 THEN 'Below target: reprice'
        WHEN COALESCE(share_before, 0) < 0.80 THEN 'Preferred'
        ELSE 'Keep'
    END                                     AS action
FROM ranked
ORDER BY category, revenue DESC;


-- ---------------------------------------------------------------------------
-- 7. Freight check: actual vs book landed cost per unit, by region
--    (India freight is quoted too low in the price book.)
-- ---------------------------------------------------------------------------
SELECT
    region,
    category,
    ROUND(SUM(cogs_book)   / SUM(qty), 2) AS book_cost_per_unit,
    ROUND(SUM(cogs_actual) / SUM(qty), 2) AS actual_cost_per_unit,
    ROUND(SUM(cogs_actual - cogs_book))   AS extra_cost_usd
FROM line_margin
WHERE sku NOT IN ('L06', 'L10')          -- exclude the OEM cost increase to isolate freight
GROUP BY region, category
HAVING SUM(cogs_actual - cogs_book) > 0
ORDER BY extra_cost_usd DESC;

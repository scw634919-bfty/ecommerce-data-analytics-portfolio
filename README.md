# E-commerce Data Analytics Portfolio

A collection of end-to-end e-commerce analytics projects covering sales performance, customer segmentation, inventory optimization, demand forecasting, KPI reporting, clickstream behavior, and B2B pricing & margin management. Each project takes raw transaction-level data, turns it into business insights with Python, and most deliver an interactive **Tableau Public dashboard**. Project 8 is a B2B pricing and margin model built in **Excel and SQL**.

**Author:** Sophie (Chaewon Shin) · M.S. Applied Analytics — Fashion & E-commerce Analytics

---

## Tech Stack

`Python` · `pandas` · `NumPy` · `Matplotlib` · `scikit-learn` · `Statsmodels (ARIMA)` · `Jupyter Notebook` · `Tableau Public` · `SQL (SQLite)` · `Excel (formula-driven modeling)`

---

## Projects

| # | Project | Focus | Notebook | Dashboard |
|---|---------|-------|:--------:|:---------:|
| 1 | [E-commerce Sales Performance](1-ecommerce-sales-performance-analysis) | Sales trends & revenue analysis | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/1-ecommerce-sales-performance-analysis/notebook/ecommerce_sales_performance_analysis.html) | [📊](https://public.tableau.com/views/EcommerceSalesPerformanceDashboard_redesign/E-commerceSalesPerformanceDashboard) |
| 2 | [Customer Segmentation (RFM)](2-customer-segmentation-rfm) | RFM-based customer segments | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/2-customer-segmentation-rfm/notebook/customer_segmentation_rfm.html) | [📊](https://public.tableau.com/views/Customer_Segmentation_RFM_Dashboard/CustomerSegmentationDashboard) |
| 3 | [Inventory Optimization](3-inventory-optimization-analysis) | Stock health & reorder decisions | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/3-inventory-optimization-analysis/notebook/inventory_optimization_analysis.html) | [📊](https://public.tableau.com/views/Inventory_Optimization_Dashboard_redesign/InventoryOptimizationDashboard) |
| 4 | [Demand Forecasting](4-demand-forecasting) | Moving Average & ARIMA forecasting | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/4-demand-forecasting/notebook/demand_forecasting.html) | [📊](https://public.tableau.com/views/Demand_Forecasting_Dashboard/DemandForecastingAnalysis) |
| 5 | [Product Performance KPI](5-product-performance-dashboard-kpi) | KPI metrics & category performance | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/5-product-performance-dashboard-kpi/notebook/product_performance_dashboard_kpi.html) | [📊](https://public.tableau.com/views/ProductPerformanceKPIDashboard/ProductPerformanceKPIDashboard) |
| 6 | [Clickstream Analysis](6-clickstream-analysis-conversion-insights) | Browsing behavior & conversion | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/6-clickstream-analysis-conversion-insights/notebook/clickstream_analysis_conversion_insights.html) | [📊](https://public.tableau.com/views/Clickstream_Analysis_Dashboard/ClickstreamAnalysisConversionInsights) |
| 8 | [B2B Pricing & Margin Model](8-b2b-pricing-margin-model) | SKU pricing, deal desk & margin leakage (Excel + SQL) | — | — |

> 📓 = Jupyter notebook (rendered)  ·  📊 = interactive Tableau Public dashboard  ·  Project 8 is an Excel workbook + SQL (see its README)

---

## Project Summaries

### 1. E-commerce Sales Performance Analysis
Exploratory analysis of transaction-level retail data to surface revenue trends, top products, and sales patterns that support product, inventory, and sales decisions.

### 2. Customer Segmentation (RFM)
Segments customers into groups such as VIP, Regular, and At-Risk using **Recency, Frequency, and Monetary** scoring, enabling targeted marketing and retention strategies.

### 3. Inventory Optimization Analysis
Builds an **inventory decision engine** that sorts **3,907 SKUs** into four actions — Reorder now, Monitor, Promotion/Bundle, or Healthy — using weeks of coverage (a 6-week reorder point and a 26-week overstock line) and **ABC revenue classes**, so the 238 high-revenue SKUs below the reorder point come first. The dataset has no stock levels, so inventory is simulated as weeks of supply. Turns inventory analytics into a repeatable decision workflow instead of a one-time report.

### 4. Demand Forecasting
Aggregates monthly sales and forecasts next-month demand using a **3-month Moving Average** baseline and an **ARIMA** time-series model to support inventory and purchasing decisions.

### 5. Product Performance KPI Dashboard
Transforms raw transactions into business-ready KPIs — total revenue, orders, customers, and Average Order Value (AOV) — with monthly trend and category-level performance views.

### 6. Clickstream Analysis & Conversion Insights
Analyzes online clothing clickstream behavior across categories, colors, countries, and price points, and builds a basic machine-learning pipeline to explore conversion-related patterns.

### 8. B2B Pricing & Margin Model
A pricing model for a B2B IT-hardware reseller (laptops, monitors, accessories in 5 countries), built on **simulated data**. A formula-driven Excel workbook turns vendor cost, OEM rebates, duty, freight and FX into a **SKU × region price book**, checks big-deal quotes against **margin guardrails** (deal desk), and breaks a year of margin into a **bridge** (discounts, vendor cost drift, FX). SQL queries (window functions, `LAG`, conditional aggregation) find the leakage: a stale price book, under-quoted India freight, unapproved below-floor deals, and a weaker GBP. An ABC assortment view flags SKUs to push, reprice, consolidate, or phase out.

---

## Dataset

Most projects use the **Online Retail dataset** (UK-based online retailer, UCI / Kaggle). The clickstream project (#6) uses the **e-shop clothing 2008** dataset. Raw data files are not stored in the repo: each project's `data/README.md` links to the source and shows where to put the file. Project 8 uses **simulated** data generated by its own script, so its small CSVs are included.

---

## Repository Structure

```text
ecommerce-data-analytics-portfolio/
│
├── 1-ecommerce-sales-performance-analysis/
├── 2-customer-segmentation-rfm/
├── 3-inventory-optimization-analysis/
├── 4-demand-forecasting/
├── 5-product-performance-dashboard-kpi/
├── 6-clickstream-analysis-conversion-insights/
├── 8-b2b-pricing-margin-model/
│
└── README.md
```

Projects 1–6 each contain their own `data/`, `notebook/`, `outputs/`, `images/`, and a detailed `README.md`. Project 8 contains the Excel model, `sql/`, `data/`, its Python build scripts, and a `README.md`.

---

## How to Explore

1. Click a project name above to open its folder and full README.
2. Use the 📓 link to view the rendered Jupyter notebook (analysis & code).
3. Use the 📊 link to open the interactive Tableau Public dashboard.

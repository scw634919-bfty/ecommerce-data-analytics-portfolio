# E-commerce Data Analytics Portfolio

A collection of end-to-end e-commerce analytics projects covering sales performance, customer segmentation, inventory optimization, demand forecasting, KPI reporting, and clickstream behavior. Each project takes raw transaction-level data, turns it into business insights with Python, and delivers an interactive **Tableau Public dashboard**.

**Author:** Sophie (Chaewon Shin) · M.S. Applied Analytics — Fashion & E-commerce Analytics

---

## Tech Stack

`Python` · `pandas` · `NumPy` · `Matplotlib` · `scikit-learn` · `Statsmodels (ARIMA)` · `Jupyter Notebook` · `Tableau Public`

---

## Projects

| # | Project | Focus | Notebook | Dashboard |
|---|---------|-------|:--------:|:---------:|
| 1 | [E-commerce Sales Performance](1-ecommerce-sales-performance-analysis) | Sales trends & revenue analysis | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/1-ecommerce-sales-performance-analysis/notebook/ecommerce_sales_performance_analysis.html) | [📊](https://public.tableau.com/views/EcommerceSalesPerformanceDashboard_17799845497770/E-commerceSalesPerformanceDashboard) |
| 2 | [Customer Segmentation (RFM)](2-customer-segmentation-rfm) | RFM-based customer segments | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/2-customer-segmentation-rfm/notebook/customer_segmentation_rfm.html) | [📊](https://public.tableau.com/views/Customer_Segmentation_RFM_Dashboard/CustomerSegmentationDashboard) |
| 3 | [Inventory Optimization](3-inventory-optimization-analysis) | Stock health & reorder decisions | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/3-inventory-optimization-analysis/notebook/inventory_optimization_analysis.html) | [📊](https://public.tableau.com/views/Inventory_Optimization_Dashboard/InventoryOptimizationDashboard) |
| 4 | [Demand Forecasting](4-demand-forecasting) | Moving Average & ARIMA forecasting | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/4-demand-forecasting/notebook/demand_forecasting.html) | [📊](https://public.tableau.com/views/Demand_Forecasting_Dashboard/DemandForecastingAnalysis) |
| 5 | [Product Performance KPI](5-product-performance-dashboard-kpi) | KPI metrics & category performance | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/5-product-performance-dashboard-kpi/notebook/product_performance_dashboard_kpi.html) | [📊](https://public.tableau.com/views/ProductPerformanceKPIDashboard/ProductPerformanceKPIDashboard) |
| 6 | [Clickstream Analysis](6-clickstream-analysis-conversion-insights) | Browsing behavior & conversion | [📓](https://scw634919-bfty.github.io/ecommerce-data-analytics-portfolio/6-clickstream-analysis-conversion-insights/notebook/clickstream_analysis_conversion_insights.html) | [📊](https://public.tableau.com/views/Clickstream_Analysis_Dashboard/ClickstreamAnalysisConversionInsights) |

> 📓 = Jupyter notebook (rendered)  ·  📊 = interactive Tableau Public dashboard

---

## Project Summaries

### 1. E-commerce Sales Performance Analysis
Exploratory analysis of transaction-level retail data to surface revenue trends, top products, and sales patterns that support product, inventory, and sales decisions.

### 2. Customer Segmentation (RFM)
Segments customers into groups such as VIP, Regular, and At-Risk using **Recency, Frequency, and Monetary** scoring, enabling targeted marketing and retention strategies.

### 3. Inventory Optimization Analysis
Evaluates product performance and inventory health (sell-through, overstock, stockout risk) and simulates a rule-based **AI inventory decision assistant** that recommends reorder, promotion, or maintain actions.

### 4. Demand Forecasting
Aggregates monthly sales and forecasts next-month demand using a **3-month Moving Average** baseline and an **ARIMA** time-series model to support inventory and purchasing decisions.

### 5. Product Performance KPI Dashboard
Transforms raw transactions into business-ready KPIs — total revenue, orders, customers, and Average Order Value (AOV) — with monthly trend and category-level performance views.

### 6. Clickstream Analysis & Conversion Insights
Analyzes online clothing clickstream behavior across categories, colors, countries, and price points, and builds a basic machine-learning pipeline to explore conversion-related patterns.

---

## Dataset

Most projects use the **Online Retail dataset** (UK-based online retailer, UCI / Kaggle). The clickstream project (#6) uses the **e-shop clothing 2008** dataset. Raw data files are stored in each project's `data/` folder.

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
│
└── README.md
```

Each project folder contains its own `data/`, `notebook/`, `outputs/`, `images/`, and a detailed `README.md`.

---

## How to Explore

1. Click a project name above to open its folder and full README.
2. Use the 📓 link to view the rendered Jupyter notebook (analysis & code).
3. Use the 📊 link to open the interactive Tableau Public dashboard.

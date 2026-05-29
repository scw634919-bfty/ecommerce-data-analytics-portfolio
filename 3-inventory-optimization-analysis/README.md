# E-commerce Inventory Optimization & AI Decision Analysis

[![Open in nbviewer](https://img.shields.io/badge/Open%20in-nbviewer-orange?logo=jupyter)](https://nbviewer.org/github/scw634919-bfty/ecommerce-data-analytics-portfolio/blob/main/3-inventory-optimization-analysis/notebook/inventory_optimization_analysis.ipynb)

## Project Overview

Efficient inventory management is critical in e-commerce because poor stock planning can lead to stockouts, overstock, and revenue loss.

This project analyzes transaction-level retail sales data to evaluate product performance, inventory health, and category-level revenue trends.

Additionally, the project simulates an **AI-assisted inventory decision system** that recommends inventory actions based on stock conditions.

---

## Business Problem

This project aims to answer the following business questions:

- Which product categories generate the highest revenue?
- Which products are at risk of stockout?
- Which SKUs are overstocked or slow-moving?
- What actions should be taken to improve inventory efficiency?

---

## Dataset

**Source:** Online Retail Dataset (UCI / Kaggle)

### Features Used

| Feature | Description |
|----------|-------------|
| SKU | Product identifier |
| Product Description | Product name |
| Quantity | Number of units sold |
| Unit Price | Product price |
| Invoice Date | Purchase date |

---

## Methodology

### 1. Data Cleaning

- Removed invalid transactions (negative quantity and price)
- Standardized column names
- Created revenue variable

### 2. Product Categorization

Built a keyword-based categorization system to group products into:

- Home Decor
- Kitchen
- Bags
- Gift / Decorative
- Seasonal
- Sets
- Other

This step improves business interpretability and category-level reporting.

### 3. Sales Trend Analysis

Analyzed:

- Monthly revenue trend
- Category-level revenue contribution
- Product performance

### 4. Inventory Health Analysis

Calculated inventory metrics including:

- Sell-through rate
- Overstock detection
- Stockout risk detection

The project simulates inventory conditions due to the absence of real inventory data.

### 5. AI Inventory Decision Assistant

Built a rule-based recommendation engine to simulate AI-assisted inventory decisions.

Business actions include:

| Inventory Condition | Recommendation |
|--------------------|----------------|
| Stockout Risk | Reorder Immediately |
| Overstock | Run Promotion / Bundle |
| Healthy Inventory | Maintain Inventory |

---

## Key Insights

- Home decor and kitchen categories generated the highest revenue.
- Several SKUs showed stockout risk and may require replenishment.
- Overstocked products were identified for promotional opportunities.
- Product categorization improved category-level business reporting.

---

## Business Recommendations

1. Reorder high-demand products with low inventory levels.
2. Bundle or discount slow-moving inventory.
3. Monitor sell-through and inventory turnover regularly.
4. Improve product categorization for more accurate reporting.

---

## Project Structure

```text
3-inventory-optimization-analysis/
│
├── data/
│   └── Online Retail.xlsx
│
├── notebook/
│   └── inventory_optimization_analysis.ipynb
│
├── outputs/
│   ├── monthly_sales.csv
│   ├── category_performance.csv
│   ├── slow_moving_skus.csv
│   └── inventory_reorder_recommendations.csv
│
└── README.md
```

---

## Output Files

| File | Description |
|------|-------------|
| `outputs/monthly_sales.csv` | Monthly revenue and units sold trend |
| `outputs/category_performance.csv` | Revenue and units by product category (excl. other) |
| `outputs/slow_moving_skus.csv` | SKUs with sell-through rate below 30% |
| `outputs/inventory_reorder_recommendations.csv` | Full reorder recommendation table with priority actions |

---

## Tableau Dashboard

> 🔗 *Tableau Public link — coming soon*

**Dashboard Views:**
- Monthly revenue trend (line chart)
- Category revenue breakdown (bar chart)
- Inventory health: stockout risk vs overstock (highlight table)
- Top slow-moving SKUs (table)
- Reorder recommendation summary

---

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- Tableau Public

---

## Future Improvements

- Add real inventory data from WMS/ERP
- Implement safety stock calculation with demand variability
- Build ML-based inventory forecasting
- Expand category coverage with more granular product tagging

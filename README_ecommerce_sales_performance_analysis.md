# E-Commerce Sales Performance Analysis

## Project Overview

This project analyzes an online retail transaction dataset to understand overall sales performance, identify top-performing products, and compare revenue by country. The goal is to turn raw order-level data into simple business insights that can support product, inventory, and marketing decisions.

## Business Questions

- How does monthly sales performance change over time?
- Which products generate the highest revenue?
- Which countries contribute the most to total sales?
- What business actions can be taken based on product and market performance?

## Dataset

The analysis uses an online retail CSV dataset containing transaction-level sales records.

Key columns used in this analysis:

| Column | Description |
|---|---|
| `InvoiceDate` | Date and time of each transaction |
| `Description` | Product name or product description |
| `Quantity` | Number of units purchased |
| `UnitPrice` | Price per unit |
| `CustomerID` | Unique customer identifier |
| `Country` | Country where the transaction occurred |

## Tools Used

- Python
- Pandas
- Matplotlib
- Jupyter Notebook

## Analysis Process

### 1. Data Cleaning

The raw dataset was cleaned before analysis to improve accuracy.

Steps included:

- Removed rows with missing `CustomerID` or `Description`
- Removed transactions with `Quantity <= 0`
- Removed transactions with `UnitPrice <= 0`
- Converted `InvoiceDate` into a datetime format

These steps help remove incomplete records, returns, cancellations, and invalid price entries.

### 2. Feature Engineering

New columns were created for analysis:

| New Column | Purpose |
|---|---|
| `Sales` | Calculates revenue using `Quantity * UnitPrice` |
| `YearMonth` | Extracts monthly period from `InvoiceDate` for trend analysis |

### 3. Monthly Sales Trend

Sales were grouped by month to understand revenue changes over time.

This helps identify:

- Seasonal sales patterns
- High-performing months
- Potential demand peaks
- Months that may need further investigation

### 4. Top Product Analysis

Products were grouped by `Description`, and total sales were calculated for each product.

Top revenue-generating products included:

| Product | Sales |
|---|---:|
| PAPER CRAFT , LITTLE BIRDIE | 168,469.60 |
| REGENCY CAKESTAND 3 TIER | 142,592.95 |
| WHITE HANGING HEART T-LIGHT HOLDER | 100,448.15 |
| JUMBO BAG RED RETROSPOT | 85,220.78 |
| MEDIUM CERAMIC TOP STORAGE JAR | 81,416.73 |

### 5. Country Sales Analysis

Sales were grouped by country to identify the strongest markets.

Top countries by sales included:

| Country | Sales |
|---|---:|
| United Kingdom | 7,308,391.55 |
| Netherlands | 285,446.34 |
| EIRE | 265,545.90 |
| Germany | 228,867.14 |
| France | 209,024.05 |

## Key Insights

- The United Kingdom is the dominant revenue market, contributing significantly more sales than other countries.
- A small group of products drives a large amount of revenue, suggesting that best-selling products should be prioritized for inventory planning.
- Monthly sales trend analysis can help identify seasonal demand patterns and support better forecasting.
- High-performing international markets such as the Netherlands, EIRE, Germany, and France may be worth further marketing or distribution analysis.

## Business Recommendations

- Prioritize inventory for top-selling products to reduce stockout risk.
- Monitor monthly sales trends to prepare for seasonal demand changes.
- Investigate whether high-performing products share common characteristics such as category, price range, or gifting appeal.
- Explore growth opportunities in strong non-UK markets.
- Build a dashboard version of this analysis for easier business reporting.

## Project Files

```text
├── ecommerce_sales_performance_analysis.ipynb   # Main analysis notebook
├── online_retail.csv                            # Raw dataset
└── README.md                                    # Project documentation
```

## Skills Demonstrated

- Data cleaning
- Feature engineering
- Exploratory data analysis
- Sales performance analysis
- Product performance analysis
- Geographic sales analysis
- Data visualization
- Business insight generation

## Next Steps

Future improvements could include:

- Creating KPI cards for total revenue, total orders, and average order value
- Building a Tableau or Power BI dashboard
- Adding customer segmentation analysis
- Comparing product performance by season
- Forecasting future monthly sales
- Analyzing repeat customers and purchase frequency

# Demand Forecasting Analysis

## Project Overview
This project analyzes historical online retail sales data to forecast future monthly demand. The goal is to support better inventory planning, purchasing decisions, and operational forecasting by identifying monthly sales trends and predicting next-month sales.

## Business Problem
Retail businesses often need to estimate future demand in order to avoid both stockouts and overstock. Without a forecasting process, inventory planning can become reactive and inefficient.

This project answers the question:

> Based on historical monthly sales, what is the expected sales demand for the next month?

## Dataset
The analysis uses an online retail transaction dataset containing order-level sales information.

Key fields used in this project include:

- `InvoiceDate`: Date and time of each transaction
- `Quantity`: Number of units purchased
- `UnitPrice`: Price per unit
- `Sales`: Calculated revenue from each transaction

## Tools & Libraries
- Python
- Pandas
- Matplotlib
- Statsmodels
- ARIMA
- Jupyter Notebook

## Analysis Process

### 1. Data Loading
The dataset was loaded from an Excel file and reviewed in Python using Pandas.

### 2. Data Cleaning
The column names were standardized by removing extra spaces and converting them to lowercase. Invalid transaction rows were removed, including rows with negative or zero quantity and unit price.

### 3. Feature Engineering
A new `sales` column was created by multiplying quantity by unit price.

```python
sales = quantity * unitprice
```

The transaction date was also converted into a monthly period so that sales could be analyzed at the monthly level.

### 4. Monthly Sales Aggregation
Sales were grouped by month to calculate total monthly revenue.

This monthly sales table became the main dataset for forecasting.

### 5. Forecasting Models
Two forecasting approaches were used:

#### Moving Average Forecast
A 3-month moving average was used as a simple baseline forecasting method. This approach assumes that recent sales trends are a good indicator of near-term future demand.

#### ARIMA Forecast
An ARIMA model was used to capture time-series patterns and forecast the next month’s sales.

## Key Results

| Forecasting Method | Next-Month Sales Forecast |
|---|---:|
| 3-Month Moving Average | 1,241,021.93 |
| ARIMA | 1,461,941.30 |

The ARIMA model produced a higher next-month forecast than the moving average model, suggesting that the model captured stronger upward movement or recent trend changes in the time series.

## Key Insights
- Monthly sales data provides a clearer view of demand trends than individual transaction-level data.
- Removing incomplete or invalid transaction records improves the reliability of the forecast.
- The moving average model is easy to understand and useful as a baseline.
- ARIMA can capture more complex time-series patterns than a simple average.
- Forecasting results can help support inventory planning and purchasing decisions.

## Business Recommendations
- Use forecasting results as a starting point for monthly inventory planning.
- Compare simple baseline models with more advanced models before making decisions.
- Monitor actual sales against forecasted sales each month to improve accuracy.
- Consider adding product-level forecasting in the future to identify which items need replenishment.
- Include seasonality, promotions, and stockout information in future model improvements.

## Conclusion
This project demonstrates a practical demand forecasting workflow using historical online retail sales data. By cleaning transaction data, aggregating monthly sales, and applying Moving Average and ARIMA forecasting models, the analysis provides a foundation for data-driven inventory and demand planning.

## Future Improvements
- Forecast demand by product category or SKU
- Add seasonality features
- Compare additional models such as Prophet or SARIMA
- Evaluate model accuracy using train-test split
- Build a dashboard to monitor actual vs. forecasted demand

"""
Honest evaluation of the demand forecasting models (ARIMA vs 3-month Moving Average).

Replicates the data prep from demand_forecasting.ipynb, then does a PROPER
train/test split and computes MAPE / RMSE / MAE on a held-out test set using
walk-forward (one-step-ahead) validation, which is a fair comparison for both
models. Nothing is hardcoded; every number is computed from the data.
"""

import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 1. Load + clean (identical logic to the notebook)
# ---------------------------------------------------------------------------
import os

_CANDIDATES = ["Online Retail.xlsx", "data/Online Retail.xlsx", "../data/Online Retail.xlsx"]
_data_path = next((p for p in _CANDIDATES if os.path.exists(p)), _CANDIDATES[0])
df = pd.read_excel(_data_path)
df.columns = df.columns.str.strip().str.lower()
df = df[(df["quantity"] > 0) & (df["unitprice"] > 0)].copy()
df["invoicedate"] = pd.to_datetime(df["invoicedate"])
df["sales"] = df["quantity"] * df["unitprice"]
df["month"] = df["invoicedate"].dt.to_period("M").astype(str)

monthly_sales = df.groupby("month")["sales"].sum().reset_index()
monthly_sales["month"] = pd.to_datetime(monthly_sales["month"])
# drop the last (incomplete) month, as in the notebook
monthly_sales = monthly_sales.sort_values("month").iloc[:-1].copy()

ts = monthly_sales.set_index("month")["sales"]
print(f"Total complete months available: {len(ts)}")
print(f"Date range: {ts.index.min():%Y-%m} -> {ts.index.max():%Y-%m}")
print(ts.round(0).to_string())
print("-" * 60)

# ---------------------------------------------------------------------------
# 2. Train/test split
# ---------------------------------------------------------------------------
N_TEST = 3  # hold out the last 3 months
train, test = ts.iloc[:-N_TEST], ts.iloc[-N_TEST:]
print(f"Train: {len(train)} months ({train.index.min():%Y-%m} -> {train.index.max():%Y-%m})")
print(f"Test:  {len(test)} months ({test.index.min():%Y-%m} -> {test.index.max():%Y-%m})")
print("-" * 60)


def metrics(actual, pred):
    actual = np.asarray(actual, dtype=float)
    pred = np.asarray(pred, dtype=float)
    mae = np.mean(np.abs(actual - pred))
    rmse = np.sqrt(np.mean((actual - pred) ** 2))
    mape = np.mean(np.abs((actual - pred) / actual)) * 100
    return mape, rmse, mae


# ---------------------------------------------------------------------------
# 3. Walk-forward one-step-ahead forecasts on the test set
# ---------------------------------------------------------------------------
# Moving-average baseline: forecast = mean of the prior 3 actual months
ma_preds = []
for i in range(len(ts) - N_TEST, len(ts)):
    ma_preds.append(ts.iloc[i - 3:i].mean())

# ARIMA(1,1,1): refit on all data up to each test point, forecast 1 step
arima_preds = []
history = list(train)
for actual in test:
    model_fit = ARIMA(history, order=(1, 1, 1)).fit()
    arima_preds.append(model_fit.forecast(steps=1)[0])
    history.append(actual)

ma_mape, ma_rmse, ma_mae = metrics(test.values, ma_preds)
ar_mape, ar_rmse, ar_mae = metrics(test.values, arima_preds)

# ---------------------------------------------------------------------------
# 4. Report
# ---------------------------------------------------------------------------
cmp = pd.DataFrame(
    {
        "month": [f"{m:%Y-%m}" for m in test.index],
        "actual": test.values.round(0),
        "ma_pred": np.round(ma_preds, 0),
        "arima_pred": np.round(arima_preds, 0),
    }
)
print(cmp.to_string(index=False))
print("-" * 60)

results = pd.DataFrame(
    {
        "model": ["Moving Average (3-mo)", "ARIMA(1,1,1)"],
        "MAPE_%": [ma_mape, ar_mape],
        "RMSE": [ma_rmse, ar_rmse],
        "MAE": [ma_mae, ar_mae],
    }
)
print(results.round(2).to_string(index=False))
print("-" * 60)

for name, base, ar in [("MAPE", ma_mape, ar_mape), ("RMSE", ma_rmse, ar_rmse), ("MAE", ma_mae, ar_mae)]:
    impr = (base - ar) / base * 100
    verdict = "ARIMA better" if impr > 0 else "baseline better/equal"
    print(f"{name}: MA={base:.2f}  ARIMA={ar:.2f}  -> ARIMA change {impr:+.1f}%  ({verdict})")

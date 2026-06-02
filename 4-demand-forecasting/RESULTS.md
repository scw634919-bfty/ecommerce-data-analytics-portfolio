# Demand Forecasting — Model Evaluation Results

**Dataset:** UCI *Online Retail* (UK e-commerce). Monthly total sales, 12 complete
months (Dec 2010 – Nov 2011). The incomplete final month was dropped, matching the notebook.

**Split:** Last **3 months** held out as test (Sep–Nov 2011); models evaluated with
walk-forward one-step-ahead forecasting. Train = first 9 months.
Reproduce with `evaluate_models.py` — all numbers are computed, none hardcoded.

## Metrics on the 3-month holdout

| Model                  | MAPE   | RMSE       | MAE        |
|------------------------|--------|------------|------------|
| Moving Average (3-mo)  | 30.20% | 392,386    | 379,938    |
| ARIMA(1,1,1)           | 23.65% | 303,231    | 293,271    |

**ARIMA vs. baseline:** MAPE −21.7%, RMSE −22.7%, MAE −22.8% (ARIMA wins on all three).

## Honest takeaway

ARIMA beat the moving-average baseline, reducing MAPE from 30.2% to 23.7% (~22% relative
improvement) on a 3-month holdout. **Caveat:** this rests on only 12 monthly data points
(9 train / 3 test), so it is illustrative, not statistically robust. The win is largely
because the holdout months were strongly trending upward and a trailing moving average
lags a trend, while ARIMA's differencing captures it. Both models still have high absolute
error (~24–30% MAPE).

**Most honest way to report:** state the holdout size explicitly and frame ARIMA's edge as
directional/trend-capturing rather than a precise accuracy claim. To strengthen this you'd
want more history (weekly or daily aggregation gives far more points) or cross-validated
folds.

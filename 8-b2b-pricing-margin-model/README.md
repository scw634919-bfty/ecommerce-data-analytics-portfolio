# B2B Tech Hardware: SKU Pricing, Deal Desk & Margin Leakage Model

A practice project that copies the core work of a pricing & merchandising analyst at a B2B IT-hardware reseller.
The business sells laptops, monitors and accessories to companies in 5 countries. The project answers four questions:

1. **What should each SKU cost and sell for in each country?** (landed cost → target price → local list price)
2. **How low can Sales go on a big deal, and who has to approve it?** (deal desk + guardrails)
3. **Where did we lose margin last year, and why?** (margin bridge: discounts, cost drift, FX)
4. **Which SKUs should we push, fix, or remove?** (ABC assortment by category)

> ⚠️ **All data is simulated.** Costs and prices are rough, illustrative numbers. This is not real data from any OEM, distributor or company.

**Tools:** Excel (formula-driven model, ~37,000 formulas, no hardcoded results), SQL (SQLite, standard SQL with window functions), Python (pandas, to generate data and cross-check every Excel total).

---

## What's inside

| File | What it is |
|---|---|
| `B2B_Pricing_Margin_Model.xlsx` | The model. Change any blue input and everything recalculates. |
| `sql/01_schema.sql`, `sql/02_analysis.sql` | Schema + 7 analysis queries (margin bridge, guardrail breaks, stale price book, MoM margin with `LAG`, ABC with window frames, freight check) |
| `sql/query_output.txt` | Output of every query |
| `data/*.csv` | Simulated regions, categories, 30 SKUs, 150-row price book, 1,961 order lines (Oct 2025 – Sep 2026) |
| `generate_data.py`, `build_model.py`, `verify.py` | Rebuild the data and workbook; check Excel totals against pandas |

### Workbook sheets

| Sheet | Purpose |
|---|---|
| **Assumptions** | FX, import duty, FX buffer, freight per unit by region; target/floor margin and list headroom by category |
| **SKU_Master** | 30 SKUs: OEM, category, tier, lifecycle, vendor cost, base OEM rebate |
| **Price_Book** | 30 SKUs × 5 regions: landed cost, target price, local list price, floor price |
| **Deal_Desk** | Quote checker: margin, approval tier, walk-away price, counter-offer, with two scenarios side by side |
| **FX_Scenario** | How much currency movement a list price absorbs before it breaks the floor |
| **Orders** | Order lines with realized margin per line |
| **Margin_Leakage** | Margin bridge + cuts by region, category, sales rep and month, with charts |
| **Assortment** | ABC by category + recommendation per SKU |

---

## How the pricing works

```
Landed cost (USD)   = vendor cost × (1 − OEM rebate) × (1 + import duty) + freight per unit
Target price (USD)  = landed cost ÷ (1 − target margin)          ← margin on price, not markup on cost
List price (local)  = round up to 5 of: target price × (1 + list headroom) × (1 + FX buffer) × FX rate
Floor price         = landed cost ÷ (1 − floor margin)
```

| Category | Target margin | Floor margin | List headroom |
|---|---|---|---|
| Laptop | 12% | 8% | 3% |
| Monitor | 18% | 12% | 4% |
| Accessory | 32% | 22% | 5% |

**Approval guardrails:** margin ≥ target → auto-approve · floor ≤ margin < target → Sales Lead · 0 ≤ margin < floor → Finance (VP) · margin < 0 → reject.

VAT/GST is left out on purpose: B2B prices are quoted ex-VAT and business buyers reclaim it, so it does not change our margin.

---

## Key findings (simulated year, Oct 2025 – Sep 2026)

**Revenue $26.7M, gross profit $3.61M, margin 13.5% vs a 13.8% revenue-weighted target → $305K short of target.**

### Margin bridge

| Step | USD |
|---|---|
| Gross profit at list price (book cost & FX) | $4,911K |
| − Discounts | −$1,010K (of which **−$129K** on below-floor lines with no approval) |
| − Vendor cost increases not in the price book | −$167K |
| − FX movement vs book rate | −$127K |
| **= Actual gross profit** | **$3,607K** |

Discounts are the biggest item, but most of them are normal negotiation that the list headroom is built for. The **fixable** leakage is the last three lines, plus the unapproved discounts.

### Where it came from

| # | Finding | Evidence | Fix |
|---|---|---|---|
| 1 | **Stale price book:** Dell XPS 13 (L06) and HP EliteBook 840 (L10) vendor costs rose ~6% in Apr 2026; list prices never changed | SQL query 4: first seen 2026-04, ~$72K margin lost; both SKUs run at ~9.7% vs 12% target | Reprice or renegotiate; alert when a vendor cost changes by more than 2% |
| 2 | **India freight under-quoted:** actual $75/laptop vs $55 in the price book | SQL query 7: ~$80K extra cost; India is the worst region at −1.6 pts vs target | Update the freight assumption and reprice India list prices |
| 3 | **Guardrail breaks:** 48 order lines below floor with no approval logged | Rep R04 owns 28 of them, average discount 5.0% vs 1.8–2.9% for other reps | Make the floor a hard stop in the quoting tool; deal-desk review for enterprise accounts |
| 4 | **FX:** GBP weakened ~5% from March 2026; UK margin fell from ~15% to ~11% by summer | Margin_Leakage by month; SQL query 5 (`LAG`) | Monthly FX review of the price book, 30-day quote validity, larger GBP buffer |
| 5 | **Assortment clutter:** 5 low-volume duplicates and 1 end-of-life model | Assortment sheet / SQL query 6 | Consolidate L11, L13, L14, M06, A07 into preferred SKUs; phase out L15; use the extra volume to ask for better rebates |

### Deal desk example

A customer asks for **500 ThinkPad X1 Carbon at $1,600** (8% below the $1,740 list).

| | A: as requested | B: + deal registration |
|---|---|---|
| Extra OEM deal-registration rebate | 0% | 2% |
| Volume freight discount | 0% | 20% |
| Landed cost per unit | $1,484.80 | $1,450.80 |
| Deal margin | 7.2% | 9.3% |
| Approval | Finance (VP) | Sales Lead |
| Deal gross profit | $57,600 | $74,600 |

Same customer price, **+$17,000 gross profit**: register the deal with the OEM and consolidate freight before saying yes or no to the discount.

### FX check

A UK MacBook Air list price of £1,145 can absorb about **10% GBP weakening** before it falls below the 8% floor.

---

## How to run

```bash
python3 generate_data.py        # simulated CSVs → data/
python3 build_model.py          # builds the workbook (Excel recalculates on open)
bash sql/run_sql.sh             # loads SQLite and runs every query
python3 verify.py B2B_Pricing_Margin_Model.xlsx   # after opening + saving in Excel: checks totals vs pandas
```

## Limitations

- Simulated data with problems planted on purpose (cost increase, freight gap, one over-discounting rep, GBP move), so the analysis has something to find.
- One FX rate per month; no hedging, payment terms, warranty, or services revenue.
- Rebates are applied when buying. In real life many OEM rebates are paid later (back-end) and should be accrued, not counted at quote time.

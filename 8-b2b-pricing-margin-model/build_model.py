"""Build B2B_Pricing_Margin_Model.xlsx from the simulated CSVs in data/.

Every calculated cell is an Excel formula, so changing an assumption (FX, freight,
target margin, a vendor cost) updates the price book, the deal desk, and the
leakage analysis.
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).parent
D = HERE / "data"
OUT = HERE / "B2B_Pricing_Margin_Model.xlsx"

regions = pd.read_csv(D / "regions.csv")
categories = pd.read_csv(D / "categories.csv")
skus = pd.read_csv(D / "sku_master.csv")
orders = pd.read_csv(D / "orders.csv")

# ---------------------------------------------------------------- styles
FONT = "Arial"
BLUE, GREEN, BLACK = "0000FF", "008000", "000000"
NAVY = "1F3864"
f_title = Font(name=FONT, size=14, bold=True, color=NAVY)
f_sub = Font(name=FONT, size=10, italic=True, color="595959")
f_head = Font(name=FONT, size=10, bold=True, color="FFFFFF")
f_sec = Font(name=FONT, size=11, bold=True, color=NAVY)
fill_head = PatternFill("solid", fgColor=NAVY)
fill_input = PatternFill("solid", fgColor="FFFF00")
fill_out = PatternFill("solid", fgColor="E2EFDA")
thin = Side(style="thin", color="BFBFBF")
box = Border(left=thin, right=thin, top=thin, bottom=thin)

USD = '$#,##0;($#,##0);"-"'
USD2 = '$#,##0.00;($#,##0.00);"-"'
NUM = '#,##0;(#,##0);"-"'
NUM2 = '#,##0.00;(#,##0.00);"-"'
NUM4 = '0.0000'
PCT = '0.0%;(0.0%);"-"'


def put(ws, ref, value, fmt=None, bold=False, inp=False, key=False):
    """Write a cell with the model's color code: blue = input, green = cross-sheet link, black = formula."""
    c = ws[ref]
    c.value = value
    color = BLACK
    if inp:
        color = BLUE
    elif isinstance(value, str) and value.startswith("=") and "!" in value:
        color = GREEN
    c.font = Font(name=FONT, size=10, bold=bold, color=color)
    if fmt:
        c.number_format = fmt
    if key:
        c.fill = fill_input
    return c


def header(ws, row, labels, col=1, widths=None):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=lab)
        c.font = f_head
        c.fill = fill_head
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = box
    ws.row_dimensions[row].height = 30
    if widths:
        for i, w in enumerate(widths):
            ws.column_dimensions[get_column_letter(col + i)].width = w


def title(ws, text, sub):
    ws["A1"] = text
    ws["A1"].font = f_title
    ws["A2"] = sub
    ws["A2"].font = f_sub
    ws.sheet_view.showGridLines = False


wb = Workbook()

# ================================================================ README
rd = wb.active
rd.title = "README"
title(rd, "B2B Tech Hardware: SKU Pricing, Deal Desk & Margin Leakage Model",
      "Practice project by Chaewon Shin. ALL DATA IS SIMULATED for illustration; not real OEM, distributor, or company data.")
rd.column_dimensions["A"].width = 26
rd.column_dimensions["B"].width = 100
lines = [
    ("Business question", "We resell laptops, monitors and accessories to companies in 5 countries. What should each SKU cost, "
                          "what should we charge, how low can Sales go on a big deal, and where are we losing margin?"),
    ("", ""),
    ("SHEET GUIDE", ""),
    ("Assumptions", "Inputs: FX, import duty, FX buffer, freight per unit by region; target and floor margin by category."),
    ("SKU_Master", "30 SKUs: OEM, category, tier, lifecycle, vendor cost, base OEM rebate."),
    ("Price_Book", "150 SKU x region rows: landed cost -> target price (USD) -> list price in local currency, plus floor price."),
    ("Deal_Desk", "Quote checker for one big deal. Compares 'as requested' vs 'with deal-registration rebate' and returns the approval tier."),
    ("FX_Scenario", "How much FX movement a list price can absorb before it breaks the margin floor."),
    ("Orders", "12 months of simulated order lines (Oct 2025 - Sep 2026) with realized margin per line."),
    ("Margin_Leakage", "Margin bridge (list -> discounts -> cost drift -> FX -> actual) and cuts by region, category, rep, month."),
    ("Assortment", "ABC class per category and a keep / preferred / consolidate / phase-out recommendation per SKU."),
    ("", ""),
    ("COLOR LEGEND", ""),
    ("Blue text", "Hard-coded input you can change."),
    ("Yellow fill", "Key lever to try first (e.g. Deal_Desk inputs, FX shock, target margins)."),
    ("Green text", "Formula pulling from another sheet."),
    ("Black text", "Formula on the same sheet."),
    ("", ""),
    ("CORE FORMULAS", ""),
    ("Landed cost (USD)", "Vendor cost x (1 - OEM rebate) x (1 + import duty) + freight per unit"),
    ("Target price (USD)", "Landed cost / (1 - target margin)      (margin is on price, not markup on cost)"),
    ("List price (local)", "Round up to 5 of: target price x (1 + list headroom) x (1 + FX buffer) x FX rate"),
    ("Floor price", "Landed cost / (1 - floor margin). Below floor needs Finance approval."),
    ("Approval tiers", "Margin >= target: auto-approve | floor <= margin < target: Sales Lead | 0 <= margin < floor: Finance (VP) | margin < 0: reject"),
    ("VAT / GST", "Excluded. B2B prices are quoted ex-VAT and business buyers reclaim VAT, so it does not change our margin."),
    ("", ""),
    ("HEADLINE NUMBERS (live)", ""),
]
r = 4
for a, b in lines:
    rd.cell(row=r, column=1, value=a).font = Font(name=FONT, size=10, bold=a.isupper() or a == "Business question", color=NAVY if a.isupper() else BLACK)
    c = rd.cell(row=r, column=2, value=b)
    c.font = Font(name=FONT, size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
kpi_start = r
# filled after Margin_Leakage exists (cell refs below)

# ================================================================ Assumptions
asm = wb.create_sheet("Assumptions")
title(asm, "Assumptions", "Blue = input. Rates are illustrative (simulated). FX = units of local currency per 1 USD.")
asm["A3"] = "Region economics"
asm["A3"].font = f_sec
asm["F3"] = "Freight & handling per unit (USD)"
asm["F3"].font = f_sec
header(asm, 4, ["Region", "Currency", "FX (local per USD)", "Import duty %", "FX buffer %", "Laptop", "Monitor", "Accessory"],
       widths=[16, 11, 14, 13, 12, 11, 11, 11])
for i, row in regions.iterrows():
    rr = 5 + i
    put(asm, f"A{rr}", row.region, inp=True)
    put(asm, f"B{rr}", row.currency, inp=True)
    put(asm, f"C{rr}", float(row.fx_book), NUM4 if row.fx_book < 10 else NUM2, inp=True, key=True)
    put(asm, f"D{rr}", float(row.duty_pct), PCT, inp=True)
    put(asm, f"E{rr}", float(row.fx_buffer_pct), PCT, inp=True)
    put(asm, f"F{rr}", float(row.freight_laptop), USD, inp=True)
    put(asm, f"G{rr}", float(row.freight_monitor), USD, inp=True)
    put(asm, f"H{rr}", float(row.freight_accessory), USD, inp=True)
asm["A10"] = ("FX buffer = extra cushion built into non-USD list prices so a small currency move does not erase margin. "
              "Duty for IN is an illustrative 11% on IT hardware.")
asm["A10"].font = f_sub

asm["A12"] = "Category margin policy"
asm["A12"].font = f_sec
header(asm, 13, ["Category", "Target margin", "Floor margin", "List headroom %"], widths=None)
for i, row in categories.iterrows():
    rr = 14 + i
    put(asm, f"A{rr}", row.category, inp=True)
    put(asm, f"B{rr}", float(row.target_margin), PCT, inp=True, key=True)
    put(asm, f"C{rr}", float(row.floor_margin), PCT, inp=True, key=True)
    put(asm, f"D{rr}", float(row.list_headroom_pct), PCT, inp=True, key=True)
asm["A17"] = ("Laptops carry thin margins (commoditized, price-transparent); accessories carry the margin. Gross margin on price. "
               "List headroom = room for normal negotiation built into list price, so a standard discount still lands on target.")
asm["A17"].font = f_sub

asm["A19"] = "Assortment rules"
asm["A19"].font = f_sec
put(asm, "A20", "Class A = top cumulative revenue share up to")
put(asm, "C20", 0.80, PCT, inp=True)
put(asm, "A21", "Class B = up to")
put(asm, "C21", 0.95, PCT, inp=True)
put(asm, "A22", "Low-volume threshold (share of category units)")
put(asm, "C22", 0.02, PCT, inp=True)
put(asm, "A23", "Margin tolerance below target before flagging (pts)")
put(asm, "C23", 0.01, PCT, inp=True)

REG = "Assumptions!$A$5:$A$9"
CAT = "Assumptions!$A$14:$A$16"

def reg_lookup(col, region_ref):
    return f"INDEX(Assumptions!${col}$5:${col}$9,MATCH({region_ref},{REG},0))"

def cat_lookup(col, cat_ref):
    return f"INDEX(Assumptions!${col}$14:${col}$16,MATCH({cat_ref},{CAT},0))"

def freight_lookup(region_ref, cat_ref):
    return f"INDEX(Assumptions!$F$5:$H$9,MATCH({region_ref},{REG},0),MATCH({cat_ref},Assumptions!$F$4:$H$4,0))"

# ================================================================ SKU_Master
sk = wb.create_sheet("SKU_Master")
title(sk, "SKU Master", "Vendor cost = price we pay the OEM/distributor per unit (USD, illustrative). Base rebate = standing OEM partner rebate.")
header(sk, 4, ["SKU", "OEM", "Model", "Category", "Tier", "Lifecycle", "Vendor cost (USD)", "Base OEM rebate %"],
       widths=[8, 11, 40, 11, 12, 10, 13, 13])
N_SKU = len(skus)
for i, row in skus.iterrows():
    rr = 5 + i
    for col, val in zip("ABCDEF", [row.sku, row.oem, row.model, row.category, row.tier, row.lifecycle]):
        put(sk, f"{col}{rr}", val, inp=True)
    put(sk, f"G{rr}", float(row.vendor_cost_usd), USD, inp=True)
    put(sk, f"H{rr}", float(row.base_rebate_pct), PCT, inp=True)
SK_LAST = 4 + N_SKU
SKU_RNG = f"SKU_Master!$A$5:$A${SK_LAST}"

def sku_lookup(col, sku_ref):
    return f"INDEX(SKU_Master!${col}$5:${col}${SK_LAST},MATCH({sku_ref},{SKU_RNG},0))"

# ================================================================ Price_Book
pbk = wb.create_sheet("Price_Book")
title(pbk, "Price Book (SKU x Region)", "All formulas. Change Assumptions or SKU_Master and every price updates.")
pb_cols = ["SKU", "Model", "Category", "Region", "Currency", "Vendor cost (USD)", "OEM rebate %", "Net cost after rebate",
           "Duty %", "Duty (USD)", "Freight (USD)", "Landed cost (USD)", "Target margin", "Target price (USD)",
           "FX buffer %", "FX (book)", "List headroom %", "List price (local)", "Floor margin", "Floor price (USD)", "Floor price (local)",
           "List margin at book FX", "Lookup key"]
header(pbk, 4, pb_cols, widths=[7, 36, 10, 8, 9, 12, 10, 12, 8, 10, 10, 12, 10, 12, 9, 10, 10, 13, 9, 12, 13, 11, 10])
r = 5
for _, s in skus.iterrows():
    for reg in regions.region:
        put(pbk, f"A{r}", s.sku)
        put(pbk, f"D{r}", reg)
        put(pbk, f"B{r}", "=" + sku_lookup("C", f"$A{r}"))
        put(pbk, f"C{r}", "=" + sku_lookup("D", f"$A{r}"))
        put(pbk, f"E{r}", "=" + reg_lookup("B", f"$D{r}"))
        put(pbk, f"F{r}", "=" + sku_lookup("G", f"$A{r}"), USD2)
        put(pbk, f"G{r}", "=" + sku_lookup("H", f"$A{r}"), PCT)
        put(pbk, f"H{r}", f"=F{r}*(1-G{r})", USD2)
        put(pbk, f"I{r}", "=" + reg_lookup("D", f"$D{r}"), PCT)
        put(pbk, f"J{r}", f"=H{r}*I{r}", USD2)
        put(pbk, f"K{r}", "=" + freight_lookup(f"$D{r}", f"$C{r}"), USD2)
        put(pbk, f"L{r}", f"=H{r}+J{r}+K{r}", USD2, bold=True)
        put(pbk, f"M{r}", "=" + cat_lookup("B", f"$C{r}"), PCT)
        put(pbk, f"N{r}", f"=L{r}/(1-M{r})", USD2)
        put(pbk, f"O{r}", "=" + reg_lookup("E", f"$D{r}"), PCT)
        put(pbk, f"P{r}", "=" + reg_lookup("C", f"$D{r}"), NUM4)
        put(pbk, f"Q{r}", "=" + cat_lookup("D", f"$C{r}"), PCT)
        put(pbk, f"R{r}", f"=ROUNDUP(N{r}*(1+Q{r})*(1+O{r})*P{r}/5,0)*5", NUM, bold=True)
        put(pbk, f"S{r}", "=" + cat_lookup("C", f"$C{r}"), PCT)
        put(pbk, f"T{r}", f"=L{r}/(1-S{r})", USD2)
        put(pbk, f"U{r}", f"=T{r}*(1+O{r})*P{r}", NUM2)
        put(pbk, f"V{r}", f"=IF(R{r}=0,0,(R{r}/P{r}-L{r})/(R{r}/P{r}))", PCT)
        put(pbk, f"W{r}", f'=A{r}&"|"&D{r}')
        r += 1
PB_LAST = r - 1
pbk.freeze_panes = "B5"
pbk.auto_filter.ref = f"A4:W{PB_LAST}"
pbk.cell(row=PB_LAST + 2, column=1,
         value="List price is in local currency, ex-VAT. 'List margin at book FX' is above target by design: list headroom, FX buffer and rounding leave room to negotiate.").font = f_sub

def pb_lookup(col, key_expr):
    return f"INDEX(Price_Book!${col}$5:${col}${PB_LAST},MATCH({key_expr},Price_Book!$W$5:$W${PB_LAST},0))"

# ================================================================ Deal_Desk
dd = wb.create_sheet("Deal_Desk")
title(dd, "Deal Desk: special-pricing check", "Yellow cells are inputs. Example: a customer asks for 500 ThinkPad X1 Carbon at $1,600 each.")
dd.column_dimensions["A"].width = 4
dd.column_dimensions["B"].width = 44
dd.column_dimensions["C"].width = 22
dd.column_dimensions["D"].width = 26
dd.column_dimensions["E"].width = 60
dd["B4"] = "Deal inputs"
dd["B4"].font = f_sec
inputs = [("SKU", "L08", None), ("Region", "US", None), ("Quantity (units)", 500, NUM),
          ("Requested unit price (local currency, ex-VAT)", 1600, NUM2)]
for i, (lab, val, fmt) in enumerate(inputs):
    rr = 5 + i
    put(dd, f"B{rr}", lab)
    put(dd, f"C{rr}", val, fmt, inp=True, key=True)
    dd[f"C{rr}"].border = box
dv_sku = DataValidation(type="list", formula1=f"={SKU_RNG}", allow_blank=False)
dv_reg = DataValidation(type="list", formula1=f"={REG}", allow_blank=False)
dd.add_data_validation(dv_sku)
dd.add_data_validation(dv_reg)
dv_sku.add("C5")
dv_reg.add("C6")
put(dd, "B9", "Model")
put(dd, "C9", "=" + sku_lookup("C", "$C$5"))
put(dd, "B10", "Category")
put(dd, "C10", "=" + sku_lookup("D", "$C$5"))
put(dd, "B11", "Currency")
put(dd, "C11", "=" + reg_lookup("B", "$C$6"))

header(dd, 13, ["", "Scenario", "A: As requested", "B: + deal registration", "What it means"], col=1)
dd["A13"].fill = PatternFill(fill_type=None)
KEY = '$C$5&"|"&$C$6'
rows_dd = [
    # (row, label, C formula/value, D formula/value, fmt, is_input, note)
    (14, "Extra OEM deal-registration rebate %", 0.0, 0.02, PCT, True, "OEMs give extra rebate when a big deal is registered with them first."),
    (15, "Volume freight discount %", 0.0, 0.20, PCT, True, "Consolidated shipment of 500 units is cheaper per unit."),
    (16, "Price book list price (local)", "=" + pb_lookup("R", KEY), None, NUM2, False, "Standard price before any discount."),
    (17, "Discount vs list", "=IF(C16=0,0,1-$C$8/C16)", None, PCT, False, ""),
    (18, "Vendor cost (USD)", "=" + sku_lookup("G", "$C$5"), None, USD2, False, ""),
    (19, "Net cost after base + extra rebate (USD)", "=C18*(1-" + sku_lookup("H", "$C$5") + "-C14)", None, USD2, False, "Effective vendor cost."),
    (20, "Import duty (USD)", "=C19*" + reg_lookup("D", "$C$6"), None, USD2, False, ""),
    (21, "Freight per unit (USD)", "=" + freight_lookup("$C$6", "$C$10") + "*(1-C15)", None, USD2, False, ""),
    (22, "Landed cost per unit (USD)", "=C19+C20+C21", None, USD2, False, ""),
    (23, "FX (book, local per USD)", "=" + reg_lookup("C", "$C$6"), None, NUM4, False, ""),
    (24, "Requested price (USD)", "=$C$8/C23", None, USD2, False, ""),
    (25, "Gross profit per unit (USD)", "=C24-C22", None, USD2, False, ""),
    (26, "Deal margin %", "=IF(C24=0,0,C25/C24)", None, PCT, False, "Gross margin on price."),
    (27, "Target margin", "=" + cat_lookup("B", "$C$10"), None, PCT, False, ""),
    (28, "Floor margin", "=" + cat_lookup("C", "$C$10"), None, PCT, False, ""),
    (29, "Total deal revenue (USD)", "=C24*$C$7", None, USD, False, ""),
    (30, "Total deal gross profit (USD)", "=C25*$C$7", None, USD, False, ""),
    (31, "APPROVAL", '=IF(C26<0,"Reject",IF(C26<C28,"Finance (VP) approval",IF(C26<C27,"Sales Lead approval","Auto-approve")))',
     None, None, False, "Guardrail tier from the margin policy."),
    (32, "Lowest price at floor margin (local)", "=C22/(1-C28)*C23", None, NUM2, False, "Walk-away price without Finance."),
    (33, "Counter-offer at target margin (local)", "=ROUNDUP(C22/(1-C27)*C23/5,0)*5", None, NUM2, False, "Price that keeps target margin."),
    (34, "Max discount vs list at floor", "=IF(C16=0,0,1-C32/C16)", None, PCT, False, ""),
]
for rr, lab, cval, dval, fmt, is_in, note in rows_dd:
    put(dd, f"B{rr}", lab, bold=(lab == "APPROVAL" or lab == "Deal margin %"))
    if is_in:
        put(dd, f"C{rr}", cval, fmt, inp=True, key=True)
        put(dd, f"D{rr}", dval, fmt, inp=True, key=True)
    else:
        put(dd, f"C{rr}", cval, fmt, bold=(rr in (26, 31)))
        # Column D uses the same formula with its own scenario levers (C14/C15 -> D14/D15).
        dform = cval.replace("C14", "D14").replace("C15", "D15")
        for a in ["C16", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C32"]:
            dform = dform.replace(a, "D" + a[1:])
        put(dd, f"D{rr}", dform, fmt, bold=(rr in (26, 31)))
    put(dd, f"E{rr}", note)
    dd[f"E{rr}"].font = f_sub
    for col in "BCD":
        dd[f"{col}{rr}"].border = box
for col in "CD":
    dd[f"{col}31"].fill = fill_out
red = PatternFill("solid", fgColor="F8CBAD")
amber = PatternFill("solid", fgColor="FFE699")
green_f = PatternFill("solid", fgColor="C6EFCE")
dd.conditional_formatting.add("C31:D31", FormulaRule(formula=['LEFT(C31,7)="Finance"'], fill=red))
dd.conditional_formatting.add("C31:D31", FormulaRule(formula=['C31="Reject"'], fill=red))
dd.conditional_formatting.add("C31:D31", FormulaRule(formula=['LEFT(C31,5)="Sales"'], fill=amber))
dd.conditional_formatting.add("C31:D31", FormulaRule(formula=['C31="Auto-approve"'], fill=green_f))
put(dd, "B36", "Take-away")
dd["B36"].font = f_sec
put(dd, "B37", '="Scenario A margin "&TEXT(C26,"0.0%")&" -> "&C31&". Registering the deal and consolidating freight lifts it to "&TEXT(D26,"0.0%")&" -> "&D31&", adding "&TEXT(D30-C30,"$#,##0")&" gross profit at the same customer price."')
dd["B37"].alignment = Alignment(wrap_text=True, vertical="top")
dd.merge_cells("B37:E38")
dd.row_dimensions[37].height = 30
dd["B39"] = "Note: deal desk prices at book FX with no FX buffer; for non-USD deals, add the region's buffer or set a short quote validity."
dd["B39"].font = f_sub

# ================================================================ FX_Scenario
fx = wb.create_sheet("FX_Scenario")
title(fx, "FX Scenario: how much currency movement can a list price absorb?", "Positive shock = local currency weakens (more local units per USD), so each local price is worth fewer dollars.")
fx.column_dimensions["A"].width = 4
fx.column_dimensions["B"].width = 36
for col in "CDEFG":
    fx.column_dimensions[col].width = 16
put(fx, "B4", "SKU")
put(fx, "C4", "L01", inp=True, key=True)
put(fx, "B5", "Region")
put(fx, "C5", "UK", inp=True, key=True)
dv_sku2 = DataValidation(type="list", formula1=f"={SKU_RNG}")
dv_reg2 = DataValidation(type="list", formula1=f"={REG}")
fx.add_data_validation(dv_sku2)
fx.add_data_validation(dv_reg2)
dv_sku2.add("C4")
dv_reg2.add("C5")
FKEY = '$C$4&"|"&$C$5'
put(fx, "B6", "Model")
put(fx, "C6", "=" + sku_lookup("C", "$C$4"))
put(fx, "B7", "List price (local)")
put(fx, "C7", "=" + pb_lookup("R", FKEY), NUM2)
put(fx, "B8", "Landed cost (USD)")
put(fx, "C8", "=" + pb_lookup("L", FKEY), USD2)
put(fx, "B9", "Book FX (local per USD)")
put(fx, "C9", "=" + pb_lookup("P", FKEY), NUM4)
put(fx, "B10", "Floor margin")
put(fx, "C10", "=" + pb_lookup("S", FKEY), PCT)
put(fx, "B11", "Break-even FX at floor margin")
put(fx, "C11", "=C7/(C8/(1-C10))", NUM4, bold=True)
put(fx, "B12", "FX move absorbed before hitting floor")
put(fx, "C12", "=C11/C9-1", PCT, bold=True)
fx["C12"].fill = fill_out
header(fx, 14, ["FX shock", "FX rate", "Price in USD", "Gross profit / unit (USD)", "Margin %", "Status"], col=2)
shocks = [-0.10, -0.075, -0.05, -0.025, 0, 0.025, 0.05, 0.075, 0.10]
for i, sh in enumerate(shocks):
    rr = 15 + i
    put(fx, f"B{rr}", sh, PCT, inp=True)
    put(fx, f"C{rr}", f"=$C$9*(1+B{rr})", NUM4)
    put(fx, f"D{rr}", f"=$C$7/C{rr}", USD2)
    put(fx, f"E{rr}", f"=D{rr}-$C$8", USD2)
    put(fx, f"F{rr}", f"=IF(D{rr}=0,0,E{rr}/D{rr})", PCT)
    put(fx, f"G{rr}", f'=IF(F{rr}<0,"Loss",IF(F{rr}<$C$10,"Below floor","OK"))')
fx.conditional_formatting.add("G15:G23", FormulaRule(formula=['G15<>"OK"'], fill=red))
ch = LineChart()
ch.title = "Margin % vs FX shock"
ch.y_axis.title = "Margin %"
ch.x_axis.title = "FX shock"
ch.y_axis.numFmt = "0%"
ch.add_data(Reference(fx, min_col=6, min_row=14, max_row=23), titles_from_data=True)
ch.set_categories(Reference(fx, min_col=2, min_row=15, max_row=23))
ch.height, ch.width = 7, 14
fx.add_chart(ch, "I4")

# ================================================================ Orders
od = wb.create_sheet("Orders")
title(od, "Order lines (simulated, Oct 2025 - Sep 2026)", "Columns A-Q = raw data from the 'ERP'. Columns R-AH = formulas.")
o_cols = ["Order ID", "Line", "Order date", "Month", "Customer", "Segment", "Rep", "Region", "SKU", "Qty",
          "List price (local)", "Quoted price (local)", "Approval logged", "FX book", "FX actual",
          "Book landed cost (USD)", "Actual landed cost (USD)",
          "Category", "Discount %", "Revenue at list, book FX", "Revenue at book FX", "Discount impact",
          "Revenue (USD)", "FX impact", "Book COGS", "Actual COGS", "Cost variance", "Gross profit",
          "Margin %", "Target margin", "Floor margin", "Below floor", "Unapproved below floor", "Shortfall vs target"]
header(od, 4, o_cols, widths=[10, 5, 11, 9, 9, 11, 6, 7, 6, 7] + [11] * 24)
raw_cols = ["order_id", "line_no", "order_date", "month", "customer_id", "segment", "rep", "region", "sku", "qty",
            "list_price_local", "quoted_price_local", "approval_logged", "fx_book", "fx_actual",
            "book_landed_cost_usd", "actual_landed_cost_usd"]
raw_fmt = [None, None, None, None, None, None, None, None, None, NUM, NUM2, NUM2, None, NUM4, NUM4, USD2, USD2]
data_font = Font(name=FONT, size=9, color=BLACK)
link_font = Font(name=FONT, size=9, color=GREEN)
for i, rec in enumerate(orders[raw_cols].itertuples(index=False)):
    rr = 5 + i
    for j, val in enumerate(rec):
        c = od.cell(row=rr, column=j + 1, value=val.item() if hasattr(val, "item") else val)
        c.font = data_font
        if raw_fmt[j]:
            c.number_format = raw_fmt[j]
    f = {
        "R": ("=" + sku_lookup("D", f"$I{rr}"), None, True),
        "S": (f"=IF(K{rr}=0,0,1-L{rr}/K{rr})", PCT, False),
        "T": (f"=J{rr}*K{rr}/N{rr}", USD, False),
        "U": (f"=J{rr}*L{rr}/N{rr}", USD, False),
        "V": (f"=U{rr}-T{rr}", USD, False),
        "W": (f"=J{rr}*L{rr}/O{rr}", USD, False),
        "X": (f"=W{rr}-U{rr}", USD, False),
        "Y": (f"=J{rr}*P{rr}", USD, False),
        "Z": (f"=J{rr}*Q{rr}", USD, False),
        "AA": (f"=Y{rr}-Z{rr}", USD, False),
        "AB": (f"=W{rr}-Z{rr}", USD, False),
        "AC": (f"=IF(W{rr}=0,0,AB{rr}/W{rr})", PCT, False),
        "AD": ("=" + cat_lookup("B", f"$R{rr}"), PCT, True),
        "AE": ("=" + cat_lookup("C", f"$R{rr}"), PCT, True),
        "AF": (f"=IF(AC{rr}<AE{rr},1,0)", NUM, False),
        "AG": (f'=IF(AND(AF{rr}=1,M{rr}="N"),1,0)', NUM, False),
        "AH": (f"=MAX(0,W{rr}*AD{rr}-AB{rr})", USD, False),
    }
    for col, (form, fmt, is_link) in f.items():
        c = od[f"{col}{rr}"]
        c.value = form
        c.font = link_font if is_link else data_font
        if fmt:
            c.number_format = fmt
OD_LAST = 4 + len(orders)
od.freeze_panes = "B5"
od.auto_filter.ref = f"A4:AH{OD_LAST}"


def O(col):
    return f"Orders!${col}$5:${col}${OD_LAST}"


# ================================================================ Margin_Leakage
ml = wb.create_sheet("Margin_Leakage")
title(ml, "Margin Leakage Analysis", "Where did margin go between the price book and the invoice? All numbers in USD, from the Orders sheet.")
ml.column_dimensions["A"].width = 34
for col in "BCDEFGHIJKL":
    ml.column_dimensions[col].width = 14

ml["A4"] = "1. Margin bridge: list price -> actual gross profit"
ml["A4"].font = f_sec
header(ml, 5, ["Step", "USD", "% of revenue at list"])
bridge = [
    ("Gross profit at list price (book cost & FX)", f"=SUM({O('T')})-SUM({O('Y')})"),
    ("  - Discounts given", f"=SUM({O('V')})"),
    ("      of which: unapproved below-floor lines", f"=SUMIFS({O('V')},{O('AG')},1)"),
    ("  - Vendor cost increases not in price book", f"=SUM({O('AA')})"),
    ("  - FX movement vs book rate", f"=SUM({O('X')})"),
    ("Actual gross profit", "=B6+B7+B9+B10"),
    ("Check: equals sum of order-line gross profit (should be 0)", f"=ROUND(B11-SUM({O('AB')}),2)"),
]
for i, (lab, form) in enumerate(bridge):
    rr = 6 + i
    put(ml, f"A{rr}", lab, bold=rr in (6, 11))
    put(ml, f"B{rr}", form, USD, bold=rr in (6, 11))
    put(ml, f"C{rr}", f"=IF(SUM({O('T')})=0,0,B{rr}/SUM({O('T')}))", PCT)
    for col in "ABC":
        ml[f"{col}{rr}"].border = box
ml["A12"].font = f_sub
ml["B12"].font = Font(name=FONT, size=9, color=GREEN)

ml["E4"] = "Headline KPIs"
ml["E4"].font = f_sec
kpis = [
    ("Revenue (USD)", f"=SUM({O('W')})", USD),
    ("Gross profit (USD)", f"=SUM({O('AB')})", USD),
    ("Gross margin %", "=IF(F5=0,0,F6/F5)", PCT),
    ("Target margin % (revenue-weighted)", f"=IF(F5=0,0,SUMPRODUCT({O('W')},{O('AD')})/F5)", PCT),
    ("Shortfall vs target (USD)", f"=SUM({O('AH')})", USD),
    ("Order lines below floor", f"=SUM({O('AF')})", NUM),
    ("  of which no approval logged", f"=SUM({O('AG')})", NUM),
    ("Revenue on unapproved below-floor lines", f"=SUMIFS({O('W')},{O('AG')},1)", USD),
]
for i, (lab, form, fmt) in enumerate(kpis):
    rr = 5 + i
    put(ml, f"E{rr}", lab)
    put(ml, f"F{rr}", form, fmt, bold=True)
    ml[f"F{rr}"].fill = fill_out
ml.column_dimensions["E"].width = 34


def breakdown(start_row, title_txt, key_col, keys, extra_disc=False):
    ml[f"A{start_row}"] = title_txt
    ml[f"A{start_row}"].font = f_sec
    cols = ["", "Revenue", "Gross profit", "Margin %", "Target %", "Gap (pts)", "Shortfall vs target",
            "Discount impact", "Cost variance", "FX impact", "Lines below floor", "Unapproved"]
    header(ml, start_row + 1, cols)
    for i, k in enumerate(keys):
        rr = start_row + 2 + i
        crit = f'{O(key_col)},$A{rr}'
        put(ml, f"A{rr}", k)
        put(ml, f"B{rr}", f"=SUMIFS({O('W')},{crit})", USD)
        put(ml, f"C{rr}", f"=SUMIFS({O('AB')},{crit})", USD)
        put(ml, f"D{rr}", f"=IF(B{rr}=0,0,C{rr}/B{rr})", PCT, bold=True)
        put(ml, f"E{rr}", f"=IF(B{rr}=0,0,SUMPRODUCT(({O(key_col)}=$A{rr})*{O('W')}*{O('AD')})/B{rr})", PCT)
        put(ml, f"F{rr}", f"=(D{rr}-E{rr})*100", '0.0;(0.0);"-"')
        put(ml, f"G{rr}", f"=SUMIFS({O('AH')},{crit})", USD)
        put(ml, f"H{rr}", f"=SUMIFS({O('V')},{crit})", USD)
        put(ml, f"I{rr}", f"=SUMIFS({O('AA')},{crit})", USD)
        put(ml, f"J{rr}", f"=SUMIFS({O('X')},{crit})", USD)
        put(ml, f"K{rr}", f"=SUMIFS({O('AF')},{crit})", NUM)
        put(ml, f"L{rr}", f"=SUMIFS({O('AG')},{crit})", NUM)
    last = start_row + 1 + len(keys)
    ml.conditional_formatting.add(f"F{start_row+2}:F{last}", CellIsRule(operator="lessThan", formula=["-1"], fill=red))
    return start_row + 2, last


reg_first, reg_last = breakdown(15, "2. By region", "H", list(regions.region))
cat_first, cat_last = breakdown(reg_last + 3, "3. By category", "R", list(categories.category))
rep_first, rep_last = breakdown(cat_last + 3, "4. By sales rep", "G", sorted(orders.rep.unique()))
mon_first, mon_last = breakdown(rep_last + 3, "5. By month", "D", sorted(orders.month.unique()))

# charts
c1 = BarChart()
c1.type = "bar"
c1.title = "Shortfall vs target margin by region (USD)"
c1.add_data(Reference(ml, min_col=7, min_row=reg_first - 1, max_row=reg_last), titles_from_data=True)
c1.set_categories(Reference(ml, min_col=1, min_row=reg_first, max_row=reg_last))
c1.legend = None
c1.height, c1.width = 7, 14
ml.add_chart(c1, "N4")

c2 = LineChart()
c2.title = "Gross margin % by month vs target"
c2.add_data(Reference(ml, min_col=4, max_col=5, min_row=mon_first - 1, max_row=mon_last), titles_from_data=True)
c2.set_categories(Reference(ml, min_col=1, min_row=mon_first, max_row=mon_last))
c2.y_axis.numFmt = "0%"
c2.height, c2.width = 7, 14
ml.add_chart(c2, "N20")

c3 = BarChart()
c3.title = "Gross margin % by sales rep vs target"
c3.add_data(Reference(ml, min_col=4, max_col=5, min_row=rep_first - 1, max_row=rep_last), titles_from_data=True)
c3.set_categories(Reference(ml, min_col=1, min_row=rep_first, max_row=rep_last))
c3.y_axis.numFmt = "0%"
c3.height, c3.width = 7, 14
ml.add_chart(c3, "N36")

# ================================================================ Assortment
# Row order = category, then revenue (descending) — computed here only to sort; values stay formulas.
o2 = orders.merge(skus[["sku", "category"]], on="sku")
o2["rev"] = o2.qty * o2.quoted_price_local / o2.fx_actual
rev_by_sku = o2.groupby("sku").rev.sum()
srt = skus.assign(rev=skus.sku.map(rev_by_sku).fillna(0),
                  cat_order=skus.category.map({"Laptop": 0, "Monitor": 1, "Accessory": 2}))
srt = srt.sort_values(["cat_order", "rev"], ascending=[True, False]).reset_index(drop=True)

asr = wb.create_sheet("Assortment")
title(asr, "Assortment: ABC by category + recommendation", "Sorted by category, then revenue. ABC thresholds and the low-volume rule live on Assumptions.")
a_cols = ["SKU", "Model", "Category", "Tier", "Lifecycle", "Units", "Revenue (USD)", "Gross profit (USD)", "Margin %",
          "Target margin", "Cum. revenue share in category", "ABC", "Share of category units", "SKUs in same tier",
          "Recommendation"]
header(asr, 4, a_cols, widths=[7, 36, 10, 11, 9, 9, 13, 13, 9, 9, 12, 6, 11, 9, 40])
A_FIRST = 5
A_LAST = 4 + len(srt)
for i, s in srt.iterrows():
    rr = 5 + i
    put(asr, f"A{rr}", s.sku)
    put(asr, f"B{rr}", "=" + sku_lookup("C", f"$A{rr}"))
    put(asr, f"C{rr}", "=" + sku_lookup("D", f"$A{rr}"))
    put(asr, f"D{rr}", "=" + sku_lookup("E", f"$A{rr}"))
    put(asr, f"E{rr}", "=" + sku_lookup("F", f"$A{rr}"))
    put(asr, f"F{rr}", f"=SUMIFS({O('J')},{O('I')},$A{rr})", NUM)
    put(asr, f"G{rr}", f"=SUMIFS({O('W')},{O('I')},$A{rr})", USD)
    put(asr, f"H{rr}", f"=SUMIFS({O('AB')},{O('I')},$A{rr})", USD)
    put(asr, f"I{rr}", f"=IF(G{rr}=0,0,H{rr}/G{rr})", PCT)
    put(asr, f"J{rr}", "=" + cat_lookup("B", f"$C{rr}"), PCT)
    put(asr, f"K{rr}", f"=IF(SUMIFS($G${A_FIRST}:$G${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr})=0,0,"
                       f"SUMIFS($G${A_FIRST}:G{rr},$C${A_FIRST}:C{rr},C{rr})/SUMIFS($G${A_FIRST}:$G${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr}))", PCT)
    # A SKU is class A if the share BEFORE it is still under the A threshold (so the #1 SKU is always A).
    put(asr, f"L{rr}", f"=IF(K{rr}-IF(SUMIFS($G${A_FIRST}:$G${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr})=0,0,G{rr}/SUMIFS($G${A_FIRST}:$G${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr}))<Assumptions!$C$20,\"A\","
                       f"IF(K{rr}-IF(SUMIFS($G${A_FIRST}:$G${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr})=0,0,G{rr}/SUMIFS($G${A_FIRST}:$G${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr}))<Assumptions!$C$21,\"B\",\"C\"))", bold=True)
    put(asr, f"M{rr}", f"=IF(SUMIFS($F${A_FIRST}:$F${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr})=0,0,F{rr}/SUMIFS($F${A_FIRST}:$F${A_LAST},$C${A_FIRST}:$C${A_LAST},C{rr}))", PCT)
    put(asr, f"N{rr}", f"=COUNTIFS($C${A_FIRST}:$C${A_LAST},C{rr},$D${A_FIRST}:$D${A_LAST},D{rr})", NUM)
    put(asr, f"O{rr}",
        f'=IF(E{rr}="EOL","Phase out: end of life, move demand to current gen",'
        f'IF(AND(L{rr}="C",N{rr}>1,M{rr}<Assumptions!$C$22),"Consolidate: low volume, duplicate of same tier",'
        f'IF(I{rr}<J{rr}-Assumptions!$C$23,"Below target: reprice or renegotiate cost",'
        f'IF(L{rr}="A","Preferred: negotiate volume rebate","Keep"))))')
asr.conditional_formatting.add(f"O{A_FIRST}:O{A_LAST}", FormulaRule(formula=[f'OR(LEFT(O{A_FIRST},5)="Phase",LEFT(O{A_FIRST},5)="Below")'], fill=red))
asr.conditional_formatting.add(f"O{A_FIRST}:O{A_LAST}", FormulaRule(formula=[f'LEFT(O{A_FIRST},5)="Conso"'], fill=amber))
asr.conditional_formatting.add(f"O{A_FIRST}:O{A_LAST}", FormulaRule(formula=[f'LEFT(O{A_FIRST},5)="Prefe"'], fill=green_f))
asr.conditional_formatting.add(f"I{A_FIRST}:I{A_LAST}", FormulaRule(formula=[f"I{A_FIRST}<J{A_FIRST}-Assumptions!$C$23"], font=Font(name=FONT, color="C00000", bold=True)))
asr.freeze_panes = "C5"
asr[f"A{A_LAST+2}"] = "Red margin = more than the tolerance (Assumptions C23) below category target. ABC is computed within each category so accessories are not all 'C' next to laptops."
asr[f"A{A_LAST+2}"].font = f_sub

# ================================================================ README live KPIs
kp = [
    ("Revenue (USD)", "=Margin_Leakage!F5", USD),
    ("Gross margin %", "=Margin_Leakage!F7", PCT),
    ("Target margin % (weighted)", "=Margin_Leakage!F8", PCT),
    ("Shortfall vs target (USD)", "=Margin_Leakage!F9", USD),
    ("Discount impact (USD)", "=Margin_Leakage!B7", USD),
    ("Cost increases not repriced (USD)", "=Margin_Leakage!B9", USD),
    ("FX impact (USD)", "=Margin_Leakage!B10", USD),
]
for i, (lab, form, fmt) in enumerate(kp):
    rr = kpi_start + i
    put(rd, f"A{rr}", lab)
    put(rd, f"B{rr}", form, fmt, bold=True)
    rd[f"B{rr}"].alignment = Alignment(horizontal="left")

# Ask Excel to recalculate everything on open.
wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print("saved", OUT)

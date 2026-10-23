-- B2B pricing & margin project: schema (SIMULATED data)
-- Tested in SQLite 3.45. Standard SQL, so it also runs in PostgreSQL with minor type changes.

DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS sku_master;
DROP TABLE IF EXISTS price_book;
DROP TABLE IF EXISTS orders;

CREATE TABLE regions (
    region             TEXT PRIMARY KEY,
    currency           TEXT,
    fx_book            REAL,     -- local currency per 1 USD used to build the price book
    duty_pct           REAL,
    fx_buffer_pct      REAL,
    freight_laptop     REAL,     -- USD per unit
    freight_monitor    REAL,
    freight_accessory  REAL
);

CREATE TABLE categories (
    category           TEXT PRIMARY KEY,
    target_margin      REAL,
    floor_margin       REAL,
    list_headroom_pct  REAL
);

CREATE TABLE sku_master (
    sku               TEXT PRIMARY KEY,
    oem               TEXT,
    model             TEXT,
    category          TEXT REFERENCES categories(category),
    tier              TEXT,
    lifecycle         TEXT,
    vendor_cost_usd   REAL,
    base_rebate_pct   REAL
);

CREATE TABLE price_book (
    sku                   TEXT REFERENCES sku_master(sku),
    region                TEXT REFERENCES regions(region),
    book_landed_cost_usd  REAL,
    list_price_local      REAL,
    floor_price_local     REAL,
    PRIMARY KEY (sku, region)
);

CREATE TABLE orders (
    order_id                TEXT,
    line_no                 INTEGER,
    order_date              TEXT,
    month                   TEXT,     -- 'YYYY-MM'
    customer_id             TEXT,
    segment                 TEXT,
    rep                     TEXT,
    region                  TEXT REFERENCES regions(region),
    sku                     TEXT REFERENCES sku_master(sku),
    qty                     INTEGER,
    list_price_local        REAL,
    quoted_price_local      REAL,
    approval_logged         TEXT,     -- 'Y' if a special-price approval was recorded
    fx_book                 REAL,
    fx_actual               REAL,
    book_landed_cost_usd    REAL,     -- cost the quote assumed
    actual_landed_cost_usd  REAL,     -- cost we actually paid
    PRIMARY KEY (order_id, line_no)
);

-- Index the columns used in joins and filters.
CREATE INDEX idx_orders_sku    ON orders(sku);
CREATE INDEX idx_orders_region ON orders(region);
CREATE INDEX idx_orders_month  ON orders(month);

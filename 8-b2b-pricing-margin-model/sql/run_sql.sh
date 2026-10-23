#!/bin/bash
# Build pricing.db from data/*.csv and run every analysis query.
# Usage (from the project folder):  bash sql/run_sql.sh
set -e
cd "$(dirname "$0")/.."
rm -f pricing.db
sqlite3 pricing.db < sql/01_schema.sql
for t in regions categories sku_master price_book orders; do
  sqlite3 pricing.db ".import --csv --skip 1 data/$t.csv $t"
done
sqlite3 -header -column pricing.db < sql/02_analysis.sql

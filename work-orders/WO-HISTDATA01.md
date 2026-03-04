# WO-HISTDATA01: Fix Historical Data Loading
**P0** | File: src/engine/market_data_service.py | Gatekeeper: Risto

## Problem
1. SQLite path wrong: points to printer2/data/market_data.db (MISSING). Real: brrr-data/market_data.db (643MB)
2. DataHub fallback limit=500: 500 1m bars = ~100 5m. topstep_aplus needs 210.

## Fix 1: SQLite path (line 35)
BEFORE: os.path.join(PROJECT_ROOT, "data", "market_data.db")
AFTER: os.environ.get("MARKET_DATA_DB", os.path.join(PROJECT_ROOT, "..", "brrr-data", "market_data.db"))

## Fix 2: DataHub limit (line 420)
BEFORE: limit=500
AFTER: limit=1500 (300 5m bars, covers all strategies)

## Fix 3: Health diagnostics (_check_historical_data_health ~line 310)
ADD: per-symbol/tf bar count logging after health check

## DO NOT: symlink, change sqlite loader, change min_bars, start engine without TopStepX check

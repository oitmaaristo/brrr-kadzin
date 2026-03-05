# WO-BACKFILL-MGC: MGC/MNQ 60m Forward-Fill Fix
**P2** | brrr-printer2 + brrr-data | Gatekeeper: Risto

## Kontekst
MGC 1m OK (754k bari). Gap 10:58->18:00 UTC = NORMAALNE settlement paus. MNQ paus 21:15-21:30 UTC.

## Probleem
market_data_service.py aggregeerib 1m->60m. Settlement pausis tehakse forward-filled barrid.
Tulemus: 60m chart horisontaalne joon kus peaks olema gap.

## Fix 1: Leia forward-fill koht
Leia market_data_service.py aggregation loogikast kus forward-fill juhtub.

## Fix 2: Settlement paus filter
MGC: 16:00-18:00 UTC | MNQ: 21:15-21:30 UTC
Periood pausis -> jata baar loomata. Osaliselt pausis -> ainult pausivalised minutid.

## Fix 3: Backfill
1. Tuvasta forward-filled barrid (volume=0 voi open=high=low=close pausis)
2. Kustuta ohlcv_MGC_60m ja ohlcv_MNQ_60m vallatavad read
3. Regenereeri korrektsed barrid 1m andmetest

## EI TOHI
Muuta 1m andmeid, kustutada barre valjaspool pausit, restartida engine.

## Testimine
SELECT timestamp FROM ohlcv_MGC_60m
WHERE timestamp BETWEEN 2026-01-05 15:00:00 AND 2026-01-05 19:00:00
-- tulemusi ei tohi olla

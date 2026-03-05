# WO-TRADE-SLTP: Tehingud Salvestada Koos SL/TP Vaartustega
**P2** | brrr-printer2 | Gatekeeper: Risto

## Probleem
Suletud tehingud salvestatakse realized_pnl-iga aga SL/TP ei salvestata.
Replay ei saa rekonstrueerida mis SL/TP-ga trade tehti.

## Fix 1: DB migration (IF NOT EXISTS)
Lisa positions + closed_positions tabelitesse:
intended_sl_ticks, intended_tp_ticks, intended_sl_price, intended_tp_price

## Fix 2: bracket_executor.py
Kirjuta SL/TP DB-sse kohe positsiooni avamisel.

## Fix 3: position_storage.py
close_position(): salvesta SL/TP closed_positions tabelisse.

## Testimine
SELECT * FROM closed_positions -- sl/tp veerud peavad olema taidetud.

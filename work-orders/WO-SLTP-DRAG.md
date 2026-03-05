# WO-SLTP-DRAG: SL/TP Jooned Graafikul Lohistatavaks
**P3** | brrr-printer2 src/dashboard/ | Gatekeeper: Risto
**BLOCKED: vajab WO-SLTP valmimist esmalt**

## Soov
HITLab graafikul SL/TP horisontaaljooned lohistatavaks.
Trader tostab joont -> engine uuendab bracket orderi reaalajas.

## Fix 1: Frontend
Drag handler SL/TP joontele (TradingView Lightweight Charts price line drag).

## Fix 2: API endpoint
POST /api/positions/<id>/adjust body: {sl_price, tp_price}

## Fix 3: Backend
bracket_executor.modify_bracket(position_id, new_sl, new_tp)

## Fix 4: Valideerimine
SL max 2x ATR entry vastu. TP min 0.5x ATR entry suunas.

## Soltuvus
WO-SLTP peab olema done enne seda.

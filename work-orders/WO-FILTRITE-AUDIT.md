# WO-FILTRITE-AUDIT: Filtrite Audit ja Test
**P2** | signal_filters.py | Gatekeeper: Risto

## Eesmarg
Kontrollida et koik kasutuses olevad filtrid teeksid seda mida nad tegema peaksid.
Kasutada: kirjutaja -> 2x review -> testija -> gatekeeper loopi.

## Filtrid (filter_config.json)
market_hours, session_windows, vol_spike, exhaustion, rsi, adx, momentum, daily_loss, regime

## Ulesoanded
1. Iga filtri kohta: loe kood + config, kirjuta mis peaks juhtuma
2. Lisa ajutine verbose logi igasse filtrisse
3. Kaivita engine --no-trading 30min, kogu filter otsused logist
4. Vorrda expected vs actual - leia lahknevused
5. Paranda valed filtrid, dokumenteeri

## EI TOHI
HMM filtrit puutuda (eraldi WO-HMM01)
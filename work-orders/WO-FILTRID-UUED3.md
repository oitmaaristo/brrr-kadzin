# WO-FILTRID-UUED3: 3 Uut Pre-Execution Filtrit
P2 | src/engine/signal_filters.py + data/filter_config.json | Gatekeeper: Risto

Viide uuringule: brrr-printer2/docs/TEGEVUSKAVA-SIGNAL-QUALITY.md
(Seal on taustainfo filtrite disaini kohta, ensemble loogika, Feb17 analyys)

Branch: auto-claude/wo-filtrid-uued3

## Filter 1: HTF Trend Alignment
"Kas suur pilt on sama meelt?"
Kui 5m ütleb osta aga 60m on selgelt langustrendis -> blokeeri.
Ainult kauple suunas kuhu ka suurem TF vaatab.
Implement: kontrolli 60m EMA suund vs signaali suund.
Toggle + konfigureeritav TF paar dashboardist.

## Filter 2: RVOL Gate
"Kas keegi uldse kaupleb praegu?"
Kui kauplemismaht on tavapärasest palju vahem (nt alla 50
## Filter 2: RVOL Gate
"Kas keegi kaupleb praegu?"
Kui maht on alla 50 protsendi 20-bari keskmisest -> signaal blokeeritud.
Vaikne turg = juhuslik hinnaliikumine, suured tegijad pole kohal.
Implement: current volume vs 20-bar rolling average. Threshold konfigureeritav.
Toggle dashboardist.

## Filter 3: ORB Extension Gate
"Ara jookse rongi jargi mis juba laks."
Kui hind on juba liiga kaugele liikunud opening range breakout punktist,
siis signaal blokeeritud - momentum on ammendunud.
Implement: arvuta ORB (esimese N minuti high/low), blokeeri kui hind
on juba uldelnud X ATR ORB-ist kaugemale.
Toggle + N minutit + X ATR threshold konfigureeritav dashboardist.

## Nouded
- Iga filter: eraldi toggle dashboardis (nagu olemasolevad filtrid)
- Iga filter: BLOCK või WARN mode valitav
- Iga filter: parameetrid muudetavad dashboardist (filter_config.json kaudu)
- Testid: min 10 testi filtri kohta
- Ei muuda olemasolevate filtrite loogikat

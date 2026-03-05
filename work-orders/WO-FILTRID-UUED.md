# WO-FILTRID-UUED: 3 Uue Filtri Uuring ja Valik
**P3** | src/engine/ | Gatekeeper: Risto

## Eesmarg
Uuri ja vali 3 filtrit mida saaksime lisada. Parem win rate voi profit factor.

## Kriteeriumid
- Tootavad futuuridel (MGC, MNQ)
- Ei duplikeeri olemasolevaid (ADX, RSI, vol_spike, HMM juba olemas)
- Implementeeritavad hmmlearn/pandas/ta-lib-ga

## Kandidaadid (uurida)
- Order flow delta / bid-ask imbalance
- Intermarket korrelatsioon: GC vs MGC, NQ vs MNQ
- Time-of-day seasonality: parim kauplemisaeg per strateegia
- VIX tase filter (CBOE VIX)

## Output
Kirjuta /home/brrr/brrr-kadzin/docs/filter-research.md
3 soovitust koos: kirjeldus, implementatsiooni skits, eeldatav moju
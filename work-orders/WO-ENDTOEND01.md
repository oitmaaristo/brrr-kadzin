# WO-ENDTOEND01: End-to-End Printer Validation + Strategy Live Stats

**Prioriteet:** P1  
**Projekt:** brrr-printer2  
**Branch:** auto-claude/wo-endtoend01  
**Kirjutaja:** Claudia 2026-03-06

---

## KONTEKST

Eile mergiti 15+ WO-d: startup, positsioonide käsitlemine, SL/TP, safety, filtrid, HMM, dashboard.
Ükski neist pole end-to-end valideeritud — käivitusest kuni strateegia statistika salvestuseni.

Lisaks: `data/strategy_library/*.json` failides `"live": {"net": 0, "winRate": 0, "pf": 0, "trades": 0}` —
live trade statistika ei koguta ega salvestata strateegiate kaupa. `position_storage.py` teab
`strategy_id` per trade, aga `StrategyLibrary` ei kasuta seda.

---

## SCOPE

### A) Live strategy stats kogumine (koodimuudatus)

1. `StrategyLibrary` loeb `closed_positions` tabelist live stats per `strategy_id`
2. Arvuta per strateegia: `net_pnl`, `win_rate`, `profit_factor`, `total_trades`, `avg_win`, `avg_loss`
3. Salvesta strateegia JSON-i `live_results` blokki (ei puuduta `backtest_results`)
4. `/api/strategies/library` tagastab reaalsed live numbrid, mitte nullid
5. Dashboard Strategies lehel kuvatakse live stats õigesti (BT/Live kõrvuti juba olemas UI-s)

### B) End-to-end pipeline valideerimine

Kogu printer flow peab olema valideeritud:
- Signaal genereeritakse (signal_generator.py + filtrid → HMM → RSI → etc)
- Order saadetakse (bracket_executor.py → REST API)
- Position trackitakse (position_monitor.py + data_cache.py)
- Position sulgub → close_reason salvestub
- Trade salvestub DB-sse: strategy_id + timeframe + intended_sl/tp + close_reason
- Live stats uuendatakse strategy_library JSON-is
- Dashboard kuvab kõike õigesti

---

## PIPELINE

```
WRITER → REVIEWER-FUNC → REVIEWER-UI → FIX-FUNC → FIX-UI → TESTER-FUNC → TESTER-UI → GATEKEEPER-FUNC → GATEKEEPER-UI → FINAL
```

---

### WRITER

Implementeerib scope A:
- `src/strategies/library.py` — lisa `compute_live_stats(strategy_id)` meetod
- `src/dashboard/blueprints/api.py` — `/api/strategies/library` täidab `live: {}` päris andmetega
- `data/strategy_library/*.json` — saavad `live_results: {}` bloki
- `tests/test_live_strategy_stats.py` — uus testifail

Edge cases mida WRITER PEAB katma:
- 0 trades → live_results kõik nullid, ei crashita
- Ainult losing trades → profit_factor = 0 (mitte division by zero)
- strategy_id on None (vanad tradid) → fallback strategy_name järgi
- JSON kirjutamine ebaõnnestub → logi warning, ära crashita engine't

Push branch, ÄRA merge main.

---

### REVIEWER-FUNC (funktsionaalne review)

Kontrollib:
- SQL päringud live stats arvutamiseks on korrektsed
- win_rate / profit_factor arvutus on õige (edge cases: 0 trades, ainult kaotused)
- strategy_id match toimib õigesti
- JSON kirjutamine on atomic (ei riku backtest_results)
- Puuduvad testid?

Väljund: `review/WO-ENDTOEND01-func-review.md`
EI PARANDA — ainult dokumenteerib.

---

### REVIEWER-UI (UI/UX review — inimese vaatenurk)

Avab dashboard `localhost:8373`, käib läbi KÕIk lehed nagu kasutaja:

1. **Overview/Index** — balance, DD, positsioonid — kas numbrid on mõistlikud ja ühikutega?
2. **Positions** — aktiivsed positsioonid, SL/TP nähtav, mitte NaN/undefined
3. **Trades/History** — viimased tradid, strategy_name, close_reason, intended SL/TP
4. **Strategies** — live stats kuvatakse (mitte 0/0/0), activate/deactivate töötab
5. **Controls** — Start/Stop/Emergency visuaalselt selged, nupud annavad tagasisidet
6. **Replay** — kuupäeva valimine, tradide laadimine, equity curve
7. **Chart (hitlab)** — 1D/1W/intraday laadimine, SL/TP jooned draggable

Dokumenteerib KÕIK vead/puudused failis `review/WO-ENDTOEND01-ui-review.md`
EI PARANDA — ainult dokumenteerib.

---

### FIX-FUNC

Loeb `review/WO-ENDTOEND01-func-review.md`, parandab kõik funktsionaalsed vead, uuendab testid.

---

### FIX-UI

Loeb `review/WO-ENDTOEND01-ui-review.md`, parandab kõik UI vead.
Scope: HTML/JS/CSS ainult. Äriloogika muudatused → FIX-FUNC ülesanne.

Konkreetsed asjad mida kontrollida ja vajadusel parandada:
- Kõigil numbritel on ühikud/kontekst ($ märk, %, ticks)
- Error state'id on kasutajasõbralikud (mitte "undefined", "NaN", "null")
- Nupud annavad visuaalset tagasisidet (loading spinner, success/error state)
- Tühi olek on selge (nt "No active positions" mitte tühi tabel)
- Layout ei murra väiksemas aknas

---

### TESTER-FUNC

Käivitab: `python -m pytest tests/ -x -q`

Kontrollib spetsiifiliselt:
- Live stats arvutatakse õigesti tühja DB peal (0 trades → nullid, ei crashita)
- Live stats arvutatakse õigesti kui trades on olemas
- strategy_id match + strategy_name fallback toimib
- JSON kirjutamine ei riku backtest_results

Kui testid purunevad → `review/WO-ENDTOEND01-func-testfail.md` + PEATA pipeline.

---

### TESTER-UI (inimese simulatsioon)

Simuleerib täpset kasutaja workflow'd samm-sammult:

1. Ava dashboard → browser console — 0 JS errorit?
2. Positions → kas positsioonid kuvatakse või selge "no positions" message?
3. Strategies → kas live stats on reaalsed numbrid? Activate/deactivate nupp töötab?
4. Trades → kas viimased 10 trade'i on näha? close_reason loetav?
5. Chart → laadib? SL joon draggable?
6. Controls → Emergency Stop selgelt punane ja nähtav?
7. Replay → vali kuupäev → tradid laadivad?

Dokumenteerib KÕIK leitud probleemid failis `review/WO-ENDTOEND01-ui-testfail.md`
Kui kriitiline UI viga → PEATA pipeline.

---

### GATEKEEPER-FUNC

- `pytest tests/ -q` → 0 failures, sh uued live stats testid
- `/api/strategies/library` tagastab reaalsed live numbrid (mitte nullid) kui tradid olemas
- Strateegia JSON-ides on `live_results` blokk täidetud pärast stats update
- Kontrollib et signaal→order→position→close→DB→stats pipeline on kaetud

Blokeerimisel: `review/WO-ENDTOEND01-gk-func-block.md`

---

### GATEKEEPER-UI

Teeb viimase käigu läbi kogu dashboardi. Küsib: "Kas uus kasutaja saab sellest aru ilma juhendita?"

Kontrollib:
- Kõigil numbritel on ühikud ja kontekst
- Error state'id on kasutajasõbralikud
- Kõik 7 lehte laadivad ilma JS errorita
- Nupud annavad tagasisidet
- Layout ei murra väiksemas aknas

Blokeerimisel: `review/WO-ENDTOEND01-gk-ui-block.md`

---

### FINAL (ainult kui mõlemad gatekeeperid on OK)

- Merge branch main-iga
- Kustuta review/ temp failid
- Flux kaart → done

---

## LIVE STATS STRUKTUUR (JSON)

```json
"live_results": {
  "net_pnl": 127.50,
  "win_rate": 0.62,
  "profit_factor": 1.8,
  "total_trades": 13,
  "avg_win": 24.30,
  "avg_loss": -14.20,
  "last_updated": "2026-03-06T10:00:00"
}
```

---

## TÄPSED FAILID MIS MUUTUVAD

```
src/strategies/library.py                  — compute_live_stats() meetod
src/dashboard/blueprints/api.py            — live stats päris andmetega
data/strategy_library/*.json               — live_results blokk
tests/test_live_strategy_stats.py          — uus testifail
```

Kõik muud failid ainult FIX-FUNC / FIX-UI raames kui reviewer leidis konkreetse vea.

---

## DEFINITSIOON "DONE"

- [ ] `pytest tests/ -q` → 0 failures, sh uued live stats testid
- [ ] `/api/strategies/library` → reaalsed live numbrid kui trades olemas
- [ ] Strategies leht näitab live stats (mitte 0/0/0)
- [ ] UI tester kinnitab: kõik 7 lehte laadivad ilma JS errorita
- [ ] GATEKEEPER-FUNC kirjalikult kinnitanud
- [ ] GATEKEEPER-UI kirjalikult kinnitanud
- [ ] Branch merged main-iga

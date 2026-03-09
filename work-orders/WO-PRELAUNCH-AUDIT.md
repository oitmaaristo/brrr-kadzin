# WO-PRELAUNCH-AUDIT: Printer2 käivituseelne täisaudit

**Prioriteet:** P1 | **Branch:** auto-claude/wo-prelaunch-audit | **Gatekeeper:** Risto
**Kontekst:** TopStepX API key aegunud, kasutame pausi auditi jaoks

---

## EESMÄRK

Veendu et Printer2 on 100% valmis printima kohe kui uus API key on olemas.
Kõik mis saab teha ilma live API-ta — tee ära.

---

## OSA 1: KNOWN ISSUES FIX

### 1.1 Screenshot cron timeout fix
- Cron `*/5 * * * *` jookseb Playwright screenshot scripti
- Fail: timeout `.header-balance` selectoril kui dashboard ei saa andmeid
- **Fix:** `ops/scripts/screenshot_dashboard.py` — lisa timeout handling, ära crashi kui dashboard on ilma datata
- Testi: `python ops/scripts/screenshot_dashboard.py` ei crashi ka ilma live datata

### 1.2 Emergency false positive verifitseerimine
- Commit `82ae7ae` parandas stale HWM — verifitseeri et fix on main-is ja töötab
- Kontrolli `emergency.log` — pole uusi false positive triggereid pärast fixi
- Kontrolli et emergency state on puhas (reset tehtud)

### 1.3 Dashboard auth loop
- Dashboard jookseb aga logib `Auth failed (errorCode: 3)` iga 5 sek
- **Fix:** Dashboard peaks gracefully käsitlema expired token — näita "API key expired" sõnumit, mitte loopi
- Fail: `src/dashboard/` — lisa token expiry handling

---

## OSA 2: TESTIDE LÄBIJOOKSUTAMINE

### 2.1 Unit testid
```bash
cd /home/brrr/brrr-printer2
python -m pytest ops/tests/ -v --tb=short 2>&1 | tee /tmp/audit-tests.log
```
- Dokumenteeri: mitu testi, mitu PASS, mitu FAIL, mitu SKIP
- Iga FAIL-i kohta: root cause + fix (kui lihtne) või eskaleeri

### 2.2 Integration testid
```bash
python -m pytest ops/tests/integration/ -v --tb=short 2>&1 | tee /tmp/audit-integration.log
```

### 2.3 Code quality
```bash
python -m ruff check src/ --statistics
python -m black src/ --check --diff
```
- Paranda kõik ruff warningud
- Paranda kõik black formatting probleemid

---

## OSA 3: PLAYWRIGHT UI/UX AUDIT

### 3.0 Playwright setup
- Playwright 1.58.0 on juba installitud
- Kontrolli et browserid on installitud: `python -m playwright install chromium`
- Kui vaja, installi puuduvad sõltuvused

### 3.1 Dashboard smoke test
Kirjuta `ops/tests/playwright/test_dashboard_smoke.py`:

```python
# Testi kõik dashboard route'id (ka ilma live datata):
# - / (index) — laeb, pole JS erroreid
# - /positions — laeb
# - /alerts — laeb
# - /analytics — laeb
# - /controls — laeb
# - /filters — laeb
# - /performance — laeb
# - /reports — laeb
# - /hitlab — laeb
# - /health — tagastab 200
```

Iga route kohta kontrolli:
- HTTP 200
- Pole console.error-eid (JS vead)
- Pole unhandled exception bannereid
- Pealkiri/header renderib

### 3.2 Dashboard UX kontroll
Kirjuta `ops/tests/playwright/test_dashboard_ux.py`:

- Navigatsioon: kõik menüü lingid töötavad
- Responsive: test 1920x1080 ja 1366x768
- Socket.IO: ühenduse staatus nähtav (kas connected/disconnected)
- Dark/light mode (kui on)
- Tabelid: renderivad ka tühjade andmetega (pole broken layout)

### 3.3 Screenshot baseline
- Tee screenshot igast route'ist (1920x1080)
- Salvesta: `data/screenshots/audit/` kausta
- See on baseline edaspidiseks visuaalseks regressioonitestiks

---

## OSA 4: SÜSTEEMI TERVIKLIKKUS

### 4.1 DB skeemi kontroll
```bash
sqlite3 data/datahub.db ".schema" > /tmp/audit-db-schema.txt
```
- Kontrolli et kõik vajalikud tabelid eksisteerivad
- Kontrolli et `closed_positions` tabelis on `strategy_id`, `timeframe`, `close_reason` väljad
- Kontrolli et migratsioonid on IF NOT EXISTS

### 4.2 Konfiguratsioon
- `.env` — kontrolli et kõik vajalikud muutujad on olemas (v.a. token mis on aegunud)
- `config/` — kontrolli strateegia konfiguratsioonid
- Systemd service failid — kontrolli et need on ajakohased

### 4.3 Sõltuvused
```bash
pip list --outdated
pip check  # kontrolli konflikte
```

### 4.4 Logide puhastus
- Arhiveeri vanad logid (>7 päeva)
- Kontrolli et log rotation on seadistatud
- Puhasta emergency state

---

## OSA 5: RESTART READINESS CHECKLIST

Koosta fail `docs/cc-vps/memory/restart-checklist.md`:

```markdown
# Restart Checklist — YYYY-MM-DD

## Enne restarti
- [ ] Uus API key `.env` failis
- [ ] Emergency state puhas
- [ ] Kõik unit testid PASS
- [ ] Dashboard UI renderib
- [ ] DB skeemid korras

## Restart järjekord
1. DataHub: `systemctl start brrr-datahub`
2. Oota 10s, kontrolli WS ühendust
3. Engine: `systemctl start brrr-engine`
4. Oota warmup (120s)
5. Dashboard: peaks juba jooksma, kontrolli andmeid
6. Kontrolli Telegram alerti: "Engine started"

## Pärast restarti
- [ ] DataHub WS connected
- [ ] Engine warmup läbitud
- [ ] Dashboard näitab balance
- [ ] Screenshot cron töötab
- [ ] 0 emergency alerts
- [ ] Esimene signaal genereeritud
```

---

## VÄLJUND

1. `docs/cc-vps/memory/YYYY-MM-DD.md` — auditi päevalogi
2. `docs/cc-vps/memory/restart-checklist.md` — restart checklist
3. `data/screenshots/audit/` — UI baseline screenshotid
4. Kõik leitud bugid parandatud või eskaleeritud
5. Testide tulemused logitud

## EI TOHI

- Startida Engine või DataHub (API key puudub)
- Muuta strateegia konfiguratsiooni
- Kustutada andmebaasi andmeid
- Force push või rebase

## ACCEPTANCE CRITERIA

- [ ] Kõik unit testid PASS (või FAIL-id dokumenteeritud + eskaleeritud)
- [ ] Ruff 0 warningut
- [ ] Playwright smoke test PASS kõigil route'idel
- [ ] Screenshot baseline olemas
- [ ] Screenshot cron ei crashi ilma datata
- [ ] Dashboard ei loopi auth error-iga
- [ ] Emergency state puhas, false positive fix verifitseeritud
- [ ] Restart checklist valmis
- [ ] DB skeemid verifitseeritud

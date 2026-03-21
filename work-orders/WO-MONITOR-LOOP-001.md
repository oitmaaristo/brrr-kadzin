# WO-MONITOR-LOOP-001: Autonoomne 15-minutiline monitor loop
**Created:** 2026-03-16
**Author:** CC Windows (HQ)
**Assignee:** CC Printer (VPS)
**Department:** printer
**Priority:** P0
**Status:** TODO

---

## Eesmärk

Ehita autonoomne monitor loop, mis töötab VPS-il 24/7 ilma Risto sekkumiseta — jälgib iga 15 minuti tagant süsteemi seisundit, leiab probleemid ja parandab need ise. Risto ei pea Windows-t lahti hoidma. Risto ei pea ise TopStepi vaatama.

## Kontekst

Praegune olukord: pärast iga bugifixi läheb tihti mitu tundi enne kui saab kontrollida, kas fix töötas. Keegi peale Risto ei vaata positsioone. On olnud juhtumeid kus positsioon on TopStepis avatud aga meie süsteem ei tea sellest — ja see võib kesta tunde. Selle WO tulemusena on keegi alati valve.

**Tehniline piirang:** Loop peab kasutama `claude -p` CLI-t (Max subscription), mitte Anthropic API-t (lisatasu). Telegram alerte ei kasutata praegu.

---

## Arhitektuur

```
CRON (iga 15 min)
    → käivitab: claude -p "$(cat ~/monitor-program.md)"
    → CC loeb süsteemi seisundit
    → leiab probleemi → spawni subagent → fix → verifitseeri
    → ei leia probleemi → logi "OK" → väljub
    → cron käivitab 15 min pärast uuesti
```

Loop ei pea jooksma pidevalt. Iga cron invocation on iseseisev — loeb hetkeseisu, tegutseb, väljub.

---

## Sammud

### 1. Uuri süsteemi seisundit ise

Enne kui midagi ehitad, vaata läbi:
- Mis API key olukord on hetkel? (töötab / demo / aegunud)
- Kas Playwright on installitud ja töötab?
- Kas TopStep positsioonide kontrolliks on juba skript olemas?
- Mis logifailid on olemas ja kus?
- Kuidas praegu SL/TP olemasolu kontrollida DB-s?
- Mis on `closed_positions` tabeli struktuur?

Kirjuta oma leiud WO lõppu "CC leiud" sektsiooni.

### 2. Kirjuta `monitor-program.md`

Fail asub: `~/monitor-program.md` (VPS, brrr kasutaja)

See on loopi "aju" — CC saab selle iga kord kui cron käivitab. Sisu peab sisaldama:

**Iga 15-minutise tsükli loogika:**

```
1. SÜSTEEMI KONTROLL
   - Kas Engine process jookseb?
   - Kas DataHub WebSocket on ühendatud?
   - Logi tulemus: ~/monitor-logs/YYYY-MM-DD.log

2. POSITSIOONIDE KONTROLL
   - Loe meie DB-st avatud positsioonid
   - Loe TopStepist avatud positsioonid (API või Playwright)
   - Kui erinevus → see on kriitiline bug → käivita fix subagent
   - Iga avatud positsioon: kas SL ja TP on olemas?
   - Puuduv SL/TP → kriitiline bug → käivita fix subagent

3. VIIMASE 15 MIN TEHINGUD
   - Kas on suletud tehinguid vahemikus (nüüd - 15min)?
   - Ei ole → logi "no trades" → lõpeta
   - On → hinda iga tehingut 5 näitaja osas (vt allpool)
   - Lisa hinnang: ~/experiments-log.md

4. LOGI JA LÕPETA
   - Kirjuta kokkuvõte: ~/monitor-logs/YYYY-MM-DD.log
   - Väljub (cron käivitab 15 min pärast uuesti)
```

**Tehingu hindamine (5 näitajat):**
```
1. Tulemus: USD +/-, % kontost
2. Kuidas suleti: SL hit / TP hit / manuaalne / muu
3. Strateegia + filter kombinatsioon (mis andis signaali)
4. Slippage: oodatud vs tegelik hind
5. DD mõju: kas drawdown läks lähemale piirile?
```

### 3. Määra selged piirid subagentidele

**Subagent VÕIB iseseisvalt parandada:**
- Order management bugid (SL/TP ei saadetud → saada uuesti)
- DB ja TopStep sünkroonimine (positsioon puudub ühel pool)
- API ühenduse taastamine kui katkes
- Logimise ja monitoring kood

**Subagent EI TOHI kunagi muuta:**
- Strateegia parameetrid ja filter loogika
- Risk limits (DD piirid, position sizing)
- .env fail
- Midagi ilma git commitita (iga muutus peab olema commititud)

**Kui subagent ei suuda parandada:**
- Logi probleem detailselt: `~/monitor-logs/ESCALATE-YYYY-MM-DD.log`
- Kirjuta Risto jaoks selge kokkuvõte: mis probleem, mis prooviti, miks ei õnnestunud
- Ära blokeeri — järgmine tsükkel proovib uuesti

### 4. Seadista cron

```bash
# brrr kasutajana VPS-il:
crontab -e

# Lisa rida:
*/15 * * * * /usr/local/bin/claude -p "$(cat /home/brrr/monitor-program.md)" >> /home/brrr/monitor-logs/cron.log 2>&1
```

**NB:** Kontrolli esmalt `which claude` — tee kindlaks täielik path.

**Turgude välisel ajal** (öö, nädalavahetus): loop võib töötada kergemas režiimis — ainult süsteemi kontroll, tehingute hindamist ei ole vaja.

### 5. Testi

- Käivita manuaalselt üks kord: `claude -p "$(cat ~/monitor-program.md)"`
- Kontrolli et logi tekib: `~/monitor-logs/YYYY-MM-DD.log`
- Kontrolli et experiments-log tekib kui on tehinguid
- Kontrolli et cron töötab: `crontab -l` ja oota 15 min

---

## Acceptance Criteria

- [ ] `monitor-program.md` on kirjutatud ja CC saab sellest aru
- [ ] Cron töötab — iga 15 min käivitub automaatselt
- [ ] Positsioonide kontroll töötab (DB vs TopStep)
- [ ] SL/TP kontroll töötab
- [ ] Tehingute hinnang kirjutatakse `experiments-log.md`-sse
- [ ] Subagendi piirid on selgelt defineeritud `monitor-program.md`-s
- [ ] Loop töötab kui Windows on kinni
- [ ] Iga muutus mida subagent teeb on git commitiga

## EI TOHI

- Kasutada Anthropic API-t (ainult `claude -p` CLI)
- Saata Telegram alerteid (praegu)
- Muuta strateegia parameetreid
- Muuta risk limite
- Töötada ilma git commitita kui muutusi teeb

---

## CC leiud (täida see osa enne ehitamist)

*CC Printer täidab siia oma leiud sammust 1:*

- API key staatus: TBD
- Playwright staatus: TBD
- Olemasolevad positsioonikontrolli skriptid: TBD
- DB struktuur (positsioonid, SL/TP väljad): TBD
- Logifailide asukoht: TBD
- `claude` binary asukoht: TBD

---

## Handoff märkmed

- See WO kirjutati CC Windows poolt, CC Printer viib ellu
- Risto tahab seda tööle saada ilma lisakuluta (Max subscription ainult)
- Alusta sammust 1 — uuri enne kui ehitad
- Küsimuste korral: lisa küsimused siia WO-sse, Risto vaatab

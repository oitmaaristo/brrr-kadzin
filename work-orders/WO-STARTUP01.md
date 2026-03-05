# WO-STARTUP01: Startup SESSION_CONFLICT fix

**Prioriteet:** P0 | **Branch:** auto-claude/wo-startup01 | **Gatekeeper:** Risto

## PROBLEEM

Restart ajal:
1. brrr-engine.service avab WS TopStepX-ile
2. brrr-dashboard.service käivitub SAMAL AJAL
3. app.py:134 kutsub engine.start() UUESTI — teine WS ühendus
4. Broker: GatewayLogout + SESSION_CONFLICT
5. Lisaks: RECONCILE_INTERVAL pole defineeritud → crash app.py:262

## ROOT CAUSE

Dashboard --no-trading moodis aga käivitab ikkagi engine.start() (app.py:125-144).
brrr-dashboard.service ei soltu brrr-engine.service-st — paralleelne startup.

## LAHENDUS

### OSA 1: Dashboard EI kaivita engine-i ise

src/dashboard/app.py — eemalda auto-start blokk (read ~125-144):
  Eemalda: await state.engine.start()
  Dashboard loeb engine state API kaudu (/api/status juba olemas)
  Kui engine offline: naita "Engine offline", mitte crash

### OSA 2: systemd — dashboard soltub engine-st

/etc/systemd/system/brrr-dashboard.service [Unit] sektsiooni:
  After=network.target brrr-engine.service
  Wants=brrr-engine.service

### OSA 3: RECONCILE_INTERVAL

src/dashboard/app.py tippu:
  RECONCILE_INTERVAL = 300

### OSA 4: Engine restart policy

/etc/systemd/system/brrr-engine.service:
  Restart=on-failure (mitte always)

## ACCEPTANCE CRITERIA

- [ ] systemctl restart brrr-dashboard ei tekita SESSION_CONFLICT
- [ ] systemctl restart brrr-engine brrr-dashboard — dashboard ootab engine-t
- [ ] Dashboard naitab "Engine offline" kui engine pole saadaval
- [ ] RECONCILE_INTERVAL defineeritud, startup crash kaob
- [ ] Restart 3x jarjest — SESSION_CONFLICT ei teki

## EI TOHI

- Muuta engine WebSocket loogikat
- Muuta dashboard API endpointe
- Eemaldada --no-trading flag
- Mergida main ilma Risto loata

# WO-MONITOR-REDESIGN — Agent Monitor UI Redesign

**Priority:** LOW
**Assignee:** CC-Windows
**Created:** 2026-03-19
**Status:** TODO

---

## TAUST

Agent Monitor (Claude Code Agent Monitor) jookseb VPS-il port 4820.
Claudia tegi esialgse BRRR brandingu (värvid, logo, fondid) aga see vajab
korralikku redesigni läbi frontend-design skilli.

## ASUKOHT

- VPS: `/home/brrr/agent-monitor/`
- Client (React + Tailwind + Vite): `/home/brrr/agent-monitor/client/`
- Server (Node.js + Express + SQLite): `/home/brrr/agent-monitor/server/`
- URL: http://100.93.186.17:4820 (Tailscale)

## MIS ON JUBA TEHTUD

Claudia muutis:
- Tailwind config: BRRR värvid (Deep Navy #1a1a2e, Teal #00d4aa, Electric Blue #4361ee)
- Google Fonts: Outfit (display), Inter (body), JetBrains Mono (code)
- Sidebar: brrr.kadzin logo (text-2xl, Outfit 600, teal punkt)
- Footer: puhastatud (ainult Live/Disconnected staatus)
- Scrollbar ja selection värvid

## MIDA VAJA TEHA

### 1. Loe frontend-design skill
```
/mnt/skills/public/frontend-design/SKILL.md
```
See juhendab kuidas teha kvaliteetset kujundust mis ei ole "AI slop".

### 2. Loe BRRR brand guidelines
```
VPS: /home/brrr/brrr-kadzin/brand/BRAND.md
```
Või siit:

| Värv | Hex | Kasutus |
|------|-----|---------|
| Deep Navy | #1a1a2e | Taust |
| Teal | #00d4aa | Accent, punkt, success |
| Electric Blue | #4361ee | Secondary accent, lingid |
| Light Gray | #e0e0e0 | Body text |
| Pure White | #ffffff | Headers |

Fondid: Outfit 600 (headers), Inter 400 (body), JetBrains Mono (code)
Toon: Tehniline, enesekindel, otsene, natuke huumorit (BRRR!)
Ära kasuta emojisid UI-s.

### 3. Vaata üle praegune kood

```bash
ssh brrr@100.93.186.17
cd /home/brrr/agent-monitor/client
```

Põhifailid:
- `tailwind.config.js` — värvid, fondid (juba BRRR branded)
- `src/components/Sidebar.tsx` — navigatsioon (juba branded)
- `src/pages/Dashboard.tsx` — pealeht
- `src/pages/Sessions.tsx` — sessioonide vaade
- `src/pages/ActivityFeed.tsx` — aktiivsuse voog
- `src/pages/Analytics.tsx` — analüütika
- `src/pages/SessionDetail.tsx` — sessiooni detail
- `src/components/` — kõik komponendid
- `src/index.css` — globaalsed stiilid

### 4. Redesigni juhend

Kasuta frontend-design skilli lähenemist:
- **Tone:** Luxury/refined + industrial/utilitarian hübriid.
  Trading dashboard = professionaalne, mitte mänguline.
- **Diferentseerimine:** See on KAUPLEMISAGENTIDE monitor, mitte veel üks
  geneerilne admin panel. Peab tunduma nagu mission control.
- **Tüpograafia:** Outfit on juba sees, kasuta seda julgemalt.
  Numbrid monospace (JetBrains Mono). Stat kaardid prominentsemaks.
- **Värvipalett:** Teal on hero-värv. Electric Blue sekundaarne.
  Punane ainult vigade/hoiatuste jaoks. Roheline success/live.
- **Motion:** Subtle, mitte üle pingutatud. Stat numbrite count-up
  animatsioon. Sujuvad hover transitions. Activity feed uute ridade
  fade-in. MITTE bouncing/spinning/pulsing.
- **Layout:** Dashboard stat kaardid suuremaks ja selgemaks.
  Activity feed peaks olema visuaalselt domineeriv — see on
  põhiline mida kasutaja vaatab.
- **Taust:** Kasuta peent gradient'i või textuuret, mitte flat
  ühevärviline. Aga piisavalt peen et ei sega lugemist.

### 5. Konkreetsed muudatused

- [ ] Dashboard stat kaardid: suuremad numbrid, teal accent äärised
- [ ] Activity feed: parem visuaalne hierarhia, tool badge'id värviga
- [ ] Sidebar nav ikoonid: teal hover efekt
- [ ] Page headerid: Outfit font, suuremad
- [ ] Sessions tabel: parem spacing, monospace numbrid
- [ ] Üldine polish: hover states, transitions, focus rings
- [ ] Eemalda "Claude Code" viited kus võimalik (asenda "Agent")
- [ ] Favicon: tee lihtne SVG "b." teal punktiga

### 6. Build ja restart

```bash
cd /home/brrr/agent-monitor && npm run build
tmux send-keys -t agent-monitor C-c
sleep 2
tmux send-keys -t agent-monitor 'npm start' Enter
```

Kontrolli: http://100.93.186.17:4820

## REEGLID

- ÄRA muuda serverit (server/) — ainult client
- ÄRA muuda hookide integratsiooni
- ÄRA eemalda funktsionaalsust — ainult visuaal
- TESTI et build läbib enne commitimist
- Outfit font PEAB olema headers
- JetBrains Mono PEAB olema numbrites/koodis
- Teal (#00d4aa) PEAB olema primary accent


## KRIITILISED PROBLEEMID (Risto feedback)

1. **"No active agents"** — Stradivarius ja Handel jooksevad aga monitor ei näe neid.
   Tõenäoliselt hookid ei jõua headless (-p) sessioonidest monitorisse.
   Uuri: kas --dangerously-skip-permissions blokeerib hookide tulitamise?
   Kui jah — lisa monitor hookid otse agentide settings.json-idesse
   (`/home/brrr/brrr-stradivarius/.claude/settings.json` ja
   `/home/brrr/brrr-handel/.claude/settings.json`).

2. **"Total Cost $1.60K"** — mõttetu, me oleme Max plaanil.
   Eemalda cost kaart dashboardist täielikult, või asenda millegi
   kasulikuga (nt "Experiments Today" Stradivariuse jaoks).

3. **Numbrid on suvalised** — 356 sessiooni, 46.2K events jne on
   KÕIKIDE VPS-i CC sessioonide koondandmed, mitte ainult agentide oma.
   Dashboard peaks näitama AINULT Stradivariuse ja Handeli sessioone,
   või vähemalt selgelt eristama agentide sessioone ülejäänutest.

4. **Dashboardi fookus on vale** — praegu näitab geneerilisi CC statistikaid.
   Meie jaoks on olulised:
   - Kas Stradivarius jookseb? Mitu eksperimenti täna? Mitu CANDIDATE'd?
   - Kas Handel jookseb? Mitu otsust täna? Kas ta on midagi muutnud?
   - Viimased optimization_log.jsonl ja handel_audit.jsonl read
   - Agentide tmux sessioonide staatus (live/dead)

### Prioriteedid (kõrgeim esimesena)

1. **FIKSI et agendid oleks nähtavad** — see on #1 probleem
2. **Eemalda/asenda mõttetud kaardid** (cost, total sessions)
3. **Lisa agendi-spetsiifilised vaated** kus loetakse
   optimization_log.jsonl ja handel_audit.jsonl reaalajas
4. Alles SIIS visuaalne polish (frontend-design skill)

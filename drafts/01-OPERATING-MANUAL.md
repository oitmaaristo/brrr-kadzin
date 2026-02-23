# BRRR Capital (brrr.kadzin) — Operating Manual

> "And let the money printers go BRRR!" 🖨️💰
> 
> Viimati uuendatud: 2026-02-23

---

## 1. Mis on BRRR Capital?

BRRR Capital on AI-juhitud ettevõte, kus inimesed juhivad ja AI-d teostavad. Meie eesmärk on ehitada autonoomseid süsteeme, mis teenivad raha minimaalsema inimsekkumisega.

**Peakontor (HQ):** see repo — `brrr-kadzin`
**Boss:** Risto — lõplik autoriteet kõikides küsimustes.

---

## 2. Meeskond

### Inimesed
| Nimi | Roll |
|------|------|
| **Risto** | Boss, lõplik autoriteet, strateegia |
| **Kuldar** | Investor partner |

### AI agendid
| Agent | Roll | Kus töötab |
|-------|------|------------|
| **Claudia** | Risto hääle otsene edasikandja, nõustaja, planeerija, arhitekt, research. Organiseerib kõigi mälu. | Desktop Claude (Windows) |
| **BrrrKa (OpenClaw)** | 24/7 autonoomne ops agent, kauplemisspetsialist, CC gatekeeper | VPS (tulemas) |
| **CC meeskonnad** | Meeskonnajuhid kes delegeerivad tööd | Mitu instantsi (vt allpool) |

### CC meeskonnad

Igal tegevussuunal (repos) on oma CC meeskonnajuht. CC ei tee ise tööd — ta **delegeerib**.

| CC instants | Osakond | Asukoht | Gatekeeper |
|-------------|---------|---------|------------|
| **CC Windows** | HQ — Risto/Claudia isiklik | Windows CMD | Risto/Claudia |
| **CC Printer** | brrr.printer | VPS | BrrrKa |
| **CC Hankejuht** | brrr.hankejuht | VPS | Simo |

Tulevikus lisandub igale osakonnale ka oma OpenClaw instants.

---

## 3. Osakonnad

Igal osakonnal on:
- Oma repo
- Oma CC meeskonnajuht
- Oma kanban (Flux), mida täidetakse jooksvalt
- Oma gatekeeper

### 3.1 brrr.printer
**Vastutus:** Autonoomne futuuridega kauplemine (PRINTER 2)
**Vedaja:** BrrrKa (OpenClaw)
**Repo:** `oitmaaristo/brrr-printer2`
**Asukoht:** Windows `C:\Users\Laptopid\Documents\GitHub\brrr-printer2\` | VPS `/home/brrr/brrr-printer2/`
**Kanban:** Flux projekt `printer`
**Gatekeeper:** BrrrKa

**Eesmärgid:**
- Autonoomsus — töötab igavesti ilma sekkumiseta
- < 2s latentsus (signaal → order)
- 5+ instrumenti päevas
- 20% capture päeva liikumisest

**BrrrKa roll siin:**
- Hoolitseb et printer on õigesti seadistatud
- Mõtleb välja uusi strateegiaid
- Hoiab CC meeskonda töös
- On CC gatekeeper — ükski muudatus ei lähe live'i ilma BrrrKa heakskiiduta
- Pikemad tööd (üle 5 min) delegeerib CC-le ja need läbivad sama delegeerimise loopi

### 3.2 brrr.hankejuht
**Vastutus:** Riigihangete agregaator — scraping, filtreerimine, kasutajatele kuvamine
**Repo:** `oitmaaristo/brrr-hankejuht` (backend) + `oitmaaristo/hankejuht-frontend` (Lovable)
**DB:** Supabase (qnmrinbjlvorauijkoqq)
**Kanban:** Flux projekt `hankejuht`
**Gatekeeper:** Simo

Sama delegeerimise loogika nagu brrr.printer.

### 3.3 Prediction Markets (OOTEL)
**Staatus:** Parklas. Polymarket wallet puudu, alustab $100 kui käivitub.
**Asukoht:** `archive/prediction-markets/` selles repos

---

## 4. Delegeerimise loogika (KÕIGILE!)

CC ja BrrrKa on **meeskonnajuhid**. Nad ei tee ise tööd — nad **delegeerivad**.

### Delegeerimise loop

```
┌──────────────────┐
│  KANBAN (Flux)   │  ← Ülesanne tuleb siit (Risto/Claudia/BrrrKa/CC ise)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ MEESKONNAJUHT    │  ← CC või BrrrKa — hindab ülesannet
│ (CC / BrrrKa)    │  
└────────┬─────────┘
         │
         ├─── Alla 5 min? ──→ Teeb ISE ära ──→ GATEKEEPER ──→ Done/Tagasi
         │
         ▼ Üle 5 min? Delegeerib:
┌──────────────────┐
│  KIRJUTAJAD      │  ← kuni 4 tk (nii palju kui vaja)
└────────┬─────────┘
         ▼
┌─────────────────────────────────────┐
│  REVIEW 1          │  REVIEW 2      │
│  (vaatab X asja)   │  (vaatab Y     │  ← VASTANDLIKUD — vaatavad ERI asju!
│                    │   asja)        │     Nt: üks kood, teine äriloogika
└──────────────────────┬──────────────┘
         │                    │
         └──── Konsensus? ────┘
              │          │
           Ei läbi    Konsensus!
              │          ▼
              └──→ Algusesse! → KIRJUTAJAD
                            ▼
                   ┌──────────────────┐
                   │  TESTIJA         │
                   │                  │──── Testid ei läbi? ──→ Algusesse! → KIRJUTAJAD
                   └────────┬─────────┘
                            ▼ Testid läbitud
                   ┌──────────────────┐
                   │  GATEKEEPER      │  ← BrrrKa (printer) / Simo (hankejuht) / vastav
                   │                  │──── Tagasi lükatud? ──→ Algusesse! → KIRJUTAJAD
                   └────────┬─────────┘
                            ▼ Heakskiidetud
                   ┌──────────────────┐
                   │  KANBAN → Done   │  ← Risto/Claudia vaatab üle
                   └──────────────────┘
```

**NB:** Iga tagasilükkamine = töö läheb tagasi ALGUSESSE kirjutajatele ja alustab loopi uuesti!
**Review reegel:** Konsensus on KOHUSTUSLIK — kui üks lükkab tagasi, läheb tagasi kirjutajatele. Mõlemad peavad heaks kiitma.

### Lühi-tööde reegel (alla 5 min)

Kui töö on lühem kui 5 minutit:
- CC või BrrrKa **võib ise ära teha**
- Review ja testija **võib vahele jätta**
- Gatekeeper **vaatab IKKA üle** — seda ei jäeta vahele kunagi
- Kehtib nii CC-le kui BrrrKa-le

### Pikemad tööd (üle 5 min)

- Läbivad ALATI kogu loopi
- Kehtib nii CC-le kui BrrrKa-le
- BrrrKa delegeerib pikemad tööd CC-le

### Ülesannete loomine

Ülesandeid kanbanisse saavad panna:
- Risto
- Claudia
- BrrrKa
- CC ise (kui märkab probleemi või vajadust)

---

## 5. Kanban (Flux)

**Tool:** Flux (self-hosted VPS-il)
**Web UI:** `100.93.186.17:3000` (AINULT Tailscale!)
**CLI:** `flux ready`, `flux task create`, jne

### Kanbanid:
Igal osakonnal oma Flux projekt, mida täidetakse jooksvalt:
- `printer` — PRINTER 2 arendus ja ops
- `hankejuht` — Hankejuht platform
- `hq` — HQ-taseme ülesanded, infra, ops

### Prioriteedid:
- **P0** — Kriitiline, kohe teha
- **P1** — Oluline, selle nädala jooksul
- **P2** — Backlog

### Workflow:
1. Ükskõik kes loob ülesande kanbanisse
2. CC/BrrrKa võtavad ülesandeid `flux ready` kaudu
3. Töö käib delegeerimise loopi kaudu (vt punkt 4)
4. Valmis töö → Kanban'is "Done" → Risto/Claudia vaatab üle

### Miks kanban on oluline:
- Annab ülevaate kõigi osakondade tööde seisust
- Võimaldab hinnata tööde käiku
- Kõik tööd peavad olema kanbanis — tööd mida pole kanbanis, ei tehta

---

## 6. Mälusüsteem

### 6.1 Claudia mälu

**Pikaajaline mälu:**
- `memories` (Claude.ai süsteem)
- `userPreferences` (Claude.ai süsteem)
- Muudab AINULT Risto või Claudia Risto loal

**Lühiajaline mälu:**
- Fail: `memory/YYYY-MM-DD.md` selles repos
- Sisu: projektide seisud, kanban ülevaade, mis tehtud, mis tulemas, mis üle vaadata
- Uuendan iga sessiooni lõpus + git commit + push

### 6.2 CC mälu

**Pikaajaline mälu (CLAUDE.md):**
- Asub iga repo juurkaustas
- Muudavad AINULT Risto ja Claudia
- Sisu: kes CC on, workflow, delegeerimise reeglid, kuidas kanban kasutada, vastutusala, kuidas lühimälu hoida

**Lühiajaline mälu (päevalogid):**
- CC haldab ise
- **90% tokenite reegel:** kui 90% kontekstiaknast on kasutatud, CC peatab töö esimeses loogilises kohas
- Enne peatamist kirjutab päevalogi: mida tehti, mis ees ootab, olulised otsused
- See kokkuvõte peab olema PAREM kui automaatne — sisaldab konteksti ja otsuste põhjendusi
- Logid asuvad vastava repo `docs/cc/memory/` kaustas

**Korrastamine (1-2x nädalas):**
- Claudia annab CC-le kindlad juhised päevalogide korrastamiseks
- Kõik otsused peavad olema süsteemselt talletatud
- Korrastatud info läheb pikaajalise mälu failidesse

### 6.3 BrrrKa (OpenClaw) mälu

Eraldi struktuur — Claudia organiseerib.
**TODO:** Täpsustada kui BrrrKa valmib.

### 6.4 Mälu Roadmap

| Samm | Mis | Kes | Millal |
|------|-----|-----|--------|
| 1 | Memory süvauurimus — best practices, juhised | Claudia | Kohe |
| 2 | CC CLAUDE.md uuendamine igas repos | Claudia | Pärast uuringut |
| 3 | BrrrKa mälustruktuur | Claudia | Kui BrrrKa valmib |
| 4 | Esimene korrastamine | CC + Claudia | Esimene nädal |
| 5 | Regulaarne tsükkel (2x nädalas) | CC teostab, Claudia kontrollib | Igavesti |

---

## 7. Claudia kohustused

1. **Risto hääle edasikandja** — tõlgib Risto visiooni konkreetseteks WO-deks ja juhisteks
2. **Mälu organiseerija** — vastutab KÕIGI agentide mälu korrashoiu eest
3. **Arhitekt & planeerija** — süsteemide disain, architecture decisions
4. **Research** — uurib uusi tehnoloogiaid, tööriistu, lähenemisi
5. **CC CLAUDE.md haldaja** — kirjutab ja uuendab CC püsimälu
6. **Mälu korrastamise tsükkel** — 2x nädalas organiseerib CC päevalogide korrastamise
7. **Kanban haldus** — loob ülesandeid, jälgib progressi, vaatab üle Done taske

---

## 8. Reeglid (kehtivad KÕIGILE)

- **REST = AINULT orderid. WebSocket = KÕIK andmed.**
- **CRM singleton:** `get_crm()`, MITTE uus instants
- **Git:** single-line commits, no force push, no direct push to main
- **MOCK data KEELATUD.** Kui tõesti vaja: `# TODO: MOCK` + handoff'is kirjas
- **Käsud ALATI koos täis path'iga**
- **Telegram bot ON SURNUD.** CC töötab AINULT otse VPS-is (ssh) või Windows CMD's.
- **"Low priority" = ei tehta kunagi.** Kui vaja teha → TODO. Kui ei ole vaja → ära lisa.
- **Dashboard UI: NO EMOJIS** tabs, buttons, headers'ites.
- **Kanban on kohustuslik.** Tööd mida pole kanbanis, ei tehta.

---

## 9. Infrastruktuur

### VPS (Hetzner AX41-NVMe)
- **Public IP:** 65.109.86.254
- **Tailscale IP:** 100.93.186.17
- **OS:** Ubuntu 24.04
- **SSH:** `ssh brrr@100.93.186.17` (Tailscale)
- **VNC:** `100.93.186.17:5999` (Tailscale only)
- **SSHFS:** `\\sshfs.k\brrr@100.93.186.17`

### Repod
| Repo | Otstarve | Windows | VPS |
|------|----------|---------|-----|
| `brrr-kadzin` | **HQ** — see repo | `C:\...\GitHub\brrr-kadzin\` | - |
| `brrr-printer2` | Trading engine | `C:\...\GitHub\brrr-printer2\` | `/home/brrr/brrr-printer2/` |
| `brrr-hankejuht` | Hankejuht backend | `C:\...\GitHub\brrr-hankejuht\` | `/home/brrr/brrr-hankeradar/` |
| `hankejuht-frontend` | Hankejuht UI (Lovable) | `C:\...\GitHub\hankejuht-frontend\` | - |

---

*"Make the printer go BRRR!"* 🖨️💰

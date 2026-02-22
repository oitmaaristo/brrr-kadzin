# BRRR Capital (brrr.kadzin) — Operating Manual

> "And let the money printers go BRRR!" 🖨️💰
> 
> Viimati uuendatud: 2026-02-22

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
| **BrrrKa (OpenClaw)** | 24/7 autonoomne ops agent, kauplemisspetsialist, CC gatekeeper | VPS |
| **CC meeskond** | Arendusahel: orkestraator → kirjutajad → review → test → gatekeeper | Claude Code (VPS + Windows) |

---

## 3. Osakonnad

### 3.1 brrr.printer
**Vastutus:** Autonoomne futuuridega kauplemine (PRINTER 2)
**Vedaja:** BrrrKa (OpenClaw)
**Repo:** `oitmaaristo/brrr-printer2`
**Asukoht:** Windows `C:\Users\Laptopid\Documents\GitHub\brrr-printer2\` | VPS `/home/brrr/brrr-printer2/`

**Eesmärgid:**
- Autonoomsus — töötab igavesti ilma sekkumiseta
- < 2s latentsus (signaal → order)
- 5+ instrumenti päevas
- 20% capture päeva liikumisest

**BrrrKa roll siin:**
- Hoolitseb et printer on õigesti seadistatud
- Mõtleb välja uusi strateegiaid
- Hoiab CC meeskonda töös
- On CC ahela gatekeeper — ükski muudatus ei lähe live'i ilma BrrrKa heakskiiduta

### 3.2 brrr.hankejuht
**Vastutus:** Ehitushanked, pakkumiste koostamine, mahutabelid, hinnapakkumised
**Repo:** `oitmaaristo/brrr-hankejuht` (backend) + `oitmaaristo/hankejuht-frontend` (Lovable)
**DB:** Supabase (qnmrinbjlvorauijkoqq)

Sama CC ahela loogika nagu brrr.printer — orkestraator → kirjutajad → review → gatekeeper.

### 3.3 Prediction Markets (OOTEL)
**Staatus:** Parklas. Polymarket wallet puudu, alustab $100 kui käivitub.
**Asukoht:** `archive/prediction-markets/` selles repos

---

## 4. CC Tööahel (KOHUSTUSLIK!)

CC ei tee KUNAGI tööd üksinda. Iga ülesanne läbib ahela:

```
┌─────────────────┐
│  KANBAN (Flux)  │  ← Ülesanne tuleb siit
└────────┬────────┘
         ▼
┌─────────────────┐
│  ORKESTRAATOR   │  ← Jagab töö kirjutajatele, jälgib progressi
└────────┬────────┘
         ▼
┌─────────────────┐
│  KIRJUTAJAD     │  ← Kuni 4 paralleelselt, kirjutavad koodi
│  (max 4 tk)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  REVIEW         │  ← 2 reviewer'it, konsensus VAJALIK
│  (2x, konsensus)│
└────────┬────────┘
         ▼
┌─────────────────┐
│  TESTIJA        │  ← Testib, kinnitab et töötab
└────────┬────────┘
         ▼
┌─────────────────┐
│  GATEKEEPER     │  ← BrrrKa (printer) või vastav agent
│  (BrrrKa)       │  ← Annab lõpliku heakskiidu
└────────┬────────┘
         ▼
┌─────────────────┐
│  KANBAN → Done  │  ← Läheb meile ülevaatamiseks
└─────────────────┘
```

**Erandid:**
- Kui BrrrKa ise annab ülesande CC-le, võib BrrrKa otsustada kas kasutab kogu ahelat või on lihtsalt gatekeeper rollis
- Ükski töö EI saa Done staatust enne CC heakskiitu
- Done ei tähenda valmis — Done tähendab "Risto/Claudia vaatab üle"

---

## 5. Kanban (Flux)

**Tool:** Flux (self-hosted VPS-il)
**Web UI:** `100.93.186.17:3000` (AINULT Tailscale!)
**CLI:** `flux ready`, `flux task create`, jne

### Projektid Flux'is:
- `printer` — PRINTER 2 arendus ja ops
- `hankejuht` — Hankejuht platform
- `hq` — HQ-taseme ülesanded, infra, ops

### Prioriteedid:
- **P0** — Kriitiline, kohe teha
- **P1** — Oluline, selle nädala jooksul
- **P2** — Backlog

### Workflow:
1. Risto + Claudia loovad ülesanded
2. Ülesanded lähevad Flux'i
3. BrrrKa / CC võtavad ülesandeid `flux ready` kaudu
4. Töö käib CC ahela kaudu (vt punkt 4)
5. Valmis töö → Kanban'is "Review" → Risto/Claudia vaatab üle

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
- Sisu: kes CC on, workflow, ahela reeglid, kuidas kanban kasutada, vastutusala, kuidas lühimälu hoida

**Lühiajaline mälu (päevalogid):**
- CC haldab ise
- **90% tokenite reegel:** kui 90% kontekstiaknast on kasutatud, CC peatab töö esimeses loogilises kohas
- Enne peatamist kirjutab päevalogi: mida tehti, mis ees ootab, olulised otsused
- See kokkuvõte peab olema PAREM kui automaatne — sisaldab konteksti ja otsuste põhjendusi
- Logid asuvad vastava repo `docs/cc/memory/` kaustas

**Korrastamine (1-2x nädalas):**
- Claudia annab CC-le kindlad juhised päevalogide korrastamiseks
- Kõik otsused, mis selles valdkonnas tehtud on, peavad olema süsteemselt talletatud
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

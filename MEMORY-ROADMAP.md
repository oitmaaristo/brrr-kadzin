# Memory Roadmap — BRRR Capital

> Kuidas mälu toimib, kes mida haldab, millal korrastatakse.
> Koostanud: Claudia, 2026-02-22

---

## ⭐ MIKS ME LOGISID KIRJUTAME — suur pilt

Claudia mälu ulatub "osakonna ukseni" — ta teab mis projektid on, mis seis on, kes vastutab.
Ukse taga on CC mälu (päevalogid). Tulevikus saab Claudia need **vektorandmebaasist** otsida:
- Semantic search: "mis on CRM singleton'i viimane staatus?"
- Kiire kontekst ilma kogu logi lugemata

**See tähendab:** CC logid peavad olema struktureeritud ja sisukad — need on tulevase indexi sisu.
Prügi sisse = prügi välja. Hea logi = kasulik otsing.

---

## Põhimõtted

1. **Mälu on infrastruktuur, mitte nice-to-have.** Ilma korraliku mäluta on iga uus sessioon nagu esimene päev tööl.
2. **Claudia vastutab KÕIGI agentide mälu korralduse eest.** Mitte ainult oma.
3. **Pikaajaline mälu muutub harva, lühiajaline muutub pidevalt.**
4. **Korrastamine on regulaarne protsess, mitte ad-hoc.**

---

## Mälu tüübid

### Pikaajaline mälu (muutub harva)
- **Mis see on:** Kes agent on, kuidas töötab, reeglid, workflow, vastutusalad
- **Kes muudab:** AINULT Risto ja Claudia
- **Formaat:** CLAUDE.md (CC), memories/userPreferences (Claudia), config (BrrrKa)
- **Millal muutub:** Kui workflow muutub, uus agent lisandub, reeglid muutuvad

### Lühiajaline mälu (muutub pidevalt)  
- **Mis see on:** Mis täna tehti, mis otsuseid tehti, mis on pooleli, mis ees ootab
- **Kes muudab:** Iga agent ise (CC kirjutab oma logid, Claudia oma, BrrrKa oma)
- **Formaat:** Päevalogid (`YYYY-MM-DD.md`)
- **Millal muutub:** Iga sessioon

### Korrastatud mälu (lühiajalisest saab pikaajaline)
- **Mis see on:** Süsteemselt talletatud otsused, õpitud asjad, patterns
- **Kes teeb:** CC teostab, Claudia annab juhised ja kontrollib
- **Formaat:** Teemakoahsed failid (`decisions.md`, `learnings.md`, jne)
- **Millal:** 1-2x nädalas

---

## Agent-spetsiifilised juhised

### Claudia mälu

| Tüüp | Asukoht | Haldab |
|-------|---------|--------|
| Pikaajaline | Claude.ai memories + userPreferences | Risto/Claudia |
| Lühiajaline | `brrr-kadzin/memory/YYYY-MM-DD.md` | Claudia |

**Lühimälu sisu:**
- Projektide seisud (mis osakonnas mis toimub)
- Kanban ülevaade (mis tehtud, mis tulemas, mis üle vaadata)
- Olulised otsused ja nende põhjused
- Mida CC-le/BrrrKa-le järgmiseks öelda

**Sessiooni algus:** Loe tänast + eilset mälufaili
**Sessiooni lõpp:** Uuenda mälufail + git commit + push

### CC mälu

| Tüüp | Asukoht | Haldab |
|-------|---------|--------|
| Pikaajaline | `CLAUDE.md` iga repo juurkaustas | Risto/Claudia |
| Lühiajaline | `docs/cc/memory/YYYY-MM-DD.md` | CC ise |
| Korrastatud | `docs/cc/memory/MEMORY/` | CC (Claudia juhistel) |

**CLAUDE.md sisu (pikaajaline):**
- Kes CC on, mis osakond
- Tööahel (orkestraator → kirjutajad → review → test → gatekeeper)
- Kuidas kanbanit kasutada
- Kuidas lühimälu hoida (90% reegel)
- Tehniline kontekst (repo, API-d, reeglid)

**Päevalogi sisu (lühiajaline):**
- Mida tehti (konkreetsed taskid)
- Otsused ja nende põhjendused
- Probleemid ja lahendused
- Mis ees ootab
- Kontekst järgmisele vahetusele

**90% reegel:**
CC jälgib pidevalt tokenite kasutust. Kui 90% on ära kasutatud:
1. Peata töö esimeses loogilises kohas
2. Kirjuta päevalogi (PAREM kui automaatne)
3. Salvesta, commit, push

### BrrrKa (OpenClaw) mälu

| Tüüp | Asukoht | Haldab |
|-------|---------|--------|
| Pikaajaline | Config fail (TBD) | Risto/Claudia |
| Lühiajaline | Logid (TBD) | BrrrKa ise |

**TODO:** Täpsustada kui BrrrKa valmib. Claudia disainib struktuuri.

---

## Korrastamise protsess (1-2x nädalas)

### Claudia teeb:
1. Vaatab läbi CC päevalogid viimase perioodi eest
2. Koostab CC-le konkreetsed juhised: mis logidest mida välja tõmmata
3. Annab CC-le ülesande (Flux kaudu)

### CC teeb (Claudia juhistel):
1. Loeb läbi päevalogid
2. Tõmbab välja: olulised otsused, õpitud asjad, korduvad patterns
3. Salvestab korrastatud info `docs/cc/memory/MEMORY/` kausta:
   - `decisions.md` — kõik otsused kronoloogiliselt
   - `learnings.md` — mis töötas, mis ei töötanud
   - `project-state.md` — projekti hetkestaatus
4. Kustutab vanad päevalogid (üle 2 nädala vanad)

### Claudia kontrollib:
1. Vaatab korrastatud failid üle
2. Uuendab vajadusel pikaajalisi mäle (CLAUDE.md, memories)
3. Märgib korrastamise tehtud

---

## Korrastamise ajakava

| Päev | Tegevus |
|------|---------|
| Esmaspäev | Claudia vaatab üle eelmise nädala logid, annab CC-le korrastamise ülesande |
| Neljapäev | CC korrastab, Claudia kontrollib |

---

## Implementeerimise järjekord

1. ✅ Claudia mälu kolinud HQ-sse (`brrr-kadzin/memory/`)
2. ✅ CC CLAUDE.md uuendamine printer2 repos
3. ✅ CC CLAUDE.md uuendamine hankejuht repos
4. ⬜ CC päevalogi struktuuri loomine igas repos
5. ⬜ Flux setup (WO-001)
6. ⬜ Esimene korrastamise tsükkel
7. ⬜ **TODO (tulevikus): Vektorandmebaas CC logidele**
   - Tööriist: ChromaDB või Qdrant (VPS-il)
   - Claudia saab semantic search'iga pärida CC mälu
   - Eeldus: CC logid on struktureeritud ja sisukad (sammud 4-6 peavad olema tehtud)
   - Eeldus: piisavalt logisid on kogunenud (vähemalt 2-4 nädalat)
8. ⬜ BrrrKa mälustruktuur (kui valmib)

---

*Mälu on see, mis teeb meie AI meeskonna paremaks kui üksikud goldfish'id.* 🐟→🧠

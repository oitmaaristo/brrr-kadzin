# Mälu Korrastamise Juhis CC-le

> Selle ülesande annab Claudia CC-le 1-2x nädalas Flux kaudu.

---

## Ülesanne

Korasta viimase [X päeva] päevalogid ja uuenda pikaajalisi mälufaile.

## Sammud

### 1. Loe päevalogid läbi
```bash
ls docs/cc/memory/
# Loe kõik logid alates [kuupäev]
```

### 2. Tõmba välja olulised otsused
Lisa `docs/cc/memory/MEMORY/decisions.md` faili:
- Kuupäev, otsus, põhjus, kontekst
- Kronoloogiline järjekord
- Ära kustuta vanu kirjeid!

### 3. Tõmba välja õpitud asjad
Lisa `docs/cc/memory/MEMORY/learnings.md` faili:
- Mis töötas, mis ei töötanud
- Patterns mis korduvad
- Workaround'id ja nipid

### 4. Uuenda projekti staatust
Uuenda `docs/cc/memory/MEMORY/project-state.md`:
- Hetke staatus
- Viimased muudatused
- Mis on pooleli
- Mis blokeerib

### 5. Puhasta vanad logid
Kustuta päevalogid mis on vanemad kui 14 päeva.
(Oluline info on nüüd MEMORY/ failides.)

### 6. Commit
```bash
git add docs/cc/memory/
git commit -m "Memory: weekly cleanup YYYY-MM-DD"
git push
```

## Acceptance Criteria
- [ ] decisions.md uuendatud
- [ ] learnings.md uuendatud
- [ ] project-state.md uuendatud
- [ ] Vanad logid kustutatud
- [ ] Committitud ja pushitud

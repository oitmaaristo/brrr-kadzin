# WO-001: Flux Kanban Board Setup
**Created:** 2026-02-22
**Author:** Claudia (Desktop Claude)
**Assignee:** CC (VPS)
**Priority:** P1
**Status:** TODO

---

## Eesmärk
Paigaldada Flux kanban board VPS-ile, et Claudia, CC ja OpenClaw saaksid jagatud task management süsteemi kasutada. Flux on git-native, CLI-first kanban board mis on loodud AI agentide jaoks.

## Miks Flux?
- CLI-first: agendid kasutavad `flux ready`, `flux task create` jne
- Git-native sync: taskid elavad repo's, ei sõltu pilveserveritest
- Web UI: Risto näeb board'i browser'ist
- MCP integratsioon: CC saab MCP kaudu otse taske hallata
- Self-hosted: kõik jääb meie VPS-ile, ei mingit kolmandat osapoolt
- Repo: https://github.com/sirsjg/flux

## Turvanõuded
- [ ] Web UI AINULT Tailscale kaudu (100.93.186.17:3000), MITTE public IP
- [ ] Firewall: port 3000 blokeeritud public interface'il
- [ ] Kõik Flux andmed `/home/brrr/` all, MITTE root'i all

---

## Sammud

### 1. Flux CLI paigaldamine
```bash
# brrr kasutajana!
ssh brrr@100.93.186.17

# Kontrolli node/npm versioon
node --version
npm --version

# Installi Flux CLI globaalselt
npm install -g flux-tasks
```

### 2. Flux init brrr-printer2 repos
```bash
cd /home/brrr/brrr-printer2
flux init
```
**NB:** Vali JSON storage (mitte SQLite) — lihtsam git sync jaoks.

### 3. Testi CLI toimivust
```bash
flux task create "WO-001 test task - kustuta pärast" -P 2
flux ready
flux task list
```

### 4. Web UI + MCP server (Docker)
```bash
cd /home/brrr
curl -fsSL https://raw.githubusercontent.com/sirsjg/flux/main/scripts/quickstart.sh | bash
```
**VÕI** kui quickstart ei tööta:
```bash
git clone https://github.com/sirsjg/flux.git /home/brrr/flux
cd /home/brrr/flux
# Järgi README install juhiseid
```

### 5. Firewall — Tailscale-only
```bash
# Kontrolli et port 3000 EI OLE avatud public IP-l
# Kui ufw on aktiivne:
sudo ufw deny from any to any port 3000
sudo ufw allow from 100.64.0.0/10 to any port 3000  # Tailscale subnet
```
**KRIITILINE:** Testi et `65.109.86.254:3000` EI vasta, aga `100.93.186.17:3000` töötab!

### 6. CC MCP integratsioon
```bash
# CC VPS-is:
claude mcp add flux -- docker exec -i flux-web bun packages/mcp/dist/index.js

# VÕI kui CLI mode:
claude mcp add flux -- flux mcp
```

### 7. Esimesed projektid Flux'is
Kui kõik töötab, loo järgmised projektid:
- `printer2` — PRINTER 2 arendus
- `hankejuht` — Hankejuht platform
- `kadzin` — Brrr Kadzin prediction markets
- `infra` — VPS, turvalisus, ops

---

## Acceptance Criteria
- [ ] `flux ready` töötab VPS-is brrr kasutajana
- [ ] Web UI nähtav `100.93.186.17:3000` (Tailscale)
- [ ] Web UI EI OLE nähtav `65.109.86.254:3000` (public)
- [ ] CC saab MCP kaudu taske lugeda ja luua
- [ ] Test task loodud ja kustutatud edukalt
- [ ] Flux data elab `/home/brrr/` all

## Handoff märkmed
- Pärast setupi: uuenda `docs/handoffs/cc-handoff.json` Flux infoga
- Lisa `.gitignore` vajalikud Flux failid kui vaja
- Raporteeri Ristole kui valmis

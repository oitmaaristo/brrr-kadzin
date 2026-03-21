# WO-AGENTS-INFRA — Autonomous Agent Infrastructure Setup

**Priority:** CRITICAL
**Assignee:** CC-Windows
**Reviewer:** Claudia (Desktop Claude)
**Final Approval:** Risto
**Created:** 2026-03-19
**Status:** DONE (dry runs passed, awaiting production launch approval)

---

## TL;DR

Set up two autonomous Claude Code agents on VPS for brrr-printer2:
- **Stradivarius** — Strategy R&D loop (backtesting + new strategy creation)
- **Handel** — Live filter/SL/TP tuning + monitoring

Both follow Karpathy's autoresearch pattern: infinite loop, git as state machine, filesystem as memory, output to files, NEVER STOP.

---

## PREREQUISITE CHECKLIST

Before ANY agent work, verify these exist and work:

```bash
# 1. Claude Code is installed on VPS
claude --version

# 2. API key is configured
echo $ANTHROPIC_API_KEY | head -c 10

# 3. Metaformer can run (basic import test)
cd /home/brrr/brrr-printer2
python3 -c "from src.metaformer.pipeline import *; print('OK')"

# 4. filter_config.json is readable/writable
cat data/filter_config.json | python3 -m json.tool > /dev/null && echo "OK"

# 5. Git is clean
git status

# 6. Slack webhook works (if configured)
cat /home/brrr/.slack_tokens
```

If any of these fail — STOP and escalate to Risto.

---

## PHASE 1: Directory Structure Setup

### 1.1 Create agent worktrees

```bash
cd /home/brrr/brrr-printer2
git worktree add /home/brrr/brrr-stradivarius -b agent/stradivarius/active
git worktree add /home/brrr/brrr-handel -b agent/handel/active
```

### 1.2 Create support directories

```bash
mkdir -p /home/brrr/agent-logs
mkdir -p /home/brrr/agent-scripts
mkdir -p /var/log/claude-agents
```

### 1.3 Create shared state files

```bash
touch /home/brrr/brrr-printer2/data/optimization_log.jsonl
touch /home/brrr/brrr-printer2/data/handel_audit.jsonl
```

---

## PHASE 2: Settings.json for Each Agent

### 2.1 Stradivarius settings

Path: `/home/brrr/brrr-stradivarius/.claude/settings.json`

- Allowed: python3, git (add/commit/reset/log/diff/status/checkout), file ops, flock, Read/Write/Edit/Glob/Grep
- Denied: rm -rf, sudo, curl, wget, ssh, git push, systemctl, pkill, kill
- Denied paths: .env, brrr-handel/*, engine/*, crm/*, api/*, data_hub/*, accounts.json
- Stop hook: blocks exit, tells agent to continue loop
- PostToolUse hook: logs all Bash commands to /var/log/claude-agents/stradivarius.log

### 2.2 Handel settings

Path: `/home/brrr/brrr-handel/.claude/settings.json`

- Allowed: python3, git (add/commit/log/diff/status), file ops, flock, sqlite3, Read/Write/Edit/Glob/Grep
- Denied: rm -rf, sudo, curl, wget, ssh, git push, git reset --hard, systemctl, pkill, kill
- Denied paths: .env, brrr-stradivarius/*, core engine files, crm/*, api/*, metaformer/*, accounts.json
- Stop hook: blocks exit, tells agent to observe and wait
- PreToolUse hook: blocks Edit on core engine files
- PostToolUse hook: logs all Bash commands to /var/log/claude-agents/handel.log

---

## PHASE 3: Agent CLAUDE.md Files

### 3.1 Stradivarius CLAUDE.md

Path: `/home/brrr/brrr-stradivarius/CLAUDE.md`

Loop: ASSESS -> DECIDE -> EXECUTE -> EVALUATE -> RECORD -> CONTINUE (never stop)
- ASSESS: read optimization_log.jsonl, library.py, filter_stats.json
- DECIDE: EXPLOIT (80%) or EXPLORE (20%)
- EXECUTE: run metaformer optimization, redirect output to file
- EVALUATE: quality gates (OOS/IS > 0.6, min 200 trades, Sharpe < 3.0, etc.)
- RECORD: git commit, append to optimization_log.jsonl with flock

### 3.2 Handel CLAUDE.md

Path: `/home/brrr/brrr-handel/CLAUDE.md`

Loop: OBSERVE -> ASSESS -> ACT -> EVALUATE -> LOG -> CONTINUE (never stop)
- OBSERVE: read filter_stats, filter_config, audit log, engine log, trading.db
- ASSESS: check triggers (block rate, win rate, consecutive losses, SL/TP hit rates)
- ACT: if trigger fires, adjust ONE parameter within hard limits
- EVALUATE: compare pre/post metrics after ~20 trades
- LOG: always log to handel_audit.jsonl, even if no action taken

---

## PHASE 4: Launch Scripts

All in `/home/brrr/agent-scripts/`:

| Script | Purpose |
|--------|---------|
| `launch-stradivarius.sh` | Start Stradivarius in tmux (default 200 turns) |
| `launch-handel.sh` | Start Handel in tmux (default 150 turns) |
| `stradivarius-loop.sh` | Continuous restart wrapper for Stradivarius |
| `handel-loop.sh` | Continuous restart wrapper for Handel |
| `agent-health.sh` | Health check (cron every 5 min, Slack alerts) |

---

## PHASE 5: Implementation Steps

1. Create directory structure
2. Create settings.json files
3. Write CLAUDE.md files
4. Create launch scripts
5. Create shared state files
6. Dry run Stradivarius (10 turns)
7. Dry run Handel (10 turns)
8. Write report

---

## PHASE 6: Production Launch (Risto approval required)

DO NOT execute without Risto's explicit "go".

```bash
nohup /home/brrr/agent-scripts/stradivarius-loop.sh > /home/brrr/agent-logs/strad-loop.log 2>&1 &
nohup /home/brrr/agent-scripts/handel-loop.sh > /home/brrr/agent-logs/handel-loop.log 2>&1 &
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/brrr/agent-scripts/agent-health.sh >> /var/log/claude-agents/health.log 2>&1") | crontab -
```

---

## COST & RATE LIMITS

Max plan — CC usage is included in subscription, no per-token API costs.
`--max-turns` is used for periodic restart with fresh context (prevents instruction degradation).

---

## ROLLBACK PLAN

```bash
tmux kill-session -t stradivarius 2>/dev/null
tmux kill-session -t handel 2>/dev/null
pkill -f stradivarius-loop
pkill -f handel-loop
cd /home/brrr/brrr-printer2
git worktree remove /home/brrr/brrr-stradivarius --force
git worktree remove /home/brrr/brrr-handel --force
git branch -D agent/stradivarius/active
git branch -D agent/handel/active
```

Main repo is UNTOUCHED through all of this. Zero risk to production.

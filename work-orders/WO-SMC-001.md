# WO-SMC-001: Smart Money Concepts AI - MVP

**Status:** PLANNING  
**Priority:** HIGH  
**Owner:** CC  
**Created:** 2026-02-13  
**Target:** Q1 2026  

---

## 🎯 Vision

Build the first AI-powered Smart Money Concepts analysis tool that combines:
1. **ICT-style chart analysis** - Order Blocks, FVG, BOS/CHoCH, Kill Zones
2. **Prop Firm Risk Manager** - Real-time drawdown tracking, position sizing, rule enforcement
3. **MCP Integration** - Works with Claude, ChatGPT, and any MCP-compatible AI

**Target User:** Retail traders taking prop firm challenges (FTMO, Topstep, Apex, etc.)

**Unique Value:** 
> "Pass your prop firm challenge on the FIRST try."

No one else combines SMC + AI + Prop Firm Rules in one tool.

---

## 💰 Revenue Model

| Tier | Price | Features |
|------|-------|----------|
| **Free** | €0 | Basic SMC analysis, 5 queries/day |
| **Trader** | €29/mo | Unlimited analysis, 1 prop firm, alerts |
| **Pro** | €79/mo | All prop firms, position sizer, kill switch, priority |
| **Lifetime** | €499 | Pro forever |

**Target:** 1,000 Pro users = €79,000/month

---

## 🧠 Core Features (MVP)

### 1. SMC AI Analyst

**Input:** Chart image OR symbol + timeframe  
**Output:** Structured analysis

```json
{
  "bias": "bullish",
  "confidence": 0.78,
  "market_structure": {
    "trend": "uptrend",
    "last_bos": "1.0892",
    "last_choch": null
  },
  "order_blocks": [
    {"type": "bullish", "zone": [1.0845, 1.0860], "strength": "strong"}
  ],
  "fvg": [
    {"type": "bullish", "zone": [1.0870, 1.0878], "filled": false}
  ],
  "liquidity": {
    "buy_side": [1.0920, 1.0945],
    "sell_side": [1.0810, 1.0795]
  },
  "kill_zone": {
    "active": true,
    "session": "new_york",
    "time_remaining": "2h 15m"
  },
  "trade_idea": {
    "direction": "long",
    "entry_zone": [1.0850, 1.0860],
    "sl": 1.0830,
    "tp1": 1.0920,
    "tp2": 1.0945,
    "rr": "3.2:1"
  }
}
```

### 2. Prop Firm Risk Manager

**Real-time tracking:**
- Daily loss % (current vs limit)
- Max drawdown % (current vs limit)
- Open position risk
- Trades today vs max allowed
- News events (next 4 hours)

**Position Sizer:**
```
Input: Account $50,000, Risk 1%, SL 25 pips
Output: Position size = 2.0 lots
```

**Alerts:**
- ⚠️ "Daily loss at 3.8% - limit is 5%"
- ⚠️ "FOMC in 45 minutes - close positions"
- 🛑 "Max drawdown reached - STOP TRADING"

**Kill Switch:**
- Auto-flatten if daily loss > threshold
- User-configurable trigger

### 3. Prop Firm Rules Engine

| Firm | Daily Loss | Max DD | Min Days | News | Scaling |
|------|------------|--------|----------|------|---------|
| FTMO | 5% | 10% | 4 | ❌ 2min | Yes |
| Topstep 50K | $1,000 | $2,000 | 0 | ✅ | Yes |
| Topstep 150K | $3,000 | $4,500 | 0 | ✅ | Yes |
| Apex | Trailing | Trailing | 7 | ✅ | Yes |
| The5ers | 3% | 6% | 3 | ❌ | Yes |
| FundedNext | 5% | 10% | 5 | ❌ | Yes |

---

## 🔧 Tech Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MCP SERVER                         │
│            (Claude/ChatGPT/etc)                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              SMC AI ENGINE                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐        │
│  │ Chart    │ │ Market   │ │ Trade Idea   │        │
│  │ Analysis │ │ Structure│ │ Generator    │        │
│  └──────────┘ └──────────┘ └──────────────┘        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│            RISK MANAGER                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐        │
│  │ Position │ │ Drawdown │ │ Prop Firm    │        │
│  │ Sizer    │ │ Tracker  │ │ Rules        │        │
│  └──────────┘ └──────────┘ └──────────────┘        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│          PLATFORM INTEGRATIONS                      │
│  ┌──────┐ ┌──────────┐ ┌────────┐ ┌─────────┐      │
│  │ MT5  │ │ Tradovate│ │cTrader │ │TradingV │      │
│  └──────┘ └──────────┘ └────────┘ └─────────┘      │
└─────────────────────────────────────────────────────┘
```

### Tech Stack

- **MCP Server:** TypeScript, @modelcontextprotocol/sdk
- **AI Engine:** Claude API (vision for charts)
- **Risk Manager:** Python (real-time calculations)
- **Data:** WebSocket feeds (broker APIs)
- **Platform:** Apify (hosting & monetization)

---

## 📋 MVP Scope (Phase 1)

### Must Have
- [ ] MCP server structure
- [ ] SMC analysis from chart image (Claude Vision)
- [ ] Basic market structure detection (BOS/CHoCH)
- [ ] Order Block identification
- [ ] FVG detection
- [ ] Kill Zone awareness
- [ ] Position size calculator
- [ ] FTMO rules (first prop firm)
- [ ] Daily loss tracker

### Nice to Have (Phase 2)
- [ ] Real-time broker integration (MT5)
- [ ] All major prop firms
- [ ] Telegram alerts
- [ ] Auto kill switch
- [ ] Historical analysis
- [ ] Backtesting

### Future (Phase 3)
- [ ] Multi-platform (Tradovate, cTrader)
- [ ] AI trade journal
- [ ] Strategy optimization
- [ ] Copy trading signals

---

## 📊 Success Metrics

| Metric | Target (3 months) |
|--------|-------------------|
| MCP installs | 500 |
| Free users | 1,000 |
| Paid users | 100 |
| MRR | €5,000 |
| Prop firm pass rate increase | +20% |

---

## 🚀 Timeline

| Week | Milestone |
|------|----------|
| 1-2 | MCP server skeleton, Claude Vision integration |
| 3-4 | SMC analysis (OB, FVG, structure) |
| 5-6 | Risk manager, position sizer |
| 7-8 | FTMO rules, daily loss tracking |
| 9-10 | Testing, polish, Apify deploy |
| 11-12 | Launch, marketing, iterate |

---

## 🔗 Dependencies

- Claude API access (vision)
- Apify account (Vooluahel OÜ)
- Prop firm rule documentation
- Beta testers (prop firm traders)

---

## Notes

- LuxAlgo proves ICT/SMC terminology is safe to use
- Prop firms ALLOW analysis tools (not bots)
- Focus on "AI suggests, trader decides" positioning
- Educational tool, not financial advice

---

**BRRR!** 🖨️💰

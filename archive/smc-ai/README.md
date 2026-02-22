# Smart Money Concepts AI

> AI-powered SMC analysis for prop firm traders

## Status: In Development 🚧

See [WO-SMC-001](../work-orders/WO-SMC-001.md) for full specification.

## Quick Start

```bash
# Coming soon
npm install @brrr-kadzin/smc-ai
```

## Features

- 🧠 ICT-style chart analysis
- 📊 Order Blocks, FVG, BOS/CHoCH detection
- ⏰ Kill Zone timing
- 💧 Liquidity sweep identification
- 🛡️ Prop firm risk manager
- 📐 Position size calculator

## MCP Tools

```typescript
// Analyze chart
smc_analyze({ image: "base64..." })
smc_analyze({ symbol: "EURUSD", timeframe: "1H" })

// Risk management
risk_calculate_position({ account: 50000, risk_percent: 1, sl_pips: 25 })
risk_check_daily_loss({ prop_firm: "ftmo", current_equity: 48500 })

// Prop firm rules
prop_firm_rules({ firm: "ftmo" })
prop_firm_can_trade({ firm: "ftmo", daily_loss: 3.5 })
```

## License

MIT

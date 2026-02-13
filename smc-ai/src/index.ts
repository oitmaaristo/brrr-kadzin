#!/usr/bin/env node
/**
 * SMC AI — MCP Server
 *
 * Smart Money Concepts analysis + Prop Firm risk management.
 * Runs over stdio transport for Claude Desktop / MCP clients.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { analyzeSchema, handleAnalyze } from "./tools/analyze.js";
import {
  positionSizeSchema,
  handlePositionSize,
  dailyLossSchema,
  handleDailyLoss,
} from "./tools/risk.js";
import {
  propFirmRulesSchema,
  handlePropFirmRules,
  propFirmCanTradeSchema,
  handleCanTrade,
} from "./tools/propfirm.js";

// ---------- Server ----------

const server = new McpServer({
  name: "smc-ai",
  version: "0.1.0",
});

// ---------- Tools ----------

// 1. SMC Chart Analysis
server.registerTool(
  "smc_analyze",
  {
    title: "SMC Chart Analysis",
    description:
      "Analyze a trading chart using Smart Money Concepts (ICT-style). " +
      "Provide a base64-encoded chart image for vision analysis, or a symbol+timeframe for a quick overview. " +
      "Returns order blocks, FVG, BOS/CHoCH, liquidity levels, kill zones, and trade ideas.",
    inputSchema: analyzeSchema,
  },
  handleAnalyze
);

// 2. Position Size Calculator
server.registerTool(
  "risk_position_size",
  {
    title: "Position Size Calculator",
    description:
      "Calculate the correct position size (lots) based on account size, risk percentage, and stop-loss distance. " +
      "Essential for prop firm risk management.",
    inputSchema: positionSizeSchema,
  },
  handlePositionSize
);

// 3. Daily Loss Checker
server.registerTool(
  "risk_daily_loss",
  {
    title: "Daily Loss Checker",
    description:
      "Check current daily loss against your prop firm's limit. " +
      "Returns status (ok/warning/danger/stop), remaining buffer, and alerts.",
    inputSchema: dailyLossSchema,
  },
  handleDailyLoss
);

// 4. Prop Firm Rules
server.registerTool(
  "propfirm_rules",
  {
    title: "Prop Firm Rules",
    description:
      "Get the rules for a specific prop firm (FTMO, Topstep, Apex, The5ers, FundedNext). " +
      "Includes daily loss limits, max drawdown, news restrictions, and more.",
    inputSchema: propFirmRulesSchema,
  },
  handlePropFirmRules
);

// 5. Prop Firm Trade Validator
server.registerTool(
  "propfirm_can_trade",
  {
    title: "Prop Firm Trade Validator",
    description:
      "Validate whether you can take a trade given your current prop firm state. " +
      "Checks daily loss, drawdown, news restrictions, and trading day requirements.",
    inputSchema: propFirmCanTradeSchema,
  },
  handleCanTrade
);

// ---------- Start ----------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SMC AI MCP server running on stdio");
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});

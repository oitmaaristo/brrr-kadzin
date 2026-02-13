/**
 * Prop Firm rules engine
 *
 * Tools:
 *  - propfirm_rules     — Get rules for a specific prop firm
 *  - propfirm_can_trade — Validate if a trade is allowed given current state
 */

import { z } from "zod";

// --- Prop Firm Rules Database ---

export interface PropFirmRules {
  firm: string;
  daily_loss_limit: string;
  max_drawdown: string;
  min_trading_days: number;
  news_trading: boolean;
  weekend_holding: boolean;
  scaling_plan: boolean;
  max_position_size: string;
  notes: string[];
}

const PROP_FIRMS: Record<string, PropFirmRules> = {
  ftmo: {
    firm: "FTMO",
    daily_loss_limit: "5%",
    max_drawdown: "10%",
    min_trading_days: 4,
    news_trading: false,
    weekend_holding: true,
    scaling_plan: true,
    max_position_size: "varies by account",
    notes: [
      "No trading 2 minutes before/after high-impact news",
      "Challenge: 10% profit target, Verification: 5%",
      "Drawdown calculated from initial balance",
      "Swing accounts allow news trading and weekend holding",
    ],
  },
  topstep_50k: {
    firm: "Topstep 50K",
    daily_loss_limit: "$1,000",
    max_drawdown: "$2,000 (trailing)",
    min_trading_days: 0,
    news_trading: true,
    weekend_holding: false,
    scaling_plan: true,
    max_position_size: "5 contracts",
    notes: [
      "Trailing max drawdown — locks in profits",
      "No minimum trading days for evaluation",
      "Must close positions before 3:10 PM CT",
      "Futures only",
    ],
  },
  topstep_150k: {
    firm: "Topstep 150K",
    daily_loss_limit: "$3,000",
    max_drawdown: "$4,500 (trailing)",
    min_trading_days: 0,
    news_trading: true,
    weekend_holding: false,
    scaling_plan: true,
    max_position_size: "15 contracts",
    notes: [
      "Trailing max drawdown — locks in profits",
      "No minimum trading days for evaluation",
      "Must close positions before 3:10 PM CT",
      "Futures only",
    ],
  },
  apex: {
    firm: "Apex Trader Funding",
    daily_loss_limit: "trailing",
    max_drawdown: "trailing",
    min_trading_days: 7,
    news_trading: true,
    weekend_holding: false,
    scaling_plan: true,
    max_position_size: "varies by account",
    notes: [
      "Trailing drawdown only — no daily limit",
      "Must trade at least 7 days",
      "No positions during market close",
      "Futures only",
    ],
  },
  the5ers: {
    firm: "The5ers",
    daily_loss_limit: "3%",
    max_drawdown: "6%",
    min_trading_days: 3,
    news_trading: false,
    weekend_holding: true,
    scaling_plan: true,
    max_position_size: "varies by program",
    notes: [
      "No trading during high-impact news",
      "Hyper Growth: 6% target, 3% daily loss",
      "Scaling up to $4M",
      "Forex, metals, indices",
    ],
  },
  fundednext: {
    firm: "FundedNext",
    daily_loss_limit: "5%",
    max_drawdown: "10%",
    min_trading_days: 5,
    news_trading: false,
    weekend_holding: true,
    scaling_plan: true,
    max_position_size: "varies by account",
    notes: [
      "No news trading on evaluation accounts",
      "Phase 1: 8% target, Phase 2: 5% target",
      "15% profit sharing from challenge phase",
      "Scaling up to $4M",
    ],
  },
};

// --- Tool: propfirm_rules ---

export const propFirmRulesSchema = {
  firm: z
    .string()
    .describe(
      `Prop firm name. Available: ${Object.keys(PROP_FIRMS).join(", ")}`
    ),
};

export async function handlePropFirmRules(args: {
  firm: string;
}): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  const key = args.firm.toLowerCase().replace(/\s+/g, "_");
  const rules = PROP_FIRMS[key];

  if (!rules) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error: `Unknown prop firm: "${args.firm}"`,
            available: Object.keys(PROP_FIRMS),
          }),
        },
      ],
    };
  }

  return {
    content: [{ type: "text", text: JSON.stringify(rules, null, 2) }],
  };
}

// --- Tool: propfirm_can_trade ---

export const propFirmCanTradeSchema = {
  firm: z.string().describe("Prop firm name"),
  daily_loss_percent: z
    .number()
    .optional()
    .describe("Current daily loss as %"),
  total_drawdown_percent: z
    .number()
    .optional()
    .describe("Current total drawdown as %"),
  trading_days: z
    .number()
    .optional()
    .describe("Number of trading days completed"),
  has_news_soon: z
    .boolean()
    .optional()
    .describe("Is there high-impact news within the next 2 minutes?"),
};

export async function handleCanTrade(args: {
  firm: string;
  daily_loss_percent?: number;
  total_drawdown_percent?: number;
  trading_days?: number;
  has_news_soon?: boolean;
}): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  const key = args.firm.toLowerCase().replace(/\s+/g, "_");
  const rules = PROP_FIRMS[key];

  if (!rules) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error: `Unknown prop firm: "${args.firm}"`,
            available: Object.keys(PROP_FIRMS),
          }),
        },
      ],
    };
  }

  const violations: string[] = [];
  const warnings: string[] = [];

  // Check daily loss
  if (args.daily_loss_percent !== undefined) {
    const limitPct = parseFloat(rules.daily_loss_limit);
    if (!isNaN(limitPct)) {
      if (args.daily_loss_percent >= limitPct) {
        violations.push(
          `Daily loss ${args.daily_loss_percent}% >= limit ${limitPct}%`
        );
      } else if (args.daily_loss_percent >= limitPct * 0.8) {
        warnings.push(
          `Daily loss ${args.daily_loss_percent}% approaching limit ${limitPct}%`
        );
      }
    }
  }

  // Check total drawdown
  if (args.total_drawdown_percent !== undefined) {
    const ddLimit = parseFloat(rules.max_drawdown);
    if (!isNaN(ddLimit)) {
      if (args.total_drawdown_percent >= ddLimit) {
        violations.push(
          `Total drawdown ${args.total_drawdown_percent}% >= limit ${ddLimit}%`
        );
      } else if (args.total_drawdown_percent >= ddLimit * 0.8) {
        warnings.push(
          `Total drawdown ${args.total_drawdown_percent}% approaching limit ${ddLimit}%`
        );
      }
    }
  }

  // Check news
  if (args.has_news_soon && !rules.news_trading) {
    violations.push(
      `${rules.firm} does not allow trading during high-impact news`
    );
  }

  const canTrade = violations.length === 0;

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            can_trade: canTrade,
            firm: rules.firm,
            violations,
            warnings,
            rules_summary: {
              daily_loss_limit: rules.daily_loss_limit,
              max_drawdown: rules.max_drawdown,
              news_trading_allowed: rules.news_trading,
            },
          },
          null,
          2
        ),
      },
    ],
  };
}

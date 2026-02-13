/**
 * Risk management tools — position sizing & daily loss tracking
 *
 * Tools:
 *  - risk_position_size   — Calculate lot size for a trade
 *  - risk_daily_loss      — Check current drawdown vs prop firm limit
 */

import { z } from "zod";

// --- Position Sizer ---

export const positionSizeSchema = {
  account_size: z.number().positive().describe("Account balance in base currency"),
  risk_percent: z.number().min(0.1).max(10).describe("Risk per trade as % of account (e.g. 1 = 1%)"),
  sl_pips: z.number().positive().describe("Stop loss distance in pips"),
  pip_value: z
    .number()
    .positive()
    .optional()
    .describe("Value of 1 pip per standard lot (default: 10 for forex majors)"),
};

export async function handlePositionSize(args: {
  account_size: number;
  risk_percent: number;
  sl_pips: number;
  pip_value?: number;
}): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  const pipValue = args.pip_value ?? 10; // $10/pip for standard lot on most forex majors
  const riskAmount = args.account_size * (args.risk_percent / 100);
  const lots = riskAmount / (args.sl_pips * pipValue);
  const roundedLots = Math.floor(lots * 100) / 100; // round down to 0.01

  const result = {
    account_size: args.account_size,
    risk_percent: args.risk_percent,
    risk_amount: Math.round(riskAmount * 100) / 100,
    sl_pips: args.sl_pips,
    pip_value: pipValue,
    position_size_lots: roundedLots,
    position_size_mini_lots: roundedLots * 10,
    position_size_micro_lots: roundedLots * 100,
  };

  return {
    content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
  };
}

// --- Daily Loss Checker ---

export const dailyLossSchema = {
  starting_equity: z.number().positive().describe("Account equity at start of day"),
  current_equity: z.number().positive().describe("Current account equity"),
  daily_loss_limit_percent: z
    .number()
    .min(0)
    .max(100)
    .describe("Maximum daily loss allowed as % (e.g. 5 for FTMO)"),
  open_risk: z
    .number()
    .optional()
    .describe("Risk of currently open positions in currency"),
};

export async function handleDailyLoss(args: {
  starting_equity: number;
  current_equity: number;
  daily_loss_limit_percent: number;
  open_risk?: number;
}): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  const loss = args.starting_equity - args.current_equity;
  const lossPct = (loss / args.starting_equity) * 100;
  const limitAmount =
    args.starting_equity * (args.daily_loss_limit_percent / 100);
  const remaining = limitAmount - loss;
  const openRisk = args.open_risk ?? 0;
  const effectiveRemaining = remaining - openRisk;

  type AlertLevel = "ok" | "warning" | "danger" | "stop";
  let status: AlertLevel = "ok";
  if (lossPct >= args.daily_loss_limit_percent) {
    status = "stop";
  } else if (lossPct >= args.daily_loss_limit_percent * 0.8) {
    status = "danger";
  } else if (lossPct >= args.daily_loss_limit_percent * 0.6) {
    status = "warning";
  }

  const alerts: string[] = [];
  if (status === "stop") {
    alerts.push(
      `STOP TRADING — Daily loss limit reached (${lossPct.toFixed(1)}%)`
    );
  } else if (status === "danger") {
    alerts.push(
      `Daily loss at ${lossPct.toFixed(1)}% — limit is ${args.daily_loss_limit_percent}%. Consider stopping.`
    );
  } else if (status === "warning") {
    alerts.push(
      `Daily loss at ${lossPct.toFixed(1)}% — approaching limit of ${args.daily_loss_limit_percent}%.`
    );
  }

  if (openRisk > 0 && effectiveRemaining < 0) {
    alerts.push(
      `Open positions risk ($${openRisk}) exceeds remaining buffer ($${remaining.toFixed(2)}). Reduce exposure!`
    );
  }

  const result = {
    status,
    starting_equity: args.starting_equity,
    current_equity: args.current_equity,
    loss_amount: Math.round(loss * 100) / 100,
    loss_percent: Math.round(lossPct * 100) / 100,
    daily_limit_percent: args.daily_loss_limit_percent,
    daily_limit_amount: Math.round(limitAmount * 100) / 100,
    remaining_before_limit: Math.round(remaining * 100) / 100,
    open_risk: openRisk,
    effective_remaining: Math.round(effectiveRemaining * 100) / 100,
    can_trade: status !== "stop",
    alerts,
  };

  return {
    content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
  };
}

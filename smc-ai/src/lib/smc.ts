/**
 * Smart Money Concepts detection logic
 *
 * Core SMC structures: Order Blocks, Fair Value Gaps, BOS/CHoCH,
 * Kill Zones, Liquidity levels
 */

// --- Types ---

export type Bias = "bullish" | "bearish" | "neutral";
export type Trend = "uptrend" | "downtrend" | "ranging";
export type OBType = "bullish" | "bearish";
export type SessionName = "asian" | "london" | "new_york" | "london_close";

export interface OrderBlock {
  type: OBType;
  zone: [number, number]; // [low, high]
  strength: "strong" | "moderate" | "weak";
  mitigated: boolean;
}

export interface FairValueGap {
  type: "bullish" | "bearish";
  zone: [number, number];
  filled: boolean;
}

export interface MarketStructure {
  trend: Trend;
  last_bos: string | null;
  last_choch: string | null;
}

export interface Liquidity {
  buy_side: number[];
  sell_side: number[];
}

export interface KillZone {
  active: boolean;
  session: SessionName;
  time_remaining: string;
}

export interface TradeIdea {
  direction: "long" | "short";
  entry_zone: [number, number];
  sl: number;
  tp1: number;
  tp2: number;
  rr: string;
}

export interface SMCAnalysis {
  bias: Bias;
  confidence: number;
  market_structure: MarketStructure;
  order_blocks: OrderBlock[];
  fvg: FairValueGap[];
  liquidity: Liquidity;
  kill_zone: KillZone;
  trade_idea: TradeIdea | null;
}

// --- Kill Zone Schedule (UTC) ---

interface KillZoneWindow {
  name: SessionName;
  start: number; // hour UTC
  end: number;   // hour UTC
}

const KILL_ZONES: KillZoneWindow[] = [
  { name: "asian", start: 0, end: 3 },
  { name: "london", start: 7, end: 10 },
  { name: "new_york", start: 12, end: 15 },
  { name: "london_close", start: 15, end: 17 },
];

export function getActiveKillZone(): KillZone {
  const now = new Date();
  const hour = now.getUTCHours();
  const minute = now.getUTCMinutes();

  for (const kz of KILL_ZONES) {
    if (hour >= kz.start && hour < kz.end) {
      const remainingMinutes = (kz.end - hour) * 60 - minute;
      const h = Math.floor(remainingMinutes / 60);
      const m = remainingMinutes % 60;
      return {
        active: true,
        session: kz.name,
        time_remaining: `${h}h ${m}m`,
      };
    }
  }

  // Find next kill zone
  let nextKz = KILL_ZONES.find((kz) => kz.start > hour);
  if (!nextKz) nextKz = KILL_ZONES[0]; // wrap to asian

  return {
    active: false,
    session: nextKz.name,
    time_remaining: "not active",
  };
}

/**
 * Parse SMC analysis from Claude Vision response text.
 * The Vision API returns structured JSON — this validates and
 * normalises it. Falls back to a neutral analysis on parse failure.
 */
export function parseSMCAnalysis(raw: string): SMCAnalysis {
  try {
    const data = JSON.parse(raw);
    return {
      bias: data.bias ?? "neutral",
      confidence: data.confidence ?? 0,
      market_structure: data.market_structure ?? {
        trend: "ranging",
        last_bos: null,
        last_choch: null,
      },
      order_blocks: data.order_blocks ?? [],
      fvg: data.fvg ?? [],
      liquidity: data.liquidity ?? { buy_side: [], sell_side: [] },
      kill_zone: data.kill_zone ?? getActiveKillZone(),
      trade_idea: data.trade_idea ?? null,
    };
  } catch {
    return {
      bias: "neutral",
      confidence: 0,
      market_structure: { trend: "ranging", last_bos: null, last_choch: null },
      order_blocks: [],
      fvg: [],
      liquidity: { buy_side: [], sell_side: [] },
      kill_zone: getActiveKillZone(),
      trade_idea: null,
    };
  }
}

/**
 * smc_analyze — SMC chart analysis tool
 *
 * Accepts either a base64 chart image or a symbol+timeframe pair.
 * When an image is provided it goes through Claude Vision;
 * symbol+timeframe returns a mock for now (needs market data feed later).
 */

import { z } from "zod";
import { analyzeChartImage } from "../lib/vision.js";
import { parseSMCAnalysis, getActiveKillZone } from "../lib/smc.js";
import type { SMCAnalysis } from "../lib/smc.js";

export const analyzeSchema = {
  image: z
    .string()
    .optional()
    .describe("Base64-encoded chart image"),
  image_media_type: z
    .enum(["image/png", "image/jpeg", "image/webp", "image/gif"])
    .optional()
    .describe("Media type of the image (default: image/png)"),
  symbol: z
    .string()
    .optional()
    .describe("Trading symbol, e.g. EURUSD, NQ, ES"),
  timeframe: z
    .string()
    .optional()
    .describe("Chart timeframe, e.g. 1M, 5M, 15M, 1H, 4H, 1D"),
};

export async function handleAnalyze(args: {
  image?: string;
  image_media_type?: "image/png" | "image/jpeg" | "image/webp" | "image/gif";
  symbol?: string;
  timeframe?: string;
}): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  // Validate: need either image or symbol
  if (!args.image && !args.symbol) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error:
              "Provide either an image (base64) or a symbol to analyze.",
          }),
        },
      ],
    };
  }

  let analysis: SMCAnalysis;

  if (args.image) {
    // Real vision analysis
    try {
      const raw = await analyzeChartImage({
        image: args.image,
        mediaType: args.image_media_type,
      });
      analysis = parseSMCAnalysis(raw);
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Vision analysis failed";
      return {
        content: [{ type: "text", text: JSON.stringify({ error: msg }) }],
      };
    }
  } else {
    // Mock response for symbol+timeframe (real data feed comes in Phase 2)
    analysis = buildMockAnalysis(args.symbol!, args.timeframe ?? "1H");
  }

  // Attach live kill zone info
  analysis.kill_zone = getActiveKillZone();

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(analysis, null, 2),
      },
    ],
  };
}

function buildMockAnalysis(symbol: string, timeframe: string): SMCAnalysis {
  return {
    bias: "bullish",
    confidence: 0.72,
    market_structure: {
      trend: "uptrend",
      last_bos: "1.0892",
      last_choch: null,
    },
    order_blocks: [
      {
        type: "bullish",
        zone: [1.0845, 1.086],
        strength: "strong",
        mitigated: false,
      },
    ],
    fvg: [
      { type: "bullish", zone: [1.087, 1.0878], filled: false },
    ],
    liquidity: {
      buy_side: [1.092, 1.0945],
      sell_side: [1.081, 1.0795],
    },
    kill_zone: getActiveKillZone(),
    trade_idea: {
      direction: "long",
      entry_zone: [1.085, 1.086],
      sl: 1.083,
      tp1: 1.092,
      tp2: 1.0945,
      rr: "3.2:1",
    },
  };
}

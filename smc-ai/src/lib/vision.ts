/**
 * Claude Vision wrapper for chart image analysis.
 *
 * Sends chart screenshots to Claude's vision model and requests
 * structured SMC analysis output.
 */

import Anthropic from "@anthropic-ai/sdk";

const SMC_SYSTEM_PROMPT = `You are an expert Smart Money Concepts (ICT-style) chart analyst.
Analyze the trading chart image and return a JSON object with the following structure:

{
  "bias": "bullish" | "bearish" | "neutral",
  "confidence": 0.0 - 1.0,
  "market_structure": {
    "trend": "uptrend" | "downtrend" | "ranging",
    "last_bos": "price_level" | null,
    "last_choch": "price_level" | null
  },
  "order_blocks": [
    { "type": "bullish" | "bearish", "zone": [low, high], "strength": "strong" | "moderate" | "weak", "mitigated": false }
  ],
  "fvg": [
    { "type": "bullish" | "bearish", "zone": [low, high], "filled": false }
  ],
  "liquidity": {
    "buy_side": [price_levels],
    "sell_side": [price_levels]
  },
  "trade_idea": {
    "direction": "long" | "short",
    "entry_zone": [low, high],
    "sl": price,
    "tp1": price,
    "tp2": price,
    "rr": "ratio"
  } | null
}

Rules:
- Identify Break of Structure (BOS) and Change of Character (CHoCH)
- Mark unmitigated Order Blocks with their strength
- Detect Fair Value Gaps and whether they have been filled
- Identify liquidity pools (equal highs/lows, trendline liquidity)
- Only suggest a trade idea if there is a clear setup with >= 2:1 RR
- Return ONLY valid JSON, no markdown, no explanation`;

let client: Anthropic | null = null;

function getClient(): Anthropic {
  if (!client) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error(
        "ANTHROPIC_API_KEY environment variable is required. " +
          "Set it in your .env or MCP config."
      );
    }
    client = new Anthropic({ apiKey });
  }
  return client;
}

export interface VisionAnalysisOptions {
  image: string; // base64 encoded image
  mediaType?: "image/png" | "image/jpeg" | "image/webp" | "image/gif";
  model?: string;
}

/**
 * Analyze a chart image using Claude Vision.
 * Returns the raw JSON string from Claude.
 */
export async function analyzeChartImage(
  options: VisionAnalysisOptions
): Promise<string> {
  const anthropic = getClient();
  const mediaType = options.mediaType ?? "image/png";
  const model = options.model ?? "claude-sonnet-4-20250514";

  const response = await anthropic.messages.create({
    model,
    max_tokens: 2048,
    system: SMC_SYSTEM_PROMPT,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: mediaType,
              data: options.image,
            },
          },
          {
            type: "text",
            text: "Analyze this chart using Smart Money Concepts. Return JSON only.",
          },
        ],
      },
    ],
  });

  const textBlock = response.content.find((b) => b.type === "text");
  if (!textBlock || textBlock.type !== "text") {
    throw new Error("No text response from Claude Vision");
  }
  return textBlock.text;
}

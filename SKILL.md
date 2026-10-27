---
name: tradingview-chart
description: Draw verified, interactive financial charts — candlesticks, volume, MA20/MA50, and support/resistance levels — using the TradingView Lightweight Charts library. Use whenever a conversation involves substantive analysis of a stock, ETF, index, or crypto (price position, trend, support/resistance, buy/sell timing), or when the user asks for a K线图 / 行情图 / candlestick chart / TradingView-style chart / OHLCV visualization — even if they never name this skill explicitly. If you are about to discuss where a price sits without showing it, that is the moment to reach for this skill.
---

# TradingView Chart

Render interactive financial charts with the open-source **Lightweight Charts 5.0.0** library: candles, volume, moving averages, reference levels, zoom/pan and crosshair.

"TradingView" here means the chart *library*, not the website. Never substitute a screenshot of tradingview.com; Advanced Charts is a separate licensed product — use it only when the user explicitly requests it and access exists.

## Core principle: verified data first, chart second

The builder deliberately has **no market-data access**. It accepts only a JSON file of bars you obtained and verified in this session. This separation exists so that every candle on screen traces back to a real source — an agent that can both fetch and render in one step will eventually chart hallucinated prices. Never invent candles, interpolate across market holidays, fill missing volume with zero, or present historical closes as live prices. If trustworthy data cannot be obtained, say so instead of charting.

## Workflow

1. **Scope the instrument.** Confirm ticker, exchange, currency, and market timezone. Chart the securities actually under analysis, not incidental mentions. Honor an explicit request to skip charts.

2. **Obtain and verify OHLCV** from whatever market-data tools the host environment offers (broker SDKs, public quote endpoints, data files). Prefer 6–12 months of daily bars, plus longer weekly context when available; disclose shorter coverage. Keep price and volume on one feed — if feed coverage conflicts, disclose it and avoid volume-based conclusions. Record provenance as you go: source name and URL, retrieval time, last trading session, adjustment convention (raw / 前复权 qfq / etc.), and any volume unit conversion (e.g. lots 手 × 100 → shares 股/份).

3. **Write the data JSON** (schema below). A complete working example lives at [`docs/examples/NVDA.json`](docs/examples/NVDA.json) — copy its shape, including the provenance fields.

4. **Check and build the chart** with the bundled script (Python 3.10+, standard library only):

   ```bash
   python <skill-directory>/scripts/build_chart.py --input <absolute data.json> --output <absolute chart.html>
   ```

   Before rendering, run `python <skill-directory>/scripts/build_chart.py --input <absolute data.json> --check --report <absolute quality.json>`. Fix errors (exit code `2`) and disclose material warnings. Reports summarize supplied sessions, missing volume and MA availability; they do not verify quotes, market calendars or adjustments. Missing retrieval time is a warning, not a build failure. Record `retrieved_utc` as an ISO 8601 UTC datetime with `Z` or `+00:00` when known. Add `--report` to a normal build to save the same quality report. Never treat an old output file as a successful build after a failed command.

   - Default output is an HTML **fragment** for hosts that provide an inline-rendering/visualize skill — follow that host's rendering contract and save fragments where the host expects them.
   - Add `--standalone` for a self-contained page with its own light/dark theme when no rendering host exists.
   - The builder validates OHLC bounds, rejects duplicate or non-canonical dates, sorts chronologically, omits missing volume, and embeds text safely. The generated page loads the pinned library from jsDelivr (needs internet) and makes no market-data requests of its own.

5. **Verify the render** before presenting: preview via the host's render helper, or screenshot the standalone page with a headless browser. Check candles, volume pane, MA lines, axes, crosshair, and level labels. If the library failed to load, report that honestly rather than describing a chart nobody can see.

6. **Present with judgment.** Pair the chart with a concise read of price position relative to the moving averages and levels. If the user wants a trade plan, it must include trigger, invalidation, sizing, and portfolio fit using known current holdings. Never execute orders.

## Data JSON schema

Required fields (UTF-8):

- `symbol` — ticker, ideally with exchange and name
- `currency` — price currency
- `as_of` — last session date, market timezone, regular/after-hours and delay note
- `source_name`, `source_url` — where the data came from
- `adjustment` — adjustment convention and volume unit conversion
- `bars` — non-empty array of `{time, open, high, low, close, volume?}`; `time` is `YYYY-MM-DD`, prices are positive finite numbers satisfying OHLC bounds, volume is a nonnegative finite number in shares/units (not lots, not turnover) — omit volume when missing, never fill zero

Optional: `locale` (`en-US` for English labels or `zh-CN`, the default), `levels` (array of `{price, title, kind}` where kind is `support` or `resistance`), `retrieved_utc`, and other provenance fields.

Levels are research annotations — keep analyst support/resistance lines visually and conceptually separate from market data, and never present them as fair value. The full field reference and validation rules are in [README.md](README.md).

## Moving averages and coverage

MA20/MA50 are computed from the input closes and drawn only when the data covers the window. The builder does not repair adjustment inconsistencies, backfill missing sessions, or validate quotes — that responsibility stays with the data-verification step, which is why it cannot be skipped.

## Licensing and attribution

Templates embed the required TradingView attribution and link — preserve both. The skill, scripts and templates are MIT-licensed; Lightweight Charts is Apache-2.0 by TradingView (see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). When redistributing the library itself, preserve its license and NOTICE.

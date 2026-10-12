---
name: tradingview-chart
description: Draw interactive stock, ETF, index and crypto charts using TradingView Lightweight Charts. Use automatically during substantive security discussions about price position, trends and buy/sell decisions, or when the user requests the TradingView chart library.
---

# TradingView chart

The user means the chart library, not the TradingView website. Default to open-source Lightweight Charts; do not substitute a TradingView webpage or screenshot. Advanced Charts is a separate product requiring access; use it only when requested and available.

## Workflow

1. Verify ticker, exchange, currency and market timezone. Chart the securities actually analyzed, not incidental mentions. Honor an explicit request to skip charts.
2. Obtain genuine dated OHLCV from available market-data tools or public sources. Record source URLs, retrieval date, last session, adjustment convention and delay. The library supplies rendering, not quotes. Never invent candles, interpolate missing sessions or call historical closes live. Keep price and volume on one feed; if feed coverage conflicts, disclose it and avoid volume-based conclusions.
3. Prefer 6–12 months of daily history and longer weekly context when available. Disclose shorter coverage. Show candles, verified volume, MA20/50 only with sufficient observations, and a few evidence-based support/resistance lines. Separate analyst levels from market data and fair-value judgments.
4. For an in-conversation chart, read the host's visualize skill if available and follow its rendering contract. Generate an inline fragment with `assets/chart-fragment.html` and `scripts/build_chart.py`. It uses pinned Lightweight Charts 5.0.0, native zoom/pan/crosshair, embedded data and TradingView attribution. Preserve the attribution and TradingView link. If redistributing the library itself, preserve its license and NOTICE. Do not add market-data network calls to inline fragments.
5. Save data and a concise source note in the user's project according to its conventions. Save inline fragments in the host's supplied visualization directory. If there is no inline rendering host, use `--standalone` to create an ordinary HTML page with its own theme, without depending on another skill. Preview with the host's render helper (when available) or open the standalone page in a browser. Verify candles, axes, resize, crosshair and levels. Report failed library loading honestly.
6. Display the chart in the final response with a concise price-position judgment. A trade plan must include trigger, invalidation, sizing and portfolio fit using current holdings when known. Do not execute orders.

## Build

Provide UTF-8 JSON fields `symbol`, `currency`, `as_of` (last session and market timezone), `source_name`, `source_url`, `adjustment`, `bars` and optional `levels`. Bars contain ISO `time`, numeric `open/high/low/close`, optional nonnegative `volume`. Levels contain numeric `price`, `title`, `kind` (`support` or `resistance`). Missing volume is omitted, never filled with zero. Refresh snapshots for subsequent current-price discussions.

```powershell
python <skill-directory>/scripts/build_chart.py --input <absolute-data.json> --output <absolute-fragment.html>
```

The builder validates OHLC bounds, dates and volume, sorts chronologically and embeds JSON safely with a unique root ID.

For a standalone browser page, add `--standalone`. Python 3.10+ is required; the builder uses only the standard library. The output embeds observations and loads the pinned chart library from jsDelivr; it needs internet access for that library. No market-data requests are made by the generated chart. See [README.md](README.md) for installation and the JSON schema.

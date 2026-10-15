# Screenshot provenance / 截图来源

These are browser screenshots of this package's chart builder. The current gallery shows **NVIDIA (NVDA), Apple (AAPL), and Microsoft (MSFT)** with English labels, sourced from Yahoo Finance daily historical OHLCV. They are not fabricated charts or screenshots of tradingview.com.

截图制作于 **2026-10-15（Asia/Taipei）**；行情最后交易日为 **2026-10-14（America/New_York）**。这些是历史常规盘收盘数据，非实时或盘后报价。

| Input | Instrument | Market / currency | Coverage | Screenshot |
| --- | --- | --- | --- | --- |
| [NVDA.json](examples/NVDA.json) | NVIDIA / 英伟达 | NASDAQ / USD | 2025-10-15–2026-10-14, 251 bars | [Dark](images/nvda-dark.jpg) |
| [AAPL.json](examples/AAPL.json) | Apple / 苹果 | NASDAQ / USD | Same 251 sessions | [Light](images/aapl-light.jpg) |
| [MSFT.json](examples/MSFT.json) | Microsoft / 微软 | NASDAQ / USD | Same 251 sessions | [Light](images/msft-light.jpg) |

## Data conventions

- Yahoo Finance chart endpoint, daily `indicators.quote` OHLCV. Exact HTTPS query URLs and UTC retrieval timestamps are retained in each JSON. Retrieved on 2026-10-15 UTC / Asia/Taipei.
- All three instruments were verified as NasdaqGS (`NMS`), USD, `America/New_York`. Daily timestamps were mapped to that market timezone before assigning session dates.
- The query uses a fixed end cutoff of 2026-10-15 00:00 UTC, so it excludes the 2026-10-15 US session. No incomplete current-day bar is displayed.
- OHLC is used as returned by the quote endpoint, not the separate dividend-adjusted `adjclose` series. Cash dividends are not adjusted. The returned corporate-action events contain no splits within the displayed window. These are price charts, not total-return charts.
- Volume is the same provider's daily share count. No lot conversion, source mixing, missing-volume substitution or market-holiday interpolation.
- All 251 observations per ticker passed finite-value, OHLC-bound and unique-date validation; no missing OHLC observations were dropped.
- MA20/MA50 use supplied closes and begin after their respective windows; there is no pre-window warmup.
- No support/resistance levels were added. Candles use green up / red down. `locale: "en-US"` selects English titles, dates, OHLC readouts, volume legends and source labels.

The market data is not covered by the repository's MIT software license. See [third-party notices](../THIRD_PARTY_NOTICES.md).

## Reproduce

```bash
python scripts/build_showcase.py
python -m http.server 8765 --directory output/showcase
```

Open `http://localhost:8765/NVDA.html`, `AAPL.html`, or `MSFT.html`. The script fixes each page's light/dark scheme for repeatable documentation captures. The chart library needs a CDN connection; market data is embedded in each page.

The committed JPEGs were captured at the default 1280×720 browser viewport, preserving the source label, last session, axes and TradingView attribution. Capture after the library loads. The earlier ETF example inputs and screenshots remain in Git for compatibility; the README and showcase builder now use these US stocks.

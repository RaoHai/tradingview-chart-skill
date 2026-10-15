# Screenshot provenance / 截图来源

These are browser screenshots of the included builder, not fabricated chart images or screenshots of tradingview.com. Price and volume are from the same Tencent Finance daily snapshot. No private account information is included.

这些图片是本包生成器实际渲染的浏览器截图。截图制作于 **2026-10-15（Asia/Taipei）**，行情最后交易日是 **2026-10-12**；两者不可混为一谈。

| Input | Instrument | Market / currency | Coverage | Screenshot |
| --- | --- | --- | --- | --- |
| [588000.json](examples/588000.json) | STAR 50 ETF / 科创50ETF | SSE / CNY | 2026-02-06–2026-10-12, 160 bars | [Light](images/star50-light.jpg) |
| [515000.json](examples/515000.json) | Technology leaders ETF / 科技龙头ETF | SSE / CNY | Same 160 sessions | [Light](images/technology-light.jpg) |
| [512800.json](examples/512800.json) | Bank ETF / 银行ETF | SSE / CNY | Same 160 sessions | [Dark](images/bank-dark.jpg) |

## Data conventions

- Regular-session daily observations, Asia/Shanghai (UTC+8); frozen historical closes, not live or intraday quotes.
- Tencent `qfqday` forward-adjusted OHLC. Each JSON retains its exact HTTPS source URL and original UTC retrieval timestamp (2026-10-12 UTC / 2026-10-13 UTC+8).
- Tencent's volume field is in 100-unit lots; converted by ×100 to ETF units. Both price and volume are sourced from Tencent. Independent unit checks on overlapping minute observations confirmed the scale, with provider aggregate differences up to approximately 1.71%; no feeds are spliced.
- These snapshots are the last 160 observations of the original source response. No holiday interpolation or fabricated volume. Input validation checks finite values, OHLC bounds and unique ISO dates.
- MA20/MA50 use the supplied closes. Their lines start after 20/50 observations; there is no pre-window warmup in these examples.
- No support/resistance levels were added to these screenshots. The builder supports such analyst annotations, but the gallery only demonstrates market data, volume and moving averages.
- Candles use green up / red down. The screenshot labels currently use Chinese, independently of the README language.

The market data is not licensed under the repository's MIT software license. See [third-party notices](../THIRD_PARTY_NOTICES.md).

## Reproduce

```bash
python scripts/build_showcase.py
python -m http.server 8765 --directory output/showcase
```

Open `http://localhost:8765/588000.html`, `515000.html`, or `512800.html`. The script builds each page with the unchanged chart generator and fixes its light/dark scheme for repeatable documentation captures. The chart library needs a CDN connection.

The committed JPEGs were captured at the browser's default 1280×720 viewport, preserving the source label, date, axes and TradingView attribution. Capture the rendered browser viewport after the library has loaded. Screenshot files may be attached to a project introduction; retain context that these are historical demonstration data.

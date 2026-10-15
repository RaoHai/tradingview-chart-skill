# Third-party notices

The generated chart loads **TradingView Lightweight Charts™ 5.0.0** from:

https://cdn.jsdelivr.net/npm/lightweight-charts@5.0.0/dist/lightweight-charts.standalone.production.js

Upstream: https://github.com/tradingview/lightweight-charts

Copyright TradingView, Inc. Licensed under the Apache License, Version 2.0.
A copy of the license from the pinned npm package is included at
`licenses/lightweight-charts-5.0.0-APACHE-2.0.txt`.
The chart library itself is not bundled in this repository or the generated HTML.
The template keeps `attributionLogo: true` and a visible link to
https://www.tradingview.com/. Preserve attribution and any applicable upstream
license and NOTICE files if you later redistribute the library itself.

This is an independent community skill, not an official TradingView product.

`examples/588000-historical.json` contains a small, frozen historical quotation
sample from Tencent Finance. The source URL, retrieval timestamp, market,
currency, date range and adjustment convention are in that file. The volume is
converted from 100-unit lots to ETF units. The repository's MIT software license
does not grant rights in third-party market data.

The additional `docs/examples/*.json` snapshots and `docs/images/*.jpg`
screenshots use the same Tencent Finance source. Their dates, conventions and
reproduction steps are documented in [docs/SHOWCASE.md](docs/SHOWCASE.md).

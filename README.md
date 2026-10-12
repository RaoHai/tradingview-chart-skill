# tradingview-chart

An agent skill for verified financial charts with TradingView Lightweight Charts™.

给 Codex 等支持 `SKILL.md` 的智能体使用的交互行情图技能：日 K、成交量、MA20/MA50、参考价位、缩放拖动与十字光标。使用开源 **Lightweight Charts 5.0.0**，并非 TradingView 网站截图或 Advanced Charts。

## 安装

将本仓库克隆到智能体的技能目录，文件夹命名为 `tradingview-chart`。Codex 的常见安装方式：

```bash
git clone https://github.com/RaoHai/tradingview-chart-skill.git ~/.codex/skills/tradingview-chart
```

Windows PowerShell：

```powershell
git clone https://github.com/RaoHai/tradingview-chart-skill.git "$env:USERPROFILE/.codex/skills/tradingview-chart"
```

若设置了 `CODEX_HOME`，使用其 `skills/tradingview-chart` 目录。已有同名技能时先比较内容，避免覆盖本地修改。启动新的会话加载技能后，可以说：

> 使用 $tradingview-chart 核验 588000 的近一年日线，画出成交量、MA20/MA50，并说明数据日期和复权口径。

技能要求智能体先获取并核验真实 OHLCV，再生成图。**不自带行情订阅、数据下载器或交易执行功能。** 数据获取依赖宿主可用工具；生成器只接受 JSON。

## 独立运行

需要 Python 3.10+，无 pip 运行依赖。浏览器需联网加载固定版本的图表库。

```bash
python scripts/build_chart.py --input examples/588000-historical.json --output output/chart.html --standalone
python -m http.server 8765 --directory output
```

浏览器打开 `http://localhost:8765/chart.html`。也可直接打开生成的 HTML。例子是上交所 588000 的 **2025 年历史行情**，仅用于演示，日期、来源、复权及量能单位都记录在 JSON 中；不代表当前价格。

去掉 `--standalone` 则输出 HTML 片段，供支持内联 HTML 的宿主渲染。片段使用宿主主题变量；独立网页自带亮暗主题，不依赖 Codex 或另一项技能。嵌入时需允许 jsDelivr 脚本与片段中的脚本执行。

## 输入格式

必需字段：

| 字段 | 含义 |
| --- | --- |
| `symbol` | 代码，建议附交易所和名称 |
| `currency` | 价格币种 |
| `as_of` | 最后交易日、市场时区、常规盘／盘后与延迟说明 |
| `source_name`, `source_url` | 数据来源名称与 HTTPS 地址 |
| `adjustment` | 不复权／前复权等口径及量能单位转换 |
| `bars` | 非空日线数组：`time`, `open`, `high`, `low`, `close`，可选 `volume` |

`time` 必须是 `YYYY-MM-DD`；日期不得重复，生成器会排序。价格须为正的有限数且满足 OHLC 上下界；量须为非负有限数，缺量直接省略，不能填零。`volume` 使用份／股，不是成交额或手数。

可选 `levels` 数组，每项包含正数 `price`、文字 `title` 和 `kind`（`support` / `resistance`）。这些是研究参考线，不是公允价值。可添加 `retrieved_utc` 等追溯字段。

MA 按输入日线收盘价计算，窗口不足时不绘制。计算不修复复权不一致、缺失交易日或错误行情，调用方须先核验数据。休市日不插值。文字内容以安全编码嵌入，避免源数据中的 HTML 结束脚本标签。

## 验证

```bash
python -m unittest discover -s tests -v
```

覆盖 OHLC 约束、非有限数、日期冲突、缺量保留、排序、嵌入转义和独立网页输出。GitHub Actions 在 Python 3.10 / 3.13 运行这些检查。

## 许可与来源

本仓库原创技能、脚本和模板使用 [MIT License](LICENSE)。Lightweight Charts 由 TradingView 提供，使用 Apache-2.0，详情见 [第三方说明](THIRD_PARTY_NOTICES.md)。模板保留 TradingView 标识与链接；本项目与 TradingView 无隶属关系。

示例行情来自公开历史行情接口，保留来源元数据；行情数据不属于本仓库 MIT 软件授权范围。包内不含个人持仓、账户日志或科技／银行回测研究。

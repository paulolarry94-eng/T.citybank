# Funnel of three public strategy collections — pre-registration

Fixed 2026-11-01, before any result. The owner asked: take every strategy in these three collections, treat each as a
fresh idea, run it through our backtest universe and our test protocol, and show the results.

| Source (commit) | What it holds |
|---|---|
| trustdan/trend-following-backtesting-strategies @ a34b7ba | 48 TradingView Pine scripts: a Turtle/Seykota Donchian trend system (`turtle-core-v2.2`) and 47 variants (alt1–alt47), tested by the author on 21 US stocks and ETFs 2010–2025 |
| sofus-nl/swing-trading-strategies @ 1b7cf1c | 23 swing setups described in prose, for single US stocks, long only |
| paperswithbacktest/awesome-systematic-trading @ ddfee8b | 61 QuantConnect implementations of published anomalies (Quantpedia) |

Every strategy is listed in `INVENTORY.csv` with its class:

| Class | trustdan | sofus | awesome | Total |
|---|---:|---:|---:|---:|
| CFD lab (our 11 markets, Truth Lab protocol) | 48 | 18 | 2 | 68 |
| Futures funnel (pysystemtrade data, cross-asset rules) | 0 | 0 | 16 | 16 |
| Already tested in this project | 0 | 0 | 3 | 3 |
| Not testable with our data (reason in the inventory) | 0 | 5 | 40 | 45 |
| **Total** | **48** | **23** | **61** | **132** |

Priors (research memory): Donchian trend on our CFDs has been rejected four times by the lab's market-breadth gate
(positive on gold and USDJPY, negative on EURUSD, GBPUSD, indices, oil, silver: P6). Chart patterns failed (P14). Index
RSI(2) dip-buying failed after costs. Cross-sectional momentum on futures was rejected (Sharpe 0.00); futures trend +
carry survived (futures only). Published effects fade after publication (P11). So the expected answer is "mostly
rejected"; the funnel is run because the owner asked to check, and because exits, pyramiding and filters differ from
what we tested.

## A. CFD lab: common rules (all 68)

- Markets: XAUUSD, EURUSD, GBPUSD, USDJPY, US500, NAS100, GER40, UK100, JP225, WTI, XAGUSD (all 11 we hold, M1 bid
  2011–2025). The payday strategy uses the five index CFDs only.
- Bars: the lab's D1 bars (02:00 UTC boundaries). The Sunday-evening stub (22:00–02:00) is merged into Monday's bar.
  No entries in the first 260 merged bars (indicator warm-up, about the year 2011).
- Fills (Pine semantics, also how an EA works): decide at the bar's close; market orders fill at the open of the first
  minute after it (orders falling in the 20:30–23:00 UTC rollover block wait until 23:00); stop and limit orders are
  checked minute by minute; if a stop and a target trigger in the same minute the stop wins; a gap fills at the worse
  open. Longs pay the ask (bid + all-in cost), shorts pay it on exit.
- Costs: `research/truth/costs.json` all-in round-trip cost and overnight swap per night (Wednesday x3). The lab also
  reports stress (costs x1.5, swaps x2, +1 minute) and, separately, a low-cost swap-free profile (costs x0.5, no swap).
- Positions: one per market. Pyramid units belong to that position, and a whole position is one trade row (so unit
  adds do not inflate the trade count). R: 1% of equity per unit of risk. trustdan: one unit = the source's stop
  distance (stopN x ATR20 at entry). sofus and awesome: entry minus initial stop.
- Protocol: the Truth Lab unchanged (`research/truth/run.py`): look-ahead check; development 2011–19 gate (>= 200 trades,
  both eras 2011–15 and 2016–19 > 0, >= 9 of 11 markets > 0); best gated configuration by t; walk-forward; validation
  2020–22; stress; deflated Sharpe against the file's whole grid; ONE logged 2023–25 look per configuration; verdict.
- If more than one configuration in a file passes the gate, each further one gets its own final look in a new lab file
  named `<file>_<rule>_v1`, and its report states the parent file's configuration count.

## B. trustdan (lab file `funnel_trustdan_v1`, grid = 48 rules)

Translated line by line from the Pine source with the source's default inputs (both sides on, market filter off, volume
filter off). Pine semantics kept: N = ATR(20) (Wilder) frozen at entry; `entryPrice` and the add reference are the
signal bar's close; stop levels are recomputed every bar exactly as written (no ratchet unless the source has one);
`strategy.close` targets fire at the next open after the bar's high/low touched the level; partial closes are
first-in-first-out; unit sizes are the source's fractions of one unit.

Unavoidable deviations, fixed now:
1. Our stop protects the position from the entry minute (Pine leaves the entry bar without a stop).
2. Weekly values (alt4, alt17) as Pine shows them on historical bars: the last completed week, switching on Friday's bar.
3. alt18's regime symbol SPY is our US500 CFD (its SMA50 vs SMA200).
4. alt46's asset type: FX = "Stock" (3/6/9N), indices = "ETF" (4/7/10N), gold, silver, oil = "Commodity" (2/4/6N).
5. Share counts are not rounded; the day boundary is 02:00 UTC, not an exchange session.
6. alt20's source bug is kept (the long stop uses the 10-bar HIGH, the short stop the 10-bar LOW, so positions close
   at the next open): it is what the author tested ("0% success").
7. Their `sectors/*/alt9.pine` is a mislabelled copy of alt1; we test the `pine-scripts/` versions as named.

## C. sofus (lab file `funnel_sofus_v1`, grid = 18 rules x 2 sides = 36)

Price-only translation. Dropped everywhere (no data): volume, RS rank, earnings, news, sector baselines, the market
regime line and the site's A–D grade. Stock percentages become ATR(14) multiples at 2% per ATR (x% -> x/2 ATR). Swing
low/high = 3-bar fractal (the repo's glossary), known one bar later. Stops: the tighter of the listed stops that is on
the right side of the entry. Targets: limit orders with the listed fractions (50% when the source says "partial").
Trailing stops start after target 1 unless the source says otherwise and only move in the trade's favour. Hard exits
on a close fill at the next open. Sides: "long" (as written) and "both" (mirror image for shorts: highs/lows swapped,
above/below swapped, RSI x -> 100-x, +DI/-DI swapped). s10 is two-sided in the source; its "long" config is the
bullish half.

| Rule | Entry (close of the signal bar) | Exit |
|---|---|---|
| s01 VCP* | close > SMA50 > SMA150 > SMA200; last 65 bars hold >= 3 pullbacks (swing high to next low), the last three strictly shrinking and the last <= half the first; first close above the last swing high; prior rise >= 12.5 ATR in the 130 bars before the base; within 12.5 ATR of the 252-bar high | stop 1.5 ATR; 50% at +2 ATR, 50% at +4 ATR; after T1 exit on a close below the last swing low |
| s02 Cup & handle* | SMA50 > SMA200; handle of 5–15 bars (smallest that fits) under the right lip, low in the cup's upper half, depth <= 12% of the cup; cup 15–65 bars, depth 6–17.5 ATR, bottom in the middle 60% of the cup, right lip within 10% of depth of the left lip; prior rise >= 15 ATR in 130 bars; close above the handle high | stop 1.5 ATR; 40% at +2.5 ATR, 60% at +5 ATR; after T1 exit on a close below the last swing low or back below the right lip |
| s03 EMA 9/21 cross | EMA9 crosses above EMA21; close > SMA50; SMA50 >= its value 5 bars ago; ADX14 > 20; RSI14 in 50–70 | stop: tighter of EMA21 and 1.5 ATR; 50% at +1.5, 50% at +3 ATR; after T1 trail close − 1.5 ATR; exit on EMA9 < EMA21 |
| s04 RSI pullback | close > SMA200; RSI14 in 40–50 with RSI14 > 70 in the prior 10 bars; close > rising EMA21; close in the upper 60% of its range; ADX14 > 20 | stop: tighter of last swing low and 2 ATR; all at +1.5 ATR or on RSI14 crossing above 70; after 5 bars trail 2.5 ATR from the highest close |
| s07 Stage 2 | SMA150 above its value 20 bars ago; first close above the 63-bar high; close <= SMA150 + 7.5 ATR | stop: tighter of SMA150 and the 63-bar low; 50% at +10 ATR; stop trails SMA150; exit when SMA150 <= its value 10 bars ago |
| s08 Bull flag* | pole >= 5 ATR (lowest low of the 15 bars before the flag to the top just before it); flag 5–15 bars, retrace < 50% of the pole, all closes above EMA21; close above the flag high; RSI14 50–70 | stop: tighter of flag low and 1.5 ATR; 50% at breakout + pole, 50% at + 1.5 pole; after T1 trail the last swing low |
| s10 Triple RSI divergence* | three swing lows within 60 bars, each lower, with RSI14 at each higher; bullish engulfing or hammer within 5 bars after the third; RSI14 > 30 (mirror for shorts) | stop below the pattern low; 50% at the highest swing high inside the pattern (if above entry), 50% at +2 ATR; trail 2.5 ATR from the extreme |
| s11 Qullamaggie* | up-leg >= 15 ATR in the 63 bars before a 5–15 bar base whose range < 10% of the leg; ATR5 falling through the base; closes above a rising EMA20; close above the base high | stop: tighter of base low and 1.5 ATR; 50% at +2 ATR; rest: exit on close < EMA10 or trail highest high − 1.5 ATR; max 25 bars |
| s12 Multi-period strength | 63/126/252-bar returns > 0; close > SMA50 and SMA200, both rising (vs 5 bars ago); trigger: low <= EMA21 < close, or the first close above the 20-bar high after 5 bars without one | stop 2 ATR; 50% at +2.5 ATR; then swing-low trail; exit if the 63-bar return turns negative |
| s13 MA stack | EMA10 > EMA21 > SMA50 > SMA200, all above their values 5 bars ago; close within 2.5 ATR of EMA10 | stop: tighter of EMA21 and 1.5 ATR; 50% at +2.5 ATR; exit on EMA10 < EMA21 or a close < SMA50 |
| s14 ADX trend | ADX14 > 25 and above its value 3 bars ago; +DI > −DI with the gap widening; close > SMA50; close in the upper half of its range | stop: tighter of 1.5 ATR and last swing low; 50% at +2 ATR; trail close − 1.5 ATR; exit on ADX < 20, or −DI > +DI before T1 |
| s16 Trend template | 7 conditions (price > SMA150 & SMA200; SMA150 > SMA200; SMA200 > its value 21 bars ago; SMA50 > SMA150 & SMA200; price > SMA50; >= 15 ATR above the 252-bar low; within 12.5 ATR of the 252-bar high) all true today, and >= 2 failed on some day of the prior 20 | stop: tighter of 1.5 ATR and SMA50; 33% at +2 ATR; trail max(swing low, SMA50); exit on a close < SMA50 or any condition failing |
| s18 ROC breakout | close > prior 20-bar high; ROC21 > 0 and > its value 5 bars ago; close > SMA50 | stop: tighter of the prior 20-bar high and 1.5 ATR; 50% at +2 ATR; swing-low trail; exit when ROC21 < 0 |
| s19 HHV breakout | close > prior 20-bar high; close > SMA50 rising (vs 5 bars ago) | stop: tighter of the breakout bar's low and 2 ATR; exit on a close below the prior 10-bar low |
| s20 Frog in the pan | 126-bar return > 0; information discreteness in its own lowest third of the past 756 bars; no open gap > 3 ATR in 126 bars; close > SMA50 and SMA200; trigger as s12 | stop 2 ATR; 50% at +2.5 ATR; trail max(swing low, EMA21); exit on any gap > 2.5 ATR |
| s21 Proximity pullback | high of the last 10 bars within 2.5 ATR of the 252-bar high; pullback of 1.5–5 ATR from it over 3–10 bars; close above a rising EMA21 or rising SMA50; close in the upper half of the range | stop: tighter of the pullback low and 1.5 ATR; 50% at that high (if above entry), 50% at entry + 2 x depth; after T1 trail max(swing low, close − 1.5 ATR) |
| s22 RSI(2) reversion | close > SMA200; RSI2 < 10; close >= 252-bar low + 2.5 ATR | stop 2 ATR; exit when RSI2 crosses above 70, after 5 bars, or on a close < SMA200 |
| s23 Trend pullback | close > SMA50; EMA20 > SMA50, both rising (vs 5 bars ago); low within 1 ATR of EMA20 or SMA50; close in the upper half of its range | stop: tighter of EMA20 and 1.5 ATR; 50% at +2 ATR; trail max(swing low, highest high − 1.5 ATR); exit on two closes < SMA50 |

\* Mechanical approximations of discretionary chart patterns: their results speak about this reading, not about a
skilled chartist's. Not testable (5): s05 VWAP reclaim, s09 anchored VWAP, s17 volume-weighted trend (need traded
volume), s06 power earnings gap (earnings), s15 residual momentum (a stock cross-section).

## D. awesome-systematic-trading on CFDs (2 lab files)

- `ath_trend_v1` (trend-following-effect-in-stocks, applied to our markets): enter at the next open when the daily close
  >= the highest close of the prior 2,520 bars (all history we have before 2021); stop = close − 1 x ATR(10), raised
  each day and never lowered, checked intrabar. Sides: long (source) and both (mirror: a 10-year closing low -> short).
  11 markets, 2 configurations.
- `payday_indices_v1` (payday-anomaly): payday = the 15th (Saturday -> Friday 14th, Sunday -> Friday 13th); long from
  the 20:00 UTC H1 bar of payday (or of the last trading day before it in our data) to the 20:00 UTC bar of the next
  trading day; catastrophe stop 5%. Five index CFDs, 1 configuration (the anchors of `tom_indices_v2`).

## E. Futures funnel (`research/repofunnel/futures_funnel.py`, 16 strategies)

Cross-asset portfolios cannot run on our 11 CFDs, so they run on the futures data already in the project
(pysystemtrade, ends 2024-03-28). Daily return = change in the adjusted price / previous price of the traded contract.
Signals use data up to the month's last close; positions are held from that close. Each rebalance uses the instruments
with enough history on that date. Costs: per side (spread cost x point size + commission per contract) / (price x point
size) from `csvconfig`, times turnover.

Periods: development 2000–2019 (eras 2000–09 and 2010–19), validation 2020–22, final look 2023-01 to 2024-03 (15 months,
logged once; low power, said so in the report). Gate: Sharpe after costs > 0 in both eras and in validation. Long-only
timing strategies (F10, F14, F15, F16) are judged on their return minus the equal-weight buy-and-hold of the same
universe (otherwise equity drift passes them). Verdict: "candidate (futures only)" if the gate passes and the final
look is positive; else rejected. Deflated Sharpe against all 16. Universes (pysystemtrade names):

- COMM (28): CORN WHEAT REDWHEAT SOYBEAN SOYMEAL SOYOIL OATIES RICE CANOLA LIVECOW FEEDCOW LEANHOG MILK GOLD SILVER PLAT
  PALLAD COPPER CRUDE_W BRENT_W GAS_US HEATOIL GASOILINE GASOIL COCOA COFFEE COTTON2 SUGAR11 OJ (as available).
- FX (12, vs USD): AUD CAD CHF EUR GBP JPY MXP NZD NOK SEK ZAR BRE. Developed 9 (F8): EUR AUD CAD JPY NZD NOK SEK CHF GBP.
- EQ: SP500 NASDAQ DOW SP400 DAX CAC FTSE100 AEX IBEX SMI EUROSTX NIKKEI TOPIX HANG KOSPI SPI200 MIB.
- BOND: US2 US5 US10 US20 BUND BOBL SHATZ BTP OAT GILT JGB CAD10.

| # | Strategy | Rule |
|---|---|---|
| F1 | Time-series momentum | all four universes; sign of the 252-day return; weight sign x (10% / 60-day vol) / n; gross leverage capped at 4; monthly |
| F2 | Commodity momentum | COMM; 252-day return; long top, short bottom quintile, equal weight; monthly |
| F3 | Commodity term structure | COMM with a second contract; annualised roll yield ln(near/far) / years apart; long top, short bottom quintile; monthly |
| F4 | Commodity skewness | COMM; skewness of 252 daily returns; long lowest, short highest quintile; monthly |
| F5 | Return asymmetry | the source's 22 commodities; IE = days above mean + 2 sd minus days below mean − 2 sd over 260 days; long the 7 lowest, short the 7 highest; monthly |
| F6 | Currency momentum | FX; 252-day return; long top 3, short bottom 3; monthly |
| F7 | FX carry | FX; interest differential from the futures roll yield; long top 3, short bottom 3; monthly |
| F8 | Dollar carry | developed 9; if their average differential vs USD > 0, long the basket (short USD), else short it; monthly |
| F9 | Short-term reversal | 24 US futures (AUD CAD EUR JPY; SP500 US2 US5 US10 US20; CORN WHEAT SOYBEAN SOYMEAL SOYOIL LIVECOW LEANHOG COTTON2; GOLD SILVER COPPER CRUDE_W GAS_US HEATOIL PLAT); Wednesday-to-Wednesday weeks; weight −(r − mean r), gross 1. SIMPLIFIED: the volume / open-interest grouping is dropped |
| F10 | Paired switching | SP500 vs US20; each quarter hold the one with the higher prior-quarter return |
| F11 | Country pairs | EQ; every 20 days pick the 5 closest pairs over 120 days (sum of squared gaps of normalised prices); open at a gap > 0.5 sd, close on convergence or at the period end |
| F12 | Country betting-against-beta | EQ ex US vs SP500; 252-day beta; rank-weighted low-beta long, high-beta short, each leg scaled to beta 1; monthly |
| F13 | WTI–Brent spread | CRUDE_W vs BRENT_W; spread of the traded contracts vs its 20-day mean; short the spread above it, long below; daily |
| F14 | January barometer | SP500 DAX FTSE100 HANG IBEX NASDAQ; long in January; February–December only after a positive January |
| F15 | Asset-class trend | US stocks (SP500), foreign stocks (equal-weight non-US EQ), bonds (US10), commodities (equal-weight COMM), REITs omitted (no futures before 2014); hold classes above their 210-day mean, 1/k each; monthly |
| F16 | Asset-class momentum | the same classes; top 3 by 252-day return, 1/3 each; monthly |

## F. What gets reported

One table per source with every strategy: trades, R per trade and t-statistic 2011–19 and 2020–22, markets positive,
gate pass/fail, final look where earned, the swap-free view, and the number of configurations tried. The futures table
gives Sharpe per period. Rejections are reported plainly. Everything is recorded in the research memory.

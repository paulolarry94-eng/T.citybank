# Exness Zero costs — measured spreads, estimated commission (2026-10-31)

**Outcome:** on the Zero account the spread is effectively zero on gold, EUR, GBP, JPY, US500 and oil, so the cost
is commission + slippage. With the commission at the high end of what is published, the 11-leg book re-scores from
Sharpe 1.20 (research costs) to **1.36 with swaps** and **1.74 if the account is swap-free** (2023–25: 0.95 / 1.27). Two
numbers are still unconfirmed: the exact commission per lot and the owner's swap-free status.
*Corrected 2026-10-31: the first version read 1.00 → 1.15 / 1.51 (2023–25 0.75 / 1.06) because the daily series dropped
trades that closed at the Sunday-night open (principle P20). Tables below are the corrected re-run.*

## 1. Spreads (measured from Exness's own Zero-account ticks)
Source: Exness's public tick archive `ticks.ex2archive.com` (`{SYMBOL}_Zero_Spread`, 2020–2026). The sample was fixed
before measuring: 6 months (2021-03, 2022-06, 2023-09, 2024-01, 2024-07, 2025-04) × 8 markets. Each value is the
spread of the last tick in each minute. Weekends and the 20:30–23:00 UTC rollover block are excluded.
Script: `research/exness/exness_costs.py`; data: `research/results/exness/zero_spreads.json`.

| Market | Mean spread (6-month average) | Worst month (mean) | Minutes at zero spread |
|---|---|---|---|
| EURUSD | 0.05 pip | 0.17 pip | 94–100% |
| GBPUSD | 0.08 pip | 0.20 pip | 49–100% |
| USDJPY | 0.10 pip | 0.21 pip | 91–98% |
| XAUUSD | $0.002 | $0.009 | 94–100% |
| XAGUSD | $0.005 | $0.012 | 0–10% |
| US500 | 0.003 pt | 0.009 pt | 62–100% |
| DE30 | 0.22 pt | 1.23 pt (2025-04) | 1–100% |
| USOIL | $0.008 | $0.024 | 0–97% |

## 2. Commission (public sources disagree, so it is estimated)
- Exness (help centre and account pages, quoted by search results): Zero commission "from $0.05 per lot per side",
  varies by instrument.
- Third-party reviews (2026): "up to $3.50 per side" on FX majors; gold $5.50 per side (dated 2026-09-30).
- **Realistic profile:** $3.50 per side on FX (0.7 pip round trip), $5.50 per side on gold ($0.11/oz round trip).
- **Low-commission profile:** half of that.
- Slippage allowance: 0.2 pip FX, $0.05 gold.

| All-in round trip | Lab standard | Exness Zero realistic | Exness Zero low commission |
|---|---|---|---|
| XAUUSD | $0.45 | $0.16 | $0.11 |
| EURUSD | 1.5 pips | 0.95 pip | 0.60 pip |
| GBPUSD | 1.8 pips | 0.98 pip | 0.63 pip |
| USDJPY | 1.2 pips | 1.35 pips (the dollar commission costs more in yen) | 0.82 pip |

## 3. The 11-leg book re-scored (same trades, same weights; `research/exness/rescore_book.py`)
| Profile | Sharpe 2011–25 | Sharpe 2023–25 | Per year at 1% risk | Max drawdown at 1% risk |
|---|---|---|---|---|
| Lab costs + swaps (as before) | 1.20 | 0.79 | 9.4% | 10.3% |
| Exness Zero realistic + swaps | 1.36 | 0.95 | 10.7% | 9.7% |
| Exness Zero realistic, swap-free | **1.74** | **1.27** | 14.2% | 8.3% |
| Exness Zero low commission + swaps | 1.50 | 1.08 | 11.9% | 9.2% |
| Exness Zero low commission, swap-free | 1.88 | 1.39 | 15.5% | 7.8% |

Risk scaling, Exness Zero realistic and swap-free (`research/results/exness/book_risk_scaling.json`; backtest, before
the expected live haircut, P11):
| Risk per trade | Per year 2011–25 | Per year 2023–25 | Max drawdown |
|---|---|---|---|
| 1% | 14% | 10% | 8% |
| 2% | 30% | 21% | 16% |
| 3% | 46% | 32% | 23% |
| 4% | 64% | 44% | 30% |

Untouched check, January–October 2026 (`research/champion/`): −1.36% with swaps, +0.78% swap-free at 1% risk. The
backtest rows above are the best case; plan with the live haircut of P11.

## 4. What is still unverified, and the 2-minute check on a phone
1. **Swap-free status** (worth +0.38 Sharpe): MT5 app → Quotes → tap XAUUSD → Specification (Details) → read
   "Swap long" and "Swap short". If both are 0, the account is swap-free on gold. Repeat for EURUSD, GBPUSD, USDJPY.
2. **Commission:** open and close 0.01 lot of EURUSD and of XAUUSD on the Zero account (demo is fine) → History
   shows the commission. Multiply by 100 for a full lot.
3. Real fills (slippage) are only known from live or demo trading (Q3).

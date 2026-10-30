# TimelessCity v2.42 under the North Star tests (2026-10-30)

The four deployed legs (presets checked: market-breakout entry, fixed risk, S1/S2 long-only, S3 both),
re-scored from their research trade files. R per trade:

| Leg (risk) | Trades/yr | 2011–18 | 2019–22 | 2023–25 | with constant swap 2011–18 / 19–22 / 23–25 |
|---|---|---|---|---|---|
| S1 gold reversion (3%) | 6 | +0.16 | +0.36 | +0.14 | +0.14 / +0.34 / +0.14 |
| S1 EUR reversion (3%) | 6 | +0.26 | +0.18 | **−0.06** | +0.25 / +0.17 / −0.09 |
| S2 USDJPY trend (2%) | 22 | +0.16 | +0.45 | +0.36 | +0.08 / +0.35 / +0.30 |
| S3 gold trend (2%) | 23 | +0.13 | +0.21 | +0.26 | **+0.01** / +0.11 / +0.20 |

Portfolio at the deployed risk (3/3/2/2%, P&L at exit, no heat cap), 2011–2025:
- with a constant swap both ways: Sharpe 0.67, CAGR 15%, max DD 30%, 11/15 positive years;
- low-cost and swap-free (costs x0.5, no swap): **Sharpe 1.04, CAGR 27%, max DD 25.5%, 14/15
  positive years** (2014 +72%, 2021 +59%, 2022 +86%, 2023 +23%, 2024 +32%, 2025 +36%).
Monthly correlations between legs: −0.13 to +0.16.

Reading: the dossier's figures (Sharpe 1.14, DD 22.6%, 14/15 years) hold on a low-cost,
swap-free account and not with full swaps. Gold-trend swaps are the main risk. The constant swap is
pessimistic for long USDJPY, whose real swap was positive for much of 2017–2025. S1 EUR has been
negative in 2023–25 (18 trades; too few to judge, so it's on watch). The S1 legs trade about 6 times a
year each, so the dossier's "≥ 20 S1 trades" demo gate takes about 20 months.
Parity lists for the EA: `../results/northstar/parity/timelesscity/*.csv`.

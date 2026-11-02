# Truth Lab report — ssr_sweep_shift_v1

**Verdict: Rejected**

Hypothesis: A sweep beyond the 20-bar extreme that is reclaimed and followed by a lower-timeframe structure break traps breakout traders; fading it to the opposite liquidity pool earns more than costs, and more than a near miss.

Fingerprint `3bcb526802195dd5` · started 2026-11-02 11:06:05 UTC · markets XAUUSD, EURUSD · timeframes M15 · parameters {"window": ["5xM15", "5xH1"], "entry": ["confirm", "first"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 25% positive in development 2011–19, 0% positive in development and validation; median -0.022R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "M15", "window": "5xM15", "entry": "confirm", "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 493 trades, E +0.107R, t 2.09 · validation E -0.087R · walk-forward E +0.017R · neighbours all positive: False (median t -0.59)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E -0.005R · deflated Sharpe +0.806 (chance the edge is real after 4 tries).
5. Final look 2023–25 (logged 2026-11-02 11:06:55 UTC): 208 trades, E +0.057R, t +0.71, PF +1.13; per market XAUUSD -0.077, EURUSD +0.194.
6. Criteria: 1_E_pos_dev_val_oos ✘, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✔, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✘, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.139, 2020–22 -0.057, 2023–25 +0.084R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.00; Sharpe book +1.21 → book + this +1.08 (2017 on: +1.03 → +0.92).

## Cycle goal (owner: +2% to +7% per 10-trade cycle, 95% of 360-trade lifecycles inside the drawdown cap)
Edge quality s = mean R / spread of R per trade (after costs). Needed: +2% inside 3.6% 0.42, inside 5% 0.35; +7% inside 3.6% 0.81, inside 5% 0.68.

| Period | Trades | Win rate | Edge quality s | Cycle at 3.6% cap | at 5% | at 8% | Gap to +2% at 3.6% |
|---|---|---|---|---|---|---|---|
| 2011-19 | 493 | 47% | 0.094 | +0.15% | +0.21% | +0.34% | x4.5 |
| 2020-22 | 209 | 40% | -0.083 | -0.04% | -0.06% | -0.10% | no edge |
| 2023-25 | 208 | 44% | 0.050 | +0.08% | +0.11% | +0.18% | x8.5 |

## Cost ladder (same trades, other prices; swaps unchanged): mean R per trade (t)
| Prices | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| gross | +0.121 (+2.4) | -0.074 (-1.0) | +0.070 (+0.9) |
| roboforex_prime | +0.107 (+2.1) | -0.087 (-1.2) | +0.057 (+0.7) |
| exness_zero | +0.102 (+2.0) | -0.092 (-1.3) | +0.051 (+0.6) |
| lab_standard | +0.082 (+1.6) | -0.109 (-1.5) | +0.035 (+0.4) |

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.

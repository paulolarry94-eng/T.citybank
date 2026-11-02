# Truth Lab report — ema4_flip_v1

**Verdict: Rejected: look-ahead (signals change when future bars are removed)**

Hypothesis: Four consecutive candles crossing the 10 EMA in turn, with the 4th closing beyond the 3rd candle's open (B+), or also the 2nd beyond the 1st (A+), predict a move in the 4th candle's direction larger than costs.

Fingerprint `8ccd8bb8e6f43912` · started 2026-11-02 23:49:35 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M5, M15, M30, H1, H4 · parameters {"entry": ["mid50", "close"], "stop": ["c4", "all4"], "buffer": [0.0, 0.1, 0.25, 0.5], "target": [1, 2, 3, 4], "grade": ["A", "AB"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **FAIL**.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.

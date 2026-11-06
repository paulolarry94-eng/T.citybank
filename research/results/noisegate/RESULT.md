# Noise gate on the survivors — result (2026-11-06)

**Verdict: rejected.** The gate does not filter better than chance, and it reversed on the untouched 2026 data.
Pre-registered: `research/noisegate/PREREGISTRATION.md`; code `research/noisegate/study.py`; numbers `study.json`.
8 configurations (H1 or D1 efficiency ratio x 2 thresholds x 2 policies); 13 survivor strategies at 1R, Exness Zero costs + swaps.

## Selected configuration (best of 8): H1 gate, threshold = 67th percentile of the past year, by-type policy
| Period | All trades: edge quality s | Passed by the gate: s (trades) | Blocked: s (trades) | Random gates with the same count |
|---|---|---|---|---|
| 2011-19 | 0.068 (4,524) | 0.074 (2,210) | 0.063 (2,314) | median 0.070; the gate beats 64% of them (p 0.36) |
| 2020-22 | 0.066 (1,543) | 0.082 (754) | 0.048 (789) | - |
| 2023-25 (one look, logged 2026-11-06 06:32 UTC) | 0.043 (1,558) | 0.047 (740) | 0.040 (818) | - |
| Jan-Oct 2026, 11-leg book, untouched | 0.020 (333) | **-0.054** (157) | **+0.086** (176) | - |

Swap-free profile (separate, not instead): passed s 0.095 (2011-19), 0.098 (2020-22), 0.061 (2023-25).

## In cycle units
- Per 10-trade cycle at the 3.6% cap: +0.105% gated vs +0.10% ungated (2011-19): no real change, far from the +2% goal (s 0.42).
- The gate halves the trades (about 250 a year instead of 500), so the yearly return about halves too.

## Why it fails
- Pre-registered keep rule needed random-gate p < 0.05: got 0.36. All 8 configurations were within the random range
  (best p 0.36, textbook versions 0.48-0.69).
- Per strategy the gate is inconsistent: gold and GBPJPY Donchian trend legs did BETTER when the gate said "noise"
  (blocked +0.21R / +0.28R vs passed +0.04R / +0.05R in 2011-19), against the idea behind the gate.
- 2026 reversed: the trades the gate passed lost, the trades it blocked made money.

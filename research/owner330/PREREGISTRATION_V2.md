# Owner's 3:30 EMA retest — v2 pre-registration (2026-11-02, before any v2 result)

Code: `research/truth/strategies/owner330_ema_retest_v2.py`; tests: `research/truth/tests/test_owner330_v2.py`.

## Why a v2
After v1 was rejected the owner checked the random audit charts (`research/results/owner330/AUDIT.md`) and corrected one
chart, US500 8 Apr 2014: "Everything else is right except this, entry should have been in marked high, so far I see it just
gets wicked… can you optimize find the right stops above the candle high or low and then make it 1:1R let's see the winrate".
The data: the 16:45 WAT candle (a pullback that closed below the M5 EMA) wicked into the anchor range (low 1841.25, range top
1841.50); the 16:50 candle crossed back above the EMA (close 1843.00) without touching the range (low 1842.00), so v1 skipped
it and took a later candle. The owner's marks are the 16:50 high (1843.25, entry) and the pullback low (~1841.25).

## Changes (nothing else changes: anchor, cancel rule, displaced 50% entry, time exit, news days, markets, costs)
| | v1 | v2 |
|---|---|---|
| Reference | the cross candle must touch the range | the cross candle OR its pullback (the run of wrong-side closes just before it, after the anchor) touches the range |
| Entry | A / B3 / B6 / B12 | A only (stop order at the reference high/low; 50% limit if displaced), the owner's "marked high" |
| Stop | reference candle's far end | `candle` (reference far end) or `swing` (pullback extreme), + buffer 0 / 0.1 / 0.25 / 0.5 x ATR(14) M5 |
| Target | 2R / 3R / 4R, breakeven on/off | 1R, no breakeven |
| Grid | 48 | anchor 2 x stop 2 x buffer 4 = **16 configurations** |

## Not clean, said plainly
- v1's 2011-22 results were seen before this correction; v2 is a test of the corrected rules, not a blind first look at the idea.
- The stop grid is chosen now, before any v2 result; it is a search over 8 stop placements (deflated in the lab).
- 2026 is the owner's own period (not clean). The 2023-25 holdout has not been opened for this family; the lab looks once
  if, and only if, a v2 configuration passes the development gate (standard protocol).
- At 1:1 the win rate needed to break even is (1 + cost in R) / 2: 55% when costs are 0.10R, 58% at 0.17R. Win rate alone is
  not edge (P16); the report shows win rate next to R per trade and the cycle numbers.

## Reports
Lab REPORT (gate, neighbours, validation, walk-forward, stress, deflated Sharpe over 16, one look only if a config passes),
cycle league (all 16, 2011-19 and 2020-22), control (anchor + 2 h), and `research/owner330/v2_study.py`: win rate and the
break-even win rate per configuration and period, by market, 2026 on both feeds, US summer vs winter, and how often a
stopped trade later reached the 1R target before the time exit (the "wicked out" share).
Priors: v1 rejected (0 of 48), session patterns rejected (P1, P14, P21); 1:1 and wider stops lower the cost share but do not
create direction (P3). Expectation: rejection.

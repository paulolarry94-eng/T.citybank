# Resume after the break

Written at the freeze, 2026-11-13. Read this first when you come back; then `START_HERE.md`.

## State at the freeze
| | |
|---|---|
| Code and memory | the commit titled `Freeze 2026-11-13` on branch `claude/loving-davinci-uzjf3z` (find it with `git log --grep='^Freeze 2026-11-13'`); tests verified at commit `02bf236`, and the freeze differs from it only in documentation. The cloud session's git proxy refuses tag pushes, so there is no tag; to make one: `git tag freeze-2026-11-13 <that commit> && git push origin freeze-2026-11-13` |
| Research record | 133 ideas tested, about 337,000 configurations, 7 survivors or candidates (`docs/STRATEGY_CATALOGUE.md`) |
| Recommended system | **Timeless 10 + v2**: 13 rule-based legs on 7 markets; a candidate for forward testing, not a proven system |
| Backtest at the 3.6% envelope | +6.66% a year (2011-22), +5.38% (2023-25), +0.80% in Jan-Oct 2026 (10 months); worst drawdown 4.11%; every calendar year 2011-25 positive |
| Backtest at the 8% envelope | +15.2% / +12.1% / +1.7% in the same periods |
| The goal it was measured against | +2% every two weeks inside a 3.6% drawdown (60-120% a year): needs a two-week Sharpe of 1.17; the mix has 0.39 / 0.27 / 0.08. Not reachable with these edges (`research/goal/CYCLE_GOAL_MATH.pdf`) |
| Report | `research/results/portfolio/report/` (single-file offline copy `report_offline.html`; the live page https://claude.ai/artifact/QRh9Gy181Wsd2pn7uYgx8K is private to the owner's account) |
| Unseen data begins | **2026-10-31** (GER40: 2026-11-07). Every earlier window has been used by some study |
| Nothing is live | no demo or live record exists; no EA has been built for the new legs; MQL5 other than TimelessCity is uncompiled |

## Resume in six commands
```bash
git clone https://github.com/paulolarry94-eng/T.citybank && cd T.citybank     # the tip of the default branch is the freeze
pip install -r requirements-frozen.txt            # Python 3.11; exact versions the tests passed on
python3 -m unittest discover -s research/truth/tests    # must end with OK
python3 research/truth/memory.py --digest         # what has been tested, principles, open questions
python3 tools/lab.py list --survivors             # what works
python3 tools/lab.py priors <tags>                # before testing anything new
```

## Two jobs for the next session
**A. Test a new strategy.** `docs/TEST_A_STRATEGY.md`: write the idea down, check the priors, scaffold, pre-register by committing, run,
read the verdict. Of the 68 ideas tagged `owner-idea` in the ledger, none is recorded as a survivor (the EURUSD close-beyond reversal, also from
the owner, is tagged differently and is a Tier B candidate; the three thin pivot-sweep legs in the mix passed only an era rule
and a look, as small additions). Say why a new idea differs before spending effort.

**B. Check the frozen portfolio on the months that have arrived since.** Everything up to 2026-10-30 has been seen, so the months
after it are a free, genuine out-of-sample test of the whole mix. Rules fixed now, before any of that data exists:
1. Extend the data (`docs/DATA_AND_SOURCES.md`: Exness ticks for XAUUSD, EURUSD, GBPUSD, USDJPY; HistData for EURGBP, NAS100, GER40).
2. Re-run each leg's rules unchanged on the new months and rebuild the portfolio at the 3.6% and 8% envelopes with the frozen risk and
   weights (`research/portfolio/build.py`). **Not automated:** `build.py` stops at 2026-10-31 (the end dates are written into lines 26,
   93 and 129) and takes the book legs' 2026 trades from `research/trades/champion_2026/` (made by `research/champion/regen_2026.py`).
   First make the end date a parameter and prove it by rebuilding the published Jan-Oct 2026 figures; only then run it on new data.
3. Compare the result with the yardstick below. Do not change a rule or a weight after seeing it.

### Yardstick: what 4 consecutive months looked like for this portfolio (2011-01 to 2026-10, brokers' costs and swaps)
| Envelope | 5th percentile | 25th | Median | 75th | 95th | Worst | Windows below zero | Median since 2023 |
|---|---|---|---|---|---|---|---|---|
| 3.6% | -1.31% | +0.83% | +1.88% | +3.54% | +5.71% | -2.76% | 13% (of 187) | +1.14% |
| 8% | -2.91% | +1.81% | +4.19% | +7.97% | +13.04% | -6.08% | 13% (of 187) | +2.54% |

Windows overlap, and 2011-22 is the data the legs were chosen on, so the middle of this table is optimistic (P11 expects live results
30-50% weaker; the median since 2023 is the better centre). Reading rule: below the 5th percentile = evidence of a weaker edge
(Q3); between the 5th and 25th = weak but ordinary; above the 25th = in line. One window cannot prove anything: judge by repeated
windows, and by the leg-by-leg breakdown, not the total alone.

## What goes stale
- **Broker costs, commission and swaps** change; commission is an estimate and the swap-free status is unconfirmed (Q1). The real
  numbers come from the account: `mt5/NorthStarExport.mq5` then `tools/ingest_mt5.py`.
- **Data tools** depend on HistData's page layout and Exness's archive URLs (`tools/histdata_months.py`, `tools/exness_m1.py`).
- **Python packages**: use `requirements-frozen.txt` (the lower-bound `requirements.txt` will pick newer versions over time).
- **MT5 builds**: TimelessCity was compiled by the owner; everything else under `mt5/` has never been compiled here.
- **Claude Code sessions**: the continuity is `CLAUDE.md` (read at the start of every session), `START_HERE.md` and the research memory.

## Decisions waiting for the owner (details in `research/truth/memory/OPEN_QUESTIONS.md`)
1. **Repository visibility** (it was public at the freeze: see `docs/IP_REGISTER.md`).
2. Q1: the real Exness or RoboForex costs and whether the account is swap-free. This moves every result.
3. The envelope: 3.6% (about 5-7% a year in backtest) or 8% (about 12-15%); and payouts from a buffer (the report: $500 a fortnight needs about $200,000 at the 2011-22 pace and far more at the 2026 pace).
4. Broker and structure (Q31: RoboForex VPS, copy trading, affiliate; Q7: prop accounts; Q6: a futures account, where trend + carry actually works).
5. Whether to build EAs for the 13 legs and demo them for 3-6 months (the gated plan in `CLAUDE.md`).

# Test a new strategy: the routine

One idea, one file, one verdict. The Truth Lab does the testing and keeps the discipline for you: costs and swaps are always
charged, the rules are fixed before results, and the final period is looked at once. You bring the idea; the commands below do
the rest. Everything works from a fresh clone.

## 0. Set up (once per fresh computer or container)
```bash
git clone https://github.com/paulolarry94-eng/T.citybank && cd T.citybank   # the frozen state is the tag freeze-2026-11-13
python3 -m venv .venv && . .venv/bin/activate                                # optional; Python 3.11 was used
pip install -r requirements-frozen.txt                                       # the exact versions the tests passed on
python3 -m unittest discover -s research/truth/tests                         # must end with OK
python3 tools/lab.py list --survivors                                        # what already works
```
In a Claude Code cloud session the start-up hook installs the packages and prints the research memory for you.

## 1. Write the idea down first (answers go into the strategy file; paste them to Claude)
1. **The rule in one sentence:** entry, stop, exit. If a chart explains it better, send the chart with its date and time and say
   which candle is which. Claude replays dated examples in our data to check it reads the rule the way you do.
2. **Who is on the other side, and why do they pay?** A forced flow, a known rebalance, a risk premium. Chart shapes with no
   payer have no survivors in this project (P14, P22).
3. **Markets and timeframes, fixed now.** Data exists for 12 markets, 2011-2025 (XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP,
   WTI, US500, NAS100, GER40, UK100, JP225) and Jan-Oct 2026 for six of them. Choosing them after seeing results is hindsight.
4. **A small grid of settings.** Every setting is another lottery ticket that the deflated Sharpe charges for. The lab's default
   exit grid already multiplies your grid by 12 (targets x trails x trend filter), so a grid of 2 values on one timeframe is 24
   settings. `tools/lab.py check` prints the real count.
5. **Costs:** Exness Zero (measured spreads, `research/truth/costs.json`) or RoboForex Prime (published,
   `research/truth/costs_roboforex_prime.json`). Swaps are charged unless you say the account is swap-free (the lab also reports
   a swap-free profile separately).
6. **What result would make you drop the idea?** Write it before you see one.

## 2. Check the priors (30 seconds)
```bash
python3 tools/lab.py priors reversal,intraday     # tags: python3 tools/lab.py list shows them in each idea's family
```
It says how many earlier ideas shared the tags and how many survived. If they were all rejected, write down why this one
differs before spending effort (CLAUDE.md learning rule 1). As of the freeze: 133 ideas tested, 7 survivors or candidates.

## 3. Scaffold, fill in, check, and commit before running
```bash
python3 tools/lab.py new my_idea_v1 --family reversal,intraday --markets XAUUSD,EURUSD --timeframes H1,H4 \
        --hypothesis "Who pays, and why"
# edit research/truth/strategies/my_idea_v1.py: RULES, GRID, signals(), and the PRE-REGISTRATION block at the top
python3 tools/lab.py check my_idea_v1             # loads like the lab loads it; markets, data, costs, settings per market
git add research/truth/strategies/my_idea_v1.py && git commit -m "Pre-register my_idea_v1" && git push
```
That commit is the pre-registration: the rules are on record before any number exists.

`signals(B, p, M)` may only use bars up to and including the signal bar (the lab checks this automatically) and returns rows
`(bar, side, stop)` for a market order at the next bar's open, or `(bar, side, stop, limit_price, valid_bars)` for a limit order.
Management (target in R, trail, trend filter), `TIME_STOP`, `STOP_CAP_ATR` and a per-market `COSTS` override are optional
variables in the file (see `research/truth/strategies/TEMPLATE.py`). Exits the lab does not have (bracket prices, bailout
exits) are in `research/truth/executors.py`.

Ideas with their own order logic (partial exits, pivots, resting orders that wait): build the pattern as its own small engine, as
`research/sweep5/` and `research/body4/` do: a `PREREGISTRATION.md` committed first, a plain-Python reference simulator (the
specification), a numba twin, and a test that the two agree trade for trade (`research/truth/tests/test_sweep5.py` is the model).

## 4. Run
```bash
python3 tools/lab.py run my_idea_v1               # everything except the final look; safe to repeat
```
A small grid takes minutes; a large multi-market, multi-timeframe grid can take much longer (the 504-setting pivot-sweep grid ran
for a long while on 12 markets). Output is `research/results/truth/my_idea_v1/REPORT.md`; read it top to bottom: verdict line,
look-ahead check, development gate (2011-19), validation (2020-22), stress and deflated Sharpe, the cost ladder, the cycle goal.
The lab appends the run to the memory ledger by itself.

Editing the rules and re-running is tuning: each round is another lottery ticket. Different rules are a new file and a new NAME
(`my_idea_v2`); the scaffold refuses a name that is already used.

## 5. Reading the verdict (criteria: `research/northstar/PREREGISTRATION.md` section 5)
| Verdict | Meaning | What next |
|---|---|---|
| Rejected | did not pass the development gate, validation, stability or stress | it is a result: keep it in the ledger, do not rescue it |
| Tier B | forward-test candidate: positive after costs and swaps in development and validation, stable neighbours, survives stress, final look positive with PF 1.05 or more | write the EA from `EA_SPEC.md`, parity-check, demo (below) |
| Tier A | deployment-ready: Tier B plus final look PF 1.10, t 2, 100 or more trades, and 2 or more markets positive | as Tier B, then the small live stage |

Tiers need the logged look. A strategy that only passed development and validation is still "unlooked".

## 6. The one logged look (2023-25), only if it passed the earlier gates
```bash
python3 tools/lab.py run my_idea_v1 --look        # refuses unless the strategy file is committed
```
It uses 2023-25 once. After it, changed rules need a new NAME. The windows 2023-25 and Jan-Oct 2026 have been used by many earlier
studies; the only unseen data is whatever arrives after 2026-10-30 (see `docs/RESUME_AFTER_4_MONTHS.md`).

## 7. After every run
- Add a JOURNAL entry (`research/truth/memory/JOURNAL.md`); if the result changes what we believe, update PRINCIPLES.md with the
  evidence (keep the old text under History); add or answer an open question.
- `python3 research/truth/memory.py --render` and `python3 tools/lab.py catalogue`; commit and push.
- Report to the owner in plain language: outcome first, numbers in tables, how many configurations were tried, costs and swaps
  included, a swap-free profile beside it, never instead.

## From a Tier A/B result to an EA
`EA_SPEC.md` gives the rules. Copy `mt5/TruthEA.mq5`, implement `Signal()`, compile it in MetaEditor (MQL5 cannot be compiled in
this repo's cloud container, so everything under `mt5/` except TimelessCity is uncompiled source), run the Strategy Tester on
2023-25, then
`python3 tools/parity_check.py research/results/truth/<NAME>/parity_trades.csv <TruthEA log>.csv --market <SYMBOL> --tf-minutes <bar>`
(pass: 95% of trades matched, median R difference 0.10 or less). Then demo with `mt5/NorthStarGovernor.mq5` and the weekly report
(`research/northstar/weekly.py`).

## The rules that do not bend
1. Never claim code compiled, tests passed or an edge was verified unless that happened.
2. Fix markets, timeframes and grids before seeing results; call out any hindsight.
3. 2023-2025 is a final holdout: one logged look per strategy fingerprint.
4. Every result includes spread, commission, slippage and swaps; a low-cost swap-free profile is reported separately.
5. Report rejections plainly and say how many configurations were tried.
6. Plain language: outcome first, numbers in tables, no hype.

## A message to paste into a new Claude session
```
Read CLAUDE.md and START_HERE.md. I want to test a new strategy with the Truth Lab.
Rule: ...   Who pays: ...   Markets/timeframes: ...   Settings to try: ...   Broker/costs: ...   Drop it if: ...
Examples (dated charts): ...
Check the priors first and tell me if similar ideas were all rejected. Pre-register the strategy file (commit before running),
run without the final look, and report plainly.
```

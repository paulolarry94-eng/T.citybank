# JOURNAL — one entry per session (newest last)

Format: date · what the owner asked · what was done · what was learned (with evidence) · decisions · next.
Facts and estimates are labelled; nothing is recorded as learned without evidence.

## 2026-10-27 → 2026-10-31 · founding sessions (North Star, scanner, multi-asset, liquidity, Truth Lab)
- **Asked:** find strategies and risk systems for a 60–120% a year goal; validate rigorously (North Star
  brief); test ICT/SMC, liquidity grabs and a daily best-setup scanner; search GitHub repos (pysystemtrade,
  vectorbt, qlib, nautilus); build a container that tests any idea and builds an EA if worthy; give it memory.
- **Done:** about 300,000 configurations across 25+ studies; the North Star pre-registered protocol;
  financing and rollover modelling; a risk-manager comparison; futures trend+carry; the Kelly/Monte Carlo
  frontier; a TimelessCity re-score; the Truth Lab (`research/truth/`), TruthEA template, parity checker,
  Exness export script, Dukascopy downloader; this memory.
- **Learned:** P1–P14 in PRINCIPLES.md. Survivors: TimelessCity v2.42, the 11-leg book (Tier B), futures
  trend+carry. Everything pattern-based was rejected on these four markets.
- **Decisions:** stop pattern hunting; the next truth comes from real costs (Q1), EA parity (Q2) and demo (Q3).
- **Facts vs estimates:** the Exness sensitivity (book Sharpe 1.64) is an ESTIMATE until Q1 is answered.
- **Next:** Q1 → Q2 → Q3; breadth (Q4) when data arrives.

## 2026-10-31 (later) · prop-firm (FTMO) approach
- **Asked:** how to build a bot that survives and is consistent on an FTMO-style prop account.
- **Done:** checked current FTMO rules (public summaries, not the official page: +10% / +5% targets, 5% daily and
  10% max loss of the initial balance, 4 trading days, no time limit reported for 2026); replayed TimelessCity and the
  11-leg book from every month start 2011-2024 under those rules (`research/prop/ftmo_sim.py`).
- **Learned (study, P&L at exit; optimistic and pessimistic bounds):** the book is the better prop engine (many small
  uncorrelated trades): both phases passed in 33% (1% risk) to 40-54% (1.5% risk) of windows; +10% takes ~6-8 months;
  funded payouts ~6-8% of the account a year at 80%. At 1.5% risk, phase 1 failure rises to 4-28%. TimelessCity passes less often.
- **Decisions:** none yet. Open question Q7 added (per-phase risk, near-barrier brake, structural daily-loss guard).
- **Facts vs estimates:** FTMO rules are from third-party summaries; costs are our research costs, not FTMO's.

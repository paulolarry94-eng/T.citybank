# The funnel — how a candidate leg earns a place

Source benchmark: paperswithbacktest/awesome-systematic-trading (snapshot saved beside this
file, taken 2026-10-29). Used ONLY as a filter. No edge is imported from it.

## What the benchmark actually says (quoted, not paraphrased)
- 4,843 published strategies replicated over their own full history.
- Median replication Sharpe **0.37**; only **48%** clear a t-statistic of 1.96.
- A strategy needs roughly **(1.96 / Sharpe)^2 years** to prove itself.
- Its Sharpe ratios are **gross of trading costs**.
- Note: the repo does NOT publish a median profit factor or a median R-expectancy. The
  "PF ~1.2 / ~0.05R" figures in the brief are not from this source, so they are not used as
  gates here.

## Gates every candidate must pass (all after our corrected-fill scoring and real costs)
1. **Beats the median, net:** annualised Sharpe > 0.37 after spread, commission and slippage
   (the benchmark is gross, so ours is the harder bar).
2. **Distinguishable from zero on our record:** t-stat >= 1.96 over 2011-2025. With 15 years,
   that means Sharpe >= 1.96 / sqrt(15) ~= 0.51. Anything below cannot be told apart from luck
   on the data we have, whatever its backtest says.
3. **Out-of-sample:** parameters chosen on 2011-2018 only; 2019-2025 must stay positive and
   keep at least half of the in-sample expectancy. The last two years are never used to choose.
4. **Brief's own walls:** expectancy > +0.15R after true fills; monthly-return correlation
   < 0.20 with every leg already in the book.
5. **Perturbation and second instrument** (ledger L-006): survives a small parameter nudge,
   and is not a single shiny cell.

## Families the benchmark marks as worth looking for in OUR markets
(as places to search with our own data, not as results)
- Time-series trend / momentum on commodities -> gold trend (S3 territory)
- Currency carry ("Good Carry, Bad Carry", Sharpe 1.74 gross) -> USD/JPY long bias (S2
  territory). Testing carry properly needs swap rates, which our price files do not contain.
- Gold-silver mean reversion -> needs silver after 2018, which we do not have.

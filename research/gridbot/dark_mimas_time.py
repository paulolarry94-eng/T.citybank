"""When do Dark Mimas-style trades win? A time-of-day and market-condition study, built so it cannot fool us.

Question (owner, 2026-10-31): study the winners and their timing; give the bot active hours; what is special about
the rare big winners of a high-frequency bot, and the rare losers of a grid; is any of it timeless?
Method (fixed before running):
  - Trades from dark_mimas_sim.py (classic stop-and-reverse, and the grid set), EURUSD and GBPUSD, M5/M15/H1,
    oscillator versions R1-R3, Exness Zero realistic costs (1.0 pip) with swaps.
  - LEARN on 2011-2019 only. CHECK on 2020-2025. A pattern counts as timeless only if it repeats in the check years.
  - Features at entry: hour (UTC), weekday, volatility regime (chart ATR14 vs its 500-bar median: low/mid/high
    terciles fixed on 2011-2019), and the day's range vs its 20-day average (known only after the day: used to
    DESCRIBE what happened, never as a filter).
  - Timeless test for hours: for each configuration, the 24-hour profile of gross pips per trade in 2011-2019 vs
    2020-2025 (Spearman correlation), and "pick the best hours on 2011-19, trade only those in 2020-25".
Output: research/results/gridbot/dark_mimas_time.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E
import dark_mimas_sim as D

OUT = os.path.join(HERE, "..", "results", "gridbot")
PIP = 1e-4; COST = 1.0 * PIP; SWAP = 0.6 * PIP
LEARN_END = pd.Timestamp("2020-01-01").value // 10 ** 9


def spearman(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 5:
        return float("nan")
    ra = pd.Series(a[m]).rank().to_numpy(); rb = pd.Series(b[m]).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def day_range_ratio(ts, h, l):
    d = pd.DataFrame({"d": ts // 86400, "h": h, "l": l}).groupby("d").agg(h=("h", "max"), l=("l", "min"))
    r = d.h - d.l
    return (r / r.rolling(20, min_periods=10).mean().shift(1)).to_dict()


def main():
    out = {"classic": [], "grid": [], "notes": {}}
    for sym in ("EURUSD", "GBPUSD"):
        ts, o, h, l, c = E.load_m1(sym)
        drr = day_range_ratio(ts, h, l)
        for tf in (5, 15, 60):
            bt, bo, bh, bl, bc, ends = E.resample(ts, o, h, l, c, tf)
            tr_ = np.maximum(bh - bl, np.abs(bh - np.r_[bc[0], bc[:-1]]))
            tr_ = np.maximum(tr_, np.abs(bl - np.r_[bc[0], bc[:-1]]))
            atr = pd.Series(tr_).rolling(14).mean().to_numpy()
            ratio = atr / pd.Series(atr).rolling(500, min_periods=100).median().to_numpy()
            learn_bars = bt < LEARN_END
            q1, q2 = np.nanquantile(ratio[learn_bars], [1 / 3, 2 / 3])
            for kind in ("R1", "R2", "R3"):
                a = D.arrows(D.oscillator(kind, bh, bl))
                idx = np.flatnonzero(a != 0); idx = idx[ends[idx] < len(ts)]
                act = ends[idx].astype(np.int64); side = a[idx].astype(np.int64)
                # ---------------- classic: every trade with its entry features
                tr, _ = D.classic(ts, o, h, l, c, act, side, 500 * PIP, COST, SWAP)
                t_in = tr[:, 0].astype(np.int64); gross = tr[:, 4] / PIP; net = tr[:, 3] / PIP
                bar_of = np.searchsorted(bt, t_in, side="right") - 2          # the signal bar (closed before entry)
                vr = ratio[np.clip(bar_of, 0, len(ratio) - 1)]
                regime = np.where(vr < q1, "low", np.where(vr < q2, "mid", "high"))
                hour = (t_in % 86400) // 3600; wd = ((t_in // 86400) + 3) % 7
                learn = t_in < LEARN_END; check = ~learn
                prof = lambda m: np.array([gross[m & (hour == hh)].mean() if (m & (hour == hh)).sum() >= 30 else np.nan for hh in range(24)])
                pL, pC = prof(learn), prof(check)
                best = np.argsort(np.nan_to_num(pL, nan=-1e9))[::-1][:6]                 # top 6 hours on 2011-19
                sel_check = check & np.isin(hour, best)
                top = net >= np.quantile(net[learn], 0.99)                                 # top 1% winners (threshold on learn)
                tday = t_in // 86400
                rng_top = np.nanmean([drr.get(int(d), np.nan) for d in tday[top & learn]])
                rng_all = np.nanmean([drr.get(int(d), np.nan) for d in tday[learn]])
                pos = net[learn][net[learn] > 0]
                share_top1 = float(np.sort(pos)[::-1][: max(1, len(net[learn]) // 100)].sum() / pos.sum()) if len(pos) else None
                row = dict(sym=sym, tf=tf, osc=kind, trades_learn=int(learn.sum()), trades_check=int(check.sum()),
                           gross_pips_learn=round(float(gross[learn].mean()), 3), gross_pips_check=round(float(gross[check].mean()), 3),
                           net_pips_learn=round(float(net[learn].mean()), 3), net_pips_check=round(float(net[check].mean()), 3),
                           hour_profile_corr=round(spearman(pL, pC), 3),
                           best6_hours_learn=[int(x) for x in sorted(best)],
                           best6_gross_learn=round(float(gross[learn & np.isin(hour, best)].mean()), 3),
                           best6_gross_check=round(float(gross[sel_check].mean()), 3),
                           best6_net_check=round(float(net[sel_check].mean()), 3),
                           regime_gross_learn={r: round(float(gross[learn & (regime == r)].mean()), 3) for r in ("low", "mid", "high")},
                           regime_gross_check={r: round(float(gross[check & (regime == r)].mean()), 3) for r in ("low", "mid", "high")},
                           top1pct_share_of_profit_learn=round(share_top1, 3) if share_top1 else None,
                           top1pct_hours_learn=np.bincount(hour[top & learn], minlength=24).tolist(),
                           top1pct_high_vol_share=round(float((regime[top & learn] == "high").mean()), 3),
                           all_high_vol_share=round(float((regime[learn] == "high").mean()), 3),
                           top1pct_day_range_vs_avg=round(float(rng_top), 2), all_day_range_vs_avg=round(float(rng_all), 2),
                           top1pct_avg_hold_hours=round(float(((tr[:, 1] - tr[:, 0])[top & learn]).mean() / 3600), 1),
                           all_avg_hold_hours=round(float(((tr[:, 1] - tr[:, 0])[learn]).mean() / 3600), 1))
                out["classic"].append(row)
                # ---------------- grid: where do the stopped baskets come from?
                B, *_ = D.grid(ts, o, h, l, c, ends[:-1].astype(np.int64), act, side, 5 * PIP, 5 * PIP, 50 * PIP, 50, COST, SWAP)
                t0 = B[:, 5].astype(np.int64); stop = B[:, 4] == 0; bh_ = (t0 % 86400) // 3600
                learnB = t0 < LEARN_END
                stop_rate = lambda m: np.array([stop[m & (bh_ == hh)].mean() if (m & (bh_ == hh)).sum() >= 30 else np.nan for hh in range(24)])
                sL, sC = stop_rate(learnB), stop_rate(~learnB)
                dB = (B[:, 0].astype(np.int64)) // 86400
                rng_stop = np.nanmean([drr.get(int(d), np.nan) for d in dB[stop & learnB]])
                rng_win = np.nanmean([drr.get(int(d), np.nan) for d in dB[~stop & learnB]])
                # basket gross by opening hour; best 8 hours chosen on 2011-19, applied to 2020-25
                g = B[:, 3] / PIP
                gL = np.array([g[learnB & (bh_ == hh)].mean() if (learnB & (bh_ == hh)).sum() >= 30 else np.nan for hh in range(24)])
                gC = np.array([g[~learnB & (bh_ == hh)].mean() if (~learnB & (bh_ == hh)).sum() >= 30 else np.nan for hh in range(24)])
                best8 = np.argsort(np.nan_to_num(gL, nan=-1e9))[::-1][:8]
                out["grid"].append(dict(sym=sym, tf=tf, osc=kind, baskets_learn=int(learnB.sum()),
                                        stop_rate_learn=round(float(stop[learnB].mean()), 4), stop_rate_check=round(float(stop[~learnB].mean()), 4),
                                        stop_rate_by_open_hour_corr=round(spearman(sL, sC), 3),
                                        gross_pips_by_hour_corr=round(spearman(gL, gC), 3),
                                        best8_hours_learn=[int(x) for x in sorted(best8)],
                                        best8_gross_pips_per_basket_learn=round(float(g[learnB & np.isin(bh_, best8)].mean()), 3),
                                        best8_gross_pips_per_basket_check=round(float(g[~learnB & np.isin(bh_, best8)].mean()), 3),
                                        stop_day_range_vs_avg=round(float(rng_stop), 2), target_day_range_vs_avg=round(float(rng_win), 2)))
                print(sym, tf, kind, "classic corr", out["classic"][-1]["hour_profile_corr"], "best6 learn/check",
                      out["classic"][-1]["best6_gross_learn"], out["classic"][-1]["best6_gross_check"], "| grid corr",
                      out["grid"][-1]["gross_pips_by_hour_corr"], out["grid"][-1]["best8_gross_pips_per_basket_learn"],
                      out["grid"][-1]["best8_gross_pips_per_basket_check"], flush=True)
    json.dump(out, open(os.path.join(OUT, "dark_mimas_time.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

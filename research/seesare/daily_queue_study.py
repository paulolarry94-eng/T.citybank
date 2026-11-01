"""One high-quality trade a day from a queue of validated strategies (owner, 2026-11-01). Fixed before any result.

Owner: 10 trades = 1 cycle; every day one session; across all markets a queue picks the day's highest-quality setup by
backtest; a combination of independent strategies that survives a Monte Carlo with a median of 1-3% per cycle or more, at a
drawdown closest to 3.6% (about 5%).

Candidates: the 13 strategies that passed the lab (11-leg book, Tokyo gotobi fix, EURUSD close-beyond reversal), their own
trades, Exness Zero costs + swaps (primary; lab costs + swaps and Exness swap-free reported too). No new, untested strategy is
added (a "just sell" bot is a bet on drift, not a tested edge). Note: the book's legs were chosen in Oct 2026 on data through
2025, so every year before 2026 is in-sample for them; 2020-25 has also been seen in earlier studies. Only forward data is clean.

Quality of a leg = its 2011-2019 R per trade after costs, shrunk toward zero for small samples: sum(R) / (n + 30).
Queue (real time, no look-ahead): each day starts at the session hour H (UTC); signals are taken in time order; at the first
moment an allowed leg signals, the highest-quality leg signalling at that moment is taken; then nothing else that day.
"Best of the whole day" would need the day's later signals (look-ahead) and is not tested.
Grid (16 configurations): allowed legs = the top k by quality, k in 3, 5, 8, 13; session start H in 0 (Tokyo day),
7 (London), 13 (New York), 21 (daily close). Reported alongside, not selected: every signal of all 13 legs (no queue).
Sizing: the same risk r per trade. Monte Carlo per configuration on 2011-2019 taken trades: 5,000 lifecycles of 36 cycles,
each cycle a block of 10 consecutive taken trades drawn with replacement; r set so the 95th percentile of lifecycle drawdown
(closed trades in order) is 3.6% (primary) or 5.0%. Reported: per-cycle return median, mean, 10th / 90th percentile, share
positive; lifecycle median return; chance the lifecycle drawdown exceeds 3.6% and 5%.
Selection: the configuration with the highest Monte Carlo median per-cycle return at the 3.6% sizing on 2011-2019.
Then, same sizing, actual sequences: 2020-22, 2023-25 and the book-only Jan-Oct 2026 (no 2026 trades exist for the two Tier B
legs): per-cycle returns, lifecycle drawdowns, and the same Monte Carlo on each period. Most open positions at once is reported.
Output: research/results/seesare/daily_queue_study.json
"""
import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import universe_cap_study as U   # noqa: E402

Y20, Y23, Y26 = 1577836800, U.Y23, U.JAN26
KS, HOURS = (3, 5, 8, 13), (0, 7, 13, 21)
SHRINK, CYCLE, CYCLES, SIMS = 30, 10, 36, 5000
OUT = os.path.join(U.OUT, "daily_queue_study.json")


def legs(profile, y2026=False):
    out, max_iv = U.book_legs(profile, y2026)
    if not y2026:
        out += [U.lab_leg(n, s, profile, max_iv) for n, s in U.EXTRA]
    return out


def quality(all_legs):
    q = {}
    for g in all_legs:
        m = g["t_in"] < Y20
        q[g["name"]] = float(g["r"][m].sum() / (m.sum() + SHRINK))
    return q


def signals(all_legs, names):
    rows = [(int(t), int(o), float(r), g["name"]) for g in all_legs if g["name"] in names
            for t, o, r in zip(g["t_in"], g["t_out"], g["r"])]
    rows.sort(key=lambda x: (x[0], x[3]))
    return rows


def queue(rows, q, hour):
    """One trade per session day: first signalling moment, best quality at that moment."""
    taken, day_done, i = [], set(), 0
    while i < len(rows):
        j = i
        while j < len(rows) and rows[j][0] == rows[i][0]:
            j += 1
        day = (rows[i][0] - hour * 3600) // 86400
        if day not in day_done:
            best = max(rows[i:j], key=lambda x: q[x[3]])
            taken.append(best)
            day_done.add(day)
        i = j
    return taken


def lifecycle_dd(R):
    eq = np.cumsum(R, axis=-1)
    peak = np.maximum.accumulate(np.concatenate([np.zeros(eq.shape[:-1] + (1,)), eq], axis=-1), axis=-1)[..., 1:]
    return np.max(peak - eq, axis=-1)


def monte_carlo(R, seed=11):
    """Blocks of 10 consecutive trades; 5,000 lifecycles of 36 cycles. Returns cycle sums (R) and lifecycle drawdowns (R)."""
    R = np.asarray(R, float)
    nb = len(R) - CYCLE + 1
    if nb < 1:
        return None, None
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, nb, size=(SIMS, CYCLES))
    idx = starts[..., None] + np.arange(CYCLE)
    paths = R[idx].reshape(SIMS, CYCLES * CYCLE)
    return paths.reshape(SIMS, CYCLES, CYCLE).sum(axis=2), lifecycle_dd(paths)


def mc_report(R, r):
    cyc, dd = monte_carlo(R)
    if cyc is None:
        return None
    c = cyc.ravel() * r * 100
    life = cyc.sum(axis=1) * r * 100
    d = dd * r * 100
    return dict(cycle_median=round(float(np.median(c)), 3), cycle_mean=round(float(c.mean()), 3),
                cycle_p10=round(float(np.percentile(c, 10)), 3), cycle_p90=round(float(np.percentile(c, 90)), 3),
                cycle_positive=round(float((c > 0).mean()), 3), lifecycle_median=round(float(np.median(life)), 2),
                lifecycle_p10=round(float(np.percentile(life, 10)), 2), dd_median=round(float(np.median(d)), 2),
                dd_p95=round(float(np.percentile(d, 95)), 2), p_dd_over_3_6=round(float((d > 3.6).mean()), 3),
                p_dd_over_5=round(float((d > 5.0).mean()), 3))


def actual(R, r):
    R = np.asarray(R, float)
    n = len(R) // CYCLE
    cyc = R[:n * CYCLE].reshape(n, CYCLE).sum(axis=1) * r * 100 if n else np.zeros(0)
    lives = [R[i:i + CYCLES * CYCLE] for i in range(0, len(R), CYCLES * CYCLE)]
    return dict(trades=len(R), cycles=n, cycle_median=round(float(np.median(cyc)), 3) if n else None,
                cycle_mean=round(float(cyc.mean()), 3) if n else None,
                cycle_positive=round(float((cyc > 0).mean()), 3) if n else None,
                lifecycle_dd=[round(float(lifecycle_dd(x)) * r * 100, 2) for x in lives],
                lifecycle_ret=[round(float(x.sum()) * r * 100, 2) for x in lives],
                r_per_trade=round(float(R.mean()), 4) if len(R) else None)


def max_open(taken):
    ev = sorted([(t, 1) for t, o, _, _ in taken] + [(o, -1) for t, o, _, _ in taken], key=lambda x: (x[0], x[1]))
    cur = best = 0
    for _, d in ev:
        cur += d
        best = max(best, cur)
    return best


def period(taken, a, b):
    return [x for x in taken if a <= x[0] < b]


if __name__ == "__main__":
    res = dict(design=__doc__, quality={}, dev={}, selected=None, after={})
    data = {pf: legs(pf) for pf in U.PROFILES}
    q = quality(data["zero_swaps"])
    order = sorted(q, key=q.get, reverse=True)
    res["quality"] = {k: round(q[k], 4) for k in order}
    print("leg quality (2011-19 R per trade, shrunk):", res["quality"])
    configs = [(k, h) for k in KS for h in HOURS]
    for k, h in configs:
        tk = queue(signals(data["zero_swaps"], set(order[:k])), q, h)
        dev = [x[2] for x in period(tk, 0, Y20)]
        _, dd = monte_carlo(dev)
        dd95 = float(np.percentile(dd, 95))
        r36, r50 = 0.036 / dd95, 0.05 / dd95
        res["dev"][f"top{k}/h{h}"] = dict(trades=len(dev), per_year=round(len(dev) / 9, 1), r_per_trade=round(float(np.mean(dev)), 4),
                                          risk_3_6=round(r36 * 100, 3), risk_5=round(r50 * 100, 3),
                                          mc_3_6=mc_report(dev, r36), mc_5=mc_report(dev, r50), max_open=max_open(period(tk, 0, Y20)))
        m = res["dev"][f"top{k}/h{h}"]["mc_3_6"]
        print(f"top{k:2d} h{h:2d}: {len(dev)} trades ({len(dev)/9:.0f}/yr) {np.mean(dev):+.4f}R  risk {r36*100:.3f}% -> cycle median "
              f"{m['cycle_median']:+.3f}% mean {m['cycle_mean']:+.3f}% pos {m['cycle_positive']:.2f} life median {m['lifecycle_median']:+.2f}%")
    # baseline: every signal of all 13 legs (no queue)
    allsig = [x[2] for x in signals(data["zero_swaps"], set(order)) if x[0] < Y20]
    _, dd = monte_carlo(allsig)
    rb = 0.036 / float(np.percentile(dd, 95))
    res["baseline_all_signals"] = dict(trades=len(allsig), risk_3_6=round(rb * 100, 3), mc_3_6=mc_report(allsig, rb))
    print("baseline all signals:", res["baseline_all_signals"])
    key = max(res["dev"], key=lambda c: res["dev"][c]["mc_3_6"]["cycle_median"])
    k, h = int(key.split("/")[0][3:]), int(key.split("/")[1][1:])
    res["selected"] = key
    sel = res["dev"][key]
    for pf in U.PROFILES:
        tk = queue(signals(data[pf], set(order[:k])), q, h)
        for name, a, b in (("2020-22", Y20, Y23), ("2023-25", Y23, Y26)):
            R = [x[2] for x in period(tk, a, b)]
            res["after"][f"{name}/{pf}"] = dict(actual_3_6=actual(R, sel["risk_3_6"] / 100), actual_5=actual(R, sel["risk_5"] / 100),
                                                mc_3_6=mc_report(R, sel["risk_3_6"] / 100))
        book26 = legs(pf, y2026=True)
        tk26 = queue(signals(book26, set(order[:k]) & {g["name"] for g in book26}), q, h)
        R26 = [x[2] for x in tk26]
        res["after"][f"2026_book_only/{pf}"] = dict(actual_3_6=actual(R26, sel["risk_3_6"] / 100), actual_5=actual(R26, sel["risk_5"] / 100))
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1, default=float)
    print("selected", key, sel)
    for k2, v in res["after"].items():
        print(k2, v)

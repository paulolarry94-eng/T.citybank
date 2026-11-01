"""Strategy universe under a 3.6% drawdown cap per lifecycle (owner, 2026-11-01): fixed before any result.

Question: combining every surviving strategy and choosing the sizing rule (including a reconfigured ladder), how much return
can be had while each 360-trade lifecycle stays within about 3.6% drawdown?

Universes (survivors only; rejected strategies have no edge after costs; TimelessCity is left out because its three legs are
book legs already):
  U1  the 11-leg book, frozen weights (research/results/book_v3.json, inverse 2011-19 monthly-vol weights)
  U2  U1 + Tokyo gotobi fix + EURUSD close-beyond reversal (both Tier B; trades = the lab's parity_trades.csv), each weighted
      by the book's own rule: (1 / 2011-19 monthly R vol) / the book's largest (1 / vol), capped at 1
Costs: primary profile Exness Zero realistic costs + swaps (the champion tearsheet's formula); also reported: lab costs + swaps
(a higher-cost proxy; RoboForex ProCent costs are unmeasured) and Exness Zero swap-free (separately, never instead).
Lifecycle: 360 consecutive signals of the universe (taken or skipped), by entry time. Sizes, drawdown and the cap are % of the
lifecycle's starting equity; equity compounds from one lifecycle to the next. Drawdown = closed-trade equity below the
lifecycle's high. "Guard" = a trade is taken only if drawdown + open risk + its risk <= 3.6%.
Sizing rules (each risk is x the leg weight):
  FIXED(r)    risk r per trade, no guard                               r in 0.25, 0.375, 0.5, 0.625, 0.75, 1.0 %
  GUARD(r)    risk r per trade + guard                                 same grid
  DDLADDER(m) reconfigured ladder: 16 levels keyed to drawdown, not to wins and losses: level k = floor(drawdown / 0.225%),
              risk = m x (3.6% - (k+1) x 0.225%) (m x the room left at the bottom of the band), + guard
                                                                       m in 0.05, 0.1, 0.15, 0.2, 0.3, 0.5
  SEESARE(s)  SEESARE outcome ladder (default proportions, +1 per win, -2/-3/-4 per loss, ascension rule: a trade's sign is
              its outcome; skipped trades move the ladder as SHADOW), L0 risk s, reset to L0 each lifecycle, + guard
                                                                       s in 0.5, 0.75, 1.0, 1.5, 2.0, 3.0 %
Configurations: 4 rules x 6 settings x 2 universes = 48.
Selection (development only, entries 2011-2022, run on its own): per rule and universe, the setting with the highest annual
return among those whose worst development lifecycle drawdown <= 3.6%. Then ONE look: 2023-2025 (entries 2023-2025, run on
its own from a fresh lifecycle) for the 8 selected configurations only; and the book's untouched Jan-Oct 2026 trades
(research/trades/champion_2026/, book legs only: no 2026 trades exist for the two Tier B legs) for the U1 selections.
Output: research/results/seesare/universe_cap_study.json
"""
import os
import sys
import json
import heapq
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, ".."))
ROOTDIR = os.path.abspath(os.path.join(R, ".."))
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "exness"), os.path.join(ROOTDIR, "tools")):
    sys.path.insert(0, p)
import core                      # noqa: E402
import ns_portfolio as PF        # noqa: E402
import rescore_book as RB        # noqa: E402
from rescore import COST, SWAP   # noqa: E402
import seesare_verify as S       # noqa: E402

CAP, LIFE = 0.036, 360
BAND = CAP / 16
Y23, JAN26 = 1672531200, 1767225600
GRIDS = {"FIXED": [0.0025, 0.00375, 0.005, 0.00625, 0.0075, 0.01], "GUARD": [0.0025, 0.00375, 0.005, 0.00625, 0.0075, 0.01],
         "DDLADDER": [0.05, 0.1, 0.15, 0.2, 0.3, 0.5], "SEESARE": [0.005, 0.0075, 0.01, 0.015, 0.02, 0.03]}
PROFILES = ("zero_swaps", "lab_swaps", "zero_swapfree")
EXTRA = (("tokyo_fix_gotobi_v1", "USDJPY"), ("eurusd_close_beyond_reversal_v1", "EURUSD"))
OUT = os.path.join(R, "results", "seesare")


def book_legs(profile, y2026=False):
    zc = RB.zero_costs(1.0)
    _, names = PF.build("BOOK")
    w = {n["leg"]: n["weight"] for n in names}
    legs = []
    for name, sym, x in PF.legs("BOOK"):
        if y2026:
            x = np.load(os.path.join(R, "trades", "champion_2026", f"{name}.npy"))
            x = x[x["t_in"] >= JAN26]
        nights = np.array([core.nights_held(int(a), int(b)) for a, b in zip(x["t_in"], x["t_out"])])
        cost = COST[sym] if profile == "lab_swaps" else zc[sym]
        swap = 0.0 if profile == "zero_swapfree" else SWAP[sym]
        r = x["r"] + COST[sym] / x["dist"] - cost / x["dist"] - nights * swap / x["dist"]
        legs.append(dict(name=name, w=w[name], t_in=x["t_in"].astype(np.int64), t_out=x["t_out"].astype(np.int64), r=r))
    return legs, max(1.0 / n["vol"] for n in names if np.isfinite(n["vol"]) and n["vol"] > 0)


def lab_leg(name, sym, profile, max_iv):
    T = pd.read_csv(os.path.join(R, "results", "truth", name, "parity_trades.csv"))
    t_in = pd.to_datetime(T.t_in).to_numpy().astype("datetime64[s]").astype(np.int64)
    t_out = pd.to_datetime(T.t_out).to_numpy().astype("datetime64[s]").astype(np.int64)
    r_lab = T.r.to_numpy()
    zc = RB.zero_costs(1.0)[sym]
    r = r_lab if profile == "lab_swaps" else r_lab + T.cost_r.to_numpy() - zc / T.dist.to_numpy()
    if profile == "zero_swapfree":
        r = r + T.fin_r.to_numpy()
    ym = pd.to_datetime(T.t_in).dt.to_period("M")
    keep = pd.to_datetime(T.t_in).dt.year <= 2019
    vol = float(pd.Series(r_lab[keep.to_numpy()]).groupby(ym[keep].to_numpy()).sum().std())
    return dict(name=name, w=min(1.0, (1.0 / vol) / max_iv), t_in=t_in, t_out=t_out, r=r)


def universe(which, profile, y2026=False):
    legs, max_iv = book_legs(profile, y2026)
    if which == "U2" and not y2026:
        legs += [lab_leg(n, s, profile, max_iv) for n, s in EXTRA]
    t_in = np.concatenate([g["t_in"] for g in legs]); t_out = np.concatenate([g["t_out"] for g in legs])
    r = np.concatenate([g["r"] for g in legs]); w = np.concatenate([np.full(len(g["r"]), g["w"]) for g in legs])
    leg = np.concatenate([np.full(len(g["r"]), i) for i, g in enumerate(legs)])
    o = np.lexsort((leg, t_in))
    return dict(t_in=t_in[o], t_out=np.maximum(t_out[o], t_in[o]), r=r[o], w=w[o]), {g["name"]: round(g["w"], 4) for g in legs}


def simulate(T, rule, p):
    t_in, t_out, r, w = T["t_in"], T["t_out"], T["r"], T["w"]
    eq, open_risk, heap, lives, path = 1.0, 0.0, [], [], [(int(t_in[0]), 1.0)]
    st = {}
    level, negrun = 0, 0

    def close(upto):
        nonlocal eq, open_risk, level, negrun
        while heap and heap[0][0] <= upto:
            to, i, risk = heapq.heappop(heap)
            if risk > 0:
                eq += risk * r[i]
                open_risk -= risk
                st["hwm"] = max(st["hwm"], eq)
                st["maxdd"] = max(st["maxdd"], (st["hwm"] - eq) / st["base"])
                path.append((int(to), eq))
            res = 1 if r[i] > 0 else (-1 if r[i] < 0 else 0)
            level, negrun = S.ladder_next(level, negrun, res)

    def finish(t_end):
        st.update(end_eq=eq, t_end=int(t_end), ret=eq / st["base"] - 1)
        lives.append(dict(st))

    for i in range(len(r)):
        close(t_in[i])
        if i % LIFE == 0:
            if st:
                finish(t_in[i])
            st.clear()
            st.update(t0=int(t_in[i]), base=eq, hwm=eq, maxdd=0.0, planned=0.0, taken=0, skipped=0, signals=0)
            level, negrun = 0, 0
        st["signals"] += 1
        dd = (st["hwm"] - eq) / st["base"]
        if rule == "FIXED":
            f, guard = p * w[i], False
        elif rule == "GUARD":
            f, guard = p * w[i], True
        elif rule == "DDLADDER":
            k = min(15, int(dd / BAND + 1e-12))
            f, guard = p * w[i] * max(0.0, CAP - (k + 1) * BAND), True
        else:
            f, guard = p * w[i] * S.LADDER[level] / S.LADDER[0], True
        take = f > 0 and (not guard or dd + open_risk / st["base"] + f <= CAP + 1e-12)
        risk = f * st["base"] if take else 0.0
        if take:
            open_risk += risk
            st["taken"] += 1
            st["planned"] = max(st["planned"], dd + open_risk / st["base"])
        else:
            st["skipped"] += 1
        heapq.heappush(heap, (int(t_out[i]), i, risk))
    close(np.iinfo(np.int64).max)
    finish(int(t_out.max()))
    return lives, path


def score(lives, path):
    years = (path[-1][0] - path[0][0]) / (365.25 * 86400)
    eqs = np.array([e for _, e in path])
    full_dd = float(np.max(1 - eqs / np.maximum.accumulate(eqs)))
    rets = [x["ret"] for x in lives]
    return dict(lifecycles=len(lives), years=round(years, 2), annual_pct=round((eqs[-1] ** (1 / years) - 1) * 100, 2),
                total_pct=round((eqs[-1] - 1) * 100, 2),
                worst_life_dd_pct=round(max(x["maxdd"] for x in lives) * 100, 2),
                median_life_dd_pct=round(float(np.median([x["maxdd"] for x in lives])) * 100, 2),
                worst_planned_pct=round(max(x["planned"] for x in lives) * 100, 2),
                life_ret_pct=dict(mean=round(float(np.mean(rets)) * 100, 2), median=round(float(np.median(rets)) * 100, 2),
                                  worst=round(min(rets) * 100, 2), best=round(max(rets) * 100, 2),
                                  positive=f"{sum(x > 0 for x in rets)}/{len(rets)}"),
                full_path_dd_pct=round(full_dd * 100, 2),
                taken_share=round(sum(x["taken"] for x in lives) / sum(x["signals"] for x in lives), 3),
                lives_with_skips=sum(x["skipped"] > 0 for x in lives))


def window(T, a, b):
    m = (T["t_in"] >= a) & (T["t_in"] < b)
    return {k: v[m] for k, v in T.items()}


if __name__ == "__main__":
    out = dict(design=__doc__, weights={}, dev={}, selected={}, holdout={}, y2026={}, signals_per_year={})
    data = {}
    for u in ("U1", "U2"):
        for pf in PROFILES:
            data[(u, pf)], wts = universe(u, pf)
        out["weights"][u] = wts
        T = data[(u, "zero_swaps")]
        out["signals_per_year"][u] = round(len(T["r"]) / 15.0, 1)
    for u in ("U1", "U2"):
        dev = window(data[(u, "zero_swaps")], 0, Y23)
        for rule, grid in GRIDS.items():
            res = []
            for p in grid:
                sc = score(*simulate(dev, rule, p))
                res.append(dict(setting=p, **sc))
                out["dev"][f"{u}/{rule}/{p}"] = sc
            ok = [x for x in res if x["worst_life_dd_pct"] <= CAP * 100 + 1e-9]
            pick = max(ok, key=lambda x: x["annual_pct"]) if ok else min(res, key=lambda x: x["setting"])
            out["selected"][f"{u}/{rule}"] = dict(setting=pick["setting"], within_cap=bool(ok))
            print(f"{u} {rule:9s} dev: " + "  ".join(f"{x['setting']}: {x['annual_pct']:+.2f}%/yr dd {x['worst_life_dd_pct']:.2f}"
                                                     for x in res) + f"  -> pick {pick['setting']}" + ("" if ok else " (none within cap)"))
    # one look: 2023-2025, then the book's untouched 2026
    for key, sel in out["selected"].items():
        u, rule = key.split("/")
        for pf in PROFILES:
            T = window(data[(u, pf)], Y23, JAN26)
            out["holdout"][f"{key}/{pf}"] = score(*simulate(T, rule, sel["setting"]))
        if u == "U1":
            for pf in PROFILES:
                T26, _ = universe("U1", pf, y2026=True)
                out["y2026"][f"{key}/{pf}"] = score(*simulate(T26, rule, sel["setting"]))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "universe_cap_study.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    for key in out["selected"]:
        d = out["dev"][f"{key}/{out['selected'][key]['setting']}"]; h = out["holdout"][f"{key}/zero_swaps"]
        line = (f"{key:12s} setting {out['selected'][key]['setting']}: dev {d['annual_pct']:+.2f}%/yr worst life dd {d['worst_life_dd_pct']:.2f}% | "
                f"2023-25 {h['annual_pct']:+.2f}%/yr worst life dd {h['worst_life_dd_pct']:.2f}% full dd {h['full_path_dd_pct']:.2f}%")
        if f"{key}/zero_swaps" in out["y2026"]:
            y = out["y2026"][f"{key}/zero_swaps"]
            line += f" | 2026 {y['total_pct']:+.2f}% dd {y['worst_life_dd_pct']:.2f}%"
        print(line)

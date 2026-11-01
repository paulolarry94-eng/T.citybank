"""Strategy universe scored per LIFECYCLE (owner, 2026-11-01): fixed before any result of this study.

Owner: "backtest 360s as 1 unit, number of completed lifes, optimise for lifecycle alpha" (not per year).
Same universes, costs, sizing rules and settings as research/seesare/universe_cap_study.py (48 configurations); changed:
  - a lifecycle = 360 REAL (taken) trades, then reset (SEESARE's lock), instead of 360 signals;
  - a lifecycle that can no longer take any trade (no open trade of its own, and even the smallest trade its rule allows does
    not fit under drawdown + risk <= 3.6%) is STOPPED: it counts as one unit and a new lifecycle starts at the next signal
    (SEESARE: "continuing means a new lifecycle id");
  - each trade's profit belongs to the lifecycle that opened it; a lifecycle's return = its trades' net / its starting equity;
    its drawdown = the high-to-low of its own closed trades; equity compounds across lifecycles;
  - objective: mean return per finished lifecycle (completed + stopped) on 2011-2022, among settings whose worst lifecycle
    drawdown <= 3.6%; also reported: completed vs stopped, median, worst, best, share positive, days per lifecycle.
Evaluation: settings chosen on 2011-2022 (run alone); then 2023-2025 (run alone) and the book's Jan-Oct 2026 for the chosen
settings. CAUTION written before running: 2023-25 and 2026 were already seen for this universe in universe_cap_study (v1), so
they are not a clean holdout for this study; forward data is the only clean test left.
Output: research/results/seesare/universe_lifecycle_study.json
"""
import os
import sys
import json
import heapq
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import universe_cap_study as U   # noqa: E402  (data, costs, weights, grids)
import seesare_verify as S       # noqa: E402

CAP, LIFE, BAND = U.CAP, U.LIFE, U.BAND


def rule_risk(rule, p, w, dd, level):
    if rule in ("FIXED", "GUARD"):
        return p * w
    if rule == "DDLADDER":
        k = min(15, int(dd / BAND + 1e-12))
        return p * w * max(0.0, CAP - (k + 1) * BAND)
    return p * w * S.LADDER[level] / S.LADDER[0]


def simulate(T, rule, p):
    t_in, t_out, r, w = T["t_in"], T["t_out"], T["r"], T["w"]
    w_min = float(w.min())
    guard = rule != "FIXED"
    eq, open_risk, heap, lives = 1.0, 0.0, [], []
    state = dict(level=0, negrun=0)

    def new_life(t):
        lives.append(dict(t0=int(t), t_last=int(t), base=eq, net=0.0, hwm=0.0, maxdd=0.0, taken=0, signals=0, open=0,
                          status="partial"))
        state["level"], state["negrun"] = 0, 0

    def close(upto):
        nonlocal eq, open_risk
        while heap and heap[0][0] <= upto:
            to, i, risk, li = heapq.heappop(heap)
            if risk > 0:
                L = lives[li]
                pnl = risk * r[i]
                eq += pnl
                open_risk -= risk
                L["net"] += pnl
                L["hwm"] = max(L["hwm"], L["net"])
                L["maxdd"] = max(L["maxdd"], (L["hwm"] - L["net"]) / L["base"])
                L["open"] -= 1
                L["t_last"] = max(L["t_last"], int(to))
            if li == len(lives) - 1:
                res = 1 if r[i] > 0 else (-1 if r[i] < 0 else 0)
                state["level"], state["negrun"] = S.ladder_next(state["level"], state["negrun"], res)

    for i in range(len(r)):
        close(t_in[i])
        if not lives:
            new_life(t_in[i])
        L = lives[-1]
        dd = (L["hwm"] - L["net"]) / L["base"]
        if guard and L["open"] == 0 and L["taken"] > 0:
            f_min = rule_risk(rule, p, w_min, dd, 15 if rule == "SEESARE" else state["level"])
            if f_min <= 0 or dd + f_min > CAP + 1e-12:
                L["status"] = "stopped"
                new_life(t_in[i])
                L, dd = lives[-1], 0.0
        L["signals"] += 1
        f = rule_risk(rule, p, w[i], dd, state["level"])
        take = f > 0 and (not guard or dd + open_risk / L["base"] + f <= CAP + 1e-12)
        risk = f * L["base"] if take else 0.0
        if take:
            open_risk += risk
            L["taken"] += 1
            L["open"] += 1
        heapq.heappush(heap, (int(t_out[i]), i, risk, len(lives) - 1))
        if L["taken"] == LIFE:
            L["status"] = "completed"
            new_life(t_in[i] + 1)
            if i + 1 < len(r):
                lives[-1]["t0"] = int(t_in[i + 1])
    close(np.iinfo(np.int64).max)
    if lives and lives[-1]["taken"] == 0 and lives[-1]["status"] == "partial":
        lives.pop()
    return lives


def score(lives):
    fin = [x for x in lives if x["status"] in ("completed", "stopped")]
    ret = [x["net"] / x["base"] * 100 for x in fin]
    days = [(x["t_last"] - x["t0"]) / 86400 for x in fin]
    part = [x for x in lives if x["status"] == "partial"]
    out = dict(finished=len(fin), completed=sum(x["status"] == "completed" for x in fin),
               stopped=sum(x["status"] == "stopped" for x in fin),
               worst_dd_pct=round(max(x["maxdd"] for x in lives) * 100, 2) if lives else None,
               partial=[dict(taken=x["taken"], ret_pct=round(x["net"] / x["base"] * 100, 2), dd_pct=round(x["maxdd"] * 100, 2))
                        for x in part])
    if fin:
        out.update(mean_ret_pct=round(float(np.mean(ret)), 2), median_ret_pct=round(float(np.median(ret)), 2),
                   worst_ret_pct=round(min(ret), 2), best_ret_pct=round(max(ret), 2),
                   positive=f"{sum(v > 0 for v in ret)}/{len(ret)}", mean_days=round(float(np.mean(days)), 0),
                   each=[dict(status=x["status"], taken=x["taken"], ret_pct=round(x["net"] / x["base"] * 100, 2),
                              dd_pct=round(x["maxdd"] * 100, 2), days=round((x["t_last"] - x["t0"]) / 86400)) for x in fin])
    return out


if __name__ == "__main__":
    out = dict(design=__doc__, dev={}, selected={}, after={}, y2026={})
    data = {(u, pf): U.universe(u, pf)[0] for u in ("U1", "U2") for pf in U.PROFILES}
    for u in ("U1", "U2"):
        dev = U.window(data[(u, "zero_swaps")], 0, U.Y23)
        for rule, grid in U.GRIDS.items():
            res = []
            for p in grid:
                sc = score(simulate(dev, rule, p))
                out["dev"][f"{u}/{rule}/{p}"] = sc
                res.append((p, sc))
            ok = [(p, s) for p, s in res if s["worst_dd_pct"] <= CAP * 100 + 1e-9 and s["finished"] > 0]
            p, s = max(ok, key=lambda x: x[1]["mean_ret_pct"]) if ok else min(res, key=lambda x: x[0])
            out["selected"][f"{u}/{rule}"] = dict(setting=p, within_cap=bool(ok))
            print(f"{u} {rule:9s} dev: " + "  ".join(
                f"{q}: {v.get('mean_ret_pct')}%/life {v['completed']}c+{v['stopped']}s dd {v['worst_dd_pct']}" for q, v in res)
                + f"  -> {p}" + ("" if ok else " (none within cap)"))
    for key, sel in out["selected"].items():
        u, rule = key.split("/")
        for pf in U.PROFILES:
            out["after"][f"{key}/{pf}"] = score(simulate(U.window(data[(u, pf)], U.Y23, U.JAN26), rule, sel["setting"]))
            if u == "U1":
                out["y2026"][f"{key}/{pf}"] = score(simulate(U.universe("U1", pf, y2026=True)[0], rule, sel["setting"]))
    os.makedirs(U.OUT, exist_ok=True)
    with open(os.path.join(U.OUT, "universe_lifecycle_study.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    for key, sel in out["selected"].items():
        d = out["dev"][f"{key}/{sel['setting']}"]; a = out["after"][f"{key}/zero_swaps"]
        print(f"{key:12s} {sel['setting']}: 2011-22 {d['completed']}c+{d['stopped']}s mean {d['mean_ret_pct']}% median {d['median_ret_pct']}% "
              f"worst {d['worst_ret_pct']}% dd {d['worst_dd_pct']}% days {d['mean_days']} | 2023-25 {a['completed']}c+{a['stopped']}s "
              f"mean {a.get('mean_ret_pct')}% dd {a['worst_dd_pct']}% partial {a['partial']}")

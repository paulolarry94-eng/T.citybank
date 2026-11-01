"""NOTE (2026-11-01): written for ledger format 1 (the retired win/loss ladder); it ran at commit 6624594. The current
tools/seesare_verify.py writes format 2 (drawdown-keyed ladder), so this script no longer runs against it; its results file
stands as recorded.
SEESARE cycle-block study, Phase 4: the owner's time-exit ascension rule (fixed 2026-11-01 before any result).

Question: with the new hardcoded rule (a time exit with a net gain is POSITIVE and climbs one level, a net loss NEGATIVE,
exactly 0 MANUAL: time_policy=GAIN_POSITIVE_LOSS_NEGATIVE), does the only lab-verified flow (Tokyo gotobi fix) trade real money
on a RoboForex ProCent cent account, how many cycles close, what does a cycle earn, and does the lifecycle drawdown stay within
3.6%? Same trades, costs and sizing as research/seesare/cycle_study.py (USDJPY M1 2011-2025, buy 23:00 UTC at bid + spread,
stop 0.3%, exit 00:55 UTC; ProCent 1.9 pips, stress 2.85; cent lot 1,000 units, minimum 0.01, step 0.01, volume rounded down;
REAL only if >= 0.01 lot and the envelope guard allows it).

Variants (all reported, none selected; 3 x 2 spreads = 6 runs):
  D  SEESARE default ladder, declared ratio 1.04 (the measured payoff)
  E  owner-scaled ladder, declared ratio 1.04. Ladder = default x 2.43665 (rounded down to 4 decimals), from the owner's spec
     "-0.35% average expiration" for a 4:1 flow: L0 plan at ratio 4.0 = 0.35% of $1,000 ($3.50). Derived from the spec, not
     from data: 0.3508,0.2314,0.1510,0.0999,0.0657,0.0438,0.0292,0.0194,0.0121,0.0080,0.0053,0.0034,0.0021,0.0014,0.0009,0.0007
  F  owner-scaled ladder, declared ratio 4.0 (the owner's figure; NOT measured for this flow, which pays about 1:1). No target is
     placed, so the trades are the same; only the size changes. Shows what sizing "as if 4:1" does.
Reported per variant: real trades, lifecycles (a new one starts when one locks at 360 real events), cycles closed, cycle net %
(mean, median, best, worst, share positive), sums over 5 and 10 consecutive cycles, lifecycle max drawdown %, envelope
violations, entries refused by the guard and by the minimum lot, real P&L in USD and in R (P&L / risk), all by era.
Output: research/results/seesare/cycle_study_ascension.json
"""
import os
import sys
import json
import math
import datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cycle_study as C          # noqa: E402  (also puts tools/ and the strategy folder on the path)
import seesare_verify as S      # noqa: E402

POLICY = "GAIN_POSITIVE_LOSS_NEGATIVE"
OWNER_SCALE = 0.35 / (1.05 * 0.95 * 0.144)
OWNER_LADDER = [S.floor_dp(x * OWNER_SCALE, 4) for x in S.LADDER]
VARIANTS = (("D_default_ladder_ratio_1.04", None, 1.04), ("E_owner_ladder_ratio_1.04", OWNER_LADDER, 1.04),
            ("F_owner_ladder_declared_4.0", OWNER_LADDER, 4.0))


def run(tr, ladder, ratio):
    L, lives, rows = None, [], []
    for x in tr:
        if L is None or L.locked:
            L = S.Ledger(f"ASC{len(lives) + 1}", ladder=ladder, time_policy=POLICY)
            L.genesis_line(x["t_in"] - 86400)
            lives.append(L)
        stop = x["entry"] * (1 - C.STOP_PCT)
        by, px, t_close = "TIME", x["exit"], x["t_out"]
        for lo, t in zip(x["lo"], x["ts"]):
            if lo <= stop:
                by, px, t_close = "STOP", min(stop, lo), int(t)
                break
        loss_per_lot = C.UNITS_PER_LOT * (x["entry"] - stop) / stop
        plan = L.plan_at(ratio, "forex")
        vol = math.floor(plan / loss_per_lot / C.STEP + 1e-9) * C.STEP
        lot_ok = vol >= C.VMIN - 1e-12
        risk = vol * loss_per_lot
        guard_ok = L.allows_real_risk(risk) if lot_ok else None
        real = lot_ok and guard_ok
        volume = vol if real else plan / loss_per_lot
        pnl = volume * C.UNITS_PER_LOT * (px - x["entry"]) / px
        lvl, life = L.level, L.life
        L.record(dict(mode="REAL" if real else "SHADOW", module="TOKYO_FIX", domain="forex", symbol="USDJPY", side=1,
                      digits=3, open=x["t_in"], close=max(t_close, x["t_in"]), by=by, ratio=ratio,
                      risk=risk if real else 0.0, vol=volume, entry=x["entry"], lower=stop,
                      upper=x["entry"] + ratio * (x["entry"] - stop), exit=px, delta=pnl,
                      deals=str(len(rows) + 1) if real else "-"))
        rows.append(dict(year=dt.datetime.fromtimestamp(x["t_in"], dt.timezone.utc).year, real=bool(real), level=lvl,
                         life=life, by=by, pnl=float(S.num(pnl, 4)), risk=float(S.num(risk, 4)) if real else 0.0,
                         refused="" if real else ("min_lot" if not lot_ok else "guard")))
    return rows, lives


def windows(vals, n):
    s = [sum(vals[i:i + n]) for i in range(len(vals) - n + 1)]
    return dict(count=len(s), min=round(min(s), 5), median=round(float(np.median(s)), 5), max=round(max(s), 5)) if s else None


def summary(rows, lives):
    res = {}
    for name, a, b in C.ERAS:
        r = [x for x in rows if a <= x["year"] <= b]
        real = [x for x in r if x["real"]]
        res[name] = dict(events=len(r), real=len(real), real_share=round(len(real) / max(len(r), 1), 3),
                         mean_level=round(float(np.mean([x["level"] for x in r])), 2),
                         real_pnl_usd=round(sum(x["pnl"] for x in real), 2),
                         real_R=round(sum(x["pnl"] for x in real) / sum(x["risk"] for x in real), 3) if real else None,
                         refused_min_lot=sum(x["refused"] == "min_lot" for x in r),
                         refused_guard=sum(x["refused"] == "guard" for x in r))
    cy = C.cycles(lives)
    pct = [c["net_pct"] for c in cy]
    real = [x for x in rows if x["real"]]
    lv = [x["level"] for x in rows]
    res["all"] = dict(events=len(rows), real=len(real), lifecycles=len(lives), locked=sum(L.locked for L in lives),
                      cycles_closed=len(cy),
                      cycle_net_pct_mean=round(float(np.mean(pct)), 5) if pct else None,
                      cycle_net_pct_median=round(float(np.median(pct)), 5) if pct else None,
                      cycle_net_pct_best=round(max(pct), 5) if pct else None,
                      cycle_net_pct_worst=round(min(pct), 5) if pct else None,
                      positive_cycles_share=round(sum(p > 0 for p in pct) / len(pct), 3) if pct else None,
                      five_cycle_sums_pct=windows(pct, 5), ten_cycle_sums_pct=windows(pct, 10),
                      real_pnl_usd=round(sum(x["pnl"] for x in real), 2),
                      # risk-weighted mean R per real trade (fixed after the first run: it was divided by the count twice)
                      real_R_per_trade=round(sum(x["pnl"] for x in real) / sum(x["risk"] for x in real), 4) if real else None,
                      max_life_dd_usd=round(max(L.l_dd for L in lives), 4),
                      max_life_dd_pct=round(max(L.l_dd for L in lives) / 10.0, 4),
                      violations=sum(len(L.violations) for L in lives),
                      refused_min_lot=sum(x["refused"] == "min_lot" for x in rows),
                      refused_guard=sum(x["refused"] == "guard" for x in rows),
                      share_events_at_L0=round(float(np.mean([v == 0 for v in lv])), 3),
                      share_events_at_L15=round(float(np.mean([v == 15 for v in lv])), 3),
                      mean_level=round(float(np.mean(lv)), 2))
    res["lifecycles"] = [dict(life=L.life, real=L.n, shadow=L.shadow, locked=L.locked, net_usd=round(L.l_net, 2),
                              net_pct=round(L.l_net / 10.0, 3), max_dd_pct=round(L.l_dd / 10.0, 3),
                              room_left_usd=round(L.envelope_room(), 2)) for L in lives]
    return res, cy


if __name__ == "__main__":
    print("owner ladder:", ",".join(S.num(x, 4) for x in OWNER_LADDER))
    out = dict(policy=POLICY, owner_ladder=[S.num(x, 4) for x in OWNER_LADDER], runs={})
    for spread, tag in ((1.9, "procent_1.9pip"), (2.85, "stress_2.85pip")):
        tr = C.trades(spread)
        for key, ladder, ratio in VARIANTS:
            rows, lives = run(tr, ladder, ratio)
            res, cy = summary(rows, lives)
            out["runs"][f"{tag}/{key}"] = dict(summary=res, cycles=cy)
            a = res["all"]
            print(f"{tag:15s} {key:28s} real {a['real']:4d}/{a['events']} lives {a['lifecycles']} locked {a['locked']} "
                  f"cycles {a['cycles_closed']:3d} mean {a['cycle_net_pct_mean']}% worst {a['cycle_net_pct_worst']}% "
                  f"P&L {a['real_pnl_usd']:+.2f} USD R/trade {a['real_R_per_trade']} maxDD {a['max_life_dd_pct']:.3f}% "
                  f"viol {a['violations']} guard {a['refused_guard']} minlot {a['refused_min_lot']} L0 {a['share_events_at_L0']}")
            for e, _, _ in C.ERAS:
                s = res[e]
                print(f"     {e}: real {s['real']:3d}/{s['events']:3d} level {s['mean_level']:5.2f} P&L {s['real_pnl_usd']:+7.2f} "
                      f"R {s['real_R']} guard {s['refused_guard']} minlot {s['refused_min_lot']}")
            for lf in res["lifecycles"]:
                print("     ", lf)
    os.makedirs(C.OUT, exist_ok=True)
    with open(os.path.join(C.OUT, "cycle_study_ascension.json"), "w") as f:
        json.dump(out, f, indent=1)

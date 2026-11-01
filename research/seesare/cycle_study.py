"""SEESARE cycle-block study (owner's Phase 3 directive, Part II), fixed 2026-11-01 before any result.

Question: run the only lab-verified flow (Tokyo gotobi fix, research/truth/strategies/tokyo_fix_gotobi_v1.py, pre2300) through
the real SEESARE ledger rules (tools/seesare_verify.py Ledger: 16-level ladder, 2.0 exponent, losing time exits NEGATIVE,
pre-trade envelope guard, 10-event cycles, 360-event lifecycles) on a RoboForex ProCent (cent) account, 2011-2025, and report
cycle by cycle what the money and the ladder do.

Trades: every gotobi fix in the research calendar; buy at 23:00 UTC at the bid open + spread, stop 0.3% of price below the
entry, exit at the 00:55 UTC bid open (or at the stop / target, scanned minute by minute on bid highs and lows).
Costs: ProCent average USDJPY spread 1.9 pips, no commission (RoboForex specifications page, 2026-11-01); stress 2.85 pips.
Sizing (cent account): 1 cent lot = 1,000 units, minimum 0.01, step 0.01; volume = floor(plan / loss per lot / 0.01) x 0.01;
REAL if >= 0.01 lot and the envelope guard allows it, else SHADOW at the unrounded shadow lot.
Variants (all reported, none selected):
  A  as coded: no target (time exit), declared ratio 1.04 (measured payoff), losing time exits NEGATIVE (hardcoded rule)
  B  target placed at the declared ratio 1.04 (so target hits can climb the ladder)
  C  earlier mandate for comparison: time exits MANUAL, no target
Each variant replays all trades in order as consecutive lifecycles (a new lifecycle starts when one locks at 360 REAL events).
Output: research/results/seesare/cycle_study.json
"""
import os, sys, json, math, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "research", "truth"), os.path.join(ROOT, "research", "northstar"),
          os.path.join(ROOT, "research", "truth", "strategies")):
    sys.path.insert(0, p)
import seesare_verify as S
import tokyo_fix_gotobi_v1 as T

STOP_PCT, PIP = 0.003, 0.01
UNITS_PER_LOT, STEP, VMIN = 1000.0, 0.01, 0.01
OUT = os.path.join(ROOT, "research", "results", "seesare"); os.makedirs(OUT, exist_ok=True)


def load():
    ts, o, h, l = [], [], [], []
    for y in range(2011, 2026):
        d = np.load(os.path.join(ROOT, "data", f"USDJPY_M1_bid_{y}.npz"))
        ts.append(d["ts"] // 1000); o.append(d["o"]); h.append(d["h"]); l.append(d["l"])
    ts = np.concatenate(ts); idx = np.argsort(ts, kind="stable")
    ts, o, h, l = ts[idx], np.concatenate(o)[idx], np.concatenate(h)[idx], np.concatenate(l)[idx]
    keep = np.r_[True, ts[1:] != ts[:-1]]
    return ts[keep], o[keep], h[keep], l[keep]


def trades(spread_pips):
    ts, o, h, l = load()
    out = []
    for fix in sorted(T.gotobi_days(2011, 2025)):
        t_in = int(dt.datetime(fix.year, fix.month, fix.day, tzinfo=dt.timezone.utc).timestamp()) - 3600
        t_out = t_in + 115 * 60
        i0, i1 = np.searchsorted(ts, t_in), np.searchsorted(ts, t_out)
        if i0 >= len(ts) or i1 >= len(ts) or ts[i0] != t_in or ts[i1] - t_out > 300 or i1 - i0 < 90:
            continue
        entry = o[i0] + spread_pips * PIP                      # buy at the ask
        out.append(dict(t_in=t_in, t_out=int(ts[i1]), entry=entry, hi=h[i0:i1], lo=l[i0:i1], ts=ts[i0:i1], exit=o[i1]))
    return out


def run(tr, place_target, policy, ratio=1.04):
    L, lives = None, []
    rows = []
    for x in tr:
        if L is None or L.locked:
            L = S.Ledger(f"STUDY{len(lives) + 1}", time_policy=policy)
            L.genesis_line(x["t_in"] - 86400); lives.append(L)
        stop = x["entry"] * (1 - STOP_PCT)
        tgt = x["entry"] + ratio * (x["entry"] - stop) if place_target else None
        by, px, t_close = "TIME", x["exit"], x["t_out"]
        for hi, lo, t in zip(x["hi"], x["lo"], x["ts"]):
            if lo <= stop:
                by, px, t_close = "STOP", min(stop, lo), int(t); break
            if tgt is not None and hi >= tgt:
                by, px, t_close = "TARGET", tgt, int(t); break
        loss_per_lot = UNITS_PER_LOT * (x["entry"] - stop) / stop          # USD per cent lot at the stop
        plan = L.plan_at(ratio, "forex")
        ok, vol, virtual = (lambda v: (v >= VMIN - 1e-12, v, plan / loss_per_lot))(
            math.floor(plan / loss_per_lot / STEP + 1e-9) * STEP)
        risk = vol * loss_per_lot
        real = ok and L.allows_real_risk(risk)
        volume = vol if real else virtual
        pnl = volume * UNITS_PER_LOT * (px - x["entry"]) / px
        lvl = L.level
        L.record(dict(mode="REAL" if real else "SHADOW", module="TOKYO_FIX", domain="forex", symbol="USDJPY", side=1,
                      digits=3, open=x["t_in"], close=max(t_close, x["t_in"]), by=by, ratio=ratio, risk=risk if real else 0.0,
                      vol=volume, entry=x["entry"], lower=stop, upper=x["entry"] + ratio * (x["entry"] - stop), exit=px,
                      delta=pnl, deals=str(len(rows) + 1) if real else "-"))
        rows.append(dict(year=dt.datetime.utcfromtimestamp(x["t_in"]).year, real=real, level=lvl, by=by,
                         pnl=float(S.num(pnl, 4)), pips=(px - x["entry"]) / PIP))
    return rows, lives


def cycles(lives):
    out = []
    for L in lives:
        for a in L.anchors:
            kv = S.parse(S.split_line(a)[0])[1]
            out.append(dict(life=L.life, cycle=int(kv["cycle"]), net=float(kv["net"]), net_pct=float(kv["net_pct"]),
                            dd=float(kv["max_dd"]), lvl_start=int(kv["lvl_start"]), lvl_end=int(kv["lvl_end"])))
    return out


ERAS = [("2011-15", 2011, 2015), ("2016-19", 2016, 2019), ("2020-22", 2020, 2022), ("2023-25", 2023, 2025)]


def summary(rows, lives):
    res = {}
    for name, a, b in ERAS:
        r = [x for x in rows if a <= x["year"] <= b]
        real = [x for x in r if x["real"]]
        res[name] = dict(events=len(r), real=len(real), real_share=round(len(real) / max(len(r), 1), 3),
                         mean_level=round(float(np.mean([x["level"] for x in r])), 2),
                         real_pnl_usd=round(sum(x["pnl"] for x in real), 2),
                         gross_pips_per_event=round(float(np.mean([x["pips"] for x in r])), 2),
                         stops=sum(x["by"] == "STOP" for x in r), targets=sum(x["by"] == "TARGET" for x in r))
    cy = cycles(lives)
    lv = [x["level"] for x in rows]
    first_l15 = next((i for i, v in enumerate(lv) if v == 15), None)
    res["all"] = dict(events=len(rows), real=sum(x["real"] for x in rows), lifecycles=len(lives),
                      cycles_closed=len(cy), real_pnl_usd=round(sum(x["pnl"] for x in rows if x["real"]), 2),
                      max_life_dd_usd=round(max(L.l_dd for L in lives), 4),
                      max_life_dd_pct=round(max(L.l_dd for L in lives) / 10.0, 4),
                      cycle_net_pct_mean=round(float(np.mean([c["net_pct"] for c in cy])), 5) if cy else None,
                      cycle_net_pct_best=round(max(c["net_pct"] for c in cy), 5) if cy else None,
                      cycle_net_pct_worst=round(min(c["net_pct"] for c in cy), 5) if cy else None,
                      positive_cycles=sum(c["net"] > 0 for c in cy), first_event_at_L15=first_l15,
                      share_events_at_L15=round(float(np.mean([v == 15 for v in lv])), 3),
                      violations=sum(len(L.violations) for L in lives))
    return res, cy


if __name__ == "__main__":
    out = {}
    for spread, tag in ((1.9, "procent_1.9pip"), (2.85, "stress_2.85pip")):
        tr = trades(spread)
        for key, tgt, pol in (("A_as_coded", False, "LOSS_NEGATIVE"), ("B_target_1.04", True, "LOSS_NEGATIVE"),
                              ("C_time_exits_manual", False, "MANUAL")):
            rows, lives = run(tr, tgt, pol)
            res, cy = summary(rows, lives)
            out[f"{tag}/{key}"] = dict(summary=res, cycles=cy)
            a = res["all"]
            print(f"{tag:15s} {key:20s} events {a['events']} real {a['real']} cycles {a['cycles_closed']} "
                  f"real P&L {a['real_pnl_usd']:+.2f} USD  maxDD {a['max_life_dd_pct']:.3f}%  cycle mean {a['cycle_net_pct_mean']}% "
                  f"L15 share {a['share_events_at_L15']} (first at event {a['first_event_at_L15']})")
            for e, _, _ in ERAS:
                s = res[e]
                print(f"     {e}: events {s['events']:3d} real {s['real']:3d} mean level {s['mean_level']:5.2f} "
                      f"real P&L {s['real_pnl_usd']:+7.2f} USD gross {s['gross_pips_per_event']:+.2f} pips/event "
                      f"stops {s['stops']} targets {s['targets']}")
    json.dump(out, open(os.path.join(OUT, "cycle_study.json"), "w"), indent=1)

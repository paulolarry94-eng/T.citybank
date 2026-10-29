"""ORB 50 — E4 (trade management) and E5 (market-quality filters), each tested on fixed bases.

Bases
  canonical  Model A as most traders run it: market entry on the breakout close, no buffer,
             stop at the far side of the OR, fixed 2R target; every market/session/ORB length
  picks      the development-period robust pick of each model (A=E1, B=E2, C=E3) per
             market/session
E4 varies only management: break-even {off, .75, 1, 1.25R} x chandelier trail {off, 2, 2.5, 3,
3.5 ATR} x partial {off, 50% at 1R} x ATR period {10, 14, 20}. With a trail the fixed target is
removed (the trail is the exit); with partial + trail the remainder trails.
E5 varies one filter at a time: OR-width percentile band (trailing 100 sessions), volatility
regime (daily ATR / its 250-day median), impulsive breakout bar, failed attempts before the
breakout, relative activity of the breakout bar (only USDJPY has activity data in every year).
"""
import sys, itertools
import numpy as np
import pandas as pd
import core, experiments as X, selection as SEL

CANON = dict(entry=0, buf=0.0, stop=0, tgt=2.0)
PCOLS = list(__import__("strategy").PARAMS)


def cfg_of(row):
    c = {k: row[k] for k in PCOLS if k in row.index}
    for k in ("side", "entry", "pb_k", "stop", "max_fails", "bias", "inval", "delay", "pb_hi", "max_tr", "atr_p", "min_fails"):
        c[k] = int(c[k])
    for k in c:
        if not isinstance(c[k], int):
            c[k] = float(c[k])
    b = dict(period=int(row["bias_ema"]), kind=row["bias_kind"], z=float(row["bias_z"])) if int(row["bias"]) else None
    return c, b


def bases():
    out = []
    for sym, sess, orb in X.combos():
        out.append(("canon", sym, sess, orb, dict(CANON), None, ""))
    for model, st in (("A", "E1"), ("B", "E2"), ("C", "E3")):
        df = SEL.load([st])
        sel = SEL.pick(df)
        for _, r in sel.iterrows():
            if not np.isfinite(r["score"]):
                continue
            c, b = cfg_of(r)
            out.append((f"pick{model}", r["sym"], r["session"], int(r["orb"]), c, b, ""))
    return out


def e4_tasks(B):
    T = []
    for tag, sym, sess, orb, c, b, f in B:
        for be, tr, part, ap in itertools.product((0.0, 0.75, 1.0, 1.25), (0.0, 2.0, 2.5, 3.0, 3.5), (0, 1), (10, 14, 20)):
            cc = dict(c, be=be, trail=tr, atr_p=ap, part_f=0.5 if part else 0.0, part_r=1.0)
            if tr > 0:
                cc["tgt"] = 0.0
            if part and tr == 0 and cc["tgt"] == 0:
                continue                                  # partial without anything after it = session exit
            T.append((sym, sess, orb, cc, f, b))
    return T


FILTERS = ["", "w:10~90", "w:20~80", "w:0~80", "w:20~100", "w:30~70", "v:0.8~1.25", "v:1.0~99", "v:0~1.0"]


def e5_tasks(B):
    T = []
    for tag, sym, sess, orb, c, b, f in B:
        for flt in FILTERS:
            T.append((sym, sess, orb, dict(c), flt, b))
        for imp in (1.5, 2.0, 3.0):
            T.append((sym, sess, orb, dict(c, imp=imp), "", b))
        for mf in (0, 1, 2):
            T.append((sym, sess, orb, dict(c, max_fails=mf), "", b))
        if sym == "USDJPY":
            for v in (1.0, 1.5, 2.0):
                T.append((sym, sess, orb, dict(c, vol=v), "", b))
    return T


if __name__ == "__main__":
    B = bases()
    pd.DataFrame([dict(tag=t, sym=s, session=se, orb=o, cfg=str(c), bias=str(b)) for t, s, se, o, c, b, f in B]).to_csv(
        core.HERE + "/../results/orb_experiments/bases.csv", index=False)
    for st in sys.argv[1:]:
        X.run_stage(st, extra=e4_tasks(B) if st == "E4" else e5_tasks(B))

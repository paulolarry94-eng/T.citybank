"""ORB 50 — Part 8 ablation. Fixed, un-tuned component settings so the test measures what each
component does, not how well it can be fitted.

Base (1) ORB alone: market entry on the M5 close beyond the OR, no buffer, stop at the far side,
2R target. Components (each added alone to the base, and as a cumulative ladder):
  ema    H4 EMA50, whole candle body on the trade side (last closed H4 bar)
  vol    skip sessions whose OR width is outside the 20th-80th percentile of the previous 100
  retest buy limit at ORH + 0.25 ATR after the breakout close (instead of market entry)
  pb2    two-candle pullback after a 0.5 ATR displacement, buy stop above the last pullback bar
  chand  chandelier exit 3 x ATR14 (highest high of 14 bars), no fixed target
  be     stop to break-even at +1R
  full   ema + vol + pb2 + chand + be, with the stop moved below the pullback low (step 8)
"""
import numpy as np
import pandas as pd
import core, experiments as X

BASE = dict(entry=0, buf=0.0, stop=0, tgt=2.0)
EMA = dict(period=50, kind="body", z=0.25)
COMP = {
    "ema": (dict(bias=1), "", EMA),
    "vol": ({}, "w:20~80", None),
    "retest": (dict(entry=2, tol=0.25), "", None),
    "pb2": (dict(entry=3, pb_k=2, disp=0.5), "", None),
    "chand": (dict(trail=3.0, tgt=0.0), "", None),
    "be": (dict(be=1.0), "", None),
}
LADDER = [("1 ORB alone", []), ("2 +EMA50", ["ema"]), ("3 +vol filter", ["ema", "vol"]),
          ("4 +retest", ["ema", "vol", "retest"]), ("5 +2-candle pullback (instead of retest)", ["ema", "vol", "pb2"]),
          ("6 +chandelier", ["ema", "vol", "pb2", "chand"]), ("7 +break-even", ["ema", "vol", "pb2", "chand", "be"]),
          ("8 full spec (stop below the pullback low)", ["ema", "vol", "pb2", "chand", "be", "swing"])]


def build(parts):
    cfg, filt, bias = dict(BASE), "", None
    for p in parts:
        if p == "swing":
            continue
        c, f, b = COMP[p]
        cfg.update(c)
        filt = f or filt
        bias = b or bias
    if "swing" in parts:
        cfg["stop"] = 1                    # full strategy as written: stop beyond the pullback swing
    return cfg, filt, bias


def variants():
    V = [("single", "ORB alone", [])] + [("single", f"ORB + {p}", [p]) for p in COMP]
    V += [("ladder", name, parts) for name, parts in LADDER[1:]]
    return V


def tasks():
    T, labels = [], []
    for sym, sess, orb in X.combos():
        for kind, name, parts in variants():
            cfg, filt, bias = build(parts)
            T.append((sym, sess, orb, cfg, filt, bias)); labels.append((kind, name))
    return T, labels


if __name__ == "__main__":
    T, labels = tasks()
    rows = X.run_stage("AB", extra=T)
    lab = pd.DataFrame(labels, columns=["kind", "variant"])
    lab["id"] = [f"AB-{i}" for i in range(len(T))]
    lab.to_csv(core.HERE + "/../results/orb_experiments/AB_labels.csv", index=False)

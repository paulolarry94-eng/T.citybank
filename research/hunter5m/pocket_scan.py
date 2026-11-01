"""Hunter, step 3: does the owner's Leg 34 setup work in ANY pocket: market x timeframe x session? (owner, 2026-11-01:
"check all timeframes M5, M10, M15, M30, M45, H1, for all the markets, then Asian, London, New York ... we are not giving up").
Method fixed BEFORE running:

Setups: Leg 34 detector (truth/strategies/leg34_gold_v1.py): swing 3, perfect or slow engulfing, entry 30% into the eaten
  Leg 4 candle, stop 0.032% of price beyond Leg 4, order valid 96 candles, time stop 288 candles (the M5 rules in candles),
  both sides. Each setup simulated ALONE with the lab's fills and exit engine; exits t3 (3R target) and ladder (breakeven
  at +1R, lock each completed R). Costs: Exness Zero realistic for XAUUSD, EURUSD, GBPUSD, USDJPY; lab estimates for XAGUSD,
  WTI, US500, NAS100, GER40, UK100, JP225 (the owner's US500 swap of -142.4 points long / 0 short is close to the lab's 0.8).
Grid: 11 markets x 6 timeframes (M5, M10, M15, M30, M45, H1) x 3 sessions by decision hour (Asia 22-07, London 07-12,
  New York 12-21 UTC) x 2 exits = 396 cells.
Selection uses 2011-2022 only:
  discovery 2011-19: mean R after costs > 0, at least 100 trades, t >= 2.0;
  confirmation 2020-22: mean R after costs > 0, at least 30 trades.
  Only cells passing both are reported on 2023-25 and on January-September 2026 (gold, EUR, GBP, JPY); October 2026
  separately. About 2.3% of cells (~9) would pass the discovery bar by luck alone.
Persistence check over all cells: share positive in 2020-22 among cells positive vs negative in 2011-19 (after costs, and
  before costs). Equal shares = what looked good was luck.
Hint test, declared now from the past grids: sop_4leg_v1 found EUR/GBP M30 in the 16-20 UTC window positive in 2011-19 and
  2020-22 (n 17-82). Reported for M30, 16-20 UTC, on the other 9 markets, every period, both exits.
Output: research/results/hunter5m/pocket_scan.json; research/results/hunter5m/pocket_trades.csv.gz (one row per trade)
"""
import os, sys, json, time
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import winner_anatomy as W                                   # market loader, costs, fill spreads (same as step 1)
import core
import protocol as P
import executors as X
S = W.S

core.MINUTES.update({"M10": 10, "M45": 45})
TFS = ["M5", "M10", "M15", "M30", "M45", "H1"]
SESSIONS = {"asia": (22, 7), "london": (7, 12), "newyork": (12, 21)}
EXITS = {"t3": (3.0, False, False, False), "ladder": (0.0, True, True, False)}
SETUP = {"k": 3, "engulf": "any"}; BUFFER = "scaled"
JAN26, OCT26 = W.JAN26, W.OCT26
OUT = W.OUT


def in_session(hour, s):
    a, b = SESSIONS[s]
    return (a <= hour < b) if a < b else (hour >= a or hour < b)


def simulate(M, B, setups, tfmin):
    rows = [(s["d"], s["side"], S.stop_of(s, BUFFER), s["entry"], S.VALID) for s in setups]
    C = P.to_candidates(B, rows, M, S.STOP_CAP_ATR, W.fill_spread(M.sym))
    ts = M.ts.astype(np.int64); gaps = M.gaps.astype(np.int64); out = []
    for i in range(len(C["k0"])):
        k0 = C["k0"][i:i + 1].astype(np.int64); sd = C["side"][i:i + 1].astype(np.int64)
        en = C["entry"][i:i + 1].astype(np.float64); st = C["stop"][i:i + 1].astype(np.float64)
        rec = dict(dec_t=int(C["dec_t"][i]), side=int(sd[0]))
        for name, (tgt, be, lad, ux) in EXITS.items():
            res = X._managed(M.o, M.h, M.l, M.G.c, ts, gaps, k0, sd, en, st, tgt, be, lad, W.EMPTY, W.EMPTY, ux, M.cost,
                             M.swap, 2 ** 62, 0, S.TIME_STOP * tfmin, core.BLOCK[0], core.BLOCK[1])
            if not len(res):
                rec = None; break
            rec[name] = float(res[0, 3]); rec[name + "_gross"] = float(res[0, 3] + res[0, 5])
        if rec is not None:
            out.append(rec)
    return out


def collect(sym, y2026=False):
    M = W.market(sym, y2026); recs = []
    for tf in TFS:
        B = M.bars(tf); S._CACHE.clear()
        st = S._setups(B, SETUP)
        for r in simulate(M, B, st, core.MINUTES[tf]):
            r.update(sym=sym, tf=tf); recs.append(r)
        print(f"{sym}{' 2026' if y2026 else ''} {tf}: {len(st)} setups", flush=True)
    return pd.DataFrame(recs)


def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 2:
        return dict(n=int(len(r)))
    sd = r.std(ddof=1)
    return dict(n=int(len(r)), E=round(float(r.mean()), 3), t=round(float(r.mean() / (sd / np.sqrt(len(r)))), 2) if sd > 0 else None)


def main():
    t0 = time.time()
    D = pd.concat([collect(m) for m in W.MARKETS], ignore_index=True)
    D26 = pd.concat([collect(m, True) for m in W.HOLD_MARKETS], ignore_index=True)
    D26 = D26[D26.dec_t >= JAN26]
    for Df in (D, D26):
        dt = pd.to_datetime(Df.dec_t, unit="s"); Df["year"] = dt.dt.year; Df["hour"] = dt.dt.hour
        Df["session"] = [next(s for s in SESSIONS if in_session(h, s)) if not (21 <= h < 22) else "none" for h in Df.hour]
    D.to_csv(os.path.join(OUT, "pocket_trades.csv.gz"), index=False)
    D26.to_csv(os.path.join(OUT, "pocket_trades_2026.csv.gz"), index=False)
    cells = []
    for (sym, tf, ses), g in D[D.session != "none"].groupby(["sym", "tf", "session"]):
        g26 = D26[(D26.sym == sym) & (D26.tf == tf) & (D26.session == ses)]
        for ex in EXITS:
            row = dict(sym=sym, tf=tf, session=ses, exit=ex)
            for per, gg in (("dev", g[g.year <= 2019]), ("val", g[g.year.between(2020, 2022)]), ("oos", g[g.year >= 2023])):
                s_ = stats(gg[ex]); sg = stats(gg[ex + "_gross"])
                row.update({f"{per}_n": s_.get("n"), f"{per}_E": s_.get("E"), f"{per}_t": s_.get("t"), f"{per}_Egross": sg.get("E")})
            s26 = stats(g26[g26.dec_t < OCT26][ex]); s10 = stats(g26[g26.dec_t >= OCT26][ex])
            row.update(y26_n=s26.get("n"), y26_E=s26.get("E"), oct_n=s10.get("n"), oct_E=s10.get("E"))
            cells.append(row)
    C = pd.DataFrame(cells)
    disc = (C.dev_n >= 100) & (C.dev_E > 0) & (C.dev_t >= 2.0)
    conf = disc & (C.val_n >= 30) & (C.val_E > 0)
    res = {"cells": int(len(C)), "discovery_pass": int(disc.sum()), "confirmed": int(conf.sum()),
           "survivors": C[conf][["sym", "tf", "session", "exit", "dev_n", "dev_E", "dev_t", "val_n", "val_E", "oos_n", "oos_E",
                                 "oos_t", "y26_n", "y26_E", "oct_n", "oct_E"]].to_dict("records"),
           "discovery_passes": C[disc][["sym", "tf", "session", "exit", "dev_n", "dev_E", "dev_t", "val_n", "val_E"]].to_dict("records")}
    for lab, col_d, col_v in (("after costs", "dev_E", "val_E"), ("before costs", "dev_Egross", "val_Egross")):
        pos = C[col_d] > 0
        res[f"persistence {lab}"] = dict(cells_positive_2011_19=int(pos.sum()),
                                         P_val_pos_if_dev_pos=round(float((C[pos][col_v] > 0).mean()), 3) if pos.any() else None,
                                         P_val_pos_if_dev_neg=round(float((C[~pos][col_v] > 0).mean()), 3) if (~pos).any() else None)
    res["median_E_after_costs_by_tf"] = C.groupby("tf")[["dev_E", "val_E", "oos_E"]].median().round(3).to_dict("index")
    res["median_E_before_costs_by_tf"] = C.groupby("tf")[["dev_Egross", "val_Egross", "oos_Egross"]].median().round(3).to_dict("index")
    res["median_E_after_costs_by_session"] = C.groupby("session")[["dev_E", "val_E", "oos_E"]].median().round(3).to_dict("index")
    res["share_cells_positive_after_costs"] = {p: round(float((C[f"{p}_E"] > 0).mean()), 3) for p in ("dev", "val", "oos")}
    res["share_cells_positive_before_costs"] = {p: round(float((C[f"{p}_Egross"] > 0).mean()), 3) for p in ("dev", "val", "oos")}
    H = D[(D.tf == "M30") & D.hour.between(16, 19) & ~D.sym.isin(["EURUSD", "GBPUSD"])]
    H26 = D26[(D26.tf == "M30") & D26.hour.between(16, 19) & ~D26.sym.isin(["EURUSD", "GBPUSD"])]
    res["hint_M30_16_20_other_markets"] = {ex: {"2011-19": stats(H[H.year <= 2019][ex]), "2020-22": stats(H[H.year.between(2020, 2022)][ex]),
                                               "2023-25": stats(H[H.year >= 2023][ex]), "Jan-Sep 2026": stats(H26[H26.dec_t < OCT26][ex]),
                                               "by market 2011-25": {m: stats(g[ex]) for m, g in H.groupby("sym")}} for ex in EXITS}
    C.to_csv(os.path.join(OUT, "pocket_cells.csv"), index=False)
    res["runtime_s"] = round(time.time() - t0)
    json.dump(res, open(os.path.join(OUT, "pocket_scan.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("survivors", "discovery_passes", "hint_M30_16_20_other_markets")}, indent=1, default=str))
    print("survivors:", json.dumps(res["survivors"], default=str))


if __name__ == "__main__":
    main()

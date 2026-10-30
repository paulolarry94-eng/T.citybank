"""Experiment 10 baselines: the original strategies re-scored with the North Star financing charge.

Uses the stored trade files (entry/exit time, stop distance, R after costs) of the four locked
strategies, the ORB finalists and the 11-leg book. Financing per trade = rollover nights x SWAP / stop
distance (core.nights_held; Wednesday x3). Crosses (not in the pre-registration) use their quote
currency's rate: GBPJPY as USDJPY, EURGBP as EURUSD.

    python3 rescore.py -> results/northstar/baselines_financed.json
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core
sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E
from grid import year_index
from confirm import stats
ROOT = os.path.join(HERE, "..")
SWAP = dict(core.SWAP, GBPJPY=core.SWAP["USDJPY"], EURGBP=core.SWAP["EURUSD"])
COST = dict(E.COST, GBPJPY=0.030, EURGBP=0.00015)          # crosses: the costs used in research/hunt/crosses.py
PFX = {"EUR": "EURUSD", "XAU": "XAUUSD", "JPY": "USDJPY", "GBP": "GBPUSD", "GBPJPY": "GBPJPY", "EURGBP": "EURGBP"}
PERIODS = {"dev": (2011, 2019), "val": (2020, 2022), "oos": (2023, 2025)}


def finance(x, sym):
    n = np.array([core.nights_held(int(a), int(b)) for a, b in zip(x["t_in"], x["t_out"])])
    return n * SWAP[sym] / x["dist"]


def score(parts):
    """parts: list of (trades, sym). Returns per-period stats before and after financing."""
    t = np.concatenate([p["t_in"] for p, _ in parts]); r = np.concatenate([p["r"] for p, _ in parts])
    f = np.concatenate([finance(p, s) for p, s in parts]); y = year_index(t)
    c = np.concatenate([COST[s] / p["dist"] for p, s in parts])
    out = {}
    for k, (a, b) in PERIODS.items():
        m = (y >= a) & (y <= b)
        out[k] = dict(before=stats(r[m]), after=stats(r[m] - f[m]), fin_R=float(f[m].mean()) if m.any() else None)
    dv = y <= 2022
    out["stress_dev_val"] = stats(r[dv] - f[dv] - 0.5 * c[dv] - f[dv])          # costs x1.5, financing x2 (no latency re-run)
    o = out["oos"]["after"]
    out["criteria"] = {"1_E_pos_dev_val_oos": all((out[p]["after"].get("E") or -1) > 0 for p in PERIODS),
                       "2_oos_PF110_t2_n100": (o.get("PF") or 0) >= 1.10 and (o.get("t") or 0) >= 2.0 and o["n"] >= 100,
                       "5_stress_dev_val_pos_no_latency": (out["stress_dev_val"].get("E") or -1) > 0}
    return out


def main():
    res = {}
    for strat in ("TC", "FB", "VC", "VE"):
        parts = [(np.load(os.path.join(ROOT, "trades", "four", f"{strat}_{s}.npy")), s) for s in core.SWAP]
        res[f"four_{strat}"] = score(parts)
    res["four_all"] = score([(np.load(os.path.join(ROOT, "trades", "four", f"{st}_{s}.npy")), s)
                             for st in ("TC", "FB", "VC", "VE") for s in core.SWAP])
    for c in json.load(open(os.path.join(ROOT, "results", "orb_final.json")))["configs"]:
        x = np.load(os.path.join(ROOT, "results", "orb_final", f"{c['key']}_trades.npy"))
        res[f"orb_{c['key']}"] = score([(x, c["sym"])])
    book = json.load(open(os.path.join(ROOT, "results", "book_v3.json")))
    legs = []
    for leg in book["kept"]:
        sym = PFX[leg.split("_")[0]]
        x = np.load(os.path.join(ROOT, book["files"][leg]))
        res[f"book_{leg}"] = score([(x, sym)]); legs.append((x, sym))
    res["book_all_unweighted"] = score(legs)
    json.dump(res, open(os.path.join(ROOT, "results", "northstar", "baselines_financed.json"), "w"), indent=1)
    for k, v in res.items():
        line = " | ".join(f"{p} n={v[p]['after']['n']:5d} E {v[p]['before'].get('E') or 0:+.3f}->{v[p]['after'].get('E') or 0:+.3f}"
                          for p in PERIODS)
        print(f"{k:38s} {line} | oos t={v['oos']['after'].get('t', 0):+.2f} PF={v['oos']['after'].get('PF') or 0:.2f} | stress {v['stress_dev_val'].get('E', 0):+.3f} | {''.join('Y' if x else '.' for x in v['criteria'].values())}")


if __name__ == "__main__":
    main()

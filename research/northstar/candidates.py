"""Part 9: every surviving candidate on the brief's metric list (R after costs AND financing, 1R per trade
unless stated; portfolios use the frozen leg weights).

    python3 candidates.py -> results/northstar/candidates.json
"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core
from grid import year_index, SYMS
from confirm import run
from rescore import ROOT, finance
import ns_portfolio as PF

RES = os.path.join(ROOT, "results", "northstar")


def months(t):
    return np.asarray(t, np.int64).astype("datetime64[s]").astype("datetime64[M]").astype(np.int64)


def metrics(t, r, w=None, inst=None):
    w = np.ones(len(r)) if w is None else w
    x = r * w
    o = np.argsort(t); t, x, r = t[o], x[o], r[o]
    inst = None if inst is None else inst[o]
    cum = np.cumsum(x); dd = float((np.maximum.accumulate(np.r_[0, cum]) - np.r_[0, cum]).max())
    m = months(t); um = np.arange(m.min(), m.max() + 1); ms = np.zeros(len(um)); np.add.at(ms, m - um[0], x)
    y = year_index(t); ys = {int(k): float(x[y == k].sum()) for k in np.unique(y)}
    down = ms[ms < 0]
    se = r.std(ddof=1) / math.sqrt(len(r))
    w_, l_ = r[r > 0].sum(), -r[r < 0].sum()
    out = dict(n=int(len(r)), E=float(r.mean()), E_ci95=[float(r.mean() - 1.96 * se), float(r.mean() + 1.96 * se)],
               t=float(r.mean() / se), PF=float(w_ / l_) if l_ > 0 else None, total_R=float(x.sum()), max_dd_R=dd,
               recovery=float(x.sum() / dd) if dd > 0 else None,
               sharpe_m=float(ms.mean() / ms.std(ddof=1) * math.sqrt(12)) if ms.std() > 0 else None,
               sortino_m=float(ms.mean() / math.sqrt((down ** 2).sum() / len(ms)) * math.sqrt(12)) if len(down) else None,
               pos_years=f"{sum(v > 0 for v in ys.values())}/{len(ys)}", pos_months=float((ms > 0).mean()), years=ys)
    if inst is not None:
        out["per_instrument_E"] = {str(s): float(r[inst == s].mean()) for s in np.unique(inst)}
    return out, dict(zip(um.tolist(), ms.tolist()))


def corr(a, b):
    k = sorted(set(a) & set(b))
    if len(k) < 12:
        return None
    x = np.array([a[i] for i in k]); y = np.array([b[i] for i in k])
    return float(np.corrcoef(x, y)[0, 1])


def combined_dd(*series):
    k = sorted(set().union(*[set(s) for s in series]))
    x = np.array([sum(s.get(i, 0.0) for s in series) for i in k]); c = np.cumsum(x)
    return float((np.maximum.accumulate(np.r_[0, c]) - np.r_[0, c]).max())


def stream_portfolio(which):
    T, names = PF.build(which)
    return T["t_in"], T["r"], T["w"], np.array([names[i]["sym"] for i in T["leg"]])


def stream_module(mod, cfg):
    ts, rs, ins = [], [], []
    for s in SYMS:
        tr = run(core.Mkt(s), mod, cfg, cut=0)
        ts.append(tr[:, 0].astype(np.int64)); rs.append(tr[:, 3]); ins.append(np.full(len(tr), s))
    return np.concatenate(ts), np.concatenate(rs), None, np.concatenate(ins)


def stream_orb(key, sym):
    x = np.load(os.path.join(ROOT, "results", "orb_final", f"{key}_trades.npy"))
    return x["t_in"].astype(np.int64), x["r"] - finance(x, sym), None, np.full(len(x), sym)


def main():
    sel = json.load(open(os.path.join(RES, "selection.json"))); base = json.load(open(os.path.join(RES, "baselines_financed.json")))
    conf = json.load(open(os.path.join(RES, "confirm.json"))); tiers = json.load(open(os.path.join(RES, "tiers.json")))
    C = {"BOOK (11 legs, weighted)": stream_portfolio("BOOK"), "BOOK+FOUR (23 legs, weighted)": stream_portfolio("BOOK+FOUR")}
    F = stream_portfolio("BOOK+FOUR"); kb = F[3] != "x"
    T4, _ = PF.build("BOOK+FOUR"); four = T4["leg"] >= 11
    C["FOUR (16 legs, weighted)"] = (T4["t_in"][four], T4["r"][four], T4["w"][four], np.array(["-"] * four.sum()))
    for mod in ("QM", "QM+FVG"):
        C[f"{mod} candidate"] = stream_module(mod, sel[mod]["candidate"])
    for c in json.load(open(os.path.join(ROOT, "results", "orb_final.json")))["configs"]:
        C[f"ORB {c['key']} ({c['sym']})"] = stream_orb(c["key"], c["sym"])
    out = {}; monthly = {}
    for name, (t, r, w, inst) in C.items():
        full, ms = metrics(t, r, w, inst)
        oos = t >= core.CUT
        o, _ = metrics(t[oos], r[oos], None if w is None else w[oos], inst[oos])
        out[name] = dict(full_2011_2025=full, oos_2023_2025=o); monthly[name] = ms
    for name in out:
        out[name]["corr_monthly_with_BOOK"] = corr(monthly[name], monthly["BOOK (11 legs, weighted)"])
        out[name]["corr_monthly_with_FOUR"] = corr(monthly[name], monthly["FOUR (16 legs, weighted)"])
        out[name]["combined_dd_R_with_BOOK"] = combined_dd(monthly[name], monthly["BOOK (11 legs, weighted)"])
    out["BOOK (11 legs, weighted)"]["book_alone_dd_R"] = combined_dd(monthly["BOOK (11 legs, weighted)"])
    for mod in ("QM", "QM+FVG"):
        k = f"{mod} candidate"
        out[k].update(tier=tiers[mod]["tier"], walk_forward_E=sel[mod]["walk_forward"]["E"], neighbours_all_pos=sel[mod]["neighbours_all_pos"],
                      neighbours_median_t=sel[mod]["neighbours_median_t"], stress_dev_val_E=conf[mod]["stress_dev_val"]["E"],
                      dsr=conf[mod]["dsr"]["dsr"], configs_tried=sel[mod]["configs"])
    out["BOOK (11 legs, weighted)"].update(stress_dev_val_E_unweighted=base["book_all_unweighted"]["stress_dev_val"]["E"],
                                           criteria=base["book_all_unweighted"]["criteria"])
    out["FOUR (16 legs, weighted)"].update(stress_dev_val_E_unweighted=base["four_all"]["stress_dev_val"]["E"], criteria=base["four_all"]["criteria"])
    json.dump(out, open(os.path.join(RES, "candidates.json"), "w"), indent=1, default=float)
    for k, v in out.items():
        f, o = v["full_2011_2025"], v["oos_2023_2025"]
        print(f"{k:32s} full n={f['n']:5d} E={f['E']:+.3f} PF={f['PF'] or 0:.2f} Sh={f['sharpe_m'] or 0:.2f} So={f['sortino_m'] or 0:.2f} "
              f"DD={f['max_dd_R']:.1f}R RF={f['recovery'] or 0:.1f} yrs+ {f['pos_years']} mo+ {f['pos_months']:.2f} | "
              f"OOS n={o['n']} E={o['E']:+.3f} [{o['E_ci95'][0]:+.3f},{o['E_ci95'][1]:+.3f}] PF={o['PF'] or 0:.2f} | "
              f"corrBOOK {v['corr_monthly_with_BOOK'] if v['corr_monthly_with_BOOK'] is None else round(v['corr_monthly_with_BOOK'], 2)}")


if __name__ == "__main__":
    main()

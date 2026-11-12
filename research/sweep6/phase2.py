"""Phase 2 of the deep M1 study: entry conditions (research/sweep6/PREREGISTRATION.md). Superset of M1 setups on 12
markets, frictionless, outcome = R under the Phase 1 structure; LEARN 2011-15 chooses, CONFIRM 2016-19 must agree,
VALIDATE 2020-22 is reported. Single conditions, winners vs losers, pairs, loser anatomy, then the greedy scanner rule.
    python3 research/sweep6/phase2.py -> research/results/sweep6/phase2.json
"""
import os, sys, json, glob, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import sweep6_outcomes as OC   # noqa: E402

DIR = os.environ.get("SWEEP6_DIR", os.path.join(ROOT, "research", "results", "sweep6", "_cells"))
OUT = os.path.join(ROOT, "research", "results", "sweep6")
T = lambda y: int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp())
PER = {"LEARN": (T(2011), T(2016)), "CONFIRM": (T(2016), T(2020)), "VALIDATE": (T(2020), T(2023))}
FX = {"EURUSD", "GBPUSD", "USDJPY", "EURGBP"}
CHOICE = json.load(open(os.path.join(OUT, "phase1.json")))["choice"]
SHOW = ["3R", "5R", "10R", "20R", "TP2", "TP2-BE75", "P60"]
CONT = ["depth_atr", "depth_R", "pivot_age", "pullback_atr", "range_atr", "risk_atr", "ratio4", "ratio2", "c4pos", "mom60",
        "mom1440", "vol_regime", "daypos", "room1", "room2", "body2", "body4", "fill_delay"]


def load():
    cols = None; rows = []
    for f in sorted(glob.glob(os.path.join(DIR, "*_M1.npz"))):
        z = dict(np.load(f)); sym = os.path.basename(f).split("_")[0]
        q = OC.NAMES.index(CHOICE)
        m = (z["o_status"] == 3) & np.isfinite(z["o_R"][:, q])
        d = {k: z[k][m] for k in ("side", "t_conf", "body2", "body4", "body_min", "strict2", "strict4", "swmask", "tgmask", "sweep_pos",
                                  "pivots_swept", "depth_atr", "depth_R", "depth_pips", "reject", "pivot_age", "stop_vs_sweep_R",
                                  "pullback_atr", "range_atr", "risk_atr", "ratio4", "ratio2", "c4pos", "hour", "weekday", "mom60",
                                  "mom1440", "vol_regime", "daypos", "room1", "room2", "two_sided", "risk_pips")}
        d["sym"] = np.full(m.sum(), sym)
        d["R"] = z["o_R"][m, q].astype(float)
        for nm in SHOW:
            d["R_" + nm] = z["o_R"][m, OC.NAMES.index(nm)].astype(float)
        d["fill_delay"] = (z["o_tfill"][m] - z["t_conf"][m]) / 60.0
        d["mfe"] = z["o_mfe"][m].astype(float); d["stop_hit"] = z["o_stop_hit"][m]
        for k in ("p_tp1", "p_tp2", "p_3r", "p_past", "p_adv60", "p_fav60"):
            d[k] = z["o_" + k][m]
        rows.append(d)
    D = {k: np.concatenate([r[k] for r in rows]) for k in rows[0]}
    D["period"] = np.full(len(D["R"]), "", dtype=object)
    for pn, (a, b) in PER.items():
        D["period"][(D["t_conf"] >= a) & (D["t_conf"] < b)] = pn
    return D


def categories(D):
    """Categorical features as {feature: (labels array, ordered label list)}."""
    C = {}
    sp = D["sweep_pos"]
    lab = np.full(len(sp), "none", dtype=object)
    for d, nm in ((0, "candle 4"), (1, "candle 3"), (2, "candle 2"), (3, "candle 1"), (4, "candle before 1")):
        lab[sp == d] = nm
    lab[(sp >= 5) & (sp <= 7)] = "2-4 before candle 1"; lab[(sp >= 8) & (sp <= 13)] = "5-10 before candle 1"
    C["sweeping candle"] = (lab, ["candle 4", "candle 3", "candle 2", "candle 1", "candle before 1", "2-4 before candle 1", "5-10 before candle 1", "none"])
    bm = D["body_min"]
    C["smaller body of candles 2 and 4"] = (np.select([bm < 0.5, bm < 0.6, bm < 0.7], ["40-50%", "50-60%", "60-70%"], "70%+").astype(object), ["40-50%", "50-60%", "60-70%", "70%+"])
    C["engulfing"] = (np.select([D["strict2"] & D["strict4"], D["strict2"] | D["strict4"]], ["both strict", "one strict"], "both loose").astype(object), ["both strict", "one strict", "both loose"])
    ps = D["pivots_swept"]
    C["pivots swept"] = (np.select([ps == 0, ps == 1, ps == 2], ["none", "1", "2"], "3+").astype(object), ["1", "2", "3+", "none"])
    sv = D["stop_vs_sweep_R"]
    C["stop vs the sweep extreme"] = (np.select([~np.isfinite(sv), sv < -1e-9, sv <= 1e-9], ["no sweep", "stop inside the sweep wick", "stop at the sweep extreme"], "stop beyond the sweep extreme").astype(object),
                                      ["stop inside the sweep wick", "stop at the sweep extreme", "stop beyond the sweep extreme", "no sweep"])
    rj = D["reject"]; has = D["swmask"] > 0
    C["sweep candle closed back inside"] = (np.select([~has, rj], ["no sweep", "yes"], "no").astype(object), ["yes", "no", "no sweep"])
    hr = D["hour"]
    C["hour (UTC, candle 4 close)"] = (np.select([hr < 7, hr < 12, hr < 16, hr < 21], ["00-07 Asia", "07-12 London", "12-16 overlap", "16-21 New York"], "21-24 late").astype(object),
                                      ["00-07 Asia", "07-12 London", "12-16 overlap", "16-21 New York", "21-24 late"])
    C["weekday"] = (np.array(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], dtype=object)[D["weekday"]], ["Mon", "Tue", "Wed", "Thu", "Fri"])
    C["side"] = (np.where(D["side"] > 0, "buy", "sell").astype(object), ["buy", "sell"])
    C["target-side sweep too"] = (np.where(D["two_sided"], "yes", "no").astype(object), ["yes", "no"])
    return C


def quintiles(D, f):
    x = D[f]; L = (D["period"] == "LEARN") & np.isfinite(x)
    edges = np.quantile(x[L], [0.2, 0.4, 0.6, 0.8])
    lab = np.full(len(x), "n/a", dtype=object)
    names = [f"Q1 <= {edges[0]:.3g}", f"Q2 {edges[0]:.3g}-{edges[1]:.3g}", f"Q3 {edges[1]:.3g}-{edges[2]:.3g}", f"Q4 {edges[2]:.3g}-{edges[3]:.3g}", f"Q5 > {edges[3]:.3g}"]
    fin = np.isfinite(x)
    idx = np.searchsorted(edges, x[fin], side="right")
    lab[fin] = np.array(names, dtype=object)[idx]
    return lab, names + (["n/a"] if (~fin).any() else [])


def tstat_edge(x):
    return float(x.mean() / x.std() * np.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else 0.0


def tstat_diff(x, y):
    if len(x) < 3 or len(y) < 3:
        return 0.0
    se = np.sqrt(x.var() / len(x) + y.var() / len(y))
    return float((x.mean() - y.mean()) / se) if se > 0 else 0.0


def bin_table(D, lab, names, R):
    out = {}
    for b in names:
        rec = {}
        for pn in PER:
            P = D["period"] == pn
            x = R[P & (lab == b)]; y = R[P & (lab != b)]
            rec[pn] = dict(n=int(len(x)), E=round(float(x.mean()), 4) if len(x) else None, win=round(float((x > 0).mean()), 4) if len(x) else None,
                           t_edge=round(tstat_edge(x), 2), t_vs_rest=round(tstat_diff(x, y), 2))
        L_, C_ = rec["LEARN"], rec["CONFIRM"]
        rec["IMPROVE"] = bool(L_["n"] >= 300 and C_["n"] >= 200 and L_["t_vs_rest"] >= 3 and C_["t_vs_rest"] >= 2)
        rec["WORSE"] = bool(L_["n"] >= 300 and C_["n"] >= 200 and L_["t_vs_rest"] <= -3 and C_["t_vs_rest"] <= -2)
        rec["EDGE"] = bool(L_["n"] >= 300 and C_["n"] >= 200 and L_["t_edge"] >= 3 and C_["t_edge"] >= 2 and (L_["E"] or 0) > 0 and (C_["E"] or 0) > 0)
        out[b] = rec
    return out


def ks(a, b):
    a = np.sort(a); b = np.sort(b)
    v = np.concatenate([a, b])
    return float(np.max(np.abs(np.searchsorted(a, v, side="right") / len(a) - np.searchsorted(b, v, side="right") / len(b))))


def main():
    D = load()
    R = D["R"]
    res = dict(prereg="research/sweep6/PREREGISTRATION.md", structure=CHOICE, n={pn: int((D["period"] == pn).sum()) for pn in PER},
               overall={pn: dict(E=round(float(R[D["period"] == pn].mean()), 4), win=round(float((R[D["period"] == pn] > 0).mean()), 4)) for pn in PER},
               single={}, single_other_structures={}, winners_vs_losers={}, pairs={}, loser_anatomy={}, owner_tables={}, tests={})
    feats = categories(D)
    for f in CONT:
        feats[f] = quintiles(D, f)
    n_tests = 0
    for f, (lab, names) in feats.items():
        res["single"][f] = bin_table(D, lab, names, R)
        n_tests += len(names)
        res["single_other_structures"][f] = {nm: {b: {pn: round(float(D["R_" + nm][(D["period"] == pn) & (lab == b)].mean()), 4) if ((D["period"] == pn) & (lab == b)).any() else None
                                                       for pn in PER} for b in names} for nm in ("3R", "10R", "TP2")}
    res["tests"]["single_bins"] = n_tests
    # winners vs losers (continuous features)
    for f in CONT:
        rec = {}
        for pn in ("LEARN", "CONFIRM"):
            P = (D["period"] == pn) & np.isfinite(D[f])
            w = D[f][P & (R > 0)]; l_ = D[f][P & (R <= 0)]
            sd = np.sqrt((w.var() + l_.var()) / 2)
            rec[pn] = dict(winners_mean=round(float(w.mean()), 4), losers_mean=round(float(l_.mean()), 4),
                           smd=round(float((w.mean() - l_.mean()) / sd), 4) if sd > 0 else None, ks=round(ks(w, l_), 4))
        res["winners_vs_losers"][f] = rec
    # pairs among the 8 features with the widest LEARN spread
    spread = {}
    for f, tab in res["single"].items():
        v = [r["LEARN"]["E"] for r in tab.values() if r["LEARN"]["n"] >= 300 and r["LEARN"]["E"] is not None]
        spread[f] = max(v) - min(v) if len(v) >= 2 else 0
    top = sorted(spread, key=spread.get, reverse=True)[:8]
    res["pairs_features"] = top
    n_pairs = 0
    for f1, f2 in itertools.combinations(top, 2):
        l1, n1 = feats[f1]; l2, n2 = feats[f2]
        for b1 in n1:
            for b2 in n2:
                n_pairs += 1
                m = (l1 == b1) & (l2 == b2)
                rec = {}
                for pn in PER:
                    P = D["period"] == pn
                    x = R[P & m]; y = R[P & ~m]
                    rec[pn] = dict(n=int(len(x)), E=round(float(x.mean()), 4) if len(x) else None, t_edge=round(tstat_edge(x), 2), t_vs_rest=round(tstat_diff(x, y), 2))
                L_, C_ = rec["LEARN"], rec["CONFIRM"]
                ok_edge = L_["n"] >= 300 and C_["n"] >= 200 and L_["t_edge"] >= 3 and C_["t_edge"] >= 2 and (L_["E"] or 0) > 0 and (C_["E"] or 0) > 0
                ok_imp = L_["n"] >= 300 and C_["n"] >= 200 and L_["t_vs_rest"] >= 3 and C_["t_vs_rest"] >= 2
                if ok_edge or ok_imp:
                    res["pairs"][f"{f1} = {b1} & {f2} = {b2}"] = dict(EDGE=bool(ok_edge), IMPROVE=bool(ok_imp), **rec)
    res["tests"]["pair_cells"] = n_pairs
    res["tests"]["expected_false_passes"] = round((n_tests + n_pairs) * 0.00135 * 0.023, 3)
    # loser anatomy (losers under the chosen structure)
    lose = R <= 0
    cat = np.select([D["mfe"] < 0.3, D["mfe"] >= 1.0], ["immediate failure (best < 0.3R)", "reversal (reached >= 1R first)"], "middle (0.3-1R)").astype(object)
    for pn in PER:
        P = (D["period"] == pn) & lose & (D["stop_hit"] == 1)
        res["loser_anatomy"][pn] = dict(losers=int(P.sum()),
            shares={c: round(float((cat[P] == c).mean()), 4) for c in ("immediate failure (best < 0.3R)", "middle (0.3-1R)", "reversal (reached >= 1R first)")},
            wick_stop=round(float(((D["p_adv60"][P] < 0.2) & (D["p_fav60"][P] == 1)).mean()), 4),
            breakout_3R_past_stop=round(float((D["p_past"][P] >= 3).mean()), 4),
            reached_TP1_within_a_day=round(float(D["p_tp1"][P].mean()), 4), reached_TP2_within_a_day=round(float(D["p_tp2"][P].mean()), 4))
    # owner tables: sweep depth in pips (FX only)
    fx = np.isin(D["sym"], list(FX))
    dp = D["depth_pips"]
    lab = np.select([~np.isfinite(dp), dp < 1, dp < 2, dp < 3, dp < 5, dp < 10], ["no sweep", "0-1 pip", "1-2 pips", "2-3 pips", "3-5 pips", "5-10 pips"], "10+ pips").astype(object)
    names = ["0-1 pip", "1-2 pips", "2-3 pips", "3-5 pips", "5-10 pips", "10+ pips", "no sweep"]
    sub = {k: (v[fx] if isinstance(v, np.ndarray) and len(v) == len(R) else v) for k, v in D.items()}
    res["owner_tables"]["sweep depth (FX pairs, pips)"] = bin_table(sub, lab[fx], names, R[fx])
    res["owner_tables"]["sweep depth (FX pairs, pips), other structures"] = {nm: {b: {pn: round(float(D["R_" + nm][fx][(sub["period"] == pn) & (lab[fx] == b)].mean()), 4) if ((sub["period"] == pn) & (lab[fx] == b)).any() else None for pn in PER} for b in names} for nm in ("3R", "10R", "TP2")}
    # greedy scanner rule
    res["scanner"] = greedy(D, feats, res)
    json.dump(res, open(os.path.join(OUT, "phase2.json"), "w"), indent=1, default=float)
    return res


def greedy(D, feats, res):
    """Start from the superset; candidates = single bins and pair cells that passed IMPROVE or EDGE (keep the bin) and
    single bins that are WORSE (drop the bin). Add the candidate that raises LEARN R a trade the most, if it adds >= 0.02R
    with t >= 3 against the setups it removes, CONFIRM R a trade does not fall, and >= 300 LEARN trades remain. <= 4 steps."""
    R = D["R"]
    cands = []
    for f, tab in res["single"].items():
        lab, _ = feats[f]
        for b, rec in tab.items():
            if rec["IMPROVE"] or rec["EDGE"]:
                cands.append((f"{f} = {b}", lab == b))
            if rec["WORSE"]:
                cands.append((f"{f} != {b}", lab != b))
    for key, rec in res["pairs"].items():
        (f1, b1), (f2, b2) = [tuple(x.split(" = ", 1)) for x in key.split(" & ")]
        cands.append((key, (feats[f1][0] == b1) & (feats[f2][0] == b2)))
    cur = np.ones(len(R), bool); steps = []
    L = D["period"] == "LEARN"; C = D["period"] == "CONFIRM"; V = D["period"] == "VALIDATE"
    for _ in range(4):
        best = None
        for name, m in cands:
            new = cur & m; gone = cur & ~m
            if (new & L).sum() < 300 or not gone.any():
                continue
            gain = R[new & L].mean() - R[cur & L].mean()
            t = tstat_diff(R[new & L], R[gone & L])
            if gain < 0.02 or t < 3:
                continue
            if R[new & C].mean() < R[cur & C].mean():
                continue
            if best is None or R[new & L].mean() > best[2]:
                best = (name, m, R[new & L].mean(), gain, t)
        if best is None:
            break
        cur = cur & best[1]
        steps.append(dict(condition=best[0], LEARN_E=round(float(best[2]), 4), gain=round(float(best[3]), 4), t=round(best[4], 2),
                          CONFIRM_E=round(float(R[cur & C].mean()), 4), VALIDATE_E=round(float(R[cur & V].mean()), 4),
                          n={"LEARN": int((cur & L).sum()), "CONFIRM": int((cur & C).sum()), "VALIDATE": int((cur & V).sum())}))
        cands = [c for c in cands if c[0] != best[0]]
    out = dict(steps=steps, final_n={pn: int((cur & (D["period"] == pn)).sum()) for pn in PER})
    out["final_by_structure"] = {}
    for nm in OC.NAMES if False else SHOW:
        out["final_by_structure"][nm] = {pn: round(float(D["R_" + nm][cur & (D["period"] == pn)].mean()), 4) for pn in PER}
    out["final_E_chosen_structure"] = {pn: round(float(R[cur & (D["period"] == pn)].mean()), 4) for pn in PER}
    np.save(os.path.join(DIR, "scanner_mask.npy"), cur)
    return out


if __name__ == "__main__":
    r = main()
    print("structure", r["structure"], "n", r["n"], "overall", r["overall"], "tests", r["tests"])
    for f, tab in r["single"].items():
        flags = [(b, "IMP" if v["IMPROVE"] else "", "EDGE" if v["EDGE"] else "", "WORSE" if v["WORSE"] else "") for b, v in tab.items() if v["IMPROVE"] or v["EDGE"] or v["WORSE"]]
        print(f, "|", " ; ".join(f"{b}: L {tab[b]['LEARN']['E']} ({tab[b]['LEARN']['n']}) C {tab[b]['CONFIRM']['E']} V {tab[b]['VALIDATE']['E']} {x}{y}{z}" for b, x, y, z in flags))
    print("pairs passing:", len(r["pairs"]))
    print("scanner:", json.dumps(r["scanner"], indent=1))

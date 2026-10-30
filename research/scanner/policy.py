"""Daily London scanner, step 2: online ranking (past-only scores) and the one-trade-at-a-time policies of
PREREGISTRATION.md §3-6.

    python3 policy.py -> ../results/scanner/policies.csv, selected.json, oos_log.json
"""
import os, json, time, itertools, math
import numpy as np
import pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "scanner")
PERIODS = {"dev": (2013, 2019), "val": (2020, 2022), "oos": (2023, 2025)}
THETAS = [0.0, 0.03, 0.06, 0.10]
CAPS = [1, 99]
SCORES = ["S1", "S2"]
_STARTS = np.array([(np.datetime64(f"{y}-01-01") - np.datetime64("1970-01-01")).astype(int) for y in range(1970, 2101)])


def year_of(t):
    return np.searchsorted(_STARTS, np.asarray(t, np.int64) // 86400, side="right") - 1 + 1970


@njit(cache=True)
def online_scores(dec_t, cell, t_out, r, n_cells, k):
    """score_i = sum of r over earlier candidates of the same cell whose trades closed before dec_t_i, / (n + k)."""
    n = len(dec_t); out = np.zeros(n)
    order_out = np.argsort(t_out)
    s = np.zeros(n_cells); c = np.zeros(n_cells); j = 0
    for i in range(n):                                   # candidates are sorted by dec_t
        while j < n and t_out[order_out[j]] < dec_t[i]:
            q = order_out[j]; s[cell[q]] += r[q]; c[cell[q]] += 1; j += 1
        out[i] = s[cell[i]] / (c[cell[i]] + k)
    return out


@njit(cache=True)
def run_policy(dec_t, day, t_out, score, key, theta, cap, use_score):
    """One trade at a time. Candidates sorted by dec_t. At each decision time while flat, take the candidate
    with the best score (> theta) — or, if use_score is False, the one with the lowest random key."""
    n = len(dec_t); take = np.zeros(n, np.bool_); busy = -1; i = 0; cur_day = -1; nday = 0
    while i < n:
        j = i
        while j < n and dec_t[j] == dec_t[i]:
            j += 1
        if day[i] != cur_day:
            cur_day = day[i]; nday = 0
        if dec_t[i] >= busy and nday < cap:
            best = -1; bv = -1e18
            for q in range(i, j):
                v = score[q] if use_score else -key[q]
                if use_score and score[q] <= theta:
                    continue
                if v > bv:
                    bv = v; best = q
            if best >= 0:
                take[best] = True; busy = t_out[best]; nday += 1
        i = j
    return take


def metrics(r, t):
    if len(r) < 2:
        return dict(n=int(len(r)), E=float(np.mean(r)) if len(r) else None)
    se = r.std(ddof=1) / math.sqrt(len(r)); w, lo = r[r > 0].sum(), -r[r < 0].sum()
    eq = np.cumprod(1 + 0.01 * r); pk = np.maximum.accumulate(eq)
    yrs = max((t.max() - t.min()) / (365.25 * 86400), 0.5)
    return dict(n=int(len(r)), E=float(r.mean()), t=float(r.mean() / se) if se > 0 else None, PF=float(w / lo) if lo > 0 else None,
                win=float((r > 0).mean()), per_year=float(len(r) / yrs), cagr_1pct=float(eq[-1] ** (1 / yrs) - 1),
                maxdd_1pct=float((1 - eq / pk).max()))


def by_period(r, t):
    y = year_of(t)
    return {p: metrics(r[(y >= a) & (y <= b)], t[(y >= a) & (y <= b)]) for p, (a, b) in PERIODS.items()}


def prepare(C, rcol, tcol):
    C = C.sort_values(["dec_t", "sym", "fam", "side"], kind="stable").reset_index(drop=True)
    cells = {"S1": C.fam + "|" + C.sym + "|" + C.side.astype(str) + "|" + C.aligned.astype(str), "S2": C.fam + "|" + C.sym}
    sc = {}
    for s, key in cells.items():
        codes, uniq = pd.factorize(key)
        sc[s] = online_scores(C.dec_t.values.astype(np.int64), codes.astype(np.int64), C[tcol].values.astype(np.int64),
                              C[rcol].values, len(uniq), 30.0)
    return C, sc


def evaluate(C, sc, rcol, tcol, label, rng_seeds=200):
    rows = []; dec = C.dec_t.values.astype(np.int64); day = C.ldate.values.astype(np.int64); tout = C[tcol].values.astype(np.int64)
    r = C[rcol].values; t = C.t_in.values
    rows.append(dict(policy="ALL", **flat(by_period(r, t))))
    rng = np.random.default_rng(1)
    rnd = [];
    for k in range(rng_seeds):
        key = rng.random(len(C))
        tk = run_policy(dec, day, tout, np.zeros(len(C)), key, 0.0, 99, False)
        rnd.append(by_period(r[tk], t[tk]))
    rows.append(dict(policy="RANDOM (median of 200)", **{f"{p}_{m}": float(np.median([x[p][m] for x in rnd if x[p].get(m) is not None]))
                                                         for p in PERIODS for m in ("n", "E", "t", "PF", "cagr_1pct", "maxdd_1pct")}))
    rnd_oos = np.array([x["oos"]["E"] for x in rnd])
    takes = {}
    for s, th, cap in itertools.product(SCORES, THETAS, CAPS):
        tk = run_policy(dec, day, tout, sc[s], np.zeros(len(C)), th, cap, True)
        takes[(s, th, cap)] = tk
        rows.append(dict(policy=f"BEST {s} theta={th} cap={'1/day' if cap == 1 else 'none'}", score=s, theta=th, cap=cap,
                         **flat(by_period(r[tk], t[tk]))))
    P = pd.DataFrame(rows); P.insert(0, "pool", label)
    return P, takes, rnd_oos


def flat(d):
    return {f"{p}_{k}": v for p, m in d.items() for k, v in m.items()}


def selection_value(C, sc, take, s, rcol):
    """On decision bars where the policy took a trade and >= 2 candidates were present: chosen r - mean(others)."""
    y = year_of(C.t_in.values); out = {}
    g = C.assign(taken=take, y=y).groupby("dec_t")
    diffs = {p: [] for p in PERIODS}
    for _, G in g:
        if G.taken.any() and len(G) >= 2:
            ch = G[G.taken][rcol].values[0]; oth = G[~G.taken][rcol].mean(); yy = G.y.values[0]
            for p, (a, b) in PERIODS.items():
                if a <= yy <= b:
                    diffs[p].append(ch - oth)
    for p, d in diffs.items():
        d = np.array(d)
        out[p] = dict(n=int(len(d)), mean_diff=float(d.mean()) if len(d) else None,
                      t=float(d.mean() / (d.std(ddof=1) / math.sqrt(len(d)))) if len(d) > 2 else None)
    return out


def main():
    C0 = pd.read_csv(os.path.join(RES, "candidates.csv.gz"))
    C, sc = prepare(C0, "r", "t_out")
    P, takes, rnd_oos = evaluate(C, sc, "r", "t_out", "all families")
    # development selection (pre-registered): highest dev t among BEST variants with >= 200 dev trades
    B = P[P.policy.str.startswith("BEST") & (P.dev_n >= 200)].sort_values("dev_t", ascending=False)
    sel = B.iloc[0]; key = (sel.score, float(sel.theta), int(sel.cap))
    print("selected on development:", sel.policy, f"dev n={sel.dev_n} E={sel.dev_E:+.3f} t={sel.dev_t:.2f}")
    # stress pool (costs x1.5, +1 minute), scores learned on stressed outcomes
    Cs, scs = prepare(C0[np.isfinite(C0.r_stress)], "r_stress", "t_out_stress")    # a 1-minute delay can make a setup untradeable
    Ps, takes_s, _ = evaluate(Cs, scs, "r_stress", "t_out_stress", "stress", rng_seeds=20)
    # without the known EUH leg
    Cn, scn = prepare(C0[C0.fam != "EUH"], "r", "t_out")
    Pn, takes_n, rnd_n = evaluate(Cn, scn, "r", "t_out", "without EUH", rng_seeds=50)
    pd.concat([P, Ps, Pn], ignore_index=True).to_csv(os.path.join(RES, "policies.csv"), index=False)

    tk = takes[key]; T = C[tk]
    sv = selection_value(C, sc, tk, key[0], "r")
    fam_mix = T.assign(y=year_of(T.t_in.values)).groupby("fam").agg(n=("r", "size"), E=("r", "mean")).round(3).to_dict("index")
    sym_mix = T.groupby("sym").agg(n=("r", "size"), E=("r", "mean")).round(3).to_dict("index")
    nb = []
    for s, th, cap in itertools.product(SCORES, THETAS, CAPS):
        i = THETAS.index(th); i0 = THETAS.index(key[1])
        if s == key[0] and ((cap == key[2] and abs(i - i0) == 1) or (cap != key[2] and th == key[1])):
            row = P[(P.score == s) & (P.theta == th) & (P.cap == cap)].iloc[0]
            nb.append(dict(variant=row.policy, dev_E=row.dev_E, dev_n=int(row.dev_n)))
    row_s = Ps[(Ps.score == key[0]) & (Ps.theta == key[1]) & (Ps.cap == key[2])].iloc[0]
    row_n = Pn[(Pn.score == key[0]) & (Pn.theta == key[1]) & (Pn.cap == key[2])].iloc[0]
    o = dict(n=sel.oos_n, E=sel.oos_E, t=sel.oos_t, PF=sel.oos_PF)
    crit = {
        "1_E_pos_dev_val_oos": bool(sel.dev_E > 0 and sel.val_E > 0 and sel.oos_E > 0),
        "2_oos_PF110_t2_n100": bool((sel.oos_PF or 0) >= 1.10 and (sel.oos_t or 0) >= 2.0 and sel.oos_n >= 100),
        "3_neighbours_dev_pos": bool(len(nb) > 0 and all(x["dev_E"] > 0 for x in nb)),
        "4_stress_2013_2022_pos": bool((row_s.dev_E * row_s.dev_n + row_s.val_E * row_s.val_n) / (row_s.dev_n + row_s.val_n) > 0),
        "5_selection_value_oos": bool((sv["oos"]["mean_diff"] or -1) > 0 and sel.oos_E > np.median(rnd_oos)),
        "6_without_EUH_oos_pos": bool(row_n.oos_E > 0),
    }
    verdict = "deployment-ready" if all(crit.values()) else (
        "forward-test" if crit["1_E_pos_dev_val_oos"] and crit["3_neighbours_dev_pos"] and crit["4_stress_2013_2022_pos"] and (sel.oos_PF or 0) >= 1.05
        else "rejected")
    res = dict(selected=sel.policy, key=list(key), dev=dict(n=sel.dev_n, E=sel.dev_E, t=sel.dev_t, PF=sel.dev_PF),
               val=dict(n=sel.val_n, E=sel.val_E, t=sel.val_t, PF=sel.val_PF), oos=o,
               cagr_1pct={p: sel[f"{p}_cagr_1pct"] for p in PERIODS}, maxdd_1pct={p: sel[f"{p}_maxdd_1pct"] for p in PERIODS},
               random_oos_E_median=float(np.median(rnd_oos)), random_oos_E_p95=float(np.quantile(rnd_oos, 0.95)),
               selection_value=sv, neighbours=nb, stress=dict(dev_E=row_s.dev_E, val_E=row_s.val_E, oos_E=row_s.oos_E),
               without_EUH=dict(dev_E=row_n.dev_E, val_E=row_n.val_E, oos_E=row_n.oos_E, oos_n=row_n.oos_n),
               family_mix=fam_mix, market_mix=sym_mix, criteria=crit, verdict=verdict)
    json.dump(res, open(os.path.join(RES, "selected.json"), "w"), indent=1, default=float)
    log = os.path.join(RES, "oos_log.json")
    L = json.load(open(log)) if os.path.exists(log) else []
    if not any(e["variant"] == sel.policy for e in L):                 # one logged look per variant
        L.append(dict(time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), variant=sel.policy, oos=o))
    json.dump(L, open(log, "w"), indent=1, default=float)
    cols = ["pool", "policy", "dev_n", "dev_E", "dev_t", "val_n", "val_E", "val_t", "oos_n", "oos_E", "oos_t", "oos_PF", "oos_cagr_1pct", "oos_maxdd_1pct"]
    with pd.option_context("display.width", 250, "display.max_rows", 100):
        print(pd.concat([P, Ps, Pn])[cols].round(3).to_string(index=False))
    print(json.dumps({k: v for k, v in res.items() if k not in ("family_mix", "market_mix")}, indent=1, default=float))
    print("family mix", fam_mix); print("market mix", sym_mix)


if __name__ == "__main__":
    main()

"""THE TRUTH LAB — one protocol for any trading idea.

    python3 research/truth/run.py research/truth/strategies/<idea>.py [--no-look] [--markets XAUUSD,EURUSD]

A strategy file (see strategies/TEMPLATE.py) declares NAME, HYPOTHESIS, MARKETS, TIMEFRAMES, GRID and
signals(B, p, M). The protocol, identical for every idea (rules of research/northstar/PREREGISTRATION.md):

  0  fingerprint   SHA-256 of the strategy file. Once its 2023-25 look is logged, a changed file must be
                   given a new NAME (no tuning after seeing the final period).
  1  look-ahead    signals on truncated history must equal signals on full history (prefix invariance).
  2  grid          every TIMEFRAME x GRID x management config, every market, fills before 2023 only
                   (costs + swaps + rollover block + one position at a time; North Star execution core).
  3  selection     development 2011-19 gate (>= 200 trades, both eras > 0, >= 75% of markets > 0),
                   rank by t; neighbours; validation 2020-22; walk-forward 2014-22.
  4  confirmation  trade level: stress (costs x1.5, swaps x2, +1 minute), deflated Sharpe vs the grid.
  5  final look    2023-25, ONE logged look per fingerprint + configuration.
  6  verdict       Tier A (deployment-ready) / Tier B (forward-test) / Rejected.
  7  costs         same trades at a low-cost swap-free profile (x0.5, no swap).
  8  portfolio     correlation with the 11-leg book and the combined Sharpe.
  9  report        results/truth/<NAME>/REPORT.md; EA_SPEC.md + parity trade list if Tier A or B.
"""
import os, sys, json, time, hashlib, itertools, importlib.util, math
from multiprocessing import Pool
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "northstar")); sys.path.insert(0, ROOT)
import core
import engine as E
from grid import agg, year_index
from analyze import summ, jsonable
from confirm import stats, deflated_sharpe
from oos import tier

RES = os.path.join(ROOT, "results", "truth")
COSTS = json.load(open(os.path.join(HERE, "costs.json")))
DEV, ERA1, ERA2, VAL = list(range(2011, 2020)), list(range(2011, 2016)), list(range(2016, 2020)), [2020, 2021, 2022]
DEFAULT_MGMT = {"tgt": [2.0, 3.0, 0.0], "trail": [0.0, 3.0], "bias": [0, 1]}


# ----------------------------------------------------------------------------- loading
def load_strategy(path):
    spec = importlib.util.spec_from_file_location("strategy_under_test", path)
    S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
    for need in ("NAME", "HYPOTHESIS", "TIMEFRAMES", "GRID", "signals"):
        if not hasattr(S, need):
            raise SystemExit(f"strategy file lacks {need}")
    S.MARKETS = getattr(S, "MARKETS", ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"])
    S.MANAGEMENT = getattr(S, "MANAGEMENT", DEFAULT_MGMT)
    S.TIME_STOP = getattr(S, "TIME_STOP", 50)
    S.STOP_CAP_ATR = getattr(S, "STOP_CAP_ATR", 5.0)
    S.FINGERPRINT = hashlib.sha256(open(path, "rb").read()).hexdigest()
    S.PATH = path
    return S


def ensure_costs(sym):
    if sym not in COSTS:
        raise SystemExit(f"no cost entry for {sym} in research/truth/costs.json")
    E.COST[sym] = COSTS[sym]["cost"]; core.SWAP[sym] = COSTS[sym]["swap"]


def market(sym, S=None):
    ensure_costs(sym)
    over = getattr(S, "COSTS", {}) if S is not None else {}
    if sym in over:                                          # the strategy's own cost assumption (e.g. the owner's spec)
        E.COST[sym] = over[sym]
    return core.Mkt(sym)


def execute(S, M, B, C, p, tgt, trail, bias, cut=core.CUT, **kw):
    if hasattr(S, "EXECUTOR"):
        return S.EXECUTOR(M, B, C, p, cut=cut, **kw)
    core.TIME_STOP = S.TIME_STOP
    return core.execute(M, B, C, tgt, trail, cut=cut, bias=bool(bias), **kw)


# ----------------------------------------------------------------------------- signals -> candidates
from numba import njit


@njit(cache=True)
def stop_scan(o, h, l, ts, bfirst, bnxt, start, end, side, level, cost, blo, bhi):
    """Pending STOP order from bar `start` to `end` (exclusive): a buy stop fills when the ask reaches the level
    (at the level, or the worse open on a gap); a sell stop when the bid reaches it. No fills in the rollover block."""
    for u in range(start, min(end, len(bfirst))):
        for k in range(bfirst[u], bnxt[u]):
            t = ts[k] % 86400
            if blo <= t < bhi:
                continue
            if side > 0:
                if h[k] + cost >= level:
                    return k, max(level, o[k] + cost), u
            else:
                if l[k] <= level:
                    return k, min(level, o[k]), u
    return -1, 0.0, -1


def to_candidates(B, rows, M, cap, spread=None):
    """rows: iterable of (bar, side, stop) for a market order at the next bar's open, or
    (bar, side, stop, limit_price, valid_bars) for a pending limit order from the next bar, or
    (bar, side, stop, stop_entry_price, valid_bars, "stop") for a pending stop order (breakout entry).
    spread: optional real bid-ask spread for limit fills (strategy FILL_SPREAD). Without it a buy limit fills only when
    bid + ALL-IN cost reaches the level (conservative: commission is not part of the quote). With it the fill test uses
    the spread, and the rest of the all-in cost (commission + slippage) is added to the long entry price, so the round
    trip still pays exactly the all-in cost."""
    out = []; n = len(B["c"])
    fill_cost = M.cost if spread is None else float(spread)
    for r in rows:
        bar, side, stop = int(r[0]), int(r[1]), float(r[2])
        if bar + 2 >= n or side not in (1, -1) or not np.isfinite(stop):
            continue
        dec_t = int(B["t"][bar] + B["minutes"] * 60)
        if len(r) >= 6 and r[5] == "stop":
            k, px, u = stop_scan(M.o, M.h, M.l, M.ts, B["first"], B["nxt"], bar + 1, bar + 1 + int(r[4]), side, float(r[3]),
                                 M.cost, core.BLOCK[0], core.BLOCK[1])
            if k >= 0:
                out.append((k, side, px, stop, u, u, cap, dec_t))
        elif len(r) >= 5:
            k, px, u = core.limit_scan(M.o, M.h, M.l, M.ts, B["first"], B["nxt"], B["c"], bar + 1, bar + 1 + int(r[4]), side,
                                       float(r[3]), stop, fill_cost, 0.1 * fill_cost, core.BLOCK[0], core.BLOCK[1])
            if k >= 0:
                if side > 0 and spread is not None:
                    px += M.cost - fill_cost                 # commission + slippage on top of the quoted ask
                out.append((k, side, px, stop, u, u, cap, dec_t))
        else:
            out.append((int(B["nxt"][bar]), side, -1.0, stop, bar + 1, bar, cap, dec_t))
    keys = ("k0", "side", "entry", "stop", "jb", "sig", "cap", "dec_t")
    ints = ("k0", "side", "jb", "sig", "dec_t")
    if not out:
        return {k: np.zeros(0, np.int64 if k in ints else np.float64) for k in keys}
    A_ = list(zip(*out))
    return {k: np.asarray(A_[i], np.int64 if k in ints else np.float64) for i, k in enumerate(keys)}


def param_sets(S):
    names = list(S.GRID)
    for tf in S.TIMEFRAMES:
        for vals in itertools.product(*[S.GRID[k] for k in names]):
            yield dict(tf=tf, **dict(zip(names, vals)))


def mgmt_sets(S):
    m = S.MANAGEMENT
    return list(itertools.product(m["tgt"], m["trail"], m["bias"]))


def run_config(S, M, p, tgt, trail, bias, cut=core.CUT, **kw):
    B = M.bars(p["tf"])
    C = to_candidates(B, S.signals(B, p, M), M, S.STOP_CAP_ATR, getattr(S, "FILL_SPREAD", {}).get(M.sym))
    return execute(S, M, B, C, p, tgt, trail, bias, cut=cut, **kw)


# ----------------------------------------------------------------------------- 1 look-ahead check
def lookahead_check(S, M, n_live=40, seed=7):
    """Two tests per timeframe (first parameter set):
    (a) real-time decision: for up to n_live signal bars b, history is cut right after b closes; the strategy must
        produce the same signal at b (a live EA only ever sees up to the last closed bar);
    (b) prefix invariance: at 3 cut points, every earlier signal must be unchanged (catches whole-series leaks)."""
    report = []; rng = np.random.default_rng(seed)
    for tf in S.TIMEFRAMES:
        p = next(q for q in param_sets(S) if q["tf"] == tf)
        B = M.bars(tf); n = len(B["c"])
        cut = lambda T: {k: (v[:T] if isinstance(v, np.ndarray) and len(v) == n else v) for k, v in B.items()}
        key = lambda rows: {(int(r[0]), int(r[1]), round(float(r[2]), 8)) for r in rows}
        full = key(S.signals(B, p, M))
        bars = sorted({x[0] for x in full if x[0] < n - 1})
        for b in (rng.choice(bars, size=min(n_live, len(bars)), replace=False) if bars else []):
            want = {x for x in full if x[0] == b}
            got = {x for x in key(S.signals(cut(int(b) + 1), p, M)) if x[0] == b}
            if want != got:
                report.append(dict(tf=tf, test="real-time decision", bar=int(b), full=str(sorted(want)), live=str(sorted(got)), ok=False))
                return False, report
        report.append(dict(tf=tf, test="real-time decision", checked=int(min(n_live, len(bars))), ok=True))
        for frac in (0.4, 0.6, 0.8):
            T = int(n * frac)
            a = {x for x in full if x[0] < T - 1}; b2 = {x for x in key(S.signals(cut(T), p, M)) if x[0] < T - 1}
            ok = a == b2
            report.append(dict(tf=tf, test="prefix", cut=frac, ok=ok, example=None if ok else str(sorted(a ^ b2)[:3])))
            if not ok:
                return False, report
    return True, report


# ----------------------------------------------------------------------------- 2 grid
def _worker(args):
    path, sym = args
    S = load_strategy(path); M = market(sym, S); rows = []
    for p in param_sets(S):
        B = M.bars(p["tf"])
        C = to_candidates(B, S.signals(B, p, M), M, S.STOP_CAP_ATR, getattr(S, "FILL_SPREAD", {}).get(M.sym))
        for tgt, trail, bias in mgmt_sets(S):
            tr = execute(S, M, B, C, p, tgt, trail, bias)
            rows.append(dict(sym=sym, **p, tgt=tgt, trail=trail, bias=int(bias), n_cands=len(C["k0"]), **agg(tr)))
    return rows


def run_grid(S, procs=4):
    with Pool(min(procs, len(S.MARKETS))) as pool:
        res = pool.map(_worker, [(S.PATH, s) for s in S.MARKETS])
    return pd.DataFrame([r for rr in res for r in rr])


# ----------------------------------------------------------------------------- 3 selection
def keycols(S):
    return ["tf"] + list(S.GRID) + ["tgt", "trail", "bias"]


def pooled(S, df):
    k = keycols(S)
    num = [c for c in df.columns if c[:2] in ("n_", "s_", "ss", "c_", "f_", "nl", "sl")]
    P = df.groupby(k, dropna=False)[num].sum()
    per = {s: df[df.sym == s].set_index(k)[num].reindex(P.index) for s in S.MARKETS}
    R = pd.concat([summ(P, DEV, "dev_"), summ(P, ERA1, "e1_"), summ(P, ERA2, "e2_"), summ(P, VAL, "val_")], axis=1)
    for s in S.MARKETS:
        R[f"devE_{s}"] = summ(per[s], DEV)["E"]
    need = max(1, math.ceil(0.75 * len(S.MARKETS)))
    R["mk_pos"] = sum((R[f"devE_{s}"] > 0).astype(int) for s in S.MARKETS)
    R["gate"] = (R.dev_n >= 200) & (R.e1_E > 0) & (R.e2_E > 0) & (R.mk_pos >= need)
    return P, per, R, need


def neighbours(S, key, R):
    names = keycols(S); cfg = dict(zip(names, key)); lists = {"tf": S.TIMEFRAMES, **S.GRID, "tgt": S.MANAGEMENT["tgt"], "trail": S.MANAGEMENT["trail"]}
    out = []
    for p, L in lists.items():
        L = list(L)
        hits = [i for i, v in enumerate(L) if v == cfg[p] or (isinstance(v, (int, float)) and isinstance(cfg[p], (int, float)) and float(v) == float(cfg[p]))]
        if not hits:
            continue
        i = hits[0]
        for j in (i - 1, i + 1):
            if 0 <= j < len(L):
                c2 = dict(cfg); c2[p] = L[j]; k2 = tuple(c2[x] for x in names)
                if k2 in R.index:
                    out.append(dict(param=p, value=L[j], dev_E=float(R.loc[k2, "dev_E"]), dev_t=float(R.loc[k2, "dev_t"]), dev_n=int(R.loc[k2, "dev_n"])))
    return out


def walk_forward(S, P, per, need):
    n = s = 0.0; picks = []
    for Y in range(2014, 2023):
        tr = [Y - 3, Y - 2, Y - 1]; X = summ(P, tr)
        pos = sum((summ(per[m], tr)["E"] > 0).astype(int) for m in S.MARKETS)
        ok = (X.n >= 100) & (X.E > 0) & (pos >= need)
        if not ok.any():
            picks.append(dict(year=Y, pick=None)); continue
        k = X[ok].t.idxmax(); ny, sy = float(P.loc[k, f"n_{Y}"]), float(P.loc[k, f"s_{Y}"])
        n += ny; s += sy; picks.append(dict(year=Y, pick=[str(x) for x in k], n=int(ny), E=sy / ny if ny else None))
    return dict(E=s / n if n else None, n=int(n), picks=picks)


# ----------------------------------------------------------------------------- 8 portfolio fit
def daily(trades, risk=0.01, w=1.0):
    d = pd.to_datetime(trades[:, 1].astype(np.int64), unit="s").normalize()
    s = pd.Series(risk * w * trades[:, 3], index=d).groupby(level=0).sum()
    return s.reindex(pd.date_range("2011-01-03", "2025-12-31", freq="B"), fill_value=0.0)


def book_daily():
    import ns_portfolio as PF
    T, _ = PF.build("BOOK")
    d = pd.to_datetime(T["t_out"], unit="s").normalize()
    s = pd.Series(0.01 * T["w"] * T["r"], index=d).groupby(level=0).sum()
    return s.reindex(pd.date_range("2011-01-03", "2025-12-31", freq="B"), fill_value=0.0)


def sharpe(x):
    return float(x.mean() / x.std() * 16) if x.std() > 0 else None


def portfolio_fit(cand_daily):
    b = book_daily(); j = pd.concat([b.rename("book"), cand_daily.rename("cand")], axis=1).fillna(0)
    iv = 1 / j["2011":"2016"].std(); w = iv / iv.sum(); mix = (j * w).sum(axis=1)
    return dict(corr_monthly=float(j.resample("ME").sum().corr().iloc[0, 1]), weights=w.round(3).to_dict(),
                book_sharpe=sharpe(j.book), cand_sharpe=sharpe(j.cand), combined_sharpe=sharpe(mix),
                book_sharpe_2017_on=sharpe(j.book["2017":]), combined_sharpe_2017_on=sharpe(mix["2017":]))


# ----------------------------------------------------------------------------- the protocol
def run(path, look=True, markets=None, procs=4):
    S = load_strategy(path)
    if markets:
        S.MARKETS = markets
    out = os.path.join(RES, S.NAME); os.makedirs(out, exist_ok=True)
    logp = os.path.join(out, "oos_log.json"); log = json.load(open(logp)) if os.path.exists(logp) else []
    if any(e["fingerprint"] != S.FINGERPRINT for e in log):
        raise SystemExit(f"{S.NAME}: the 2023-25 period was already looked at with a different version of this file. "
                         "Changing rules after seeing the final period is not allowed: give the new version a new NAME.")
    rec = dict(name=S.NAME, hypothesis=S.HYPOTHESIS, fingerprint=S.FINGERPRINT, started=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
               markets=S.MARKETS, timeframes=S.TIMEFRAMES, params=S.GRID, management=S.MANAGEMENT, time_stop=S.TIME_STOP)
    print(f"[0] {S.NAME}  fingerprint {S.FINGERPRINT[:12]}  markets {S.MARKETS}", flush=True)
    rec["priors"] = show_priors(S)
    M0 = market(S.MARKETS[0], S)
    ok, la = lookahead_check(S, M0); rec["lookahead"] = dict(ok=ok, checks=la)
    print(f"[1] look-ahead check: {'PASS' if ok else 'FAIL'}", flush=True)
    if not ok:
        rec["verdict"] = "Rejected: look-ahead (signals change when future bars are removed)"
        return finish(S, rec, out)
    t0 = time.time(); df = run_grid(S, procs); df.to_csv(os.path.join(out, "grid.csv.gz"), index=False)
    n_cfg = len(df) // len(S.MARKETS)
    print(f"[2] grid: {n_cfg} configurations x {len(S.MARKETS)} markets in {time.time() - t0:.0f}s", flush=True)
    P, per, R, need = pooled(S, df)
    R.reset_index().to_csv(os.path.join(out, "pooled.csv.gz"), index=False)
    rec["grid_summary"] = dict(configs=int(len(R)), passed_gate=int(R.gate.sum()), share_dev_positive=float((R.dev_E > 0).mean()),
                       median_dev_E=float(R.dev_E.median()), share_dev_and_val_positive=float(((R.dev_E > 0) & (R.val_E > 0)).mean()))
    print(f"[3] gate: {rec['grid_summary']['passed_gate']} of {len(R)} pass; {rec['grid_summary']['share_dev_positive']:.0%} positive in development", flush=True)
    if not R.gate.any():
        rec["verdict"] = "Rejected: no configuration passed the development gate"
        return finish(S, rec, out)
    G = R[R.gate].sort_values("dev_t", ascending=False); key = G.index[0]
    cfg = {k: jsonable(v) for k, v in zip(keycols(S), key)}
    nb = neighbours(S, key, R); nbt = [x["dev_t"] for x in nb]
    sel = dict(candidate=cfg, stats={k: jsonable(v) for k, v in R.loc[key].items() if k != "gate"}, neighbours=nb,
               neighbours_all_pos=bool(nb) and all(x["dev_E"] > 0 for x in nb), neighbours_median_t=float(np.median(nbt)) if nbt else None,
               walk_forward=walk_forward(S, P, per, need))
    rec["selection"] = sel
    print(f"    candidate {cfg}  dev E {sel['stats']['dev_E']:+.3f} t {sel['stats']['dev_t']:.2f}  val E {sel['stats']['val_E']:+.3f}", flush=True)
    # 4 confirmation
    p = {k: cfg[k] for k in ["tf"] + list(S.GRID)}
    base, strs, full = [], [], []
    for i, s in enumerate(S.MARKETS):
        M = market(s, S)
        b = run_config(S, M, p, cfg["tgt"], cfg["trail"], cfg["bias"]); base.append(np.c_[b, np.full(len(b), i)])
        strs.append(run_config(S, M, p, cfg["tgt"], cfg["trail"], cfg["bias"], cost_mult=1.5, swap_mult=2.0, delay=1))
        f = run_config(S, M, p, cfg["tgt"], cfg["trail"], cfg["bias"], cut=0); full.append(np.c_[f, np.full(len(f), i)])
    Bt = np.vstack(base); X = np.vstack(strs); F = np.vstack(full)
    yb = year_index(Bt[:, 0]); dev, val = yb <= 2019, (yb >= 2020) & (yb <= 2022)
    srt = (R.dev_t / np.sqrt(R.dev_n)).replace([np.inf, -np.inf], np.nan).dropna()
    conf = dict(dev=stats(Bt[dev, 3]), val=stats(Bt[val, 3]), stress_dev_val=stats(X[year_index(X[:, 0]) <= 2022, 3]),
                dsr=deflated_sharpe(Bt[dev, 3], srt.values, len(R)) if dev.sum() > 2 else None)
    rec["confirmation"] = conf
    print(f"[4] stress (costs x1.5, swaps x2, +1 min) 2011-22 E {conf['stress_dev_val'].get('E')}; deflated Sharpe {conf['dsr'] and round(conf['dsr']['dsr'], 3)}", flush=True)
    if not look:
        rec["verdict"] = "Stopped before the final look (--no-look)"
        return finish(S, rec, out)
    # 5 final look, logged once per fingerprint + configuration
    keyl = json.dumps(cfg, sort_keys=True)
    prior = [e for e in log if e["config"] == keyl]
    o = F[year_index(F[:, 0]) >= 2023]
    e = prior[0] if prior else dict(fingerprint=S.FINGERPRINT, config=keyl, time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                                     oos=stats(o[:, 3]), per_market={s: stats(o[o[:, 8] == i, 3]) for i, s in enumerate(S.MARKETS)})
    if not prior:
        log.append(e); json.dump(log, open(logp, "w"), indent=1, default=float)
    rec["final_look"] = e
    print(f"[5] 2023-25 (look logged {e['time']}): {e['oos']}", flush=True)
    t, crit = tier(sel, conf, e); rec["tier"] = t; rec["criteria"] = crit
    # 7 cost profile
    low = lambda Z: Z[:, 3] + 0.5 * Z[:, 5] + Z[:, 7]
    yf = year_index(F[:, 0])
    rec["low_cost_swap_free"] = {k: stats(low(F[m])) for k, m in (("dev", yf <= 2019), ("val", (yf >= 2020) & (yf <= 2022)), ("2023-25", yf >= 2023))}
    # 8 portfolio fit
    rec["portfolio_fit"] = portfolio_fit(daily(F))
    rec["verdict"] = {"A": "Tier A: deployment-ready candidate", "B": "Tier B: forward-test candidate"}.get(t, "Rejected")
    print(f"[6] verdict: {rec['verdict']}  {crit}", flush=True)
    if t in ("A", "B"):
        cols = ["t_in", "t_out", "side", "r", "dist", "cost_r", "nights", "fin_r", "market"]
        T = pd.DataFrame(F, columns=cols); T["market"] = [S.MARKETS[int(i)] for i in T.market]
        T["t_in"] = pd.to_datetime(T.t_in.astype(np.int64), unit="s"); T["t_out"] = pd.to_datetime(T.t_out.astype(np.int64), unit="s")
        T.to_csv(os.path.join(out, "parity_trades.csv"), index=False, float_format="%.6f")
    return finish(S, rec, out)


def show_priors(S):
    """What happened to earlier ideas of the same family (research/truth/memory/ledger.jsonl)."""
    fam = list(getattr(S, "FAMILY", []))
    if not fam:
        print("    priors: no FAMILY tags declared (add FAMILY = [...] to learn from earlier ideas)", flush=True)
        return []
    try:
        import memory
        hits = [e for e in memory.priors(fam) if e.get("name") != S.NAME]
    except Exception as ex:
        print(f"    priors: memory unavailable ({ex})", flush=True); return []
    surv = sum(memory.survived(e) for e in hits)
    print(f"    priors for {fam}: {len(hits)} earlier ideas, {surv} survived", flush=True)
    for e in hits[:8]:
        print(f"      - {e['name']}: {e['verdict']}", flush=True)
    return [dict(name=e["name"], verdict=e["verdict"]) for e in hits]


def finish(S, rec, out):
    json.dump(rec, open(os.path.join(out, "summary.json"), "w"), indent=1, default=float)
    try:                                                     # every run becomes memory
        import memory
        memory.record(memory.from_truth(S, rec))
        print("[10] memory: ledger + LESSONS.md updated (record what you learned in research/truth/memory/JOURNAL.md)", flush=True)
    except Exception as ex:
        print(f"[10] memory NOT updated: {ex}", flush=True)
    open(os.path.join(out, "REPORT.md"), "w").write(report_md(S, rec))
    if rec.get("tier") in ("A", "B"):
        open(os.path.join(out, "EA_SPEC.md"), "w").write(ea_spec_md(S, rec))
    print(f"[9] report: {os.path.relpath(os.path.join(out, 'REPORT.md'), os.path.join(ROOT, '..'))}", flush=True)
    return rec


def _f(x, nd=3):
    return "—" if x is None else (f"{x:+.{nd}f}" if isinstance(x, float) else str(x))


def report_md(S, r):
    L = [f"# Truth Lab report — {S.NAME}", "", f"**Verdict: {r.get('verdict')}**", "",
         f"Hypothesis: {S.HYPOTHESIS}", "",
         f"Fingerprint `{r['fingerprint'][:16]}` · started {r['started']} · markets {', '.join(r['markets'])} · "
         f"timeframes {', '.join(r['timeframes'])} · parameters {json.dumps(r.get('params', {}))} · management {json.dumps(r['management'])}", ""]
    la = r.get("lookahead", {})
    L += [f"1. Look-ahead check (real-time decisions + prefix invariance): **{'pass' if la.get('ok') else 'FAIL'}**."]
    g = r.get("grid_summary")
    if g:
        L += [f"2. Grid: {g['configs']} configurations; {g['share_dev_positive']:.0%} positive in development 2011–19, "
              f"{g['share_dev_and_val_positive']:.0%} positive in development and validation; median {g['median_dev_E']:+.3f}R per trade.",
              f"3. Development gate passed by {g['passed_gate']} configurations."]
    s = r.get("selection")
    if s and s.get("stats"):
        st = s["stats"]
        L += [f"   Candidate: `{json.dumps(s['candidate'])}`",
              f"   Development {st['dev_n']} trades, E {_f(st['dev_E'])}R, t {st['dev_t']:.2f} · validation E {_f(st['val_E'])}R · "
              f"walk-forward E {_f(s['walk_forward']['E'])}R · neighbours all positive: {s['neighbours_all_pos']} (median t {_f(s['neighbours_median_t'], 2)})"]
    c = r.get("confirmation")
    if c:
        L += [f"4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E {_f(c['stress_dev_val'].get('E'))}R · deflated Sharpe "
              f"{_f(c['dsr']['dsr'] if c.get('dsr') else None)} (chance the edge is real after {g['configs']} tries)."]
    fl = r.get("final_look")
    if fl:
        o = fl["oos"]
        L += [f"5. Final look 2023–25 (logged {fl['time']}): {o['n']} trades, E {_f(o.get('E'))}R, t {_f(o.get('t'), 2)}, PF {_f(o.get('PF'), 2)}; "
              "per market " + ", ".join(f"{k} {_f(v.get('E'))}" for k, v in fl["per_market"].items()) + ".",
              f"6. Criteria: " + ", ".join(f"{k} {'✔' if v else '✘'}" for k, v in r["criteria"].items()) + "."]
        lc = r["low_cost_swap_free"]
        L += [f"7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 {_f(lc['dev'].get('E'))}, 2020–22 {_f(lc['val'].get('E'))}, 2023–25 {_f(lc['2023-25'].get('E'))}R per trade."]
        pf = r["portfolio_fit"]
        L += [f"8. Portfolio fit: monthly correlation with the 11-leg book {pf['corr_monthly']:+.2f}; Sharpe book {_f(pf['book_sharpe'], 2)} → "
              f"book + this {_f(pf['combined_sharpe'], 2)} (2017 on: {_f(pf['book_sharpe_2017_on'], 2)} → {_f(pf['combined_sharpe_2017_on'], 2)})."]
    L += ["", "Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json."]
    return "\n".join(L) + "\n"


def ea_spec_md(S, r):
    c = r["selection"]["candidate"]
    return "\n".join([
        f"# EA specification — {S.NAME} ({r['verdict']})", "",
        f"Hypothesis: {S.HYPOTHESIS}", "", f"Signal rules: {getattr(S, 'RULES', S.signals.__doc__ or 'see the strategy file')}", "",
        f"Configuration: `{json.dumps(c)}` on {', '.join(S.MARKETS)}.",
        f"Management: target {c['tgt']}R (0 = none), chandelier trail {c['trail']} x ATR (0 = none), time stop {S.TIME_STOP} bars, "
        f"H4 EMA50 bias filter {'on' if c['bias'] else 'off'}; market entry at the next bar's open after the signal bar closes; "
        "no entries 20:30–23:00 UTC; one position per market.",
        "Build: copy mt5/TruthEA.mq5, implement Signal() from the rules above, set the inputs to this configuration.",
        f"Parity: run the Strategy Tester (real ticks) and compare its trade log with results/truth/{S.NAME}/parity_trades.csv using "
        "tools/parity_check.py; pass = >= 95% of trades matched (entry within one bar, same side) and R within 0.1.",
        "Then: demo per research/northstar/NORTHSTAR_REPORT.md §7, sized by the portfolio governor."]) + "\n"

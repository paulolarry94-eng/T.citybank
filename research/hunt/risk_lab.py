"""Hunt 2, step 6: risk systems compared at EQUAL drawdown risk.

Each policy sets the risk of every new trade as base x leg weight x m(state):
  fixed    m = 1
  voltgt   m = clip(target_vol / realised_vol, 0.5, 2.0); realised vol = EWMA (60-day half-life)
           of the account's daily closed-equity returns, annualised; m = 1 for the first 60 days
  ddbrake  m = 1 - (1 - floor) * min(1, drawdown / dd_full); floor 0.3, dd_full = the budget
  both     voltgt x ddbrake
  eqtrend  m = 1.3 when equity is above its 100-day average, else 0.7
A shared heat cap (total open risk) refuses trades beyond it. The base risk of each policy is
solved so that the MEDIAN maximum drawdown over 2,000 reshuffled 15-year histories equals the
budget; then returns are compared. Reshuffling moves whole calendar quarters of the real trade
record, so clustering inside a quarter is kept.
"""
import os, sys, json
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
os.chdir(os.path.join(HERE, ".."))

DAY = 86400
POLICIES = {"fixed": 0, "voltgt": 1, "ddbrake": 2, "both": 3, "eqtrend": 4}


def load_book(path="results/book_v3.json"):
    B = json.load(open(path))
    legs = []
    for k in B["kept"]:
        f = B["files"][k] if "files" in B else None
        legs.append((k, np.load(f), B["weights"][k]))
    return legs


def merge(legs):
    t_in = np.concatenate([l[1]["t_in"] for l in legs]).astype(np.int64)
    t_out = np.concatenate([l[1]["t_out"] for l in legs]).astype(np.int64)
    r = np.concatenate([l[1]["r"] for l in legs]).astype(np.float64)
    w = np.concatenate([np.full(len(l[1]), l[2]) for l in legs]).astype(np.float64)
    o = np.argsort(t_in, kind="stable")
    return t_in[o], t_out[o], r[o], w[o]


@njit(cache=True)
def sim(t_in, t_out, r, w, base, policy, heat_cap, dd_full, floor, vol_target, out_daily, trade_cap=1.0):
    """Returns (final equity multiple, max drawdown, years, n_blocked). If out_daily has
    length > 0 it receives end-of-day equity for each calendar day from the first entry."""
    n = len(r)
    ev_t = np.empty(2 * n, np.int64); ev_i = np.empty(2 * n, np.int64); ev_e = np.empty(2 * n, np.int64)
    for i in range(n):
        ev_t[2 * i] = t_in[i]; ev_i[2 * i] = i; ev_e[2 * i] = 1
        ev_t[2 * i + 1] = t_out[i]; ev_i[2 * i + 1] = i; ev_e[2 * i + 1] = 0
    order = np.argsort(ev_t * 2 + ev_e, kind="mergesort")      # exits before entries at equal times
    eq = 1.0; peak = 1.0; mdd = 0.0
    amt = np.zeros(n); pct = np.zeros(n); taken = np.zeros(n, np.bool_)
    heat = 0.0; blocked = 0
    day0 = ev_t[order[0]] // 86400; cur = day0; eq_day = 1.0
    lam = 0.5 ** (1.0 / 60.0); var = 0.0; ndays = 0
    ema = 1.0; a_ema = 2.0 / 101.0
    for q in range(2 * n):
        j = order[q]; t = ev_t[j]; i = ev_i[j]; d = t // 86400
        while cur < d:                                   # close out calendar days
            ret = eq / eq_day - 1.0
            wd = (cur + 3) % 7
            if wd < 5:
                var = lam * var + (1 - lam) * ret * ret; ndays += 1
                ema = ema + a_ema * (eq - ema)
            if len(out_daily) > 0 and cur - day0 < len(out_daily):
                out_daily[cur - day0] = eq
            eq_day = eq; cur += 1
        if ev_e[j] == 1:
            m = 1.0
            if policy == 1 or policy == 3:
                if ndays > 60 and var > 0:
                    v = np.sqrt(var * 252.0)
                    m = min(2.0, max(0.5, vol_target / v))
            if policy == 2 or policy == 3:
                dd = 1.0 - eq / peak
                m *= 1.0 - (1.0 - floor) * min(1.0, dd / dd_full)
            if policy == 4 and ndays > 100:
                m = 1.3 if eq > ema else 0.7
            p = min(base * w[i] * m, trade_cap)
            if heat + p > heat_cap + 1e-12:
                blocked += 1
                continue
            taken[i] = True; pct[i] = p; amt[i] = eq * p; heat += p
        else:
            if not taken[i]:
                continue
            heat -= pct[i]
            eq += amt[i] * r[i]
            if eq > peak:
                peak = eq
            dd = 1.0 - eq / peak
            if dd > mdd:
                mdd = dd
            if eq <= 0.0:
                return 0.0, 1.0, (t - ev_t[order[0]]) / (365.25 * 86400.0), blocked
    if len(out_daily) > 0:
        k = cur - day0
        while k < len(out_daily):
            out_daily[k] = eq; k += 1
    years = (ev_t[order[2 * n - 1]] - ev_t[order[0]]) / (365.25 * 86400.0)
    return eq, mdd, years, blocked


def reshuffle(legs, rng, block_days=91):
    t0 = min(int(l[1]["t_in"].min()) for l in legs)
    t1 = max(int(l[1]["t_out"].max()) for l in legs)
    B = block_days * DAY
    nblk = int((t1 - t0) // B) + 1
    pick = rng.integers(0, nblk, nblk)
    T_in, T_out, R, W = [], [], [], []
    for _, tr, w in legs:
        k = (tr["t_in"] - t0) // B
        for j, src in enumerate(pick):
            sel = k == src
            if sel.any():
                shift = (j - src) * B
                T_in.append(tr["t_in"][sel] + shift); T_out.append(tr["t_out"][sel] + shift)
                R.append(tr["r"][sel]); W.append(np.full(sel.sum(), w))
    t_in = np.concatenate(T_in).astype(np.int64); o = np.argsort(t_in, kind="stable")
    return t_in[o], np.concatenate(T_out).astype(np.int64)[o], np.concatenate(R)[o], np.concatenate(W)[o]


class Paths:
    def __init__(self, legs, n=2000, seed=11):
        rng = np.random.default_rng(seed)
        self.real = merge(legs)
        self.paths = [reshuffle(legs, rng) for _ in range(n)]

    def run(self, base, policy, heat_cap=0.20, dd_full=0.20, floor=0.3, vol_target=0.15, trade_cap=1.0):
        empty = np.zeros(0)
        P = POLICIES[policy]
        res = np.array([sim(*p, base, P, heat_cap, dd_full, floor, vol_target, empty, trade_cap) for p in self.paths])
        eq, mdd, yrs = res[:, 0], res[:, 1], res[:, 2]
        cagr = np.where(eq > 0, eq ** (1 / yrs) - 1, -1.0)
        real = sim(*self.real, base, P, heat_cap, dd_full, floor, vol_target, empty, trade_cap)
        return dict(base=base, cagr_med=float(np.median(cagr)), cagr_p5=float(np.percentile(cagr, 5)),
                    dd_med=float(np.median(mdd)), dd_p95=float(np.percentile(mdd, 95)), dd_worst=float(mdd.max()),
                    p_dd40=float((mdd > 0.40).mean()), real_cagr=float(real[0] ** (1 / real[2]) - 1), real_dd=float(real[1]))

    def solve(self, policy, budget, **kw):
        lo, hi = 0.002, 0.60
        for _ in range(18):
            mid = (lo + hi) / 2
            if self.run(mid, policy, **kw)["dd_med"] > budget:
                hi = mid
            else:
                lo = mid
        return self.run(lo, policy, **kw)


if __name__ == "__main__":
    legs = load_book()
    P = Paths(legs, n=int(os.environ.get("NPATHS", "1000")))
    out = {}
    for budget in (0.15, 0.25, 0.35):
        print(f"\nmedian drawdown budget {budget:.0%} (heat cap 20%)")
        print(f"  {'policy':8s} {'base':>6s} {'CAGR med':>9s} {'CAGR p5':>8s} {'DD med':>7s} {'DD p95':>7s} {'DD worst':>8s} {'P(DD>40%)':>9s} {'real CAGR':>9s} {'real DD':>7s}")
        for pol in POLICIES:
            kw = dict(dd_full=budget) if pol in ("ddbrake", "both") else {}
            r = P.solve(pol, budget, **kw)
            out[f"{pol}@{budget}"] = r
            print(f"  {pol:8s} {r['base']:6.2%} {r['cagr_med']:9.1%} {r['cagr_p5']:8.1%} {r['dd_med']:7.1%} {r['dd_p95']:7.1%} "
                  f"{r['dd_worst']:8.1%} {r['p_dd40']:9.1%} {r['real_cagr']:9.1%} {r['real_dd']:7.1%}", flush=True)
    json.dump(out, open("results/risk_lab.json", "w"), indent=1)

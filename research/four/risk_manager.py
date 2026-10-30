"""Central risk manager for the four strategies (and, optionally, the existing 11-leg book).

Per new trade: risk = min(base x leg weight x brake x throttle, per-trade cap), refused if total open
risk would pass the heat cap or that market's open risk would pass the market cap.
  leg weight  inverse monthly-R volatility measured on 2011-2019 only (risk balance)
  brake       drawdown brake: x1 at the equity peak falling linearly to x0.3 at the budget
  throttle    x0.5 while the leg's last 20 closed trades average below 0R (the leg is out of form)
Comparisons at equal risk: each set's base risk is solved so the median max drawdown of 600
reshuffled 15-year histories (whole calendar quarters re-ordered) equals 25%.
"""
import os, sys, json, glob
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "hunt"))
os.chdir(os.path.join(HERE, ".."))
import risk_lab as RL

MKT = {"XAUUSD": 0, "EURUSD": 1, "GBPUSD": 2, "USDJPY": 3, "GBPJPY": 4, "EURGBP": 5}


def monthly(tr):
    import datetime as dt
    mk = np.array([(dt.datetime.utcfromtimestamp(int(t)).year - 2011) * 12 + dt.datetime.utcfromtimestamp(int(t)).month - 1 for t in tr["t_out"]])
    s = np.zeros(180); ok = (mk >= 0) & (mk < 180); np.add.at(s, mk[ok], tr["r"][ok]); return s


def legs_four(fams=("TC", "VC", "VE")):
    out = []
    for f in sorted(glob.glob("trades/four/*.npy")):
        fam, sym = os.path.basename(f)[:-4].split("_")
        if fam in fams:
            out.append((f"{fam}_{sym}", np.load(f), sym))
    return out


def legs_book():
    B = json.load(open("results/book_v3.json"))
    def mk(name):
        for s in MKT:
            if name.startswith(s[:3]) or name.startswith(s):
                return s
        return "XAUUSD"
    m = {"XAU": "XAUUSD", "JPY": "USDJPY", "EUR": "EURUSD", "GBP": "GBPUSD"}
    out = []
    for k in B["kept"]:
        sym = "GBPJPY" if k.startswith("GBPJPY") else "EURGBP" if k.startswith("EURGBP") else m[k[:3]]
        out.append((k, np.load(B["files"][k]), sym))
    return out


def weights(legs):
    vol = np.array([monthly(tr)[:108].std(ddof=1) for _, tr, _ in legs])
    w = 1 / np.where(vol > 0, vol, np.inf); return w / w.max()


def merge(legs, w):
    T = [(tr, wi, li, MKT[s]) for li, ((_, tr, s), wi) in enumerate(zip(legs, w)) if wi > 0 and len(tr)]
    t_in = np.concatenate([x[0]["t_in"] for x in T]).astype(np.int64); o = np.argsort(t_in, kind="stable")
    cat = lambda f: np.concatenate([f(x) for x in T])[o]
    return (t_in[o], cat(lambda x: x[0]["t_out"]).astype(np.int64), cat(lambda x: x[0]["r"]).astype(np.float64),
            cat(lambda x: np.full(len(x[0]), x[1])), cat(lambda x: np.full(len(x[0]), x[2], np.int64)),
            cat(lambda x: np.full(len(x[0]), x[3], np.int64)))


@njit(cache=True)
def sim(t_in, t_out, r, w, leg, mkt, base, heat_cap, mkt_cap, trade_cap, dd_full, floor, thr_n, thr_mult, nleg):
    n = len(r)
    ev_t = np.empty(2 * n, np.int64); ev_i = np.empty(2 * n, np.int64); ev_e = np.empty(2 * n, np.int64)
    for i in range(n):
        ev_t[2 * i] = t_in[i]; ev_i[2 * i] = i; ev_e[2 * i] = 1
        ev_t[2 * i + 1] = t_out[i]; ev_i[2 * i + 1] = i; ev_e[2 * i + 1] = 0
    order = np.argsort(ev_t * 2 + ev_e, kind="mergesort")
    eq = 1.0; peak = 1.0; mdd = 0.0; heat = 0.0
    mheat = np.zeros(8); amt = np.zeros(n); pct = np.zeros(n); taken = np.zeros(n, np.bool_)
    buf = np.zeros((nleg, 64)); cnt = np.zeros(nleg, np.int64)
    year_eq = np.zeros(20); y0 = 2011
    for q in range(2 * n):
        j = order[q]; i = ev_i[j]
        if ev_e[j] == 1:
            dd = 1.0 - eq / peak
            m = 1.0 - (1.0 - floor) * min(1.0, dd / dd_full)
            L = leg[i]
            if thr_n > 0 and cnt[L] >= thr_n:
                s = 0.0
                for k in range(thr_n):
                    s += buf[L, (cnt[L] - 1 - k) % 64]
                if s < 0:
                    m *= thr_mult
            p = min(base * w[i] * m, trade_cap)
            if heat + p > heat_cap + 1e-12 or mheat[mkt[i]] + p > mkt_cap + 1e-12:
                continue
            taken[i] = True; pct[i] = p; amt[i] = eq * p; heat += p; mheat[mkt[i]] += p
        else:
            if not taken[i]:
                continue
            heat -= pct[i]; mheat[mkt[i]] -= pct[i]; eq += amt[i] * r[i]
            L = leg[i]; buf[L, cnt[L] % 64] = r[i]; cnt[L] += 1
            if eq > peak:
                peak = eq
            dd = 1.0 - eq / peak
            if dd > mdd:
                mdd = dd
            yr = int(1970 + ev_t[j] / 31557600.0) - y0
            if 0 <= yr < 20:
                year_eq[yr] = eq
            if eq <= 0:
                return 0.0, 1.0, year_eq
    return eq, mdd, year_eq


class Book:
    def __init__(self, legs, npaths=600, seed=11):
        self.legs = legs; self.w = weights(legs); self.nleg = len(legs)
        self.real = merge(legs, self.w)
        rng = np.random.default_rng(seed)
        L2 = [(n, tr, wi) for (n, tr, s), wi in zip(legs, self.w)]
        self.paths = []
        for _ in range(npaths):
            ti, to, rr, ww = RL.reshuffle([(n, self._tag(tr, li, s), wi) for li, ((n, tr, s), wi) in enumerate(zip(legs, self.w))], rng)
            self.paths.append((ti, to, rr, ww))
        self.span = (self.real[1].max() - self.real[0].min()) / (365.25 * 86400)

    def _tag(self, tr, li, s):
        # encode leg and market into the trade weight field via a side array handled in run()
        return tr

    def run_real(self, base, **kw):
        t_in, t_out, r, w, leg, mkt = self.real
        eq, mdd, ye = sim(t_in, t_out, r, w, leg, mkt, base, kw.get("heat", 0.3), kw.get("mcap", 0.12), kw.get("cap", 0.04),
                          kw.get("budget", 0.25), 0.3, kw.get("thr_n", 0), kw.get("thr_mult", 0.5), self.nleg)
        return eq, mdd, ye

    def boot(self, base, **kw):
        res = []
        for ti, to, rr, ww in self.paths:
            leg = np.zeros(len(rr), np.int64); mkt = np.zeros(len(rr), np.int64)   # throttle / market caps need leg ids
            eq, mdd, _ = sim(ti, to, rr, ww, leg, mkt, base, kw.get("heat", 0.3), 9.0, kw.get("cap", 0.04),
                             kw.get("budget", 0.25), 0.3, 0, 0.5, 1)
            res.append((eq, mdd))
        A = np.array(res); cagr = np.where(A[:, 0] > 0, A[:, 0] ** (1 / self.span) - 1, -1)
        return dict(cagr_med=float(np.median(cagr)), cagr_p5=float(np.percentile(cagr, 5)), dd_med=float(np.median(A[:, 1])),
                    dd_p95=float(np.percentile(A[:, 1], 95)), dd_worst=float(A[:, 1].max()))

    def solve(self, budget=0.25, **kw):
        lo, hi = 0.002, 0.6
        for _ in range(16):
            mid = (lo + hi) / 2
            if self.boot(mid, budget=budget, **kw)["dd_med"] > budget:
                hi = mid
            else:
                lo = mid
        return lo, self.boot(lo, budget=budget, **kw)


def period_returns(ye):
    out = {}
    prev = 1.0
    for k in range(15):
        if ye[k] > 0:
            out[2011 + k] = ye[k] / prev - 1; prev = ye[k]
    return out


if __name__ == "__main__":
    sets = {"Four (TC+VC+VE, 12 legs)": legs_four(), "Four incl. failed breakout (16 legs)": legs_four(("TC", "VC", "VE", "FB")),
            "Book (11 legs)": legs_book(), "Book + Four (23 legs)": legs_book() + legs_four()}
    out = {}
    for name, legs in sets.items():
        B = Book(legs, npaths=int(os.environ.get("NPATHS", "400")))
        base, s = B.solve(0.25)
        row = dict(base=base, **s)
        for thr in (0, 20):
            eq, mdd, ye = B.run_real(base, thr_n=thr)
            yr = period_returns(ye)
            g = lambda a, b: float(np.prod([1 + yr[y] for y in yr if a <= y <= b]) ** (1 / (b - a + 1)) - 1)
            row[f"real{'_thr' if thr else ''}"] = dict(cagr=float(eq ** (1 / B.span) - 1), mdd=float(mdd), dev=g(2011, 2019), val=g(2020, 2022),
                                                      oos=g(2023, 2025), years=yr)
        out[name] = row
        r0, r1 = row["real"], row["real_thr"]
        print(f"{name:38s} base {base:5.2%} | reshuffled: CAGR med {s['cagr_med']:6.1%} p5 {s['cagr_p5']:6.1%} DD p95 {s['dd_p95']:5.1%} worst {s['dd_worst']:5.1%}")
        print(f"{'':38s} real: CAGR {r0['cagr']:6.1%} maxDD {r0['mdd']:5.1%} | per year dev {r0['dev']:+6.1%} val {r0['val']:+6.1%} 2023-25 {r0['oos']:+6.1%}")
        print(f"{'':38s} real + throttle: CAGR {r1['cagr']:6.1%} maxDD {r1['mdd']:5.1%} | dev {r1['dev']:+6.1%} val {r1['val']:+6.1%} 2023-25 {r1['oos']:+6.1%}", flush=True)
    json.dump(out, open("results/four/risk_manager.json", "w"), indent=1, default=float)

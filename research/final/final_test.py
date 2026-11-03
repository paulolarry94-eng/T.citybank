"""Final test of the best 4-flip variant with and without the H4 50-EMA trend filter (research/final/PREREGISTRATION.md).

    python3 research/final/final_test.py     # writes research/results/final/final_look.json and FINAL.md

ONE logged look at 2023-25 (the lab made none: no configuration passed its gate) plus Jan-Oct 2026 on the five markets with
2026 data. Same strategy file as the lab run (ema4_final_v1, fingerprint recorded). Costs RoboForex Prime published.
"""
import os, sys, json, math, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, os.path.join(ROOT, "research", "owner330"))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, os.path.join(ROOT, "research", "northstar"))
import protocol as P        # noqa: E402
import cyclegoal as G       # noqa: E402
import replay               # noqa: E402  (Market2026)
import engine as E          # noqa: E402
from grid import year_index  # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "ema4_final_v1.py"))
CFG = dict(tf="H4", entry="close", stop="c4", buffer=0.25, target=2, grade="AB")
FIVE = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP"]
T2026 = int(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp())
OUT = os.path.join(ROOT, "research", "results", "final")


class M26(replay.Market2026):
    """2025-26 minutes with the lab's bar construction (H4 offset, ATR) so the strategy runs unchanged."""
    def bars(self, tf):
        m = {"M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240}[tf]
        if tf not in self._b:
            bt, bo, bh, bl, bc, nxt = E.resample(self.ts, self.o, self.h, self.l, self.G.c, m, 120 if m >= 240 else 0)
            nxt = nxt.astype(np.int64)
            B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt, first=np.r_[0, nxt[:-1]].astype(np.int64), minutes=m)
            B["atr"] = np.nan_to_num(E.atr_sma(bh, bl, bc, 14), nan=0.0)
            self._b[tf] = B
        return self._b[tf]


def st(R):
    R = np.asarray(R, float)
    if len(R) < 3:
        return dict(n=int(len(R)), E=round(float(R.mean()), 4) if len(R) else None)
    sd = R.std(ddof=1)
    return dict(n=int(len(R)), E=round(float(R.mean()), 4), t=round(float(R.mean() / sd * math.sqrt(len(R))), 2),
                win=round(float((R > 0).mean()), 3), sum_R=round(float(R.sum()), 1))


def main():
    out = dict(note=__doc__, fingerprint=S.FINGERPRINT, looked_at_utc=dt.datetime.utcnow().isoformat(timespec="seconds"), configs={})
    for trend in (0, 1):
        p = dict(CFG, trend=trend); allT = []; per_m = {}
        for i, s in enumerate(S.MARKETS):
            M = P.market(s, S); B = M.bars("H4"); S._CACHE.clear()
            D = S.detail(M, B, p, cut=0)                      # cut=0: every fill, 2011-2025 (the look)
            allT.append(np.c_[D[:, [0, 3]], np.full(len(D), i)])
        T = np.vstack(allT); T = T[np.argsort(T[:, 0], kind="stable")]; y = year_index(T[:, 0])
        res = {}
        for per, m in (("2011-19", y <= 2019), ("2020-22", (y >= 2020) & (y <= 2022)), ("2023-25", (y >= 2023) & (y <= 2025))):
            res[per] = dict(all=st(T[m, 1]), by_market={s: st(T[m & (T[:, 2] == i), 1]) for i, s in enumerate(S.MARKETS)},
                            cycle=G.score(T[m, 1], T[m, 0]))
            res[per]["by_year"] = {int(yy): st(T[m & (y == yy), 1]) for yy in sorted(set(y[m].tolist()))}
        parts = []
        for i, s in enumerate(FIVE):
            M = M26(s, S.COSTS[s]); S._CACHE.clear()
            D = S.detail(M, M.bars("H4"), p); D = D[D[:, 0] >= T2026]
            parts.append(np.c_[D[:, [0, 3]], np.full(len(D), i)])
        X = np.vstack(parts)
        res["2026 (5 markets)"] = dict(all=st(X[:, 1]), by_market={s: st(X[X[:, 2] == i, 1]) for i, s in enumerate(FIVE)})
        out["configs"]["with trend filter" if trend else "without filter"] = res
        print("trend", trend, {k: v["all"] for k, v in res.items()}, flush=True)
    f = out["configs"]["with trend filter"]; a = f["2023-25"]["all"]; b = f["2026 (5 markets)"]["all"]
    if (a.get("E") or 0) > 0 and (a.get("t") or 0) >= 2 and (b.get("E") or 0) > 0:
        verdict = "WORKS (forward-test candidate)"
    elif (a.get("E") or 0) > 0:
        verdict = "NOT PROVEN (positive in 2023-25 but t < 2" + ("" if (b.get("E") or 0) > 0 else "; 2026 negative") + ")"
    else:
        verdict = "FAILS (2023-25 not positive)"
    out["verdict"] = verdict; print("VERDICT:", verdict)
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "final_look.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()

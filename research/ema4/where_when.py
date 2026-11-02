"""Where and when does the 4-flip pattern work? Pre-registered learn-then-check search (research/ema4/PREREGISTRATION.md).

    python3 research/ema4/where_when.py      # writes research/results/ema4/where_when.json and WHERE_WHEN.md

Cells = market x timeframe x session of the 4th candle's close (Asia 23-07, London 07-12, New York 12-20:30 UTC).
LEARN (2011-19): per cell, the trade setting (entry x stop x buffer x target x grade = 128) with the highest t after costs
among those with >= 100 trades. CHECK (2020-22, untouched by the choice): same setting, mean R > 0 and t >= 2 (>= 30 trades).
Fills before 2023 only; the 2023-25 holdout is not opened here.
"""
import os, sys, json, itertools, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P             # noqa: E402
from grid import year_index      # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "ema4_flip_v1.py"))
SESS = {"Asia": (23, 7), "London": (7, 12), "NewYork": (12, 20.5)}
OUT = os.path.join(ROOT, "research", "results", "ema4")


def session(t):
    h = (np.asarray(t, np.int64) % 86400) / 3600.0
    s = np.full(len(h), "", object)
    s[(h >= 23) | (h < 7)] = "Asia"; s[(h >= 7) & (h < 12)] = "London"; s[(h >= 12) & (h < 20.5)] = "NewYork"
    return s


def tstat(x):
    x = np.asarray(x, float)
    if len(x) < 3 or x.std(ddof=1) == 0:
        return None
    return float(x.mean() / x.std(ddof=1) * math.sqrt(len(x)))


def main():
    names = list(S.GRID)
    settings = [dict(zip(names, v)) for v in itertools.product(*[S.GRID[k] for k in names])]
    cells = {}
    hours = {}
    for sym in S.MARKETS:
        M = P.market(sym, S)
        for tf in S.TIMEFRAMES:
            B = M.bars(tf)
            for st in settings:
                p = dict(tf=tf, **st)
                D = S.detail(M, B, p, cut=P.core.CUT)
                if not len(D):
                    continue
                Sx = S.select(S.setups(B, p, M), p)
                t4 = Sx["t4"][D[:, 13].astype(int)]
                y = year_index(D[:, 0]); ss = session(t4)
                key_s = json.dumps(st, sort_keys=True)
                for sname in SESS:
                    m = ss == sname
                    cells.setdefault((sym, tf, sname), {})[key_s] = dict(dev=D[m & (y <= 2019), 3], val=D[m & (y >= 2020) & (y <= 2022), 3])
            print(sym, tf, flush=True)
    rows = []
    for (sym, tf, sname), byset in cells.items():
        cand = [(tstat(v["dev"]), k, v) for k, v in byset.items() if len(v["dev"]) >= 100 and tstat(v["dev"]) is not None]
        if not cand:
            rows.append(dict(market=sym, tf=tf, session=sname, learn=None)); continue
        t, k, v = max(cand, key=lambda x: x[0])
        tv = tstat(v["val"])
        rows.append(dict(market=sym, tf=tf, session=sname, setting=json.loads(k), learn_n=len(v["dev"]), learn_E=round(float(v["dev"].mean()), 4),
                         learn_t=round(t, 2), check_n=len(v["val"]), check_E=round(float(v["val"].mean()), 4) if len(v["val"]) else None,
                         check_t=round(tv, 2) if tv is not None else None,
                         passed=bool(t >= 3 and len(v["val"]) >= 30 and v["val"].mean() > 0 and (tv or 0) >= 2),
                         settings_tried=len(cand)))
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(note=__doc__, rows=rows), open(os.path.join(OUT, "where_when.json"), "w"), indent=1, default=float)
    open(os.path.join(OUT, "WHERE_WHEN.md"), "w").write(markdown(rows))


def markdown(rows):
    r = [x for x in rows if x.get("learn_t") is not None]
    a = [x for x in r if x["learn_t"] >= 3]; b = [x for x in r if x.get("passed")]
    L = ["# 4-flip pattern: where and when (learn 2011-19, check 2020-22)", "",
         f"Cells: {len(rows)} (12 markets x 5 timeframes x 3 sessions); with enough trades: {len(r)}; best setting t >= 3 in "
         f"2011-19: {len(a)}; also positive with t >= 2 in 2020-22 (PASS): {len(b)}. Each cell's best of up to 128 settings was "
         "chosen on 2011-19, so its learn t is inflated by the choice; the 2020-22 check is untouched.", "",
         "| Market | TF | Session | Best setting (2011-19) | Trades | R/trade | t | 2020-22 trades | R/trade | t | Pass |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(r, key=lambda x: -x["learn_t"]):
        st = x["setting"]
        L.append(f"| {x['market']} | {x['tf']} | {x['session']} | {st['entry']} {st['stop']}+{st['buffer']} {st['target']}R {st['grade']} | "
                 f"{x['learn_n']} | {x['learn_E']:+.3f} | {x['learn_t']:+.2f} | {x['check_n']} | "
                 f"{(x['check_E'] if x['check_E'] is not None else float('nan')):+.3f} | {x['check_t']} | {'PASS' if x['passed'] else ''} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()

"""The same trades with zero costs and zero swaps (spread, commission, slippage = 0): is there any edge BEFORE costs?
Every configuration, 12 markets, 2011-19 and 2020-22 (fills before 2023).
    python3 research/body4/gross.py  ->  research/results/body4/gross.json
"""
import os, sys, json, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

NAME = next((a for a in sys.argv[1:] if a.startswith("body4_")), "body4_range_v1")
S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", f"{NAME}.py"))
SUB = "" if NAME == "body4_range_v1" else NAME.split("_")[-1]
Y20 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())
ZERO = dict(spread=0.0, commission=0.0, slippage=0.0)


def main():
    acc = {}
    for sym in S.MARKETS:
        M = P.market(sym, S)
        S.SPLIT[sym] = dict(ZERO)
        for tf in S.TIMEFRAMES:
            B = M.bars(tf)
            for v in itertools.product(*S.GRID.values()):
                c = dict(zip(S.GRID, v))
                D = S.detail(M, B, dict(c, tf=tf), cut=P.core.CUT, swap=0.0)
                k = f"{tf} | " + (f"target {c['target']}R | " if "target" in c else "") + f"entry {int(c['entry'] * 100)}% | be {'on' if c['be'] else 'off'} | buffer {int(c['buffer'] * 100)}% | lookback {'on' if c['lookback'] else 'off'}"
                for per, m in (("2011-19", D[:, 0] < Y20), ("2020-22", D[:, 0] >= Y20)):
                    a = acc.setdefault(k, {}).setdefault(per, [0, 0.0, 0.0, 0])
                    a[0] += int(m.sum()); a[1] += float(D[m, 3].sum()); a[2] += float((D[m, 3] ** 2).sum())
                    a[3] += int(m.sum() > 0 and D[m, 3].mean() > 0)
        print(sym, flush=True)
    out = {}
    for k, d in acc.items():
        out[k] = {}
        for per, (n, s, ss, mk) in d.items():
            E = s / n if n else None
            sd = np.sqrt(max(ss / n - E * E, 0)) if n else None
            out[k][per] = dict(n=n, E=round(E, 4) if E is not None else None,
                               t=round(E / sd * np.sqrt(n), 2) if n and sd else None, markets_positive=mk)
    d = os.path.join(ROOT, "research", "results", "body4", SUB) if SUB else os.path.join(ROOT, "research", "results", "body4")
    os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, "gross.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    o = main()
    for k in sorted(o, key=lambda x: -(o[x]["2011-19"]["E"] or -9))[:12]:
        print(k, o[k])

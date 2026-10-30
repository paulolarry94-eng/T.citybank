"""Full FVG grid on four markets; only fills before 2023-01-01 (2023-2025 reserved)."""
import os, sys, time, itertools, gzip, csv
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "four"))
import fvg_lab as F
from runner import aggregate

SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
CUT = 1672531200


def configs():
    for tf in ("M15", "H1", "H4"):
        kills = (False, True) if tf == "M15" else (False,)
        for disp, g, bias, kill in itertools.product((0.0, 1.0, 1.5), (0.1, 0.3), (False, True), kills):
            for mode in ("edge", "ce"):
                for stop in ("origin", "gap"):
                    for tgt, tr in itertools.product((1.5, 2.0, 3.0, 0.0), (0.0, 3.0)):
                        yield (tf, mode, disp, g, stop, tgt, tr, bias, kill)
            for tgt, tr in itertools.product((1.5, 2.0, 3.0, 0.0), (0.0, 3.0)):
                yield (tf, "ifvg", disp, g, "gap", tgt, tr, bias, kill)
            yield (tf, "fade", disp, g, "gap", 0.0, 0.0, bias, kill)


def work(sym):
    L = F.Lab(sym); rows = []; t0 = time.time()
    for tf, mode, disp, g, stop, tgt, tr, bias, kill in configs():
        res = L.run(tf, mode, disp, g, stop, tgt, tr, bias=bias, kill=kill, cut=CUT)
        row = dict(sym=sym, tf=tf, mode=mode, disp=disp, gmin=g, stop=stop, tgt=tgt, trail=tr, bias=int(bias), kill=int(kill))
        row.update(aggregate(res)); rows.append(row)
    print(f"  {sym}: {len(rows)} runs {time.time() - t0:.0f}s", flush=True)
    return rows


if __name__ == "__main__":
    with Pool(4) as p:
        parts = p.map(work, SYMS)
    rows = [r for p in parts for r in p]
    os.makedirs(os.path.join(HERE, "..", "results", "fvg"), exist_ok=True)
    with gzip.open(os.path.join(HERE, "..", "results", "fvg", "grid.csv.gz"), "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    print(len(rows), "runs logged")

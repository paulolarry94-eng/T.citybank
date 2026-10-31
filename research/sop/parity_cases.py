"""Does the coded 4-leg SOP (research/truth/strategies/sop_4leg_v1.py) find the owner's own case-study setups?

For each case (times converted from the owner's UTC+1 charts to UTC) the detector runs on that market and timeframe
(any hour; swing sizes 3, 4, 5; perfect or slow engulfings) and lists the setups whose decision falls in the 18 hours
before the case time, with their entry, stop and what happened next (bracket at 2R, with and without breakeven).
Data: 2025 from data/ (lab data), 2026 from data/holdout/ (Exness Zero ticks -> M1).
Output: research/results/sop/parity_cases.json and a printed table.
"""
import os, sys, json
import datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, p)
import engine as E
import sop_4leg_v1 as S

DATA = os.path.join(R, "..", "data")
OUT = os.path.join(R, "results", "sop"); os.makedirs(OUT, exist_ok=True)
CASES = [  # id, symbol, tf minutes, owner time (UTC+1), side, owner outcome, owner notes
    ("EU#1", "EURUSD", 30, "2026-01-07 16:00", -1, "win", "A+, perfect/perfect, 15 candles, 30% (doc says 26 Jan; chart prices = 7 Jan)"),
    ("EU#2", "EURUSD", 30, "2025-11-11 07:30", 1, "win", "A+, perfect/perfect, 30%"),
    ("EU#3", "EURUSD", 30, "2025-10-29 16:30", -1, "win", "A, slow/perfect, 70%"),
    ("EU#4", "EURUSD", 30, "2025-10-22 17:30", -1, "rejected (EMA not aligned)", "would have sold"),
    ("GU#1", "GBPUSD", 30, "2026-01-29 16:00", 1, "loss (wick 8 pips), then TP", "A+, 70%"),
    ("#6", "EURUSD", 5, "2026-01-15 17:05", 1, "win", "A, perfect/slow, 14 candles, 30%"),
    ("#7", "EURUSD", 15, "2026-01-05 16:30", -1, "loss", "A+, 12 candles, 30% (doc says GU 29 Jan; chart = EUR/USD 5 Jan)"),
    ("#8", "EURUSD", 15, "2026-01-02 12:00", -1, "rejected (40 candles > 30)", "doc says 30 Jan; chart = 31 Dec-2 Jan"),
    ("#9", "GBPUSD", 5, "2026-01-20 15:00", 1, "win", "A+, perfect/perfect, 9 candles, 70%"),
    ("#10", "EURUSD", 15, "2025-12-15 15:00", 1, "win", "A+, slow/perfect, 20 candles, 30% (doc says 29 Jan; chart = 15 Dec)"),
    ("#10b", "EURUSD", 15, "2026-01-23 15:00", 1, "win", "alternative date for #10 (also fits the chart prices)"),
    ("doc1", "EURUSD", 5, "2026-01-30 19:50", -1, "rejected (outside time)", "A, perfect/slow, 20 candles"),
    ("doc2", "EURUSD", 5, "2026-01-29 14:30", -1, "hesitated", "A, slow/slow, 27 candles"),
]


def load(sym, year):
    f = os.path.join(DATA, f"{sym}_M1_bid_{year}.npz") if year <= 2025 else os.path.join(DATA, "holdout", f"{sym}_M1_bid_{year}.npz")
    d = np.load(f)
    return (d["ts"] // 1000).astype(np.int64), d["o"], d["h"], d["l"], d["c"]


def outcome(ts, o, h, l, c, i0, side, entry, stop, be, cost, spread=0.0):
    """Fill the limit from minute i0 within the order's life, then manage at 2R; returns (fill time, R)."""
    d = abs(entry - stop)
    for i in range(i0, len(ts)):
        if (side > 0 and l[i] + spread <= entry) or (side < 0 and h[i] >= entry):
            k0 = i; break
    else:
        return None, None
    tp = entry + 2 * d * side; trig = entry + d * side; st = stop; armed = False
    for i in range(k0, len(ts)):
        if side > 0:
            if l[i] <= st: return int(ts[k0]), round((st - entry - cost) / d, 2)
            if h[i] >= tp: return int(ts[k0]), round((tp - entry - cost) / d, 2)
            if be and not armed and h[i] >= trig: armed = True; st = entry + cost
        else:
            if h[i] + cost >= st: return int(ts[k0]), round((entry - st - cost) / d, 2)
            if l[i] + cost <= tp: return int(ts[k0]), round((entry - tp - cost) / d, 2)
            if be and not armed and l[i] + cost <= trig: armed = True; st = entry - cost
    return int(ts[k0]), None


def main():
    rows = []
    u = lambda t: dt.datetime.fromtimestamp(int(t), dt.timezone.utc).strftime("%m-%d %H:%M")
    for cid, sym, tf, when, side, res, note in CASES:
        t_case = int(dt.datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone(dt.timedelta(hours=1))).timestamp())
        y = dt.datetime.fromtimestamp(t_case, dt.timezone.utc).year
        ts, o, h, l, c = load(sym, y)
        m = (ts >= t_case - 6 * 86400) & (ts <= t_case + 2 * 86400)
        ts, o, h, l, c = ts[m], o[m], h[m], l[m], c[m]
        bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, tf)
        B = dict(t=bt, o=bo, h=bh, l=bl, c=bc, minutes=tf)
        found = []
        for k in (3, 4, 5):
            for eg in ("any",):
                for s in S._setups(B, {"k": k, "engulf": eg}):
                    dec = int(bt[s["d"]] + tf * 60)
                    if s["side"] == side and t_case - 30 * 3600 <= dec <= t_case + 1800:
                        i0 = int(nxt[s["d"]])
                        f0, r0 = outcome(ts, o, h, l, c, i0, side, s["entry"], s["stop"], False, S.COSTS[sym], S.FILL_SPREAD[sym])
                        f1, r1 = outcome(ts, o, h, l, c, i0, side, s["entry"], s["stop"], True, S.COSTS[sym], S.FILL_SPREAD[sym])
                        legs = [u(bt[x]) for x in s["legs"]]
                        found.append(dict(k=k, decision=u(dec), legs_4_to_1=legs, candles=int(s["legs"][3] - s["legs"][0]),
                                          entry=round(s["entry"], 5), stop=round(s["stop"], 5), pct=s["pct"],
                                          eg4=s["eg4"], eg2=s["eg2"], fill=u(f0) if f0 else None, R=r0, R_be=r1))
        rows.append(dict(case=cid, sym=sym, tf=tf, owner_time_utc=u(t_case), side="BUY" if side > 0 else "SELL",
                         owner=res, note=note, found=found))
        print(f"{cid:5} {sym} M{tf:<3} {u(t_case)} UTC {'BUY ' if side > 0 else 'SELL'} owner: {res}")
        if not found:
            print("      detector: no matching setup in the 18 h before")
        for f in found:
            print(f"      k={f['k']} decision {f['decision']} legs {f['legs_4_to_1']} ({f['candles']} candles) entry {f['entry']} "
                  f"stop {f['stop']} ({f['pct']:.0%}) EG4 {f['eg4']} EG2 {f['eg2']} -> fill {f['fill']} R {f['R']} (BE {f['R_be']})")
    json.dump(rows, open(os.path.join(OUT, "parity_cases.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

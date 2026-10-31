"""Re-score the 11-leg book with a realistic Exness Zero cost profile built from MEASURED Zero spreads.

Spreads: research/results/exness/zero_spreads.json (exness_costs.py: Exness's own Zero-account ticks, 6 months x 8
markets, sample fixed before measuring). Spread = mean of the six monthly means (rollover block and weekends excluded).
Commission is not in tick data. Public sources conflict (Exness: "from $0.05 per lot per side", varies by instrument;
reviews: up to $3.50 per side on FX majors; $5.50 per side on gold dated 2026-09-30). The realistic profile takes the
HIGH end ($3.50 FX, $5.50 gold, per side); the low-commission profile halves it. Slippage allowance: 0.2 pip FX,
$0.05 gold, 0.3 pip JPY crosses. Crosses (GBPJPY, EURGBP) have no measured spread here: 1 pip / 0.3 pip assumed.
Swaps: the research swaps, or none (swap-free; Exness grants swap-free status on popular instruments to many
clients, but the owner's status is unconfirmed).
Same trades, same leg weights as the frozen book; only costs and swaps change.

    python3 research/exness/rescore_book.py -> research/results/exness/book_rescore.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "northstar")); sys.path.insert(0, os.path.join(HERE, ".."))
import core
import ns_portfolio as PF
from rescore import COST, SWAP

OUT = os.path.join(HERE, "..", "results", "exness")
SPREADS = json.load(open(os.path.join(OUT, "zero_spreads.json")))


def measured(sym):
    v = [x["mean"] for k, x in SPREADS.items() if k.split()[0] == sym]
    return float(np.mean(v))


def zero_costs(comm_scale=1.0):
    fx = 7.0 / 100000 * comm_scale                      # $3.50 per side per 100k lot, in USD per unit of base
    return {
        "EURUSD": measured("EURUSD") + fx + 0.00002,
        "GBPUSD": measured("GBPUSD") + fx + 0.00002,
        "USDJPY": measured("USDJPY") + fx * 150 + 0.002,                  # commission in yen at USDJPY ~150 (high end)
        "XAUUSD": measured("XAUUSD") + 11.0 / 100 * comm_scale + 0.05,    # $5.50 per side per 100 oz
        "GBPJPY": 0.01 + fx * 150 + 0.003,
        "EURGBP": 0.00003 + fx / 1.25 + 0.00002,
    }


def daily(T, w):
    d = pd.DatetimeIndex(pd.to_datetime(np.asarray(T["t_out"]), unit="s")).normalize()
    pnl = pd.Series(0.01 * w * np.asarray(T["r"]), index=d).groupby(level=0).sum()
    idx = pd.date_range("2011-01-03", "2025-12-31", freq="B")
    return pnl.reindex(idx, fill_value=0.0)


def stats(p):
    s = float(p.mean() / p.std() * np.sqrt(252)) if p.std() > 0 else float("nan")
    eq = (1 + p).cumprod(); dd = float((1 - eq / eq.cummax()).max())
    yrs = len(p) / 252
    return dict(sharpe=round(s, 2), cagr_at_1pct=round(float(eq.iloc[-1] ** (1 / yrs) - 1), 4), max_dd_at_1pct=round(dd, 4))


def main():
    T0, names = PF.build("BOOK")
    legs = PF.legs("BOOK")
    w = np.array([n["weight"] for n in names])
    profiles = {"research costs + swaps (as assumed)": (COST, SWAP),
                "Exness Zero realistic + swaps": (zero_costs(1.0), SWAP),
                "Exness Zero realistic, swap-free": (zero_costs(1.0), {k: 0.0 for k in SWAP}),
                "Exness Zero low commission + swaps": (zero_costs(0.5), SWAP),
                "Exness Zero low commission, swap-free": (zero_costs(0.5), {k: 0.0 for k in SWAP})}
    res = {"costs_round_trip": {k: {s: round(v, 6) for s, v in c.items()} for k, (c, _) in profiles.items()}, "results": {}}
    for label, (cost, swap) in profiles.items():
        rows = []
        for i, (name, sym, x) in enumerate(legs):
            nights = np.array([core.nights_held(int(a), int(b)) for a, b in zip(x["t_in"], x["t_out"])])
            r = x["r"] + COST[sym] / x["dist"] - cost[sym] / x["dist"] - nights * swap[sym] / x["dist"]
            rows.append(pd.DataFrame(dict(t_out=x["t_out"].astype(np.int64), r=r, w=w[i])))
        D = pd.concat(rows)
        p = daily(D, D["w"].to_numpy())
        res["results"][label] = {"2011-2025": stats(p), "2023-2025": stats(p[p.index >= "2023-01-01"]),
                                 "mean_R_per_trade": round(float(D["r"].mean()), 4), "trades": int(len(D))}
        print(label, res["results"][label], flush=True)
    json.dump(res, open(os.path.join(OUT, "book_rescore.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

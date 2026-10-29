"""Combine the timeless gold strategies into one book; weights fitted on 2011-2018 only."""
import numpy as np, datetime as dt, json
import gold_search as GS, payout as PO, pareto as PA, portfolio as P

LEGS = {"DON_H4_n20_turtle": "trades/gold/DON_H4_n20_turtle.npy",
        "S1REV_gold_H1M30M20": "trades/S1_XAUUSD_H1+M30+M20_long_off120.npy",
        "EMA_H4_20-50": "trades/gold/MAX_H4_20-50.npy",
        "VBO_D1_k0.5": "trades/gold/VBO_D1_k0.5.npy"}


def monthly(tr):
    mk = np.array([(dt.datetime.utcfromtimestamp(int(t)).year - 2011) * 12 + dt.datetime.utcfromtimestamp(int(t)).month - 1 for t in tr["t_out"]])
    s = np.zeros(180); ok = (mk >= 0) & (mk < 180); np.add.at(s, mk[ok], tr["r"][ok]); return s


def weights_is():
    """Kelly-style w = inv(Cov) * mean on monthly R, 2011-2018 only (96 months), clipped >= 0,
    then scaled so the largest weight is 1.0."""
    M = np.array([monthly(np.load(p)) for p in LEGS.values()])[:, :96]
    mu, C = M.mean(1), np.cov(M)
    w = np.linalg.solve(C + 1e-9 * np.eye(len(mu)), mu)
    w = np.clip(w, 0, None)
    return w / w.max()


if __name__ == "__main__":
    w = weights_is()
    print("weights fitted on 2011-2018 only:", {k: round(float(x), 2) for k, x in zip(LEGS, w)})
    trs = [np.load(p) for p in LEGS.values()]
    # book in R units of the base risk: each trade's R x its weight
    book = np.concatenate([np.c_[t["t_in"], t["t_out"], t["r"] * wi] for t, wi in zip(trs, w)])
    book = book[np.argsort(book[:, 0])]
    bt = np.zeros(len(book), dtype=GS.GL.DT); bt["t_in"], bt["t_out"], bt["r"] = book[:, 0], book[:, 1], book[:, 2]
    j = GS.judge(bt); r = j["regimes"]
    mon = sum(wi * monthly(t) for t, wi in zip(trs, w))
    sh_m = mon.mean() / mon.std(ddof=1) * np.sqrt(12)
    t_m = mon.mean() / mon.std(ddof=1) * np.sqrt(np.count_nonzero(mon != 0))
    print(f"BOOK: {j['per_yr']:.0f} trades/yr | E/trade {j['E']:+.3f}R (weighted) | IS {j['E_is']:+.3f} OOS {j['E_oos']:+.3f} | "
          f"monthly Sharpe {sh_m:.2f}, t {t_m:.2f} | bear {r['bear_2011_15']:+.3f} range {r['range_2016_18']:+.3f} bull {r['bull_2019_25']:+.3f}")
    pos_m = (mon > 0).mean(); yrs = {}
    for k in range(180):
        yrs.setdefault(2011 + k // 12, 0.0); yrs[2011 + k // 12] += mon[k]
    print(f"positive months {pos_m:.0%} | positive years {sum(v > 0 for v in yrs.values())}/15 | per-year R: " +
          " ".join(f"{y % 100:02d}:{v:+.1f}" for y, v in yrs.items()))
    json.dump({"weights": dict(zip(LEGS, map(float, w)))}, open("results/gold_book.json", "w"), indent=1)

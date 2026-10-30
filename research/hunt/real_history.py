"""Real 2011-2025 record of the chosen profiles: yearly returns (growth mode, no payouts),
fortnightly payouts per year (salary mode), first payout and longest dry spell; figures."""
import os, sys, json, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import risk_lab as RL, payout_lab as PL
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = os.path.join(HERE, "figures"); os.makedirs(FIG, exist_ok=True)
SURF, INK2, GRID = "#fcfcfb", "#52514e", "#e4e3df"
COL = {"Steady": "#1baf7a", "Balanced": "#2a78d6", "Max": "#eb6834"}
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.grid": True,
                     "grid.color": GRID, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "axes.titleweight": "bold", "legend.frameon": False, "xtick.color": INK2, "ytick.color": INK2})

if __name__ == "__main__":
    legs = RL.load_book(); real = RL.merge(legs)
    P = json.load(open("results/payout_v3.json"))
    day0 = int(real[0].min() // 86400)
    ndays = int(real[1].max() // 86400) - day0 + 2
    out = {}
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    fig2, ax2 = plt.subplots(figsize=(7.4, 3.0))
    for i, (name, p) in enumerate(P.items()):
        daily = np.zeros(ndays)
        eq, mdd, yrs, _ = RL.sim(*real, p["base"], 2, p["heat"], p["budget"], 0.3, 0.15, daily, p["cap"])
        dates = [dt.datetime.utcfromtimestamp((day0 + k) * 86400) for k in range(ndays)]
        years = np.array([d.year for d in dates])
        yr_ret = {}
        prev = 1.0
        for y in range(2011, 2026):
            k = years == y
            if k.any():
                yr_ret[y] = float(daily[k][-1] / prev - 1); prev = daily[k][-1]
        pays = np.zeros(400)
        f, mdd2, eq2, bank = PL.sim_pay(*real, p["base"], p["heat"], p["budget"], 0.3, p["target"], 0.0, pays, p["cap"])
        pays = pays[:f]
        full = pays >= 0.999 * p["target"]
        first = int(np.argmax(full)) if full.any() else -1
        streak = cur = 0
        for x in full[first:] if first >= 0 else full:
            cur = 0 if x else cur + 1; streak = max(streak, cur)
        py = {}
        for j, x in enumerate(pays):
            y = dt.datetime.utcfromtimestamp(int(real[0].min()) + (j + 1) * 14 * 86400).year
            py[y] = py.get(y, 0.0) + float(x)
        out[name] = dict(cagr=float(eq ** (1 / yrs) - 1), max_dd=float(mdd), yearly=yr_ret, paid_by_year=py,
                         first_full_payout_fortnight=first, longest_miss_after_first=int(streak),
                         on_time=float(full.mean()), bank_end=float(bank), base_end=float(eq2))
        print(f"{name:9s} growth CAGR {out[name]['cagr']:.1%} max DD {mdd:.1%} | yearly: " +
              " ".join(f"{y % 100:02d}:{v:+.0%}" for y, v in yr_ret.items()))
        print(f"          salary {p['target']:.2%}/fn: on time {full.mean():.0%}, first full payout in fortnight {first + 1}, "
              f"longest miss after that {streak} fortnights, bank left {bank:.2f}x, base end {eq2:.2f}x | paid by year: " +
              " ".join(f"{y % 100:02d}:{v:.0%}" for y, v in py.items()))
        ax.plot(dates, daily, color=COL[name], lw=1.8, label=f"{name} (CAGR {out[name]['cagr']:.0%}, max DD {mdd:.0%})")
        yy = sorted(py); ax2.bar(np.array(yy) + (i - 1) * 0.27, [py[y] * 100 for y in yy], 0.25, color=COL[name], label=f"{name} {p['target']:.2%}/fortnight")
    ax.set_yscale("log"); ax.set_ylabel("account multiple (log)")
    ax.set_title("Expanded book with drawdown brake, real 2011-2025 record, no withdrawals", loc="left"); ax.legend(loc="upper left")
    fig.savefig(os.path.join(FIG, "book_v3_equity.png"), dpi=140, bbox_inches="tight")
    ax2.set_ylabel("% of starting capital paid"); ax2.set_title("Fortnightly payouts per calendar year, real record", loc="left")
    ax2.legend(fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig2.savefig(os.path.join(FIG, "book_v3_payouts.png"), dpi=140, bbox_inches="tight")
    json.dump(out, open("results/book_v3_real.json", "w"), indent=1)

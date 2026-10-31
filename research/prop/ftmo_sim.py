"""FTMO-style prop challenge replay of the surviving systems (exploratory study, not a Truth Lab strategy test).

Rules modelled (2-step, 2026 per public summaries): Phase 1 +10%, Phase 2 +5%, max daily loss 5% and max loss 10%
of the initial balance, no time limit (capped here at 12 months per phase). Funded: same limits, profits paid
every 2 weeks at an 80% split (balance resets to the initial amount after a payout), 12 months observed.
Sizing: fixed risk per trade as % of the INITIAL balance x leg weight (no compounding inside the account).

Each path starts at a month start 2011-2024 and replays the real historical trades (after costs and swaps).
Two bounds because P&L is booked at exit:
  optimistic   = only realised P&L counts toward the loss limits
  pessimistic  = all open positions are assumed to hit their stops the same day (worst case)

    python3 research/prop/ftmo_sim.py -> research/results/prop/ftmo.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "northstar"))
from rescore import ROOT, finance
import ns_portfolio as PF

OUT = os.path.join(ROOT, "results", "prop")
DAYS = pd.date_range("2011-01-03", "2025-12-31", freq="B")


def tc_trades():
    legs = [("S1_XAUUSD_M20+M30_long_off120.npy", "XAUUSD", 1.0), ("S1_EURUSD_M20+M30_long_off120.npy", "EURUSD", 1.0),
            ("TR_USDJPY_H4_atr2_long_off120.npy", "USDJPY", 2 / 3), ("TR_XAUUSD_H4_atr3_both_off120.npy", "XAUUSD", 2 / 3)]
    parts = []
    for f, s, w in legs:
        x = np.load(os.path.join(ROOT, "trades", f))
        parts.append(pd.DataFrame(dict(t_in=x["t_in"], t_out=x["t_out"], r=x["r"] - finance(x, s), w=w)))
    return pd.concat(parts, ignore_index=True)


def book_trades():
    T, _ = PF.build("BOOK")
    return pd.DataFrame(dict(t_in=T["t_in"], t_out=T["t_out"], r=T["r"], w=T["w"]))


def index(T):
    di = np.clip(DAYS.searchsorted(pd.to_datetime(T.t_in, unit="s").dt.normalize()), 0, len(DAYS) - 1)
    do = np.clip(DAYS.searchsorted(pd.to_datetime(T.t_out, unit="s").dt.normalize()), 0, len(DAYS) - 1)
    return di, do


def phase(T, di, do, start, k, target, limit_days, pessimistic, funded=False):
    """Returns (outcome, end_day, payouts). outcome: pass / fail / timeout / survived."""
    sel = di >= start
    d_in, d_out, r, w = di[sel], do[sel], T.r.values[sel], T.w.values[sel]
    bal = 1.0; paid = 0.0; end = min(start + limit_days, len(DAYS) - 1)
    exits = {}
    for a, b, rr, ww in zip(d_in, d_out, r, w):
        exits.setdefault(b, []).append(k * ww * rr)
    opens = np.zeros(len(DAYS))
    for a, b, ww in zip(d_in, d_out, w):
        opens[a:b] += k * ww                               # risk carried at the end of each day the trade is open
    for d in range(start, end + 1):
        day_pnl = sum(exits.get(d, []))
        bal += day_pnl
        open_risk = opens[d] if pessimistic else 0.0
        if -day_pnl + open_risk >= 0.05 or bal - open_risk <= 0.90:
            return "fail", d, paid
        if not funded and bal >= 1.0 + target:
            return "pass", d, paid
        if funded and (d - start) % 10 == 9 and bal > 1.0:   # fortnightly payout
            paid += 0.8 * (bal - 1.0); bal = 1.0
    return ("survived" if funded else "timeout"), end, paid


def run(name, T, risks=(0.0025, 0.005, 0.0075, 0.01, 0.015)):
    di, do = index(T)
    starts = [DAYS.searchsorted(m) for m in pd.date_range("2011-01-01", "2024-12-01", freq="MS")]
    rows = []
    for pess in (False, True):
        for k in risks:
            res = []
            for s in starts:
                o1, e1, _ = phase(T, di, do, s, k, 0.10, 252, pess)
                o2 = e2 = None; of = None; paid = 0.0
                if o1 == "pass":
                    o2, e2, _ = phase(T, di, do, e1 + 1, k, 0.05, 252, pess)
                    if o2 == "pass" and e2 + 1 < len(DAYS) - 252:
                        of, _, paid = phase(T, di, do, e2 + 1, k, 0, 252, pess, funded=True)
                res.append(dict(p1=o1, d1=e1 - s, p2=o2, d2=(e2 - e1) if e2 else None, funded=of, paid=paid))
            R = pd.DataFrame(res)
            both = (R.p1 == "pass") & (R.p2 == "pass")
            fund = R[R.funded.notna()]
            rows.append(dict(system=name, bound="pessimistic" if pess else "optimistic", risk_per_trade=k, paths=len(R),
                             pass_phase1=float((R.p1 == "pass").mean()), fail_phase1=float((R.p1 == "fail").mean()),
                             median_weeks_phase1=float(R[R.p1 == "pass"].d1.median() / 5) if (R.p1 == "pass").any() else None,
                             pass_both=float(both.mean()),
                             funded_paths=len(fund), funded_survive_12m=float((fund.funded == "survived").mean()) if len(fund) else None,
                             funded_payout_12m_median=float(fund.paid.median()) if len(fund) else None,
                             funded_payout_12m_p10=float(fund.paid.quantile(0.1)) if len(fund) else None))
            print(f"{name:12s} {rows[-1]['bound']:11s} risk {k:.2%}: phase1 pass {rows[-1]['pass_phase1']:.0%} fail {rows[-1]['fail_phase1']:.0%} "
                  f"(median {rows[-1]['median_weeks_phase1']} wks) | both {rows[-1]['pass_both']:.0%} | funded 12m survive "
                  f"{rows[-1]['funded_survive_12m'] if rows[-1]['funded_survive_12m'] is None else round(rows[-1]['funded_survive_12m'], 2)}, "
                  f"payout median {rows[-1]['funded_payout_12m_median'] if rows[-1]['funded_payout_12m_median'] is None else round(rows[-1]['funded_payout_12m_median'] * 100, 1)}% of account", flush=True)
    return rows


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    allrows = run("TimelessCity", tc_trades()) + run("Book (11)", book_trades())
    json.dump(allrows, open(os.path.join(OUT, "ftmo.json"), "w"), indent=1, default=float)

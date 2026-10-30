"""Part 10: weekly monitoring report (Markdown) from the EA's CSV logs.

Inputs (written by mt5/NorthStarGovernor.mq5; schemas in NORTHSTAR_SPEC.md):
  trades.csv   ticket,leg,symbol,side,t_open,t_close,entry,exit,stop,risk_money,pnl_money,r,spread_entry,slippage_pts,slippage_r,swap,commission
  equity.csv   time,balance,equity,open_risk_pct,state
  events.csv   time,type,detail          (type: STALE_FEED, REJECT, SPREAD, CAP_BLOCK, AMBER, RED, ACK, MARGIN)
Expected ranges: results/northstar/expected.json (built from 2011-2022 backtest trades by `--build-expected`).

Every line is tagged FACT (observed in the logs), ESTIMATE (statistical, with its uncertainty) or
RULE (a recommendation that follows mechanically from the pre-registered monitoring rules below).

Monitoring rules (fixed before any live data):
  R1  Portfolio state = the governor's GREEN/AMBER/RED state; RED -> no new entries, verify server stops, operator acknowledgement.
  R2  A strategy is "under review" only if it has >= 30 live trades AND its live mean R is below the backtest mean with
      t < -2.33 (one-sided p < 0.01), OR its current losing streak exceeds the backtest 99th-percentile streak for that leg.
      Nothing else changes a strategy's status; a strategy is never called broken from a short losing run.
  R3  Execution: median slippage of the last 20 fills > 2x the assumed slippage (assumed = 25% of the all-in cost per trade,
      i.e. 0.25 x 0.026R) -> AMBER (live); any spread > 4x normal at
      decision -> RED event (logged by the governor).
  R4  The week's return outside the backtest 5-95% weekly band is reported as "outside the expected range"; on its own it
      triggers no action.
  R5  Breaches (cap blocks, rejects, stale feed, margin) are listed every week; >= 3 rejects in a day or a stale feed > 5 min -> RED.

    python3 weekly.py --build-expected
    python3 weekly.py --logs DIR --week-end YYYY-MM-DD [--out report.md]
    python3 weekly.py --example        (example report from backtest trades; clearly labelled as such)
"""
import os, sys, json, math, argparse, datetime as dt
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results", "northstar")
EXP = os.path.join(RES, "expected.json")


def losing_streaks(r):
    s, c = [], 0
    for x in r:
        if x < 0:
            c += 1
        else:
            if c:
                s.append(c)
            c = 0
    if c:
        s.append(c)
    return np.array(s or [0])


def build_expected():
    import ns_portfolio as PF
    T, names = PF.build("BOOK")
    IS = PF.window(T, 0, PF.CUT23)
    legs = {}
    for i, nm in enumerate(names):
        r = IS["r"][IS["leg"] == i]
        st = losing_streaks(r)
        legs[nm["leg"]] = dict(symbol=nm["sym"], weight=nm["weight"], n_2011_2022=int(len(r)), mean_R=float(r.mean()), sd_R=float(r.std(ddof=1)),
                               win_rate=float((r > 0).mean()), trades_per_year=float(len(r) / 12),
                               streak_p99=int(np.quantile(st, 0.99)), streak_max=int(st.max()))
    pj = json.load(open(os.path.join(RES, "portfolio.json")))["BOOK"]
    out = dict(source="BOOK 11 legs, R after costs and financing, 2011-2022; weekly bands from 200 reshuffled paths at the demo policy",
               policy=pj["demo"]["policy"], base_risk=pj["demo"]["risk"], weekly=pj["weekly_bands"], legs=legs,
               assumed_cost_R=0.026)
    json.dump(out, open(EXP, "w"), indent=1)
    return out


def tstat_below(live, mu):
    if len(live) < 2 or np.std(live, ddof=1) == 0:
        return None
    return float((np.mean(live) - mu) / (np.std(live, ddof=1) / math.sqrt(len(live))))


def report(trades, equity, events, week_end, exp, label=""):
    we = pd.Timestamp(week_end) + pd.Timedelta(days=1); ws = we - pd.Timedelta(days=7)
    L = []; add = L.append
    eq = equity.sort_values("time"); wk_eq = eq[(eq.time >= ws) & (eq.time < we)]
    last = eq[eq.time < we].iloc[-1]; first = eq.iloc[0]
    prev = eq[eq.time < ws]; start = prev.iloc[-1] if len(prev) else first
    closed = trades[trades.t_close.notna()]; wk = closed[(closed.t_close >= ws) & (closed.t_close < we)]
    opn = trades[(trades.t_open < we) & ((trades.t_close.isna()) | (trades.t_close >= we))]
    ret_w = last.equity / start.equity - 1; ret_all = last.equity / first.equity - 1
    peak = eq[eq.time < we].equity.cummax(); ddc = float(1 - last.equity / peak.iloc[-1]); ddm = float((1 - eq[eq.time < we].equity / peak).max())
    add(f"# North Star weekly report — week ending {week_end}{label}\n")
    add("Tags: **FACT** = observed in the logs · **ESTIMATE** = statistical, with uncertainty · **RULE** = action that follows from the pre-registered monitoring rules (R1–R5).\n")
    add("## 1. Account equity and balance")
    add(f"- FACT: balance {last.balance:,.2f}, equity {last.equity:,.2f} (start of week equity {start.equity:,.2f}).")
    add("## 2. Realised and unrealised P&L")
    add(f"- FACT: realised this week {wk.pnl_money.sum():+,.2f} from {len(wk)} closed trades; unrealised now {last.equity - last.balance:+,.2f}.")
    add("## 3. Return for the week and since inception")
    add(f"- FACT: week {ret_w:+.2%}; since inception {ret_all:+.2%} ({first.time:%Y-%m-%d} → {week_end}).")
    b = exp["weekly"]
    inside = b["return_p05"] <= ret_w <= b["return_p95"]
    add(f"- ESTIMATE: backtest weekly range at {exp['base_risk']:.0%} base risk — 5%: {b['return_p05']:+.2%}, median: {b['return_median']:+.2%}, 95%: {b['return_p95']:+.2%}. "
        f"This week is {'inside' if inside else 'OUTSIDE'} the 5–95% range (R4: information only).")
    add("## 4. Peak-to-trough drawdown")
    add(f"- FACT: current drawdown {ddc:.2%}; worst since inception {ddm:.2%}.")
    add("## 5. Open positions and total risk")
    add(f"- FACT: {len(opn)} open position(s); open risk {last.open_risk_pct:.2f}% of equity (cap 10%).")
    for _, p in opn.iterrows():
        add(f"  - {p.leg} {p.symbol} {'long' if p.side > 0 else 'short'} since {p.t_open:%Y-%m-%d %H:%M}, risk {p.risk_money:,.2f}")
    add("## 6. Trades by strategy")
    add("| strategy | week trades | week R | live trades | live mean R | backtest mean R | current losing streak | backtest 99% streak |")
    add("|---|---|---|---|---|---|---|---|")
    reviews = []
    for leg, e in exp["legs"].items():
        lt = closed[(closed.leg == leg) & (closed.t_close < we)].sort_values("t_close")
        w = wk[wk.leg == leg]
        r = lt.r.values; cur = 0
        for x in r[::-1]:
            if x < 0:
                cur += 1
            else:
                break
        add(f"| {leg} | {len(w)} | {w.r.sum():+.2f} | {len(lt)} | {np.mean(r) if len(r) else float('nan'):+.3f} | {e['mean_R']:+.3f} | {cur} | {e['streak_p99']} |")
        t = tstat_below(r, e["mean_R"])
        if (len(r) >= 30 and t is not None and t < -2.33) or cur > e["streak_p99"]:
            reviews.append((leg, len(r), t, cur, e["streak_p99"]))
    add("## 7. Expectancy and profit factor (with sample-size caveats)")
    r_all = closed[closed.t_close < we].r.values
    if len(r_all) >= 2:
        se = np.std(r_all, ddof=1) / math.sqrt(len(r_all)); pf = r_all[r_all > 0].sum() / max(-r_all[r_all < 0].sum(), 1e-12)
        add(f"- ESTIMATE: live expectancy {np.mean(r_all):+.3f}R per trade, 95% interval [{np.mean(r_all) - 1.96 * se:+.3f}, {np.mean(r_all) + 1.96 * se:+.3f}] "
            f"from {len(r_all)} trades; profit factor {pf:.2f}.")
        need = int(math.ceil((1.96 * np.std(r_all, ddof=1) / max(abs(np.mean(r_all)), 1e-6)) ** 2))
        add(f"- ESTIMATE: at this spread of results, about {need:,} trades are needed before the sign of the expectancy is known with 95% confidence"
            f" — {'reached' if len(r_all) >= need else 'not reached yet; do not judge the system on this sample'}.")
    else:
        add("- FACT: fewer than 2 closed trades — no estimate.")
    add("## 8. Spread, slippage and execution quality")
    if len(wk):
        add(f"- FACT: median entry spread {wk.spread_entry.median():.1f} points; median slippage {wk.slippage_pts.median():+.1f} points; "
            f"swap {wk.swap.sum():+,.2f}; commission {wk.commission.sum():+,.2f}.")
    last20 = closed[closed.t_close < we].tail(20)
    slip_R = last20.slippage_r.median() if len(last20) else np.nan
    lim = 2 * 0.25 * exp["assumed_cost_R"]
    add(f"- FACT: median slippage of the last {len(last20)} fills {slip_R:+.4f}R (limit {lim:.4f}R).")
    add(f"- RULE R3: {'within limits' if not (slip_R > lim) else 'ABOVE 2x assumed slippage -> AMBER'}.")
    add("## 9. Live/demo against backtest ranges")
    n_wk = len(wk); tw = exp["weekly"]
    add(f"- ESTIMATE: backtest trades per active week 5%–95%: {tw['trades_per_active_week_p05']:.0f}–{tw['trades_per_active_week_p95']:.0f}; this week {n_wk} (FACT).")
    add(f"- ESTIMATE: backtest win rate {tw['win_rate']:.0%}, mean {tw['mean_R']:+.3f}R; live win rate {np.mean(r_all > 0) if len(r_all) else float('nan'):.0%} (FACT, {len(r_all)} trades).")
    add("## 10. Portfolio state")
    add(f"- FACT: governor state at week end: **{last.state}**.")
    add("## 11. Data, execution and risk-limit breaches")
    ev = events[(events.time >= ws) & (events.time < we)] if len(events) else events
    if len(ev):
        for typ, g in ev.groupby("type"):
            add(f"- FACT: {typ} x{len(g)} (first {g.time.min():%Y-%m-%d %H:%M}: {g.detail.iloc[0]})")
    else:
        add("- FACT: none logged.")
    add("## 12. Recommended action (rules R1–R5)")
    if last.state == "RED":
        add("- RULE R1: RED — no new entries; confirm every open position has its server-side stop; investigate the trigger; resume only after operator acknowledgement (in AMBER).")
    elif last.state == "AMBER":
        add("- RULE R1: AMBER — continue; under the demo policy AMBER is shadow-only (no size change); note the trigger.")
    else:
        add("- RULE R1: GREEN — continue unchanged.")
    for leg, n, t, cur, p99 in reviews:
        add(f"- RULE R2: {leg} under review ({n} live trades, t vs backtest {t if t is None else round(t, 2)}, losing streak {cur} vs 99% {p99}). "
            f"Operator decision required; no automatic change.")
    if not reviews:
        add("- RULE R2: no strategy meets the review threshold. Losing runs inside the backtest range are normal and need no action.")
    if not inside:
        add("- RULE R4: weekly return outside the expected band — reported only; no action on its own.")
    return "\n".join(L) + "\n"


def example():
    """Example report built from the book's 2025 backtest trades replayed at the demo policy (NOT live data)."""
    import ns_portfolio as PF, risk
    exp = json.load(open(EXP)) if os.path.exists(EXP) else build_expected()
    T, names = PF.build("BOOK")
    W = PF.window(T, int(pd.Timestamp("2025-01-01").timestamp()), 2 ** 62)
    s = risk.simulate(W, exp["base_risk"], exp["policy"])
    bal = 10000.0
    rows = []; eqrows = []; e = bal
    o = np.argsort(W["t_out"])
    risk_now = exp["base_risk"]
    for k in o:
        risk_money = e * risk_now * W["w"][k]; pnl = risk_money * W["r"][k]; e += pnl
        rows.append(dict(ticket=int(k), leg=names[W["leg"][k]]["leg"], symbol=names[W["leg"][k]]["sym"], side=int(W["side"][k]),
                         t_open=pd.Timestamp(int(W["t_in"][k]), unit="s"), t_close=pd.Timestamp(int(W["t_out"][k]), unit="s"),
                         entry=1.0, exit=1.0, stop=0.99, risk_money=risk_money, pnl_money=pnl, r=W["r"][k], spread_entry=np.nan,
                         slippage_pts=0.0, slippage_r=0.0, swap=0.0, commission=0.0))
        eqrows.append(dict(time=pd.Timestamp(int(W["t_out"][k]), unit="s"), balance=e, equity=e, open_risk_pct=0.0, state="GREEN"))
    trades = pd.DataFrame(rows); equity = pd.DataFrame([dict(time=pd.Timestamp("2025-01-01"), balance=bal, equity=bal, open_risk_pct=0.0, state="GREEN")] + eqrows)
    events = pd.DataFrame(columns=["time", "type", "detail"])
    md = report(trades, equity, events, "2025-12-26", exp, label=" (EXAMPLE from 2025 backtest trades — not live data)")
    out = os.path.join(HERE, "WEEKLY_REPORT_EXAMPLE.md")
    open(out, "w").write(md)
    print(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-expected", action="store_true"); ap.add_argument("--example", action="store_true")
    ap.add_argument("--logs"); ap.add_argument("--week-end"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.build_expected:
        print(json.dumps(build_expected(), indent=1)[:2000]); return
    if a.example:
        example(); return
    exp = json.load(open(EXP))
    rd = lambda f, cols: pd.read_csv(os.path.join(a.logs, f), parse_dates=cols) if os.path.exists(os.path.join(a.logs, f)) else pd.DataFrame(columns=["time", "type", "detail"])
    md = report(rd("trades.csv", ["t_open", "t_close"]), rd("equity.csv", ["time"]), rd("events.csv", ["time"]), a.week_end, exp)
    if a.out:
        open(a.out, "w").write(md)
    print(md)


if __name__ == "__main__":
    main()

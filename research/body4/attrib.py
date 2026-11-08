"""What makes the losses (owner, 2026-11-08: "what made the biggest loser, the cost, what cost goes high, Asians and news").
v3 main settings (50% entry, stop at the range end, breakeven at 75%, lookback on with dojis bullish, 10R), 12 markets x
M1-H4, fills 2011-22. Pre-registered: research/body4/PREREGISTRATION_V4.md section 1.

Every trade's result in R = price move (bid to bid, gaps included) - spread - commission - slippage - swaps, grouped by
entry session, US news day, overnight hold, timeframe and market; the gap part of stop and target fills; and the 50
biggest losers classified.
    python3 research/body4/attrib.py  ->  research/results/body4/v4/attribution.json + ATTRIBUTION.md
"""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v3.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v4")
MAIN = dict(entry=0.5, be=1, buffer=0.0, lookback=1, target=10)
UTC, NY = dt.timezone.utc, ZoneInfo("America/New_York")
_cal = json.load(open(os.path.join(ROOT, "research", "truth", "calendars", "us_news_days.json")))
NEWS = {dt.date.fromisoformat(d) for k in ("nfp", "cpi", "fomc") for d in _cal[k]}
FX24 = {"XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP"}


def session(t):
    h = (int(t) % 86400) / 3600
    if h >= 23 or h < 7:
        return "Asia (23:00-07:00 UTC)"
    if h < 12:
        return "London (07:00-12:00)"
    if h < 16:
        return "London-New York overlap (12:00-16:00)"
    if h < 20.5:
        return "New York (16:00-20:30)"
    return "Rollover (20:30-23:00)"


def main():
    recs = []
    for sym in S.MARKETS:
        M = P.market(sym, S)
        ts = np.asarray(M.ts, np.int64); o = np.asarray(M.o, float)
        sp, cm, sl = S.SPLIT[sym]["spread"], S.SPLIT[sym]["commission"], S.SPLIT[sym]["slippage"]
        for tf in S.TIMEFRAMES:
            D = S.detail(M, M.bars(tf), dict(MAIN, tf=tf), cut=P.core.CUT)
            for r in D:
                s, R0, why = int(r[2]), r[4], int(r[9])
                spread_R, comm_R = sp / R0, cm / R0
                slip_R = sl / R0 if why in (1, 3, 4, 5) else 0.0
                swap_R = r[7]
                move_R = r[3] + spread_R + comm_R + slip_R + swap_R
                gap_loss = gap_gain = 0.0
                if why in (1, 3, 5):
                    stop_used = r[10] if why == 3 else r[12]
                    gap_loss = max(0.0, ((stop_used - s * sl) - r[11]) * s / R0)
                elif why == 2:
                    gap_gain = max(0.0, (r[11] - r[13]) * s / R0)
                ix = int(np.searchsorted(ts, int(r[1])))
                pause = int(ts[ix] - ts[ix - 1]) if 0 < ix < len(ts) and ts[ix] == int(r[1]) else 0
                recs.append(dict(sym=sym, tf=tf, R=float(r[3]), move=float(move_R), spread=float(spread_R), comm=float(comm_R),
                                 slip=float(slip_R), swap=float(swap_R), gap_loss=float(gap_loss), gap_gain=float(gap_gain),
                                 why=why, nights=int(r[6]), t_in=int(r[0]), t_out=int(r[1]), pause=pause,
                                 sess=session(r[0]), news=dt.datetime.fromtimestamp(int(r[0]), NY).date() in NEWS))
        print(sym, len(recs), flush=True)
    def summ(xs):
        n = len(xs)
        if n == 0:
            return dict(n=0)
        a = lambda k: round(float(np.mean([x[k] for x in xs])), 4)
        return dict(n=n, R=a("R"), move=a("move"), spread=a("spread"), commission=a("comm"), slippage=a("slip"), swaps=a("swap"),
                    gap_loss=a("gap_loss"), gap_gain=a("gap_gain"),
                    stopped=round(float(np.mean([x["why"] in (1, 5) for x in xs])), 3),
                    target=round(float(np.mean([x["why"] == 2 for x in xs])), 3))
    res = dict(settings="v3 main settings at 10R (entry 50%, stop at range end, breakeven at 75%, lookback on, dojis bullish), 2011-22",
               all=summ(recs))
    for key, f in (("by_session", lambda x: x["sess"]), ("by_news_day", lambda x: "US news day" if x["news"] else "other days"),
                   ("by_overnight", lambda x: "held overnight" if x["nights"] > 0 else "closed the same day"),
                   ("by_timeframe", lambda x: x["tf"]), ("by_market", lambda x: x["sym"])):
        g = {}
        for x in recs:
            g.setdefault(f(x), []).append(x)
        res[key] = {k: summ(v) for k, v in sorted(g.items())}
    # session x timeframe: cost share (where costs go high)
    g = {}
    for x in recs:
        g.setdefault(f"{x['tf']} | {x['sess']}", []).append(x)
    res["by_timeframe_and_session"] = {k: summ(v) for k, v in sorted(g.items())}
    worst = sorted(recs, key=lambda x: x["R"])[:50]
    def kind(x):
        k = []
        if x["gap_loss"] > 1.0:
            k.append("gap through the stop")
            if x["pause"] > 1800:
                if x["sym"] in FX24 and not (20 * 3600 <= x["t_out"] % 86400 <= 23 * 3600 + 1800):
                    k.append("hole in the price data")
                else:
                    k.append("market closed overnight")
        if x["nights"] > 0:
            k.append("held overnight")
        if x["news"]:
            k.append("US news day")
        if x["sess"].startswith("Asia"):
            k.append("Asian session entry")
        if x["swap"] > 0.5:
            k.append("swaps > 0.5R")
        if x["spread"] + x["comm"] + x["slip"] > 0.5:
            k.append("costs > 0.5R")
        return k
    cnt = {}
    for x in worst:
        for k in kind(x):
            cnt[k] = cnt.get(k, 0) + 1
    res["worst50"] = dict(causes=dict(sorted(cnt.items(), key=lambda z: -z[1])),
                          list=[dict(sym=x["sym"], tf=x["tf"], R=round(x["R"], 2), fill=dt.datetime.fromtimestamp(x["t_in"], UTC).strftime("%Y-%m-%d %H:%M"),
                                     causes=kind(x), gap_loss=round(x["gap_loss"], 2), swaps=round(x["swap"], 2),
                                     costs=round(x["spread"] + x["comm"] + x["slip"], 2)) for x in worst[:20]])
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "attribution.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("all", "by_session", "by_news_day", "by_overnight", "by_timeframe")}, indent=1))
    print(json.dumps(r["worst50"]["causes"], indent=1))

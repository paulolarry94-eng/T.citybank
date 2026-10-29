"""Part 1b — can each session's opening range be reconstructed, and what does it cost to trade?

For every instrument x session x ORB length: sessions available, share of weekdays whose
opening-range window has >= 80% of its minutes, typical OR width (price, daily-ATR units and
multiples of the all-in cost), measured median spread in the entry window (tick-built years
only) against the cost assumption, and whether activity (volume) data exists.
Also prints the UTC open times across daylight-saving changes as a check.
"""
import os, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
import core

OUT = os.path.join(core.HERE, "..", "results", "orb_session_audit.json")


def dst_table():
    rows = []
    for name, (tz, (oh, om), _) in core.SESSIONS.items():
        for day in ("2024-03-08", "2024-03-12", "2024-04-02", "2024-10-29", "2024-11-05", "2024-07-01"):
            y, m, d = map(int, day.split("-"))
            t = dt.datetime(y, m, d, oh, om, tzinfo=ZoneInfo(tz)).astimezone(dt.timezone.utc)
            rows.append((name, day, t.strftime("%H:%M UTC")))
    return rows


def main():
    res = []
    for sym in core.SYMS:
        M = core.Market(sym)
        for sess in core.SESSIONS:
            for orb in core.ORB_MIN:
                D = M.days(sess, orb)
                n_week = np.busday_count("2011-01-03", "2026-01-01")
                if sym == "XAUUSD":
                    n_week -= np.busday_count("2011-01-03", "2011-05-10") + np.busday_count("2018-06-19", "2019-01-01")
                w = D["orh"] - D["orl"]
                # measured spreads in the first 3 hours of the session (tick years only)
                sp = []
                for i0 in D["i_open"][::5]:
                    x = M.spr[i0:i0 + 180]
                    x = x[np.isfinite(x)]
                    if len(x):
                        sp.append(np.median(x))
                v_ok = np.mean([M.v[i0:i0 + orb].sum() > 0 for i0 in D["i_open"]])
                res.append(dict(sym=sym, session=sess, orb=orb, sessions=int(len(w)),
                                coverage_pct=round(100 * len(w) / n_week, 1),
                                width_med=float(np.median(w)), width_atrD_med=float(np.median(D["w_atr"])),
                                width_p10_p90_atrD=[float(np.percentile(D["w_atr"], 10)), float(np.percentile(D["w_atr"], 90))],
                                width_over_cost_med=float(np.median(w) / M.cost),
                                spread_med_entry_window=float(np.median(sp)) if sp else None,
                                spread_years=len(sp) * 5, cost=M.cost,
                                activity_data_share=round(float(v_ok), 3)))
                r = res[-1]
                print(f"{sym} {sess:5s} ORB{orb:<2d} n={r['sessions']:4d} cov={r['coverage_pct']:5.1f}% "
                      f"width={r['width_med']:.5g} ({r['width_atrD_med']:.2f} ATR_D, {r['width_over_cost_med']:.1f}x cost) "
                      f"spread={r['spread_med_entry_window']} vs cost {M.cost} act={r['activity_data_share']}", flush=True)
    json.dump(dict(dst=dst_table(), rows=res), open(OUT, "w"), indent=1)
    for r in dst_table():
        print(*r)


if __name__ == "__main__":
    main()

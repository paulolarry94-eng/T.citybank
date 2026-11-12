"""Reference simulator for pivot-sweep v2 (research/sweep5/PREREGISTRATION.md). Plain Python: the specification; the
fast engine (sweep5_fast.py) must match it trade for trade. M1 bid bars; ask = bid + spread; commission per trade;
slippage on stop and time exits.

New setup (from the first minute after candle 4 closes): ignored in the weekend window or while a trade is open; skipped
if price is already through the entry level or 1R is not bigger than the round-trip cost. Pending orders: same direction
added; opposite direction replaces all pending orders if its range is wider than every one, else ignored.
Pending order: fills when price trades at its level (buy: ask <= level; sell: bid >= level), not in the 20:30-23:00 UTC
rollover; cancelled when price trades at its stop first (buy: bid <= stop; sell: ask >= stop), when its life ends, or at
the Friday 20:30 UTC cutoff. When one order fills, the others are removed.
At the fill: TP1 / TP2 = the nearest / next live pivot beyond the entry on the target side, from the last closed candle of
the pattern timeframe (fewer than 2: the fill is dropped, no trade). Exits: `partial`: 60% at TP1, then the remaining 40%
has its stop at entry +/- (spread + commission) and its target at TP2; `tp1`: all at TP1; `tp2`: all at TP2. Stop first
when stop and target fall in the same minute; the fill minute can only stop out; Friday 20:30 UTC closes at market.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "body4"))
from body4_orders import weekend, friday_cut_after, nights_held, BLOCK   # noqa: E402

FRAC1 = 0.6


def run(M, O, S, spread, commission, slippage, swap=0.0, exit="partial", allow=None, cut=2 ** 62, gaps=(), tgt_r=0.0, be_frac=0.0):
    """exit "fixed": all at tgt_r R from the level (no pivots needed); be_frac > 0: the stop moves to the entry once price
    has covered be_frac of the distance from the level to the target (from the next minute)."""
    ts, o, h, l, c = M["ts"], M["o"], M["h"], M["l"], M["c"]
    N = len(ts); P = len(O["t_conf"])
    cost = spread + commission + slippage
    gaps = np.asarray(gaps, np.int64)
    allow = np.ones(P, bool) if allow is None else np.asarray(allow, bool)
    starts = np.searchsorted(ts, np.asarray(O["t_conf"], np.int64))
    trades, pend, pos, pj = [], [], None, 0

    def finish(i, t_out, px2, why):
        nonlocal pos
        s, d, e = pos["side"], pos["risk"], pos["entry"]
        if pos["part"]:
            gross = FRAC1 * (pos["px1"] - e) / d * s + (1 - FRAC1) * (px2 - e) / d * s
        else:
            gross = (px2 - e) / d * s
        nts = nights_held(pos["t_in"], t_out); fin = nts * swap / d
        if not np.any((gaps > pos["i_in"]) & (gaps <= i)):
            trades.append(dict(j=pos["j"], side=s, t_in=pos["t_in"], t_out=int(t_out), entry=e, stop0=pos["stop0"], tp1=pos["tp1"],
                               tp2=pos["tp2"], exit=px2, R=gross - commission / d - fin, risk=d, cost_r=cost / d, nights=nts,
                               fin_r=fin, why=why, part=pos["part"], mfe=pos["mfe"]))
        pos = None

    for i in range(N):
        t = int(ts[i])
        if pos is not None and t >= pos["cut"]:
            px = c[i - 1] - slippage if pos["side"] > 0 else c[i - 1] + spread + slippage
            finish(i - 1, pos["cut"], px, 6 if pos["part"] else 4)
        if pend:
            pend = [q for q in pend if t < q["cut"] and t < q["exp"]]
        if t >= cut:
            pend = []
            if pos is None:
                break
        while pj < P and starts[pj] <= i:
            j = pj; pj += 1
            if t >= cut or not allow[j] or weekend(int(O["t_conf"][j])) or weekend(t) or pos is not None:
                continue
            s = int(O["side"][j]); lvl = float(O["level"][j]); stp = float(O["stop"][j]); w = float(O["width"][j])
            if (s > 0 and o[i] + spread <= lvl) or (s < 0 and o[i] >= lvl):
                continue
            if abs(lvl - stp) <= cost:
                continue
            if pend and pend[0]["side"] != s:
                if w > max(q["width"] for q in pend):
                    pend = []
                else:
                    continue
            pend.append(dict(j=j, side=s, level=lvl, stop=stp, width=w, risk=abs(lvl - stp), exp=int(O["t_exp"][j]),
                             cut=friday_cut_after(t)))
        if pend and pos is None:
            blocked = BLOCK[0] <= t % 86400 < BLOCK[1]
            hit = [q for q in pend if not blocked and ((l[i] + spread <= q["level"]) if q["side"] > 0 else (h[i] >= q["level"]))]
            if hit:
                q = max(hit, key=lambda x: x["level"]) if hit[0]["side"] > 0 else min(hit, key=lambda x: x["level"])
                pend = []
                s = q["side"]
                px = min(q["level"], o[i] + spread) if s > 0 else max(q["level"], o[i])
                jb = int(np.searchsorted(S["bt"], t, side="right")) - 2      # the last closed pattern candle
                lev = S["LH"][jb] if s > 0 else S["LL"][jb]
                lev = [float(x) for x in lev if not np.isnan(x) and (x - px) * s > 0] if jb >= 0 else []
                if len(lev) >= 2 or exit == "fixed":
                    if exit == "fixed":
                        tp1 = tp2 = tp = q["level"] + s * tgt_r * q["risk"]
                    else:
                        tp1, tp2 = lev[0], lev[1]
                        tp = tp2 if exit == "tp2" else tp1      # partial and tp1 aim at TP1 first
                    pos = dict(j=q["j"], side=s, entry=px, stop=q["stop"], stop0=q["stop"], risk=q["risk"], tp1=tp1, tp2=tp2,
                               tgt=tp, part=False, px1=0.0, i_in=i, t_in=t, cut=friday_cut_after(t), mfe=0.0, k=i, be=False,
                               trig=q["level"] + be_frac * (tp - q["level"]) if be_frac > 0 else None)
                    if (l[i] <= pos["stop"]) if s > 0 else (h[i] + spread >= pos["stop"]):
                        px2 = (min(pos["stop"], o[i]) - slippage) if s > 0 else (max(pos["stop"], o[i] + spread) + slippage)
                        finish(i, t, px2, 5)
                continue
            keep = []
            for q in pend:                                              # an order whose stop is touched first is invalid
                s = q["side"]
                if not ((l[i] <= q["stop"]) if s > 0 else (h[i] + spread >= q["stop"])):
                    keep.append(q)
            pend = keep
            continue
        if pos is not None and i > pos["k"]:
            s = pos["side"]
            hit_sl = (l[i] <= pos["stop"]) if s > 0 else (h[i] + spread >= pos["stop"])
            hit_tp = (h[i] >= pos["tgt"]) if s > 0 else (l[i] + spread <= pos["tgt"])
            if hit_sl:
                px = (min(o[i], pos["stop"]) - slippage) if s > 0 else (max(o[i] + spread, pos["stop"]) + slippage)
                finish(i, t, px, 3 if (pos["part"] or pos.get("be")) else 1)
            elif hit_tp:
                px = max(pos["tgt"], o[i]) if s > 0 else min(pos["tgt"], o[i] + spread)
                pos["mfe"] = max(pos["mfe"], (px - pos["entry"]) / pos["risk"] * s)
                if exit == "partial" and not pos["part"]:
                    pos["part"] = True; pos["px1"] = px; pos["tgt"] = pos["tp2"]
                    pos["stop"] = pos["entry"] + s * (spread + commission); pos["k"] = i
                else:
                    finish(i, t, px, 2)
            else:
                run_ = (h[i] - pos["entry"]) / pos["risk"] if s > 0 else (pos["entry"] - (l[i] + spread)) / pos["risk"]
                pos["mfe"] = max(pos["mfe"], run_)
                if pos.get("trig") is not None and not pos["be"] and not pos["part"] and \
                        ((s > 0 and h[i] >= pos["trig"]) or (s < 0 and l[i] + spread <= pos["trig"])):
                    pos["stop"] = pos["entry"]; pos["be"] = True
    return trades

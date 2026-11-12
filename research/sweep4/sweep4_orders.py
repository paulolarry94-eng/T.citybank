"""Reference simulator for the owner's pivot-sweep body-engulf range (2026-11-12). Plain Python on purpose: it is the
written specification. The fast engine (sweep4_fast.py) must match it trade for trade.

Patterns are found on closed candles of the chosen timeframe (sweep4_scan.py); orders and trades run on M1 bid bars.
Prices: the data is the BID. ask = bid + spread. Commission is charged per trade; slippage only on stop and market exits.

New setup (tradeable from the first minute after candle 4 closes):
  1. weekend: candle 4 closed between Friday 20:30 UTC and Sunday 23:00 UTC -> ignored.
  2. a trade is open -> ignored.
  3. entry level = 60% of the range back from candle 4's end (buy: hi - 0.6 x range; sell: lo + 0.6 x range). If price is
     already through that level when the order would be placed, the setup is skipped.
  4. stop = the swept end of the range (+ buffer x range); 1R = entry level to stop; target = entry +/- its R multiple.
     Stop and target are fixed prices set with the order (as in MT5); a gap fill at a better price keeps them.
     A setup whose 1R is not bigger than the round-trip cost cannot be traded and is skipped.
  5. pending orders: same direction -> the new order is added; when one order fills, all other pending orders are
     removed. Opposite direction -> the new setup replaces all pending orders if its range is wider than every one of
     them, otherwise it is ignored.
Pending order: fills when price trades at its level (buy: ask <= level; sell: bid >= level), not in the daily rollover
  block 20:30-23:00 UTC. Cancelled if price reaches its target first (same minute: cancelled), at the time cutoff (Friday
  20:30 UTC, or every day 20:30 UTC in the safe-window mode), or by a wider opposite setup.
Trade: stop first if stop and target fall in the same minute; the fill minute can only stop out. Closed at market at the
  time cutoff. Trades that span a hole in the data are dropped. Swaps: nights held x swap per night.
Pivot trailing stop (option): after the fill, each time a new pivot on the stop side is CONFIRMED (buy: a pivot low; sell: a
  pivot high; known when its 10th following candle closes) and it lies between the current stop and the price at that
  minute's open, the stop moves to it from that minute.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "body4"))
from body4_orders import weekend, day_cut_after, friday_cut_after, nights_held, BLOCK   # noqa: E402  (same calendar rules)


def run(M, pats, spread, commission, slippage, swap=0.0, cut=2 ** 62, delay=0, gaps=(), day_close=False, trail=False,
        conf_hi=None, conf_lo=None):
    """M = dict(ts, o, h, l, c) M1 bid bars; pats = list of dicts (id, side, level, stop, tgt, width, t_conf[, allow]) in
    time order. Returns (trades, log, stats)."""
    ts, o, h, l, c = M["ts"], M["o"], M["h"], M["l"], M["c"]
    N = len(ts)
    cost = spread + commission + slippage
    gaps = np.asarray(gaps, np.int64)
    eh_t, eh_p = conf_hi if conf_hi is not None else (np.zeros(0, np.int64), np.zeros(0))
    el_t, el_p = conf_lo if conf_lo is not None else (np.zeros(0, np.int64), np.zeros(0))
    trades, log, pend, pos = [], [], [], None
    stats = dict(ambiguous=0)
    starts = np.searchsorted(ts, np.array([p["t_conf"] for p in pats], np.int64) + 60 * delay)
    pj = 0
    cut_after = day_cut_after if day_close else friday_cut_after

    def close(i, t_out, px, why, code):
        nonlocal pos
        s, d = pos["side"], pos["risk"]
        gross = (px - pos["entry"]) / d * s
        nights = nights_held(pos["t_in"], t_out)
        fin = nights * swap / d
        log.append((int(t_out), f"#{pos['p']['id']} closed: {why} at {px:.6g} ({gross - commission / d - fin:+.2f}R)"))
        if not np.any((gaps > pos["i_in"]) & (gaps <= i)):
            trades.append(dict(id=pos["p"]["id"], side=s, t_in=pos["t_in"], t_out=int(t_out), entry=pos["entry"],
                               stop0=pos["stop0"], tp=pos["tp"], exit=px, R=gross - commission / d - fin, gross=gross, risk=d,
                               cost_r=cost / d, nights=nights, fin_r=fin, reason=why, code=code, moved=pos["moved"],
                               mfe=pos["mfe"], pattern=pos["p"]))
        pos = None

    for i in range(N):
        t = int(ts[i])
        if pos is not None and t >= pos["cut"]:                      # time cutoff: closed at the last price before it
            px = c[i - 1] - slippage if pos["side"] > 0 else c[i - 1] + spread + slippage
            close(i - 1, pos["cut"], px, "time close", 4)
        if pend and t >= pend[0]["cut"]:
            pend = []
        if t >= cut:
            pend = []
            if pos is None:
                break
        while pj < len(pats) and starts[pj] <= i:                    # new setups that became tradeable
            p = pats[pj]; pj += 1
            if t >= cut:
                continue
            s = p["side"]
            if not p.get("allow", True):
                continue
            if weekend(p["t_conf"]) or weekend(t):
                continue
            if pos is not None:
                log.append((t, f"#{p['id']} ignored: a trade is open")); continue
            lvl = p["level"]
            if (s > 0 and o[i] + spread <= lvl) or (s < 0 and o[i] >= lvl):
                log.append((t, f"#{p['id']} skipped: price already through the entry level")); continue
            risk = abs(lvl - p["stop"])
            if risk <= cost:
                log.append((t, f"#{p['id']} skipped: 1R not bigger than the round-trip cost")); continue
            order = dict(p=p, side=s, level=lvl, stop=p["stop"], risk=risk, tp=lvl + s * p["tgt"] * risk, width=p["width"],
                         cut=cut_after(t))
            if pend and pend[0]["side"] != s:
                if p["width"] > max(q["width"] for q in pend):
                    log.append((t, f"#{p['id']} replaces pending " + ", ".join(f"#{q['p']['id']}" for q in pend)))
                    pend = []
                else:
                    log.append((t, f"#{p['id']} ignored: opposite direction, not wider than the pending order")); continue
            pend.append(order)
            log.append((t, f"#{p['id']} {'BUY' if s > 0 else 'SELL'} limit {lvl:.6g}, stop {p['stop']:.6g}, target {order['tp']:.6g}"))
        if pend and pos is None:                                     # pending orders
            blocked = BLOCK[0] <= t % 86400 < BLOCK[1]
            keep, filled = [], []
            for q in pend:
                s = q["side"]
                hit_tp = (h[i] >= q["tp"]) if s > 0 else (l[i] + spread <= q["tp"])
                hit = (not blocked) and ((l[i] + spread <= q["level"]) if s > 0 else (h[i] >= q["level"]))
                if hit_tp:
                    stats["ambiguous"] += int(hit)
                    log.append((t, f"#{q['p']['id']} cancelled: price reached its target first"))
                elif hit:
                    filled.append(q)
                else:
                    keep.append(q)
            pend = keep
            if filled:
                q = max(filled, key=lambda x: x["level"]) if filled[0]["side"] > 0 else min(filled, key=lambda x: x["level"])
                s = q["side"]
                px = min(q["level"], o[i] + spread) if s > 0 else max(q["level"], o[i])     # a gap fills at the open
                ev_t = el_t if s > 0 else eh_t
                pos = dict(p=q["p"], side=s, entry=px, stop=q["stop"], stop0=q["stop"], risk=q["risk"], tp=q["tp"], moved=False,
                           i_in=i, t_in=t, cut=cut_after(t), mfe=0.0, q=int(np.searchsorted(ev_t, t, side="right")) if trail else 0)
                log.append((t, f"#{q['p']['id']} filled at {px:.6g}"))
                pend = []
                if (l[i] <= pos["stop"]) if s > 0 else (h[i] + spread >= pos["stop"]):
                    stats["ambiguous"] += 1
                    px2 = (min(pos["stop"], o[i]) - slippage) if s > 0 else (max(pos["stop"], o[i] + spread) + slippage)
                    close(i, t, px2, "stop in the fill minute", 5)
            continue
        if pos is not None and i > pos["i_in"]:                      # open trade, from the minute after the fill
            s = pos["side"]
            if trail:
                ev_t, ev_p = (el_t, el_p) if s > 0 else (eh_t, eh_p)
                while pos["q"] < len(ev_t) and ev_t[pos["q"]] <= t:
                    pv = float(ev_p[pos["q"]]); pos["q"] += 1
                    if (s > 0 and pos["stop"] < pv < o[i]) or (s < 0 and o[i] + spread < pv < pos["stop"]):
                        pos["stop"] = pv; pos["moved"] = True
                        log.append((t, f"#{pos['p']['id']} stop trailed to the new pivot {pv:.6g}"))
            hit_sl = (l[i] <= pos["stop"]) if s > 0 else (h[i] + spread >= pos["stop"])
            hit_tp = (h[i] >= pos["tp"]) if s > 0 else (l[i] + spread <= pos["tp"])
            if hit_sl:
                stats["ambiguous"] += int(hit_tp)
                if s > 0:
                    px = min(o[i], pos["stop"]) - slippage
                else:
                    px = max(o[i] + spread, pos["stop"]) + slippage
                close(i, t, px, "trailed stop" if pos["moved"] else "stop", 3 if pos["moved"] else 1)
            elif hit_tp:
                px = max(pos["tp"], o[i]) if s > 0 else min(pos["tp"], o[i] + spread)
                pos["mfe"] = max(pos["mfe"], (px - pos["entry"]) / pos["risk"] * s)
                close(i, t, px, "target", 2)
            else:
                run_ = (h[i] - pos["entry"]) / pos["risk"] if s > 0 else (pos["entry"] - (l[i] + spread)) / pos["risk"]
                pos["mfe"] = max(pos["mfe"], run_)
    return trades, log, stats

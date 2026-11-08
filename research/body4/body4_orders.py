"""Reference simulator for the owner's body-engulf 4-candle range (Q30), rules as corrected by the owner on 2026-11-08.
Plain Python on purpose: it is the written specification. The fast engine (body4_fast.py) must match it trade for trade.

Patterns are found on bars of the chosen timeframe (body4_scan.py); orders and trades run on M1 bid bars.
Prices: the data is the BID. ask = bid + spread. Commission is charged per trade; slippage only on stop and market exits.

New setup (tradeable from the first minute after candle 4 closes, + `delay` minutes):
  1. weekend: candle 4 closed between Friday 20:30 UTC and Sunday 23:00 UTC (= Monday 00:00 in Lagos) -> ignored.
  2. lookback (option): at least 3 of the 5 candles before candle 1 go the trade's way (dojis count for neither side).
  3. a trade is open -> ignored (the open trade ends only by stop, target, breakeven stop or the Friday close).
  4. intent: candle 4 must close on the trade's side of the midpoint (buy above it, sell below it); otherwise skipped
     ("price above the midpoint shows no intent").
  5. entry level: 50% of the range (the midpoint) or 70% (a 70% pull-back: buy hi - 0.7 x range, sell lo + 0.7 x range).
     If price is already through that level when the order would be placed, it is skipped.
  6. stop = far end of the range + buffer x range; 1R = entry level to stop; target = entry level +/- 4R; breakeven
     level = +2R. All three are fixed prices set with the order (as in MT5); a gap fill at a better price keeps them.
     A setup whose 1R is not bigger than the round-trip cost cannot be traded and is skipped.
  7. pending orders: same direction -> the new order is added; when one order fills, all other pending orders are
     removed. Opposite direction -> the new setup replaces all pending orders if its range is wider than every one of
     them, otherwise it is ignored.
Pending order: fills when price trades at its level (buy: ask <= level; sell: bid >= level), not in the daily
  rollover block 20:30-23:00 UTC. Cancelled if price reaches its target level first (same minute: cancelled), or at the
  Friday cutoff, or by a wider opposite setup.
Trade: stop first if stop and target fall in the same minute; the fill minute can only stop out. Breakeven (option):
  once price reaches +2R the stop moves to the entry price from the next minute. Closed at market at Friday 20:30 UTC.
  Trades that span a hole in the data are dropped (as everywhere in the lab). Swaps: nights held x swap per night.
"""
import datetime as dt
import numpy as np

import body4_scan as SC

WEEK = 7 * 86400
FRI_CUT = 4 * 86400 + 20 * 3600 + 1800      # Friday 20:30 UTC, seconds from Monday 00:00 UTC
SUN_OPEN = 6 * 86400 + 23 * 3600            # Sunday 23:00 UTC = Monday 00:00 WAT
BLOCK = (20 * 3600 + 1800, 23 * 3600)       # daily rollover: no fills


def week_sec(t):
    return (int(t) - 345600) % WEEK          # 1970-01-05 00:00 UTC was a Monday


def weekend(t):
    s = week_sec(t)
    return FRI_CUT <= s < SUN_OPEN


def day_cut_after(t):
    """The next 20:30 UTC at or after t (daily close before the rollover; safe-window mode)."""
    s = int(t) % 86400
    return int(t) - s + 73800 if s < 73800 else int(t) - s + 86400 + 73800


def friday_cut_after(t):
    """The Friday 20:30 UTC that ends the trading week containing t."""
    s = week_sec(t)
    base = int(t) - s
    return base + FRI_CUT if s < FRI_CUT else base + WEEK + FRI_CUT


def nights_held(t_in, t_out):
    """22:00 UTC rollovers between entry and exit on weekdays; Wednesday counts three times (as research/northstar/core)."""
    n = 0
    for d in range(int(t_in) // 86400, int(t_out) // 86400 + 1):
        rt = d * 86400 + 79200
        if t_in < rt <= t_out:
            wd = (d + 3) % 7
            if wd < 5:
                n += 3 if wd == 2 else 1
    return n


def patterns(B, tf_min, sample="flow", doji_bullish=False):
    """B = dict(t, o, h, l, c) of the pattern timeframe. List of setups in time order."""
    P = SC.setups(B, tf_min, sample=sample, doji_bullish=doji_bullish)
    out = []
    for j in range(len(P["k"])):
        k = int(P["k"][j])
        out.append(dict(id=j + 1, k=k, side=int(P["side"][j]), hi=float(P["hi"][j]), lo=float(P["lo"][j]),
                        width=float(P["hi"][j] - P["lo"][j]), mid=float((P["hi"][j] + P["lo"][j]) / 2),
                        c4=float(B["c"][k]), lookback=int(P["lookback"][j]), t1=int(B["t"][k - 3]),
                        t_conf=int(B["t"][k]) + tf_min * 60))
    return out


def run(M, pats, spread, commission, slippage, swap=0.0, entry=0.5, buffer=0.0, breakeven=True, use_lookback=True,
        target_r=4.0, be_r=2.0, cut=2 ** 62, delay=0, gaps=(), day_close=False):
    """M = dict(ts, o, h, l, c) M1 bid bars. Returns (trades, log)."""
    ts, o, h, l, c = M["ts"], M["o"], M["h"], M["l"], M["c"]
    N = len(ts)
    cost = spread + commission + slippage
    gaps = np.asarray(gaps, np.int64)
    trades, log = [], []
    pend = []                                   # pending orders (all the same direction)
    pos = None
    stats = dict(ambiguous=0)
    starts = np.searchsorted(ts, np.array([p["t_conf"] for p in pats], np.int64) + 60 * delay)
    pj = 0
    cut_after = day_cut_after if day_close else friday_cut_after

    def stamp(i):
        return dt.datetime.fromtimestamp(int(ts[i]), dt.timezone.utc).strftime("%a %Y-%m-%d %H:%M")

    def name(p):
        return f"pattern #{p['id']} {'SELL' if p['side'] < 0 else 'BUY'} (range {p['width']:.5g}, lookback {p['lookback']}/5)"

    def close(i, t_out, px, why):
        nonlocal pos
        s = pos["side"]; d = pos["risk"]
        gross = (px - pos["entry"]) / d * s
        nights = nights_held(pos["t_in"], t_out)
        fin = nights * swap / d
        net = gross - commission / d - fin
        span_gap = bool(np.any((gaps > pos["i_in"]) & (gaps <= i)))
        log.append((ts[min(i, N - 1)], f"{stamp(min(i, N - 1))}  pattern #{pos['p']['id']} closed: {why} at {px:.5g} "
                    f"({net:+.2f}R after costs{', swaps' if fin else ''})" + ("  [spans a data hole: dropped]" if span_gap else "")))
        if not span_gap:
            trades.append(dict(id=pos["p"]["id"], side=s, t_in=pos["t_in"], t_out=int(t_out), entry=pos["entry"],
                               stop0=pos["stop0"], tp=pos["tp"], be=pos["be"], exit=px, R=net, gross=gross, risk=d,
                               cost_r=cost / d, nights=nights, fin_r=fin, reason=why, moved=pos["moved"], pattern=pos["p"]))
        pos = None

    for i in range(N):
        t = int(ts[i])
        # Friday cutoff (the data usually jumps from Friday evening to Sunday night)
        if pos is not None and t >= pos["cut"]:
            px = c[i - 1] - slippage if pos["side"] > 0 else c[i - 1] + spread + slippage
            close(i - 1, pos["cut"], px, "daily close" if day_close else "Friday close")
        if pend and t >= pend[0]["cut"]:
            for q in pend:
                log.append((t, f"{stamp(i)}  pattern #{q['p']['id']} pending order cancelled: {'daily' if day_close else 'Friday'} close"))
            pend = []
        if t >= cut:
            if pend:
                pend = []
            if pos is None:
                break
        # new setups that became tradeable
        while pj < len(pats) and starts[pj] <= i:
            p = pats[pj]; pj += 1
            if t >= cut:
                continue
            s = p["side"]
            if not p.get("allow", True):
                log.append((t, f"{stamp(i)}  {name(p)}: ignored, outside the safe window or on a news day")); continue
            if weekend(p["t_conf"]) or weekend(t):
                log.append((t, f"{stamp(i)}  {name(p)}: ignored, formed in the weekend window")); continue
            if use_lookback and p["lookback"] < 3:
                log.append((t, f"{stamp(i)}  {name(p)}: ignored, fewer than 3 of the 5 lookback candles in its direction")); continue
            if pos is not None:
                log.append((t, f"{stamp(i)}  {name(p)}: ignored, a trade is open")); continue
            if (s > 0 and not p["c4"] > p["mid"]) or (s < 0 and not p["c4"] < p["mid"]):
                log.append((t, f"{stamp(i)}  {name(p)}: skipped, candle 4 closed beyond the midpoint (no intent)")); continue
            lvl = p["hi"] - entry * p["width"] if s > 0 else p["lo"] + entry * p["width"]
            if (s > 0 and o[i] + spread <= lvl) or (s < 0 and o[i] >= lvl):
                log.append((t, f"{stamp(i)}  {name(p)}: skipped, price already through the entry level")); continue
            stop = p["lo"] - buffer * p["width"] if s > 0 else p["hi"] + buffer * p["width"]
            risk = abs(lvl - stop)
            if risk <= cost:
                log.append((t, f"{stamp(i)}  {name(p)}: skipped, 1R ({risk:.5g}) not bigger than the round-trip cost")); continue
            order = dict(p=p, side=s, level=lvl, stop=stop, risk=risk, tp=lvl + s * target_r * risk, be=lvl + s * be_r * risk,
                         width=p["width"], cut=cut_after(t))
            if pend and pend[0]["side"] != s:
                if p["width"] > max(q["width"] for q in pend):
                    log.append((t, f"{stamp(i)}  {name(p)}: opposite direction, WIDER than every pending order: replaces "
                                + ", ".join(f"#{q['p']['id']}" for q in pend)))
                    pend = []
                else:
                    log.append((t, f"{stamp(i)}  {name(p)}: opposite direction, not wider than pending "
                                + ", ".join(f"#{q['p']['id']}" for q in pend) + ": ignored")); continue
            pend.append(order)
            log.append((t, f"{stamp(i)}  {name(p)}: limit order at {lvl:.5g} ({int(entry * 100)}% of the range), stop {stop:.5g}, "
                        f"target {order['tp']:.5g}"))
        # pending orders
        if pend and pos is None:
            sod = t % 86400
            blocked = BLOCK[0] <= sod < BLOCK[1]
            keep, filled = [], []
            for q in pend:
                s = q["side"]
                hit_tp = (h[i] >= q["tp"]) if s > 0 else (l[i] + spread <= q["tp"])
                hit = (not blocked) and ((l[i] + spread <= q["level"]) if s > 0 else (h[i] >= q["level"]))
                if hit_tp:
                    if hit:
                        stats["ambiguous"] += 1
                    log.append((t, f"{stamp(i)}  pattern #{q['p']['id']} pending order cancelled: price reached its target first"))
                elif hit:
                    filled.append(q)
                else:
                    keep.append(q)
            pend = keep
            if filled:
                # a falling price meets the highest buy level first; a rising price the lowest sell level
                q = max(filled, key=lambda x: x["level"]) if filled[0]["side"] > 0 else min(filled, key=lambda x: x["level"])
                s = q["side"]
                px = min(q["level"], o[i] + spread) if s > 0 else max(q["level"], o[i])     # a gap fills at the open
                # stop, target and breakeven level are fixed prices set with the order; 1R = planned entry to stop
                pos = dict(p=q["p"], side=s, entry=px, stop=q["stop"], stop0=q["stop"], risk=q["risk"], tp=q["tp"],
                           be=q["be"], moved=False, i_in=i, t_in=t, cut=cut_after(t))
                others = [x for x in pend + filled if x is not q]
                log.append((t, f"{stamp(i)}  pattern #{q['p']['id']} {'SELL' if s < 0 else 'BUY'} filled at {px:.5g}"
                            + (("; removed pending " + ", ".join(f"#{x['p']['id']}" for x in others)) if others else "")))
                pend = []
                if (l[i] <= pos["stop"]) if s > 0 else (h[i] + spread >= pos["stop"]):
                    stats["ambiguous"] += 1
                    px2 = (min(pos["stop"], o[i]) - slippage) if s > 0 else (max(pos["stop"], o[i] + spread) + slippage)
                    close(i, t, px2, "stop (-1R), same minute as the fill")
            continue
        # open trade, from the minute after the fill
        if pos is not None and i > pos["i_in"]:
            s = pos["side"]
            hit_sl = (l[i] <= pos["stop"]) if s > 0 else (h[i] + spread >= pos["stop"])
            hit_tp = (h[i] >= pos["tp"]) if s > 0 else (l[i] + spread <= pos["tp"])
            if hit_sl:
                if hit_tp:
                    stats["ambiguous"] += 1
                if s > 0:
                    px = (o[i] if o[i] < pos["stop"] else pos["stop"]) - slippage
                else:
                    px = (o[i] + spread if o[i] + spread > pos["stop"] else pos["stop"]) + slippage
                close(i, t, px, "breakeven stop" if pos["moved"] else "stop (-1R)")
            elif hit_tp:
                px = max(pos["tp"], o[i]) if s > 0 else min(pos["tp"], o[i] + spread)
                close(i, t, px, f"target (+{target_r:g}R)")
            elif breakeven and not pos["moved"] and ((h[i] >= pos["be"]) if s > 0 else (l[i] + spread <= pos["be"])):
                pos["stop"] = pos["entry"]; pos["moved"] = True
                log.append((t, f"{stamp(i)}  pattern #{pos['p']['id']} reached +{be_r:g}R: stop moved to the entry price"))
    return trades, log, stats

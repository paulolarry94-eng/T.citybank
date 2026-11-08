"""Reference simulator for the owner's body-engulf 4-candle range (Q30), with the owner's answers of 2026-11-07.
Plain Python on purpose: it is the written specification. The fast (numba) engine for the full backtest must match it
trade for trade.

Patterns are found on bars of the chosen timeframe (body4_scan.py); orders and trades are run on M1 bars.
Per market there is ONE slot: a pending order or an open trade.
  New pattern (tradeable from the first minute after the 4th candle closes):
    - Friday cutoff to Sunday 22:00 UTC: ignored (no trade starts over the weekend).
    - lookback filter (option): among the 5 candles BEFORE candle 1, at least 3 in the trade's direction.
    - a trade is open: the pattern is ignored (assumption: an open trade is only closed by stop / target / Friday).
    - an order is pending: same direction -> the newer replaces it; opposite direction -> the wider range wins.
    - price already past the midpoint (buy: ask <= midpoint; sell: bid >= midpoint): option "market" enters now at
      market, option "skip" ignores the pattern. Otherwise a limit order rests at the midpoint.
  Pending order: filled when price trades at the midpoint; cancelled if price reaches the target level first
    (same minute: cancelled, the cautious reading), when replaced, or at the Friday cutoff. No other expiry.
  Trade: stop = far end of the range + buffer (fraction of the range); 1R = entry to stop; target = 4R;
    breakeven (option): once price reaches +2R the stop moves to the entry price. Stop and target in the same minute:
    stop first. Closed at market at the Friday cutoff. Overnight holds Mon-Thu pay swaps (counted as nights).
  Costs: `cost` = round-trip cost in price, paid as the spread (buy at bid + cost, sell exits at ask = bid + cost).
"""
import datetime as dt
import numpy as np

import body4_scan as SC

FRI_CUT = 4 * 86400 + 20 * 3600 + 1800      # Friday 20:30 UTC, seconds from Monday 00:00
WEEK_OPEN = 6 * 86400 + 22 * 3600           # Sunday 22:00 UTC


def week_sec(t):
    return (int(t) - 345600) % (7 * 86400)  # 1970-01-05 was a Monday


def weekend(t):
    s = week_sec(t)
    return s >= FRI_CUT and s < WEEK_OPEN


def atr(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h, pc) - np.minimum(l, pc)
    out = np.convolve(tr, np.ones(n) / n, "full")[:len(tr)]
    out[:n - 1] = np.nan
    return out


def patterns(B, tf_min):
    """B = dict(t, o, h, l, c) of the pattern timeframe. Returns a list of dicts in time order."""
    o, h, l, c = B["o"], B["h"], B["l"], B["c"]
    a = atr(h, l, c)
    out = []
    for k, side, hi, lo, mid, stop, risk in SC.detect(o, h, l, c):
        before = range(k - 8, k - 3)
        n_dir = sum(1 for i in before if i >= 0 and ((c[i] > o[i]) if side > 0 else (c[i] < o[i])))
        out.append(dict(k=k, side=side, hi=hi, lo=lo, mid=mid, width=hi - lo, t1=int(B["t"][k - 3]),
                        t_conf=int(B["t"][k]) + tf_min * 60, lookback=n_dir, lookback_ok=n_dir >= 3,
                        body2=abs(c[k - 2] - o[k - 2]) / a[k] if np.isfinite(a[k]) else np.nan,
                        body4=abs(c[k] - o[k]) / a[k] if np.isfinite(a[k]) else np.nan, c4=float(c[k])))
    return out


def run(M, pats, cost, beyond="market", buffer=0.0, breakeven=True, use_lookback=True, target_r=4.0, be_r=2.0,
        t_from=None, t_to=None):
    """M = dict(ts, o, h, l, c) M1 bid bars. Returns (trades, log)."""
    ts, o, h, l, c = M["ts"], M["o"], M["h"], M["l"], M["c"]
    i0 = 0 if t_from is None else int(np.searchsorted(ts, t_from))
    i1 = len(ts) if t_to is None else int(np.searchsorted(ts, t_to))
    pats = [p for p in pats if (t_from is None or p["t_conf"] >= t_from) and (t_to is None or p["t_conf"] < t_to)]
    trades, log = [], []
    pend = pos = None
    pj = 0

    def stamp(i):
        return dt.datetime.fromtimestamp(int(ts[i]), dt.timezone.utc).strftime("%a %Y-%m-%d %H:%M")

    def open_trade(p, i, entry, how):
        stop = p["hi"] + buffer * p["width"] if p["side"] < 0 else p["lo"] - buffer * p["width"]
        risk = abs(entry - stop)
        if risk <= cost:
            log.append((ts[i], f"{stamp(i)}  pattern #{p['id']}: stop closer than costs, skipped")); return None
        tp = entry - target_r * risk if p["side"] < 0 else entry + target_r * risk
        be = entry - be_r * risk if p["side"] < 0 else entry + be_r * risk
        log.append((ts[i], f"{stamp(i)}  pattern #{p['id']} {'SELL' if p['side'] < 0 else 'BUY'} filled {how} at {entry:.5g}"))
        return dict(p=p, i_in=i, entry=entry, stop=stop, stop0=stop, tp=tp, be=be, moved=False, how=how)

    def close_trade(i, px, why):
        nonlocal pos
        s = pos["p"]["side"]
        r = (px - pos["entry"]) / abs(pos["entry"] - pos["stop0"]) * (1 if s > 0 else -1)
        trades.append(dict(id=pos["p"]["id"], side=s, t_in=int(ts[pos["i_in"]]), t_out=int(ts[i]), i_in=pos["i_in"], i_out=i,
                           entry=pos["entry"], stop0=pos["stop0"], tp=pos["tp"], be=pos["be"], exit=px, R=r, reason=why,
                           how=pos["how"], pattern=pos["p"]))
        log.append((ts[i], f"{stamp(i)}  pattern #{pos['p']['id']} closed: {why} at {px:.5g} ({r:+.2f}R before swaps)"))
        pos = None

    for i in range(i0, i1):
        t = ts[i]
        # Friday cutoff: close everything
        if weekend(t):
            if pos is not None:
                close_trade(i, o[i] + cost if pos["p"]["side"] < 0 else o[i], "Friday close")
            if pend is not None:
                log.append((t, f"{stamp(i)}  pattern #{pend['id']} pending order cancelled: Friday close")); pend = None
        # new patterns that became tradeable
        while pj < len(pats) and pats[pj]["t_conf"] <= t:
            p = pats[pj]; pj += 1
            p.setdefault("id", pj)
            name = f"pattern #{p['id']} {'SELL' if p['side'] < 0 else 'BUY'} (range {p['width']:.5g}, lookback {p['lookback']}/5)"
            if weekend(t) or weekend(p["t_conf"]):
                log.append((t, f"{stamp(i)}  {name}: ignored, formed in the Friday-to-Sunday window")); continue
            if use_lookback and not p["lookback_ok"]:
                log.append((t, f"{stamp(i)}  {name}: ignored, lookback has fewer than 3 candles in its direction")); continue
            if pos is not None:
                log.append((t, f"{stamp(i)}  {name}: ignored, a trade is open")); continue
            if pend is not None:
                if pend["side"] == p["side"]:
                    log.append((t, f"{stamp(i)}  {name}: same direction, replaces pending #{pend['id']}"))
                elif p["width"] > pend["width"]:
                    log.append((t, f"{stamp(i)}  {name}: opposite direction with a WIDER range, replaces pending #{pend['id']}"))
                else:
                    log.append((t, f"{stamp(i)}  {name}: opposite direction with a narrower range, ignored (keeps #{pend['id']})"))
                    continue
                pend = None
            past = (o[i] + cost <= p["mid"]) if p["side"] > 0 else (o[i] >= p["mid"])
            if past:
                if beyond == "skip":
                    log.append((t, f"{stamp(i)}  {name}: price already past the midpoint, skipped")); continue
                pos = open_trade(p, i, o[i] + cost if p["side"] > 0 else o[i], "at market (price already past the midpoint)")
            else:
                pend = p
                log.append((t, f"{stamp(i)}  {name}: limit order at midpoint {p['mid']:.5g}"))
        # pending order
        if pend is not None and pos is None:
            p = pend; s = p["side"]
            stop_ = p["hi"] + buffer * p["width"] if s < 0 else p["lo"] - buffer * p["width"]
            risk_ = abs(p["mid"] - stop_)
            tp_ = p["mid"] - target_r * risk_ if s < 0 else p["mid"] + target_r * risk_
            hit_tp = (l[i] + cost <= tp_) if s < 0 else (h[i] >= tp_)
            hit_mid = (h[i] >= p["mid"]) if s < 0 else (l[i] + cost <= p["mid"])
            if hit_tp:
                log.append((t, f"{stamp(i)}  pattern #{p['id']} pending order cancelled: price reached the target before filling"))
                pend = None
            elif hit_mid:
                pend = None
                pos = open_trade(p, i, p["mid"], "by the limit at the midpoint")
                if pos is not None and ((h[i] + cost >= pos["stop"]) if s < 0 else (l[i] <= pos["stop"])):
                    close_trade(i, pos["stop"], "stop (-1R)")
            continue
        # open trade (from the minute after the fill)
        if pos is not None and i > pos["i_in"]:
            s = pos["p"]["side"]
            if (h[i] + cost >= pos["stop"]) if s < 0 else (l[i] <= pos["stop"]):
                gap = (o[i] + cost > pos["stop"]) if s < 0 else (o[i] < pos["stop"])
                px = (o[i] + cost if s < 0 else o[i]) if gap else pos["stop"]
                close_trade(i, px, "breakeven stop" if pos["moved"] else "stop (-1R)")
            elif (l[i] + cost <= pos["tp"]) if s < 0 else (h[i] >= pos["tp"]):
                close_trade(i, pos["tp"], f"target (+{target_r:g}R)")
            elif breakeven and not pos["moved"] and ((l[i] + cost <= pos["be"]) if s < 0 else (h[i] >= pos["be"])):
                pos["stop"] = pos["entry"]; pos["moved"] = True
                log.append((t, f"{stamp(i)}  pattern #{pos['p']['id']} reached +{be_r:g}R: stop moved to breakeven"))
    return trades, log

"""Hunt 2, step 2: hold-through-a-window strategies (one round trip a day) and flow tests.

Window search: for each instrument and London-local window [a, b) with 0 <= a < b <= 21
(the 21:00-24:00 London rollover hours are excluded: spreads widen there and bid data dips),
direction chosen on 2011-2018 only, net of one all-in cost per day. Reported out-of-sample
2019-2025 for the in-sample winners only.
"""
import os, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "orb"))
import core

LDN = ZoneInfo("Europe/London")


def day_hours(M, tz=LDN):
    """Matrix [day, hour] of local-hour moves (NaN when missing) plus day years and weekday."""
    ts = M.ts
    days = np.unique(ts // 86400)
    off = {int(d): int(dt.datetime.fromtimestamp(int(d) * 86400 + 43200, tz).utcoffset().total_seconds()) for d in days}
    loc = ts + np.array([off[int(d)] for d in ts // 86400])
    key = loc // 3600
    st = np.flatnonzero(np.r_[True, key[1:] != key[:-1]]); en = np.r_[st[1:], len(ts)] - 1
    ok = (en - st + 1) >= 45
    dkey = key[st] // 24; hr = key[st] % 24
    ud, di = np.unique(dkey, return_inverse=True)
    X = np.full((len(ud), 24), np.nan)
    X[di[ok], hr[ok]] = (M.c[en] - M.o[st])[ok]
    yr = np.array([dt.datetime.utcfromtimestamp(int(d) * 86400).year for d in ud])
    wd = ((ud + 3) % 7) < 5
    return X[wd], yr[wd], ud[wd]


def search(sym):
    M = core.Market(sym)
    X, yr, ud = day_hours(M)
    c = M.cost
    res = []
    for a in range(0, 21):
        for b in range(a + 1, 22):
            w = X[:, a:b]
            ok = ~np.isnan(w).any(axis=1)
            mv = w[ok].sum(axis=1); y = yr[ok]
            IS, OS = mv[y <= 2018], mv[y >= 2019]
            s = np.sign(IS.mean())
            n_is = s * IS - c; n_os = s * OS - c
            t_is = n_is.mean() / n_is.std() * np.sqrt(len(n_is)); t_os = n_os.mean() / n_os.std() * np.sqrt(len(n_os))
            yrs = sum((s * mv[y == q] - c).mean() > 0 for q in range(2011, 2026))
            res.append((a, b, "long" if s > 0 else "short", n_is.mean() / c, t_is, n_os.mean() / c, t_os, yrs, (s * IS).mean() / c))
    res.sort(key=lambda r: -r[4])
    print(f"\n{sym}: top windows by in-sample t (net of one cost/day; values in cost units)")
    print("  window(London)  side   IS net  IS t   OOS net OOS t  yrs+  IS gross")
    for r in res[:8]:
        print(f"  {r[0]:02d}:00-{r[1]:02d}:00     {r[2]:5s}  {r[3]:+.3f} {r[4]:+5.2f}  {r[5]:+.3f} {r[6]:+5.2f}  {r[7]:2d}   {r[8]:+.3f}")
    return M, X, yr, ud


def gotobi(M):
    """USDJPY 09:00 -> 09:55 JST (00:00 -> 00:55 UTC) on gotobi vs other days."""
    ts = M.ts
    out = {True: [], False: []}
    days = np.unique(ts // 86400)
    for d in days:
        D = dt.datetime.utcfromtimestamp(int(d) * 86400).date()
        if D.weekday() >= 5:
            continue
        # gotobi: day-of-month multiple of 5, or last business day; weekend gotobi moves to the Friday before
        nxt = [D + dt.timedelta(days=k) for k in range(1, 4)]
        is_g = D.day % 5 == 0
        for n in nxt:                      # a gotobi date falling on the coming weekend is settled today (Friday)
            if n.weekday() >= 5 and n.day % 5 == 0 and D.weekday() == 4:
                is_g = True
        last_bd = (D + dt.timedelta(days=1)).month != D.month or (D.weekday() == 4 and (D + dt.timedelta(days=3)).month != D.month)
        is_g = is_g or last_bd
        t0 = int(d) * 86400 + 0 * 3600; t1 = t0 + 55 * 60; tm = t0 - 3 * 3600
        a = np.searchsorted(ts, tm); b = np.searchsorted(ts, t0); e = np.searchsorted(ts, t1)
        if e >= len(ts) or b >= len(ts) or ts[e] - t1 > 120 or ts[b] - t0 > 120:
            continue
        out[is_g].append((D.year, M.o[b], M.o[e], M.o[a]))
    for k, lab in ((True, "gotobi"), (False, "other ")):
        A = np.array(out[k]); mv = (A[:, 2] - A[:, 1]) / M.cost; pre = (A[:, 1] - A[:, 3]) / M.cost
        y = A[:, 0]
        for nm, x in (("09:00-09:55 JST", mv), ("06:00-09:00 JST", pre)):
            i, o = x[y <= 2018], x[y >= 2019]
            print(f"  {lab} {nm}: n={len(x)} mean {x.mean():+.3f} cost | IS {i.mean():+.3f} (t {i.mean()/i.std()*np.sqrt(len(i)):+.2f}) "
                  f"OOS {o.mean():+.3f} (t {o.mean()/o.std()*np.sqrt(len(o)):+.2f}) | yrs+ {sum(x[y==q].mean()>0 for q in range(2011,2026))}/15")


def wmr(M):
    """Move into the 16:00 London fix (15:30-16:00) vs the hour after (16:00-17:00)."""
    ts = M.ts
    rows = []
    for d in np.unique(ts // 86400):
        D = dt.datetime.utcfromtimestamp(int(d) * 86400).date()
        if D.weekday() >= 5:
            continue
        t16 = int(dt.datetime(D.year, D.month, D.day, 16, 0, tzinfo=LDN).timestamp())
        i0, i1, i2 = (np.searchsorted(ts, t) for t in (t16 - 1800, t16, t16 + 3600))
        if i2 >= len(ts) or ts[i2] - (t16 + 3600) > 120 or ts[i0] - (t16 - 1800) > 120:
            continue
        me = (D + dt.timedelta(days=1)).month != D.month or (D.weekday() == 4 and (D + dt.timedelta(days=3)).month != D.month)
        rows.append((D.year, me, M.o[i0], M.o[i1], M.o[i2]))
    A = np.array(rows, dtype=float)
    pre = (A[:, 3] - A[:, 2]) / M.cost; post = (A[:, 4] - A[:, 3]) / M.cost
    for lab, k in (("all days", np.ones(len(A), bool)), ("month-end", A[:, 1] == 1)):
        x = -np.sign(pre[k]) * post[k]          # fade the pre-fix move for the next hour, gross
        y = A[k, 0]
        i, o = x[y <= 2018], x[y >= 2019]
        print(f"  WMR fade {lab}: n={k.sum()} gross {x.mean():+.3f} cost | IS {i.mean():+.3f} (t {i.mean()/i.std()*np.sqrt(len(i)):+.2f}) "
              f"OOS {o.mean():+.3f} (t {o.mean()/o.std()*np.sqrt(len(o)):+.2f}) | corr(pre,post) {np.corrcoef(pre[k], post[k])[0,1]:+.3f}")


if __name__ == "__main__":
    for sym in core.SYMS:
        M, X, yr, ud = search(sym)
        if sym == "USDJPY":
            print("\nUSDJPY gotobi (Tokyo fix 09:55 JST), cost units:")
            gotobi(M)
        if sym != "XAUUSD":
            print(f"\n{sym} London 4pm fix:")
            wmr(M)

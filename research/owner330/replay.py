"""Replay check: does the scanner make the owner's calls on the owner's own example days (Oct 2026)?

    python3 research/owner330/replay.py            # writes research/results/owner330/replay.json, REPLAY.md and charts

Data: our 2026 minute data (data/holdout: Exness ticks for XAUUSD, GBPUSD, USDJPY; HistData for EURGBP), with 2025 before it
for the EMA warm-up. The owner's charts are TradingView (FXCM gold, ICE FX), so prices differ by a fraction of a pip and
an EMA touch can flip; every difference is shown, not hidden. Anchor wat1530 (15:30 Nigerian time = 14:30 UTC), the time
the owner's October charts use. This is an implementation check, not a performance test.
"""
import os, sys, json, types, importlib.util, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, os.path.join(ROOT, "research", "northstar"))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import engine as E   # noqa: E402

_spec = importlib.util.spec_from_file_location("o330", os.path.join(ROOT, "research", "truth", "strategies", "owner330_ema_retest_v1.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)
OUT = os.path.join(ROOT, "research", "results", "owner330")
WAT = S.WAT

# the owner's calls, from the owner's charts and notes (times in Nigerian time, WAT)
EXAMPLES = [
    dict(sym="XAUUSD", date="2026-10-20", owner="no trade: the 15:30 candle does not cross the EMA"),
    dict(sym="XAUUSD", date="2026-10-21", owner="invalid: the 15:30 body stays above the EMA"),
    dict(sym="XAUUSD", date="2026-10-29", owner="SELL; reference M5 16:40; entry 4022.67 (low), stop 4025.98 (high), 3R hit ~17:30",
         side=-1, ref="16:40", entry=4022.67, stop=4025.98),
    dict(sym="GBPUSD", date="2026-10-28", owner="BUY; 16:00 no setup (closed above the range); reference 16:55; entry 1.3302, "
         "stop 1.3298, 4R 1.3318 hit", side=1, ref="16:55", entry=1.3302, stop=1.3298),
    dict(sym="GBPUSD", date="2026-10-27", owner="SELL; displaced reference 16:05, entry at its 50% 1.3321, stop 1.3325, 4R 1.3305",
         side=-1, ref="16:05", entry=1.3321, stop=1.3325),
    dict(sym="GBPUSD", date="2026-10-23", owner="reference formed but price never broke it: no entry", side=1),
    dict(sym="GBPUSD", date="2026-10-15", owner="SELL; entry about 17:20 at 1.3252, stop 1.3258, target 1.3243 (a loss)",
         side=-1, entry=1.3252, stop=1.3258),
    dict(sym="EURGBP", date="2026-10-23", owner="SELL bias; M5 broke above the range: no trade", side=-1),
    dict(sym="EURGBP", date="2026-10-27", owner="BUY; reference 16:00 (high 0.83674, low 0.83647); entered on the pullback ~16:35",
         side=1, ref="16:00", entry=0.83674, stop=0.83647),
    dict(sym="USDJPY", date="2026-10-27", owner="owner's test; my answer: invalid anchor (opened on/below the EMA), no trade"),
]


class Market2026:
    """Minute data for 2025-2026 with the lab's cleaning (duplicates and flat filler minutes dropped)."""
    def __init__(self, sym, cost, path2026=None):
        parts = []
        for f in (os.path.join(ROOT, "data", f"{sym}_M1_bid_2025.npz"),
                  path2026 or os.path.join(ROOT, "data", "holdout", f"{sym}_M1_bid_2026.npz")):
            d = np.load(f); parts.append((d["ts"] // 1000, d["o"], d["h"], d["l"], d["c"]))
        ts = np.concatenate([p[0] for p in parts]).astype(np.int64)
        o, h, l, c = (np.concatenate([p[i] for p in parts]).astype(float) for i in (1, 2, 3, 4))
        k = np.argsort(ts, kind="stable"); ts, o, h, l, c = ts[k], o[k], h[k], l[k], c[k]
        keep = np.r_[True, ts[1:] != ts[:-1]]
        flat = (o == h) & (h == l) & (l == c); flat[1:] &= o[1:] == c[:-1]; flat[0] = False
        keep &= ~flat
        self.sym, self.cost = sym, cost
        self.ts, self.o, self.h, self.l, c = ts[keep], o[keep], h[keep], l[keep], c[keep]
        self.G = types.SimpleNamespace(c=c); self.gaps = E.data_gaps(self.ts); self._b = {}

    def bars(self, tf):
        m = {"M5": 5, "M30": 30}[tf]
        if tf not in self._b:
            bt, bo, bh, bl, bc, nxt = E.resample(self.ts, self.o, self.h, self.l, self.G.c, m, 0)
            self._b[tf] = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt.astype(np.int64), minutes=m)
        return self._b[tf]


def wat(t):
    return dt.datetime.fromtimestamp(int(t), WAT).strftime("%H:%M")


def anchor_facts(M, D):
    """The 15:30 WAT M30 candle and the EMA it is judged against (previous candle's EMA, as the scanner does)."""
    B = M.bars("M5"); t5 = B["t"]; g = t5 // 1800
    st = np.flatnonzero(np.r_[True, g[1:] != g[:-1]]); en = np.r_[st[1:], len(t5)]
    m30_t = g[st] * 1800; c30 = B["c"][en - 1]; e30 = S.ema(c30)
    ta, _ = S.anchor_times(D, "wat1530")
    i = int(np.searchsorted(m30_t, ta))
    if i >= len(m30_t) or m30_t[i] != ta:
        return None
    return dict(open=float(B["o"][st[i]]), close=float(c30[i]), high=float(np.max(B["h"][st[i]:en[i]])),
                low=float(np.min(B["l"][st[i]:en[i]])), ema_before=float(e30[i - 1]), ema_on_candle=float(e30[i]))


def run_example(ex, markets, news):
    M = markets[ex["sym"]]; B = M.bars("M5"); D = dt.date.fromisoformat(ex["date"])
    S._CACHE.clear(); S.NEWS = news
    res = dict(ex, anchor=anchor_facts(M, D), news_day=D in S._NEWS_ALL, configs={})
    for entry in ("A", "B6"):
        p = dict(tf="M5", anchor="wat1530", entry=entry, target=3 if ex["sym"] == "XAUUSD" else 4, be=0)
        st = S.setups(B, p, M)
        k = [i for i, dd in enumerate(st["date"]) if dd == D.toordinal()]
        tr = S.detail(M, B, p)
        trs = [r for r in tr if int(r[14]) in k]
        row = dict(setup=None, trade=None)
        if k:
            i = k[0]
            row["setup"] = dict(side=int(st["side"][i]), ref_time=wat(B["t"][st["j"][i]]), ref_high=float(st["rhi"][i]),
                                ref_low=float(st["rlo"][i]), displaced=bool(st["disp"][i]), range_high=float(st["H"][i]),
                                range_low=float(st["L"][i]))
        if trs:
            r = trs[0]
            row["trade"] = dict(entry_time=wat(r[0]), entry=float(r[8]), stop=float(r[9]), target=float(r[10]),
                                exit_time=wat(r[1]), exit=float(r[11]), reason=S.REASON[int(r[12])], R=round(float(r[3]), 2))
        res["configs"][entry] = row
    return res


def fmt(x, sym):
    return f"{x:.2f}" if sym in ("XAUUSD", "USDJPY") else f"{x:.5f}"


def report(rows):
    L = ["# Replay check: the scanner on the owner's example days (Oct 2026, anchor 15:30 Nigerian time)", "",
         "Owner's calls from the owner's charts; scanner on our data (TradingView prices differ slightly). Times are WAT.", "",
         "| Market | Date | Owner | Anchor candle (open / close vs EMA before it) | Scanner, entry A | Scanner, entry B6 |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        a = r["anchor"]; sym = r["sym"]
        if a:
            side = "SELL" if (a["open"] > a["ema_before"] and a["close"] < a["ema_before"]) else \
                   ("BUY" if (a["open"] < a["ema_before"] and a["close"] > a["ema_before"]) else "no cross")
            anc = f"o {fmt(a['open'], sym)} / c {fmt(a['close'], sym)} vs EMA {fmt(a['ema_before'], sym)}: {side}"
        else:
            anc = "no data"
        cells = []
        for e in ("A", "B6"):
            c = r["configs"][e]
            if r.get("news_day_skipped"):
                cells.append("skipped (news day)")
            elif not c["setup"]:
                cells.append("no setup")
            else:
                s_ = c["setup"]; t = c["trade"]
                txt = f"{'SELL' if s_['side'] < 0 else 'BUY'} ref {s_['ref_time']}{' (displaced)' if s_['displaced'] else ''}"
                txt += (f"; in {t['entry_time']} @ {fmt(t['entry'], sym)}, stop {fmt(t['stop'], sym)}; out {t['exit_time']} "
                        f"{t['reason']} {t['R']:+.2f}R") if t else "; no fill"
                cells.append(txt)
        L.append(f"| {sym} | {r['date']}{' (news day)' if r['news_day'] else ''} | {r['owner']} | {anc} | {cells[0]} | {cells[1]} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    import charts
    S._NEWS_ALL = set(S.NEWS)
    costs = {**{k: v["cost"] for k, v in json.load(open(os.path.join(ROOT, "research", "truth", "costs.json"))).items()
                if isinstance(v, dict)}, **S.COSTS}
    markets = {s: Market2026(s, costs[s]) for s in sorted({e["sym"] for e in EXAMPLES})}
    os.makedirs(os.path.join(OUT, "charts"), exist_ok=True)
    rows = []
    for ex in EXAMPLES:
        r = run_example(ex, markets, news=set())                      # news filter off: compare the pattern itself
        r["news_day_skipped"] = False
        rows.append(r)
        p = dict(tf="M5", anchor="wat1530", entry="A", target=3 if ex["sym"] == "XAUUSD" else 4, be=0)
        S._CACHE.clear(); S.NEWS = set()
        charts.day_chart(markets[ex["sym"]], dt.date.fromisoformat(ex["date"]), p, S,
                         os.path.join(OUT, "charts", f"replay_{ex['sym']}_{ex['date']}.png"), note=ex["owner"])
    json.dump(rows, open(os.path.join(OUT, "replay.json"), "w"), indent=1, default=str)
    open(os.path.join(OUT, "REPLAY.md"), "w").write(report(rows))
    print(report(rows))

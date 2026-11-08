"""Tables for the v5 report, built only from the saved results (no new runs, no new 2023-25 numbers):
research/results/body4/v5/study_v5.json (2011-19, 2020-22) and LOOK_2023_25.json (the owner's logged 2023-25 look).
    python3 research/body4/tables_v5.py  ->  research/results/body4/v5/TABLES.md
"""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "research", "results", "body4", "v5")
TFS = ("M1", "M5", "M15", "M30", "H1", "H4")
COMBOS = (("body", "none"), ("body", "on"), ("loose", "none"), ("loose", "on"))
NAME = {("body", "none"): "strict engulf, no layering", ("body", "on"): "strict engulf + layering",
        ("loose", "none"): "loose engulf, no layering", ("loose", "on"): "loose engulf + layering"}


def key(tf, e, ly, T, be, buf, lb):
    return f"{tf} | engulf={e}|layer={ly}|target={T}|be={be}|buffer={buf}|lookback={lb}"


def pretty(k):
    return k.replace(" | ", ": ").replace("|", ", ")


def cell(v, digits=3):
    if not v or v.get("n", 0) < 3 or v.get("E") is None:
        return f"{(v or {}).get('n', 0)} trades"
    return f"{v['n']:,}, {v['E']:+.{digits}f}R"


def paired(table, var, a, b, per, min_n=100):
    wins = tot = 0; dE = []
    for k, v in table.items():
        if f"{var}={a}" not in k:
            continue
        o = table.get(k.replace(f"{var}={a}", f"{var}={b}"))
        x = v[per] if per else v
        y = ((o or {}).get(per, {}) if per else (o or {}))
        if x.get("n", 0) < min_n or y.get("n", 0) < min_n:
            continue
        tot += 1; wins += x["E"] > y["E"]; dE.append(x["E"] - y["E"])
    return tot, (wins / tot if tot else None), (float(np.mean(dE)) if dE else None)


def main():
    st = json.load(open(os.path.join(OUT, "study_v5.json")))
    lk = json.load(open(os.path.join(OUT, "LOOK_2023_25.json")))
    dev, look = st["pooled"], lk["all"]
    L = ["# Body-engulf range v5: tables (built by research/body4/tables_v5.py from study_v5.json and LOOK_2023_25.json)", "",
         "R per trade is after spread, commission and slippage (RoboForex Prime published costs). Swaps are zero in every v5",
         "setting: the safe window closes everything at 20:30 UTC, before the 22:00 UTC rollover, so the swap-free result is the",
         "same number. 12 markets pooled. 2023-25 = the owner's logged look (description only, except the 4 primaries).", ""]

    # 1. paired comparisons
    L += ["## 1. Paired comparisons (same timeframe and settings, only one thing changed; both sides >= 100 trades)", "",
          "| Change | Period | Pairs | Share where the change is better | Mean change in R per trade |", "|---|---|---|---|---|"]
    for var, a, b, label in (("engulf", "loose", "body", "loose engulf instead of strict"), ("layer", "on", "none", "layering on instead of off")):
        for per in ("2011-19", "2020-22", None):
            n, sh, d = paired(dev if per else look, var, a, b, per)
            L.append(f"| {label} | {per or '2023-25 (look)'} | {n} | {sh:.0%} | {d:+.3f}R |" if n else f"| {label} | {per or '2023-25'} | 0 | - | - |")
    L.append("")

    # 2. trade counts and R per trade at the main settings
    for T in (2, 10):
        L += [f"## 2{'a' if T == 2 else 'b'}. Main settings at {T}R (entry 50%, stop at the range end, breakeven at 75% on, lookback on): trades, R per trade", "",
              "| Timeframe | " + " | ".join(NAME[c] for c in COMBOS) + " |", "|---|" + "---|" * len(COMBOS)]
        for per in ("2011-19", "2020-22", "2023-25"):
            for tf in TFS:
                row = []
                for e, ly in COMBOS:
                    k = key(tf, e, ly, T, 1, 0.0, 1)
                    row.append(cell(look.get(k) if per == "2023-25" else dev.get(k, {}).get(per)))
                L.append(f"| {tf} {per} | " + " | ".join(row) + " |")
        L.append("")

    # 3. before costs (2011-22 only; the look was after costs)
    L += ["## 3. Before costs (spread, commission and slippage set to 0), main settings, 2011-19 / 2020-22 (2023-25 was not run before costs)", "",
          "| Timeframe | Target | " + " | ".join(NAME[c] for c in COMBOS) + " |", "|---|---|" + "---|" * len(COMBOS)]
    for tf in TFS:
        for T in (2, 3, 5, 10):
            row = []
            for e, ly in COMBOS:
                v = st["before_costs"].get(f"{tf} | engulf={e}|layer={ly}|target={T}", {})
                a, b = v.get("2011-19", {}), v.get("2020-22", {})
                row.append(f"{cell(a)} / {cell(b)}")
            L.append(f"| {tf} | {T}R | " + " | ".join(row) + " |")
    L.append("")

    # 4. the 4 primaries
    L += ["## 4. The 4 PRIMARY settings (chosen on 2011-22 before the look) in each period", "",
          "| Combination | Setting | Period | Trades | R per trade | t | Profit factor | Target hit | Markets positive |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, v in lk["primary"].items():
        e, ly = name.replace("engulf=", "").replace("layer=", "").split()
        for per, s in (("2011-19", v["before_2023"]["2011-19"]), ("2020-22", v["before_2023"]["2020-22"]), ("2023-25", v["look_2023_25"])):
            L.append(f"| {NAME[(e, ly)]} | {pretty(v['config'])} | {per} | {s['n']:,} | {s['E']:+.3f}R | {s['t']} | {s['pf']} | "
                     f"{s['hit']:.1%} | {s.get('markets_positive', '-')} of 12 |")
    L.append("")
    L += ["### Per market, 2023-25", "", "| Market | " + " | ".join(NAME[tuple(n.replace('engulf=', '').replace('layer=', '').split())] for n in lk["primary"]) + " |",
          "|---|" + "---|" * len(lk["primary"])]
    mk = list(next(iter(lk["primary"].values()))["per_market"])
    for m in mk:
        L.append(f"| {m} | " + " | ".join(cell(v["per_market"].get(m)) for v in lk["primary"].values()) + " |")
    L.append("")

    # 5. all 768 in the look, by combination
    L += ["## 5. All 768 settings in 2023-25 (description only: picking one from here would be hindsight)", "",
          "| Combination | Settings with >= 100 trades | Positive | Median R per trade | Best (its 2011-22 result) |", "|---|---|---|---|---|"]
    for e, ly in COMBOS + (("all", "all"),):
        items = [(k, v) for k, v in look.items() if v.get("n", 0) >= 100 and (e == "all" or f"engulf={e}|layer={ly}|" in k)]
        if not items:
            L.append(f"| {NAME.get((e, ly), 'all'):s} | 0 | - | - | - |"); continue
        Es = np.array([v["E"] for _, v in items])
        bk, bv = max(items, key=lambda z: z[1]["E"])
        d = dev.get(bk, {}).get("2011-22", {})
        L.append(f"| {NAME.get((e, ly), 'all four')} | {len(items)} | {int((Es > 0).sum())} ({(Es > 0).mean():.0%}) | {np.median(Es):+.3f}R | "
                 f"{pretty(bk)}: {bv['n']} trades, {bv['E']:+.3f}R, t {bv['t']} ({d.get('n', 0):,} trades, {d.get('E', 0):+.3f}R in 2011-22) |")
    L.append("")
    # 6. by timeframe in the look
    L += ["## 6. 2023-25 by timeframe (all settings with >= 100 trades)", "", "| Timeframe | Settings | Positive | Median R per trade |", "|---|---|---|---|"]
    for tf in TFS:
        Es = np.array([v["E"] for k, v in look.items() if k.startswith(tf + " |") and v.get("n", 0) >= 100])
        L.append(f"| {tf} | {len(Es)} | {int((Es > 0).sum())} | {np.median(Es):+.3f}R |" if len(Es) else f"| {tf} | 0 | - | - |")
    L.append("")
    open(os.path.join(OUT, "TABLES.md"), "w").write("\n".join(L) + "\n")
    return "\n".join(L)


if __name__ == "__main__":
    print(main())

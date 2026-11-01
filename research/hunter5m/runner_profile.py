"""5-minute hunter, step 2: trade only setups that look like the top-1% runners (declared 2026-11-01, after reading the
anatomy of step 1 on gold 2011-19 and BEFORE computing anything outside it).

From research/results/hunter5m/winner_anatomy.json, top 1% by MFE (>= 23R, 106 gold trades 2011-19), the numeric features
whose low or high third holds at least 1.25x its share of runners, excluding the ones that are mechanical or period
artifacts (cost_R and stop_atr only change the size of R; side reflects gold's 2011-15 bear market; Sunday reflects
weekend gaps):
  vol_regime low third (1.36x), day_used low third (1.27x), mom_4h high third (1.27x), struct_atr low third (1.30x),
  leg2_retrace high third (1.56x)   -> the "runner profile": a quiet market and a quiet day, a strong 4-hour push, a
  small structure with a deep Leg 2 pullback.
Rule: runner score = how many of the 5 hold (cut points from gold 2011-19); trade setups with score >= 3. Score >= 4 is
  reported for information. Exits: ladder (primary, as step 1), t10 and t3 for information; after costs and swaps.
Reported without change on gold 2011-19 (in-sample), gold 2020-22 and 2023-25, each of the other 10 markets 2011-25,
  January-September 2026 (gold, EUR, GBP, JPY) and October 2026 separately. Uses the setups saved by step 1.
Output: research/results/hunter5m/runner_profile.json
"""
import os, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
RES = os.path.join(R, "results", "hunter5m")
PROFILE = [("vol_regime", "low"), ("day_used", "low"), ("mom_4h", "high"), ("struct_atr", "low"), ("leg2_retrace", "high")]
EXITS = ["ladder", "t10", "t3"]
OCT26 = 1790812800


def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 2:
        return dict(n=int(len(r)))
    return dict(n=int(len(r)), E=round(float(r.mean()), 3), t=round(float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))), 2),
                win=round(float((r > 0).mean()), 3))


def main():
    D = pd.read_csv(os.path.join(RES, "setups_m5.csv.gz")); D26 = pd.read_csv(os.path.join(RES, "setups_m5_2026.csv.gz"))
    D["year"] = pd.to_datetime(D.dec_t, unit="s").dt.year
    L = D[(D.sym == "XAUUSD") & (D.year <= 2019)]
    cuts = {f: L[f].quantile([1 / 3, 2 / 3]).values for f, _ in PROFILE}

    def score(Df):
        s = pd.Series(0, index=Df.index)
        for f, side in PROFILE:
            s += (Df[f] <= cuts[f][0]).astype(int) if side == "low" else (Df[f] > cuts[f][1]).astype(int)
        return s

    D["score"] = score(D); D26["score"] = score(D26)
    groups = {"gold 2011-19 (in-sample)": D[(D.sym == "XAUUSD") & (D.year <= 2019)],
              "gold 2020-22": D[(D.sym == "XAUUSD") & D.year.between(2020, 2022)],
              "gold 2023-25": D[(D.sym == "XAUUSD") & (D.year >= 2023)],
              "other 10 markets 2011-25 (pooled)": D[D.sym != "XAUUSD"]}
    for sym in sorted(D.sym.unique()):
        if sym != "XAUUSD":
            groups[f"{sym} 2011-25"] = D[D.sym == sym]
    groups["4 markets Jan-Sep 2026 (untouched)"] = D26[D26.dec_t < OCT26]
    groups["gold Jan-Sep 2026 (untouched)"] = D26[(D26.sym == "XAUUSD") & (D26.dec_t < OCT26)]
    groups["4 markets Oct 2026"] = D26[D26.dec_t >= OCT26]
    out = {"profile": PROFILE, "cut_points": {f: [round(float(x), 3) for x in v] for f, v in cuts.items()}, "results": {}}
    for name, G in groups.items():
        row = {"all setups": {ex: stats(G[ex]) for ex in EXITS}}
        for th in (3, 4):
            S = G[G.score >= th]
            row[f"score>={th}"] = {ex: stats(S[ex]) for ex in EXITS} | {"ladder_gross": stats(S["ladder_gross"]) if "ladder_gross" in S else {}}
        out["results"][name] = row
        print(f"{name:36s} all {row['all setups']['ladder'].get('n'):>6} {row['all setups']['ladder'].get('E')}  "
              f"score>=3 {row['score>=3']['ladder'].get('n'):>5} ladder {row['score>=3']['ladder'].get('E')} t10 {row['score>=3']['t10'].get('E')} "
              f"t3 {row['score>=3']['t3'].get('E')}  | score>=4 {row['score>=4']['ladder'].get('n')} {row['score>=4']['ladder'].get('E')}", flush=True)
    json.dump(out, open(os.path.join(RES, "runner_profile.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()

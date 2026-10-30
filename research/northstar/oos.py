"""Final out-of-sample (2023-2025): ONE logged look per module candidate (PREREGISTRATION.md §5), then
tier classification by the fixed criteria. A look that is already in the log is not repeated: the
logged numbers are reused, so the look count stays at one per configuration.

    python3 oos.py -> results/northstar/oos_log.json, tiers.json
"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core
from grid import year_index, SYMS
from confirm import run, stats
RES = os.path.join(HERE, "..", "results", "northstar")
LOG = os.path.join(RES, "oos_log.json")


def look(mod, cfg, markets):
    key = mod + " " + json.dumps(cfg, sort_keys=True)
    log = json.load(open(LOG)) if os.path.exists(LOG) else []
    for e in log:
        if e["key"] == key:
            print(f"{mod}: already looked at {e['time']}; reusing the logged result")
            return e
    parts = []
    for i, s in enumerate(SYMS):
        tr = run(markets[s], mod, cfg, cut=0)
        tr = tr[year_index(tr[:, 0]) >= 2023]
        parts.append(np.c_[tr, np.full(len(tr), i)])
    T = np.vstack(parts)
    e = dict(key=key, module=mod, config=cfg, time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
             oos=stats(T[:, 3]), oos_before_financing=stats(T[:, 3] + T[:, 7]),
             per_market={s: stats(T[T[:, 8] == i, 3]) for i, s in enumerate(SYMS)},
             per_year={int(y): stats(T[year_index(T[:, 0]) == y, 3]) for y in (2023, 2024, 2025)})
    log.append(e)
    json.dump(log, open(LOG, "w"), indent=1)
    np.save(os.path.join(RES, f"oos_trades_{mod.replace('+', '_')}.npy"), T)
    return e


def tier(sel, conf, e):
    o = e["oos"]
    c = {
        "1_E_pos_dev_val_oos": conf["dev"]["E"] > 0 and conf["val"]["E"] > 0 and o["E"] > 0,
        "2_oos_PF110_t2_n100": (o.get("PF") or 0) >= 1.10 and (o.get("t") or 0) >= 2.0 and o["n"] >= 100,
        "3_walk_forward_E_pos": (sel["walk_forward"]["E"] or -1) > 0,
        "4_neighbours_stable": bool(sel["neighbours_all_pos"]) and (sel["neighbours_median_t"] or 0) >= 1.0,
        "5_stress_dev_val_pos": conf["stress_dev_val"]["E"] > 0,
        "6_oos_pos_2_markets": sum(1 for v in e["per_market"].values() if (v.get("E") or -1) > 0) >= 2,
    }
    if all(c.values()):
        t = "A"
    elif c["1_E_pos_dev_val_oos"] and c["4_neighbours_stable"] and c["5_stress_dev_val_pos"] and (o.get("PF") or 0) >= 1.05:
        t = "B"
    else:
        t = "Rejected"
    return t, c


def main():
    sel = json.load(open(os.path.join(RES, "selection.json")))
    conf = json.load(open(os.path.join(RES, "confirm.json")))
    markets = {s: core.Mkt(s) for s in SYMS}
    out = {}
    for mod, r in sel.items():
        if not r.get("candidate"):
            out[mod] = dict(tier="Rejected", reason="no configuration passed the development gate", configs=r["configs"])
            continue
        e = look(mod, r["candidate"], markets)
        t, c = tier(r, conf[mod], e)
        out[mod] = dict(tier=t, criteria=c, config=r["candidate"], oos=e["oos"], per_market=e["per_market"], per_year=e["per_year"],
                        dsr=conf[mod]["dsr"]["dsr"], configs=r["configs"])
        print(f"{mod:8s} OOS n={e['oos']['n']} E={e['oos']['E']:+.3f} t={e['oos'].get('t', 0):+.2f} PF={e['oos'].get('PF')} -> {t}")
        print("         ", {k: v for k, v in c.items()})
        print("          per market:", {s: (v["n"], round(v.get("E") or 0, 3)) for s, v in e["per_market"].items()})
    json.dump(out, open(os.path.join(RES, "tiers.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

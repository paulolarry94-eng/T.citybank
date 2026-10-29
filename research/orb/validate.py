"""ORB 50 — robustness tests (Part 6): market regimes, Monte Carlo trade resampling, execution
cost and latency perturbation, multiple-testing adjustment (deflated Sharpe ratio), and the
guarded final out-of-sample evaluation.

The final out-of-sample years (2023-2025) are only reachable through final_run(), which
appends every call to results/orb_oos_log.json so the number of looks is on record.
"""
import os, json, math, datetime as dt
import numpy as np
from statistics import NormalDist
import core, strategy as S, experiments as X

_N = NormalDist()


class norm:
    ppf = staticmethod(_N.inv_cdf)
    cdf = staticmethod(_N.cdf)

LOG_OOS = os.path.join(core.HERE, "..", "results", "orb_oos_log.json")

DISRUPTIONS = [("2011-08-01", "2011-09-30", "US downgrade / euro crisis"), ("2013-04-10", "2013-04-30", "gold crash"),
               ("2015-01-15", "2015-01-31", "SNB unpeg"), ("2015-08-20", "2015-09-05", "China devaluation"),
               ("2016-06-23", "2016-07-08", "Brexit vote"), ("2016-11-08", "2016-11-18", "US election"),
               ("2020-02-24", "2020-04-30", "COVID crash"), ("2022-09-22", "2022-10-31", "gilt crisis / BoJ intervention"),
               ("2024-08-01", "2024-08-09", "yen carry unwind"), ("2025-04-02", "2025-04-15", "tariff shock")]


def _ts(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())


def regimes(M, tr):
    """Label each trade by the instrument's state at the last closed UTC day before entry:
    trend  bull (close > SMA200 and SMA200 up over 20 days) / bear (mirror) / sideways
    vol    high (ATR14 > 1.25 x its 250-day median) / low (< 0.8 x) / normal
    shock  inside one of the listed disruption windows."""
    D = M.D
    c = D["c"]; cs = np.r_[0, np.cumsum(c)]
    sma = np.full(len(c), np.nan); sma[199:] = (cs[200:] - cs[:-200]) / 200
    up = sma > np.r_[np.full(20, np.nan), sma[:-20]]
    atr = D["atr"]
    med = np.array([np.nanmedian(atr[max(0, i - 250):i]) if i >= 60 else np.nan for i in range(len(atr))])
    k = np.searchsorted(D["t"] + 86400, tr["t_in"], side="right") - 1
    k = np.clip(k, 0, len(c) - 1)
    trend = np.where((c[k] > sma[k]) & up[k], "bull", np.where((c[k] < sma[k]) & ~up[k], "bear", "sideways"))
    ratio = atr[k] / med[k]
    vol = np.where(ratio > 1.25, "high", np.where(ratio < 0.8, "low", "normal"))
    shock = np.zeros(len(tr), bool)
    for a, b, _ in DISRUPTIONS:
        shock |= (tr["t_in"] >= _ts(a)) & (tr["t_in"] < _ts(b) + 86400)
    return trend, vol, shock


def regime_table(M, tr):
    trend, vol, shock = regimes(M, tr)
    r = tr["r"]; out = {}
    for name, lab in (("trend", trend), ("vol", vol)):
        for v in np.unique(lab):
            k = lab == v
            out[f"{name}:{v}"] = dict(n=int(k.sum()), E=float(r[k].mean()) if k.any() else np.nan)
    out["shock"] = dict(n=int(shock.sum()), E=float(r[shock].mean()) if shock.any() else np.nan)
    out["no_shock"] = dict(n=int((~shock).sum()), E=float(r[~shock].mean()))
    return out


def monte_carlo(tr, risk=0.005, paths=10000, years=3.0, block="month", seed=7):
    """Resample the trade sequence (whole calendar months kept together) to build `paths`
    alternative histories of `years` years; report max drawdown and return quantiles at a
    fixed fractional risk."""
    rng = np.random.default_rng(seed)
    r = tr["r"]
    if block == "month":
        m = (tr["t_in"] // (86400 * 30.4375)).astype(np.int64)
        groups = [r[m == u] for u in np.unique(m)]
        n_blocks = int(round(years * 12))
    else:
        groups = [np.array([x]) for x in r]
        n_blocks = int(round(len(r) / ((tr["t_out"].max() - tr["t_in"].min()) / (365.25 * 86400)) * years))
    dd = np.empty(paths); ret = np.empty(paths)
    for p in range(paths):
        seq = np.concatenate([groups[i] for i in rng.integers(0, len(groups), n_blocks)])
        eq = np.cumprod(1 + risk * seq) if len(seq) else np.ones(1)
        peak = np.maximum.accumulate(np.r_[1.0, eq])[1:]
        dd[p] = (1 - eq / peak).max() if len(eq) else 0.0
        ret[p] = eq[-1] - 1 if len(eq) else 0.0
    q = lambda x: {f"p{int(k)}": float(np.percentile(x, k)) for k in (5, 25, 50, 75, 95)}
    return dict(max_dd=q(dd), total_return=q(ret), p_loss=float((ret < 0).mean()), years=years, risk=risk)


def deflated_sharpe(r, sr_trials, n_trials):
    """Bailey & Lopez de Prado (2014). r: trade returns of the selected config; sr_trials:
    per-trade Sharpe ratios of all configurations tried; n_trials: number tried."""
    r = np.asarray(r, float); T = len(r)
    sr = r.mean() / r.std(ddof=1)
    sk = ((r - r.mean()) ** 3).mean() / r.std() ** 3
    ku = ((r - r.mean()) ** 4).mean() / r.std() ** 4
    v = np.nanvar(sr_trials)
    g = 0.5772156649
    sr0 = math.sqrt(v) * ((1 - g) * norm.ppf(1 - 1 / n_trials) + g * norm.ppf(1 - 1 / (n_trials * math.e)))
    z = (sr - sr0) * math.sqrt(T - 1) / math.sqrt(1 - sk * sr + (ku - 1) / 4 * sr ** 2)
    return dict(sr_trade=float(sr), sr0=float(sr0), dsr=float(norm.cdf(z)), n_trials=int(n_trials), T=T)


def bonferroni_t(n_tests, alpha=0.05):
    return float(norm.ppf(1 - alpha / (2 * n_tests)))


def perturb(M, sess, orb, cfg, bias_cfg, filt, years=(2011, 2022)):
    """Same configuration with costs x1.5 / x2 and with 1 and 2 extra minutes of latency."""
    D = M.days(sess, orb)
    allow = (D["year"] >= years[0]) & (D["year"] <= years[1]) & X.filter_mask(M, sess, orb, filt)
    out = {}
    for label, kw in (("base", {}), ("cost x1.5", dict(cost=M.cost * 1.5)), ("cost x2", dict(cost=M.cost * 2)),
                      ("delay +1m", dict(delay=1)), ("delay +2m", dict(delay=2))):
        c = dict(cfg); cost = kw.pop("cost", None); c.update(kw)
        tr = S.run(M, sess, orb, allow=allow, bias_cfg=bias_cfg, cost=cost, **c)
        r = tr["r"]
        out[label] = dict(n=len(r), E=float(r.mean()) if len(r) else np.nan,
                          t=float(r.mean() / r.std(ddof=1) * math.sqrt(len(r))) if len(r) > 2 else np.nan)
    return out


def final_run(M, sess, orb, cfg, bias_cfg=None, filt="", label="", years=(2011, 2025)):
    """Runs a configuration over the full record INCLUDING the final out-of-sample years.
    Every call is appended to the OOS log."""
    D = M.days(sess, orb)
    allow = (D["year"] >= years[0]) & (D["year"] <= years[1]) & X.filter_mask(M, sess, orb, filt)
    tr = S.run(M, sess, orb, allow=allow, bias_cfg=bias_cfg, **cfg)
    log = json.load(open(LOG_OOS)) if os.path.exists(LOG_OOS) else []
    log.append(dict(when=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), label=label, sym=M.sym,
                    session=sess, orb=orb, cfg=cfg, bias=bias_cfg, filt=filt))
    json.dump(log, open(LOG_OOS, "w"), indent=1, default=str)
    return tr, D["year"][tr["d"]]

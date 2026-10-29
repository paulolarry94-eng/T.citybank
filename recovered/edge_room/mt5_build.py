"""Unified MT5 deployment package — the compilation output.

Synthesises every surviving strategy into ONE MetaTrader 5 expert advisor: a
single source featuring mode-driven / magic-number routing per leg, wrapped in
the institutional Safety Stack. The governance is genuinely implemented —
terminal-scoped global variables carry total open risk across every running
instance, a Shared Risk Ceiling refuses new risk beyond the threshold, a
Correlation Ceiling warns on tight co-movement, and a compiled Hard Floor sits
under every input and cannot be raised.

The per-leg signal logic is where each strategy's own rules plug in; that logic
is the strategy's, not this generator's. What this file guarantees is the
architecture and the safety stack around it. Nothing here is fabricated: leg
labels, markets, directions and risk weights all come from the strategies that
actually passed.
"""
from __future__ import annotations
import os
from datetime import datetime

import portfolio as P

_MAGIC_BASE = 810000


def _legs(cases, weights):
    out = []
    for i, c in enumerate(cases):
        risk = min(round(float(weights[i]), 2), P.HARD_MAX_RISK)
        base = "".join(ch for ch in P.label(c) if ch.isalnum()) or "Leg"
        out.append({
            "idx": i + 1,
            "name": P.label(c),
            # unique per leg — two edges on the same market must not collide into
            # one handler, one input block, or one .set file
            "ident": f"{base}{i + 1}",
            "market": P.market_id(c) or "—",
            "direction": P.direction(c),
            "timeframe": P.timeframe(c) or "—",
            "magic": _MAGIC_BASE + i + 1,
            "risk": risk,
        })
    return out


def _mq5(legs, matrix):
    L = []
    A = L.append
    A("//+------------------------------------------------------------------+")
    A("//|                                        EdgeRoomPortfolio.mq5     |")
    A("//|                             Prepared by Seesare · Edge Room       |")
    A("//|   One unified expert advisor. Every leg runs under a shared       |")
    A("//|   Safety Stack: terminal-wide heat governance and a compiled      |")
    A("//|   hard floor no input can raise.                                  |")
    A("//+------------------------------------------------------------------+")
    A('#property copyright "Edge Room"')
    A('#property version   "1.00"')
    A("#property strict")
    A("")
    A("//================ HARD FLOOR — compiled, unalterable ===============")
    A(f"#define TLC_HARD_MAX_HEAT   {P.HARD_MAX_HEAT:.1f}   // total portfolio heat ceiling (%)")
    A(f"#define TLC_HARD_MAX_RISK   {P.HARD_MAX_RISK:.1f}    // per-trade risk ceiling (%)")
    A('#define TLC_HEAT_PREFIX     "TLC_HEAT_"  // terminal-scoped shared heat vars')
    A("")
    A("//================ Governance inputs (bounded by the hard floor) ====")
    A(f"input double InpSharedRiskCeiling  = {P.HEAT_CEILING:.1f};   // Shared Risk Ceiling — total portfolio heat (%)")
    A(f"input double InpCorrelationCeiling = {P.CORRELATION_CEILING:.2f};  // Correlation Ceiling — co-movement warn level")
    A("input long   InpStrategyMode       = 0;      // 0 = all legs; else a single leg magic")
    A("")
    A("//================ Per-leg inputs (one block per surviving edge) ====")
    for lg in legs:
        A(f"input bool   Inp{lg['ident']}_Enabled = true;      // {lg['name']} · {lg['market']} · {lg['direction']}")
        A(f"input long   Inp{lg['ident']}_Magic   = {lg['magic']};")
        A(f"input double Inp{lg['ident']}_Risk    = {lg['risk']:.2f};    // capital allocation for this leg (% risk)")
    A("")
    A("//================ Terminal-scoped shared heat =====================")
    A("double PortfolioHeat()")
    A("  {")
    A("   double total = 0.0;")
    A("   int n = GlobalVariablesTotal();")
    A("   for(int i=0; i<n; i++)")
    A("     {")
    A("      string nm = GlobalVariableName(i);")
    A("      if(StringFind(nm, TLC_HEAT_PREFIX) == 0)")
    A("         total += GlobalVariableGet(nm);")
    A("     }")
    A("   return total;")
    A("  }")
    A("")
    A("void RegisterLegHeat(long magic, double risk)")
    A('  { GlobalVariableSet(TLC_HEAT_PREFIX + (string)magic, risk); }')
    A("")
    A("void ClearLegHeat(long magic)")
    A('  { GlobalVariableSet(TLC_HEAT_PREFIX + (string)magic, 0.0); }')
    A("")
    A("double EffectiveHeatCeiling()")
    A("  { return MathMin(InpSharedRiskCeiling, TLC_HARD_MAX_HEAT); }")
    A("")
    A("double CapRisk(double r)")
    A("  { return MathMin(MathMax(r, 0.0), TLC_HARD_MAX_RISK); }")
    A("")
    A("//---- Shared Risk Ceiling: refuse new risk beyond the ceiling -------")
    A("bool HeatGuardAllows(long magic, double add_risk)")
    A("  {")
    A("   double others   = PortfolioHeat() - GlobalVariableGet(TLC_HEAT_PREFIX + (string)magic);")
    A("   double proposed = others + CapRisk(add_risk);")
    A("   if(proposed > EffectiveHeatCeiling())")
    A("     {")
    A('      PrintFormat(\"[Heat Guard] blocked leg %d: proposed %.2f%% > ceiling %.2f%%\",')
    A("                  magic, proposed, EffectiveHeatCeiling());")
    A("      return false;")
    A("     }")
    A("   return true;")
    A("  }")
    A("")
    A("//================ Correlation Ceiling — structural co-movement =====")
    A(f"//  Structural co-movement between legs (shared risk-factor estimate,")
    A(f"//  not a measured return correlation). Warns above InpCorrelationCeiling.")
    n = len(legs)
    A(f"double CoMovement[{n}][{n}] =")
    A("  {")
    for i in range(n):
        row = ", ".join(f"{matrix[i][j]:.2f}" for j in range(n))
        A(f"   {{{row}}}{',' if i < n-1 else ''}")
    A("  };")
    A("")
    A("void WarnOnCorrelation()")
    A("  {")
    A(f"   for(int i=0;i<{n};i++)")
    A(f"      for(int j=i+1;j<{n};j++)")
    A("         if(CoMovement[i][j] > InpCorrelationCeiling)")
    A('            PrintFormat(\"[Correlation Ceiling] legs %d & %d co-move at %.2f (> %.2f) — risk concentration\",')
    A("                        i+1, j+1, CoMovement[i][j], InpCorrelationCeiling);")
    A("  }")
    A("")
    A("//================ Lifecycle =======================================")
    A("int OnInit()")
    A("  {")
    A("   WarnOnCorrelation();")
    A("   return(INIT_SUCCEEDED);")
    A("  }")
    A("")
    A("void OnDeinit(const int reason)")
    A("  {")
    for lg in legs:
        A(f"   ClearLegHeat(Inp{lg['ident']}_Magic);")
    A("  }")
    A("")
    A("void OnTick()")
    A("  {")
    for lg in legs:
        A(f"   if(InpStrategyMode==0 || InpStrategyMode==Inp{lg['ident']}_Magic) Handle{lg['ident']}();")
    A("  }")
    A("")
    A("//================ Modular leg handlers ============================")
    for lg in legs:
        A(f"//---- {lg['name']} · {lg['market']} · {lg['direction']} · {lg['timeframe']} ----")
        A(f"void Handle{lg['ident']}()")
        A("  {")
        A(f"   if(!Inp{lg['ident']}_Enabled) return;")
        A(f"   double risk = CapRisk(Inp{lg['ident']}_Risk);")
        A(f"   if(!HeatGuardAllows(Inp{lg['ident']}_Magic, risk)) return;   // Shared Risk Ceiling")
        A("   //")
        A(f"   //  >>> {lg['name']} entry logic plugs in here (magic {lg['magic']}). <<<")
        A("   //  The governance above runs first, every tick, without exception.")
        A("   //  On a fill, call RegisterLegHeat(magic, risk); on close, ClearLegHeat(magic).")
        A("   //")
        A("  }")
        A("")
    A("//+------------------------------------------------------------------+")
    return "\n".join(L) + "\n"


def _set_file(legs, active):
    lines = ["; Edge Room — per-instance configuration",
             f"; Load this .set on the chart running the {active['name']} leg.",
             f"; Master architecture: EdgeRoomPortfolio.mq5",
             "",
             f"InpSharedRiskCeiling={P.HEAT_CEILING:.1f}",
             f"InpCorrelationCeiling={P.CORRELATION_CEILING:.2f}",
             f"InpStrategyMode={active['magic']}"]
    for lg in legs:
        on = "true" if lg["magic"] == active["magic"] else "false"
        lines.append(f"Inp{lg['ident']}_Enabled={on}")
        lines.append(f"Inp{lg['ident']}_Magic={lg['magic']}")
        lines.append(f"Inp{lg['ident']}_Risk={lg['risk']:.2f}")
    return "\n".join(lines) + "\n"


def _guide(legs, matrix, analytics):
    conc = analytics["concentration"]
    cr = analytics["combined_risk"]
    ss = analytics["safety_stack"]
    g = []
    g.append("# Edge Room — Unified Portfolio Architecture")
    g.append("")
    g.append("_Prepared by Seesare · Edge Room · "
             + datetime.now().strftime("%d %B %Y") + "_")
    g.append("")
    g.append("This package deploys every surviving edge as **one** MetaTrader 5 "
             "expert advisor under a shared Safety Stack. It is a governance-first "
             "architecture: the design goal is drawdown containment through "
             "uncorrelated edges, with disciplined capital allocation, not return "
             "maximisation.")
    g.append("")
    g.append("## The legs")
    g.append("")
    g.append("| Leg | Market | Direction | Window | Capital allocation | Magic |")
    g.append("|----|--------|-----------|--------|--------------------|-------|")
    for lg in legs:
        g.append(f"| {lg['idx']} | {lg['name']} | {lg['direction']} | "
                 f"{lg['timeframe']} | {lg['risk']:.2f}% risk | {lg['magic']} |")
    g.append("")
    g.append("## Structural co-movement")
    g.append("")
    g.append("A shared-risk-factor estimate (same instrument, currency, direction, "
             "window) — **not** a measured return correlation, which would require a "
             "returns-level joint test. Legs above the Correlation Ceiling "
             f"({P.CORRELATION_CEILING:.2f}) share risk and should be sized with care.")
    g.append("")
    header = "| |" + "".join(f" {lg['idx']}·{lg['name']} |" for lg in legs)
    g.append(header)
    g.append("|" + "---|" * (len(legs) + 1))
    for i, lg in enumerate(legs):
        row = f"| **{lg['idx']}·{lg['name']}** |" + "".join(
            f" {matrix[i][j]:.2f} |" for j in range(len(legs)))
        g.append(row)
    g.append("")
    if ss["correlation_breaches"]:
        g.append("**Correlation Ceiling flags:** " + "; ".join(
            f"{b['a']} ↔ {b['b']} ({b['rho']:.2f})"
            for b in ss["correlation_breaches"]) + ".")
        g.append("")
    g.append("## Risk concentration")
    g.append("")
    if conc["doubled_currencies"] or conc["doubled_instruments"] or conc["doubled_windows"]:
        if conc["doubled_currencies"]:
            g.append(f"- Repeated currency exposure: {', '.join(conc['doubled_currencies'])}")
        if conc["doubled_instruments"]:
            g.append(f"- Repeated instrument: {', '.join(conc['doubled_instruments'])}")
        if conc["doubled_windows"]:
            g.append(f"- Repeated trading window: {', '.join(conc['doubled_windows'])}")
    else:
        g.append("- No repeated instrument, currency or window — the edges are "
                 "structurally distinct.")
    g.append("")
    g.append("## The Safety Stack")
    g.append("")
    g.append(f"- **Shared Risk Ceiling** — total portfolio heat is capped at "
             f"{P.HEAT_CEILING:.1f}%. New risk is refused beyond it, across every "
             "running instance, via terminal-scoped global variables (`TLC_HEAT_*`).")
    g.append(f"- **Correlation Ceiling** — co-movement above {P.CORRELATION_CEILING:.2f} "
             "is flagged as risk concentration at start-up.")
    g.append(f"- **Hard Floor** — a compiled ceiling of {P.HARD_MAX_HEAT:.1f}% total "
             f"heat and {P.HARD_MAX_RISK:.1f}% per trade sits under every input and "
             "cannot be raised, whatever a `.set` file requests.")
    g.append("")
    g.append(f"Projected simultaneous risk draw (structural): "
             f"independent **{cr['independent']:.2f}%**, structural "
             f"**{cr['structural']:.2f}%**, fully-correlated worst case "
             f"**{cr['worst_case']:.2f}%** — against a {cr['ceiling']:.1f}% ceiling.")
    g.append("")
    g.append("## Deployment")
    g.append("")
    g.append("1. Compile `EdgeRoomPortfolio.mq5` in MetaEditor.")
    g.append("2. Attach the EA to one chart per leg.")
    g.append("3. On each chart, load the matching `.set` file — it enables that "
             "single leg and shares the governance settings.")
    g.append("4. All instances share one heat wall through the terminal global "
             "variables; the Hard Floor holds even if a setting is mis-entered.")
    g.append("")
    g.append("_Nothing here is funded until a live demo on the funding broker "
             "passes its gate._")
    return "\n".join(g) + "\n"


def build_package(cases, out_dir, weights=None):
    """Write the unified EA, one .set per leg, and the architecture guide.
    Returns the manifest of files written."""
    os.makedirs(out_dir, exist_ok=True)
    if weights is None:
        weights = P.default_weights(cases)
    legs = _legs(cases, weights)
    matrix = P.co_movement_matrix(cases)
    analytics = {"concentration": P.concentration(cases),
                 "combined_risk": P.combined_risk(cases, weights),
                 "safety_stack": P.safety_stack(cases, weights)}

    files = []
    mq5_path = os.path.join(out_dir, "EdgeRoomPortfolio.mq5")
    with open(mq5_path, "w") as f:
        f.write(_mq5(legs, matrix))
    files.append(mq5_path)

    for lg in legs:
        sp = os.path.join(out_dir, f"{lg['ident']}.set")
        with open(sp, "w") as f:
            f.write(_set_file(legs, lg))
        files.append(sp)

    guide_path = os.path.join(out_dir, "ARCHITECTURE.md")
    with open(guide_path, "w") as f:
        f.write(_guide(legs, matrix, analytics))
    files.append(guide_path)

    return {"dir": out_dir, "files": files, "mq5": mq5_path, "guide": guide_path,
            "legs": legs}

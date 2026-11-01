"""SEESARE router, Phase 3: Python twin of the Telegram outbox formatter (Ledger/Telegram.mqh), of the cent-account sizing
table (Risk/Exposure.mqh) and of the deal-reason mapping (Exec/DealReader.mqh); generator of the Phase 3 self-test vectors.

    python3 tools/seesare_outbox.py --vectors     print the reference texts and tables
    python3 tools/seesare_outbox.py --mql         print the generated block of SeesarePhase3SelfTest.mq5

The formatter only rearranges the fields of a ledger or anchor line (no number is re-printed), so MQL5 and Python produce the
same bytes, and every message ends with the full record so anyone can recompute its hash with tools/seesare_verify.py.
"""
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seesare_verify as S  # noqa: E402

MAX_TELEGRAM = 4096
HEAD = "SEESARE P26"


# ------------------------------------------------------------------------------------------------ formatter (Telegram.mqh)
def signed(v):
    """'+' in front of a positive decimal string; zero and negatives unchanged (pure text, no re-formatting)."""
    if v.startswith("-") or not any(c in "123456789" for c in v):
        return v
    return "+" + v


def _kv(line):
    c, _ = S.split_line(line)
    if c is None:
        c = line                                    # the lifecycle summary carries no hash
    p = S.parse(c)
    if p is None:
        raise ValueError("malformed record")       # Telegram.mqh returns "" and the outbox refuses it
    return p[1]


def _hash(line):
    h = S.split_line(line)[1]
    if h is None:
        raise ValueError("record without a hash")
    return h


def fmt_event(line):
    kv = _kv(line)
    h = _hash(line)
    real = kv["mode"] == "REAL"
    where = f"Cycle {kv['cycle']}/36 | Step {kv['step']}/10 | REAL" if real else f"Cycle {kv['cycle']}/36 | SHADOW (paper, not counted)"
    deals = kv["deals"].replace(";", ", ") if real else "none (paper)"
    return "\n".join([
        f"{HEAD} | {kv['life']} | {where}",
        f"{kv['module']} {kv['symbol']} {kv['side']}",
        f"Open {kv['open']} | Close {kv['close']} | by {kv['by']}",
        f"Result {kv['res']} | {signed(kv['delta'])} USD | level L{kv['lvl_before']} -> L{kv['lvl_after']} | drawdown before {kv['dd']} USD",
        f"Entry {kv['entry']} | Lower {kv['lower']} | Upper {kv['upper']} | Exit {kv['exit']}",
        f"Weight {kv['weight']} | planned {kv['plan']} USD | risk {kv['risk']} USD | volume {kv['vol']}",
        f"Deals {deals}",
        f"Chain k={kv['k']} | hash {h}",
        f"Prev {kv['prev']}"])


def fmt_genesis(line):
    kv = _kv(line)
    return "\n".join([
        f"{HEAD} | {kv['life']} | lifecycle opened {kv['created']}",
        f"Baseline {kv['baseline']} USD | {kv['events']} events in cycles of {kv['cycle_size']} | envelope {kv['envelope_pct']}%",
        f"Sizing {kv['sizing']}: {kv['levels']} levels of {kv['band']} USD drawdown | risk = {kv['room_mult']} x weight x room left | weight <= {kv['max_weight']}",
        f"Time exits {kv['time_policy']}",
        f"Genesis hash {_hash(line)}"])


def fmt_audit(line):
    kv = _kv(line)
    return "\n".join([
        f"{HEAD} | {kv['life']} | Cycle {kv['cycle']}/36 closed | events {kv['events']}",
        f"Positive {kv['pos']} | negative {kv['neg']} | manual {kv['man']} | shadow {kv['shadow']} | positive rate {kv['pos_rate']}",
        f"Cycle net {signed(kv['net'])} USD ({signed(kv['net_pct'])}%) | cycle max drawdown {kv['max_dd']} USD ({kv['max_dd_pct']}%)",
        f"Lifecycle net {signed(kv['life_net'])} USD | lifecycle max drawdown {kv['life_dd']} USD",
        f"Level L{kv['lvl_start']} -> L{kv['lvl_end']}",
        f"Block root {kv['root']}",
        f"Chain head {kv['head']}",
        f"Anchor {_hash(line)}"])


def fmt_lifecycle(line):
    kv = _kv(line)
    return "\n".join([
        f"{HEAD} | {kv['life']} | lifecycle complete: {kv['events']} events in {kv['cycles']} cycles",
        f"Positive {kv['pos']} | negative {kv['neg']} | manual {kv['man']} | shadow {kv['shadow']}",
        f"Net {signed(kv['net'])} USD ({signed(kv['net_pct'])}%) | max drawdown {kv['max_dd']} USD ({kv['max_dd_pct']}%) | "
        f"envelope violations {kv['violations']}",
        f"Final head {kv['head']}"])


def message_body(kind, record):
    """What Outbox.mqh writes after the '---' line: the formatted text, then the record itself."""
    f = {"GENESIS": fmt_genesis, "EVENT": fmt_event, "AUDIT": fmt_audit, "LIFECYCLE": fmt_lifecycle}[kind]
    return f(record) + "\nRecord: " + record


OUTBOX_FORMAT = "SEESARE-OUTBOX/2"


def outbox_message(seq, kind, life, ref, utc_iso, record):
    """Twin of CSeesareOutbox::Push: the message text with LF line ends (the file on disk has CRLF)."""
    text = (f"{OUTBOX_FORMAT}\nseq={seq:010d}\nkind={kind}\nlife={life}\nref={ref}\nutc={utc_iso}\n---\n"
            + message_body(kind, record) + "\n")
    return text + "sum=" + S.sha(text) + "\n"


def relay_text(message):
    """What the relay posts: the lines between '---' and 'sum=' (after checking sum=)."""
    lines = message.split("\n")
    if lines[-1] == "":
        lines = lines[:-1]
    body, last = lines[:-1], lines[-1]
    if not last.startswith("sum=") or S.sha("\n".join(body) + "\n") != last[4:]:
        raise ValueError("checksum mismatch")
    return "\n".join(body[body.index("---") + 1:])


def lifecycle_summary(L):
    """Twin of CSeesareCycleLedger::LifecycleSummary."""
    return (f"v=1|life={L.life}|audit=lifecycle|events={L.n}|cycles={len(L.anchors)}|shadow={L.shadow}|pos={L.t_pos}|"
            f"neg={L.t_neg}|man={L.t_man}|net={S.num(L.l_net, 4)}|net_pct={S.num(L.l_net * 100.0 / S.BASELINE, 5)}|"
            f"max_dd={S.num(L.l_dd, 4)}|max_dd_pct={S.num(L.l_dd * 100.0 / S.BASELINE, 5)}|violations={len(L.violations)}|"
            f"head={L.head}")


# ------------------------------------------------------------------------------------------------ sizing (Exposure.mqh)
def units_per_usd(currency):
    """Account money units per US dollar: USD 1, cent accounts (USC) 100, anything else 0 = refuse."""
    c = currency.strip().upper()
    if c == "USD":
        return 1.0
    if c in ("USC", "USX", "USCENT", "US CENT", "CENT"):
        return 100.0
    return 0.0


def level_table(weight, per_lot_usd, step, vmin):
    """Planned risk and volume at each of the 16 drawdown levels (the ledger's rounding), feasible = volume >= broker minimum."""
    out = []
    for lv in range(S.LEVELS):
        plan = float(S.plan_text(lv, weight))
        vol = math.floor(plan / per_lot_usd / step + 1e-9) * step if per_lot_usd > 0 else 0.0
        out.append((lv, plan, vol, vol >= vmin - 1e-12))
    return out


def table_text(rows):
    return "|".join(f"L{lv} {S.num(plan, 4)} {S.num(vol, 2)} {'real' if ok else 'shadow'}" for lv, plan, vol, ok in rows)


def lowest_feasible(rows):
    ok = [lv for lv, _, _, f in rows if f]
    return max(ok) if ok else -1


# ------------------------------------------------------------------------------------------------ deals (DealReader.mqh)
DEAL_REASONS = [("DEAL_REASON_SL", "STOP"), ("DEAL_REASON_TP", "TARGET"), ("DEAL_REASON_SO", "BROKER"),
                ("DEAL_REASON_EXPERT", "TIME"), ("DEAL_REASON_CLIENT", "HUMAN"), ("DEAL_REASON_MOBILE", "HUMAN"),
                ("DEAL_REASON_WEB", "HUMAN"), ("DEAL_REASON_ROLLOVER", "BROKER"), ("DEAL_REASON_VMARGIN", "BROKER"),
                ("DEAL_REASON_SPLIT", "BROKER")]


# ------------------------------------------------------------------------------------------------ vectors
TABLE_CASES = [("cent USDJPY 0.3% stop, weight 0.57", 0.57, 3.00), ("cent USDJPY 0.3% stop, weight 1.00", 1.0, 3.00),
               ("standard USDJPY 0.3% stop, weight 0.57", 0.57, 300.0), ("cent EURUSD 10-pip stop, weight 0.25", 0.25, 1.00)]
CURRENCIES = [("USD", 1.0), ("USC", 100.0), ("usc", 100.0), (" USC ", 100.0), ("EUR", 0.0), ("", 0.0)]
SIGNED = [("0.4321", "+0.4321"), ("-0.0592", "-0.0592"), ("0.0000", "0.0000"), ("0.00000", "0.00000"), ("12.0000", "+12.0000"),
          ("", "")]
OUTBOX_SAMPLE = dict(seq=1, kind="EVENT", life="SELFTEST", ref=1, utc="2026-11-05T00:55:00Z")

# End to end on a cent account: a closed USDJPY position read from two broker deals (tickets 50001000/50001001),
# net +30.8 US cents = +0.3080 USD, recorded by a fresh ledger; its outbox message 2 is checked byte for byte.
CENT_LIFE = "P3SELFTEST"
CENT_MONEY, CENT_UNITS = 30.8, 100.0


def cent_event():
    t0 = S.date(2026, 11, 4, 23, 0)
    return dict(mode="REAL", module="TOKYO_FIX", domain="forex", symbol="USDJPY", side=1, digits=3, open=t0,
                close=t0 + 115 * 60, by="TIME", weight=0.57, risk=0.12, vol=0.04, entry=151.234, lower=150.78,
                upper=151.706, exit=151.311, delta=CENT_MONEY / CENT_UNITS, deals="50001000;50001001")


def cent_case():
    L = S.Ledger(CENT_LIFE)
    L.genesis_line(S.SELFTEST_CREATED)
    e = cent_event()
    line = L.record(e)
    return line, outbox_message(2, "EVENT", CENT_LIFE, 1, S.iso(e["close"]), line)


def samples():
    L, lines = S.build_selftest()
    lock = S.Ledger("SELFTEST_LOCK")
    lock.genesis_line(S.SELFTEST_CREATED)
    for i in range(S.LIFECYCLE_EVENTS):
        lock.record(S.lock_event(i))
    return dict(genesis=L.lines[0], event_real=lines[0], event_shadow=lines[2], anchor=L.anchors[0],
                lifecycle=lifecycle_summary(lock))


def vectors():
    sm = samples()
    out = {"text " + k: (fmt_genesis if k == "genesis" else fmt_audit if k == "anchor" else fmt_lifecycle
                         if k == "lifecycle" else fmt_event)(v) for k, v in sm.items()}
    for name, weight, per_lot in TABLE_CASES:
        rows = level_table(weight, per_lot, 0.01, 0.01)
        out[f"table {name}"] = table_text(rows)
        out[f"lowest feasible {name}"] = lowest_feasible(rows)
    for c, u in CURRENCIES:
        out[f"units {c}"] = u
    o = OUTBOX_SAMPLE
    out["outbox message"] = outbox_message(o["seq"], o["kind"], o["life"], o["ref"], o["utc"], sm["event_real"])
    return out


def _q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _lines_check(o, name, expr, text):
    """Line count + one check per line: keeps every string literal short (no literal over ~600 characters)."""
    lines = text.split("\n")
    o.append(f"   T_Int({_q(name + ': lines')}, LineCount({expr}), {len(lines)});")
    for i, ln in enumerate(lines):
        o.append(f"   T_Str({_q(name + ': line ' + str(i + 1))}, Line({expr}, {i}), {_q(ln)});")


def mql_block():
    sm = samples()
    v = vectors()
    o = ["//--- BEGIN GENERATED VECTORS: python3 tools/seesare_outbox.py --mql  (do not edit by hand)"]
    for k, val in sm.items():
        o.append(f"#define VEC3_{k.upper()} {_q(val)}")
    ob = OUTBOX_SAMPLE
    msg = v["outbox message"]
    o.append(f"#define VEC3_OUTBOX_LINES {len(msg.rstrip(chr(10)).split(chr(10)))}")
    o.append(f"#define VEC3_OUTBOX_SUM {_q(msg.rstrip(chr(10)).split(chr(10))[-1])}")
    cl, cm = cent_case()
    cml = cm.rstrip("\n").split("\n")
    o.append(f"#define VEC3_CENT_RECORD {_q(cl)}")
    o.append(f"#define VEC3_CENT_LINES {len(cml)}")
    o.append(f"#define VEC3_CENT_HEAD {_q(cml[7])}")
    o.append(f"#define VEC3_CENT_RESULT {_q(cml[10])}")
    o.append(f"#define VEC3_CENT_DEALS {_q(cml[13])}")
    o.append(f"#define VEC3_CENT_SUM {_q(cml[-1])}")
    o += ["void GeneratedVectors(void)", "  {"]
    t = o.append
    _lines_check(o, "telegram genesis", "CSeesareTelegram::Genesis(VEC3_GENESIS)", v["text genesis"])
    _lines_check(o, "telegram real event", "CSeesareTelegram::Event(VEC3_EVENT_REAL)", v["text event_real"])
    _lines_check(o, "telegram shadow event", "CSeesareTelegram::Event(VEC3_EVENT_SHADOW)", v["text event_shadow"])
    _lines_check(o, "telegram cycle audit", "CSeesareTelegram::Audit(VEC3_ANCHOR)", v["text anchor"])
    _lines_check(o, "telegram lifecycle", "CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE)", v["text lifecycle"])
    for kind, key in (("GENESIS", "genesis"), ("EVENT", "event_real"), ("EVENT", "event_shadow"), ("AUDIT", "anchor"),
                      ("LIFECYCLE", "lifecycle")):
        body = message_body(kind, sm[key])
        expr = f"CSeesareTelegram::Body(\"{kind}\", VEC3_{key.upper()})"
        t(f"   T_Str({_q('outbox body ' + key + ': SHA-256')}, CSeesareSha256::Hex({expr}), {_q(S.sha(body))});")
        t(f"   T_Int({_q('outbox body ' + key + ': length')}, StringLen({expr}), {len(body)});")
        t(f"   T_Str({_q('outbox body ' + key + ': record line')}, Line({expr}, {len(body.split(chr(10))) - 1}), "
          f"RecordLine(VEC3_{key.upper()}));")
    t("   T_Str(\"outbox body for a malformed record\", CSeesareTelegram::Body(\"EVENT\", \"v=1||k=2\"), \"\");")
    t("   T_Str(\"outbox body for an unknown kind\", CSeesareTelegram::Body(\"NOTE\", VEC3_EVENT_REAL), \"\");")
    for a, b in SIGNED:
        t(f"   T_Str({_q('signed ' + repr(a))}, CSeesareTelegram::Signed({_q(a)}), {_q(b)});")
    for name, weight, per_lot in TABLE_CASES:
        t(f"   T_Str({_q('levels ' + name)}, LevelTable({weight!r}, {per_lot!r}), {_q(v['table ' + name])});")
        t(f"   T_Int({_q('lowest feasible level ' + name)}, CSeesareExposure::LowestFeasibleLevel({weight!r}, "
          f"{per_lot!r}, 0.01, 0.01), {v['lowest feasible ' + name]});")
    for c, u in CURRENCIES:
        t(f"   T_Str({_q('money units per USD for [' + c + ']')}, CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd({_q(c)}), 1), "
          f"{_q(S.num(u, 1))});")
    for reason, by in DEAL_REASONS:
        t(f"   T_Str(\"deal reason {reason}\", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason({reason})), "
          f"\"{by}\");")
    o += ["  }", "//--- END GENERATED VECTORS"]
    return "\n".join(o)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mql":
        print(mql_block())
    else:
        for k, val in vectors().items():
            print(f"--- {k}\n{val}")

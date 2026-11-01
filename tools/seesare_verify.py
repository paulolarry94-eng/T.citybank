"""SEESARE P26 router, Phase 1: Python twin of the MQL5 clock and cycle ledger, public verifier, and generator of the
MQL5 self-test vectors.

The MQL5 code in mt5/Seesare/Include/Seesare mirrors this file function by function. MQL5 cannot be compiled in this
container, so mt5/Seesare/Scripts/SeesarePhase1SelfTest.mq5 carries vectors generated here (--mql) and checks the
compiled code against them on the owner's terminal.

    python3 tools/seesare_verify.py LEDGER.txt [ANCHORS.txt]   verify a lifecycle written by the EA (exit 0 = intact)
    python3 tools/seesare_verify.py --vectors                  print the reference vectors
    python3 tools/seesare_verify.py --mql                      print the generated block of the MQL5 self-test

What the chain proves. Every ledger line carries the SHA-256 of the line before it (keyless), so changing any recorded
event changes every later hash. Anyone can recompute a keyless chain from scratch, so it proves integrity only against a
head published elsewhere (the outbox stream, anchors.txt, a public post). The verifier also checks every rule that can be
checked from the text alone: the SEESARE ladder moves, the multiplier, friction and planned delta, the 10-event cycles, the
lifecycle lock, and the pre-trade envelope rule (drawdown before the event + its all-in risk <= 3.6% of $1,000).
Deal tickets in each REAL line can be matched against the broker statement.
"""
import sys
import math
import re
import hashlib
import datetime as dt

# ================================================================================================ constants
BASELINE = 1000.0            # fixed virtual State Value, insulated from withdrawals and fees
CYCLE_EVENTS = 10
LIFECYCLE_EVENTS = 360
ENVELOPE_PCT = 3.6           # peak-to-trough cap on the lifecycle's real P&L, % of BASELINE
EXPONENT = 2.0               # structural multiplier below 3.5:1 (owner's decision, 2026-11-01)
LEVELS = 16
FORMAT = "1"
LADDER = [0.144, 0.095, 0.062, 0.041, 0.027, 0.018, 0.012, 0.008, 0.005, 0.0033, 0.0022, 0.0014, 0.0009, 0.0006,
          0.0004, 0.0003]    # SEESARE P26 section 5, % of State Value per level
FRICTION = {"forex": 0.05, "crypto": 0.08, "stocks": 0.03, "indices": 0.025, "commodities": 0.04}   # SEESARE 8.2
GENESIS_KEYS = "v,life,k,genesis,baseline,events,cycle_size,envelope_pct,exponent,ladder,created".split(",")
EVENT_KEYS = ("v,life,k,mode,n,cycle,step,module,domain,symbol,side,open,close,by,res,lvl_before,lvl_after,neg_run,"
              "ratio,mult,fric,plan,risk,vol,entry,lower,upper,exit,delta,deals,prev").split(",")
AUDIT_KEYS = ("v,life,audit,cycle,events,pos,neg,man,shadow,pos_rate,net,net_pct,max_dd,max_dd_pct,life_net,life_dd,"
              "lvl_start,lvl_end,root,head,prev").split(",")
CLOSE_BY = ["STOP", "TARGET", "TIME", "HUMAN", "BROKER"]          # order of ENUM_SEESARE_CLOSE
RES_NAME = {1: "POSITIVE", -1: "NEGATIVE", 0: "MANUAL"}
RES_VALUE = {v: k for k, v in RES_NAME.items()}
EMPTY_SHA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class LedgerError(Exception):
    pass


# ================================================================================================ text (Core/Text.mqh)
_TIES = []                  # near-tie values seen while TIE_CHECK is on (cross-language rounding risk)
TIE_CHECK = False


def num(x, d):
    """CSeesareText::Fmt: fixed decimals; values that would print as -0 print as 0."""
    if abs(x) < 0.5 / 10.0 ** d:
        x = 0.0
    if TIE_CHECK and d > 0:
        frac = abs(x) * 10.0 ** d
        if abs(frac - math.floor(frac) - 0.5) < 1e-6:
            _TIES.append((x, d))
    return f"{x:.{d}f}"


def floor_dp(x, d):
    """CSeesareText::FloorDp: round a non-negative value DOWN to d decimals. The +1e-6 absorbs binary error at exact
    boundaries; every step is one IEEE operation, so MQL5 and Python get the same bits, and the result k/10^d prints the
    same in both (no rounding tie is left to the formatter). Used for the multiplier and the planned delta."""
    m = 10.0 ** d
    return math.floor(x * m + 1e-6) / m


def is_decimal(s, d):
    pat = r"-?(0|[1-9][0-9]*)" + (r"\.[0-9]{%d}" % d if d > 0 else "")
    if not re.fullmatch(pat, s):
        return False
    return not (s.startswith("-") and set(s[1:]) <= set("0."))


def decimals(s):
    dot = s.find(".")
    if dot < 0:
        return 0 if is_decimal(s, 0) else -1
    d = len(s) - dot - 1
    return d if d >= 1 and is_decimal(s, d) else -1


def is_uint(s):
    return re.fullmatch(r"0|[1-9][0-9]{0,17}", s) is not None


def is_token(s, max_len=32):
    return 1 <= len(s) <= max_len and all(33 <= ord(c) <= 126 and c not in "|=;," for c in s)


def is_life(s):
    return re.fullmatch(r"[A-Za-z0-9_-]{1,32}", s) is not None


def is_hex64(s):
    return re.fullmatch(r"[0-9a-f]{64}", s) is not None


def is_deals(s):
    return s == "-" or (len(s) <= 200 and re.fullmatch(r"[0-9]+(;[0-9]+)*", s) is not None)


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ================================================================================================ clock (Core/Clock.mqh)
UTC, LONDON, FRANKFURT, NEW_YORK, TOKYO = "UTC", "LONDON", "FRANKFURT", "NEW_YORK", "TOKYO"
VENUE_ID = {UTC: 0, LONDON: 1, FRANKFURT: 2, NEW_YORK: 3, TOKYO: 4}          # ENUM_SEESARE_VENUE
GMT0, GMT2_EU, GMT2_US, FIXED = "GMT0", "GMT2_EU", "GMT2_US", "FIXED"
SCHEME_ID = {GMT0: 0, GMT2_EU: 1, GMT2_US: 2, FIXED: 3}                       # ENUM_SEESARE_SERVER_SCHEME
STD = {UTC: 0, LONDON: 0, FRANKFURT: 3600, NEW_YORK: -5 * 3600, TOKYO: 9 * 3600}
DAY, HOUR = 86400, 3600


def date(y, m, d, hh=0, mi=0):
    return int(dt.datetime(y, m, d, hh, mi, tzinfo=dt.timezone.utc).timestamp())


def _dts(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc)


def year(t):
    return _dts(t).year


def day_of_week(t):
    return (_dts(t).weekday() + 1) % 7            # 0 = Sunday, as MqlDateTime.day_of_week


def midnight(t):
    return t // DAY * DAY


def minute_of_day(t):
    return (t % DAY) // 60


def sunday_on_or_after(y, m, d):
    t = date(y, m, d)
    return t + ((7 - day_of_week(t)) % 7) * DAY


def us_start(y):
    return sunday_on_or_after(y, 3, 8) + 7 * HOUR        # 2nd Sunday of March, 02:00 New York standard time


def us_end(y):
    return sunday_on_or_after(y, 11, 1) + 6 * HOUR       # 1st Sunday of November, 02:00 New York summer time


def eu_start(y):
    return sunday_on_or_after(y, 3, 25) + HOUR           # last Sunday of March, 01:00 UTC


def eu_end(y):
    return sunday_on_or_after(y, 10, 25) + HOUR          # last Sunday of October, 01:00 UTC


def us_summer(t):
    y = year(t)
    return us_start(y) <= t < us_end(y)


def eu_summer(t):
    y = year(t)
    return eu_start(y) <= t < eu_end(y)


def is_summer(v, t):
    if v in (LONDON, FRANKFURT):
        return eu_summer(t)
    if v == NEW_YORK:
        return us_summer(t)
    return False


def venue_offset(v, t):
    return STD[v] + (HOUR if is_summer(v, t) else 0)


def utc_to_venue(v, t):
    return t + venue_offset(v, t)


def venue_to_utc(v, local):
    """Venue wall time -> UTC. Same answer as zoneinfo with fold=0: the first instant in the autumn repeat, and the
    standard-time reading inside the spring gap (a skipped 02:30 becomes 03:30 summer time)."""
    if v not in (LONDON, FRANKFURT, NEW_YORK):
        return local - STD[v]
    u_dst = local - STD[v] - HOUR
    return u_dst if is_summer(v, u_dst) else local - STD[v]


def scheme_offset(scheme, t, fixed_minutes=0):
    if scheme == GMT0:
        return 0
    if scheme == GMT2_EU:
        return (3 if eu_summer(t) else 2) * HOUR
    if scheme == GMT2_US:
        return (3 if us_summer(t) else 2) * HOUR
    return fixed_minutes * 60


def utc_to_server(scheme, t, fixed_minutes=0):
    return t + scheme_offset(scheme, t, fixed_minutes)


def server_to_utc(scheme, srv, fixed_minutes=0):
    if scheme in (GMT2_EU, GMT2_US):
        u3 = srv - 3 * HOUR
        return u3 if scheme_offset(scheme, u3) == 3 * HOUR else srv - 2 * HOUR
    return srv - scheme_offset(scheme, srv, fixed_minutes)


def iso(t):
    return _dts(t).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_to_time(s):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", s):
        return None
    try:
        t = int(dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp())
    except ValueError:
        return None
    return t if t >= date(1971, 1, 1) and iso(t) == s else None


def parse_hhmm(s):
    if not re.fullmatch(r"[0-9]{2}:[0-9]{2}", s):
        return -1
    h, m = int(s[:2]), int(s[3:])
    return h * 60 + m if h <= 23 and m <= 59 else -1


# ---------------------------------------------------------------------------------------------- timing matrix
MASK = {"MON_FRI": 62, "FRI": 32, "ALL": 127}
DEFAULT_WINDOWS = [   # (id, venue, start, end, mask): CSeesareTimingMatrix::LoadDefaults, blueprint section 4
    ("WMR_FIX", LONDON, "15:30", "16:10", "MON_FRI"),
    ("NY_MOC", NEW_YORK, "15:50", "16:05", "MON_FRI"),
    ("ECB_FIX", FRANKFURT, "14:05", "14:20", "MON_FRI"),
    ("NY_MOO", NEW_YORK, "09:15", "09:40", "MON_FRI"),
    ("US_NFP", NEW_YORK, "08:30", "10:00", "FRI"),
    ("FOMC", NEW_YORK, "14:00", "14:30", "MON_FRI"),
    ("TOKYO_FIX", TOKYO, "08:00", "09:55", "MON_FRI"),
    ("TOCOM_CLOSE", TOKYO, "15:15", "15:45", "MON_FRI"),
    ("FUNDING_00", UTC, "23:50", "00:10", "ALL"),
    ("FUNDING_08", UTC, "07:50", "08:10", "ALL"),
    ("FUNDING_16", UTC, "15:50", "16:10", "ALL"),
]


class Matrix:
    def __init__(self, windows=DEFAULT_WINDOWS):
        self.w = [(i, v, parse_hhmm(a), parse_hhmm(b), MASK[m]) for i, v, a, b, m in windows]

    def find(self, wid):
        return next((j for j, w in enumerate(self.w) if w[0] == wid), -1)

    def resolve(self, idx, local_date):
        wid, v, a, b, mask = self.w[idx]
        d = midnight(local_date)
        if not (mask >> day_of_week(d)) & 1:
            return None
        ls, le = d + a * 60, d + b * 60 + (DAY if b <= a else 0)
        return wid, idx, venue_to_utc(v, ls), venue_to_utc(v, le), d

    def active_at(self, idx, utc):
        d = midnight(utc_to_venue(self.w[idx][1], utc))
        for back in (1, 0):
            r = self.resolve(idx, d - back * DAY)
            if r and r[2] <= utc < r[3]:
                return r
        return None

    def next_at(self, idx, utc):
        d = midnight(utc_to_venue(self.w[idx][1], utc))
        for i in range(-1, 9):
            r = self.resolve(idx, d + i * DAY)
            if r and r[3] > utc:
                return r
        return None

    def on_utc_date(self, utc_any):
        day0 = midnight(utc_any)
        out = []
        for idx in range(len(self.w)):
            for i in (-1, 0, 1):
                r = self.resolve(idx, day0 + i * DAY)
                if r and day0 <= r[2] < day0 + DAY:
                    out.append(r)
        return sorted(out, key=lambda r: (r[2], r[1]))


# ================================================================================================ ladder (CycleLedger.mqh)
def ladder_text(p):
    return ",".join(num(x, 4) for x in p)


def ladder_check(v):
    if len(v) != LEVELS:
        raise LedgerError("the ladder needs 16 levels")
    for i, x in enumerate(v):
        if not 0.0 < x <= 1.0:
            raise LedgerError("ladder levels must be in (0, 1] percent")
        if i and x >= v[i - 1]:
            raise LedgerError("ladder levels must strictly decrease")
        if abs(float(num(x, 4)) - x) > 1e-12:
            raise LedgerError("ladder levels have at most 4 decimals")


def ladder_parse(s):
    parts = s.split(",")
    if len(parts) != LEVELS or not all(is_decimal(x, 4) for x in parts):
        raise LedgerError("malformed ladder")
    v = [float(x) for x in parts]
    ladder_check(v)
    return v


def ladder_next(level, neg_run, res):
    """SEESARE 7.1: a positive outcome climbs one level and clears the run; the 1st, 2nd, 3rd+ negative in a row
    descends 2, 3, 4 levels; a manual resolution changes nothing (the run is kept)."""
    if res == 1:
        return max(level - 1, 0), 0
    if res == -1:
        step = 2 if neg_run <= 0 else (3 if neg_run == 1 else 4)
        return min(level + step, LEVELS - 1), neg_run + 1
    return level, neg_run


def multiplier(r):
    if r >= 3.5:
        return min(1.0 + 0.10 * (r - 3.5), 1.5)
    return max((r / 3.5) ** EXPONENT, 0.082)


def plan_usd(level_pct, mult, fric):
    return BASELINE * level_pct / 100.0 * mult * (1.0 - fric)


def classify(by, delta, time_loss_negative=False):
    """CSeesareLadder::Classify. Default = owner's mandate: every time exit is MANUAL. Option: a losing time exit is
    NEGATIVE (descends the ladder)."""
    if by in ("STOP", "BROKER"):
        return -1
    if by == "TARGET":
        return 1
    if by == "TIME":
        return -1 if (time_loss_negative and delta < 0) else 0
    return 0


# ================================================================================================ ledger
def parse(content):
    keys, kv = [], {}
    for part in content.split("|"):
        if part == "":
            return None
        k, v = part.split("=", 1) if "=" in part else (part, "")
        if k == "" or k in kv:
            return None
        keys.append(k)
        kv[k] = v
    return keys, kv


def split_line(line):
    if len(line) < 71 or line[-70:-64] != "|hash=":
        return None, None
    return line[:-70], line[-64:]


class Ledger:
    """Replays (or writes) a lifecycle exactly as CSeesareCycleLedger does: one code path, apply_line, for both."""

    def __init__(self, life, ladder=None, adopt_ladder=False):
        if not is_life(life):
            raise LedgerError("bad lifecycle id")
        self.life = life
        self.config = list(LADDER if ladder is None else ladder)
        self.adopt_ladder = adopt_ladder
        self.ladder = None
        self.lines, self.hashes, self.line_utc = [], [], []
        self.audits, self.anchors, self.anchor_k = [], [], []
        self.genesis = self.head = ""
        self.created = 0
        self.k = -1
        self.n = self.shadow = 0
        self.level = self.neg_run = 0
        self.cycle = 1
        self.locked = False
        self.last_open = self.last_close = self.last_real_open = 0
        self.cycle_hashes = []
        self.c_pos = self.c_neg = self.c_man = self.c_shadow = self.c_level_start = 0
        self.c_net = self.c_peak = self.c_dd = 0.0
        self.t_pos = self.t_neg = self.t_man = 0
        self.l_net = self.l_peak = self.l_dd = 0.0
        self.violations = []

    # ------------------------------------------------------------------ the single code path
    def apply_line(self, line, dry=False):
        c, h = split_line(line)
        if c is None or not is_hex64(h):
            raise LedgerError(f"malformed line after k={self.k}")
        if sha(c) != h:
            raise LedgerError(f"hash mismatch after k={self.k}: the line was changed")
        p = parse(c)
        if p is None:
            raise LedgerError(f"malformed fields after k={self.k}")
        keys, kv = p
        if kv.get("v") != FORMAT:
            raise LedgerError("unknown format version")
        if kv.get("life") != self.life:
            raise LedgerError(f"line belongs to lifecycle {kv.get('life')}")
        if "genesis" in kv:
            return self._genesis(keys, kv, h, line, dry)
        return self._event(keys, kv, h, line, dry)

    def _genesis(self, keys, kv, h, line, dry):
        if self.k >= 0:
            raise LedgerError("a second genesis line")
        if keys != GENESIS_KEYS or kv["k"] != "0" or kv["genesis"] != "":
            raise LedgerError("genesis fields out of order")
        if (kv["baseline"], kv["events"], kv["cycle_size"], kv["envelope_pct"], kv["exponent"]) != (
                num(BASELINE, 2), str(LIFECYCLE_EVENTS), str(CYCLE_EVENTS), num(ENVELOPE_PCT, 2), num(EXPONENT, 2)):
            raise LedgerError("genesis constants differ from this build")
        lad = ladder_parse(kv["ladder"])
        if not self.adopt_ladder and ladder_text(lad) != ladder_text(self.config):
            raise LedgerError("the configured ladder differs from the lifecycle's genesis ladder")
        created = iso_to_time(kv["created"])
        if created is None:
            raise LedgerError("bad genesis time")
        if dry:
            return
        self.ladder, self.created = lad, created
        self.genesis = self.head = h
        self.k = 0
        self.last_close = created
        self._remember(line, h, created)

    def _event(self, keys, kv, h, line, dry):
        if self.k < 0:
            raise LedgerError("event before the genesis line")
        if self.locked:
            raise LedgerError("event after the lifecycle lock (360 real events)")
        if keys != EVENT_KEYS:
            raise LedgerError(f"event fields missing or out of order at k={self.k + 1}")
        k = self.k + 1
        if kv["k"] != str(k):
            raise LedgerError(f"chain index gap at k={k}")
        if kv["prev"] != self.head:
            raise LedgerError(f"broken link at k={k}: prev is not the hash of the line before")
        real = kv["mode"] == "REAL"
        if not real and kv["mode"] != "SHADOW":
            raise LedgerError(f"bad mode at k={k}")
        if kv["cycle"] != str(self.cycle):
            raise LedgerError(f"cycle number wrong at k={k}")
        if real and (kv["n"] != str(self.n + 1) or kv["step"] != str(self.n % CYCLE_EVENTS + 1)):
            raise LedgerError(f"real-event numbering broken at k={k}")
        if not real and (kv["n"] != str(self.n) or kv["step"] != "-"):
            raise LedgerError(f"shadow-event numbering broken at k={k}")
        if not is_token(kv["module"]) or not is_token(kv["symbol"]):
            raise LedgerError(f"bad module or symbol at k={k}")
        fric = FRICTION.get(kv["domain"])
        if fric is None or kv["fric"] != num(fric, 4):
            raise LedgerError(f"domain or friction not in the SEESARE table at k={k}")
        if kv["side"] not in ("BUY", "SELL"):
            raise LedgerError(f"bad side at k={k}")
        t_open, t_close = iso_to_time(kv["open"]), iso_to_time(kv["close"])
        if t_open is None or t_close is None:
            raise LedgerError(f"bad time at k={k}")
        if t_close < t_open or t_open < self.last_close:
            raise LedgerError(f"events out of time order at k={k}")
        if kv["by"] not in CLOSE_BY or kv["res"] not in RES_VALUE:
            raise LedgerError(f"bad exit kind or resolution at k={k}")
        res = RES_VALUE[kv["res"]]
        if kv["lvl_before"] != str(self.level):
            raise LedgerError(f"lvl_before is not the ladder's level at k={k}")
        la, na = ladder_next(self.level, self.neg_run, res)
        if kv["lvl_after"] != str(la) or kv["neg_run"] != str(na):
            raise LedgerError(f"ladder rule broken at k={k}")
        for f, d in (("ratio", 2), ("mult", 4), ("plan", 4), ("risk", 4), ("vol", 4), ("delta", 4)):
            if not is_decimal(kv[f], d):
                raise LedgerError(f"malformed {f} at k={k}")
        ratio, mult, plan = float(kv["ratio"]), float(kv["mult"]), float(kv["plan"])
        risk, vol, delta = float(kv["risk"]), float(kv["vol"]), float(kv["delta"])
        if not 0.0 < ratio <= 100.0:
            raise LedgerError(f"declared ratio out of range at k={k}")
        if abs(mult - multiplier(ratio)) > 0.0001 + 1e-9:
            raise LedgerError(f"multiplier does not match the declared ratio at k={k}")
        if abs(plan - plan_usd(self.ladder[self.level], mult, fric)) > 0.0001 + 1e-9:
            raise LedgerError(f"planned delta does not match the ladder at k={k}")
        if risk < 0.0 or vol < 0.0:
            raise LedgerError(f"negative risk or volume at k={k}")
        deals = kv["deals"]
        if not is_deals(deals):
            raise LedgerError(f"bad deal tickets at k={k}")
        if real and (risk <= 0.0 or vol <= 0.0 or deals == "-"):
            raise LedgerError(f"real event without risk, volume or deal tickets at k={k}")
        if not real and (risk != 0.0 or deals != "-"):
            raise LedgerError(f"shadow event with real risk or deal tickets at k={k}")
        pd = decimals(kv["entry"])
        if not 0 <= pd <= 8 or not all(is_decimal(kv[f], pd) for f in ("entry", "lower", "upper", "exit")):
            raise LedgerError(f"malformed prices at k={k}")
        entry, lower, upper, exitp = (float(kv[f]) for f in ("entry", "lower", "upper", "exit"))
        if min(entry, lower, exitp) <= 0.0 or upper <= lower:
            raise LedgerError(f"bad boundaries at k={k}")
        if dry:
            return
        # ---- commit
        if real:
            dd_before = self.l_peak - self.l_net
            if dd_before + risk > BASELINE * ENVELOPE_PCT / 100.0 + 1e-6:
                self.violations.append(k)
            if res > 0:
                self.c_pos += 1
                self.t_pos += 1
            elif res < 0:
                self.c_neg += 1
                self.t_neg += 1
            else:
                self.c_man += 1
                self.t_man += 1
            self.c_net += delta
            self.c_peak = max(self.c_peak, self.c_net)
            self.c_dd = max(self.c_dd, self.c_peak - self.c_net)
            self.l_net += delta
            self.l_peak = max(self.l_peak, self.l_net)
            self.l_dd = max(self.l_dd, self.l_peak - self.l_net)
            self.n += 1
            self.cycle_hashes.append(h)
            self.last_real_open = t_open
        else:
            self.shadow += 1
            self.c_shadow += 1
        self.level, self.neg_run, self.k, self.head = la, na, k, h
        self.last_open, self.last_close = t_open, t_close
        self._remember(line, h, t_close)
        if real and self.n % CYCLE_EVENTS == 0:
            self._close_cycle()
        if self.n >= LIFECYCLE_EVENTS:
            self.locked = True

    def _remember(self, line, h, utc):
        self.lines.append(line)
        self.hashes.append(h)
        self.line_utc.append(utc)

    def _close_cycle(self):
        first = self.n - CYCLE_EVENTS + 1
        decided = self.c_pos + self.c_neg
        rate = num(self.c_pos / decided, 4) if decided > 0 else "-"
        root = sha(f"{self.life}|{self.cycle}|{','.join(self.cycle_hashes)}")
        audit = (f"v={FORMAT}|life={self.life}|audit=cycle|cycle={self.cycle}|events={first}-{self.n}|pos={self.c_pos}|"
                 f"neg={self.c_neg}|man={self.c_man}|shadow={self.c_shadow}|pos_rate={rate}|net={num(self.c_net, 4)}|"
                 f"net_pct={num(self.c_net * 100.0 / BASELINE, 5)}|max_dd={num(self.c_dd, 4)}|"
                 f"max_dd_pct={num(self.c_dd * 100.0 / BASELINE, 5)}|life_net={num(self.l_net, 4)}|"
                 f"life_dd={num(self.l_dd, 4)}|lvl_start={self.c_level_start}|lvl_end={self.level}|root={root}|"
                 f"head={self.head}")
        prev = split_line(self.anchors[-1])[1] if self.anchors else self.genesis
        content = f"{audit}|prev={prev}"
        self.audits.append(audit)
        self.anchors.append(f"{content}|hash={sha(content)}")
        self.anchor_k.append(self.k)
        self.c_pos = self.c_neg = self.c_man = self.c_shadow = 0
        self.c_net = self.c_peak = self.c_dd = 0.0
        self.cycle_hashes = []
        self.c_level_start = self.level
        self.cycle += 1

    # ------------------------------------------------------------------ writing (CSeesareCycleLedger::Open / Record)
    def genesis_line(self, created):
        g = (f"v={FORMAT}|life={self.life}|k=0|genesis|baseline={num(BASELINE, 2)}|events={LIFECYCLE_EVENTS}|"
             f"cycle_size={CYCLE_EVENTS}|envelope_pct={num(ENVELOPE_PCT, 2)}|exponent={num(EXPONENT, 2)}|"
             f"ladder={ladder_text(self.config)}|created={iso(created)}")
        line = f"{g}|hash={sha(g)}"
        self.apply_line(line, dry=True)
        self.apply_line(line)
        return line

    def build_event_line(self, e):
        real = e["mode"] == "REAL"
        fric = FRICTION[e["domain"]]
        s_ratio = num(e["ratio"], 2)
        s_mult = num(floor_dp(multiplier(float(s_ratio)), 4), 4)
        s_plan = num(floor_dp(plan_usd(self.ladder[self.level], float(s_mult), fric), 4), 4)
        la, na = ladder_next(self.level, self.neg_run, e["res"])
        p = e["digits"]
        fields = [
            ("v", FORMAT), ("life", self.life), ("k", str(self.k + 1)), ("mode", "REAL" if real else "SHADOW"),
            ("n", str(self.n + 1 if real else self.n)), ("cycle", str(self.cycle)),
            ("step", str(self.n % CYCLE_EVENTS + 1) if real else "-"), ("module", e["module"]),
            ("domain", e["domain"]), ("symbol", e["symbol"]), ("side", "BUY" if e["side"] > 0 else "SELL"),
            ("open", iso(e["open"])), ("close", iso(e["close"])), ("by", e["by"]), ("res", RES_NAME[e["res"]]),
            ("lvl_before", str(self.level)), ("lvl_after", str(la)), ("neg_run", str(na)), ("ratio", s_ratio),
            ("mult", s_mult), ("fric", num(fric, 4)), ("plan", s_plan), ("risk", num(e["risk"] if real else 0.0, 4)),
            ("vol", num(e["vol"], 4)), ("entry", num(e["entry"], p)), ("lower", num(e["lower"], p)),
            ("upper", num(e["upper"], p)), ("exit", num(e["exit"], p)), ("delta", num(e["delta"], 4)),
            ("deals", e["deals"] if real else "-"), ("prev", self.head)]
        c = "|".join(f"{k}={v}" for k, v in fields)
        return f"{c}|hash={sha(c)}"

    def record(self, e):
        line = self.build_event_line(e)
        self.apply_line(line, dry=True)
        self.apply_line(line)
        return line

    # ------------------------------------------------------------------ pre-trade questions
    def drawdown(self):
        return self.l_peak - self.l_net

    def envelope_room(self):
        return BASELINE * ENVELOPE_PCT / 100.0 - self.drawdown()

    def allows_real_risk(self, risk):
        """CSeesareCycleLedger::AllowsRealRisk: a REAL event may open only if drawdown + its all-in risk stays within
        3.6% of the $1,000 baseline. Risk is taken as it will be written (4 decimals)."""
        if self.locked or self.violations or risk <= 0.0:
            return False
        return self.drawdown() + float(num(risk, 4)) <= BASELINE * ENVELOPE_PCT / 100.0 + 1e-9

    def plan_at(self, ratio, domain):
        s_mult = num(floor_dp(multiplier(float(num(ratio, 2))), 4), 4)
        return float(num(floor_dp(plan_usd(self.ladder[self.level], float(s_mult), FRICTION[domain]), 4), 4))


# ================================================================================================ verifier
def _close(a, b, d):
    return abs(float(a) - float(b)) <= 1.01 * 10.0 ** (-d)


def check_anchor(line, want, prev, cycle):
    """Compares an anchor written by MQL5 with the one replayed here. Integers, hashes and ranges must match exactly;
    money fields within one unit of their last decimal (MQL5 and Python may round a printed decimal differently)."""
    c, h = split_line(line)
    if c is None or not is_hex64(h) or sha(c) != h:
        raise LedgerError(f"anchor {cycle}: hash mismatch")
    p = parse(c)
    if p is None or p[0] != AUDIT_KEYS:
        raise LedgerError(f"anchor {cycle}: fields out of order")
    kv = p[1]
    wkv = parse(split_line(want)[0])[1]
    if kv["prev"] != prev:
        raise LedgerError(f"anchor {cycle}: broken link")
    for f in ("v", "life", "audit", "cycle", "events", "pos", "neg", "man", "shadow", "lvl_start", "lvl_end", "root",
              "head"):
        if kv[f] != wkv[f]:
            raise LedgerError(f"anchor {cycle}: {f} differs from the ledger")
    for f, d in (("net", 4), ("net_pct", 5), ("max_dd", 4), ("max_dd_pct", 5), ("life_net", 4), ("life_dd", 4)):
        if not is_decimal(kv[f], d) or not _close(kv[f], wkv[f], d):
            raise LedgerError(f"anchor {cycle}: {f} differs from the ledger")
    if (kv["pos_rate"] == "-") != (wkv["pos_rate"] == "-") or (
            kv["pos_rate"] != "-" and not _close(kv["pos_rate"], wkv["pos_rate"], 4)):
        raise LedgerError(f"anchor {cycle}: pos_rate differs from the ledger")
    return h


def verify(lines, anchor_lines=None):
    """Replays a ledger; raises LedgerError on any break. Returns the replayed Ledger."""
    if not lines:
        raise LedgerError("empty ledger")
    c, _ = split_line(lines[0])
    p = parse(c) if c else None
    if p is None or not is_life(p[1].get("life", "")):
        raise LedgerError("first line is not a genesis line")
    L = Ledger(p[1]["life"], adopt_ladder=True)
    for line in lines:
        L.apply_line(line)
    if anchor_lines is not None:
        if len(anchor_lines) > len(L.anchors):
            raise LedgerError("anchors file has more cycles than the ledger: the ledger lost lines")
        prev = L.genesis
        for i, line in enumerate(anchor_lines):
            prev = check_anchor(line, L.anchors[i], prev, i + 1)
    return L


def read_lines(path):
    with open(path, encoding="utf-8-sig") as f:
        return [s.rstrip("\r\n") for s in f if s.strip()]


# ================================================================================================ self-test vectors
SELFTEST_LIFE = "SELFTEST"
SELFTEST_CREATED = date(2026, 11, 1)
_B = ("USDJPY", 3, 151.234, 151.084)      # symbol, digits, entry, BUY stop (150 points)
# mode, side, by, res, ratio, target, exit, delta, vol, risk. BUY: lower = stop, upper = target; SELL: mirrored.
SAMPLE = [
    ("REAL", 1, "TIME", 0, 3.5, 151.759, 151.311, 0.4321, 0.01, 1.06),     # time exit, small gain: MANUAL
    ("REAL", 1, "STOP", -1, 3.5, 151.759, 151.084, -1.0592, 0.01, 1.06),   # L0 -> L2
    ("SHADOW", -1, "TARGET", 1, 3.5, 150.709, 150.709, 2.0615, 0.0059, 0),  # L2 -> L1 on paper
    ("SHADOW", 1, "TARGET", 1, 3.5, 151.759, 151.759, 3.1605, 0.0091, 0),   # L1 -> L0
    ("REAL", 1, "TARGET", 1, 2.0, 151.534, 151.534, 1.912, 0.01, 1.06),     # ratio 2: multiplier 0.3265
    ("REAL", 1, "TIME", 0, 5.0, 151.984, 151.204, -0.295, 0.01, 1.06),     # losing time exit: MANUAL (mandate)
    ("REAL", -1, "STOP", -1, 3.5, 150.709, 151.384, -1.0592, 0.01, 1.06),  # L0 -> L2
    ("SHADOW", 1, "STOP", -1, 3.5, 151.759, 151.084, -0.589, 0.0059, 0),   # 2nd negative: L2 -> L5
    ("SHADOW", 1, "TIME", 0, 3.5, 151.759, 151.25, 0.0122, 0.0017, 0),     # manual keeps the run
    ("SHADOW", 1, "STOP", -1, 3.5, 151.759, 151.084, -0.171, 0.0017, 0),   # 3rd negative: L5 -> L9
    ("SHADOW", 1, "TARGET", 1, 3.5, 151.759, 151.759, 0.1663, 0.0005, 0),  # L9 -> L8
    ("SHADOW", -1, "TARGET", 1, 0.8, 151.114, 151.114, 0.0301, 0.0003, 0),  # ratio 0.8: floor 0.082; L8 -> L7
    ("REAL", 1, "TARGET", 1, 3.5, 151.759, 151.759, 0.41, 0.01, 1.06),     # L7 -> L6
    ("REAL", 1, "TARGET", 1, 3.5, 151.759, 151.759, 0.39, 0.01, 1.06),     # L6 -> L5
    ("REAL", 1, "STOP", -1, 3.5, 151.759, 151.084, -0.18, 0.01, 1.06),     # L5 -> L7
    ("REAL", 1, "TIME", 0, 3.5, 151.759, 151.271, 0.05, 0.01, 1.06),       # manual keeps the run
    ("REAL", 1, "TARGET", 1, 3.5, 151.759, 151.759, 0.29, 0.01, 1.06),     # 10th REAL: cycle 1 closes; L7 -> L6
    ("REAL", 1, "STOP", -1, 3.5, 151.759, 151.084, -0.12, 0.01, 1.06),     # cycle 2 step 1: L6 -> L8
    ("SHADOW", 1, "HUMAN", 0, 3.5, 151.759, 151.3, 0.01, 0.0006, 0),       # human close: MANUAL
    ("REAL", -1, "BROKER", -1, 3.5, 150.709, 151.384, -0.09, 0.01, 1.06),  # stop-out: 2nd negative, L8 -> L11
]


def sample_event(i):
    mode, side, by, res, ratio, target, exitp, delta, vol, risk = SAMPLE[i]
    sym, digits, entry, stop = _B
    t0 = date(2026, 11, 4, 23, 0) + i * DAY
    lower, upper = (stop, target) if side > 0 else (target, round(2 * entry - stop, digits))
    return dict(mode=mode, module="TOKYO_FIX", domain="forex", symbol=sym, side=side, digits=digits, open=t0,
                close=t0 + 115 * 60, by=by, res=res, ratio=ratio, risk=risk, vol=vol, entry=entry, lower=lower,
                upper=upper, exit=exitp, delta=delta,
                deals=f"{50001000 + 2 * i};{50001001 + 2 * i}" if mode == "REAL" else "-")


def build_selftest():
    L = Ledger(SELFTEST_LIFE)
    L.genesis_line(SELFTEST_CREATED)
    return L, [L.record(sample_event(i)) for i in range(len(SAMPLE))]


def lock_event(i):
    """The 360-event lock test (same in the MQL5 self-test): two target hits, then one stop, one event a day."""
    t0 = date(2027, 1, 4, 23, 0) + i * DAY
    win = i % 3 != 2
    return dict(mode="REAL", module="LOCKTEST", domain="forex", symbol="USDJPY", side=1, digits=3, open=t0,
                close=t0 + 3600, by="TARGET" if win else "STOP", res=1 if win else -1, ratio=3.5, risk=1.06, vol=0.01,
                entry=151.234, lower=151.084, upper=151.759, exit=151.759 if win else 151.084,
                delta=0.25 if win else -0.4, deals=f"{60000000 + i}")


CLOCK_CASES = [   # (label, venue, local (y, m, d, hh, mi))
    ("LONDON 2026-03-10 16:00 (US already on summer time)", LONDON, (2026, 3, 10, 16, 0)),
    ("NEW_YORK 2026-03-10 15:50 (mismatch week)", NEW_YORK, (2026, 3, 10, 15, 50)),
    ("NEW_YORK 2026-03-02 15:50 (winter)", NEW_YORK, (2026, 3, 2, 15, 50)),
    ("LONDON 2026-07-01 16:00", LONDON, (2026, 7, 1, 16, 0)),
    ("FRANKFURT 2026-07-01 14:05", FRANKFURT, (2026, 7, 1, 14, 5)),
    ("TOKYO 2026-07-01 09:55", TOKYO, (2026, 7, 1, 9, 55)),
    ("NEW_YORK 2026-10-28 15:50 (EU back on winter time, US not)", NEW_YORK, (2026, 10, 28, 15, 50)),
    ("NEW_YORK 2026-03-08 02:30 (skipped hour)", NEW_YORK, (2026, 3, 8, 2, 30)),
    ("NEW_YORK 2026-11-01 01:30 (repeated hour)", NEW_YORK, (2026, 11, 1, 1, 30)),
    ("LONDON 2026-03-29 01:30 (skipped hour)", LONDON, (2026, 3, 29, 1, 30)),
    ("LONDON 2026-10-25 01:30 (repeated hour)", LONDON, (2026, 10, 25, 1, 30)),
    ("FRANKFURT 2027-03-28 02:30 (skipped hour)", FRANKFURT, (2027, 3, 28, 2, 30)),
]
SERVER_CASES = [  # (scheme, server time (y, m, d, hh, mi))
    (GMT2_US, (2026, 3, 10, 0, 0)), (GMT2_EU, (2026, 3, 10, 0, 0)), (GMT2_EU, (2026, 7, 1, 0, 0)),
    (GMT2_US, (2026, 10, 28, 0, 0)), (GMT2_EU, (2026, 10, 28, 0, 0)), (GMT0, (2026, 7, 1, 0, 0)),
]
MATRIX_DATES = [(2026, 3, 10), (2026, 3, 13), (2026, 7, 1), (2026, 10, 28), (2026, 11, 1), (2026, 12, 4)]
PROBES = [("TOKYO_FIX", (2026, 7, 1, 23, 30)), ("FUNDING_00", (2026, 7, 2, 0, 5)), ("NY_MOC", (2026, 3, 10, 19, 55)),
          ("NY_MOC", (2026, 3, 10, 20, 55)), ("WMR_FIX", (2026, 10, 30, 15, 45)), ("US_NFP", (2026, 3, 10, 13, 0))]
MULT_RATIOS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 8.5, 10.0]
TRANSITIONS = [(0, 0, 1), (0, 0, -1), (2, 1, -1), (5, 2, -1), (14, 3, -1), (15, 4, -1), (7, 2, 0), (7, 2, 1), (0, 5, 1)]
DECIMAL_CASES = [("0.4321", 4, True), ("-0.4321", 4, True), ("-0.0000", 4, False), ("00.4321", 4, False),
                 ("0.432", 4, False), ("1", 0, True), ("-1", 0, True), ("1.", 0, False), ("12.50", 2, True),
                 ("+1.00", 2, False), ("1e5", 0, False), ("", 2, False)]


def window_list(m, utc):
    return ",".join(f"{r[0]}@{iso(r[2])[11:16]}" for r in m.on_utc_date(utc))


def vectors():
    global TIE_CHECK
    TIE_CHECK = True
    _TIES.clear()
    out = {"sha256(abc)": sha("abc"),
           "sha256(two blocks)": sha("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")}
    for y in (2011, 2026, 2027, 2035):
        out[f"us_start {y}"], out[f"us_end {y}"] = iso(us_start(y)), iso(us_end(y))
        out[f"eu_start {y}"], out[f"eu_end {y}"] = iso(eu_start(y)), iso(eu_end(y))
    for label, v, a in CLOCK_CASES:
        out[f"to_utc {label}"] = iso(venue_to_utc(v, date(*a)))
    for s, a in SERVER_CASES:
        out[f"server {s} {iso(date(*a))[:16]} -> utc"] = iso(server_to_utc(s, date(*a)))
    m = Matrix()
    for y, mo, d in MATRIX_DATES:
        out[f"windows on {y}-{mo:02d}-{d:02d} (UTC start)"] = window_list(m, date(y, mo, d, 12))
    for r in MULT_RATIOS:
        out[f"multiplier {r:.2f}"] = num(floor_dp(multiplier(r), 4), 4)
    for i, p in enumerate(LADDER):
        out[f"plan L{i} forex 3.50"] = num(floor_dp(plan_usd(p, 1.0, FRICTION["forex"]), 4), 4)
    L, lines = build_selftest()
    out["genesis_line"] = L.lines[0]
    out["event1_line"] = lines[0]
    out["head_after_sample"] = L.head
    out["anchor1"] = L.anchors[0]
    out.update(level=L.level, neg_run=L.neg_run, real=L.n, shadow=L.shadow, cycle=L.cycle,
               life_net=num(L.l_net, 4), life_dd=num(L.l_dd, 4), envelope_room=num(L.envelope_room(), 4),
               messages=1 + len(lines) + len(L.anchors))
    TIE_CHECK = False
    if _TIES:
        raise SystemExit(f"vector values sit on a rounding tie, pick others: {_TIES}")
    return out


# ------------------------------------------------------------------------------------------------ MQL5 block
def _q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _d(x):
    r = repr(float(x))
    return r if ("." in r or "e" in r) else r + ".0"


def _date_call(a):
    return f"CSeesareDst::Date({', '.join(str(x) for x in a)})"


def mql_block():
    v = vectors()
    m = Matrix()
    L, lines = build_selftest()
    lock = Ledger("SELFTEST_LOCK")
    lock.genesis_line(SELFTEST_CREATED)
    for i in range(LIFECYCLE_EVENTS):
        lock.record(lock_event(i))
    o = ["//--- BEGIN GENERATED VECTORS: python3 tools/seesare_verify.py --mql  (do not edit by hand)",
         f"#define VEC_LIFE          {_q(SELFTEST_LIFE)}",
         f"#define VEC_EVENTS        {len(SAMPLE)}",
         f"#define VEC_MESSAGES      {v['messages']}",
         f"#define VEC_LEVEL         {L.level}",
         f"#define VEC_NEG_RUN       {L.neg_run}",
         f"#define VEC_REAL          {L.n}",
         f"#define VEC_SHADOW        {L.shadow}",
         f"#define VEC_CYCLE         {L.cycle}",
         f"#define VEC_LIFE_NET      {_q(v['life_net'])}",
         f"#define VEC_LIFE_DD       {_q(v['life_dd'])}",
         f"#define VEC_ROOM          {_q(v['envelope_room'])}",
         f"#define VEC_GENESIS       {_q(L.lines[0])}",
         f"#define VEC_EVENT1        {_q(lines[0])}",
         f"#define VEC_ANCHOR1       {_q(L.anchors[0])}",
         f"#define VEC_HEAD          {_q(L.head)}",
         f"#define VEC_LOCK_MESSAGES {1 + LIFECYCLE_EVENTS + LIFECYCLE_EVENTS // CYCLE_EVENTS + 1}",
         f"#define VEC_LOCK_HEAD     {_q(lock.head)}",
         f"#define VEC_LOCK_ANCHOR36 {_q(lock.anchors[-1])}"]
    ev = [sample_event(i) for i in range(len(SAMPLE))]

    def arr(name, typ, vals):
        o.append(f"const {typ} {name}[VEC_EVENTS] = {{{', '.join(vals)}}};")

    arr("VEC_MODE", "int", ["0" if e["mode"] == "REAL" else "1" for e in ev])
    arr("VEC_SIDE", "int", [str(e["side"]) for e in ev])
    arr("VEC_BY", "int", [str(CLOSE_BY.index(e["by"])) for e in ev])
    arr("VEC_RES", "int", [str(e["res"]) for e in ev])
    for key, name in (("ratio", "VEC_RATIO"), ("risk", "VEC_RISK"), ("vol", "VEC_VOL"), ("lower", "VEC_LOWER"),
                      ("upper", "VEC_UPPER"), ("exit", "VEC_EXIT"), ("delta", "VEC_DELTA")):
        arr(name, "double", [_d(e[key]) for e in ev])
    arr("VEC_DEALS", "string", [_q(e["deals"]) for e in ev])
    arr("VEC_HASH", "string", [_q(split_line(x)[1]) for x in lines])
    o += ["void GeneratedVectors(CSeesareTimingMatrix &m)", "  {"]
    t = o.append
    t(f"   T_Str(\"sha256 abc\", CSeesareSha256::Hex(\"abc\"), {_q(v['sha256(abc)'])});")
    t("   T_Str(\"sha256 two blocks\", CSeesareSha256::Hex(\"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq\"), "
      f"{_q(v['sha256(two blocks)'])});")
    t(f"   T_Str(\"sha256 empty\", CSeesareSha256::Hex(\"\"), {_q(EMPTY_SHA)});")
    for y in (2011, 2026, 2027, 2035):
        for fn, key in (("UsStart", "us_start"), ("UsEnd", "us_end"), ("EuStart", "eu_start"), ("EuEnd", "eu_end")):
            t(f"   T_Str(\"dst {key} {y}\", CSeesareDst::IsoUtc(CSeesareDst::{fn}({y})), {_q(v[f'{key} {y}'])});")
    for label, ven, a in CLOCK_CASES:
        call = f"CSeesareDst::VenueToUtc(SEESARE_VENUE_{ven}, {_date_call(a)})"
        t(f"   T_Str({_q('to utc ' + label)}, CSeesareDst::IsoUtc({call}), {_q(v['to_utc ' + label])});")
        back = iso(utc_to_venue(ven, venue_to_utc(ven, date(*a))))
        t(f"   T_Str({_q('back to local ' + label)}, CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_{ven}, "
          f"{call})), {_q(back)});")
    for s, a in SERVER_CASES:
        key = f"server {s} {iso(date(*a))[:16]} -> utc"
        t(f"   T_Str({_q(key)}, CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_{s}, "
          f"{_date_call(a)}, 0)), {_q(v[key])});")
    for y, mo, d in MATRIX_DATES:
        key = f"windows on {y}-{mo:02d}-{d:02d} (UTC start)"
        t(f"   T_Str({_q(key)}, WindowList(m, {_date_call((y, mo, d, 12, 0))}), {_q(v[key])});")
    for wid, *_ in DEFAULT_WINDOWS:
        idx = m.find(wid)
        for y, mo, d in MATRIX_DATES[:4]:
            r = m.resolve(idx, date(y, mo, d))
            want = f"{iso(r[2])}/{iso(r[3])}" if r else "closed"
            t(f"   T_Str(\"{wid} on local {y}-{mo:02d}-{d:02d}\", ResolveWin(m, \"{wid}\", {_date_call((y, mo, d))}), "
              f"{_q(want)});")
    for wid, a in PROBES:
        probe = date(*a)
        r = m.active_at(m.find(wid), probe)
        nx = m.next_at(m.find(wid), probe)
        t(f"   T_Str(\"active {wid} at {iso(probe)}\", ActiveWin(m, \"{wid}\", {_date_call(a)}), "
          f"{_q(iso(r[2]) if r else 'no')});")
        t(f"   T_Str(\"next {wid} after {iso(probe)}\", NextWin(m, \"{wid}\", {_date_call(a)}), {_q(iso(nx[2]))});")
    for r in MULT_RATIOS:
        t(f"   T_Str(\"multiplier {r:.2f}\", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier({_d(r)}), 4), 4), "
          f"{_q(v[f'multiplier {r:.2f}'])});")
    for i in range(LEVELS):
        t(f"   T_Str(\"plan L{i} forex 3.50\", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd("
          f"{_d(LADDER[i])}, 1.0, 0.05), 4), 4), {_q(v[f'plan L{i} forex 3.50'])});")
    for lv, nr, res in TRANSITIONS:
        la, na = ladder_next(lv, nr, res)
        t(f"   T_Str(\"ladder L{lv} run {nr} {RES_NAME[res]}\", Transition({lv}, {nr}, {res}), \"{la}/{na}\");")
    for by in CLOSE_BY:
        for delta in (0.5, -0.5):
            for pol in (0, 1):
                t(f"   T_Int(\"classify {by} {delta:+.1f} policy {pol}\", (long)CSeesareLadder::Classify("
                  f"(ENUM_SEESARE_CLOSE){CLOSE_BY.index(by)}, {_d(delta)}, (ENUM_SEESARE_TIME_POLICY){pol}), "
                  f"{classify(by, delta, pol == 1)});")
    for s, d, ok in DECIMAL_CASES:
        t(f"   T_Bool(\"decimal [{s}] with {d} places is {'valid' if ok else 'invalid'}\", "
          f"CSeesareText::IsDecimal({_q(s)}, {d}) == {'true' if ok else 'false'}, \"\");")
    o += ["  }", "//--- END GENERATED VECTORS"]
    return "\n".join(o)


# ================================================================================================ CLI
def main(argv):
    if len(argv) >= 2 and argv[1] == "--vectors":
        for k, val in vectors().items():
            print(f"{k} = {val}")
        return 0
    if len(argv) >= 2 and argv[1] == "--mql":
        print(mql_block())
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 2
    try:
        L = verify(read_lines(argv[1]), read_lines(argv[2]) if len(argv) > 2 else None)
    except (LedgerError, OSError) as ex:
        print(f"BROKEN: {ex}")
        return 1
    print(f"INTACT: lifecycle {L.life}: {L.n} real events (cycle {L.cycle}, {len(L.anchors)} closed), {L.shadow} shadow, "
          f"level {L.level}, head {L.head}")
    print(f"  real P&L {L.l_net:+.4f} USD, max drawdown {L.l_dd:.4f} USD ({L.l_dd / BASELINE * 100:.3f}% of the "
          f"$1,000 baseline), envelope room {L.envelope_room():.4f} USD")
    if L.violations:
        print(f"ENVELOPE RULE BROKEN: a REAL event opened with drawdown + risk above {ENVELOPE_PCT}% at k="
              f"{', '.join(map(str, L.violations))}")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

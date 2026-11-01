# SEESARE P26 x Payer-Flow Router: MQL5 object blueprint

Design document, 2026-11-01. Phase 1 (clock, timing matrix, spread gate, cycle ledger, outbox) now exists as uncompiled
source in `mt5/Seesare/` with a tested Python twin (`mt5/Seesare/README.md`); where this document and that code differ, the
code and its README are current (record format, envelope guard). Everything else here is still design. Sources: the owner's directive (24 flows, $1,000 virtual baseline, RoboForex ECN, 1 event a
day, 360-event lifecycle, Telegram attestation) and SEESARE P26 parts 1-2 (constraint hierarchy section 5, Structural Response
Multiplier 6.2, descent rules 7.1, friction 8.2, exposure formula 9.1, lifecycle 16, HMAC chain 18, terminology 48). Numbers in
section 0 were recomputed for this document (script output in the session log, reproducible from the formulas below).

Terminology follows SEESARE section 48: State Value (account value), Exposure Unit (volume), Constraint Level (risk level),
Event Resolution (trade), Declared Ratio (reward:risk), Lower/Upper Boundary (stop/target), Constraint Delta (planned loss).

## 0. Findings that shape the design (read first)

| # | Finding | Evidence | Design consequence |
|---|---|---|---|
| F1 | At a $1,000 State Value most levels cannot be traded. Constraint Delta = 1,000 x level% x multiplier x (1 - friction). Forex, ratio 3.5: L0 $1.368, L1 $0.903, L2 $0.589, L3 $0.390 ... L15 $0.003. One 0.01 lot of EURUSD moves $0.10 per pip, so L0 allows a lower boundary of at most 13.7 pips, L1 9.0, L2 5.9, L3 3.9. Gold (0.01 lot = $1 per $1 move) is untradeable at every level except a sub-$1.37 boundary at L0. | SEESARE 9.1 formula; standard contract sizes | After the first Negative Outcome (L0 -> L2) the real Exposure Unit falls below the broker minimum for any realistic boundary, and SEESARE 9.3 says "await constraint ascent", which needs resolutions that can no longer happen: a deadlock. The router adds Shadow Resolution (section 6.4). |
| F2 | The ~3.6% envelope holds only when Positive Outcomes pay about their Declared Ratio. With time-expiry exits, a pattern of (Negative, small Positive, small Positive) x 120 keeps the ladder at L0 and loses 16.2% over 360 events (wins worth 0.01R) or 11.1% (wins worth 0.3R). | Recomputed with the section 5 hierarchy, 7.1 rules, forex friction | Exits between the boundaries (time expiry, structural exhaustion) are MANUAL RESOLUTIONS, exactly as SEESARE 7.1 defines discretionary exits: no level change, negative counter kept. The same pattern then costs 0.25%. **Corrected 2026-11-01 (Phase 1): this was incomplete.** Losing time exits that never move the ladder lose 29.55% over 360 events (-0.6R each), and a stop at 3.5:1 followed by two 1:1 target hits loses 14.96%. No ladder classification holds the envelope alone; the pre-trade Envelope Guard in section 7.3 does. |
| F3 | The planned-risk arithmetic is right: 20 straight Negative Outcomes cost 0.221% and 100 cost 0.244% (forex friction included). But it bounds planned risk only; gaps fill beyond the Lower Boundary (this project's own 2026 data contains a -13.7R weekend gap). | Recomputed; research/results/champion | Envelope Guard on realized State Value; weekend and holiday flat rule; no "guarantee" wording (SEESARE part 1, priority 4, already says so). |
| F4 | The ladder caps the return. L0 risks 0.137% of the $1,000 per event; 250 events a year at +0.05R each is +1.7% a year, at +0.10R +3.4% a year, before any time spent below L0. The 3.6% envelope and a 60-120% target cannot both hold. | Arithmetic | The owner chooses which governs. This blueprint implements SEESARE as written. |
| F5 | The SEESARE HMAC chain (section 18) is keyed with the license key, so the public cannot verify it, and publishing the key would let anyone forge it. A VM snapshot restore does not change the hardware ID, so local rollback is not detected locally. | SEESARE 18.1-18.2 | Two chains: a keyless SHA-256 chain for public verification plus the SEESARE HMAC chain for license integrity. Chain heads are published as they happen (external anchor), and every record carries the broker's deal IDs, which the broker statement confirms independently. |
| F7 | SEESARE's multiplier formula and its own table disagree below 3.5:1. Formula 6.2 (ratio/3.5)^2.5 gives 0.680x at 3:1, 0.431x at 2.5:1, 0.247x at 2:1, 0.120x at 1.5:1; table 6.3 says 0.756x, 0.517x, 0.327x, 0.184x (it fits an exponent of about 2). Both agree at 1:1 (0.082x floor) and above 3.5:1. | Recomputed | CStructuralMultiplier implements the formula marked IMMUTABLE unless the owner says the table governs (decision 5). |
| F6 | SEESARE is defined as offline calculation software that never executes or transmits (sections 1.1, 38.1). An EA that executes trades for paying copy-followers and broadcasts results is a different regulatory category; section 48 itself says the terminology "does not alter the system's classification". | SEESARE 1.1, 38, 48 | Get the counsel opinion SEESARE 38.2 already budgets ($10-15k) before taking followers. The design keeps execution and the calculation engine in separate classes so the calculator can still ship alone. |

## 1. Program units

```
MQL5/Experts/SeesareRouter/SeesareRouter.mq5      Expert Advisor: one instance, trades every symbol it routes
MQL5/Services/SeesareRelay.mq5                    Service (#property service): drains the outbox, posts to Telegram
MQL5/Include/Seesare/
  Core/Clock.mqh          CClock, CDst              UTC, venue-local time, broker server offset
  Core/Calendar.mqh       CVenueCalendar             business days, holidays, month/quarter ends, 3rd Fridays, gotobi, FOMC/NFP tables
  Core/Agenda.mqh         CAgenda, CEventSlot        the day's slots and the one-event-per-day selector
  Flows/FlowModule.mqh    CFlowModule (abstract)     base class of every payer flow
  Flows/Flow*.mqh         24 + 1 module classes      one file per flow (section 9)
  Risk/Constraint.mqh     CConstraintEngine          16-level hierarchy, 7.1 ascent/descent, manual rule
  Risk/Multiplier.mqh     CStructuralMultiplier      SEESARE 6.2, immutable
  Risk/Exposure.mqh       CExposureCalculator        SEESARE 9.1 on the $1,000 virtual State Value -> broker volume, feasibility
  Exec/Gateway.mqh        CGateway                   CTrade wrapper: market order with the Lower Boundary attached, time exits
  Exec/EventBook.mqh      CEventBook, CEvent         event state machine, ticket <-> event map
  Ledger/Ledger.mqh       CEventLedger               append-only records, 360/36/10 counters, cycle audit, lifecycle lock
  Ledger/HashChain.mqh    CHashChain, CHmacSha256    keyless SHA-256 chain + SEESARE HMAC chain
  Ledger/Outbox.mqh       COutbox                    numbered message files for the relay
  Ops/Governor.mqh        CGovernor                  GREEN / AMBER / RED circuit breaker
  Ops/StateStore.mqh      CStateStore                atomic, checksummed persistence and restart recovery
tools/seesare_verify.py   public verifier: recomputes the chain from the posted records (Python, no secrets)
```

## 2. Class map

| Class | Owns | Key methods |
|---|---|---|
| CRouter (EA body) | all objects below | OnInit: load state, verify chain tail, reconcile positions, build agenda. OnTimer (1 s): Clock.Tick, Agenda.Due, EventBook.Step, Governor.Check. OnTradeTransaction: fills and closes into EventBook. OnDeinit: flush state. |
| CClock | server offset, DST rules | UtcNow(), ToUtc(venue, local), ToServer(utc), ServerOffsetAt(utc), Validate() |
| CVenueCalendar | embedded holiday and event tables per year | IsBusinessDay(venue, date), LastBusinessDays(venue, month, k), ThirdFriday(month), IsGotobi(date), FomcDays(year), NfpDays(year) |
| CAgenda | today's CEventSlot list | Build(utcDate), Due(utcNow), ConsumeDay(), FallbackNext() |
| CFlowModule | id, domain, symbols, status, magic, window | Slots(date), Direction(slot), DeclaredRatio(), BoundaryDistance(slot), SpreadCap(), IsExhausted(ctx), Status() |
| CConstraintEngine | level 0-15, consecutive negatives | ExposurePct(), OnPositive(), OnNegative(), OnManual() |
| CStructuralMultiplier | none | Value(ratio): r >= 3.5: min(1 + 0.10(r - 3.5), 1.50); r < 3.5: max((r/3.5)^2.5, 0.082) |
| CExposureCalculator | V = 1,000.00 (fixed virtual) | Plan(module, slot, level) -> CPlan {delta_usd, volume, lower, upper, verdict} |
| CGateway | CTrade | Open(plan), CloseByTime(event), VerifyStopAttached(ticket) |
| CEventBook | open and pending events | Arm, Submit, OnFill, Step, Resolve, Classify |
| CEventLedger | counters n (1-360), cycle (1-36), step (1-10) | Append(record), CycleAudit(), LockAt360() |
| CHashChain | public head, HMAC head | Link(record) -> {hash, hmac} |
| COutbox | sequence number | Push(kind, text) |
| CGovernor | state | Check(), Trip(reason), state GREEN/AMBER/RED |
| CStateStore | file `Common/Files/seesare/state.dat` | Save(), Load(), Checksum() |

## 3. Main loop

```
OnInit:   StateStore.Load -> verify checksum -> HashChain head == last ledger record?  else RED "integrity fault"
          Clock.Validate (live: TimeTradeServer - TimeGMT, rounded to 15 min; tester: input scheme)
          Gateway.Reconcile: every open position with a router magic -> its CEvent (comment = event id);
              planned exit already passed -> close now (MANUAL); position without a record -> close, RED, attest
          Agenda.Build(today UTC)
OnTimer (every 1 s):
          Clock.Tick (hourly offset re-check; alarm on an unexpected change)
          Governor.Check (spread, data staleness, connection, envelope, ledger writes)
          for slot in Agenda.Due(now): EventBook.Arm(slot)            T - 5 min preflight
          EventBook.Step(now): submit at entry time, exit at window end or exhaustion
          at 00:00 UTC: Agenda.Build(next day)
OnTradeTransaction: DEAL_ADD -> EventBook.OnFill / OnClose (deal reason SL, TP, EXPERT, SO)
```

The EA keys on the clock (OnTimer), not on ticks: flows are time events. Positions cannot carry an expiry in MQL5, so a time
exit needs the EA alive; while it is down, the broker-side Lower Boundary is the only protection, and recovery closes any
overdue position first.

## 4. Time synchronisation

Inside the EA every timestamp is UTC (seconds). Each module declares its window in its venue's local time; CClock converts
venue-local -> UTC for that date, and UTC -> server time only to read bars (CopyRates and iTime are in server time).

DST rules coded in CDst (no time-zone database exists in MQL5; these rules hold for every year in our data):

| Venue | Standard | Summer | Switch to summer | Switch back |
|---|---|---|---|---|
| London (WM/R fix, LBMA) | UTC+0 | UTC+1 | last Sunday of March 01:00 UTC | last Sunday of October 01:00 UTC |
| Frankfurt/CET (ECB fix) | UTC+1 | UTC+2 | same EU dates | same EU dates |
| New York (MOC, MOO, NFP, FOMC) | UTC-5 | UTC-4 | 2nd Sunday of March 07:00 UTC | 1st Sunday of November 06:00 UTC |
| Tokyo (Tokyo fix, TOCOM) | UTC+9 | none | none | none |

Window matrix (UTC):

| Flow | Venue time | UTC, winter | UTC, summer | Note |
|---|---|---|---|---|
| WM/R fix | 15:30-16:10 London | 15:30-16:10 | 14:30-15:10 | fix at 16:00 local |
| MOC imbalance | 15:50-16:05 New York | 20:50-21:05 | 19:50-20:05 | 3-4 weeks a year the London-NY gap is 4 h, not 5 |
| ECB reference rate | 14:05-14:20 CET | 13:05-13:20 | 12:05-12:20 | |
| MOO | 09:15-09:40 New York | 14:15-14:40 | 13:15-13:40 | |
| NFP | 08:30-10:00 New York | 13:30-15:00 | 12:30-14:00 | first Friday is not always the release day: table, not rule |
| FOMC | 14:00 New York | 19:00 | 18:00 | 8 scheduled dates a year: table |
| Tokyo fix (gotobi) | 09:55 Tokyo | 00:55 | 00:55 | Tier B in research: entry 23:00 UTC |
| TOCOM close | 15:15-15:45 Tokyo | 06:15-06:45 | 06:15-06:45 | |
| Crypto funding | 00:00, 08:00, 16:00 UTC | same | same | |

Broker server offset: live = round((TimeTradeServer() - TimeGMT()) / 900) x 900, re-checked hourly, and it must change
only on the broker's DST dates. In the Strategy Tester TimeGMT() returns server time, so the tester takes the offset from an
input scheme (GMT+0; GMT+2/+3 on EU dates; GMT+2/+3 on US dates). RoboForex's scheme is to be read from the account, not
assumed. The VPS clock must be NTP-synced: TimeGMT() derives from it.

## 5. Event lifecycle and the one-event-per-day rule

```
SCHEDULED -> ARMED (T-5 min: data fresh, spread <= module cap, Governor GREEN, direction from CLOSED bars only, plan feasible)
          -> SUBMITTED (market order, Lower Boundary attached in the same request; Upper Boundary attached if the module declares one)
          -> OPEN (fill confirmed; realized Constraint Delta <= plan x 1.10 or reduce/close)
          -> EXITING (window end | structural exhaustion | boundary touched)
          -> RESOLVED (all volume closed; delta from deal history incl. commission and swap)
          -> LEDGERED (record + both chain links) -> ATTESTED (relay acknowledged)
```

Classification (SEESARE 7.1 applied to automated exits; finding F2):

| Exit | Deal reason | Resolution | Ladder |
|---|---|---|---|
| Upper Boundary reached | DEAL_REASON_TP | POSITIVE | ascend 1 |
| Lower Boundary reached | DEAL_REASON_SL | NEGATIVE | descend 2 / 3 / 4+ |
| Window end or exhaustion | DEAL_REASON_EXPERT | MANUAL | no change, negative counter kept |
| Margin stop-out | DEAL_REASON_SO | NEGATIVE | descend + Governor RED |

One event per day: the day is the UTC date of the planned entry. Agenda.Build lists the day's eligible REAL slots in fixed
module priority (set from research evidence, highest t-statistic first). The first slot that passes ARMED takes the day; if it
is vetoed (spread, feasibility, Governor) the next REAL slot that day may take it. SHADOW slots never use the daily allowance.
A cycle is 10 resolved events, not 10 calendar days: days without an eligible slot produce no event.

## 6. The 360-event ledger

### 6.1 Counters

n = 1..360 resolved REAL events; cycle = (n - 1) div 10 + 1 (1..36); step = (n - 1) mod 10 + 1 (1..10). At n = 360 the
lifecycle locks (SEESARE 16; renewal = new genesis and license).

### 6.2 Record (canonical form: fixed field order, fixed decimals, UTC ISO-8601, `|`-separated)

Superseded by the Phase 1 format: field list `SEESARE_EVENT_KEYS` in `mt5/Seesare/Include/Seesare/Ledger/CycleLedger.mqh`, hash = SHA-256 of the line text that ends with `prev=<previous hash>`. The sketch below is the original design.

```
v=1|n=117|cycle=12|step=7|mode=REAL|module=WMR01|domain=forex|symbol=EURUSD|side=SELL|
utc_open=2027-03-03T15:30:00Z|utc_close=2027-03-03T16:01:00Z|level_before=2|level_after=2|neg_run=1|
ratio=3.50|mult=1.0000|friction=0.0500|delta_plan_usd=0.5890|volume=0.01|entry=1.08234|lower=1.08294|upper=1.08024|
exit=1.08190|resolution=MANUAL|delta_usd=0.4400|delta_pct_v=0.0440|deals=123456;123457|prev=<64 hex>
```

hash = SHA256(prev || record) (keyless, public). hmac = HMAC-SHA256(license_key, "SEESARE_P26|<binding_id>|<license>|n|resolution|
delta_usd|<prev hmac>") as SEESARE 18.1. MQL5 has SHA-256 (CryptEncode, CRYPT_HASH_SHA256) but no HMAC, so CHmacSha256 builds
it from SHA-256 per RFC 2104 (64-byte key block, ipad 0x36, opad 0x5c). MQL5 has no hardware-ID call without a DLL; the binding
ID = account login + server + an install UUID kept in the Common folder.

### 6.3 Cycle audit (at step 10)

Positive / negative / manual counts; positive-resolution frequency (SEESARE excludes manual); cycle net $ and % of the
$1,000; largest drawdown on the cycle's closed-event path; level at start and end; cycle root = SHA256 of the ten record
hashes; chain head. Then the Virtual Capital Variable restarts at $1,000.00 and a harvest instruction (cycle net, if
positive) is posted. The EA cannot withdraw money: the owner withdraws at the boundary.

### 6.4 Shadow Resolution (fixes the deadlock, finding F1)

When the plan is infeasible (volume below SYMBOL_VOLUME_MIN), the event runs on paper from live bid/ask with the same
rules and is recorded as mode=SHADOW in the chain. Owner's decision before coding: (a) SHADOW events move the ladder but
never count toward n or the money (recommended: it keeps the ladder alive at $1,000), (b) raise the State Value, or (c)
use a cent account. Without one of these, the engine stops trading after its first Negative Outcome.

## 7. Pre-trade exposure pipeline ($1,000 virtual baseline)

```
1  h      = HIERARCHY[level] / 100                     0.144% ... 0.0003%  (SEESARE 5, immutable)
2  base   = 1000.00 x h                                never AccountInfoDouble(ACCOUNT_BALANCE): insulated from withdrawals
3  m      = Multiplier.Value(module ratio)             0.082 ... 1.50       (SEESARE 6.2)
4  D      = base x m x (1 - friction[domain])          forex .05, crypto .08, stocks .03, indices .025, commodities .04 (8.2)
5  lower  = entry_ref -/+ s;  upper = entry_ref +/- s x ratio      s = the module's boundary distance
6  loss1  = -OrderCalcProfit(type, symbol, 1.0, entry_ref, lower) + commission per lot round turn (input, measured)
7  volume = floor((D / loss1) / VOLUME_STEP) x VOLUME_STEP
8  verdict: volume < VOLUME_MIN -> INFEASIBLE (never round up: rounding up breaks the envelope) -> SHADOW per 6.4
            margin (OrderCalcMargin) > 50% of free margin -> INFEASIBLE_MARGIN
            spread at T-1 min > module cap -> VETO_SPREAD
9  after the fill: realized D with the actual entry <= D x 1.10, else reduce or close
```

### 7.1 Feasibility at $1,000 (forex friction, ratio 3.5, 0.01 lot minimum, before commission)

| Level | Constraint Delta | EURUSD max boundary | USDJPY max boundary (at 150) | Gold max boundary |
|---|---:|---:|---:|---:|
| L0 | $1.368 | 13.7 pips | 20.5 pips | $1.37 |
| L1 | $0.903 | 9.0 pips | 13.5 pips | $0.90 |
| L2 | $0.589 | 5.9 pips | 8.8 pips | $0.59 |
| L3 | $0.390 | 3.9 pips | 5.8 pips | $0.39 |
| L4-L15 | $0.257 ... $0.003 | under 2.6 pips | under 3.9 pips | under $0.26 |

### 7.2 Declared Ratio per module

With time exits the Upper Boundary is rarely reached, so a declared 10:1 would raise exposure 1.5x without changing the payoff.
The ratio for each module is therefore fixed in the registry from its measured research payoff, not chosen per event.

### 7.3 Envelope Guard (pre-trade; implemented in Phase 1, findings F2 and F3)

A REAL event may open only if the lifecycle's current peak-to-trough drawdown of real P&L + the event's all-in risk (loss at the
stop for the rounded-down volume, commission, swap and slippage allowances) <= 3.6% of $1,000 = $36
(`CSeesareCycleLedger::AllowsRealRisk`); otherwise the event runs as SHADOW. The ledger re-checks the rule when it records the
event and the public verifier checks it too. This bounds planned losses under any sequence of outcomes, whatever the ladder
does; a gap through the stop can still exceed it (no positions over weekends or exchange holidays). Recomputed over 360 events:
time exits = MANUAL with every exit at -0.6R: 29.55% without the guard, 3.53% with it (real trading stops after 43 events);
losing time exits = NEGATIVE: 0.19% with all 360 real. Once the room is smaller than one event's risk, real trading stops for
the lifecycle; starting a new lifecycle is the owner's decision.

## 8. Attestation stream

```
EventLedger.Append -> HashChain.Link -> COutbox.Push  (Phase 1: Common/Files/seesare/<login>/<lifecycle>/outbox/<seq>.msg, written to .tmp then FileMove)
SeesareRelay (service, separate program): every 2 s take the lowest <seq> ->
   WebRequest("POST", "https://api.telegram.org/bot<token>/sendMessage", chat_id, text <= 4,096 chars, plain text)
   200 + ok:true -> move to sent/ with Telegram message_id;  429 -> wait retry_after;  network error -> backoff 5 s ... 10 min
```

WebRequest blocks until it returns, so it lives in the service, never in the EA. The URL must be allowed in Tools > Options >
Expert Advisors. The bot token sits only in the service inputs. Messages: one per event (summary + canonical record + hash),
one per cycle audit, one at lifecycle end, heartbeats every 6 h, RED alerts immediately (also SendNotification to the phone).
Telegram posts can be deleted by the channel admin, so each cycle root is also published to a second public place (for
example a commit in a public repository), and anyone can match the deal IDs against the broker statement.
`tools/seesare_verify.py` recomputes the public chain from the posted records; the MQL5 hash code must reproduce its test vectors.

## 9. Module registry (24 directive rows + the Tokyo fix)

Status gates real money. REAL needs a Truth Lab survivor plus a forward test; SHADOW runs on paper and builds live evidence;
DISABLED compiles but never arms. Initial status from research memory (OPEN_QUESTIONS Q19):

| Status | Modules |
|---|---|
| REAL-eligible after its forward test | Tokyo fix on gotobi days (research Tier B) |
| Lab test next, then SHADOW | 1 WM/R fix (month-end, direction from US vs rest equity returns); 2 MOC / last 30 minutes (US500, NAS100); 3 month-end and 12 quarter-end rebalancing, conditional on the month's equity move |
| Lab later | 6 ECB fix; 11 Treasury settlement; 14 triple witching; 15 Monday gap; 18 FOMC; 21 commodity option expiry; 22 NFP |
| DISABLED: not a directional payer flow | 5 TOCOM close (FX); 7 MOO without imbalance data; 9 VIX roll; 16 London/NY overlap; 17 ETF NAV arbitrage; 20 "margin liquidation hour" |
| DISABLED: no data or too rare | 4 option gamma (no open interest); 8 crypto funding (no crypto prices yet); 13 Golden Week; 19 dividend repatriation; 23 Lunar New Year; 24 intervention |
| Covered by the book | 10 CTA trend breaks (trend legs) |

## 10. Governor (circuit breaker, not a sizing tool)

GREEN: trade. AMBER: no new REAL events (spread above cap, data older than 2 min, clock offset changed unexpectedly, Envelope
Guard 3.0%). RED: close all, halt, attest (stop-out, a missing Lower Boundary after a fill, ledger or chain write failure,
integrity fault on start, Envelope Guard 3.6%). Sizing belongs to the SEESARE ladder only; research found sizing states add
nothing (P8).

## 11. Persistence and recovery

State (level, negative run, n, cycle, step, chain heads, day-consumed flag, open-event map) is saved after every transition:
write state.tmp, then FileMove with FILE_REWRITE (atomic), with a SHA-256 checksum and a schema version. On start: checksum,
chain head = last ledger record, position reconciliation by magic number (section 3).

## 12. Research side: the cycle lab (directive Part V, corrected)

A Python twin of the router replays 2011-2025 M1 with the same rules (one event a day, $1,000 virtual State Value, the
hierarchy, the feasibility rule, the classification in section 5), cuts the stream into 10-event cycles, and reports the
best and worst cycle, envelope breaches, and the distribution of 360-event results (cycle bootstrap). Parameters are fixed
before the run or walk-forward (fit on cycles before k, score cycle k). Optimising inside each 10-event block, as Part V
asks, fits every past cycle to itself and says nothing about the next one; it is not used. 2023-25 keeps one logged look
per module.

## 13. Decisions for the owner before code

Owner's answers (2026-11-01): SHADOW drives the ladder (Shadow-Lot Engine; Phase 1 writes shadow events to disk, not RAM only, so
a restart cannot lose the ladder); time exits are MANUAL resolutions (kept as the default; a losing-time-exit-NEGATIVE option
exists and is recommended, section 7.3); exponent 2.0; keyless SHA-256 chain; dual-service outbox; the hierarchy may be tuned
only if the envelope cannot breach 3.6% under any sequence (the pre-trade guard gives this for any hierarchy; a tuned ladder is
declared in the genesis line and cannot change inside a lifecycle). Still open: 2 and 3 below, and 4 before followers.

1. Infeasible levels: SHADOW drives the ladder (recommended), a larger State Value, or a cent account (section 6.4).
2. Which governs if they conflict: the 3.6% envelope (returns of a few % a year) or the 60-120% target (finding F4).
3. RoboForex: measure its spreads at the flow times, commission and server time scheme before sizing anything
   (`mt5/NorthStarExport.mq5` exports them); all cost figures in research are Exness.
4. Legal opinion before followers (finding F6).
5. Multiplier below 3.5:1: the formula (^2.5) or the reference table (about ^2) (finding F7).

## 14. Build order

Phase 1 delivered (uncompiled source, 2026-11-01): clock, DST rules, timing matrix, spread gate, cycle ledger with keyless chain,
anchors, envelope guard, state snapshot and outbox writer, plus the self-test script (`mt5/Seesare/`). Next: compile and run the
self-test on the RoboForex terminal; then CVenueCalendar, the exposure calculator (volume from `PlanUsdAt`), the gateway, the
Tokyo fix module in SHADOW, and the relay service.

1. CClock, CDst, CVenueCalendar with test vectors (time is the most common source of bugs here); 2. CHashChain + CHmacSha256
matching tools/seesare_verify.py vectors; 3. CConstraintEngine + CStructuralMultiplier + CExposureCalculator with the tables
above as unit tests; 4. router + Tokyo fix module in SHADOW on a RoboForex demo; 5. SeesareRelay; 6. lab twin and the next
modules one at a time, each through the Truth Lab before it may leave SHADOW.

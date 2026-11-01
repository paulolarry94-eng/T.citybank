//+------------------------------------------------------------------+
//|                                  Seesare/Ledger/CycleLedger.mqh  |
//| SEESARE P26 router, Phase 1: the 360-event Cycle Ledger.         |
//| UNCOMPILED SOURCE. Python twin and public verifier:              |
//| tools/seesare_verify.py (class Ledger: same rules, same lines).  |
//|                                                                  |
//| What it does                                                     |
//| - Records every resolved event, REAL or SHADOW, as one canonical |
//|   line in <root>\<life>\ledger.txt, chained by keyless SHA-256:  |
//|   each line carries the hash of the line before (prev=) and its  |
//|   own hash (hash=). Deal tickets go into the hashed text.        |
//| - Sizes every event with the DRAWDOWN-KEYED LADDER (format 2,    |
//|   owner's decision 2026-11-01; the SEESARE win/loss ladder is    |
//|   retired): 16 levels, one per $2.25 band (0.225%) of lifecycle  |
//|   drawdown; planned risk = 0.30 x weight x room left below the   |
//|   band (3.6% - (level+1) x 0.225%); a REAL event may not risk    |
//|   more than its plan. With weight <= 1.00, drawdown + plan stays |
//|   below $36 at every level, so the ladder holds the envelope by  |
//|   construction; at L15 nothing fits and the lifecycle is         |
//|   stopped. Evidence: research/seesare/universe_lifecycle_study.py|
//|   (11-leg book, 13 of 13 lifecycles completed 2011-22).          |
//| - Labels each outcome from how the event closed (stop or broker  |
//|   NEGATIVE, target POSITIVE, by hand MANUAL, time exit POSITIVE  |
//|   on a net gain, NEGATIVE on a net loss, MANUAL at 0); labels    |
//|   feed the counts and messages, not the size.                    |
//|   The caller cannot write a level or a plan that breaks these    |
//|   rules.                                                         |
//| - Counts 10 REAL events per cycle, 36 cycles per lifecycle, and  |
//|   locks at 360. SHADOW events are paper: they carry no money,    |
//|   never move the level and do not count.                         |
//| - At each 10th REAL event writes the cycle audit (counts, net,   |
//|   drawdown, levels, the root hash of the 10 events, the chain    |
//|   head) to anchors.txt, chained to the previous audit.           |
//| - Envelope guard: AllowsRealRisk(risk) is true only if the       |
//|   lifecycle's current drawdown + this event's all-in risk stays  |
//|   within 3.6% of $1,000 ($36). Ask it before every REAL entry.   |
//|   The ledger re-checks the rule when the event is recorded.      |
//| - Survives restarts: on Open it replays ledger.txt through the   |
//|   same code that recorded it, checks state.dat and anchors.txt   |
//|   against it, and re-sends any outbox message not yet written.  |
//|                                                                  |
//| One code path: ApplyLine() updates the state both when an event  |
//| is recorded and when the file is replayed, so a restart cannot   |
//| rebuild a different state from what was written.                 |
//+------------------------------------------------------------------+
#ifndef SEESARE_LEDGER_CYCLELEDGER_MQH
#define SEESARE_LEDGER_CYCLELEDGER_MQH

#include <Seesare\Core\Text.mqh>
#include <Seesare\Core\Clock.mqh>
#include <Seesare\Ledger\Sha256.mqh>
#include <Seesare\Ledger\StateStore.mqh>
#include <Seesare\Ledger\Outbox.mqh>

#define SEESARE_FORMAT            "2"              // 2 = drawdown-keyed ladder; 1 was the retired win/loss ladder
#define SEESARE_BASELINE_USD      1000.0
#define SEESARE_CYCLE_EVENTS      10
#define SEESARE_LIFECYCLE_EVENTS  360
#define SEESARE_ENVELOPE_PCT      3.6
#define SEESARE_LEVELS            16
#define SEESARE_SIZING_NAME       "DRAWDOWN_KEYED"
#define SEESARE_BAND_USD          2.25             // 3.6% of $1,000 / 16 levels
#define SEESARE_BAND_UNITS        22500            // the band in ten-thousandths of a dollar
#define SEESARE_ROOM_MULT         0.30             // share of the room left one event may risk at weight 1.00 (chosen on 2011-22)
#define SEESARE_MAX_WEIGHT        1.0              // the largest weight any tested leg has
#define SEESARE_GENESIS_KEYS      "v,life,k,genesis,baseline,events,cycle_size,envelope_pct,sizing,levels,band,room_mult,max_weight,time_policy,created"
#define SEESARE_EVENT_KEYS        "v,life,k,mode,n,cycle,step,module,domain,symbol,side,open,close,by,res,dd,lvl_before,lvl_after,weight,plan,risk,vol,entry,lower,upper,exit,delta,deals,prev"
#define SEESARE_AUDIT_KEYS        "v,life,audit,cycle,events,pos,neg,man,shadow,pos_rate,net,net_pct,max_dd,max_dd_pct,life_net,life_dd,lvl_start,lvl_end,root,head,prev"

enum ENUM_SEESARE_MODE
  {
   SEESARE_REAL   = 0,   // REAL: money at the broker
   SEESARE_SHADOW = 1    // SHADOW: paper event that moves the ladder (Shadow-Lot Engine)
  };

enum ENUM_SEESARE_RES
  {
   SEESARE_NEGATIVE = -1,
   SEESARE_MANUAL   = 0,
   SEESARE_POSITIVE = 1
  };

enum ENUM_SEESARE_CLOSE
  {
   SEESARE_BY_STOP   = 0,   // lower boundary (stop) reached
   SEESARE_BY_TARGET = 1,   // upper boundary (target) reached
   SEESARE_BY_TIME   = 2,   // window end or exhaustion: closed by the router
   SEESARE_BY_HUMAN  = 3,   // closed by hand
   SEESARE_BY_BROKER = 4    // margin stop-out
  };

enum ENUM_SEESARE_TIME_POLICY
  {
   SEESARE_TIME_EXIT_MANUAL   = 0,   // Phase 1 mandate: every time exit is a manual resolution (research only)
   SEESARE_TIME_LOSS_NEGATIVE = 1,   // Phase 2: a losing time exit is negative, any other time exit manual
   SEESARE_TIME_GAIN_POSITIVE = 2    // Phase 4: a time exit with a net gain is positive (climbs), with a net loss negative,
                                     // exactly 0.0000 manual
  };

//--- Owner decisions, 2026-11-01: Phase 2 "losing time exits count as negative"; Phase 4 "time-exit ascension": a time or
//--- exhaustion exit with a net gain counts as a positive outcome and climbs one level. Hardcoded: the ledger derives every
//--- resolution from the exit kind and the recorded net result (4 decimals, after commission and swap) with this rule,
//--- declares it in the genesis line, and refuses a lifecycle (or a line) that follows another rule. Lifecycles written
//--- under an earlier rule stay verifiable with tools/seesare_verify.py; this build does not continue them.
//--- Since format 2 the label no longer sizes anything (the drawdown-keyed ladder does); it is published in every line and
//--- counted in the cycle audits.
#define SEESARE_TIME_POLICY       SEESARE_TIME_GAIN_POSITIVE
#define SEESARE_TIME_POLICY_NAME  "GAIN_POSITIVE_LOSS_NEGATIVE"

//+------------------------------------------------------------------+
//| One resolved event, as the router hands it to the ledger.        |
//| The ledger adds k, n, cycle, step, the resolution (from close_by |
//| and delta_usd under SEESARE_TIME_POLICY), the drawdown, the      |
//| drawdown levels, the planned risk and the hashes.                |
//+------------------------------------------------------------------+
struct SSeesareEvent
  {
   ENUM_SEESARE_MODE  mode;
   string             module;       // flow module id (token)
   string             domain;       // forex, crypto, stocks, indices or commodities
   string             symbol;
   int                side;         // +1 buy, -1 sell
   int                digits;       // price decimals (SYMBOL_DIGITS)
   datetime           utc_open;
   datetime           utc_close;
   ENUM_SEESARE_CLOSE close_by;
   double             weight;       // the module's weight, (0, 1.00], recorded with 2 decimals; plan = 0.30 x weight x room
   double             risk_usd;     // REAL: all-in loss at the stop for the actual volume; may not exceed the plan
   double             volume;       // REAL: lots traded; SHADOW: the unrounded virtual lots
   double             entry;
   double             lower;        // lower boundary (BUY stop, SELL target)
   double             upper;        // upper boundary (BUY target, SELL stop)
   double             exit_price;
   double             delta_usd;    // REAL: net of all deals (profit + commission + swap + fee); SHADOW: paper result
   string             deals;        // REAL: deal tickets "123;124"; SHADOW: ignored ("-")
   void               Clear(void)
     {
      mode = SEESARE_REAL;
      module = "";
      domain = "";
      symbol = "";
      side = 0;
      digits = 0;
      utc_open = 0;
      utc_close = 0;
      close_by = SEESARE_BY_TIME;
      weight = 0.0;
      risk_usd = 0.0;
      volume = 0.0;
      entry = 0.0;
      lower = 0.0;
      upper = 0.0;
      exit_price = 0.0;
      delta_usd = 0.0;
      deals = "";
     }
  };

//+------------------------------------------------------------------+
//| Ladder arithmetic (static). Sizing must use these same functions,|
//| through CSeesareCycleLedger::PlanUsdAt(). Twin: level_from_dd,   |
//| room_usd, plan_usd, plan_text in tools/seesare_verify.py.        |
//+------------------------------------------------------------------+
class CSeesareLadder
  {
public:
   //--- whole $2.25 bands of lifecycle drawdown, 0..15; computed in whole ten-thousandths (the drawdown is a sum of
   //--- 4-decimal amounts), so no band edge depends on floating-point noise
   static int        LevelFromDrawdown(const double dd_usd)
     {
      long u = (long)MathRound(dd_usd * 10000.0);
      if(u < 0)
         u = 0;
      long lv = u / SEESARE_BAND_UNITS;
      if(lv > SEESARE_LEVELS - 1)
         lv = SEESARE_LEVELS - 1;
      return (int)lv;
     }
   //--- room left below the bottom of the level's band: $36 - (level + 1) x $2.25; 0 at L15
   static double     RoomUsd(const int level)
     {
      if(level < 0 || level > SEESARE_LEVELS - 1)
         return 0.0;
      return SEESARE_BAND_USD * (double)(SEESARE_LEVELS - 1 - level);
     }
   //--- planned risk of one event, unrounded (the ledger writes it rounded down to 4 decimals)
   static double     PlanUsd(const int level, const double weight)
     {
      return SEESARE_ROOM_MULT * weight * RoomUsd(level);
     }
   //--- the plan exactly as a ledger line carries it; the weight is taken as written (2 decimals)
   static string     PlanText(const int level, const double weight)
     {
      double w = StringToDouble(CSeesareText::Fmt(weight, 2));
      return CSeesareText::Fmt(CSeesareText::FloorDp(PlanUsd(level, w), 4), 4);
     }
   static bool       ValidWeight(const double weight)
     {
      double w = StringToDouble(CSeesareText::Fmt(weight, 2));
      return (w > 0.0 && w <= SEESARE_MAX_WEIGHT + 1e-12);
     }
   static bool       ValidDomain(const string domain)
     {
      return (domain == "forex" || domain == "crypto" || domain == "stocks" || domain == "indices" || domain == "commodities");
     }
   //--- resolution of an automated exit (twin: classify)
   static ENUM_SEESARE_RES Classify(const ENUM_SEESARE_CLOSE by, const double delta_usd, const ENUM_SEESARE_TIME_POLICY policy)
     {
      if(by == SEESARE_BY_STOP || by == SEESARE_BY_BROKER)
         return SEESARE_NEGATIVE;
      if(by == SEESARE_BY_TARGET)
         return SEESARE_POSITIVE;
      if(by == SEESARE_BY_TIME)
        {
         if(policy != SEESARE_TIME_EXIT_MANUAL && delta_usd < 0.0)
            return SEESARE_NEGATIVE;
         if(policy == SEESARE_TIME_GAIN_POSITIVE && delta_usd > 0.0)
            return SEESARE_POSITIVE;
        }
      return SEESARE_MANUAL;
     }
   static string     CloseName(const ENUM_SEESARE_CLOSE by)
     {
      if(by == SEESARE_BY_STOP)
         return "STOP";
      if(by == SEESARE_BY_TARGET)
         return "TARGET";
      if(by == SEESARE_BY_TIME)
         return "TIME";
      if(by == SEESARE_BY_HUMAN)
         return "HUMAN";
      if(by == SEESARE_BY_BROKER)
         return "BROKER";
      return "";
     }
   static int        CloseFromName(const string s)
     {
      if(s == "STOP")
         return 0;
      if(s == "TARGET")
         return 1;
      if(s == "TIME")
         return 2;
      if(s == "HUMAN")
         return 3;
      if(s == "BROKER")
         return 4;
      return -1;
     }
   static string     ResName(const ENUM_SEESARE_RES r)
     {
      if(r == SEESARE_POSITIVE)
         return "POSITIVE";
      if(r == SEESARE_NEGATIVE)
         return "NEGATIVE";
      if(r == SEESARE_MANUAL)
         return "MANUAL";
      return "";
     }
   //--- 1, -1, 0; -9 if unknown
   static int        ResFromName(const string s)
     {
      if(s == "POSITIVE")
         return 1;
      if(s == "NEGATIVE")
         return -1;
      if(s == "MANUAL")
         return 0;
      return -9;
     }
  };

//+------------------------------------------------------------------+
//| The ledger                                                       |
//+------------------------------------------------------------------+
class CSeesareCycleLedger
  {
private:
   string            m_root;
   string            m_life;
   string            m_dir;
   string            m_ledger_path;
   string            m_anchor_path;
   string            m_state_path;
   bool              m_open;
   bool              m_fault;
   string            m_error;
   string            m_warning;
   //--- rebuilt from ledger.txt by ApplyLine (recording goes through the same function)
   string            m_lines[];
   string            m_hashes[];
   datetime          m_line_utc[];
   string            m_genesis;
   string            m_head;
   int               m_k;                // chain index of the last line (genesis = 0)
   int               m_n;                // REAL events
   int               m_shadow;           // SHADOW events
   int               m_level;            // drawdown level (0..15) after the last REAL event
   int               m_cycle;            // the open cycle (1..36; 37 after the lock)
   bool              m_locked;
   datetime          m_created;
   datetime          m_last_open;
   datetime          m_last_close;
   datetime          m_last_real_open;
   string            m_cycle_hashes[];   // REAL hashes of the open cycle
   int               m_c_pos;
   int               m_c_neg;
   int               m_c_man;
   int               m_c_shadow;
   int               m_c_level_start;
   double            m_c_net;            // cycle P&L: the Virtual Capital Variable is 1000 + m_c_net
   double            m_c_peak;
   double            m_c_dd;
   int               m_t_pos;
   int               m_t_neg;
   int               m_t_man;
   double            m_l_net;            // lifecycle real P&L
   double            m_l_peak;
   double            m_l_dd;
   int               m_violations;
   int               m_first_violation_k;
   string            m_anchors[];
   int               m_anchor_k[];
   datetime          m_anchor_utc[];
   int               m_anchors_on_disk;
   //--- delivery progress, kept in state.dat
   int               m_out_next;         // next chain index to push to the outbox
   int               m_out_audits;       // cycle audits pushed
   bool              m_out_life;         // lifecycle summary pushed
   long              m_loaded_seq;
   CSeesareOutbox    m_outbox;

   bool              Fail(const string why);
   void              ResetState(void);
   void              Remember(const string line, const string hash, const datetime utc);
   bool              ApplyLine(const string line, const bool dry, string &why);
   bool              ApplyGenesis(CSeesareKV &kv, const string hash, const string line, const bool dry, string &why);
   bool              ApplyEvent(CSeesareKV &kv, const string hash, const string line, const bool dry, string &why);
   void              CloseCycle(const datetime at);
   string            GenesisContent(const datetime created) const;
   bool              BuildEventLine(const SSeesareEvent &e, string &line, string &why) const;
   bool              CheckState(const bool adopt);
   bool              VerifyAnchorsFile(void);
   bool              WriteMissingAnchors(void);
   bool              Heal(void);
   bool              SaveState(void);
   string            LifecycleSummary(void) const;

public:
                     CSeesareCycleLedger(void);
   bool              Open(const string root, const string life, const datetime created_utc, const bool adopt_ledger = false);
   bool              Record(const SSeesareEvent &e, string &hash_out);
   bool              Retry(void);
   bool              AllowsRealRisk(const double risk_usd) const;
   double            PlanUsdAt(const double weight) const;
   //--- state
   bool              IsOpen(void) const              { return m_open; }
   bool              Fault(void) const               { return m_fault; }
   string            LastError(void) const           { return m_error; }
   string            LastWarning(void) const         { return m_warning; }
   string            Life(void) const                { return m_life; }
   string            Dir(void) const                 { return m_dir; }
   int               Level(void) const               { return m_level; }
   //--- drawdown in the last band: no REAL event can be recorded any more (a new lifecycle id is the owner's decision)
   bool              Stopped(void) const             { return (m_open && m_level >= SEESARE_LEVELS - 1); }
   int               ChainIndex(void) const          { return m_k; }
   int               RealCount(void) const           { return m_n; }
   int               ShadowCount(void) const         { return m_shadow; }
   int               Cycle(void) const               { return m_cycle; }
   int               StepsDoneInCycle(void) const    { return m_n % SEESARE_CYCLE_EVENTS; }
   int               CyclesClosed(void) const        { return ArraySize(m_anchors); }
   bool              Locked(void) const              { return m_locked; }
   string            Head(void) const                { return m_head; }
   string            GenesisHash(void) const         { return m_genesis; }
   string            LineAt(const int k) const       { return ((k >= 0 && k < ArraySize(m_lines)) ? m_lines[k] : ""); }
   string            AnchorLine(const int i) const   { return ((i >= 0 && i < ArraySize(m_anchors)) ? m_anchors[i] : ""); }
   double            CycleNetUSD(void) const         { return m_c_net; }
   double            VirtualStateValue(void) const   { return SEESARE_BASELINE_USD + m_c_net; }
   double            LifeNetUSD(void) const          { return m_l_net; }
   double            LifeDrawdownUSD(void) const     { return m_l_peak - m_l_net; }
   double            LifeMaxDrawdownUSD(void) const  { return m_l_dd; }
   double            EnvelopeCapUSD(void) const      { return SEESARE_BASELINE_USD * SEESARE_ENVELOPE_PCT / 100.0; }
   double            EnvelopeRoomUSD(void) const     { return EnvelopeCapUSD() - LifeDrawdownUSD(); }
   int               EnvelopeViolations(void) const  { return m_violations; }
   datetime          LastEventOpenUtc(void) const    { return m_last_open; }
   datetime          LastRealOpenUtc(void) const     { return m_last_real_open; }
   datetime          LastCloseUtc(void) const        { return m_last_close; }
   long              OutboxSeq(void) const           { return m_outbox.LastSeq(); }
  };

CSeesareCycleLedger::CSeesareCycleLedger(void)
  {
   m_root = "";
   m_life = "";
   m_dir = "";
   m_ledger_path = "";
   m_anchor_path = "";
   m_state_path = "";
   m_open = false;
   m_fault = false;
   m_error = "";
   m_warning = "";
   ResetState();
  }

void CSeesareCycleLedger::ResetState(void)
  {
   ArrayResize(m_lines, 0);
   ArrayResize(m_hashes, 0);
   ArrayResize(m_line_utc, 0);
   ArrayResize(m_cycle_hashes, 0);
   ArrayResize(m_anchors, 0);
   ArrayResize(m_anchor_k, 0);
   ArrayResize(m_anchor_utc, 0);
   m_genesis = "";
   m_head = "";
   m_k = -1;
   m_n = 0;
   m_shadow = 0;
   m_level = 0;
   m_cycle = 1;
   m_locked = false;
   m_created = 0;
   m_last_open = 0;
   m_last_close = 0;
   m_last_real_open = 0;
   m_c_pos = 0;
   m_c_neg = 0;
   m_c_man = 0;
   m_c_shadow = 0;
   m_c_level_start = 0;
   m_c_net = 0.0;
   m_c_peak = 0.0;
   m_c_dd = 0.0;
   m_t_pos = 0;
   m_t_neg = 0;
   m_t_man = 0;
   m_l_net = 0.0;
   m_l_peak = 0.0;
   m_l_dd = 0.0;
   m_violations = 0;
   m_first_violation_k = -1;
   m_anchors_on_disk = 0;
   m_out_next = 0;
   m_out_audits = 0;
   m_out_life = false;
   m_loaded_seq = 0;
  }

bool CSeesareCycleLedger::Fail(const string why)
  {
   m_fault = true;
   m_error = why;
   Print("SEESARE ledger FAULT [", m_life, "]: ", why);
   return false;
  }

void CSeesareCycleLedger::Remember(const string line, const string hash, const datetime utc)
  {
   int n = ArraySize(m_lines);
   ArrayResize(m_lines, n + 1, 512);
   ArrayResize(m_hashes, n + 1, 512);
   ArrayResize(m_line_utc, n + 1, 512);
   m_lines[n] = line;
   m_hashes[n] = hash;
   m_line_utc[n] = utc;
  }

//+------------------------------------------------------------------+
//| The single code path: validates a line against the current state |
//| and, unless dry, applies it.                                     |
//+------------------------------------------------------------------+
bool CSeesareCycleLedger::ApplyLine(const string line, const bool dry, string &why)
  {
   why = "";
   int len = StringLen(line);
   if(len < 71 || StringSubstr(line, len - 70, 6) != "|hash=")
     {
      why = "malformed line (no hash)";
      return false;
     }
   string content = StringSubstr(line, 0, len - 70);
   string hash = StringSubstr(line, len - 64);
   if(!CSeesareText::IsHex64(hash))
     {
      why = "malformed hash";
      return false;
     }
   string calc = CSeesareSha256::Hex(content);
   if(calc == "")
     {
      why = "SHA-256 is not available in this terminal";
      return false;
     }
   if(calc != hash)
     {
      why = "hash mismatch: the line was changed";
      return false;
     }
   CSeesareKV kv;
   if(!kv.ParsePipes(content))
     {
      why = "malformed fields";
      return false;
     }
   if(kv.Get("v") != SEESARE_FORMAT)
     {
      why = "unknown format version";
      return false;
     }
   if(kv.Get("life") != m_life)
     {
      why = "the line belongs to lifecycle " + kv.Get("life");
      return false;
     }
   if(kv.Has("genesis"))
      return ApplyGenesis(kv, hash, line, dry, why);
   return ApplyEvent(kv, hash, line, dry, why);
  }

bool CSeesareCycleLedger::ApplyGenesis(CSeesareKV &kv, const string hash, const string line, const bool dry, string &why)
  {
   if(m_k >= 0)
     {
      why = "a second genesis line";
      return false;
     }
   if(!kv.KeysAre(SEESARE_GENESIS_KEYS) || kv.Get("k") != "0" || kv.Get("genesis") != "")
     {
      why = "genesis fields out of order";
      return false;
     }
   if(kv.Get("baseline") != CSeesareText::Fmt(SEESARE_BASELINE_USD, 2) ||
      kv.Get("events") != IntegerToString(SEESARE_LIFECYCLE_EVENTS) ||
      kv.Get("cycle_size") != IntegerToString(SEESARE_CYCLE_EVENTS) ||
      kv.Get("envelope_pct") != CSeesareText::Fmt(SEESARE_ENVELOPE_PCT, 2) ||
      kv.Get("sizing") != SEESARE_SIZING_NAME ||
      kv.Get("levels") != IntegerToString(SEESARE_LEVELS) ||
      kv.Get("band") != CSeesareText::Fmt(SEESARE_BAND_USD, 4) ||
      kv.Get("room_mult") != CSeesareText::Fmt(SEESARE_ROOM_MULT, 2) ||
      kv.Get("max_weight") != CSeesareText::Fmt(SEESARE_MAX_WEIGHT, 2))
     {
      why = "genesis constants differ from this build (format 2: drawdown-keyed ladder)";
      return false;
     }
   if(kv.Get("time_policy") != SEESARE_TIME_POLICY_NAME)
     {
      why = "this build records only lifecycles with time_policy=";
      why += SEESARE_TIME_POLICY_NAME;
      why += " (gain climbs, loss descends); start a new lifecycle id";
      return false;
     }
   datetime created = 0;
   if(!CSeesareDst::IsoToTime(kv.Get("created"), created))
     {
      why = "bad genesis time";
      return false;
     }
   if(dry)
      return true;
   m_created = created;
   m_genesis = hash;
   m_head = hash;
   m_k = 0;
   m_last_close = created;
   Remember(line, hash, created);
   return true;
  }

bool CSeesareCycleLedger::ApplyEvent(CSeesareKV &kv, const string hash, const string line, const bool dry, string &why)
  {
   if(m_k < 0)
     {
      why = "event before the genesis line";
      return false;
     }
   if(m_locked)
     {
      why = "event after the lifecycle lock (360 real events)";
      return false;
     }
   int k = m_k + 1;
   string at = " at k=" + IntegerToString(k);
   if(!kv.KeysAre(SEESARE_EVENT_KEYS))
     {
      why = "event fields missing or out of order" + at;
      return false;
     }
   if(kv.Get("k") != IntegerToString(k))
     {
      why = "chain index gap" + at;
      return false;
     }
   if(kv.Get("prev") != m_head)
     {
      why = "broken link: prev is not the hash of the line before" + at;
      return false;
     }
   string mode = kv.Get("mode");
   bool real = (mode == "REAL");
   if(!real && mode != "SHADOW")
     {
      why = "bad mode" + at;
      return false;
     }
   if(kv.Get("cycle") != IntegerToString(m_cycle))
     {
      why = "cycle number wrong" + at;
      return false;
     }
   if(real && (kv.Get("n") != IntegerToString(m_n + 1) || kv.Get("step") != IntegerToString(m_n % SEESARE_CYCLE_EVENTS + 1)))
     {
      why = "real-event numbering broken" + at;
      return false;
     }
   if(!real && (kv.Get("n") != IntegerToString(m_n) || kv.Get("step") != "-"))
     {
      why = "shadow-event numbering broken" + at;
      return false;
     }
   if(!CSeesareText::IsToken(kv.Get("module"), 32) || !CSeesareText::IsToken(kv.Get("symbol"), 32))
     {
      why = "bad module or symbol" + at;
      return false;
     }
   if(!CSeesareLadder::ValidDomain(kv.Get("domain")))
     {
      why = "unknown domain" + at;
      return false;
     }
   if(kv.Get("side") != "BUY" && kv.Get("side") != "SELL")
     {
      why = "bad side" + at;
      return false;
     }
   datetime t_open = 0;
   datetime t_close = 0;
   if(!CSeesareDst::IsoToTime(kv.Get("open"), t_open) || !CSeesareDst::IsoToTime(kv.Get("close"), t_close))
     {
      why = "bad time" + at;
      return false;
     }
   if(t_close < t_open || t_open < m_last_close)
     {
      why = "events out of time order" + at;
      return false;
     }
   int by = CSeesareLadder::CloseFromName(kv.Get("by"));
   int res = CSeesareLadder::ResFromName(kv.Get("res"));
   if(by < 0 || res < -1)
     {
      why = "bad exit kind or resolution" + at;
      return false;
     }
   if(!CSeesareText::IsDecimal(kv.Get("delta"), 4))
     {
      why = "malformed delta" + at;
      return false;
     }
   if(res != (int)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)by, StringToDouble(kv.Get("delta")), SEESARE_TIME_POLICY))
     {
      why = "resolution does not follow the exit rule" + at;
      return false;
     }
   if(kv.Get("dd") != CSeesareText::Fmt(m_l_peak - m_l_net, 4))
     {
      why = "dd is not the lifecycle drawdown" + at;
      return false;
     }
   if(kv.Get("lvl_before") != IntegerToString(m_level))
     {
      why = "lvl_before is not the drawdown level" + at;
      return false;
     }
   if(!CSeesareText::IsDecimal(kv.Get("weight"), 2) || !CSeesareText::IsDecimal(kv.Get("plan"), 4) ||
      !CSeesareText::IsDecimal(kv.Get("risk"), 4) || !CSeesareText::IsDecimal(kv.Get("vol"), 4) ||
      !CSeesareText::IsDecimal(kv.Get("delta"), 4))
     {
      why = "malformed number" + at;
      return false;
     }
   double weight = StringToDouble(kv.Get("weight"));
   double plan   = StringToDouble(kv.Get("plan"));
   double risk   = StringToDouble(kv.Get("risk"));
   double vol    = StringToDouble(kv.Get("vol"));
   double delta  = StringToDouble(kv.Get("delta"));
   if(weight <= 0.0 || weight > SEESARE_MAX_WEIGHT + 1e-12)
     {
      why = "weight out of range" + at;
      return false;
     }
   if(MathAbs(plan - CSeesareLadder::PlanUsd(m_level, weight)) > 0.0001 + 1e-9)
     {
      why = "planned risk does not match the drawdown ladder" + at;
      return false;
     }
   if(risk < 0.0 || vol < 0.0)
     {
      why = "negative risk or volume" + at;
      return false;
     }
   if(real && risk > plan + 1e-9)
     {
      why = "real risk above the ladder's plan" + at;
      return false;
     }
   int la = m_level;
   if(real)
     {
      double net2 = m_l_net + delta;
      double peak2 = MathMax(m_l_peak, net2);
      la = CSeesareLadder::LevelFromDrawdown(peak2 - net2);
     }
   if(kv.Get("lvl_after") != IntegerToString(la))
     {
      why = "drawdown level rule broken" + at;
      return false;
     }
   string deals = kv.Get("deals");
   if(!CSeesareText::IsDeals(deals))
     {
      why = "bad deal tickets" + at;
      return false;
     }
   if(real && (risk <= 0.0 || vol <= 0.0 || deals == "-"))
     {
      why = "real event without risk, volume or deal tickets" + at;
      return false;
     }
   if(!real && (risk != 0.0 || deals != "-"))
     {
      why = "shadow event with real risk or deal tickets" + at;
      return false;
     }
   int pd = CSeesareText::Decimals(kv.Get("entry"));
   if(pd < 0 || pd > 8 || !CSeesareText::IsDecimal(kv.Get("lower"), pd) || !CSeesareText::IsDecimal(kv.Get("upper"), pd) ||
      !CSeesareText::IsDecimal(kv.Get("exit"), pd))
     {
      why = "malformed prices" + at;
      return false;
     }
   double entry = StringToDouble(kv.Get("entry"));
   double lower = StringToDouble(kv.Get("lower"));
   double upper = StringToDouble(kv.Get("upper"));
   double exitp = StringToDouble(kv.Get("exit"));
   if(entry <= 0.0 || lower <= 0.0 || exitp <= 0.0 || upper <= lower)
     {
      why = "bad boundaries" + at;
      return false;
     }
   if(dry)
      return true;
//--- commit
   if(real)
     {
      double dd_before = m_l_peak - m_l_net;
      if(dd_before + risk > EnvelopeCapUSD() + 1e-6)
        {
         m_violations++;
         if(m_first_violation_k < 0)
            m_first_violation_k = k;
        }
      if(res > 0)
        {
         m_c_pos++;
         m_t_pos++;
        }
      else if(res < 0)
        {
         m_c_neg++;
         m_t_neg++;
        }
      else
        {
         m_c_man++;
         m_t_man++;
        }
      m_c_net += delta;
      if(m_c_net > m_c_peak)
         m_c_peak = m_c_net;
      if(m_c_peak - m_c_net > m_c_dd)
         m_c_dd = m_c_peak - m_c_net;
      m_l_net += delta;
      if(m_l_net > m_l_peak)
         m_l_peak = m_l_net;
      if(m_l_peak - m_l_net > m_l_dd)
         m_l_dd = m_l_peak - m_l_net;
      m_n++;
      int c = ArraySize(m_cycle_hashes);
      ArrayResize(m_cycle_hashes, c + 1, 16);
      m_cycle_hashes[c] = hash;
      m_last_real_open = t_open;
     }
   else
     {
      m_shadow++;
      m_c_shadow++;
     }
   m_level = la;
   m_k = k;
   m_head = hash;
   m_last_open = t_open;
   m_last_close = t_close;
   Remember(line, hash, t_close);
   if(real && m_n % SEESARE_CYCLE_EVENTS == 0)
      CloseCycle(t_close);
   if(m_n >= SEESARE_LIFECYCLE_EVENTS)
      m_locked = true;
   return true;
  }

//--- cycle audit at the 10th REAL event; the Virtual Capital Variable restarts at $1,000.00
void CSeesareCycleLedger::CloseCycle(const datetime at)
  {
   int first = m_n - SEESARE_CYCLE_EVENTS + 1;
   int decided = m_c_pos + m_c_neg;
   string rate = "-";
   if(decided > 0)
      rate = CSeesareText::Fmt((double)m_c_pos / (double)decided, 4);
   string joined = "";
   for(int i = 0; i < ArraySize(m_cycle_hashes); i++)
     {
      if(i > 0)
         joined += ",";
      joined += m_cycle_hashes[i];
     }
   string root = CSeesareSha256::Hex(m_life + "|" + IntegerToString(m_cycle) + "|" + joined);
   string a = "v=";
   a += SEESARE_FORMAT;
   a += "|life=" + m_life;
   a += "|audit=cycle|cycle=" + IntegerToString(m_cycle);
   a += "|events=" + IntegerToString(first) + "-" + IntegerToString(m_n);
   a += "|pos=" + IntegerToString(m_c_pos);
   a += "|neg=" + IntegerToString(m_c_neg);
   a += "|man=" + IntegerToString(m_c_man);
   a += "|shadow=" + IntegerToString(m_c_shadow);
   a += "|pos_rate=" + rate;
   a += "|net=" + CSeesareText::Fmt(m_c_net, 4);
   a += "|net_pct=" + CSeesareText::Fmt(m_c_net * 100.0 / SEESARE_BASELINE_USD, 5);
   a += "|max_dd=" + CSeesareText::Fmt(m_c_dd, 4);
   a += "|max_dd_pct=" + CSeesareText::Fmt(m_c_dd * 100.0 / SEESARE_BASELINE_USD, 5);
   a += "|life_net=" + CSeesareText::Fmt(m_l_net, 4);
   a += "|life_dd=" + CSeesareText::Fmt(m_l_dd, 4);
   a += "|lvl_start=" + IntegerToString(m_c_level_start);
   a += "|lvl_end=" + IntegerToString(m_level);
   a += "|root=" + root;
   a += "|head=" + m_head;
   int n = ArraySize(m_anchors);
   string prev = m_genesis;
   if(n > 0)
      prev = StringSubstr(m_anchors[n - 1], StringLen(m_anchors[n - 1]) - 64);
   string content = a + "|prev=" + prev;
   ArrayResize(m_anchors, n + 1, 64);
   ArrayResize(m_anchor_k, n + 1, 64);
   ArrayResize(m_anchor_utc, n + 1, 64);
   m_anchors[n] = content + "|hash=" + CSeesareSha256::Hex(content);
   m_anchor_k[n] = m_k;
   m_anchor_utc[n] = at;
   m_c_pos = 0;
   m_c_neg = 0;
   m_c_man = 0;
   m_c_shadow = 0;
   m_c_net = 0.0;
   m_c_peak = 0.0;
   m_c_dd = 0.0;
   ArrayResize(m_cycle_hashes, 0);
   m_c_level_start = m_level;
   m_cycle++;
  }

string CSeesareCycleLedger::GenesisContent(const datetime created) const
  {
   string g = "v=";
   g += SEESARE_FORMAT;
   g += "|life=" + m_life;
   g += "|k=0|genesis";
   g += "|baseline=" + CSeesareText::Fmt(SEESARE_BASELINE_USD, 2);
   g += "|events=" + IntegerToString(SEESARE_LIFECYCLE_EVENTS);
   g += "|cycle_size=" + IntegerToString(SEESARE_CYCLE_EVENTS);
   g += "|envelope_pct=" + CSeesareText::Fmt(SEESARE_ENVELOPE_PCT, 2);
   g += "|sizing=";
   g += SEESARE_SIZING_NAME;
   g += "|levels=" + IntegerToString(SEESARE_LEVELS);
   g += "|band=" + CSeesareText::Fmt(SEESARE_BAND_USD, 4);
   g += "|room_mult=" + CSeesareText::Fmt(SEESARE_ROOM_MULT, 2);
   g += "|max_weight=" + CSeesareText::Fmt(SEESARE_MAX_WEIGHT, 2);
   g += "|time_policy=";
   g += SEESARE_TIME_POLICY_NAME;
   g += "|created=" + CSeesareDst::IsoUtc(created);
   return g;
  }

//--- builds the canonical line for e at the current state (twin: Ledger.build_event_line)
bool CSeesareCycleLedger::BuildEventLine(const SSeesareEvent &e, string &line, string &why) const
  {
   line = "";
   bool real = (e.mode == SEESARE_REAL);
   if(e.mode != SEESARE_REAL && e.mode != SEESARE_SHADOW)
     {
      why = "bad mode";
      return false;
     }
   if(!CSeesareText::IsToken(e.module, 32) || !CSeesareText::IsToken(e.symbol, 32))
     {
      why = "module and symbol must be tokens of 1-32 printable characters without | = ; ,";
      return false;
     }
   if(!CSeesareLadder::ValidDomain(e.domain))
     {
      why = "domain must be forex, crypto, stocks, indices or commodities";
      return false;
     }
   if(e.side != 1 && e.side != -1)
     {
      why = "side must be +1 or -1";
      return false;
     }
   if(e.digits < 0 || e.digits > 8)
     {
      why = "digits must be 0-8";
      return false;
     }
   if(!CSeesareLadder::ValidWeight(e.weight))
     {
      why = "the weight must be in (0, 1.00] (2 decimals)";
      return false;
     }
   string by = CSeesareLadder::CloseName(e.close_by);
   if(by == "")
     {
      why = "bad exit kind";
      return false;
     }
   string s_delta = CSeesareText::Fmt(e.delta_usd, 4);
   ENUM_SEESARE_RES r = CSeesareLadder::Classify(e.close_by, StringToDouble(s_delta), SEESARE_TIME_POLICY);
   string res = CSeesareLadder::ResName(r);
   string deals = "-";
   if(real)
      deals = e.deals;
   if(real && (deals == "-" || !CSeesareText::IsDeals(deals)))
     {
      why = "a REAL event needs its deal tickets, like 123;124";
      return false;
     }
   string mode_name = "SHADOW";
   if(real)
      mode_name = "REAL";
   string step = "-";
   if(real)
      step = IntegerToString(m_n % SEESARE_CYCLE_EVENTS + 1);
   int n_after = m_n;
   if(real)
      n_after = m_n + 1;
   double risk = 0.0;
   if(real)
      risk = e.risk_usd;
   string side_name = "SELL";
   if(e.side > 0)
      side_name = "BUY";
   string s_weight = CSeesareText::Fmt(e.weight, 2);
   string s_plan   = CSeesareLadder::PlanText(m_level, StringToDouble(s_weight));
   int la = m_level;
   if(real)
     {
      double net2 = m_l_net + StringToDouble(s_delta);
      double peak2 = MathMax(m_l_peak, net2);
      la = CSeesareLadder::LevelFromDrawdown(peak2 - net2);
     }
   string c = "v=";
   c += SEESARE_FORMAT;
   c += "|life=" + m_life;
   c += "|k=" + IntegerToString(m_k + 1);
   c += "|mode=" + mode_name;
   c += "|n=" + IntegerToString(n_after);
   c += "|cycle=" + IntegerToString(m_cycle);
   c += "|step=" + step;
   c += "|module=" + e.module;
   c += "|domain=" + e.domain;
   c += "|symbol=" + e.symbol;
   c += "|side=" + side_name;
   c += "|open=" + CSeesareDst::IsoUtc(e.utc_open);
   c += "|close=" + CSeesareDst::IsoUtc(e.utc_close);
   c += "|by=" + by;
   c += "|res=" + res;
   c += "|dd=" + CSeesareText::Fmt(m_l_peak - m_l_net, 4);
   c += "|lvl_before=" + IntegerToString(m_level);
   c += "|lvl_after=" + IntegerToString(la);
   c += "|weight=" + s_weight;
   c += "|plan=" + s_plan;
   c += "|risk=" + CSeesareText::Fmt(risk, 4);
   c += "|vol=" + CSeesareText::Fmt(e.volume, 4);
   c += "|entry=" + CSeesareText::Fmt(e.entry, e.digits);
   c += "|lower=" + CSeesareText::Fmt(e.lower, e.digits);
   c += "|upper=" + CSeesareText::Fmt(e.upper, e.digits);
   c += "|exit=" + CSeesareText::Fmt(e.exit_price, e.digits);
   c += "|delta=" + s_delta;
   c += "|deals=" + deals;
   c += "|prev=" + m_head;
   string h = CSeesareSha256::Hex(c);
   if(h == "")
     {
      why = "SHA-256 is not available in this terminal";
      return false;
     }
   line = c + "|hash=" + h;
   return true;
  }

//+------------------------------------------------------------------+
//| Opens (or creates) <root>\<life>. created_utc is used only for a |
//| new lifecycle. adopt_ledger=true accepts a ledger whose state.dat|
//| is missing or damaged (use once, after checking ledger.txt).     |
//+------------------------------------------------------------------+
bool CSeesareCycleLedger::Open(const string root, const string life, const datetime created_utc, const bool adopt_ledger)
  {
   m_open = false;
   m_fault = false;
   m_error = "";
   m_warning = "";
   ResetState();
   m_life = life;
   if(!CSeesareText::IsFolderPath(root))
      return Fail("bad root folder name: " + root);
   if(!CSeesareText::IsLifeId(life))
      return Fail("the lifecycle id must be 1-32 letters, digits, '_' or '-'");
   string why = "";
   if(CSeesareSha256::Hex("abc") != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
      return Fail("the SHA-256 self-check failed in this terminal");
   m_root = root;
   m_dir = root + "\\" + life;
   m_ledger_path = m_dir + "\\ledger.txt";
   m_anchor_path = m_dir + "\\anchors.txt";
   m_state_path = m_dir + "\\state.dat";
   CSeesareFiles::EnsureFolder(m_dir);
   string lines[];
   int count = 0;
   if(CSeesareFiles::Exists(m_ledger_path))
     {
      count = CSeesareFiles::ReadLines(m_ledger_path, lines);
      if(count < 0)
         return Fail("cannot read " + m_ledger_path);
     }
   if(count == 0)
     {
      if(CSeesareFiles::Exists(m_state_path) || CSeesareFiles::Exists(m_state_path + ".bak") || CSeesareFiles::Exists(m_anchor_path))
         return Fail("ledger.txt is missing or empty but state.dat or anchors.txt exist: restore ledger.txt or use a new lifecycle id");
      if(created_utc <= 0)
         return Fail("a new lifecycle needs its creation time");
      string g = GenesisContent(created_utc);
      string gl = g + "|hash=" + CSeesareSha256::Hex(g);
      if(!ApplyLine(gl, true, why))
         return Fail("genesis: " + why);
      if(!CSeesareFiles::WriteAll(m_ledger_path, gl + "\r\n"))
         return Fail("cannot create " + m_ledger_path);
      if(!ApplyLine(gl, false, why))
         return Fail("genesis: " + why);
     }
   else
     {
      for(int i = 0; i < count; i++)
         if(!ApplyLine(lines[i], false, why))
            return Fail("ledger.txt line " + IntegerToString(i + 1) + ": " + why);
     }
   if(!CheckState(adopt_ledger))
      return false;
   if(!VerifyAnchorsFile())
      return false;
   if(!m_outbox.Init(m_dir + "\\outbox", m_loaded_seq))
      return Fail("outbox: " + m_outbox.LastError());
   m_open = true;
   Retry();
   return true;
  }

//--- state.dat must not be ahead of the ledger (lost lines) and must name the same chain
bool CSeesareCycleLedger::CheckState(const bool adopt)
  {
   CSeesareKV kv;
   int st = CSeesareStateStore::Load(m_state_path, kv);
   m_out_next = 0;
   m_out_audits = 0;
   m_out_life = false;
   m_loaded_seq = 0;
   if(st <= 0)
     {
      if(st == 0 && m_k == 0)
         return true;
      if(!adopt)
        {
         if(st == 0)
            return Fail("state.dat is missing while ledger.txt has events: if ledger.txt is complete, open once with adopt_ledger=true");
         return Fail("state.dat and its backup are damaged: if ledger.txt is complete, open once with adopt_ledger=true");
        }
      m_warning = "ledger adopted without a state snapshot: every outbox message is queued again (the relay drops duplicates)";
      return true;
     }
   if(st == 2)
      m_warning = "state.dat was damaged; its backup was used";
   string sk = kv.Get("k");
   if(kv.Get("life") != m_life || !CSeesareText::IsUInt(sk) || !CSeesareText::IsUInt(kv.Get("out_next")) ||
      !CSeesareText::IsUInt(kv.Get("out_audits")) || !CSeesareText::IsUInt(kv.Get("out_seq")))
      return Fail("state.dat does not belong to this lifecycle or is malformed");
   int k = (int)StringToInteger(sk);
   if(k > m_k)
      return Fail("ledger.txt ends at k=" + IntegerToString(m_k) + " but state.dat recorded k=" + IntegerToString(k) +
                  ": ledger.txt lost lines; restore it from a backup");
   if(kv.Get("head") != m_hashes[k])
      return Fail("ledger.txt line k=" + IntegerToString(k) + " differs from the hash saved in state.dat: the ledger was replaced or edited");
   m_out_next = (int)StringToInteger(kv.Get("out_next"));
   m_out_audits = (int)StringToInteger(kv.Get("out_audits"));
   m_out_life = (kv.Get("out_life") == "1");
   m_loaded_seq = StringToInteger(kv.Get("out_seq"));
   if(m_out_next > m_k + 1 || m_out_audits > ArraySize(m_anchors))
      return Fail("state.dat delivery counters are ahead of the ledger");
   return true;
  }

//--- anchors.txt must be a prefix of the audits rebuilt from the ledger
bool CSeesareCycleLedger::VerifyAnchorsFile(void)
  {
   m_anchors_on_disk = 0;
   if(!CSeesareFiles::Exists(m_anchor_path))
      return true;
   string lines[];
   int count = CSeesareFiles::ReadLines(m_anchor_path, lines);
   if(count < 0)
      return Fail("cannot read " + m_anchor_path);
   if(count > ArraySize(m_anchors))
      return Fail("anchors.txt holds more cycles than ledger.txt: the ledger lost lines or the files were mixed");
   for(int i = 0; i < count; i++)
      if(lines[i] != m_anchors[i])
         return Fail("anchors.txt line " + IntegerToString(i + 1) + " differs from the cycle audit rebuilt from ledger.txt");
   m_anchors_on_disk = count;
   return true;
  }

bool CSeesareCycleLedger::WriteMissingAnchors(void)
  {
   while(m_anchors_on_disk < ArraySize(m_anchors))
     {
      if(!CSeesareFiles::AppendLine(m_anchor_path, m_anchors[m_anchors_on_disk]))
        {
         //--- the write may have landed although it reported a failure: resynchronise from the file
         string lines[];
         int count = CSeesareFiles::ReadLines(m_anchor_path, lines);
         if(count == m_anchors_on_disk + 1 && lines[count - 1] == m_anchors[m_anchors_on_disk])
           {
            m_anchors_on_disk++;
            continue;
           }
         return false;
        }
      m_anchors_on_disk++;
     }
   return true;
  }

//--- pushes, in chain order, every message not yet in the outbox (an audit right after the event that closed its cycle)
bool CSeesareCycleLedger::Heal(void)
  {
   while(true)
     {
      while(m_out_audits < ArraySize(m_anchors) && m_anchor_k[m_out_audits] < m_out_next)
        {
         if(!m_outbox.Push("AUDIT", m_life, m_out_audits + 1, m_anchor_utc[m_out_audits], m_anchors[m_out_audits]))
            return false;
         m_out_audits++;
        }
      if(m_out_next > m_k)
         break;
      string kind = "EVENT";
      if(m_out_next == 0)
         kind = "GENESIS";
      if(!m_outbox.Push(kind, m_life, m_out_next, m_line_utc[m_out_next], m_lines[m_out_next]))
         return false;
      m_out_next++;
     }
   if(m_locked && !m_out_life)
     {
      if(!m_outbox.Push("LIFECYCLE", m_life, m_n, m_last_close, LifecycleSummary()))
         return false;
      m_out_life = true;
     }
   return true;
  }

string CSeesareCycleLedger::LifecycleSummary(void) const
  {
   string s = "v=";
   s += SEESARE_FORMAT;
   s += "|life=" + m_life;
   s += "|audit=lifecycle|events=" + IntegerToString(m_n);
   s += "|cycles=" + IntegerToString(ArraySize(m_anchors));
   s += "|shadow=" + IntegerToString(m_shadow);
   s += "|pos=" + IntegerToString(m_t_pos);
   s += "|neg=" + IntegerToString(m_t_neg);
   s += "|man=" + IntegerToString(m_t_man);
   s += "|net=" + CSeesareText::Fmt(m_l_net, 4);
   s += "|net_pct=" + CSeesareText::Fmt(m_l_net * 100.0 / SEESARE_BASELINE_USD, 5);
   s += "|max_dd=" + CSeesareText::Fmt(m_l_dd, 4);
   s += "|max_dd_pct=" + CSeesareText::Fmt(m_l_dd * 100.0 / SEESARE_BASELINE_USD, 5);
   s += "|violations=" + IntegerToString(m_violations);
   s += "|head=" + m_head;
   return s;
  }

bool CSeesareCycleLedger::SaveState(void)
  {
   CSeesareKV kv;
   kv.Set("life", m_life);
   kv.Set("k", IntegerToString(m_k));
   kv.Set("head", m_head);
   kv.Set("n", IntegerToString(m_n));
   kv.Set("shadow", IntegerToString(m_shadow));
   kv.Set("level", IntegerToString(m_level));
   kv.Set("cycle", IntegerToString(m_cycle));
   kv.Set("locked", (m_locked ? "1" : "0"));
   kv.Set("out_next", IntegerToString(m_out_next));
   kv.Set("out_audits", IntegerToString(m_out_audits));
   kv.Set("out_life", (m_out_life ? "1" : "0"));
   kv.Set("out_seq", IntegerToString(m_outbox.LastSeq()));
   kv.Set("saved", CSeesareDst::IsoUtc(TimeGMT()));
   return CSeesareStateStore::Save(m_state_path, kv);
  }

//--- writes whatever is pending (anchors, outbox messages, state.dat); safe to call from OnTimer
bool CSeesareCycleLedger::Retry(void)
  {
   if(!m_open || m_fault)
      return false;
   bool ok = WriteMissingAnchors();
   if(!Heal())
      ok = false;
   if(!SaveState())
      ok = false;
   if(!ok)
      m_warning = "pending writes (anchors, outbox or state.dat) will be retried: " + m_outbox.LastError();
   return ok;
  }

//+------------------------------------------------------------------+
//| Records one resolved event. false = not recorded (LastError()    |
//| says why); the state is then unchanged. The ledger line is on    |
//| disk before the state changes, and state.dat is saved after.     |
//+------------------------------------------------------------------+
bool CSeesareCycleLedger::Record(const SSeesareEvent &e, string &hash_out)
  {
   hash_out = "";
   if(!m_open || m_fault)
     {
      if(!m_fault)
         m_error = "the ledger is not open";
      return false;
     }
   if(m_locked)
     {
      m_error = "the lifecycle is complete (360 real events): start a new lifecycle id";
      return false;
     }
   string line = "";
   string why = "";
   if(!BuildEventLine(e, line, why) || !ApplyLine(line, true, why))
     {
      m_error = "event refused: " + why;
      return false;
     }
   if(!CSeesareFiles::AppendLine(m_ledger_path, line))
     {
      if(CSeesareFiles::LastLine(m_ledger_path) != line)
        {
         m_error = "could not append to " + m_ledger_path + ": the event is NOT recorded; call Record again";
         return false;
        }
     }
   if(!ApplyLine(line, false, why))
      return Fail("a written line could not be applied: " + why);
   hash_out = m_head;
   m_error = "";
   if(m_violations > 0 && m_first_violation_k == m_k)
     {
      m_warning = "ENVELOPE RULE BROKEN at k=" + IntegerToString(m_k) + ": a REAL event opened with drawdown + risk above " +
                  CSeesareText::Fmt(SEESARE_ENVELOPE_PCT, 1) + "% of the baseline; real risk is refused for the rest of this lifecycle";
      Print("SEESARE ledger: ", m_warning);
     }
   Retry();
   return true;
  }

//--- the pre-trade envelope guard: true if drawdown + this all-in risk stays within $36 (3.6% of $1,000).
//--- risk_usd = loss at the stop for the actual volume + round-trip commission + swap and slippage allowances.
bool CSeesareCycleLedger::AllowsRealRisk(const double risk_usd) const
  {
   if(!m_open || m_fault || m_locked || m_violations > 0 || risk_usd <= 0.0)
      return false;
   double r = StringToDouble(CSeesareText::Fmt(risk_usd, 4));
   return (LifeDrawdownUSD() + r <= EnvelopeCapUSD() + 1e-9);
  }

//--- the planned risk the ledger will accept for a REAL event now (sizing uses this); 0 when stopped; -1 if not open or
//--- the weight is outside (0, 1.00]
double CSeesareCycleLedger::PlanUsdAt(const double weight) const
  {
   if(!m_open || !CSeesareLadder::ValidWeight(weight))
      return -1.0;
   return StringToDouble(CSeesareLadder::PlanText(m_level, weight));
  }

#endif

//+------------------------------------------------------------------+
//|                                              SeesareRouter.mq5   |
//| SEESARE P26 router, Phase 2. UNCOMPILED SOURCE.                  |
//|                                                                  |
//| Runs the payer-flow modules on a 1-second clock:                 |
//|   PAPER modules  forward test on live quotes -> journal          |
//|                  Common\Files\seesare\<login>\paper\<module>.csv |
//|   LIVE modules   one SEESARE event per UTC day -> cycle ledger.  |
//|                  This build has NO order gateway: every LIVE     |
//|                  event runs as SHADOW (paper, Shadow-Lot). Real  |
//|                  orders come in the next phase, after the        |
//|                  self-tests compile and pass and a module has    |
//|                  passed its forward test.                        |
//| Module evidence (README): Tokyo fix = CANDIDATE (PAPER or LIVE); |
//| London fix = REJECTED and US close = UNTESTED (PAPER at most).   |
//| Never sends an order.                                            |
//+------------------------------------------------------------------+
#property copyright   "T.citybank"
#property version     "2.00"
#property description "SEESARE router: flow modules on paper and SEESARE shadow events (no order gateway in this build)"

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Core\SpreadGate.mqh>
#include <Seesare\Core\Calendar.mqh>
#include <Seesare\Ledger\CycleLedger.mqh>
#include <Seesare\Risk\Exposure.mqh>
#include <Seesare\Exec\PaperBook.mqh>
#include <Seesare\Flows\FlowTokyoFix.mqh>
#include <Seesare\Flows\FlowLondonFix.mqh>
#include <Seesare\Flows\FlowUsClose.mqh>

input string                     InpLifecycle     = "P26-001";                         // SEESARE lifecycle id (used by LIVE modules)
input string                     InpLadder        = "";                                // 16 level % "0.1440,...,0.0003" (4 decimals, decreasing); empty = SEESARE P26 default. Published in the genesis line; fixed for the lifecycle
input ENUM_SEESARE_SERVER_SCHEME InpScheme        = SEESARE_SERVER_GMT2_EU;            // broker server time scheme (Phase 1 self-test)
input ENUM_SEESARE_STATUS        InpTokyoStatus   = SEESARE_STATUS_PAPER;              // Module 1 Tokyo gotobi fix (CANDIDATE)
input string                     InpTokyoSymbol   = "USDJPY";
input ENUM_SEESARE_STATUS        InpLondonStatus  = SEESARE_STATUS_OFF;                // Module 3 London 4 pm fix (REJECTED: paper at most)
input string                     InpLondonSymbol1 = "EURUSD";
input string                     InpLondonSymbol2 = "GBPUSD";
input ENUM_SEESARE_STATUS        InpUsStatus      = SEESARE_STATUS_OFF;                // Module 2 US close imbalance (UNTESTED: paper at most)
input string                     InpUsSymbol      = "US500";
input string                     InpUsFeed        = "seesare\\feeds\\moc_imbalance.csv"; // Common\Files: YYYY-MM-DD,HH:MM,net_usd (New York)
input double                     InpUsMinUsd      = 1000000000.0;                      // |net imbalance| needed to trade, USD
input double                     InpUsMaxSpread   = 50.0;                              // US close spread cap, points
input double                     InpCommissionLot = 7.0;                               // commission per lot of this broker's contract, round trip, USD (RoboForex ProCent: 0)
input double                     InpUnitsPerUsd   = 0.0;                               // account money per USD: 0 = from the account currency (USD 1, USC 100)
input int                        InpPatienceSec   = 300;                               // wait this long after the entry time for a normal spread

CSeesareClock        g_clock;
CSeesareSpreadGate   g_gate;
CSeesareCycleLedger  g_ledger;
CSeesarePaperBook    g_paper;
CSeesareFlowModule  *g_mod[];
SSeesareSlot         g_slot[];
bool                 g_has_slot[];
bool                 g_done[];
string               g_note[];
datetime             g_day = 0;
datetime             g_last_retry = 0;
bool                 g_live = false;
string               g_root = "";
double               g_units = 0.0;

//+------------------------------------------------------------------+
void Log(const string text)
  {
   Print("SEESARE router: ", text);
  }

bool AddModule(CSeesareFlowModule *m, const ENUM_SEESARE_STATUS status)
  {
   if(CheckPointer(m) == POINTER_INVALID)
      return false;
   if(!m.SetStatus(status))
      Log(m.LastError());
   if(m.Status() != SEESARE_STATUS_OFF)
     {
      if(!SymbolSelect(m.Market(), true))
        {
         Log(m.Id() + ": symbol " + m.Market() + " is not available at this broker; module switched off");
         m.SetStatus(SEESARE_STATUS_OFF);
        }
     }
   if(m.Status() == SEESARE_STATUS_LIVE)
      g_live = true;
   int n = ArraySize(g_mod);
   ArrayResize(g_mod, n + 1);
   g_mod[n] = m;
   Log(m.Id() + " " + CSeesareFlowModule::StatusName(m.Status()) + " on " + m.Market() + " (evidence " +
       CSeesareFlowModule::EvidenceName(m.Evidence()) + ": " + m.EvidenceRef() + ")");
   return true;
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   if(!g_clock.Init(InpScheme, 0, 300))
     {
      Log("clock: " + g_clock.LastError());
      return INIT_PARAMETERS_INCORRECT;
     }
   if(!g_clock.Healthy())
      Log("clock not healthy yet (entries wait for it): " + g_clock.LastError());
   g_units = InpUnitsPerUsd;
   if(g_units <= 0.0)
      g_units = CSeesareExposure::AccountUnitsPerUsd();
   if(g_units <= 0.0)
     {
      Log("account currency " + AccountInfoString(ACCOUNT_CURRENCY) + " is neither USD nor US cents: set InpUnitsPerUsd");
      return INIT_PARAMETERS_INCORRECT;
     }
   Log("account currency " + AccountInfoString(ACCOUNT_CURRENCY) + ": " + CSeesareText::Fmt(g_units, 0) +
       " account units per USD; plans, risk and the envelope are kept in USD");
   string base = "seesare\\";
   if(MQLInfoInteger(MQL_TESTER) != 0)
      base = "seesare_tester\\";
   g_root = base + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
   AddModule(new CSeesareFlowTokyoFix(InpTokyoSymbol), InpTokyoStatus);
   AddModule(new CSeesareFlowLondonFix(InpLondonSymbol1), InpLondonStatus);
   AddModule(new CSeesareFlowLondonFix(InpLondonSymbol2), InpLondonStatus);
   AddModule(new CSeesareFlowUsClose(InpUsSymbol, InpUsFeed, InpUsMinUsd, InpUsMaxSpread), InpUsStatus);
   if(g_live)
     {
      if(InpLadder != "")
        {
         double pct[];
         string why = "";
         if(!CSeesareLadder::Parse(InpLadder, pct, why))
           {
            Log("ladder: " + why);
            return INIT_PARAMETERS_INCORRECT;
           }
         if(!g_ledger.SetLadder(pct))
           {
            Log(g_ledger.LastError());
            return INIT_PARAMETERS_INCORRECT;
           }
         Log("ladder " + CSeesareLadder::Text(pct) + " (declared in the genesis line)");
        }
      if(!g_ledger.Open(g_root, InpLifecycle, g_clock.UtcNow(), false))
        {
         Log("ledger: " + g_ledger.LastError());
         return INIT_FAILED;
        }
      Log("lifecycle " + InpLifecycle + ": " + IntegerToString(g_ledger.RealCount()) + " real events, level " +
          IntegerToString(g_ledger.Level()) + ", envelope room " + CSeesareText::Fmt(g_ledger.EnvelopeRoomUSD(), 2) + " USD");
     }
   if(!g_paper.Init(g_root, g_units))
      Log("paper book: " + g_paper.LastError());
   Log("no order gateway in this build: nothing is ever sent to the broker");
   EventSetTimer(1);
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   for(int i = 0; i < ArraySize(g_mod); i++)
      if(CheckPointer(g_mod[i]) == POINTER_DYNAMIC)
         delete g_mod[i];
   ArrayResize(g_mod, 0);
  }

//+------------------------------------------------------------------+
void BuildSlots(const datetime today)
  {
   g_day = today;
   int n = ArraySize(g_mod);
   ArrayResize(g_slot, n);
   ArrayResize(g_has_slot, n);
   ArrayResize(g_done, n);
   ArrayResize(g_note, n);
   string agenda = "";
   for(int i = 0; i < n; i++)
     {
      g_has_slot[i] = false;
      g_done[i] = false;
      g_note[i] = "";
      g_slot[i].module = i;
      g_slot[i].module_id = g_mod[i].Id();
      g_slot[i].day_utc = today;
      g_slot[i].entry_utc = 0;
      g_slot[i].exit_utc = 0;
      if(g_mod[i].Status() == SEESARE_STATUS_OFF)
         continue;
      SSeesareSlot s;
      if(g_mod[i].SlotForUtcDay(today, s))
        {
         SeesareCopySlot(s, g_slot[i]);
         g_slot[i].module = i;
         g_has_slot[i] = true;
         agenda += " " + g_mod[i].Id() + "@" + StringSubstr(CSeesareDst::IsoUtc(s.entry_utc), 11, 5);
        }
      else if(g_mod[i].LastError() != "")
         Log(g_mod[i].LastError());
     }
   if(agenda == "")
      agenda = " none";
   Log("agenda " + StringSubstr(CSeesareDst::IsoUtc(today), 0, 10) + " UTC:" + agenda);
  }

//--- one SEESARE event per UTC day
bool DayTaken(const datetime day)
  {
   if(!g_live)
      return false;
   if(g_paper.HasLive())
      return true;
   return (g_ledger.LastEventOpenUtc() > 0 && CSeesareDst::Midnight(g_ledger.LastEventOpenUtc()) == day);
  }

void Skip(const int i, const string why)
  {
   g_done[i] = true;
   Log(g_mod[i].Id() + " " + StringSubstr(CSeesareDst::IsoUtc(g_slot[i].entry_utc), 0, 16) + ": skipped (" + why + ")");
  }

void TryEntry(const int i, const datetime now)
  {
   if(!g_has_slot[i] || g_done[i] || now < g_slot[i].entry_utc)
      return;
   CSeesareFlowModule *m = g_mod[i];
   string key = m.Id() + "@" + CSeesareDst::IsoUtc(g_slot[i].entry_utc);
   if(g_paper.Seen(key))
     {
      g_done[i] = true;
      return;
     }
   if((long)now >= (long)g_slot[i].entry_utc + InpPatienceSec)
     {
      string why = "entry window passed";
      if(g_note[i] != "")
         why += ": " + g_note[i];
      Skip(i, why);
      return;
     }
   bool live = (m.Status() == SEESARE_STATUS_LIVE);
   if(live && DayTaken(g_slot[i].day_utc))
     {
      Skip(i, "this UTC day already has its SEESARE event");
      return;
     }
   SSeesareOrderPlan plan;
   if(!m.Decide(g_slot[i], g_clock, plan))
     {
      g_note[i] = plan.note;
      return;                                                    // data not ready: ask again next second
     }
   if(plan.side == 0)
     {
      Skip(i, plan.note);
      return;
     }
   SSeesareUtcWindow w;
   w.id = m.Id();
   w.index = i;
   w.start_utc = g_slot[i].entry_utc;
   w.end_utc = (datetime)((long)g_slot[i].entry_utc + InpPatienceSec);
   w.local_date = g_slot[i].day_utc;
   if(!g_gate.Configure(plan.max_spread_points, 0.15, InpPatienceSec, 15))
     {
      Skip(i, "spread gate: " + g_gate.LastError());
      return;
     }
   SSeesareGateResult gr;
   ENUM_SEESARE_GATE verdict = g_gate.Check(m.Market(), plan.side, plan.stop_distance, w, g_clock, gr);
   if(verdict == SEESARE_GATE_WAIT)
     {
      g_note[i] = gr.reason;
      return;
     }
   if(verdict != SEESARE_GATE_PASS)
     {
      Skip(i, CSeesareSpreadGate::VerdictName(verdict) + ": " + gr.reason);
      return;
     }
   MqlTick tick;
   if(!SymbolInfoTick(m.Market(), tick))
      return;
   double entry = (plan.side > 0 ? tick.ask : tick.bid);
   double stop = (plan.side > 0 ? entry - plan.stop_distance : entry + plan.stop_distance);
   double target_dist = plan.ratio * plan.stop_distance;
   double loss_per_lot = 0.0;
   if(!CSeesareExposure::LossPerLot(m.Market(), plan.side, entry, stop, g_units, loss_per_lot))
     {
      Skip(i, "cannot price the stop for " + m.Market());
      return;
     }
   double volume = 1.0;
   if(live)
     {
      SSeesareSizing sz;
      CSeesareExposure::Size(g_ledger, m.Market(), m.Domain(), plan.side, entry, stop, plan.ratio, InpCommissionLot, g_units, sz);
      volume = sz.virtual_volume;
      if(sz.feasible)
         Log(m.Id() + ": REAL would be feasible (" + sz.why + ") but this build has no order gateway: SHADOW");
      else
         Log(m.Id() + ": " + sz.why);
     }
   SSeesarePaper p;
   p.key           = key;
   p.module_id     = m.Id();
   p.symbol        = m.Market();
   p.domain        = m.Domain();
   p.live          = live;
   p.side          = plan.side;
   p.digits        = (int)SymbolInfoInteger(m.Market(), SYMBOL_DIGITS);
   p.volume        = volume;
   p.entry         = entry;
   p.stop          = stop;
   p.lower         = (plan.side > 0 ? stop : entry - target_dist);
   p.upper         = (plan.side > 0 ? entry + target_dist : stop);
   p.target        = 0.0;
   if(plan.place_target)
      p.target = (plan.side > 0 ? p.upper : p.lower);
   p.ratio         = plan.ratio;
   p.loss_per_lot  = loss_per_lot;
   p.commission    = InpCommissionLot;
   p.spread_points = gr.spread_points;
   p.open_utc      = now;
   p.exit_utc      = g_slot[i].exit_utc;
   p.last_msc      = tick.time_msc;
   string mode_name = " PAPER ";
   if(live)
      mode_name = " SHADOW ";
   string side_name = "SELL ";
   if(plan.side > 0)
      side_name = "BUY ";
   if(g_paper.Open(p))
      Log(m.Id() + mode_name + side_name + m.Market() + " at " + DoubleToString(entry, p.digits) + ", stop " +
          DoubleToString(stop, p.digits) + ", time exit " + CSeesareDst::IsoUtc(p.exit_utc) + " (" + plan.note + ")");
   else
      Log(m.Id() + ": " + g_paper.LastError());
   g_done[i] = true;
  }

//--- a paper position closed: journal it; a LIVE one becomes a SHADOW event in the SEESARE ledger
void Finish(const SSeesarePaperResult &r)
  {
   g_paper.Journal(r);
   string late = "";
   if(r.late)
      late = " (late: the terminal was off at the exit time)";
   Log(r.module_id + " closed by " + CSeesareLadder::CloseName(r.by) + ": " + DoubleToString(r.r_net, 3) + "R" + late);
   if(!r.live)
      return;
   SSeesareEvent e;
   e.Clear();
   e.mode       = SEESARE_SHADOW;
   e.module     = r.module_id;
   e.domain     = r.domain;
   e.symbol     = r.symbol;
   e.side       = r.side;
   e.digits     = r.digits;
   e.utc_open   = r.open_utc;
   e.utc_close  = r.close_utc;
   e.close_by   = r.by;
   e.ratio      = r.ratio;
   e.risk_usd   = 0.0;
   e.volume     = r.volume;
   e.entry      = r.entry;
   e.lower      = r.lower;
   e.upper      = r.upper;
   e.exit_price = r.exit_price;
   e.delta_usd  = r.pnl_usd;
   e.deals      = "-";
   string h = "";
   if(g_ledger.Record(e, h))
      Log("ledger k=" + IntegerToString(g_ledger.ChainIndex()) + " level " + IntegerToString(g_ledger.Level()) + " head " + h);
   else
      Log("ledger refused the event: " + g_ledger.LastError());
  }

//+------------------------------------------------------------------+
void OnTimer()
  {
   g_clock.Tick();
   datetime now = g_clock.UtcNow();
   SSeesarePaperResult closed[];
   int nc = g_paper.Step(g_clock, closed);
   for(int i = 0; i < nc; i++)
      Finish(closed[i]);
   datetime today = CSeesareDst::Midnight(now);
   if(today != g_day)
      BuildSlots(today);
   for(int i = 0; i < ArraySize(g_mod); i++)
      if(g_mod[i].Status() != SEESARE_STATUS_OFF)
         TryEntry(i, now);
   if(g_live && (long)now - (long)g_last_retry >= 60)
     {
      g_ledger.Retry();
      g_last_retry = now;
     }
  }
//+------------------------------------------------------------------+

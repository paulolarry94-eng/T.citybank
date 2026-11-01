//+------------------------------------------------------------------+
//|                                       SeesarePhase2SelfTest.mq5  |
//| SEESARE router, Phase 2 self-test. UNCOMPILED SOURCE.            |
//|                                                                  |
//| Checks the gotobi calendar, the three modules' clocks (UTC entry |
//| and exit on given dates, DST included), the volume rounding, the |
//| evidence gate, the US-close feed parser and the paper book's     |
//| restart file. Expected values come from tools/seesare_flows.py   |
//| (--mql); research/truth/tests/test_seesare_phase2.py fails if    |
//| this block and the twin drift apart. INFO lines (not counted)    |
//| price the Tokyo module's stop on this terminal's USDJPY.         |
//+------------------------------------------------------------------+
#property copyright   "T.citybank"
#property version     "2.00"
#property description "SEESARE Phase 2 self-test: calendar, module clocks, sizing, evidence gate, paper book"

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Core\Calendar.mqh>
#include <Seesare\Ledger\CycleLedger.mqh>
#include <Seesare\Risk\Exposure.mqh>
#include <Seesare\Exec\PaperBook.mqh>
#include <Seesare\Flows\FlowTokyoFix.mqh>
#include <Seesare\Flows\FlowLondonFix.mqh>
#include <Seesare\Flows\FlowUsClose.mqh>

int    g_pass = 0;
int    g_fail = 0;

void T_Bool(const string name, const bool ok, const string detail)
  {
   if(ok)
     {
      g_pass++;
      Print("PASS  ", name);
      return;
     }
   g_fail++;
   if(detail == "")
      Print("FAIL  ", name);
   else
      Print("FAIL  ", name, "  -> ", detail);
  }

void T_Str(const string name, const string got, const string want)
  {
   T_Bool(name, got == want, "got [" + got + "] want [" + want + "]");
  }

void T_Int(const string name, const long got, const long want)
  {
   T_Bool(name, got == want, "got " + IntegerToString(got) + " want " + IntegerToString(want));
  }

string GotobiList(const int year)
  {
   string s = "";
   datetime d = CSeesareDst::Date(year, 1, 1);
   while(CSeesareDst::Year(d) == year)
     {
      bool known = false;
      if(CSeesareCalendar::IsGotobiFix(d, known))
        {
         MqlDateTime t;
         TimeToStruct(d, t);
         if(s != "")
            s += ",";
         s += StringFormat("%02d%02d", t.mon, t.day);
        }
      d = (datetime)((long)d + SEESARE_DAY_SEC);
     }
   return s;
  }

CSeesareFlowModule *MakeModule(const int i)
  {
   if(i == 0)
      return new CSeesareFlowTokyoFix("USDJPY");
   if(i == 1)
      return new CSeesareFlowLondonFix("EURUSD");
   return new CSeesareFlowUsClose("US500", "seesare_selftest\\none.csv", 1000000000.0, 50.0);
  }

string SlotText(const int i, const datetime utc_day)
  {
   CSeesareFlowModule *m = MakeModule(i);
   SSeesareSlot s;
   string out = "none";
   if(m.SlotForUtcDay(utc_day, s))
      out = CSeesareDst::IsoUtc(s.entry_utc) + "/" + CSeesareDst::IsoUtc(s.exit_utc);
   delete m;
   return out;
  }

string SizeText(const double plan, const double per_lot, const double step, const double vmin, const double vmax)
  {
   double virtual_volume = 0.0;
   bool feasible = false;
   double vol = CSeesareExposure::Volume(plan, per_lot, step, vmin, vmax, virtual_volume, feasible);
   string word = "shadow ";
   if(feasible)
      word = "feasible ";
   return word + CSeesareText::Fmt(vol, 2);
  }

//--- BEGIN GENERATED VECTORS: python3 tools/seesare_flows.py --mql  (do not edit by hand)
void GeneratedVectors(void)
  {
   T_Str("gotobi fix dates 2026", GotobiList(2026), "0105,0109,0115,0120,0123,0130,0205,0210,0213,0220,0225,0227,0305,0310,0313,0319,0325,0331,0403,0410,0415,0420,0424,0430,0501,0508,0515,0520,0525,0529,0605,0610,0615,0619,0625,0630,0703,0710,0715,0717,0724,0731,0805,0810,0814,0820,0825,0831,0904,0910,0915,0918,0925,0930,1005,1009,1015,1020,1023,1030,1105,1110,1113,1120,1125,1130,1204,1210,1215,1218,1225,1230");
   T_Str("gotobi fix dates 2027", GotobiList(2027), "0105,0108,0115,0120,0125,0129,0205,0210,0215,0219,0225,0226,0305,0310,0315,0319,0325,0331,0405,0409,0415,0420,0423,0430,0510,0514,0520,0525,0531,0604,0610,0615,0618,0625,0630,0705,0709,0715,0720,0723,0730,0805,0810,0813,0820,0825,0831,0903,0910,0915,0917,0924,0930,1005,1008,1015,1020,1025,1029,1105,1110,1115,1119,1125,1130,1203,1210,1215,1220,1224,1230");
   T_Bool("tokyo business 2026-01-02", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 1, 2)) == false, "");
   T_Bool("tokyo business 2026-01-05", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 1, 5)) == true, "");
   T_Bool("tokyo business 2026-09-22", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 9, 22)) == false, "");
   T_Bool("tokyo business 2026-05-06", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 5, 6)) == false, "");
   T_Bool("tokyo business 2026-12-31", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 12, 31)) == false, "");
   T_Bool("tokyo business 2026-11-23", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 11, 23)) == false, "");
   T_Bool("tokyo business 2026-11-24", CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date(2026, 11, 24)) == true, "");
   T_Bool("last weekday 2026-10-30", CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date(2026, 10, 30)) == true, "");
   T_Bool("last weekday 2026-10-29", CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date(2026, 10, 29)) == false, "");
   T_Bool("last weekday 2026-01-30", CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date(2026, 1, 30)) == true, "");
   T_Bool("last weekday 2026-05-29", CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date(2026, 5, 29)) == true, "");
   T_Bool("last weekday 2026-05-31", CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date(2026, 5, 31)) == false, "");
   T_Bool("last weekday 2027-07-30", CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date(2027, 7, 30)) == true, "");
   T_Str("slot TOKYO_FIX 2026-11-04", SlotText(0, CSeesareDst::Date(2026, 11, 4)), "2026-11-04T23:00:00Z/2026-11-05T00:55:00Z");
   T_Str("slot TOKYO_FIX 2026-11-08", SlotText(0, CSeesareDst::Date(2026, 11, 8)), "none");
   T_Str("slot TOKYO_FIX 2026-11-09", SlotText(0, CSeesareDst::Date(2026, 11, 9)), "2026-11-09T23:00:00Z/2026-11-10T00:55:00Z");
   T_Str("slot TOKYO_FIX 2026-11-13", SlotText(0, CSeesareDst::Date(2026, 11, 13)), "none");
   T_Str("slot TOKYO_FIX 2026-11-29", SlotText(0, CSeesareDst::Date(2026, 11, 29)), "2026-11-29T23:00:00Z/2026-11-30T00:55:00Z");
   T_Str("slot TOKYO_FIX 2026-12-29", SlotText(0, CSeesareDst::Date(2026, 12, 29)), "2026-12-29T23:00:00Z/2026-12-30T00:55:00Z");
   T_Str("slot TOKYO_FIX 2026-12-30", SlotText(0, CSeesareDst::Date(2026, 12, 30)), "none");
   T_Str("slot TOKYO_FIX 2027-03-10", SlotText(0, CSeesareDst::Date(2027, 3, 10)), "none");
   T_Str("slot TOKYO_FIX 2027-03-30", SlotText(0, CSeesareDst::Date(2027, 3, 30)), "2027-03-30T23:00:00Z/2027-03-31T00:55:00Z");
   T_Str("slot TOKYO_FIX 2027-04-29", SlotText(0, CSeesareDst::Date(2027, 4, 29)), "2027-04-29T23:00:00Z/2027-04-30T00:55:00Z");
   T_Str("slot TOKYO_FIX 2027-10-27", SlotText(0, CSeesareDst::Date(2027, 10, 27)), "none");
   T_Str("slot TOKYO_FIX 2027-11-03", SlotText(0, CSeesareDst::Date(2027, 11, 3)), "none");
   T_Str("slot LDN_FIX 2026-11-04", SlotText(1, CSeesareDst::Date(2026, 11, 4)), "2026-11-04T15:55:00Z/2026-11-04T16:05:00Z");
   T_Str("slot LDN_FIX 2026-11-08", SlotText(1, CSeesareDst::Date(2026, 11, 8)), "none");
   T_Str("slot LDN_FIX 2026-11-09", SlotText(1, CSeesareDst::Date(2026, 11, 9)), "2026-11-09T15:55:00Z/2026-11-09T16:05:00Z");
   T_Str("slot LDN_FIX 2026-11-13", SlotText(1, CSeesareDst::Date(2026, 11, 13)), "2026-11-13T15:55:00Z/2026-11-13T16:05:00Z");
   T_Str("slot LDN_FIX 2026-11-29", SlotText(1, CSeesareDst::Date(2026, 11, 29)), "none");
   T_Str("slot LDN_FIX 2026-12-29", SlotText(1, CSeesareDst::Date(2026, 12, 29)), "2026-12-29T15:55:00Z/2026-12-29T16:05:00Z");
   T_Str("slot LDN_FIX 2026-12-30", SlotText(1, CSeesareDst::Date(2026, 12, 30)), "2026-12-30T15:55:00Z/2026-12-30T16:05:00Z");
   T_Str("slot LDN_FIX 2027-03-10", SlotText(1, CSeesareDst::Date(2027, 3, 10)), "2027-03-10T15:55:00Z/2027-03-10T16:05:00Z");
   T_Str("slot LDN_FIX 2027-03-30", SlotText(1, CSeesareDst::Date(2027, 3, 30)), "2027-03-30T14:55:00Z/2027-03-30T15:05:00Z");
   T_Str("slot LDN_FIX 2027-04-29", SlotText(1, CSeesareDst::Date(2027, 4, 29)), "2027-04-29T14:55:00Z/2027-04-29T15:05:00Z");
   T_Str("slot LDN_FIX 2027-10-27", SlotText(1, CSeesareDst::Date(2027, 10, 27)), "2027-10-27T14:55:00Z/2027-10-27T15:05:00Z");
   T_Str("slot LDN_FIX 2027-11-03", SlotText(1, CSeesareDst::Date(2027, 11, 3)), "2027-11-03T15:55:00Z/2027-11-03T16:05:00Z");
   T_Str("slot US_CLOSE 2026-11-04", SlotText(2, CSeesareDst::Date(2026, 11, 4)), "2026-11-04T20:50:00Z/2026-11-04T21:00:00Z");
   T_Str("slot US_CLOSE 2026-11-08", SlotText(2, CSeesareDst::Date(2026, 11, 8)), "none");
   T_Str("slot US_CLOSE 2026-11-09", SlotText(2, CSeesareDst::Date(2026, 11, 9)), "2026-11-09T20:50:00Z/2026-11-09T21:00:00Z");
   T_Str("slot US_CLOSE 2026-11-13", SlotText(2, CSeesareDst::Date(2026, 11, 13)), "2026-11-13T20:50:00Z/2026-11-13T21:00:00Z");
   T_Str("slot US_CLOSE 2026-11-29", SlotText(2, CSeesareDst::Date(2026, 11, 29)), "none");
   T_Str("slot US_CLOSE 2026-12-29", SlotText(2, CSeesareDst::Date(2026, 12, 29)), "2026-12-29T20:50:00Z/2026-12-29T21:00:00Z");
   T_Str("slot US_CLOSE 2026-12-30", SlotText(2, CSeesareDst::Date(2026, 12, 30)), "2026-12-30T20:50:00Z/2026-12-30T21:00:00Z");
   T_Str("slot US_CLOSE 2027-03-10", SlotText(2, CSeesareDst::Date(2027, 3, 10)), "2027-03-10T20:50:00Z/2027-03-10T21:00:00Z");
   T_Str("slot US_CLOSE 2027-03-30", SlotText(2, CSeesareDst::Date(2027, 3, 30)), "2027-03-30T19:50:00Z/2027-03-30T20:00:00Z");
   T_Str("slot US_CLOSE 2027-04-29", SlotText(2, CSeesareDst::Date(2027, 4, 29)), "2027-04-29T19:50:00Z/2027-04-29T20:00:00Z");
   T_Str("slot US_CLOSE 2027-10-27", SlotText(2, CSeesareDst::Date(2027, 10, 27)), "2027-10-27T19:50:00Z/2027-10-27T20:00:00Z");
   T_Str("slot US_CLOSE 2027-11-03", SlotText(2, CSeesareDst::Date(2027, 11, 3)), "2027-11-03T19:50:00Z/2027-11-03T20:00:00Z");
   T_Str("volume plan 0.1206 per lot 307.0", SizeText(0.1206, 307.0, 0.01, 0.01, 100.0), "shadow 0.00");
   T_Str("volume plan 1.368 per lot 307.0", SizeText(1.368, 307.0, 0.01, 0.01, 100.0), "shadow 0.00");
   T_Str("volume plan 2.052 per lot 307.0", SizeText(2.052, 307.0, 0.01, 0.01, 100.0), "shadow 0.00");
   T_Str("volume plan 1.368 per lot 107.0", SizeText(1.368, 107.0, 0.01, 0.01, 100.0), "feasible 0.01");
   T_Str("volume plan 1.368 per lot 57.0", SizeText(1.368, 57.0, 0.01, 0.01, 100.0), "feasible 0.02");
   T_Str("volume plan 0.03 per lot 1.0", SizeText(0.03, 1.0, 0.01, 0.01, 100.0), "feasible 0.03");
   T_Str("volume plan 0.0 per lot 107.0", SizeText(0.0, 107.0, 0.01, 0.01, 100.0), "shadow 0.00");
   T_Str("volume plan 5000.0 per lot 1.0", SizeText(5000.0, 1.0, 0.01, 0.01, 100.0), "feasible 100.00");
  }
//--- END GENERATED VECTORS

void HandWrittenTests(void)
  {
//--- evidence gates status
   CSeesareFlowModule *tokyo = MakeModule(0);
   CSeesareFlowModule *london = MakeModule(1);
   CSeesareFlowModule *usclose = MakeModule(2);
   bool allowed = tokyo.SetStatus(SEESARE_STATUS_LIVE);
   T_Bool("evidence: Tokyo fix (CANDIDATE) may run LIVE", allowed && tokyo.Status() == SEESARE_STATUS_LIVE, tokyo.LastError());
   bool refused = !london.SetStatus(SEESARE_STATUS_LIVE);
   T_Bool("evidence: London fix (REJECTED) is held to PAPER", refused && london.Status() == SEESARE_STATUS_PAPER, london.LastError());
   refused = !usclose.SetStatus(SEESARE_STATUS_LIVE);
   T_Bool("evidence: US close (UNTESTED) is held to PAPER", refused && usclose.Status() == SEESARE_STATUS_PAPER, usclose.LastError());
   T_Str("module ids", tokyo.Id() + "," + london.Id() + "," + usclose.Id(), "TOKYO_FIX,LDN_FIX_EURUSD,US_CLOSE_US500");
   T_Str("domains", tokyo.Domain() + "," + london.Domain() + "," + usclose.Domain(), "forex,forex,indices");
//--- SEESARE arithmetic at the Tokyo module's measured ratio
   double mult = CSeesareText::FloorDp(CSeesareLadder::Multiplier(StringToDouble(CSeesareText::Fmt(tokyo.DeclaredRatio(), 2))), 4);
   T_Str("Tokyo declared ratio", CSeesareText::Fmt(tokyo.DeclaredRatio(), 2), "1.04");
   T_Str("Tokyo multiplier at 1.04", CSeesareText::Fmt(mult, 4), "0.0882");
   T_Str("Tokyo planned delta at L0", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.144, mult, 0.05), 4), 4), "0.1206");
   T_Str("London declared ratio", CSeesareText::Fmt(london.DeclaredRatio(), 2), "5.00");
   T_Str("US close declared ratio", CSeesareText::Fmt(usclose.DeclaredRatio(), 2), "4.00");
   delete tokyo;
   delete london;
   delete usclose;
//--- the hardcoded time-exit rule
   T_Int("rule: a losing time exit is NEGATIVE", (long)CSeesareLadder::Classify(SEESARE_BY_TIME, -0.10, SEESARE_TIME_POLICY), -1);
   T_Int("rule: a winning time exit is MANUAL", (long)CSeesareLadder::Classify(SEESARE_BY_TIME, 0.10, SEESARE_TIME_POLICY), 0);
//--- US close feed lines
   datetime d = 0;
   int minute = -1;
   double net = 0.0;
   bool ok = CSeesareFlowUsClose::ParseFeedLine("2026-11-04,15:50,2500000000", d, minute, net);
   T_Bool("feed: a buy imbalance line", ok && d == CSeesareDst::Date(2026, 11, 4) && minute == 950 && net == 2500000000.0, "");
   ok = CSeesareFlowUsClose::ParseFeedLine("2026-11-04,15:51,-1750000000.5", d, minute, net);
   T_Bool("feed: a sell imbalance line", ok && minute == 951 && net == -1750000000.5, "");
   T_Bool("feed: two fields refused", !CSeesareFlowUsClose::ParseFeedLine("2026-11-04,15:50", d, minute, net), "");
   T_Bool("feed: month 13 refused", !CSeesareFlowUsClose::ParseFeedLine("2026-13-04,15:50,1", d, minute, net), "");
   T_Bool("feed: hour 25 refused", !CSeesareFlowUsClose::ParseFeedLine("2026-11-04,25:00,1", d, minute, net), "");
   T_Bool("feed: exponent notation refused", !CSeesareFlowUsClose::ParseFeedLine("2026-11-04,15:50,1e9", d, minute, net), "");
   T_Bool("feed: two decimal points refused", !CSeesareFlowUsClose::ParseFeedLine("2026-11-04,15:50,1.2.3", d, minute, net), "");
//--- paper book restart file
   string root = "seesare_selftest\\paper" + IntegerToString((long)TimeLocal());
   CSeesarePaperBook book;
   bool opened = book.Init(root, 1.0);
   T_Bool("paper: empty book opens", opened && book.Count() == 0, book.LastError());
   SSeesarePaper p;
   p.key = "TOKYO_FIX@2026-11-04T23:00:00Z";
   p.module_id = "TOKYO_FIX";
   p.symbol = "USDJPY";
   p.domain = "forex";
   p.live = true;
   p.side = 1;
   p.digits = 3;
   p.volume = 0.0004;
   p.entry = 151.234;
   p.lower = 150.78;
   p.upper = 151.706;
   p.stop = 150.78;
   p.target = 0.0;
   p.ratio = 1.04;
   p.loss_per_lot = 300.0;
   p.commission = 7.0;
   p.spread_points = 3.0;
   p.open_utc = CSeesareDst::Date(2026, 11, 4, 23, 0);
   p.exit_utc = CSeesareDst::Date(2026, 11, 5, 0, 55);
   p.last_msc = 0;
   opened = book.Open(p);
   T_Bool("paper: open a position", opened, book.LastError());
   T_Bool("paper: the same slot is refused", !book.Open(p), "");
   CSeesarePaperBook again;
   opened = again.Init(root, 1.0);
   T_Bool("paper: the position survives a restart", opened && again.Count() == 1 && again.Seen(p.key) && again.HasLive(),
          again.LastError());
   FileDelete(root + "\\paper\\open.dat", FILE_COMMON);
   FileDelete(root + "\\paper\\open.dat.bak", FILE_COMMON);
   FolderDelete(root + "\\paper", FILE_COMMON);
   FolderDelete(root, FILE_COMMON);
  }

//--- INFO only: what SEESARE sizing does with the Tokyo module on this terminal
void LiveSizingReport(void)
  {
   string sym = "USDJPY";
   MqlTick tick;
   if(!SymbolSelect(sym, true) || !SymbolInfoTick(sym, tick) || tick.ask <= 0.0)
     {
      Print("INFO  ", sym, " has no quote on this terminal: sizing report skipped");
      return;
     }
   double stop = tick.ask * (1.0 - SEESARE_TOKYO_STOP_PCT);
   double units = CSeesareExposure::AccountUnitsPerUsd();
   double loss = 0.0;
   if(!CSeesareExposure::LossPerLot(sym, 1, tick.ask, stop, units, loss))
     {
      Print("INFO  cannot price the stop for ", sym, " (account currency ", AccountInfoString(ACCOUNT_CURRENCY),
            ": only USD and US cents are converted)");
      return;
     }
   double mult = CSeesareText::FloorDp(CSeesareLadder::Multiplier(SEESARE_TOKYO_RATIO), 4);
   double plan = CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.144, mult, 0.05), 4);
   double virtual_volume = 0.0;
   bool feasible = false;
   double vol = CSeesareExposure::Volume(plan, loss + 7.0, SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP),
                                         SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN), SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX),
                                         virtual_volume, feasible);
   string verdict = "SHADOW only";
   if(feasible)
      verdict = "REAL feasible";
   Print("INFO  Tokyo fix on this terminal: the 0.3% stop loses ", DoubleToString(loss, 2), " USD per lot; SEESARE plan at L0 ",
         DoubleToString(plan, 4), " USD buys ", DoubleToString(virtual_volume, 5), " lots (broker minimum ",
         DoubleToString(SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN), 2), "): ", verdict, " (volume ", DoubleToString(vol, 2), ")");
  }

void OnStart()
  {
   Print("SEESARE Phase 2 self-test: start");
   GeneratedVectors();
   HandWrittenTests();
   LiveSizingReport();
   Print("SEESARE Phase 2 self-test: ", g_pass, " passed, ", g_fail, " failed");
   if(g_fail > 0)
      Alert("SEESARE Phase 2 self-test: ", g_fail, " check(s) FAILED - see the Experts tab");
  }
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//|                                       SeesarePhase3SelfTest.mq5  |
//| SEESARE router, Phase 3 self-test. UNCOMPILED SOURCE.            |
//|                                                                  |
//| Checks the Telegram texts line by line, the outbox body hashes,  |
//| a written outbox file byte for byte (through its checksum), the  |
//| cent-account level tables and lowest real level, account money  |
//| per USD, the broker deal reasons, ticket lists, and one closed   |
//| cent-account position going deals -> ledger -> outbox message.   |
//| Expected values come from tools/seesare_outbox.py (--mql);       |
//| research/truth/tests/test_seesare_phase3.py fails if this block  |
//| and the twin drift apart. INFO lines (not counted) size the      |
//| Tokyo module on this terminal's account and symbol.              |
//+------------------------------------------------------------------+
#property copyright   "T.citybank"
#property version     "3.00"
#property description "SEESARE Phase 3 self-test: Telegram outbox, cent-account sizing, deal reader"
#property script_show_inputs

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Ledger\CycleLedger.mqh>
#include <Seesare\Ledger\Telegram.mqh>
#include <Seesare\Ledger\Outbox.mqh>
#include <Seesare\Risk\Exposure.mqh>
#include <Seesare\Exec\DealReader.mqh>
#include <Seesare\Flows\FlowTokyoFix.mqh>

input string InpSymbol        = "USDJPY";   // symbol for the INFO sizing report
input double InpCommissionLot = 0.0;        // commission per lot of this broker's contract, round trip, USD (RoboForex ProCent: 0)
input bool   InpKeepFiles     = false;      // keep the test folders in Common\Files\seesare_selftest

int    g_pass = 0;
int    g_fail = 0;
string g_root = "";

//+------------------------------------------------------------------+
//| Test helpers                                                     |
//+------------------------------------------------------------------+
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

int LineCount(const string text)
  {
   string parts[];
   return StringSplit(text, '\n', parts);
  }

string Line(const string text, const int i)
  {
   string parts[];
   int n = StringSplit(text, '\n', parts);
   if(i < 0 || i >= n)
      return "";
   return parts[i];
  }

string RecordLine(const string record)
  {
   string s = "Record: ";
   s += record;
   return s;
  }

//--- "L0 plan vol real|L1 ..." for the drawdown-keyed ladder (twin: level_table + table_text)
string LevelTableFor(const double weight, const double per_lot, const double step, const double vmin)
  {
   string s = "";
   for(int lv = 0; lv < SEESARE_LEVELS; lv++)
     {
      double plan = CSeesareExposure::PlanAtLevel(lv, weight);
      double virtual_volume = 0.0;
      bool ok = false;
      double vol = CSeesareExposure::Volume(plan, per_lot, step, vmin, DBL_MAX, virtual_volume, ok);
      string verdict = "shadow";
      if(ok)
         verdict = "real";
      if(s != "")
         s += "|";
      s += "L" + IntegerToString(lv) + " " + CSeesareText::Fmt(plan, 4) + " " + CSeesareText::Fmt(vol, 2) + " " + verdict;
     }
   return s;
  }

string LevelTable(const double weight, const double per_lot)
  {
   return LevelTableFor(weight, per_lot, 0.01, 0.01);
  }

void DeleteTree(const string folder)
  {
   string names[];
   int n = 0;
   string name = "";
   long h = FileFindFirst(folder + "\\*", name, FILE_COMMON);
   if(h != INVALID_HANDLE)
     {
      do
        {
         ArrayResize(names, n + 1, 64);
         names[n] = name;
         n++;
        }
      while(FileFindNext(h, name));
      FileFindClose(h);
     }
   for(int i = 0; i < n; i++)
     {
      int len = StringLen(names[i]);
      if(len > 0 && StringGetCharacter(names[i], len - 1) == '\\')
         DeleteTree(folder + "\\" + StringSubstr(names[i], 0, len - 1));
      else
         FileDelete(folder + "\\" + names[i], FILE_COMMON);
     }
   FolderDelete(folder, FILE_COMMON);
  }

//+------------------------------------------------------------------+
//| GENERATED: do not edit between the markers                       |
//+------------------------------------------------------------------+
//--- BEGIN GENERATED VECTORS: python3 tools/seesare_outbox.py --mql  (do not edit by hand)
#define VEC3_GENESIS "v=2|life=SELFTEST|k=0|genesis|baseline=1000.00|events=360|cycle_size=10|envelope_pct=3.60|sizing=DRAWDOWN_KEYED|levels=16|band=2.2500|room_mult=0.30|max_weight=1.00|time_policy=GAIN_POSITIVE_LOSS_NEGATIVE|created=2026-11-01T00:00:00Z|hash=fe81fd4ca90826a7fa1be44cff1bd7d0924db16e4cd44d8b80efd0cf0c39f998"
#define VEC3_EVENT_REAL "v=2|life=SELFTEST|k=1|mode=REAL|n=1|cycle=1|step=1|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=BUY|open=2026-11-04T23:00:00Z|close=2026-11-05T00:55:00Z|by=TIME|res=POSITIVE|dd=0.0000|lvl_before=0|lvl_after=0|weight=1.00|plan=10.1250|risk=3.0000|vol=0.3000|entry=151.234|lower=151.084|upper=151.759|exit=151.311|delta=0.4321|deals=50001000;50001001|prev=fe81fd4ca90826a7fa1be44cff1bd7d0924db16e4cd44d8b80efd0cf0c39f998|hash=760a97cb414b48574b51c8d538c5661f7467500473cc4b8105bd972ca65b2370"
#define VEC3_EVENT_SHADOW "v=2|life=SELFTEST|k=3|mode=SHADOW|n=2|cycle=1|step=-|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=SELL|open=2026-11-06T23:00:00Z|close=2026-11-07T00:55:00Z|by=TARGET|res=POSITIVE|dd=3.0000|lvl_before=1|lvl_after=1|weight=1.00|plan=9.4500|risk=0.0000|vol=0.0059|entry=151.234|lower=150.709|upper=151.384|exit=150.709|delta=2.0615|deals=-|prev=a7ef6e49d40cb0d2da7066f88710a5f3dece7e27e2a908483b64664afc449340|hash=efe27e3ed694409a927b2e080dc470e0b565a702146a0be6d36ba3c71ef42eaf"
#define VEC3_ANCHOR "v=2|life=SELFTEST|audit=cycle|cycle=1|events=1-10|pos=6|neg=4|man=0|shadow=7|pos_rate=0.6000|net=-1.4909|net_pct=-0.14909|max_dd=5.8830|max_dd_pct=0.58830|life_net=-1.4909|life_dd=5.8830|lvl_start=0|lvl_end=0|root=23d1bd36de446af1ea172266c805d4c2e7f5573efb024908c5cf19cee2a73de1|head=ee2410b803555886c71439d3e51adb1ac3f10b4033d79de9df2d0f342bc4c19c|prev=fe81fd4ca90826a7fa1be44cff1bd7d0924db16e4cd44d8b80efd0cf0c39f998|hash=76d652e5888211a531a8f7c66783e6b53a15230e6e7c0f7181e25f1c4753e40c"
#define VEC3_LIFECYCLE "v=1|life=SELFTEST_LOCK|audit=lifecycle|events=360|cycles=36|shadow=0|pos=240|neg=120|man=0|net=12.0000|net_pct=1.20000|max_dd=0.4000|max_dd_pct=0.04000|violations=0|head=e4d3b560989f48640e6f3a523e58cff8d7fb4357a6b50a6b1099fbd4010ba252"
#define VEC3_OUTBOX_LINES 18
#define VEC3_OUTBOX_SUM "sum=8a6cb657bd2d5ba3ced97cd079a69288d496f37786b5cdace8d7fd6a8b508c08"
#define VEC3_CENT_RECORD "v=2|life=P3SELFTEST|k=1|mode=REAL|n=1|cycle=1|step=1|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=BUY|open=2026-11-04T23:00:00Z|close=2026-11-05T00:55:00Z|by=TIME|res=POSITIVE|dd=0.0000|lvl_before=0|lvl_after=0|weight=0.57|plan=5.7712|risk=0.1200|vol=0.0400|entry=151.234|lower=150.780|upper=151.706|exit=151.311|delta=0.3080|deals=50001000;50001001|prev=116ab7341644257d7fe41bdacceccd43d23a225b327b2626060e68f462960269|hash=9f59366f033fe8ee0c6359215606e3c59575778b9a58910cbcc570c98ab2b6de"
#define VEC3_CENT_LINES 18
#define VEC3_CENT_HEAD "SEESARE P26 | P3SELFTEST | Cycle 1/36 | Step 1/10 | REAL"
#define VEC3_CENT_RESULT "Result POSITIVE | +0.3080 USD | level L0 -> L0 | drawdown before 0.0000 USD"
#define VEC3_CENT_DEALS "Deals 50001000, 50001001"
#define VEC3_CENT_SUM "sum=3a877ba89f995b6fda8f2fd6d112023a4546377dd49604d09de40283fb3497e4"
void GeneratedVectors(void)
  {
   T_Int("telegram genesis: lines", LineCount(CSeesareTelegram::Genesis(VEC3_GENESIS)), 5);
   T_Str("telegram genesis: line 1", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 0), "SEESARE P26 | SELFTEST | lifecycle opened 2026-11-01T00:00:00Z");
   T_Str("telegram genesis: line 2", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 1), "Baseline 1000.00 USD | 360 events in cycles of 10 | envelope 3.60%");
   T_Str("telegram genesis: line 3", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 2), "Sizing DRAWDOWN_KEYED: 16 levels of 2.2500 USD drawdown | risk = 0.30 x weight x room left | weight <= 1.00");
   T_Str("telegram genesis: line 4", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 3), "Time exits GAIN_POSITIVE_LOSS_NEGATIVE");
   T_Str("telegram genesis: line 5", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 4), "Genesis hash fe81fd4ca90826a7fa1be44cff1bd7d0924db16e4cd44d8b80efd0cf0c39f998");
   T_Int("telegram real event: lines", LineCount(CSeesareTelegram::Event(VEC3_EVENT_REAL)), 9);
   T_Str("telegram real event: line 1", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 0), "SEESARE P26 | SELFTEST | Cycle 1/36 | Step 1/10 | REAL");
   T_Str("telegram real event: line 2", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 1), "TOKYO_FIX USDJPY BUY");
   T_Str("telegram real event: line 3", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 2), "Open 2026-11-04T23:00:00Z | Close 2026-11-05T00:55:00Z | by TIME");
   T_Str("telegram real event: line 4", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 3), "Result POSITIVE | +0.4321 USD | level L0 -> L0 | drawdown before 0.0000 USD");
   T_Str("telegram real event: line 5", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 4), "Entry 151.234 | Lower 151.084 | Upper 151.759 | Exit 151.311");
   T_Str("telegram real event: line 6", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 5), "Weight 1.00 | planned 10.1250 USD | risk 3.0000 USD | volume 0.3000");
   T_Str("telegram real event: line 7", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 6), "Deals 50001000, 50001001");
   T_Str("telegram real event: line 8", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 7), "Chain k=1 | hash 760a97cb414b48574b51c8d538c5661f7467500473cc4b8105bd972ca65b2370");
   T_Str("telegram real event: line 9", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 8), "Prev fe81fd4ca90826a7fa1be44cff1bd7d0924db16e4cd44d8b80efd0cf0c39f998");
   T_Int("telegram shadow event: lines", LineCount(CSeesareTelegram::Event(VEC3_EVENT_SHADOW)), 9);
   T_Str("telegram shadow event: line 1", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 0), "SEESARE P26 | SELFTEST | Cycle 1/36 | SHADOW (paper, not counted)");
   T_Str("telegram shadow event: line 2", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 1), "TOKYO_FIX USDJPY SELL");
   T_Str("telegram shadow event: line 3", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 2), "Open 2026-11-06T23:00:00Z | Close 2026-11-07T00:55:00Z | by TARGET");
   T_Str("telegram shadow event: line 4", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 3), "Result POSITIVE | +2.0615 USD | level L1 -> L1 | drawdown before 3.0000 USD");
   T_Str("telegram shadow event: line 5", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 4), "Entry 151.234 | Lower 150.709 | Upper 151.384 | Exit 150.709");
   T_Str("telegram shadow event: line 6", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 5), "Weight 1.00 | planned 9.4500 USD | risk 0.0000 USD | volume 0.0059");
   T_Str("telegram shadow event: line 7", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 6), "Deals none (paper)");
   T_Str("telegram shadow event: line 8", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 7), "Chain k=3 | hash efe27e3ed694409a927b2e080dc470e0b565a702146a0be6d36ba3c71ef42eaf");
   T_Str("telegram shadow event: line 9", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 8), "Prev a7ef6e49d40cb0d2da7066f88710a5f3dece7e27e2a908483b64664afc449340");
   T_Int("telegram cycle audit: lines", LineCount(CSeesareTelegram::Audit(VEC3_ANCHOR)), 8);
   T_Str("telegram cycle audit: line 1", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 0), "SEESARE P26 | SELFTEST | Cycle 1/36 closed | events 1-10");
   T_Str("telegram cycle audit: line 2", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 1), "Positive 6 | negative 4 | manual 0 | shadow 7 | positive rate 0.6000");
   T_Str("telegram cycle audit: line 3", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 2), "Cycle net -1.4909 USD (-0.14909%) | cycle max drawdown 5.8830 USD (0.58830%)");
   T_Str("telegram cycle audit: line 4", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 3), "Lifecycle net -1.4909 USD | lifecycle max drawdown 5.8830 USD");
   T_Str("telegram cycle audit: line 5", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 4), "Level L0 -> L0");
   T_Str("telegram cycle audit: line 6", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 5), "Block root 23d1bd36de446af1ea172266c805d4c2e7f5573efb024908c5cf19cee2a73de1");
   T_Str("telegram cycle audit: line 7", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 6), "Chain head ee2410b803555886c71439d3e51adb1ac3f10b4033d79de9df2d0f342bc4c19c");
   T_Str("telegram cycle audit: line 8", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 7), "Anchor 76d652e5888211a531a8f7c66783e6b53a15230e6e7c0f7181e25f1c4753e40c");
   T_Int("telegram lifecycle: lines", LineCount(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE)), 4);
   T_Str("telegram lifecycle: line 1", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 0), "SEESARE P26 | SELFTEST_LOCK | lifecycle complete: 360 events in 36 cycles");
   T_Str("telegram lifecycle: line 2", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 1), "Positive 240 | negative 120 | manual 0 | shadow 0");
   T_Str("telegram lifecycle: line 3", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 2), "Net +12.0000 USD (+1.20000%) | max drawdown 0.4000 USD (0.04000%) | envelope violations 0");
   T_Str("telegram lifecycle: line 4", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 3), "Final head e4d3b560989f48640e6f3a523e58cff8d7fb4357a6b50a6b1099fbd4010ba252");
   T_Str("outbox body genesis: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("GENESIS", VEC3_GENESIS)), "65b3ee026954e51d2f7ad834cd0ac8ea690c58f94c1bc9fdf7c05577a5bd6a7b");
   T_Int("outbox body genesis: length", StringLen(CSeesareTelegram::Body("GENESIS", VEC3_GENESIS)), 666);
   T_Str("outbox body genesis: record line", Line(CSeesareTelegram::Body("GENESIS", VEC3_GENESIS), 5), RecordLine(VEC3_GENESIS));
   T_Str("outbox body event_real: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("EVENT", VEC3_EVENT_REAL)), "4c8d30341c6d12e2d97234dc9ae330642dd98c19e7d193b6004982e6796d5a91");
   T_Int("outbox body event_real: length", StringLen(CSeesareTelegram::Body("EVENT", VEC3_EVENT_REAL)), 1023);
   T_Str("outbox body event_real: record line", Line(CSeesareTelegram::Body("EVENT", VEC3_EVENT_REAL), 9), RecordLine(VEC3_EVENT_REAL));
   T_Str("outbox body event_shadow: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("EVENT", VEC3_EVENT_SHADOW)), "4380257f06e03ea4c8f3a27ef3d05c88fefd6e16131ee13b29d98998efe5285a");
   T_Int("outbox body event_shadow: length", StringLen(CSeesareTelegram::Body("EVENT", VEC3_EVENT_SHADOW)), 1018);
   T_Str("outbox body event_shadow: record line", Line(CSeesareTelegram::Body("EVENT", VEC3_EVENT_SHADOW), 9), RecordLine(VEC3_EVENT_SHADOW));
   T_Str("outbox body anchor: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("AUDIT", VEC3_ANCHOR)), "70355eed60c02f923ee924a37cd92ea7f12adc236dfd1aa8cf333cbade271517");
   T_Int("outbox body anchor: length", StringLen(CSeesareTelegram::Body("AUDIT", VEC3_ANCHOR)), 1000);
   T_Str("outbox body anchor: record line", Line(CSeesareTelegram::Body("AUDIT", VEC3_ANCHOR), 8), RecordLine(VEC3_ANCHOR));
   T_Str("outbox body lifecycle: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("LIFECYCLE", VEC3_LIFECYCLE)), "92996612b17694a2d1909865b7782c9f420e7f3b9f215225ddb703e7a8256dcd");
   T_Int("outbox body lifecycle: length", StringLen(CSeesareTelegram::Body("LIFECYCLE", VEC3_LIFECYCLE)), 532);
   T_Str("outbox body lifecycle: record line", Line(CSeesareTelegram::Body("LIFECYCLE", VEC3_LIFECYCLE), 4), RecordLine(VEC3_LIFECYCLE));
   T_Str("outbox body for a malformed record", CSeesareTelegram::Body("EVENT", "v=1||k=2"), "");
   T_Str("outbox body for an unknown kind", CSeesareTelegram::Body("NOTE", VEC3_EVENT_REAL), "");
   T_Str("signed '0.4321'", CSeesareTelegram::Signed("0.4321"), "+0.4321");
   T_Str("signed '-0.0592'", CSeesareTelegram::Signed("-0.0592"), "-0.0592");
   T_Str("signed '0.0000'", CSeesareTelegram::Signed("0.0000"), "0.0000");
   T_Str("signed '0.00000'", CSeesareTelegram::Signed("0.00000"), "0.00000");
   T_Str("signed '12.0000'", CSeesareTelegram::Signed("12.0000"), "+12.0000");
   T_Str("signed ''", CSeesareTelegram::Signed(""), "");
   T_Str("levels cent USDJPY 0.3% stop, weight 0.57", LevelTable(0.57, 3.0), "L0 5.7712 1.92 real|L1 5.3865 1.79 real|L2 5.0017 1.66 real|L3 4.6170 1.53 real|L4 4.2322 1.41 real|L5 3.8475 1.28 real|L6 3.4627 1.15 real|L7 3.0780 1.02 real|L8 2.6932 0.89 real|L9 2.3085 0.76 real|L10 1.9237 0.64 real|L11 1.5390 0.51 real|L12 1.1542 0.38 real|L13 0.7695 0.25 real|L14 0.3847 0.12 real|L15 0.0000 0.00 shadow");
   T_Int("lowest feasible level cent USDJPY 0.3% stop, weight 0.57", CSeesareExposure::LowestFeasibleLevel(0.57, 3.0, 0.01, 0.01), 14);
   T_Str("levels cent USDJPY 0.3% stop, weight 1.00", LevelTable(1.0, 3.0), "L0 10.1250 3.37 real|L1 9.4500 3.15 real|L2 8.7750 2.92 real|L3 8.1000 2.70 real|L4 7.4250 2.47 real|L5 6.7500 2.25 real|L6 6.0750 2.02 real|L7 5.4000 1.80 real|L8 4.7250 1.57 real|L9 4.0500 1.35 real|L10 3.3750 1.12 real|L11 2.7000 0.90 real|L12 2.0250 0.67 real|L13 1.3500 0.45 real|L14 0.6750 0.22 real|L15 0.0000 0.00 shadow");
   T_Int("lowest feasible level cent USDJPY 0.3% stop, weight 1.00", CSeesareExposure::LowestFeasibleLevel(1.0, 3.0, 0.01, 0.01), 14);
   T_Str("levels standard USDJPY 0.3% stop, weight 0.57", LevelTable(0.57, 300.0), "L0 5.7712 0.01 real|L1 5.3865 0.01 real|L2 5.0017 0.01 real|L3 4.6170 0.01 real|L4 4.2322 0.01 real|L5 3.8475 0.01 real|L6 3.4627 0.01 real|L7 3.0780 0.01 real|L8 2.6932 0.00 shadow|L9 2.3085 0.00 shadow|L10 1.9237 0.00 shadow|L11 1.5390 0.00 shadow|L12 1.1542 0.00 shadow|L13 0.7695 0.00 shadow|L14 0.3847 0.00 shadow|L15 0.0000 0.00 shadow");
   T_Int("lowest feasible level standard USDJPY 0.3% stop, weight 0.57", CSeesareExposure::LowestFeasibleLevel(0.57, 300.0, 0.01, 0.01), 7);
   T_Str("levels cent EURUSD 10-pip stop, weight 0.25", LevelTable(0.25, 1.0), "L0 2.5312 2.53 real|L1 2.3625 2.36 real|L2 2.1937 2.19 real|L3 2.0250 2.02 real|L4 1.8562 1.85 real|L5 1.6875 1.68 real|L6 1.5187 1.51 real|L7 1.3500 1.35 real|L8 1.1812 1.18 real|L9 1.0125 1.01 real|L10 0.8437 0.84 real|L11 0.6750 0.67 real|L12 0.5062 0.50 real|L13 0.3375 0.33 real|L14 0.1687 0.16 real|L15 0.0000 0.00 shadow");
   T_Int("lowest feasible level cent EURUSD 10-pip stop, weight 0.25", CSeesareExposure::LowestFeasibleLevel(0.25, 1.0, 0.01, 0.01), 14);
   T_Str("money units per USD for [USD]", CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd("USD"), 1), "1.0");
   T_Str("money units per USD for [USC]", CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd("USC"), 1), "100.0");
   T_Str("money units per USD for [usc]", CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd("usc"), 1), "100.0");
   T_Str("money units per USD for [ USC ]", CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd(" USC "), 1), "100.0");
   T_Str("money units per USD for [EUR]", CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd("EUR"), 1), "0.0");
   T_Str("money units per USD for []", CSeesareText::Fmt(CSeesareExposure::UnitsPerUsd(""), 1), "0.0");
   T_Str("deal reason DEAL_REASON_SL", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_SL)), "STOP");
   T_Str("deal reason DEAL_REASON_TP", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_TP)), "TARGET");
   T_Str("deal reason DEAL_REASON_SO", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_SO)), "BROKER");
   T_Str("deal reason DEAL_REASON_EXPERT", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_EXPERT)), "TIME");
   T_Str("deal reason DEAL_REASON_CLIENT", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_CLIENT)), "HUMAN");
   T_Str("deal reason DEAL_REASON_MOBILE", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_MOBILE)), "HUMAN");
   T_Str("deal reason DEAL_REASON_WEB", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_WEB)), "HUMAN");
   T_Str("deal reason DEAL_REASON_ROLLOVER", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_ROLLOVER)), "BROKER");
   T_Str("deal reason DEAL_REASON_VMARGIN", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_VMARGIN)), "BROKER");
   T_Str("deal reason DEAL_REASON_SPLIT", CSeesareLadder::CloseName(CSeesareDealReader::CloseFromReason(DEAL_REASON_SPLIT)), "BROKER");
  }
//--- END GENERATED VECTORS

//+------------------------------------------------------------------+
//| An outbox message written to disk equals the twin's, byte for    |
//| byte (its sum= line is the SHA-256 of everything above it)       |
//+------------------------------------------------------------------+
void OutboxFileTests(void)
  {
   string dir = g_root + "\\outbox";
   CSeesareOutbox ob;
   ob.Init(dir, 0);
   bool pushed = ob.Push("EVENT", "SELFTEST", 1, CSeesareDst::Date(2026, 11, 5, 0, 55), VEC3_EVENT_REAL);
   T_Bool("outbox file: written", pushed, ob.LastError());
   string msg[];
   int n = CSeesareFiles::ReadLines(dir + "\\0000000001.msg", msg);
   T_Int("outbox file: lines", n, VEC3_OUTBOX_LINES);
   T_Str("outbox file: format line", (n > 0 ? msg[0] : ""), SEESARE_OUTBOX_FORMAT);
   T_Str("outbox file: checksum equals the twin's", (n > 0 ? msg[n - 1] : ""), VEC3_OUTBOX_SUM);
   T_Str("outbox file: record line", (n > 1 ? msg[n - 2] : ""), RecordLine(VEC3_EVENT_REAL));
   string body = "";
   for(int i = 0; i < n - 1; i++)
      body += msg[i] + "\n";
   T_Str("outbox file: checksum recomputed here", (n > 0 ? msg[n - 1] : ""), "sum=" + CSeesareSha256::Hex(body));
   bool refused = !ob.Push("EVENT", "SELFTEST", 2, CSeesareDst::Date(2026, 11, 5, 0, 55), "v=1||k=2");
   long seq_after = ob.LastSeq();
   T_Bool("outbox file: a malformed record is refused and uses no number", refused && seq_after == 1, ob.LastError());
   T_Bool("outbox file: nothing written for it", !CSeesareFiles::Exists(dir + "\\0000000002.msg"), "");
  }

//+------------------------------------------------------------------+
//| Cent account, end to end: two broker deals -> REAL event ->      |
//| ledger line -> outbox message 2 (heading, result, deals, sum)    |
//+------------------------------------------------------------------+
void CentEndToEndTests(void)
  {
   T_Str("tickets: first", CSeesareDealReader::AppendTicket("", 50001000), "50001000");
   T_Str("tickets: second", CSeesareDealReader::AppendTicket("50001000", 50001001), "50001000;50001001");
   T_Str("cents to dollars: 30.8 USC", CSeesareText::Fmt(CSeesareDealReader::NetUsd(30.8, 100.0), 4), "0.3080");
   T_Str("cents to dollars: unknown currency gives 0", CSeesareText::Fmt(CSeesareDealReader::NetUsd(30.8, 0.0), 4), "0.0000");
//--- what FromPosition would return for a closed 0.04-lot cent position (deal history is not needed for the arithmetic)
   SSeesareDealSummary d;
   d.Clear();
   d.position_id = 50001000;
   d.closed      = true;
   d.count       = 2;
   d.deals       = CSeesareDealReader::AppendTicket(CSeesareDealReader::AppendTicket("", 50001000), 50001001);
   d.symbol      = "USDJPY";
   d.side        = 1;
   d.volume_in   = 0.04;
   d.volume_out  = 0.04;
   d.entry_price = 151.234;
   d.exit_price  = 151.311;
   d.open_utc    = CSeesareDst::Date(2026, 11, 4, 23, 0);
   d.close_utc   = CSeesareDst::Date(2026, 11, 5, 0, 55);
   d.close_by    = CSeesareDealReader::CloseFromReason(DEAL_REASON_EXPERT);
   d.money       = 30.8;
   d.net_usd     = CSeesareDealReader::NetUsd(d.money, 100.0);
   SSeesareEvent e;
   bool made = CSeesareDealReader::ToEvent(d, "TOKYO_FIX", "forex", 3, 0.57, 0.12, 150.780, 151.706, e);
   T_Bool("deal reader: a closed position becomes a REAL event", made && e.mode == SEESARE_REAL && e.deals == "50001000;50001001", "");
   SSeesareDealSummary still;
   still.Clear();
   still.closed = false;
   still.count = 1;
   still.side = 1;
   SSeesareEvent e2;
   T_Bool("deal reader: an open position is not an event", !CSeesareDealReader::ToEvent(still, "TOKYO_FIX", "forex", 3, 0.57, 0.12,
          150.780, 151.706, e2), "");
//--- through a fresh ledger
   CSeesareCycleLedger L;
   bool opened = L.Open(g_root, "P3SELFTEST", CSeesareDst::Date(2026, 11, 1), false);
   T_Bool("ledger: open a lifecycle", opened, L.LastError());
   if(!opened || !made)
      return;
   string h = "";
   bool recorded = L.Record(e, h);
   T_Bool("ledger: records the event read from the deals", recorded, L.LastError());
   if(!recorded)
      return;
   T_Str("ledger: line equals the twin's", L.LineAt(1), VEC3_CENT_RECORD);
   string msg[];
   int n = CSeesareFiles::ReadLines(L.Dir() + "\\outbox\\0000000002.msg", msg);
   T_Int("outbox: message 2 lines", n, VEC3_CENT_LINES);
   T_Str("outbox: heading carries Cycle X/36 and Step Y/10", (n > 7 ? msg[7] : ""), VEC3_CENT_HEAD);
   T_Str("outbox: result in USD from US cents", (n > 10 ? msg[10] : ""), VEC3_CENT_RESULT);
   T_Str("outbox: broker deal tickets", (n > 13 ? msg[13] : ""), VEC3_CENT_DEALS);
   T_Str("outbox: message 2 equals the twin's (checksum)", (n > 0 ? msg[n - 1] : ""), VEC3_CENT_SUM);
  }

//+------------------------------------------------------------------+
//| INFO only: the cent-account sizer on this terminal               |
//+------------------------------------------------------------------+
void LiveSizingReport(void)
  {
   string cur = AccountInfoString(ACCOUNT_CURRENCY);
   double units = CSeesareExposure::UnitsPerUsd(cur);
   if(units <= 0.0)
     {
      Print("INFO  account currency ", cur, " is neither USD nor US cents: the router needs InpUnitsPerUsd set by hand");
      return;
     }
   Print("INFO  account currency ", cur, ": ", CSeesareText::Fmt(units, 0), " account units per USD");
   MqlTick tick;
   if(!SymbolSelect(InpSymbol, true) || !SymbolInfoTick(InpSymbol, tick) || tick.ask <= 0.0)
     {
      Print("INFO  ", InpSymbol, " has no quote on this terminal: sizing report skipped");
      return;
     }
   double stop = tick.ask * (1.0 - SEESARE_TOKYO_STOP_PCT);
   double loss = 0.0;
   if(!CSeesareExposure::LossPerLot(InpSymbol, 1, tick.ask, stop, units, loss))
     {
      Print("INFO  OrderCalcProfit failed for ", InpSymbol);
      return;
     }
   double per_lot = loss + InpCommissionLot;
   double step = SymbolInfoDouble(InpSymbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(InpSymbol, SYMBOL_VOLUME_MIN);
   Print("INFO  ", InpSymbol, ": contract ", DoubleToString(SymbolInfoDouble(InpSymbol, SYMBOL_TRADE_CONTRACT_SIZE), 0),
         " units per lot, minimum ", DoubleToString(vmin, 2), " lot, step ", DoubleToString(step, 2),
         "; a 0.3% stop costs ", DoubleToString(per_lot, 4), " USD per lot including commission");
   double weights[2];
   weights[0] = SEESARE_TOKYO_WEIGHT;
   weights[1] = 1.0;
   for(int i = 0; i < 2; i++)
     {
      int lowest = CSeesareExposure::LowestFeasibleLevel(weights[i], per_lot, step, vmin);
      string where = "no level can trade REAL (all SHADOW)";
      if(lowest >= 0)
         where = "REAL from L0 down to L" + IntegerToString(lowest) + ", SHADOW below";
      Print("INFO  weight ", DoubleToString(weights[i], 2), ": ", where);
      Print("INFO    ", LevelTableFor(weights[i], per_lot, step, vmin));
     }
  }

void OnStart()
  {
   g_root = "seesare_selftest\\p3run" + IntegerToString((long)TimeLocal()) + "_" + IntegerToString(GetTickCount() % 100000);
   Print("SEESARE Phase 3 self-test: start (files under Common\\Files\\", g_root, ")");
   GeneratedVectors();
   OutboxFileTests();
   CentEndToEndTests();
   if(!InpKeepFiles)
     {
      DeleteTree(g_root);
      FolderDelete("seesare_selftest", FILE_COMMON);
     }
   LiveSizingReport();
   Print("SEESARE Phase 3 self-test: ", g_pass, " passed, ", g_fail, " failed");
   if(g_fail > 0)
      Alert("SEESARE Phase 3 self-test: ", g_fail, " check(s) FAILED - see the Experts tab");
  }
//+------------------------------------------------------------------+

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

//--- "L0 plan vol real|L1 ..." for the default ladder (twin: level_table + table_text)
string LevelTableFor(const double ratio, const double per_lot, const double step, const double vmin)
  {
   double pct[];
   CSeesareLadder::Defaults(pct);
   string s = "";
   for(int lv = 0; lv < ArraySize(pct); lv++)
     {
      double plan = CSeesareExposure::PlanAtLevel(pct[lv], ratio, 0.05);
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

string LevelTable(const double ratio, const double per_lot)
  {
   return LevelTableFor(ratio, per_lot, 0.01, 0.01);
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
#define VEC3_GENESIS "v=1|life=SELFTEST|k=0|genesis|baseline=1000.00|events=360|cycle_size=10|envelope_pct=3.60|exponent=2.00|time_policy=LOSS_NEGATIVE|ladder=0.1440,0.0950,0.0620,0.0410,0.0270,0.0180,0.0120,0.0080,0.0050,0.0033,0.0022,0.0014,0.0009,0.0006,0.0004,0.0003|created=2026-11-01T00:00:00Z|hash=01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1"
#define VEC3_EVENT_REAL "v=1|life=SELFTEST|k=1|mode=REAL|n=1|cycle=1|step=1|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=BUY|open=2026-11-04T23:00:00Z|close=2026-11-05T00:55:00Z|by=TIME|res=MANUAL|lvl_before=0|lvl_after=0|neg_run=0|ratio=3.50|mult=1.0000|fric=0.0500|plan=1.3680|risk=1.0600|vol=0.0100|entry=151.234|lower=151.084|upper=151.759|exit=151.311|delta=0.4321|deals=50001000;50001001|prev=01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1|hash=c873280ea8ea9218aa4f72434e15a77d9d0e3109d08c127b073453a0fb1668ed"
#define VEC3_EVENT_SHADOW "v=1|life=SELFTEST|k=3|mode=SHADOW|n=2|cycle=1|step=-|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=SELL|open=2026-11-06T23:00:00Z|close=2026-11-07T00:55:00Z|by=TARGET|res=POSITIVE|lvl_before=2|lvl_after=1|neg_run=0|ratio=3.50|mult=1.0000|fric=0.0500|plan=0.5890|risk=0.0000|vol=0.0059|entry=151.234|lower=150.709|upper=151.384|exit=150.709|delta=2.0615|deals=-|prev=78f5339e1e19d4d7740280264e9d7cfcdad2b54a778ae84d5681bba9ccf2cb0f|hash=c1529a51372a87b3ec8cc1203bfe17afc4c397f46dcd69bc572cf91d0daa901f"
#define VEC3_ANCHOR "v=1|life=SELFTEST|audit=cycle|cycle=1|events=1-10|pos=4|neg=4|man=2|shadow=7|pos_rate=0.5000|net=0.8907|net_pct=0.08907|max_dd=1.3542|max_dd_pct=0.13542|life_net=0.8907|life_dd=1.3542|lvl_start=0|lvl_end=10|root=e275b5aa5a5d76577343cc43a2335247b74d5b522ef262f836d3d20942d0354d|head=8b629e765fb3b941bc42d11ff93422e811e39693d5aeb83f9b181cf479623d97|prev=01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1|hash=04165f75d5095815d53140c2dbf796f3f3a74a2125a69231c0148f4bd3aa7ece"
#define VEC3_LIFECYCLE "v=1|life=SELFTEST_LOCK|audit=lifecycle|events=360|cycles=36|shadow=0|pos=240|neg=120|man=0|net=12.0000|net_pct=1.20000|max_dd=0.4000|max_dd_pct=0.04000|violations=0|head=7b177c16dc5e957717ce1a50c47583e8ec1291a2c1724a4a47b7acd581ab11c8"
#define VEC3_OUTBOX_LINES 18
#define VEC3_OUTBOX_SUM "sum=7f24a5d048bd42062b21d05ba824892cc9f18cec6479bc7c5206509cce398412"
#define VEC3_CENT_RECORD "v=1|life=P3SELFTEST|k=1|mode=REAL|n=1|cycle=1|step=1|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=BUY|open=2026-11-04T23:00:00Z|close=2026-11-05T00:55:00Z|by=TIME|res=MANUAL|lvl_before=0|lvl_after=0|neg_run=0|ratio=1.04|mult=0.0882|fric=0.0500|plan=0.1206|risk=0.1200|vol=0.0400|entry=151.234|lower=150.780|upper=151.706|exit=151.311|delta=0.3080|deals=50001000;50001001|prev=8030586feaabf98ec930fe665575b9f6c51134d93632d2983fe2cf9a100aae05|hash=5b51bea4f02aa36b6b4131eb41d3719e70815e6c293b53620bff4fb39946d1e7"
#define VEC3_CENT_LINES 18
#define VEC3_CENT_HEAD "SEESARE P26 | P3SELFTEST | Cycle 1/36 | Step 1/10 | REAL"
#define VEC3_CENT_RESULT "Result MANUAL | +0.3080 USD | level L0 -> L0 | negative run 0"
#define VEC3_CENT_DEALS "Deals 50001000, 50001001"
#define VEC3_CENT_SUM "sum=0f30077939418b1cd350f5c228169aa60a67d76a3cad0b1584ae6f104a9799f6"
void GeneratedVectors(void)
  {
   T_Int("telegram genesis: lines", LineCount(CSeesareTelegram::Genesis(VEC3_GENESIS)), 5);
   T_Str("telegram genesis: line 1", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 0), "SEESARE P26 | SELFTEST | lifecycle opened 2026-11-01T00:00:00Z");
   T_Str("telegram genesis: line 2", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 1), "Baseline 1000.00 USD | 360 events in cycles of 10 | envelope 3.60%");
   T_Str("telegram genesis: line 3", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 2), "Time exits LOSS_NEGATIVE | exponent 2.00");
   T_Str("telegram genesis: line 4", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 3), "Ladder % 0.1440,0.0950,0.0620,0.0410,0.0270,0.0180,0.0120,0.0080,0.0050,0.0033,0.0022,0.0014,0.0009,0.0006,0.0004,0.0003");
   T_Str("telegram genesis: line 5", Line(CSeesareTelegram::Genesis(VEC3_GENESIS), 4), "Genesis hash 01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1");
   T_Int("telegram real event: lines", LineCount(CSeesareTelegram::Event(VEC3_EVENT_REAL)), 9);
   T_Str("telegram real event: line 1", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 0), "SEESARE P26 | SELFTEST | Cycle 1/36 | Step 1/10 | REAL");
   T_Str("telegram real event: line 2", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 1), "TOKYO_FIX USDJPY BUY");
   T_Str("telegram real event: line 3", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 2), "Open 2026-11-04T23:00:00Z | Close 2026-11-05T00:55:00Z | by TIME");
   T_Str("telegram real event: line 4", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 3), "Result MANUAL | +0.4321 USD | level L0 -> L0 | negative run 0");
   T_Str("telegram real event: line 5", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 4), "Entry 151.234 | Lower 151.084 | Upper 151.759 | Exit 151.311");
   T_Str("telegram real event: line 6", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 5), "Ratio 3.50 | multiplier 1.0000 | planned 1.3680 USD | risk 1.0600 USD | volume 0.0100");
   T_Str("telegram real event: line 7", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 6), "Deals 50001000, 50001001");
   T_Str("telegram real event: line 8", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 7), "Chain k=1 | hash c873280ea8ea9218aa4f72434e15a77d9d0e3109d08c127b073453a0fb1668ed");
   T_Str("telegram real event: line 9", Line(CSeesareTelegram::Event(VEC3_EVENT_REAL), 8), "Prev 01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1");
   T_Int("telegram shadow event: lines", LineCount(CSeesareTelegram::Event(VEC3_EVENT_SHADOW)), 9);
   T_Str("telegram shadow event: line 1", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 0), "SEESARE P26 | SELFTEST | Cycle 1/36 | SHADOW (paper, not counted)");
   T_Str("telegram shadow event: line 2", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 1), "TOKYO_FIX USDJPY SELL");
   T_Str("telegram shadow event: line 3", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 2), "Open 2026-11-06T23:00:00Z | Close 2026-11-07T00:55:00Z | by TARGET");
   T_Str("telegram shadow event: line 4", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 3), "Result POSITIVE | +2.0615 USD | level L2 -> L1 | negative run 0");
   T_Str("telegram shadow event: line 5", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 4), "Entry 151.234 | Lower 150.709 | Upper 151.384 | Exit 150.709");
   T_Str("telegram shadow event: line 6", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 5), "Ratio 3.50 | multiplier 1.0000 | planned 0.5890 USD | risk 0.0000 USD | volume 0.0059");
   T_Str("telegram shadow event: line 7", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 6), "Deals none (paper)");
   T_Str("telegram shadow event: line 8", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 7), "Chain k=3 | hash c1529a51372a87b3ec8cc1203bfe17afc4c397f46dcd69bc572cf91d0daa901f");
   T_Str("telegram shadow event: line 9", Line(CSeesareTelegram::Event(VEC3_EVENT_SHADOW), 8), "Prev 78f5339e1e19d4d7740280264e9d7cfcdad2b54a778ae84d5681bba9ccf2cb0f");
   T_Int("telegram cycle audit: lines", LineCount(CSeesareTelegram::Audit(VEC3_ANCHOR)), 8);
   T_Str("telegram cycle audit: line 1", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 0), "SEESARE P26 | SELFTEST | Cycle 1/36 closed | events 1-10");
   T_Str("telegram cycle audit: line 2", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 1), "Positive 4 | negative 4 | manual 2 | shadow 7 | positive rate 0.5000");
   T_Str("telegram cycle audit: line 3", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 2), "Cycle net +0.8907 USD (+0.08907%) | cycle max drawdown 1.3542 USD (0.13542%)");
   T_Str("telegram cycle audit: line 4", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 3), "Lifecycle net +0.8907 USD | lifecycle max drawdown 1.3542 USD");
   T_Str("telegram cycle audit: line 5", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 4), "Level L0 -> L10");
   T_Str("telegram cycle audit: line 6", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 5), "Block root e275b5aa5a5d76577343cc43a2335247b74d5b522ef262f836d3d20942d0354d");
   T_Str("telegram cycle audit: line 7", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 6), "Chain head 8b629e765fb3b941bc42d11ff93422e811e39693d5aeb83f9b181cf479623d97");
   T_Str("telegram cycle audit: line 8", Line(CSeesareTelegram::Audit(VEC3_ANCHOR), 7), "Anchor 04165f75d5095815d53140c2dbf796f3f3a74a2125a69231c0148f4bd3aa7ece");
   T_Int("telegram lifecycle: lines", LineCount(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE)), 4);
   T_Str("telegram lifecycle: line 1", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 0), "SEESARE P26 | SELFTEST_LOCK | lifecycle complete: 360 events in 36 cycles");
   T_Str("telegram lifecycle: line 2", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 1), "Positive 240 | negative 120 | manual 0 | shadow 0");
   T_Str("telegram lifecycle: line 3", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 2), "Net +12.0000 USD (+1.20000%) | max drawdown 0.4000 USD (0.04000%) | envelope violations 0");
   T_Str("telegram lifecycle: line 4", Line(CSeesareTelegram::Lifecycle(VEC3_LIFECYCLE), 3), "Final head 7b177c16dc5e957717ce1a50c47583e8ec1291a2c1724a4a47b7acd581ab11c8");
   T_Str("outbox body genesis: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("GENESIS", VEC3_GENESIS)), "94e92edae669a925ad8ad79cfff52cebb92cc7a169c3c9668f1f3a30d762e3e2");
   T_Int("outbox body genesis: length", StringLen(CSeesareTelegram::Body("GENESIS", VEC3_GENESIS)), 725);
   T_Str("outbox body genesis: record line", Line(CSeesareTelegram::Body("GENESIS", VEC3_GENESIS), 5), RecordLine(VEC3_GENESIS));
   T_Str("outbox body event_real: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("EVENT", VEC3_EVENT_REAL)), "fdd18cf66068461075f61b8eaa70484b0ae97f4a62be92eccbf412a12fa19643");
   T_Int("outbox body event_real: length", StringLen(CSeesareTelegram::Body("EVENT", VEC3_EVENT_REAL)), 1047);
   T_Str("outbox body event_real: record line", Line(CSeesareTelegram::Body("EVENT", VEC3_EVENT_REAL), 9), RecordLine(VEC3_EVENT_REAL));
   T_Str("outbox body event_shadow: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("EVENT", VEC3_EVENT_SHADOW)), "ba30744e77469cc0e0d637883c1b28312b70691a9813ae8c8d56f28d648a7d82");
   T_Int("outbox body event_shadow: length", StringLen(CSeesareTelegram::Body("EVENT", VEC3_EVENT_SHADOW)), 1048);
   T_Str("outbox body event_shadow: record line", Line(CSeesareTelegram::Body("EVENT", VEC3_EVENT_SHADOW), 9), RecordLine(VEC3_EVENT_SHADOW));
   T_Str("outbox body anchor: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("AUDIT", VEC3_ANCHOR)), "ba9659f452108f67767a98ddc0cf79ee61325a0b273486a4c3b88f042577edc4");
   T_Int("outbox body anchor: length", StringLen(CSeesareTelegram::Body("AUDIT", VEC3_ANCHOR)), 999);
   T_Str("outbox body anchor: record line", Line(CSeesareTelegram::Body("AUDIT", VEC3_ANCHOR), 8), RecordLine(VEC3_ANCHOR));
   T_Str("outbox body lifecycle: SHA-256", CSeesareSha256::Hex(CSeesareTelegram::Body("LIFECYCLE", VEC3_LIFECYCLE)), "6007856caddce0cf337187af7b8e2e5a351b8452fe1bcc46f29b103a2c0b3ece");
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
   T_Str("levels cent USDJPY 0.3% stop, ratio 1.04", LevelTable(1.04, 3.0), "L0 0.1206 0.04 real|L1 0.0796 0.02 real|L2 0.0519 0.01 real|L3 0.0343 0.01 real|L4 0.0226 0.00 shadow|L5 0.0150 0.00 shadow|L6 0.0100 0.00 shadow|L7 0.0067 0.00 shadow|L8 0.0041 0.00 shadow|L9 0.0027 0.00 shadow|L10 0.0018 0.00 shadow|L11 0.0011 0.00 shadow|L12 0.0007 0.00 shadow|L13 0.0005 0.00 shadow|L14 0.0003 0.00 shadow|L15 0.0002 0.00 shadow");
   T_Int("lowest feasible level cent USDJPY 0.3% stop, ratio 1.04", CSeesareExposure::LowestFeasibleLevel(1.04, 0.05, 3.0, 0.01, 0.01), 3);
   T_Str("levels cent USDJPY 0.3% stop, ratio 3.50", LevelTable(3.5, 3.0), "L0 1.3680 0.45 real|L1 0.9025 0.30 real|L2 0.5890 0.19 real|L3 0.3895 0.12 real|L4 0.2565 0.08 real|L5 0.1710 0.05 real|L6 0.1140 0.03 real|L7 0.0760 0.02 real|L8 0.0475 0.01 real|L9 0.0313 0.01 real|L10 0.0209 0.00 shadow|L11 0.0133 0.00 shadow|L12 0.0085 0.00 shadow|L13 0.0057 0.00 shadow|L14 0.0038 0.00 shadow|L15 0.0028 0.00 shadow");
   T_Int("lowest feasible level cent USDJPY 0.3% stop, ratio 3.50", CSeesareExposure::LowestFeasibleLevel(3.5, 0.05, 3.0, 0.01, 0.01), 9);
   T_Str("levels standard USDJPY 0.3% stop, ratio 3.50", LevelTable(3.5, 300.0), "L0 1.3680 0.00 shadow|L1 0.9025 0.00 shadow|L2 0.5890 0.00 shadow|L3 0.3895 0.00 shadow|L4 0.2565 0.00 shadow|L5 0.1710 0.00 shadow|L6 0.1140 0.00 shadow|L7 0.0760 0.00 shadow|L8 0.0475 0.00 shadow|L9 0.0313 0.00 shadow|L10 0.0209 0.00 shadow|L11 0.0133 0.00 shadow|L12 0.0085 0.00 shadow|L13 0.0057 0.00 shadow|L14 0.0038 0.00 shadow|L15 0.0028 0.00 shadow");
   T_Int("lowest feasible level standard USDJPY 0.3% stop, ratio 3.50", CSeesareExposure::LowestFeasibleLevel(3.5, 0.05, 300.0, 0.01, 0.01), -1);
   T_Str("levels cent EURUSD 10-pip stop, ratio 3.50", LevelTable(3.5, 1.0), "L0 1.3680 1.36 real|L1 0.9025 0.90 real|L2 0.5890 0.58 real|L3 0.3895 0.38 real|L4 0.2565 0.25 real|L5 0.1710 0.17 real|L6 0.1140 0.11 real|L7 0.0760 0.07 real|L8 0.0475 0.04 real|L9 0.0313 0.03 real|L10 0.0209 0.02 real|L11 0.0133 0.01 real|L12 0.0085 0.00 shadow|L13 0.0057 0.00 shadow|L14 0.0038 0.00 shadow|L15 0.0028 0.00 shadow");
   T_Int("lowest feasible level cent EURUSD 10-pip stop, ratio 3.50", CSeesareExposure::LowestFeasibleLevel(3.5, 0.05, 1.0, 0.01, 0.01), 11);
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
   bool made = CSeesareDealReader::ToEvent(d, "TOKYO_FIX", "forex", 3, 1.04, 0.12, 150.780, 151.706, e);
   T_Bool("deal reader: a closed position becomes a REAL event", made && e.mode == SEESARE_REAL && e.deals == "50001000;50001001", "");
   SSeesareDealSummary still;
   still.Clear();
   still.closed = false;
   still.count = 1;
   still.side = 1;
   SSeesareEvent e2;
   T_Bool("deal reader: an open position is not an event", !CSeesareDealReader::ToEvent(still, "TOKYO_FIX", "forex", 3, 1.04, 0.12,
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
   double ratios[2];
   ratios[0] = SEESARE_TOKYO_RATIO;
   ratios[1] = 3.5;
   for(int i = 0; i < 2; i++)
     {
      int lowest = CSeesareExposure::LowestFeasibleLevel(ratios[i], 0.05, per_lot, step, vmin);
      string where = "no level can trade REAL (all SHADOW)";
      if(lowest >= 0)
         where = "REAL from L0 down to L" + IntegerToString(lowest) + ", SHADOW below";
      Print("INFO  ratio ", DoubleToString(ratios[i], 2), ": ", where);
      Print("INFO    ", LevelTableFor(ratios[i], per_lot, step, vmin));
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

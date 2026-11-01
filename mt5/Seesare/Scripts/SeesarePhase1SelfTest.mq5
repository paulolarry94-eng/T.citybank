//+------------------------------------------------------------------+
//|                                       SeesarePhase1SelfTest.mq5  |
//| SEESARE P26 router, Phase 1 self-test. UNCOMPILED SOURCE.        |
//|                                                                  |
//| Install: copy mt5/Seesare/Include/Seesare to MQL5\Include\Seesare|
//| and this file to MQL5\Scripts; compile in MetaEditor; drag onto  |
//| any chart. Results go to the Experts tab: one PASS/FAIL line per |
//| check and a summary. INFO lines describe this broker's clock and |
//| are not counted.                                                 |
//|                                                                  |
//| The expected values come from the Python twin                    |
//| (python3 tools/seesare_verify.py --mql). The repository test     |
//| research/truth/tests/test_seesare_phase1.py fails if this block  |
//| and the twin drift apart.                                        |
//+------------------------------------------------------------------+
#property copyright   "T.citybank"
#property version     "1.00"
#property description "SEESARE Phase 1 self-test: clock, timing matrix, ladder, cycle ledger, outbox"
#property script_show_inputs

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Core\SpreadGate.mqh>
#include <Seesare\Ledger\CycleLedger.mqh>

input ENUM_SEESARE_SERVER_SCHEME InpScheme    = SEESARE_SERVER_GMT2_EU;   // server time scheme you plan to declare for this broker
input bool                       InpRunLock   = true;                     // run the full 360-event lifecycle (writes about 800 small files)
input bool                       InpKeepFiles = false;                    // keep the test folders in Common\Files\seesare_selftest

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

string WindowList(CSeesareTimingMatrix &m, const datetime utc)
  {
   SSeesareUtcWindow w[];
   int n = m.OnUtcDate(utc, w);
   string s = "";
   for(int i = 0; i < n; i++)
     {
      if(i > 0)
         s += ",";
      s += w[i].id + "@" + StringSubstr(CSeesareDst::IsoUtc(w[i].start_utc), 11, 5);
     }
   return s;
  }

string ResolveWin(CSeesareTimingMatrix &m, const string id, const datetime local_date)
  {
   SSeesareUtcWindow w;
   if(!m.ResolveLocalDate(m.Find(id), local_date, w))
      return "closed";
   return CSeesareDst::IsoUtc(w.start_utc) + "/" + CSeesareDst::IsoUtc(w.end_utc);
  }

string ActiveWin(CSeesareTimingMatrix &m, const string id, const datetime utc)
  {
   SSeesareUtcWindow w;
   if(!m.ActiveAt(m.Find(id), utc, w))
      return "no";
   return CSeesareDst::IsoUtc(w.start_utc);
  }

string NextWin(CSeesareTimingMatrix &m, const string id, const datetime utc)
  {
   SSeesareUtcWindow w;
   if(!m.NextAt(m.Find(id), utc, w))
      return "none";
   return CSeesareDst::IsoUtc(w.start_utc);
  }

string Transition(const int level, const int neg_run, const int res)
  {
   int la = 0;
   int na = 0;
   CSeesareLadder::Next(level, neg_run, (ENUM_SEESARE_RES)res, la, na);
   return IntegerToString(la) + "/" + IntegerToString(na);
  }

//--- BEGIN GENERATED VECTORS: python3 tools/seesare_verify.py --mql  (do not edit by hand)
#define VEC_LIFE          "SELFTEST"
#define VEC_EVENTS        20
#define VEC_MESSAGES      22
#define VEC_LEVEL         15
#define VEC_NEG_RUN       2
#define VEC_REAL          12
#define VEC_SHADOW        8
#define VEC_CYCLE         2
#define VEC_LIFE_NET      "0.6807"
#define VEC_LIFE_DD       "1.3542"
#define VEC_ROOM          "35.3958"
#define VEC_GENESIS       "v=1|life=SELFTEST|k=0|genesis|baseline=1000.00|events=360|cycle_size=10|envelope_pct=3.60|exponent=2.00|time_policy=LOSS_NEGATIVE|ladder=0.1440,0.0950,0.0620,0.0410,0.0270,0.0180,0.0120,0.0080,0.0050,0.0033,0.0022,0.0014,0.0009,0.0006,0.0004,0.0003|created=2026-11-01T00:00:00Z|hash=01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1"
#define VEC_EVENT1        "v=1|life=SELFTEST|k=1|mode=REAL|n=1|cycle=1|step=1|module=TOKYO_FIX|domain=forex|symbol=USDJPY|side=BUY|open=2026-11-04T23:00:00Z|close=2026-11-05T00:55:00Z|by=TIME|res=MANUAL|lvl_before=0|lvl_after=0|neg_run=0|ratio=3.50|mult=1.0000|fric=0.0500|plan=1.3680|risk=1.0600|vol=0.0100|entry=151.234|lower=151.084|upper=151.759|exit=151.311|delta=0.4321|deals=50001000;50001001|prev=01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1|hash=c873280ea8ea9218aa4f72434e15a77d9d0e3109d08c127b073453a0fb1668ed"
#define VEC_ANCHOR1       "v=1|life=SELFTEST|audit=cycle|cycle=1|events=1-10|pos=4|neg=4|man=2|shadow=7|pos_rate=0.5000|net=0.8907|net_pct=0.08907|max_dd=1.3542|max_dd_pct=0.13542|life_net=0.8907|life_dd=1.3542|lvl_start=0|lvl_end=10|root=e275b5aa5a5d76577343cc43a2335247b74d5b522ef262f836d3d20942d0354d|head=8b629e765fb3b941bc42d11ff93422e811e39693d5aeb83f9b181cf479623d97|prev=01523b82b69a8f5d986a2f650bc070a00c43d43dddb0e178a32652bfc6e973b1|hash=04165f75d5095815d53140c2dbf796f3f3a74a2125a69231c0148f4bd3aa7ece"
#define VEC_HEAD          "d584c10d779670680fe1abc8dc0c74e186345e4224c05894d32cd8db204b8979"
#define VEC_LOCK_MESSAGES 398
#define VEC_LOCK_HEAD     "7b177c16dc5e957717ce1a50c47583e8ec1291a2c1724a4a47b7acd581ab11c8"
#define VEC_LOCK_ANCHOR36 "v=1|life=SELFTEST_LOCK|audit=cycle|cycle=36|events=351-360|pos=6|neg=4|man=0|shadow=0|pos_rate=0.6000|net=-0.1000|net_pct=-0.01000|max_dd=0.4000|max_dd_pct=0.04000|life_net=12.0000|life_dd=0.4000|lvl_start=0|lvl_end=2|root=e1f240be3efedfa4510ed76a68746efb51f61bc8c19c501b8f8ffc7fa76b9116|head=7b177c16dc5e957717ce1a50c47583e8ec1291a2c1724a4a47b7acd581ab11c8|prev=8f6d02678820387a9b0a8b15f44dd996246aa94c5315f031813d95b4dbcaacff|hash=13e885b545ecbd44ea22efd27c8a21947ce6adf1ac5cbdedb98c1b819c84a3d2"
const int VEC_MODE[VEC_EVENTS] = {0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0};
const int VEC_SIDE[VEC_EVENTS] = {1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1, 1, -1};
const int VEC_BY[VEC_EVENTS] = {2, 0, 1, 1, 1, 2, 0, 0, 2, 0, 1, 1, 1, 1, 0, 2, 1, 0, 3, 4};
const double VEC_RATIO[VEC_EVENTS] = {3.5, 3.5, 3.5, 3.5, 2.0, 5.0, 3.5, 3.5, 3.5, 3.5, 3.5, 0.8, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5};
const double VEC_RISK[VEC_EVENTS] = {1.06, 1.06, 0.0, 0.0, 1.06, 1.06, 1.06, 0.0, 0.0, 0.0, 0.0, 0.0, 1.06, 1.06, 1.06, 1.06, 1.06, 1.06, 0.0, 1.06};
const double VEC_VOL[VEC_EVENTS] = {0.01, 0.01, 0.0059, 0.0091, 0.01, 0.01, 0.01, 0.0059, 0.0017, 0.0017, 0.0005, 0.0003, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.0006, 0.01};
const double VEC_LOWER[VEC_EVENTS] = {151.084, 151.084, 150.709, 151.084, 151.084, 151.084, 150.709, 151.084, 151.084, 151.084, 151.084, 151.114, 151.084, 151.084, 151.084, 151.084, 151.084, 151.084, 151.084, 150.709};
const double VEC_UPPER[VEC_EVENTS] = {151.759, 151.759, 151.384, 151.759, 151.534, 151.984, 151.384, 151.759, 151.759, 151.759, 151.759, 151.384, 151.759, 151.759, 151.759, 151.759, 151.759, 151.759, 151.759, 151.384};
const double VEC_EXIT[VEC_EVENTS] = {151.311, 151.084, 150.709, 151.759, 151.534, 151.204, 151.384, 151.084, 151.25, 151.084, 151.759, 151.114, 151.759, 151.759, 151.084, 151.271, 151.759, 151.084, 151.3, 151.384};
const double VEC_DELTA[VEC_EVENTS] = {0.4321, -1.0592, 2.0615, 3.1605, 1.912, -0.295, -1.0592, -0.589, 0.0122, -0.171, 0.1663, 0.0301, 0.41, 0.39, -0.18, 0.05, 0.29, -0.12, 0.01, -0.09};
const string VEC_DEALS[VEC_EVENTS] = {"50001000;50001001", "50001002;50001003", "-", "-", "50001008;50001009", "50001010;50001011", "50001012;50001013", "-", "-", "-", "-", "-", "50001024;50001025", "50001026;50001027", "50001028;50001029", "50001030;50001031", "50001032;50001033", "50001034;50001035", "-", "50001038;50001039"};
const string VEC_HASH[VEC_EVENTS] = {"c873280ea8ea9218aa4f72434e15a77d9d0e3109d08c127b073453a0fb1668ed", "78f5339e1e19d4d7740280264e9d7cfcdad2b54a778ae84d5681bba9ccf2cb0f", "c1529a51372a87b3ec8cc1203bfe17afc4c397f46dcd69bc572cf91d0daa901f", "d2f0cc0fdddb37c8a2c4483329d11e3fc9234073c02b195d1048bde670ac973f", "87f8338960a4464d37c4de1bf40d19c7a34a08312bb58d236a92bd11851ff39a", "68e7ba21a6b7b539f20bd61a3de6308e454426a2d671b171c190754372421a75", "8f4991dc6ebd05433ae633367e0dbd6c0e9a2ac4ec8a2dc6bc6dab31aba960b1", "2af3a420078700fc127a1874d26065ca75024d8f50694e4eff657ba851a591d6", "7797be63723e2cada31a35d5ffac619e98b6cb7f6db9f3087eb80dea798303b1", "fb74aa31c6c6ad5369da4fafb489214a1896e6ac6e441c4e5701ccd01a59e236", "cf6fb2e260072513de323209bee8e556b2811948136c3fcacdf83f8479005e7b", "049cef341de44035d8b8414e6681e226eb8541e82e4aadad9cd3137f3ef1b8d3", "7f94757b36240d0465fe4089070cb8b25fca8739059896690a288359a04b8e8a", "d134147ca4be1e3551c73941fb7c774d2dc8867812c4a5fec72f7c762d6638e6", "bc23c9eb995038799dcf1add06c8a5843556f0a3bbeaf9ac29b1583c1e838862", "9f3ef08b4653faf775fe630829d92306353d7c5f5abf752400bfa114ae0008ef", "8b629e765fb3b941bc42d11ff93422e811e39693d5aeb83f9b181cf479623d97", "abb05ff3390dc4b928188bb8303c2575adea9a632eeb0597751b46fc0fff0621", "c942e765e6a8829cbbac49594b3ab90828005845ffe99526d88e54a91ac6ea8f", "d584c10d779670680fe1abc8dc0c74e186345e4224c05894d32cd8db204b8979"};
void GeneratedVectors(CSeesareTimingMatrix &m)
  {
   T_Str("sha256 abc", CSeesareSha256::Hex("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
   T_Str("sha256 two blocks", CSeesareSha256::Hex("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"), "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
   T_Str("sha256 empty", CSeesareSha256::Hex(""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
   T_Str("dst us_start 2011", CSeesareDst::IsoUtc(CSeesareDst::UsStart(2011)), "2011-03-13T07:00:00Z");
   T_Str("dst us_end 2011", CSeesareDst::IsoUtc(CSeesareDst::UsEnd(2011)), "2011-11-06T06:00:00Z");
   T_Str("dst eu_start 2011", CSeesareDst::IsoUtc(CSeesareDst::EuStart(2011)), "2011-03-27T01:00:00Z");
   T_Str("dst eu_end 2011", CSeesareDst::IsoUtc(CSeesareDst::EuEnd(2011)), "2011-10-30T01:00:00Z");
   T_Str("dst us_start 2026", CSeesareDst::IsoUtc(CSeesareDst::UsStart(2026)), "2026-03-08T07:00:00Z");
   T_Str("dst us_end 2026", CSeesareDst::IsoUtc(CSeesareDst::UsEnd(2026)), "2026-11-01T06:00:00Z");
   T_Str("dst eu_start 2026", CSeesareDst::IsoUtc(CSeesareDst::EuStart(2026)), "2026-03-29T01:00:00Z");
   T_Str("dst eu_end 2026", CSeesareDst::IsoUtc(CSeesareDst::EuEnd(2026)), "2026-10-25T01:00:00Z");
   T_Str("dst us_start 2027", CSeesareDst::IsoUtc(CSeesareDst::UsStart(2027)), "2027-03-14T07:00:00Z");
   T_Str("dst us_end 2027", CSeesareDst::IsoUtc(CSeesareDst::UsEnd(2027)), "2027-11-07T06:00:00Z");
   T_Str("dst eu_start 2027", CSeesareDst::IsoUtc(CSeesareDst::EuStart(2027)), "2027-03-28T01:00:00Z");
   T_Str("dst eu_end 2027", CSeesareDst::IsoUtc(CSeesareDst::EuEnd(2027)), "2027-10-31T01:00:00Z");
   T_Str("dst us_start 2035", CSeesareDst::IsoUtc(CSeesareDst::UsStart(2035)), "2035-03-11T07:00:00Z");
   T_Str("dst us_end 2035", CSeesareDst::IsoUtc(CSeesareDst::UsEnd(2035)), "2035-11-04T06:00:00Z");
   T_Str("dst eu_start 2035", CSeesareDst::IsoUtc(CSeesareDst::EuStart(2035)), "2035-03-25T01:00:00Z");
   T_Str("dst eu_end 2035", CSeesareDst::IsoUtc(CSeesareDst::EuEnd(2035)), "2035-10-28T01:00:00Z");
   T_Str("to utc LONDON 2026-03-10 16:00 (US already on summer time)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 3, 10, 16, 0))), "2026-03-10T16:00:00Z");
   T_Str("back to local LONDON 2026-03-10 16:00 (US already on summer time)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_LONDON, CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 3, 10, 16, 0)))), "2026-03-10T16:00:00Z");
   T_Str("to utc NEW_YORK 2026-03-10 15:50 (mismatch week)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 3, 10, 15, 50))), "2026-03-10T19:50:00Z");
   T_Str("back to local NEW_YORK 2026-03-10 15:50 (mismatch week)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_NEW_YORK, CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 3, 10, 15, 50)))), "2026-03-10T15:50:00Z");
   T_Str("to utc NEW_YORK 2026-03-02 15:50 (winter)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 3, 2, 15, 50))), "2026-03-02T20:50:00Z");
   T_Str("back to local NEW_YORK 2026-03-02 15:50 (winter)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_NEW_YORK, CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 3, 2, 15, 50)))), "2026-03-02T15:50:00Z");
   T_Str("to utc LONDON 2026-07-01 16:00", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 7, 1, 16, 0))), "2026-07-01T15:00:00Z");
   T_Str("back to local LONDON 2026-07-01 16:00", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_LONDON, CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 7, 1, 16, 0)))), "2026-07-01T16:00:00Z");
   T_Str("to utc FRANKFURT 2026-07-01 14:05", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_FRANKFURT, CSeesareDst::Date(2026, 7, 1, 14, 5))), "2026-07-01T12:05:00Z");
   T_Str("back to local FRANKFURT 2026-07-01 14:05", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_FRANKFURT, CSeesareDst::VenueToUtc(SEESARE_VENUE_FRANKFURT, CSeesareDst::Date(2026, 7, 1, 14, 5)))), "2026-07-01T14:05:00Z");
   T_Str("to utc TOKYO 2026-07-01 09:55", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_TOKYO, CSeesareDst::Date(2026, 7, 1, 9, 55))), "2026-07-01T00:55:00Z");
   T_Str("back to local TOKYO 2026-07-01 09:55", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_TOKYO, CSeesareDst::VenueToUtc(SEESARE_VENUE_TOKYO, CSeesareDst::Date(2026, 7, 1, 9, 55)))), "2026-07-01T09:55:00Z");
   T_Str("to utc NEW_YORK 2026-10-28 15:50 (EU back on winter time, US not)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 10, 28, 15, 50))), "2026-10-28T19:50:00Z");
   T_Str("back to local NEW_YORK 2026-10-28 15:50 (EU back on winter time, US not)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_NEW_YORK, CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 10, 28, 15, 50)))), "2026-10-28T15:50:00Z");
   T_Str("to utc NEW_YORK 2026-03-08 02:30 (skipped hour)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 3, 8, 2, 30))), "2026-03-08T07:30:00Z");
   T_Str("back to local NEW_YORK 2026-03-08 02:30 (skipped hour)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_NEW_YORK, CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 3, 8, 2, 30)))), "2026-03-08T03:30:00Z");
   T_Str("to utc NEW_YORK 2026-11-01 01:30 (repeated hour)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 11, 1, 1, 30))), "2026-11-01T05:30:00Z");
   T_Str("back to local NEW_YORK 2026-11-01 01:30 (repeated hour)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_NEW_YORK, CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, CSeesareDst::Date(2026, 11, 1, 1, 30)))), "2026-11-01T01:30:00Z");
   T_Str("to utc LONDON 2026-03-29 01:30 (skipped hour)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 3, 29, 1, 30))), "2026-03-29T01:30:00Z");
   T_Str("back to local LONDON 2026-03-29 01:30 (skipped hour)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_LONDON, CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 3, 29, 1, 30)))), "2026-03-29T02:30:00Z");
   T_Str("to utc LONDON 2026-10-25 01:30 (repeated hour)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 10, 25, 1, 30))), "2026-10-25T00:30:00Z");
   T_Str("back to local LONDON 2026-10-25 01:30 (repeated hour)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_LONDON, CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, CSeesareDst::Date(2026, 10, 25, 1, 30)))), "2026-10-25T01:30:00Z");
   T_Str("to utc FRANKFURT 2027-03-28 02:30 (skipped hour)", CSeesareDst::IsoUtc(CSeesareDst::VenueToUtc(SEESARE_VENUE_FRANKFURT, CSeesareDst::Date(2027, 3, 28, 2, 30))), "2027-03-28T01:30:00Z");
   T_Str("back to local FRANKFURT 2027-03-28 02:30 (skipped hour)", CSeesareDst::IsoUtc(CSeesareDst::UtcToVenue(SEESARE_VENUE_FRANKFURT, CSeesareDst::VenueToUtc(SEESARE_VENUE_FRANKFURT, CSeesareDst::Date(2027, 3, 28, 2, 30)))), "2027-03-28T03:30:00Z");
   T_Str("server GMT2_US 2026-03-10T00:00 -> utc", CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_GMT2_US, CSeesareDst::Date(2026, 3, 10, 0, 0), 0)), "2026-03-09T21:00:00Z");
   T_Str("server GMT2_EU 2026-03-10T00:00 -> utc", CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_GMT2_EU, CSeesareDst::Date(2026, 3, 10, 0, 0), 0)), "2026-03-09T22:00:00Z");
   T_Str("server GMT2_EU 2026-07-01T00:00 -> utc", CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_GMT2_EU, CSeesareDst::Date(2026, 7, 1, 0, 0), 0)), "2026-06-30T21:00:00Z");
   T_Str("server GMT2_US 2026-10-28T00:00 -> utc", CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_GMT2_US, CSeesareDst::Date(2026, 10, 28, 0, 0), 0)), "2026-10-27T21:00:00Z");
   T_Str("server GMT2_EU 2026-10-28T00:00 -> utc", CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_GMT2_EU, CSeesareDst::Date(2026, 10, 28, 0, 0), 0)), "2026-10-27T22:00:00Z");
   T_Str("server GMT0 2026-07-01T00:00 -> utc", CSeesareDst::IsoUtc(CSeesareDst::SchemeServerToUtc(SEESARE_SERVER_GMT0, CSeesareDst::Date(2026, 7, 1, 0, 0), 0)), "2026-07-01T00:00:00Z");
   T_Str("windows on 2026-03-10 (UTC start)", WindowList(m, CSeesareDst::Date(2026, 3, 10, 12, 0)), "TOCOM_CLOSE@06:15,FUNDING_08@07:50,ECB_FIX@13:05,NY_MOO@13:15,WMR_FIX@15:30,FUNDING_16@15:50,FOMC@18:00,NY_MOC@19:50,TOKYO_FIX@23:00,FUNDING_00@23:50");
   T_Str("windows on 2026-03-13 (UTC start)", WindowList(m, CSeesareDst::Date(2026, 3, 13, 12, 0)), "TOCOM_CLOSE@06:15,FUNDING_08@07:50,US_NFP@12:30,ECB_FIX@13:05,NY_MOO@13:15,WMR_FIX@15:30,FUNDING_16@15:50,FOMC@18:00,NY_MOC@19:50,FUNDING_00@23:50");
   T_Str("windows on 2026-07-01 (UTC start)", WindowList(m, CSeesareDst::Date(2026, 7, 1, 12, 0)), "TOCOM_CLOSE@06:15,FUNDING_08@07:50,ECB_FIX@12:05,NY_MOO@13:15,WMR_FIX@14:30,FUNDING_16@15:50,FOMC@18:00,NY_MOC@19:50,TOKYO_FIX@23:00,FUNDING_00@23:50");
   T_Str("windows on 2026-10-28 (UTC start)", WindowList(m, CSeesareDst::Date(2026, 10, 28, 12, 0)), "TOCOM_CLOSE@06:15,FUNDING_08@07:50,ECB_FIX@13:05,NY_MOO@13:15,WMR_FIX@15:30,FUNDING_16@15:50,FOMC@18:00,NY_MOC@19:50,TOKYO_FIX@23:00,FUNDING_00@23:50");
   T_Str("windows on 2026-11-01 (UTC start)", WindowList(m, CSeesareDst::Date(2026, 11, 1, 12, 0)), "FUNDING_08@07:50,FUNDING_16@15:50,TOKYO_FIX@23:00,FUNDING_00@23:50");
   T_Str("windows on 2026-12-04 (UTC start)", WindowList(m, CSeesareDst::Date(2026, 12, 4, 12, 0)), "TOCOM_CLOSE@06:15,FUNDING_08@07:50,ECB_FIX@13:05,US_NFP@13:30,NY_MOO@14:15,WMR_FIX@15:30,FUNDING_16@15:50,FOMC@19:00,NY_MOC@20:50,FUNDING_00@23:50");
   T_Str("WMR_FIX on local 2026-03-10", ResolveWin(m, "WMR_FIX", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T15:30:00Z/2026-03-10T16:10:00Z");
   T_Str("WMR_FIX on local 2026-03-13", ResolveWin(m, "WMR_FIX", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T15:30:00Z/2026-03-13T16:10:00Z");
   T_Str("WMR_FIX on local 2026-07-01", ResolveWin(m, "WMR_FIX", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T14:30:00Z/2026-07-01T15:10:00Z");
   T_Str("WMR_FIX on local 2026-10-28", ResolveWin(m, "WMR_FIX", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T15:30:00Z/2026-10-28T16:10:00Z");
   T_Str("NY_MOC on local 2026-03-10", ResolveWin(m, "NY_MOC", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T19:50:00Z/2026-03-10T20:05:00Z");
   T_Str("NY_MOC on local 2026-03-13", ResolveWin(m, "NY_MOC", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T19:50:00Z/2026-03-13T20:05:00Z");
   T_Str("NY_MOC on local 2026-07-01", ResolveWin(m, "NY_MOC", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T19:50:00Z/2026-07-01T20:05:00Z");
   T_Str("NY_MOC on local 2026-10-28", ResolveWin(m, "NY_MOC", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T19:50:00Z/2026-10-28T20:05:00Z");
   T_Str("ECB_FIX on local 2026-03-10", ResolveWin(m, "ECB_FIX", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T13:05:00Z/2026-03-10T13:20:00Z");
   T_Str("ECB_FIX on local 2026-03-13", ResolveWin(m, "ECB_FIX", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T13:05:00Z/2026-03-13T13:20:00Z");
   T_Str("ECB_FIX on local 2026-07-01", ResolveWin(m, "ECB_FIX", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T12:05:00Z/2026-07-01T12:20:00Z");
   T_Str("ECB_FIX on local 2026-10-28", ResolveWin(m, "ECB_FIX", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T13:05:00Z/2026-10-28T13:20:00Z");
   T_Str("NY_MOO on local 2026-03-10", ResolveWin(m, "NY_MOO", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T13:15:00Z/2026-03-10T13:40:00Z");
   T_Str("NY_MOO on local 2026-03-13", ResolveWin(m, "NY_MOO", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T13:15:00Z/2026-03-13T13:40:00Z");
   T_Str("NY_MOO on local 2026-07-01", ResolveWin(m, "NY_MOO", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T13:15:00Z/2026-07-01T13:40:00Z");
   T_Str("NY_MOO on local 2026-10-28", ResolveWin(m, "NY_MOO", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T13:15:00Z/2026-10-28T13:40:00Z");
   T_Str("US_NFP on local 2026-03-10", ResolveWin(m, "US_NFP", CSeesareDst::Date(2026, 3, 10)), "closed");
   T_Str("US_NFP on local 2026-03-13", ResolveWin(m, "US_NFP", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T12:30:00Z/2026-03-13T14:00:00Z");
   T_Str("US_NFP on local 2026-07-01", ResolveWin(m, "US_NFP", CSeesareDst::Date(2026, 7, 1)), "closed");
   T_Str("US_NFP on local 2026-10-28", ResolveWin(m, "US_NFP", CSeesareDst::Date(2026, 10, 28)), "closed");
   T_Str("FOMC on local 2026-03-10", ResolveWin(m, "FOMC", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T18:00:00Z/2026-03-10T18:30:00Z");
   T_Str("FOMC on local 2026-03-13", ResolveWin(m, "FOMC", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T18:00:00Z/2026-03-13T18:30:00Z");
   T_Str("FOMC on local 2026-07-01", ResolveWin(m, "FOMC", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T18:00:00Z/2026-07-01T18:30:00Z");
   T_Str("FOMC on local 2026-10-28", ResolveWin(m, "FOMC", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T18:00:00Z/2026-10-28T18:30:00Z");
   T_Str("TOKYO_FIX on local 2026-03-10", ResolveWin(m, "TOKYO_FIX", CSeesareDst::Date(2026, 3, 10)), "2026-03-09T23:00:00Z/2026-03-10T00:55:00Z");
   T_Str("TOKYO_FIX on local 2026-03-13", ResolveWin(m, "TOKYO_FIX", CSeesareDst::Date(2026, 3, 13)), "2026-03-12T23:00:00Z/2026-03-13T00:55:00Z");
   T_Str("TOKYO_FIX on local 2026-07-01", ResolveWin(m, "TOKYO_FIX", CSeesareDst::Date(2026, 7, 1)), "2026-06-30T23:00:00Z/2026-07-01T00:55:00Z");
   T_Str("TOKYO_FIX on local 2026-10-28", ResolveWin(m, "TOKYO_FIX", CSeesareDst::Date(2026, 10, 28)), "2026-10-27T23:00:00Z/2026-10-28T00:55:00Z");
   T_Str("TOCOM_CLOSE on local 2026-03-10", ResolveWin(m, "TOCOM_CLOSE", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T06:15:00Z/2026-03-10T06:45:00Z");
   T_Str("TOCOM_CLOSE on local 2026-03-13", ResolveWin(m, "TOCOM_CLOSE", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T06:15:00Z/2026-03-13T06:45:00Z");
   T_Str("TOCOM_CLOSE on local 2026-07-01", ResolveWin(m, "TOCOM_CLOSE", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T06:15:00Z/2026-07-01T06:45:00Z");
   T_Str("TOCOM_CLOSE on local 2026-10-28", ResolveWin(m, "TOCOM_CLOSE", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T06:15:00Z/2026-10-28T06:45:00Z");
   T_Str("FUNDING_00 on local 2026-03-10", ResolveWin(m, "FUNDING_00", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T23:50:00Z/2026-03-11T00:10:00Z");
   T_Str("FUNDING_00 on local 2026-03-13", ResolveWin(m, "FUNDING_00", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T23:50:00Z/2026-03-14T00:10:00Z");
   T_Str("FUNDING_00 on local 2026-07-01", ResolveWin(m, "FUNDING_00", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T23:50:00Z/2026-07-02T00:10:00Z");
   T_Str("FUNDING_00 on local 2026-10-28", ResolveWin(m, "FUNDING_00", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T23:50:00Z/2026-10-29T00:10:00Z");
   T_Str("FUNDING_08 on local 2026-03-10", ResolveWin(m, "FUNDING_08", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T07:50:00Z/2026-03-10T08:10:00Z");
   T_Str("FUNDING_08 on local 2026-03-13", ResolveWin(m, "FUNDING_08", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T07:50:00Z/2026-03-13T08:10:00Z");
   T_Str("FUNDING_08 on local 2026-07-01", ResolveWin(m, "FUNDING_08", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T07:50:00Z/2026-07-01T08:10:00Z");
   T_Str("FUNDING_08 on local 2026-10-28", ResolveWin(m, "FUNDING_08", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T07:50:00Z/2026-10-28T08:10:00Z");
   T_Str("FUNDING_16 on local 2026-03-10", ResolveWin(m, "FUNDING_16", CSeesareDst::Date(2026, 3, 10)), "2026-03-10T15:50:00Z/2026-03-10T16:10:00Z");
   T_Str("FUNDING_16 on local 2026-03-13", ResolveWin(m, "FUNDING_16", CSeesareDst::Date(2026, 3, 13)), "2026-03-13T15:50:00Z/2026-03-13T16:10:00Z");
   T_Str("FUNDING_16 on local 2026-07-01", ResolveWin(m, "FUNDING_16", CSeesareDst::Date(2026, 7, 1)), "2026-07-01T15:50:00Z/2026-07-01T16:10:00Z");
   T_Str("FUNDING_16 on local 2026-10-28", ResolveWin(m, "FUNDING_16", CSeesareDst::Date(2026, 10, 28)), "2026-10-28T15:50:00Z/2026-10-28T16:10:00Z");
   T_Str("active TOKYO_FIX at 2026-07-01T23:30:00Z", ActiveWin(m, "TOKYO_FIX", CSeesareDst::Date(2026, 7, 1, 23, 30)), "2026-07-01T23:00:00Z");
   T_Str("next TOKYO_FIX after 2026-07-01T23:30:00Z", NextWin(m, "TOKYO_FIX", CSeesareDst::Date(2026, 7, 1, 23, 30)), "2026-07-01T23:00:00Z");
   T_Str("active FUNDING_00 at 2026-07-02T00:05:00Z", ActiveWin(m, "FUNDING_00", CSeesareDst::Date(2026, 7, 2, 0, 5)), "2026-07-01T23:50:00Z");
   T_Str("next FUNDING_00 after 2026-07-02T00:05:00Z", NextWin(m, "FUNDING_00", CSeesareDst::Date(2026, 7, 2, 0, 5)), "2026-07-01T23:50:00Z");
   T_Str("active NY_MOC at 2026-03-10T19:55:00Z", ActiveWin(m, "NY_MOC", CSeesareDst::Date(2026, 3, 10, 19, 55)), "2026-03-10T19:50:00Z");
   T_Str("next NY_MOC after 2026-03-10T19:55:00Z", NextWin(m, "NY_MOC", CSeesareDst::Date(2026, 3, 10, 19, 55)), "2026-03-10T19:50:00Z");
   T_Str("active NY_MOC at 2026-03-10T20:55:00Z", ActiveWin(m, "NY_MOC", CSeesareDst::Date(2026, 3, 10, 20, 55)), "no");
   T_Str("next NY_MOC after 2026-03-10T20:55:00Z", NextWin(m, "NY_MOC", CSeesareDst::Date(2026, 3, 10, 20, 55)), "2026-03-11T19:50:00Z");
   T_Str("active WMR_FIX at 2026-10-30T15:45:00Z", ActiveWin(m, "WMR_FIX", CSeesareDst::Date(2026, 10, 30, 15, 45)), "2026-10-30T15:30:00Z");
   T_Str("next WMR_FIX after 2026-10-30T15:45:00Z", NextWin(m, "WMR_FIX", CSeesareDst::Date(2026, 10, 30, 15, 45)), "2026-10-30T15:30:00Z");
   T_Str("active US_NFP at 2026-03-10T13:00:00Z", ActiveWin(m, "US_NFP", CSeesareDst::Date(2026, 3, 10, 13, 0)), "no");
   T_Str("next US_NFP after 2026-03-10T13:00:00Z", NextWin(m, "US_NFP", CSeesareDst::Date(2026, 3, 10, 13, 0)), "2026-03-13T12:30:00Z");
   T_Str("multiplier 0.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(0.5), 4), 4), "0.0820");
   T_Str("multiplier 1.00", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(1.0), 4), 4), "0.0820");
   T_Str("multiplier 1.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(1.5), 4), 4), "0.1836");
   T_Str("multiplier 2.00", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(2.0), 4), 4), "0.3265");
   T_Str("multiplier 2.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(2.5), 4), 4), "0.5102");
   T_Str("multiplier 3.00", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(3.0), 4), 4), "0.7346");
   T_Str("multiplier 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(3.5), 4), 4), "1.0000");
   T_Str("multiplier 4.00", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(4.0), 4), 4), "1.0500");
   T_Str("multiplier 5.00", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(5.0), 4), 4), "1.1500");
   T_Str("multiplier 8.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(8.5), 4), 4), "1.5000");
   T_Str("multiplier 10.00", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::Multiplier(10.0), 4), 4), "1.5000");
   T_Str("plan L0 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.144, 1.0, 0.05), 4), 4), "1.3680");
   T_Str("plan L1 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.095, 1.0, 0.05), 4), 4), "0.9025");
   T_Str("plan L2 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.062, 1.0, 0.05), 4), 4), "0.5890");
   T_Str("plan L3 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.041, 1.0, 0.05), 4), 4), "0.3895");
   T_Str("plan L4 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.027, 1.0, 0.05), 4), 4), "0.2565");
   T_Str("plan L5 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.018, 1.0, 0.05), 4), 4), "0.1710");
   T_Str("plan L6 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.012, 1.0, 0.05), 4), 4), "0.1140");
   T_Str("plan L7 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.008, 1.0, 0.05), 4), 4), "0.0760");
   T_Str("plan L8 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.005, 1.0, 0.05), 4), 4), "0.0475");
   T_Str("plan L9 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0033, 1.0, 0.05), 4), 4), "0.0313");
   T_Str("plan L10 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0022, 1.0, 0.05), 4), 4), "0.0209");
   T_Str("plan L11 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0014, 1.0, 0.05), 4), 4), "0.0133");
   T_Str("plan L12 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0009, 1.0, 0.05), 4), 4), "0.0085");
   T_Str("plan L13 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0006, 1.0, 0.05), 4), 4), "0.0057");
   T_Str("plan L14 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0004, 1.0, 0.05), 4), 4), "0.0038");
   T_Str("plan L15 forex 3.50", CSeesareText::Fmt(CSeesareText::FloorDp(CSeesareLadder::PlanUsd(0.0003, 1.0, 0.05), 4), 4), "0.0028");
   T_Str("ladder L0 run 0 POSITIVE", Transition(0, 0, 1), "0/0");
   T_Str("ladder L0 run 0 NEGATIVE", Transition(0, 0, -1), "2/1");
   T_Str("ladder L2 run 1 NEGATIVE", Transition(2, 1, -1), "5/2");
   T_Str("ladder L5 run 2 NEGATIVE", Transition(5, 2, -1), "9/3");
   T_Str("ladder L14 run 3 NEGATIVE", Transition(14, 3, -1), "15/4");
   T_Str("ladder L15 run 4 NEGATIVE", Transition(15, 4, -1), "15/5");
   T_Str("ladder L7 run 2 MANUAL", Transition(7, 2, 0), "7/2");
   T_Str("ladder L7 run 2 POSITIVE", Transition(7, 2, 1), "6/0");
   T_Str("ladder L0 run 5 POSITIVE", Transition(0, 5, 1), "0/0");
   T_Int("classify STOP +0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)0, 0.5, (ENUM_SEESARE_TIME_POLICY)0), -1);
   T_Int("classify STOP +0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)0, 0.5, (ENUM_SEESARE_TIME_POLICY)1), -1);
   T_Int("classify STOP -0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)0, -0.5, (ENUM_SEESARE_TIME_POLICY)0), -1);
   T_Int("classify STOP -0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)0, -0.5, (ENUM_SEESARE_TIME_POLICY)1), -1);
   T_Int("classify TARGET +0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)1, 0.5, (ENUM_SEESARE_TIME_POLICY)0), 1);
   T_Int("classify TARGET +0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)1, 0.5, (ENUM_SEESARE_TIME_POLICY)1), 1);
   T_Int("classify TARGET -0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)1, -0.5, (ENUM_SEESARE_TIME_POLICY)0), 1);
   T_Int("classify TARGET -0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)1, -0.5, (ENUM_SEESARE_TIME_POLICY)1), 1);
   T_Int("classify TIME +0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)2, 0.5, (ENUM_SEESARE_TIME_POLICY)0), 0);
   T_Int("classify TIME +0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)2, 0.5, (ENUM_SEESARE_TIME_POLICY)1), 0);
   T_Int("classify TIME -0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)2, -0.5, (ENUM_SEESARE_TIME_POLICY)0), 0);
   T_Int("classify TIME -0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)2, -0.5, (ENUM_SEESARE_TIME_POLICY)1), -1);
   T_Int("classify HUMAN +0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)3, 0.5, (ENUM_SEESARE_TIME_POLICY)0), 0);
   T_Int("classify HUMAN +0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)3, 0.5, (ENUM_SEESARE_TIME_POLICY)1), 0);
   T_Int("classify HUMAN -0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)3, -0.5, (ENUM_SEESARE_TIME_POLICY)0), 0);
   T_Int("classify HUMAN -0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)3, -0.5, (ENUM_SEESARE_TIME_POLICY)1), 0);
   T_Int("classify BROKER +0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)4, 0.5, (ENUM_SEESARE_TIME_POLICY)0), -1);
   T_Int("classify BROKER +0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)4, 0.5, (ENUM_SEESARE_TIME_POLICY)1), -1);
   T_Int("classify BROKER -0.5 policy 0", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)4, -0.5, (ENUM_SEESARE_TIME_POLICY)0), -1);
   T_Int("classify BROKER -0.5 policy 1", (long)CSeesareLadder::Classify((ENUM_SEESARE_CLOSE)4, -0.5, (ENUM_SEESARE_TIME_POLICY)1), -1);
   T_Bool("decimal [0.4321] with 4 places is valid", CSeesareText::IsDecimal("0.4321", 4) == true, "");
   T_Bool("decimal [-0.4321] with 4 places is valid", CSeesareText::IsDecimal("-0.4321", 4) == true, "");
   T_Bool("decimal [-0.0000] with 4 places is invalid", CSeesareText::IsDecimal("-0.0000", 4) == false, "");
   T_Bool("decimal [00.4321] with 4 places is invalid", CSeesareText::IsDecimal("00.4321", 4) == false, "");
   T_Bool("decimal [0.432] with 4 places is invalid", CSeesareText::IsDecimal("0.432", 4) == false, "");
   T_Bool("decimal [1] with 0 places is valid", CSeesareText::IsDecimal("1", 0) == true, "");
   T_Bool("decimal [-1] with 0 places is valid", CSeesareText::IsDecimal("-1", 0) == true, "");
   T_Bool("decimal [1.] with 0 places is invalid", CSeesareText::IsDecimal("1.", 0) == false, "");
   T_Bool("decimal [12.50] with 2 places is valid", CSeesareText::IsDecimal("12.50", 2) == true, "");
   T_Bool("decimal [+1.00] with 2 places is invalid", CSeesareText::IsDecimal("+1.00", 2) == false, "");
   T_Bool("decimal [1e5] with 0 places is invalid", CSeesareText::IsDecimal("1e5", 0) == false, "");
   T_Bool("decimal [] with 2 places is invalid", CSeesareText::IsDecimal("", 2) == false, "");
  }
//--- END GENERATED VECTORS

//+------------------------------------------------------------------+
//| Events of the ledger test (values from the generated arrays)     |
//+------------------------------------------------------------------+
void FillEvent(const int i, SSeesareEvent &e)
  {
   e.Clear();
   e.mode       = (ENUM_SEESARE_MODE)VEC_MODE[i];
   e.module     = "TOKYO_FIX";
   e.domain     = "forex";
   e.symbol     = "USDJPY";
   e.side       = VEC_SIDE[i];
   e.digits     = 3;
   e.utc_open   = (datetime)((long)CSeesareDst::Date(2026, 11, 4, 23, 0) + (long)i * 86400);
   e.utc_close  = (datetime)((long)e.utc_open + 115 * 60);
   e.close_by   = (ENUM_SEESARE_CLOSE)VEC_BY[i];
   e.ratio      = VEC_RATIO[i];
   e.risk_usd   = VEC_RISK[i];
   e.volume     = VEC_VOL[i];
   e.entry      = 151.234;
   e.lower      = VEC_LOWER[i];
   e.upper      = VEC_UPPER[i];
   e.exit_price = VEC_EXIT[i];
   e.delta_usd  = VEC_DELTA[i];
   e.deals      = VEC_DEALS[i];
  }

//--- the 360-event lifecycle: two target hits, then one stop, one event a day (twin: lock_event)
void FillLockEvent(const int i, SSeesareEvent &e)
  {
   bool win = (i % 3 != 2);
   e.Clear();
   e.mode       = SEESARE_REAL;
   e.module     = "LOCKTEST";
   e.domain     = "forex";
   e.symbol     = "USDJPY";
   e.side       = 1;
   e.digits     = 3;
   e.utc_open   = (datetime)((long)CSeesareDst::Date(2027, 1, 4, 23, 0) + (long)i * 86400);
   e.utc_close  = (datetime)((long)e.utc_open + 3600);
   e.close_by   = (win ? SEESARE_BY_TARGET : SEESARE_BY_STOP);
   e.ratio      = 3.5;
   e.risk_usd   = 1.06;
   e.volume     = 0.01;
   e.entry      = 151.234;
   e.lower      = 151.084;
   e.upper      = 151.759;
   e.exit_price = (win ? 151.759 : 151.084);
   e.delta_usd  = (win ? 0.25 : -0.4);
   e.deals      = IntegerToString(60000000 + i);
  }

//+------------------------------------------------------------------+
//| File helpers                                                     |
//+------------------------------------------------------------------+
string JoinLines(const string &lines[], const int count)
  {
   string s = "";
   for(int i = 0; i < count; i++)
      s += lines[i] + "\r\n";
   return s;
  }

//--- writes `content` to the ledger file, tries to open the lifecycle, restores `original`; true if Open succeeded
bool OpenWithLedger(const string path, const string &content[], const int content_n, const string &original[], const int original_n,
                    const bool adopt, string &error)
  {
   CSeesareFiles::WriteAll(path, JoinLines(content, content_n));
   CSeesareCycleLedger trial;
   bool ok = trial.Open(g_root, VEC_LIFE, 0, adopt);
   error = trial.LastError();
   CSeesareFiles::WriteAll(path, JoinLines(original, original_n));
   return ok;
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
//| Clock object and gate helpers that need no market data           |
//+------------------------------------------------------------------+
void ClockObjectTests(void)
  {
   CSeesareClock c;
   bool ok = c.Init(SEESARE_SERVER_GMT2_US, 0, 300);
   T_Bool("clock: GMT2_US scheme accepted", ok, c.LastError());
   T_Str("clock: UTC -> server, US summer (+3)", CSeesareDst::IsoUtc(c.UtcToServer(CSeesareDst::Date(2026, 3, 10, 0, 0))), "2026-03-10T03:00:00Z");
   T_Str("clock: UTC -> server, winter (+2)", CSeesareDst::IsoUtc(c.UtcToServer(CSeesareDst::Date(2026, 3, 2, 0, 0))), "2026-03-02T02:00:00Z");
   T_Str("clock: server -> UTC round trip", CSeesareDst::IsoUtc(c.ServerToUtc(c.UtcToServer(CSeesareDst::Date(2026, 7, 1, 13, 45)))), "2026-07-01T13:45:00Z");
   T_Str("clock: Tokyo is server-independent", CSeesareDst::IsoUtc(c.VenueTime(SEESARE_VENUE_TOKYO, CSeesareDst::Date(2026, 7, 1, 0, 0))), "2026-07-01T09:00:00Z");
   CSeesareClock f;
   f.Init(SEESARE_SERVER_FIXED, 330, 300);
   T_Str("clock: fixed +5:30", CSeesareDst::IsoUtc(f.UtcToServer(CSeesareDst::Date(2026, 1, 1, 0, 0))), "2026-01-01T05:30:00Z");
   CSeesareClock bad;
   T_Bool("clock: out-of-range fixed offset refused", !bad.Init(SEESARE_SERVER_FIXED, 15 * 60, 300), "");
   T_Bool("gate: blackout 23:55-00:10 holds 00:05", CSeesareSpreadGate::InMinuteRange(5, 23 * 60 + 55, 10), "");
   T_Bool("gate: blackout 23:55-00:10 releases 00:10", !CSeesareSpreadGate::InMinuteRange(10, 23 * 60 + 55, 10), "");
   T_Bool("gate: blackout 16:55-17:10 holds 17:00", CSeesareSpreadGate::InMinuteRange(17 * 60, 16 * 60 + 55, 17 * 60 + 10), "");
   CSeesareSpreadGate g;
   T_Bool("gate: a configuration without any cap is refused", !g.Configure(0.0, 0.0, 900, 15), "");
   T_Bool("gate: a 15% boundary cap is accepted", g.Configure(0.0, 0.15, 900, 15), g.LastError());
   CSeesareTimingMatrix m;
   bool dup = m.Add("X", SEESARE_VENUE_LONDON, "10:00", "11:00", SEESARE_MASK_ALL) &&
              !m.Add("X", SEESARE_VENUE_LONDON, "12:00", "13:00", SEESARE_MASK_ALL);
   T_Bool("matrix: duplicate window id refused", dup, m.LastError());
   T_Bool("matrix: server-clock window refused", !m.Add("Y", SEESARE_VENUE_SERVER, "10:00", "11:00", SEESARE_MASK_ALL), "");
   T_Bool("matrix: bad time refused", !m.Add("Z", SEESARE_VENUE_LONDON, "24:00", "11:00", SEESARE_MASK_ALL), "");
  }

//+------------------------------------------------------------------+
//| Cycle ledger: record, verify, restart, tamper, outbox            |
//+------------------------------------------------------------------+
void LedgerTests(void)
  {
   CSeesareCycleLedger L;
   bool ok = L.Open(g_root, VEC_LIFE, CSeesareDst::Date(2026, 11, 1), false);
   T_Bool("ledger: open a new lifecycle", ok, L.LastError());
   if(!ok)
      return;
   T_Str("ledger: genesis line", L.LineAt(0), VEC_GENESIS);
   T_Str("ledger: planned delta at L0, forex, 3.5", CSeesareText::Fmt(L.PlanUsdAt(3.5, "forex"), 4), "1.3680");
   for(int i = 0; i < VEC_EVENTS; i++)
     {
      SSeesareEvent e;
      FillEvent(i, e);
      string h = "";
      bool r = L.Record(e, h);
      T_Bool("ledger: record event " + IntegerToString(i + 1), r, L.LastError());
      if(!r)
         return;
      T_Str("ledger: hash of event " + IntegerToString(i + 1), h, VEC_HASH[i]);
     }
   T_Str("ledger: first event line", L.LineAt(1), VEC_EVENT1);
   T_Str("ledger: cycle 1 anchor", L.AnchorLine(0), VEC_ANCHOR1);
   T_Str("ledger: head", L.Head(), VEC_HEAD);
   T_Int("ledger: level", L.Level(), VEC_LEVEL);
   T_Int("ledger: negative run", L.NegRun(), VEC_NEG_RUN);
   T_Int("ledger: real events", L.RealCount(), VEC_REAL);
   T_Int("ledger: shadow events", L.ShadowCount(), VEC_SHADOW);
   T_Int("ledger: open cycle", L.Cycle(), VEC_CYCLE);
   T_Str("ledger: lifecycle net", CSeesareText::Fmt(L.LifeNetUSD(), 4), VEC_LIFE_NET);
   T_Str("ledger: lifecycle max drawdown", CSeesareText::Fmt(L.LifeMaxDrawdownUSD(), 4), VEC_LIFE_DD);
   T_Str("ledger: envelope room", CSeesareText::Fmt(L.EnvelopeRoomUSD(), 4), VEC_ROOM);
   T_Bool("ledger: no warning", L.LastWarning() == "", L.LastWarning());
//--- files on disk
   string dir = L.Dir();
   string lines[];
   int n = CSeesareFiles::ReadLines(dir + "\\ledger.txt", lines);
   T_Int("ledger.txt: lines", n, VEC_EVENTS + 1);
   T_Str("ledger.txt: last line", (n > 0 ? lines[n - 1] : ""), L.LineAt(VEC_EVENTS));
   string anchors[];
   int na = CSeesareFiles::ReadLines(dir + "\\anchors.txt", anchors);
   T_Int("anchors.txt: lines", na, 1);
   T_Str("anchors.txt: cycle 1", (na > 0 ? anchors[0] : ""), VEC_ANCHOR1);
   T_Int("outbox: messages written", L.OutboxSeq(), VEC_MESSAGES);
   T_Bool("outbox: first message", CSeesareFiles::Exists(dir + "\\outbox\\0000000001.msg"), "");
   T_Bool("outbox: last message", CSeesareFiles::Exists(dir + "\\outbox\\" + CSeesareOutbox::Name(VEC_MESSAGES) + ".msg"), "");
   T_Bool("outbox: nothing beyond the last", !CSeesareFiles::Exists(dir + "\\outbox\\" + CSeesareOutbox::Name(VEC_MESSAGES + 1) + ".msg"), "");
   string msg[];
   int nm = CSeesareFiles::ReadLines(dir + "\\outbox\\0000000002.msg", msg);
   T_Str("outbox: message 2 carries event 1", (nm > 7 ? msg[7] : ""), VEC_EVENT1);
   string body = "";
   for(int i = 0; i < nm - 1; i++)
      body += msg[i] + "\n";
   T_Str("outbox: message 2 checksum", (nm > 0 ? msg[nm - 1] : ""), "sum=" + CSeesareSha256::Hex(body));
//--- envelope guard
   T_Bool("guard: allows 1.06 USD of risk", L.AllowsRealRisk(1.06), "");
   T_Bool("guard: refuses risk beyond the room", !L.AllowsRealRisk(L.EnvelopeRoomUSD() + 0.0002), "");
//--- refusals leave everything unchanged
   string h2 = "";
   SSeesareEvent late;
   FillEvent(0, late);
   bool refused = !L.Record(late, h2);
   T_Bool("refuse: event out of time order", refused && L.Head() == VEC_HEAD, L.LastError());
   SSeesareEvent nodeal;
   FillEvent(VEC_EVENTS - 1, nodeal);
   nodeal.utc_open  = (datetime)((long)nodeal.utc_open + 2 * 86400);
   nodeal.utc_close = (datetime)((long)nodeal.utc_close + 2 * 86400);
   nodeal.deals = "";
   refused = !L.Record(nodeal, h2);
   T_Bool("refuse: real event without deal tickets", refused && L.Head() == VEC_HEAD, L.LastError());
   SSeesareEvent baddomain;
   FillEvent(VEC_EVENTS - 1, baddomain);
   baddomain.utc_open  = nodeal.utc_open;
   baddomain.utc_close = nodeal.utc_close;
   baddomain.domain = "fx";
   refused = !L.Record(baddomain, h2);
   T_Bool("refuse: unknown domain", refused && L.Head() == VEC_HEAD, L.LastError());
   T_Int("refuse: no outbox message for refused events", L.OutboxSeq(), VEC_MESSAGES);
//--- restart
   CSeesareCycleLedger R;
   ok = R.Open(g_root, VEC_LIFE, 0, false);
   T_Bool("restart: reopen", ok, R.LastError());
   T_Str("restart: same head", R.Head(), VEC_HEAD);
   T_Int("restart: same level", R.Level(), VEC_LEVEL);
   T_Int("restart: same real count", R.RealCount(), VEC_REAL);
   T_Str("restart: same envelope room", CSeesareText::Fmt(R.EnvelopeRoomUSD(), 4), VEC_ROOM);
   T_Int("restart: no duplicate messages", R.OutboxSeq(), VEC_MESSAGES);
   double other[];
   CSeesareLadder::Defaults(other);
   other[0] = 0.15;
   CSeesareCycleLedger tuned;
   bool tuned_refused = tuned.SetLadder(other) && !tuned.Open(g_root, VEC_LIFE, 0, false);
   T_Bool("restart: a different ladder is refused", tuned_refused, tuned.LastError());
//--- tamper, truncation, lost snapshot (the original ledger is restored after each case)
   string path = dir + "\\ledger.txt";
   string err = "";
   string edited[];
   ArrayCopy(edited, lines);
   int replaced = StringReplace(edited[6], "delta=-0.2950", "delta=0.2950");
   T_Int("tamper: test line found", replaced, 1);
   bool caught = !OpenWithLedger(path, edited, n, lines, n, false, err);
   T_Bool("tamper: a changed amount is caught", caught && StringFind(err, "hash mismatch") >= 0, err);
   caught = !OpenWithLedger(path, lines, n - 1, lines, n, false, err);
   T_Bool("tamper: a deleted last line is caught", caught && StringFind(err, "lost lines") >= 0, err);
   string garbage[];
   ArrayCopy(garbage, lines);
   ArrayResize(garbage, n + 1);
   garbage[n] = "v=1|life=SELFTEST|k=21|forged";
   caught = !OpenWithLedger(path, garbage, n + 1, lines, n, false, err);
   T_Bool("tamper: an appended line is caught", caught, err);
   string swapped[];
   ArrayCopy(swapped, lines);
   swapped[7] = lines[8];
   swapped[8] = lines[7];
   caught = !OpenWithLedger(path, swapped, n, lines, n, false, err);
   T_Bool("tamper: swapped lines are caught", caught, err);
   CSeesareCycleLedger again;
   bool reopened = again.Open(g_root, VEC_LIFE, 0, false);
   T_Bool("tamper: the restored ledger opens", reopened, again.LastError());
   FileDelete(dir + "\\state.dat", FILE_COMMON);
   FileDelete(dir + "\\state.dat.bak", FILE_COMMON);
   CSeesareCycleLedger nostate;
   bool stopped = !nostate.Open(g_root, VEC_LIFE, 0, false);
   T_Bool("snapshot: a missing state.dat stops the open", stopped && StringFind(nostate.LastError(), "adopt_ledger") >= 0, nostate.LastError());
   CSeesareCycleLedger adopt;
   ok = adopt.Open(g_root, VEC_LIFE, 0, true);
   T_Bool("snapshot: adopt_ledger reopens", ok && adopt.Head() == VEC_HEAD, adopt.LastError());
   T_Int("snapshot: adopting queues every message again under new numbers", adopt.OutboxSeq(), 2 * VEC_MESSAGES);
  }

void LockTest(void)
  {
   CSeesareCycleLedger L;
   bool ok = L.Open(g_root, "SELFTEST_LOCK", CSeesareDst::Date(2026, 11, 1), false);
   T_Bool("lock: open", ok, L.LastError());
   if(!ok)
      return;
   string h = "";
   for(int i = 0; i < 360; i++)
     {
      SSeesareEvent e;
      FillLockEvent(i, e);
      if(!L.Record(e, h))
        {
         T_Bool("lock: record event " + IntegerToString(i + 1), false, L.LastError());
         return;
        }
     }
   T_Bool("lock: locked after 360 real events", L.Locked(), "");
   T_Int("lock: 36 cycles closed", L.CyclesClosed(), 36);
   T_Str("lock: head", L.Head(), VEC_LOCK_HEAD);
   T_Str("lock: cycle 36 anchor", L.AnchorLine(35), VEC_LOCK_ANCHOR36);
   T_Int("lock: messages (genesis + 360 events + 36 audits + lifecycle)", L.OutboxSeq(), VEC_LOCK_MESSAGES);
   SSeesareEvent more;
   FillLockEvent(360, more);
   bool refused = !L.Record(more, h);
   T_Bool("lock: a 361st event is refused", refused, L.LastError());
   T_Bool("lock: no real risk after the lock", !L.AllowsRealRisk(1.0), "");
  }

//+------------------------------------------------------------------+
//| This terminal's clock (live only; INFO lines, not counted)        |
//+------------------------------------------------------------------+
void LiveClockReport(void)
  {
   if(MQLInfoInteger(MQL_TESTER) != 0)
      return;
   CSeesareClock probe;
   probe.Init(SEESARE_SERVER_MEASURED, 0, 300);
   datetime now = TimeGMT();
   Print("INFO  TimeGMT ", CSeesareDst::IsoUtc(now), "; TimeTradeServer ", TimeToString(TimeTradeServer(), TIME_DATE | TIME_SECONDS), " (server clock)");
   if(!probe.Healthy())
     {
      Print("INFO  the server offset cannot be measured now: ", probe.LastError());
      return;
     }
   long eu = CSeesareDst::SchemeOffset(SEESARE_SERVER_GMT2_EU, now, 0);
   long us = CSeesareDst::SchemeOffset(SEESARE_SERVER_GMT2_US, now, 0);
   Print("INFO  measured server offset ", CSeesareDst::OffsetText(probe.MeasuredOffset()), "; GMT0 expects +0:00, GMT2_EU expects ",
         CSeesareDst::OffsetText(eu), ", GMT2_US expects ", CSeesareDst::OffsetText(us));
   if(eu == us)
      Print("INFO  Europe and the US are on the same clock this week, so GMT2_EU and GMT2_US look alike: run this again between ",
            "the 2nd and the last Sunday of March, or in the week after the last Sunday of October, to tell them apart");
   CSeesareClock declared;
   declared.Init(InpScheme, 0, 300);
   if(declared.Healthy())
      Print("INFO  declared scheme ", CSeesareDst::SchemeName(InpScheme), " matches this server now");
   else
      Print("INFO  declared scheme ", CSeesareDst::SchemeName(InpScheme), " does NOT match: ", declared.LastError());
   CSeesareTimingMatrix m;
   m.LoadDefaults();
   SSeesareUtcWindow w[];
   int n = m.OnUtcDate(now, w);
   for(int i = 0; i < n; i++)
      Print("INFO  window ", w[i].id, "  UTC ", CSeesareDst::IsoUtc(w[i].start_utc), " - ", CSeesareDst::IsoUtc(w[i].end_utc),
            "  server ", TimeToString(probe.UtcToServer(w[i].start_utc), TIME_DATE | TIME_MINUTES));
   CSeesareSpreadGate gate;
   SSeesareUtcWindow open_now;
   open_now.id         = "SELFTEST";
   open_now.index      = -1;
   open_now.start_utc  = (datetime)((long)now - 60);
   open_now.end_utc    = (datetime)((long)now + 600);
   open_now.local_date = CSeesareDst::Midnight(now);
   SSeesareGateResult res;
   double boundary = 150.0 * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   gate.Check(_Symbol, 1, boundary, open_now, probe, res);
   Print("INFO  spread gate on ", _Symbol, " (150-point stop): ", CSeesareSpreadGate::VerdictName(res.verdict), "  ", res.reason);
  }

//+------------------------------------------------------------------+
void OnStart()
  {
   g_root = "seesare_selftest\\run" + IntegerToString((long)TimeLocal()) + "_" + IntegerToString(GetTickCount() % 100000);
   Print("SEESARE Phase 1 self-test: start (files under Common\\Files\\", g_root, ")");
   CSeesareTimingMatrix m;
   m.LoadDefaults();
   T_Int("matrix: default windows", m.Count(), 11);
   GeneratedVectors(m);
   ClockObjectTests();
   LedgerTests();
   if(InpRunLock)
      LockTest();
   if(!InpKeepFiles)
     {
      DeleteTree(g_root);
      FolderDelete("seesare_selftest", FILE_COMMON);
     }
   LiveClockReport();
   Print("SEESARE Phase 1 self-test: ", g_pass, " passed, ", g_fail, " failed");
   if(g_fail > 0)
      Alert("SEESARE Phase 1 self-test: ", g_fail, " check(s) FAILED - see the Experts tab");
  }
//+------------------------------------------------------------------+

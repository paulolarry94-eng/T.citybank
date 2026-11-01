//+------------------------------------------------------------------+
//|                                       Seesare/Core/Calendar.mqh  |
//| SEESARE router, Phase 2: Tokyo business days, gotobi fix dates,  |
//| last weekday of the month. UNCOMPILED SOURCE.                    |
//| Twin: tools/seesare_flows.py. Its gotobi dates equal the research |
//| rule (research/truth/strategies/tokyo_fix_gotobi_v1.py) for every |
//| date 2024-2035 (research/truth/tests/test_seesare_phase2.py).    |
//| Dates are held as datetime at 00:00 of the date.                 |
//+------------------------------------------------------------------+
#ifndef SEESARE_CORE_CALENDAR_MQH
#define SEESARE_CORE_CALENDAR_MQH

#include <Seesare\Core\Clock.mqh>

//--- BEGIN GENERATED HOLIDAYS: python3 tools/seesare_flows.py --holidays  (Japanese public holidays, holidays.Japan, 2024-2035)
#define SEESARE_JP_FIRST_YEAR 2024
#define SEESARE_JP_LAST_YEAR  2035
#define SEESARE_JP_COUNT      218
const int SEESARE_JP_HOLIDAYS[SEESARE_JP_COUNT] =
  {
   20240101, 20240108, 20240211, 20240212, 20240223, 20240320, 20240429, 20240503, 20240504, 20240505,
   20240506, 20240715, 20240811, 20240812, 20240916, 20240922, 20240923, 20241014, 20241103, 20241104,
   20241123, 20250101, 20250113, 20250211, 20250223, 20250224, 20250320, 20250429, 20250503, 20250504,
   20250505, 20250506, 20250721, 20250811, 20250915, 20250923, 20251013, 20251103, 20251123, 20251124,
   20260101, 20260112, 20260211, 20260223, 20260320, 20260429, 20260503, 20260504, 20260505, 20260506,
   20260720, 20260811, 20260921, 20260922, 20260923, 20261012, 20261103, 20261123, 20270101, 20270111,
   20270211, 20270223, 20270321, 20270322, 20270429, 20270503, 20270504, 20270505, 20270719, 20270811,
   20270920, 20270923, 20271011, 20271103, 20271123, 20280101, 20280110, 20280211, 20280223, 20280320,
   20280429, 20280503, 20280504, 20280505, 20280717, 20280811, 20280918, 20280922, 20281009, 20281103,
   20281123, 20290101, 20290108, 20290211, 20290212, 20290223, 20290320, 20290429, 20290430, 20290503,
   20290504, 20290505, 20290716, 20290811, 20290917, 20290923, 20290924, 20291008, 20291103, 20291123,
   20300101, 20300114, 20300211, 20300223, 20300320, 20300429, 20300503, 20300504, 20300505, 20300506,
   20300715, 20300811, 20300812, 20300916, 20300923, 20301014, 20301103, 20301104, 20301123, 20310101,
   20310113, 20310211, 20310223, 20310224, 20310321, 20310429, 20310503, 20310504, 20310505, 20310506,
   20310721, 20310811, 20310915, 20310923, 20311013, 20311103, 20311123, 20311124, 20320101, 20320112,
   20320211, 20320223, 20320320, 20320429, 20320503, 20320504, 20320505, 20320719, 20320811, 20320920,
   20320921, 20320922, 20321011, 20321103, 20321123, 20330101, 20330110, 20330211, 20330223, 20330320,
   20330321, 20330429, 20330503, 20330504, 20330505, 20330718, 20330811, 20330919, 20330923, 20331010,
   20331103, 20331123, 20340101, 20340102, 20340109, 20340211, 20340223, 20340320, 20340429, 20340503,
   20340504, 20340505, 20340717, 20340811, 20340918, 20340923, 20341009, 20341103, 20341123, 20350101,
   20350108, 20350211, 20350212, 20350223, 20350321, 20350429, 20350430, 20350503, 20350504, 20350505,
   20350716, 20350811, 20350917, 20350923, 20350924, 20351008, 20351103, 20351123
  };
//--- END GENERATED HOLIDAYS

class CSeesareCalendar
  {
public:
   static int        Ymd(const datetime d)
     {
      MqlDateTime s;
      TimeToStruct(d, s);
      return s.year * 10000 + s.mon * 100 + s.day;
     }
   static bool       Covered(const int year)
     {
      return (year >= SEESARE_JP_FIRST_YEAR && year <= SEESARE_JP_LAST_YEAR);
     }
   static bool       IsJpHoliday(const datetime d)
     {
      int key = Ymd(d);
      int lo = 0;
      int hi = SEESARE_JP_COUNT - 1;
      while(lo <= hi)
        {
         int mid = (lo + hi) / 2;
         if(SEESARE_JP_HOLIDAYS[mid] == key)
            return true;
         if(SEESARE_JP_HOLIDAYS[mid] < key)
            lo = mid + 1;
         else
            hi = mid - 1;
        }
      return false;
     }
   //--- weekday, not a Japanese holiday, not the bank year-end (31 Dec - 3 Jan): the research rule
   static bool       IsTokyoBusinessDay(const datetime d)
     {
      MqlDateTime s;
      TimeToStruct(d, s);
      if(s.day_of_week == 0 || s.day_of_week == 6)
         return false;
      if(s.mon == 12 && s.day == 31)
         return false;
      if(s.mon == 1 && s.day <= 3)
         return false;
      return !IsJpHoliday(d);
     }
   static datetime   PreviousBusinessDay(const datetime d)
     {
      datetime x = CSeesareDst::Midnight(d);
      for(int i = 0; i < 31 && !IsTokyoBusinessDay(x); i++)
         x = (datetime)((long)x - SEESARE_DAY_SEC);
      return x;
     }
   static int        LastDay(const int y, const int m)
     {
      int ny = (m == 12 ? y + 1 : y);
      int nm = (m == 12 ? 1 : m + 1);
      datetime first_next = CSeesareDst::Date(ny, nm, 1);
      MqlDateTime s;
      TimeToStruct((datetime)((long)first_next - SEESARE_DAY_SEC), s);
      return s.day;
     }
   //--- d: a Tokyo date. True if it is the fix date of the 5th, 10th, 15th, 20th, 25th or last day of its month, or
   //--- of the next month's 5th moved back (a candidate on a non-business day moves to the previous business day).
   //--- known = false outside the holiday table: the caller must not trade then.
   static bool       IsGotobiFix(const datetime d, bool &known)
     {
      MqlDateTime s;
      TimeToStruct(d, s);
      int ny = (s.mon == 12 ? s.year + 1 : s.year);
      int nm = (s.mon == 12 ? 1 : s.mon + 1);
      known = (Covered(s.year) && Covered(ny));
      if(!known)
         return false;
      datetime day0 = CSeesareDst::Midnight(d);
      int days[6] = {5, 10, 15, 20, 25, 0};
      for(int k = 0; k < 2; k++)
        {
         int y = (k == 0 ? s.year : ny);
         int m = (k == 0 ? s.mon : nm);
         days[5] = LastDay(y, m);
         for(int j = 0; j < 6; j++)
            if(PreviousBusinessDay(CSeesareDst::Date(y, m, days[j])) == day0)
               return true;
        }
      return false;
     }
   //--- a weekday whose next weekday falls in another month (weekend days are never it)
   static bool       IsLastWeekdayOfMonth(const datetime d)
     {
      int dow = CSeesareDst::DayOfWeek(d);
      if(dow == 0 || dow == 6)
         return false;
      datetime nxt = (datetime)((long)CSeesareDst::Midnight(d) + SEESARE_DAY_SEC);
      while(CSeesareDst::DayOfWeek(nxt) == 0 || CSeesareDst::DayOfWeek(nxt) == 6)
         nxt = (datetime)((long)nxt + SEESARE_DAY_SEC);
      MqlDateTime a;
      MqlDateTime b;
      TimeToStruct(d, a);
      TimeToStruct(nxt, b);
      return (a.mon != b.mon);
     }
  };

#endif

//+------------------------------------------------------------------+
//|                                          Seesare/Core/Clock.mqh  |
//| SEESARE P26 router, Phase 1: Dynamic Clock and Timing Matrix.    |
//| UNCOMPILED SOURCE. Python twin: tools/seesare_verify.py (clock   |
//| section); the twin's DST rules match the IANA time-zone database |
//| for every hour 2011-2035 (research/truth/tests/                  |
//| test_seesare_phase1.py).                                         |
//|                                                                  |
//| Everything inside the router is UTC seconds. Flow windows are    |
//| declared in their venue's wall time; DST is computed from the    |
//| legal rules (no broker data involved), so the US/EU mismatch     |
//| weeks and the switch nights resolve without waiting for the      |
//| broker. Server time is used only to read bars and to cross-check.|
//+------------------------------------------------------------------+
#ifndef SEESARE_CORE_CLOCK_MQH
#define SEESARE_CORE_CLOCK_MQH

#include <Seesare\Core\Text.mqh>

#define SEESARE_DAY_SEC      86400
#define SEESARE_HOUR_SEC     3600
#define SEESARE_MASK_MON_FRI 62      // day masks on the venue's local date: bit 0 = Sunday ... bit 6 = Saturday
#define SEESARE_MASK_FRI     32
#define SEESARE_MASK_ALL     127

enum ENUM_SEESARE_VENUE
  {
   SEESARE_VENUE_UTC       = 0,   // UTC
   SEESARE_VENUE_LONDON    = 1,   // London: UTC+0, UTC+1 in EU summer time
   SEESARE_VENUE_FRANKFURT = 2,   // Frankfurt: UTC+1, UTC+2 in EU summer time
   SEESARE_VENUE_NEW_YORK  = 3,   // New York: UTC-5, UTC-4 in US summer time
   SEESARE_VENUE_TOKYO     = 4,   // Tokyo: UTC+9, no DST
   SEESARE_VENUE_SERVER    = 5    // broker server clock (CSeesareClock only)
  };

enum ENUM_SEESARE_SERVER_SCHEME
  {
   SEESARE_SERVER_GMT0     = 0,   // server clock = UTC
   SEESARE_SERVER_GMT2_EU  = 1,   // UTC+2, UTC+3 on EU summer dates
   SEESARE_SERVER_GMT2_US  = 2,   // UTC+2, UTC+3 on US summer dates (server midnight = 17:00 New York)
   SEESARE_SERVER_FIXED    = 3,   // UTC + fixed minutes, no DST
   SEESARE_SERVER_MEASURED = 4    // live only: the offset the terminal reports now
  };

//+------------------------------------------------------------------+
//| DST rules and conversions (all static, no state)                 |
//| US: 2nd Sunday of March 07:00 UTC to 1st Sunday of November      |
//|     06:00 UTC (since 2007). EU: last Sunday of March 01:00 UTC   |
//|     to last Sunday of October 01:00 UTC (since 1996). Tokyo: none.|
//| If a government changes these laws, change UsStart..EuEnd, the   |
//| twin, and regenerate the self-test vectors.                      |
//+------------------------------------------------------------------+
class CSeesareDst
  {
public:
   static datetime   Date(const int y, const int mon, const int d, const int h = 0, const int mi = 0)
     {
      MqlDateTime s;
      ZeroMemory(s);
      s.year = y;
      s.mon  = mon;
      s.day  = d;
      s.hour = h;
      s.min  = mi;
      s.sec  = 0;
      return StructToTime(s);
     }
   static int        Year(const datetime t)
     {
      MqlDateTime s;
      TimeToStruct(t, s);
      return s.year;
     }
   static int        DayOfWeek(const datetime t)
     {
      MqlDateTime s;
      TimeToStruct(t, s);
      return s.day_of_week;
     }
   static datetime   Midnight(const datetime t)
     {
      return (datetime)(((long)t / SEESARE_DAY_SEC) * SEESARE_DAY_SEC);
     }
   static int        MinuteOfDay(const datetime t)
     {
      return (int)(((long)t % SEESARE_DAY_SEC) / 60);
     }
   static datetime   SundayOnOrAfter(const int y, const int mon, const int d)
     {
      datetime t = Date(y, mon, d);
      return (datetime)((long)t + (long)((7 - DayOfWeek(t)) % 7) * SEESARE_DAY_SEC);
     }
   static datetime   UsStart(const int y) { return (datetime)((long)SundayOnOrAfter(y, 3, 8) + 7 * SEESARE_HOUR_SEC); }
   static datetime   UsEnd(const int y)   { return (datetime)((long)SundayOnOrAfter(y, 11, 1) + 6 * SEESARE_HOUR_SEC); }
   static datetime   EuStart(const int y) { return (datetime)((long)SundayOnOrAfter(y, 3, 25) + SEESARE_HOUR_SEC); }
   static datetime   EuEnd(const int y)   { return (datetime)((long)SundayOnOrAfter(y, 10, 25) + SEESARE_HOUR_SEC); }
   static bool       UsSummer(const datetime utc)
     {
      int y = Year(utc);
      return (utc >= UsStart(y) && utc < UsEnd(y));
     }
   static bool       EuSummer(const datetime utc)
     {
      int y = Year(utc);
      return (utc >= EuStart(y) && utc < EuEnd(y));
     }
   static long       StdOffset(const ENUM_SEESARE_VENUE v)
     {
      if(v == SEESARE_VENUE_FRANKFURT)
         return SEESARE_HOUR_SEC;
      if(v == SEESARE_VENUE_NEW_YORK)
         return -5 * SEESARE_HOUR_SEC;
      if(v == SEESARE_VENUE_TOKYO)
         return 9 * SEESARE_HOUR_SEC;
      return 0;
     }
   static bool       HasDst(const ENUM_SEESARE_VENUE v)
     {
      return (v == SEESARE_VENUE_LONDON || v == SEESARE_VENUE_FRANKFURT || v == SEESARE_VENUE_NEW_YORK);
     }
   static bool       IsSummer(const ENUM_SEESARE_VENUE v, const datetime utc)
     {
      if(v == SEESARE_VENUE_LONDON || v == SEESARE_VENUE_FRANKFURT)
         return EuSummer(utc);
      if(v == SEESARE_VENUE_NEW_YORK)
         return UsSummer(utc);
      return false;
     }
   static long       VenueOffset(const ENUM_SEESARE_VENUE v, const datetime utc)
     {
      return StdOffset(v) + (IsSummer(v, utc) ? SEESARE_HOUR_SEC : 0);
     }
   static datetime   UtcToVenue(const ENUM_SEESARE_VENUE v, const datetime utc)
     {
      return (datetime)((long)utc + VenueOffset(v, utc));
     }
   //--- venue wall time -> UTC; same answer as the IANA database with fold=0: the first instant of the
   //--- repeated autumn hour, and the standard-time reading inside the skipped spring hour
   static datetime   VenueToUtc(const ENUM_SEESARE_VENUE v, const datetime local)
     {
      long u_std = (long)local - StdOffset(v);
      if(!HasDst(v))
         return (datetime)u_std;
      long u_dst = u_std - SEESARE_HOUR_SEC;
      return (datetime)(IsSummer(v, (datetime)u_dst) ? u_dst : u_std);
     }
   static long       SchemeOffset(const ENUM_SEESARE_SERVER_SCHEME scheme, const datetime utc, const int fixed_minutes)
     {
      if(scheme == SEESARE_SERVER_GMT2_EU)
         return (EuSummer(utc) ? 3 : 2) * SEESARE_HOUR_SEC;
      if(scheme == SEESARE_SERVER_GMT2_US)
         return (UsSummer(utc) ? 3 : 2) * SEESARE_HOUR_SEC;
      if(scheme == SEESARE_SERVER_FIXED)
         return (long)fixed_minutes * 60;
      return 0;   // GMT0; MEASURED is resolved by CSeesareClock
     }
   //--- server time -> UTC for a declared scheme; in the repeated autumn hour the first pass is returned
   static datetime   SchemeServerToUtc(const ENUM_SEESARE_SERVER_SCHEME scheme, const datetime srv, const int fixed_minutes)
     {
      if(scheme == SEESARE_SERVER_GMT2_EU || scheme == SEESARE_SERVER_GMT2_US)
        {
         datetime u3 = (datetime)((long)srv - 3 * SEESARE_HOUR_SEC);
         if(SchemeOffset(scheme, u3, fixed_minutes) == 3 * SEESARE_HOUR_SEC)
            return u3;
         return (datetime)((long)srv - 2 * SEESARE_HOUR_SEC);
        }
      return (datetime)((long)srv - SchemeOffset(scheme, srv, fixed_minutes));
     }
   static string     IsoUtc(const datetime t)
     {
      MqlDateTime s;
      TimeToStruct(t, s);
      return StringFormat("%04d-%02d-%02dT%02d:%02d:%02dZ", s.year, s.mon, s.day, s.hour, s.min, s.sec);
     }
   //--- strict "YYYY-MM-DDTHH:MM:SSZ"; rejects impossible dates by a round trip
   static bool       IsoToTime(const string s, datetime &t)
     {
      t = 0;
      if(StringLen(s) != 20)
         return false;
      for(int i = 0; i < 20; i++)
        {
         ushort c = StringGetCharacter(s, i);
         if(i == 4 || i == 7)
           {
            if(c != '-')
               return false;
           }
         else if(i == 10)
           {
            if(c != 'T')
               return false;
           }
         else if(i == 13 || i == 16)
           {
            if(c != ':')
               return false;
           }
         else if(i == 19)
           {
            if(c != 'Z')
               return false;
           }
         else if(!CSeesareText::IsDigit(c))
            return false;
        }
      MqlDateTime d;
      ZeroMemory(d);
      d.year = (int)StringToInteger(StringSubstr(s, 0, 4));
      d.mon  = (int)StringToInteger(StringSubstr(s, 5, 2));
      d.day  = (int)StringToInteger(StringSubstr(s, 8, 2));
      d.hour = (int)StringToInteger(StringSubstr(s, 11, 2));
      d.min  = (int)StringToInteger(StringSubstr(s, 14, 2));
      d.sec  = (int)StringToInteger(StringSubstr(s, 17, 2));
      if(d.year < 1971 || d.mon < 1 || d.mon > 12 || d.day < 1 || d.day > 31 || d.hour > 23 || d.min > 59 || d.sec > 59)
         return false;
      datetime v = StructToTime(d);
      if(IsoUtc(v) != s)
         return false;
      t = v;
      return true;
     }
   //--- "HH:MM" -> minutes after midnight, -1 if malformed
   static int        ParseHHMM(const string s)
     {
      if(StringLen(s) != 5 || StringGetCharacter(s, 2) != ':')
         return -1;
      for(int i = 0; i < 5; i++)
         if(i != 2 && !CSeesareText::IsDigit(StringGetCharacter(s, i)))
            return -1;
      int h = (int)StringToInteger(StringSubstr(s, 0, 2));
      int m = (int)StringToInteger(StringSubstr(s, 3, 2));
      if(h > 23 || m > 59)
         return -1;
      return h * 60 + m;
     }
   static string     HHMM(const int minutes)
     {
      return StringFormat("%02d:%02d", minutes / 60, minutes % 60);
     }
   static string     OffsetText(const long sec)
     {
      long a = (sec < 0 ? -sec : sec);
      string sign = (sec < 0 ? "-" : "+");
      return sign + StringFormat("%d:%02d", (int)(a / 3600), (int)((a % 3600) / 60));
     }
   static string     VenueName(const ENUM_SEESARE_VENUE v)
     {
      if(v == SEESARE_VENUE_UTC)
         return "UTC";
      if(v == SEESARE_VENUE_LONDON)
         return "LONDON";
      if(v == SEESARE_VENUE_FRANKFURT)
         return "FRANKFURT";
      if(v == SEESARE_VENUE_NEW_YORK)
         return "NEW_YORK";
      if(v == SEESARE_VENUE_TOKYO)
         return "TOKYO";
      if(v == SEESARE_VENUE_SERVER)
         return "SERVER";
      return "?";
     }
   static string     SchemeName(const ENUM_SEESARE_SERVER_SCHEME s)
     {
      if(s == SEESARE_SERVER_GMT0)
         return "GMT0";
      if(s == SEESARE_SERVER_GMT2_EU)
         return "GMT2_EU";
      if(s == SEESARE_SERVER_GMT2_US)
         return "GMT2_US";
      if(s == SEESARE_SERVER_FIXED)
         return "FIXED";
      if(s == SEESARE_SERVER_MEASURED)
         return "MEASURED";
      return "?";
     }
  };

//+------------------------------------------------------------------+
//| Broker server clock: live offset check and conversions           |
//| Live: offset = round((TimeTradeServer - TimeGMT) / 15 min); both |
//| come from the VPS clock, so the VPS must be NTP-synced. The      |
//| declared scheme must equal the measured offset, else Healthy()   |
//| is false and the spread gate vetoes every entry.                 |
//| Tester: TimeGMT() equals server time there, so the offset cannot |
//| be measured; a declared scheme is required.                      |
//+------------------------------------------------------------------+
class CSeesareClock
  {
private:
   ENUM_SEESARE_SERVER_SCHEME m_scheme;
   int               m_fixed_min;
   int               m_recheck_sec;
   bool              m_tester;
   bool              m_ready;
   bool              m_healthy;
   string            m_error;
   long              m_measured;
   datetime          m_last_check;

public:
                     CSeesareClock(void);
   bool              Init(const ENUM_SEESARE_SERVER_SCHEME scheme, const int fixed_minutes = 0, const int recheck_sec = 300);
   bool              Check(void);
   void              Tick(void);
   bool              Healthy(void) const { return (m_ready && m_healthy); }
   string            LastError(void) const { return m_error; }
   bool              IsTester(void) const { return m_tester; }
   ENUM_SEESARE_SERVER_SCHEME Scheme(void) const { return m_scheme; }
   long              MeasuredOffset(void) const { return m_measured; }
   long              ServerOffsetAt(const datetime utc) const;
   datetime          UtcToServer(const datetime utc) const;
   datetime          ServerToUtc(const datetime srv) const;
   datetime          UtcNow(void) const;
   datetime          ServerNow(void) const;
   datetime          VenueTime(const ENUM_SEESARE_VENUE v, const datetime utc) const;
  };

CSeesareClock::CSeesareClock(void)
  {
   m_scheme      = SEESARE_SERVER_GMT0;
   m_fixed_min   = 0;
   m_recheck_sec = 300;
   m_tester      = false;
   m_ready       = false;
   m_healthy     = false;
   m_error       = "clock not initialised";
   m_measured    = 0;
   m_last_check  = 0;
  }

//--- validates the configuration (false = unusable); Healthy() then says whether time can be trusted now
bool CSeesareClock::Init(const ENUM_SEESARE_SERVER_SCHEME scheme, const int fixed_minutes, const int recheck_sec)
  {
   m_scheme      = scheme;
   m_fixed_min   = fixed_minutes;
   m_recheck_sec = (recheck_sec < 60 ? 60 : recheck_sec);
   m_tester      = (MQLInfoInteger(MQL_TESTER) != 0 || MQLInfoInteger(MQL_OPTIMIZATION) != 0);
   m_ready       = false;
   m_healthy     = false;
   m_measured    = 0;
   m_last_check  = 0;
   if(fixed_minutes < -12 * 60 || fixed_minutes > 14 * 60)
     {
      m_error = "fixed offset out of range (-12:00 to +14:00)";
      return false;
     }
   if(m_tester && scheme == SEESARE_SERVER_MEASURED)
     {
      m_error = "the Strategy Tester cannot measure the server offset (TimeGMT() equals server time there): declare the scheme";
      return false;
     }
   m_ready = true;
   Check();
   return true;
  }

bool CSeesareClock::Check(void)
  {
   m_healthy = false;
   if(!m_ready)
      return false;
   if(m_tester)
     {
      m_last_check = TimeCurrent();
      m_healthy = true;
      m_error = "";
      return true;
     }
   datetime gmt = TimeGMT();
   m_last_check = gmt;
   if(TerminalInfoInteger(TERMINAL_CONNECTED) == 0)
     {
      m_error = "terminal not connected to the trade server";
      return false;
     }
   long raw = (long)TimeTradeServer() - (long)gmt;
   long q = (long)MathRound((double)raw / 900.0) * 900;
   if(MathAbs((double)(raw - q)) > 120.0)
     {
      m_error = "server minus GMT is " + IntegerToString(raw) + " s, not a whole quarter hour: check the VPS clock (NTP)";
      return false;
     }
   m_measured = q;
   if(q < -12 * SEESARE_HOUR_SEC || q > 14 * SEESARE_HOUR_SEC)
     {
      m_error = "measured server offset out of range: " + CSeesareDst::OffsetText(q);
      return false;
     }
   if(m_scheme != SEESARE_SERVER_MEASURED)
     {
      long expected = CSeesareDst::SchemeOffset(m_scheme, gmt, m_fixed_min);
      if(q != expected)
        {
         m_error = "server offset measured " + CSeesareDst::OffsetText(q) + " but scheme " + CSeesareDst::SchemeName(m_scheme) +
                   " expects " + CSeesareDst::OffsetText(expected) + " at " + CSeesareDst::IsoUtc(gmt);
         return false;
        }
     }
   m_error = "";
   m_healthy = true;
   return true;
  }

//--- call from OnTimer: re-checks every recheck_sec, every 10 s while unhealthy
void CSeesareClock::Tick(void)
  {
   if(!m_ready)
      return;
   datetime now = (m_tester ? TimeCurrent() : TimeGMT());
   long every = (m_healthy ? m_recheck_sec : 10);
   if(m_last_check == 0 || (long)now - (long)m_last_check >= every || (long)now < (long)m_last_check)
      Check();
  }

long CSeesareClock::ServerOffsetAt(const datetime utc) const
  {
   if(m_scheme == SEESARE_SERVER_MEASURED)
      return m_measured;
   return CSeesareDst::SchemeOffset(m_scheme, utc, m_fixed_min);
  }

datetime CSeesareClock::UtcToServer(const datetime utc) const
  {
   return (datetime)((long)utc + ServerOffsetAt(utc));
  }

datetime CSeesareClock::ServerToUtc(const datetime srv) const
  {
   if(m_scheme == SEESARE_SERVER_MEASURED)
      return (datetime)((long)srv - m_measured);
   return CSeesareDst::SchemeServerToUtc(m_scheme, srv, m_fixed_min);
  }

datetime CSeesareClock::UtcNow(void) const
  {
   if(m_tester)
      return ServerToUtc(TimeCurrent());
   return TimeGMT();
  }

datetime CSeesareClock::ServerNow(void) const
  {
   if(m_tester)
      return TimeCurrent();
   return TimeTradeServer();
  }

datetime CSeesareClock::VenueTime(const ENUM_SEESARE_VENUE v, const datetime utc) const
  {
   if(v == SEESARE_VENUE_SERVER)
      return UtcToServer(utc);
   return CSeesareDst::UtcToVenue(v, utc);
  }

//+------------------------------------------------------------------+
//| Timing matrix: flow windows in venue wall time -> UTC instances  |
//+------------------------------------------------------------------+
struct SSeesareWindow
  {
   string             id;
   ENUM_SEESARE_VENUE venue;
   int                start_min;    // minutes after local midnight
   int                end_min;      // end <= start means the next local day
   int                day_mask;     // on the local date of the start
  };

struct SSeesareUtcWindow
  {
   string             id;
   int                index;        // position in the matrix
   datetime           start_utc;
   datetime           end_utc;      // exclusive
   datetime           local_date;   // venue-local midnight of this instance (wall time held as datetime)
  };

void SeesareCopyUtcWindow(const SSeesareUtcWindow &src, SSeesareUtcWindow &dst)
  {
   dst.id         = src.id;
   dst.index      = src.index;
   dst.start_utc  = src.start_utc;
   dst.end_utc    = src.end_utc;
   dst.local_date = src.local_date;
  }

class CSeesareTimingMatrix
  {
private:
   SSeesareWindow    m_w[];
   string            m_error;

public:
                     CSeesareTimingMatrix(void) { m_error = ""; }
   void              Clear(void) { ArrayResize(m_w, 0); }
   int               Count(void) const { return ArraySize(m_w); }
   string            LastError(void) const { return m_error; }
   bool              Add(const string id, const ENUM_SEESARE_VENUE venue, const string start_hhmm, const string end_hhmm, const int day_mask);
   int               Find(const string id) const;
   string            Id(const int idx) const;
   bool              ResolveLocalDate(const int idx, const datetime local_date, SSeesareUtcWindow &out) const;
   bool              ActiveAt(const int idx, const datetime utc, SSeesareUtcWindow &out) const;
   bool              NextAt(const int idx, const datetime utc, SSeesareUtcWindow &out) const;
   int               OnUtcDate(const datetime utc_any, SSeesareUtcWindow &out[]) const;
   void              LoadDefaults(void);
  };

bool CSeesareTimingMatrix::Add(const string id, const ENUM_SEESARE_VENUE venue, const string start_hhmm, const string end_hhmm, const int day_mask)
  {
   int a = CSeesareDst::ParseHHMM(start_hhmm);
   int b = CSeesareDst::ParseHHMM(end_hhmm);
   if(!CSeesareText::IsToken(id, 32) || Find(id) >= 0)
     {
      m_error = "window id must be a unique token of 1-32 characters: " + id;
      return false;
     }
   if(venue < SEESARE_VENUE_UTC || venue > SEESARE_VENUE_TOKYO)
     {
      m_error = "window " + id + ": venue must be UTC, LONDON, FRANKFURT, NEW_YORK or TOKYO";
      return false;
     }
   if(a < 0 || b < 0 || a == b)
     {
      m_error = "window " + id + ": start and end must be HH:MM and differ";
      return false;
     }
   if(day_mask < 1 || day_mask > 127)
     {
      m_error = "window " + id + ": day mask must be 1-127";
      return false;
     }
   int n = ArraySize(m_w);
   ArrayResize(m_w, n + 1, 16);
   m_w[n].id        = id;
   m_w[n].venue     = venue;
   m_w[n].start_min = a;
   m_w[n].end_min   = b;
   m_w[n].day_mask  = day_mask;
   return true;
  }

int CSeesareTimingMatrix::Find(const string id) const
  {
   for(int i = 0; i < ArraySize(m_w); i++)
      if(m_w[i].id == id)
         return i;
   return -1;
  }

string CSeesareTimingMatrix::Id(const int idx) const
  {
   if(idx < 0 || idx >= ArraySize(m_w))
      return "";
   return m_w[idx].id;
  }

//--- the instance that starts on venue-local date local_date (false if the day mask closes it)
bool CSeesareTimingMatrix::ResolveLocalDate(const int idx, const datetime local_date, SSeesareUtcWindow &out) const
  {
   if(idx < 0 || idx >= ArraySize(m_w))
      return false;
   datetime d = CSeesareDst::Midnight(local_date);
   if(((m_w[idx].day_mask >> CSeesareDst::DayOfWeek(d)) & 1) == 0)
      return false;
   long ls = (long)d + (long)m_w[idx].start_min * 60;
   long le = (long)d + (long)m_w[idx].end_min * 60;
   if(m_w[idx].end_min <= m_w[idx].start_min)
      le += SEESARE_DAY_SEC;
   out.id         = m_w[idx].id;
   out.index      = idx;
   out.local_date = d;
   out.start_utc  = CSeesareDst::VenueToUtc(m_w[idx].venue, (datetime)ls);
   out.end_utc    = CSeesareDst::VenueToUtc(m_w[idx].venue, (datetime)le);
   return true;
  }

//--- the instance open at utc (start <= utc < end)
bool CSeesareTimingMatrix::ActiveAt(const int idx, const datetime utc, SSeesareUtcWindow &out) const
  {
   if(idx < 0 || idx >= ArraySize(m_w))
      return false;
   datetime d = CSeesareDst::Midnight(CSeesareDst::UtcToVenue(m_w[idx].venue, utc));
   for(int back = 1; back >= 0; back--)
     {
      SSeesareUtcWindow w;
      if(ResolveLocalDate(idx, (datetime)((long)d - (long)back * SEESARE_DAY_SEC), w) && utc >= w.start_utc && utc < w.end_utc)
        {
         SeesareCopyUtcWindow(w, out);
         return true;
        }
     }
   return false;
  }

//--- the open instance, or else the next one (searches nine local days)
bool CSeesareTimingMatrix::NextAt(const int idx, const datetime utc, SSeesareUtcWindow &out) const
  {
   if(idx < 0 || idx >= ArraySize(m_w))
      return false;
   datetime d = CSeesareDst::Midnight(CSeesareDst::UtcToVenue(m_w[idx].venue, utc));
   for(int i = -1; i <= 8; i++)
     {
      SSeesareUtcWindow w;
      if(ResolveLocalDate(idx, (datetime)((long)d + (long)i * SEESARE_DAY_SEC), w) && w.end_utc > utc)
        {
         SeesareCopyUtcWindow(w, out);
         return true;
        }
     }
   return false;
  }

//--- every instance whose start falls on the UTC date of utc_any, sorted by start then matrix order
int CSeesareTimingMatrix::OnUtcDate(const datetime utc_any, SSeesareUtcWindow &out[]) const
  {
   ArrayResize(out, 0);
   long day0 = (long)CSeesareDst::Midnight(utc_any);
   int n = 0;
   for(int idx = 0; idx < ArraySize(m_w); idx++)
     {
      for(int i = -1; i <= 1; i++)
        {
         SSeesareUtcWindow w;
         if(!ResolveLocalDate(idx, (datetime)(day0 + (long)i * SEESARE_DAY_SEC), w))
            continue;
         if((long)w.start_utc < day0 || (long)w.start_utc >= day0 + SEESARE_DAY_SEC)
            continue;
         ArrayResize(out, n + 1, 16);
         SeesareCopyUtcWindow(w, out[n]);
         n++;
        }
     }
   for(int a = 1; a < n; a++)
     {
      SSeesareUtcWindow key;
      SeesareCopyUtcWindow(out[a], key);
      int b = a - 1;
      while(b >= 0 && (out[b].start_utc > key.start_utc || (out[b].start_utc == key.start_utc && out[b].index > key.index)))
        {
         SeesareCopyUtcWindow(out[b], out[b + 1]);
         b--;
        }
      SeesareCopyUtcWindow(key, out[b + 1]);
     }
   return n;
  }

//--- blueprint section 4. Modules narrow these with their own calendars (gotobi days, FOMC and NFP dates).
void CSeesareTimingMatrix::LoadDefaults(void)
  {
   Clear();
   Add("WMR_FIX",     SEESARE_VENUE_LONDON,    "15:30", "16:10", SEESARE_MASK_MON_FRI);
   Add("NY_MOC",      SEESARE_VENUE_NEW_YORK,  "15:50", "16:05", SEESARE_MASK_MON_FRI);
   Add("ECB_FIX",     SEESARE_VENUE_FRANKFURT, "14:05", "14:20", SEESARE_MASK_MON_FRI);
   Add("NY_MOO",      SEESARE_VENUE_NEW_YORK,  "09:15", "09:40", SEESARE_MASK_MON_FRI);
   Add("US_NFP",      SEESARE_VENUE_NEW_YORK,  "08:30", "10:00", SEESARE_MASK_FRI);
   Add("FOMC",        SEESARE_VENUE_NEW_YORK,  "14:00", "14:30", SEESARE_MASK_MON_FRI);
   Add("TOKYO_FIX",   SEESARE_VENUE_TOKYO,     "08:00", "09:55", SEESARE_MASK_MON_FRI);
   Add("TOCOM_CLOSE", SEESARE_VENUE_TOKYO,     "15:15", "15:45", SEESARE_MASK_MON_FRI);
   Add("FUNDING_00",  SEESARE_VENUE_UTC,       "23:50", "00:10", SEESARE_MASK_ALL);
   Add("FUNDING_08",  SEESARE_VENUE_UTC,       "07:50", "08:10", SEESARE_MASK_ALL);
   Add("FUNDING_16",  SEESARE_VENUE_UTC,       "15:50", "16:10", SEESARE_MASK_ALL);
  }

#endif

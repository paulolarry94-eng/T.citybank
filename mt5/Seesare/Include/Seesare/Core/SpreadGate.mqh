//+------------------------------------------------------------------+
//|                                     Seesare/Core/SpreadGate.mqh  |
//| SEESARE P26 router, Phase 1: strict spread-aware entry filter.   |
//| UNCOMPILED SOURCE.                                               |
//|                                                                  |
//| Check() answers one question just before an entry: may this      |
//| symbol be entered now, inside this window? Order of the checks:  |
//|   clock healthy -> inside the window -> symbol tradable in this  |
//|   direction -> a quote exists -> the quote is fresh -> not in a  |
//|   blackout (rollover) -> spread <= cap.                          |
//| cap = min(max_points, max_frac x boundary distance / point).     |
//| A wide spread inside the first `patience` seconds of the window  |
//| returns WAIT (ask again); after that it is a VETO.               |
//| A drifting VPS clock shows up as stale quotes or a clock veto,   |
//| never as a trade.                                                |
//+------------------------------------------------------------------+
#ifndef SEESARE_CORE_SPREADGATE_MQH
#define SEESARE_CORE_SPREADGATE_MQH

#include <Seesare\Core\Clock.mqh>

enum ENUM_SEESARE_GATE
  {
   SEESARE_GATE_PASS          = 0,   // enter now
   SEESARE_GATE_WAIT          = 1,   // spread too wide, still within patience: ask again
   SEESARE_GATE_VETO_CLOCK    = 2,   // clock unhealthy or quotes ahead of the server clock
   SEESARE_GATE_VETO_WINDOW   = 3,   // outside the window
   SEESARE_GATE_VETO_SYMBOL   = 4,   // symbol missing, not in Market Watch, or not tradable this way
   SEESARE_GATE_VETO_NO_QUOTE = 5,   // no valid bid/ask
   SEESARE_GATE_VETO_STALE    = 6,   // last quote older than max_quote_age
   SEESARE_GATE_VETO_BLACKOUT = 7,   // inside a blackout (daily rollover)
   SEESARE_GATE_VETO_SPREAD   = 8    // spread above the cap after the patience ran out
  };

struct SSeesareGateResult
  {
   ENUM_SEESARE_GATE verdict;
   double            spread_points;
   double            cap_points;
   long              quote_age_sec;
   string            reason;
  };

class CSeesareSpreadGate
  {
private:
   double            m_max_points;
   double            m_max_frac;
   int               m_patience_sec;
   int               m_max_age_sec;
   int               m_bo_venue[];
   int               m_bo_from[];
   int               m_bo_to[];
   string            m_error;
   ENUM_SEESARE_GATE Done(SSeesareGateResult &r, const ENUM_SEESARE_GATE v, const string reason) const;

public:
                     CSeesareSpreadGate(void);
   bool              Configure(const double max_points, const double max_frac_of_boundary, const int patience_sec, const int max_quote_age_sec);
   bool              AddBlackout(const ENUM_SEESARE_VENUE venue, const string from_hhmm, const string to_hhmm);
   void              ClearBlackouts(void);
   void              LoadDefaultBlackouts(void);
   bool              InBlackout(CSeesareClock &clock, const datetime utc, string &which) const;
   ENUM_SEESARE_GATE Check(const string symbol, const int side, const double boundary_distance, const SSeesareUtcWindow &win,
                           CSeesareClock &clock, SSeesareGateResult &res) const;
   string            LastError(void) const { return m_error; }
   //--- minute in [from, to); from > to wraps past midnight; from == to is never
   static bool       InMinuteRange(const int minute, const int from, const int to)
     {
      if(from == to)
         return false;
      if(from < to)
         return (minute >= from && minute < to);
      return (minute >= from || minute < to);
     }
   static string     VerdictName(const ENUM_SEESARE_GATE g)
     {
      if(g == SEESARE_GATE_PASS)
         return "PASS";
      if(g == SEESARE_GATE_WAIT)
         return "WAIT";
      if(g == SEESARE_GATE_VETO_CLOCK)
         return "VETO_CLOCK";
      if(g == SEESARE_GATE_VETO_WINDOW)
         return "VETO_WINDOW";
      if(g == SEESARE_GATE_VETO_SYMBOL)
         return "VETO_SYMBOL";
      if(g == SEESARE_GATE_VETO_NO_QUOTE)
         return "VETO_NO_QUOTE";
      if(g == SEESARE_GATE_VETO_STALE)
         return "VETO_STALE";
      if(g == SEESARE_GATE_VETO_BLACKOUT)
         return "VETO_BLACKOUT";
      if(g == SEESARE_GATE_VETO_SPREAD)
         return "VETO_SPREAD";
      return "?";
     }
  };

CSeesareSpreadGate::CSeesareSpreadGate(void)
  {
   m_max_points   = 0.0;
   m_max_frac     = 0.15;
   m_patience_sec = 900;
   m_max_age_sec  = 15;
   m_error        = "";
   LoadDefaultBlackouts();
  }

//--- max_points: absolute cap in points (0 = none); max_frac_of_boundary: spread <= this share of the stop distance
//--- (0 = none); at least one cap is required. patience: seconds after the window opens during which a wide spread
//--- means WAIT. max_quote_age: seconds.
bool CSeesareSpreadGate::Configure(const double max_points, const double max_frac_of_boundary, const int patience_sec, const int max_quote_age_sec)
  {
   if(max_points < 0.0 || max_frac_of_boundary < 0.0 || max_frac_of_boundary > 1.0 || (max_points == 0.0 && max_frac_of_boundary == 0.0))
     {
      m_error = "give a point cap, a boundary fraction in (0, 1], or both";
      return false;
     }
   if(patience_sec < 0 || patience_sec > 3600 || max_quote_age_sec < 1 || max_quote_age_sec > 300)
     {
      m_error = "patience must be 0-3600 s and the quote age 1-300 s";
      return false;
     }
   m_max_points   = max_points;
   m_max_frac     = max_frac_of_boundary;
   m_patience_sec = patience_sec;
   m_max_age_sec  = max_quote_age_sec;
   m_error        = "";
   return true;
  }

bool CSeesareSpreadGate::AddBlackout(const ENUM_SEESARE_VENUE venue, const string from_hhmm, const string to_hhmm)
  {
   int a = CSeesareDst::ParseHHMM(from_hhmm);
   int b = CSeesareDst::ParseHHMM(to_hhmm);
   if(a < 0 || b < 0 || a == b || venue < SEESARE_VENUE_UTC || venue > SEESARE_VENUE_SERVER)
     {
      m_error = "blackout needs a venue and two different HH:MM times";
      return false;
     }
   int n = ArraySize(m_bo_from);
   ArrayResize(m_bo_venue, n + 1);
   ArrayResize(m_bo_from, n + 1);
   ArrayResize(m_bo_to, n + 1);
   m_bo_venue[n] = (int)venue;
   m_bo_from[n]  = a;
   m_bo_to[n]    = b;
   return true;
  }

void CSeesareSpreadGate::ClearBlackouts(void)
  {
   ArrayResize(m_bo_venue, 0);
   ArrayResize(m_bo_from, 0);
   ArrayResize(m_bo_to, 0);
  }

//--- the daily rollover: liquidity providers roll at 17:00 New York; the broker books swaps at its server midnight
void CSeesareSpreadGate::LoadDefaultBlackouts(void)
  {
   ClearBlackouts();
   AddBlackout(SEESARE_VENUE_NEW_YORK, "16:55", "17:10");
   AddBlackout(SEESARE_VENUE_SERVER,   "23:55", "00:10");
  }

bool CSeesareSpreadGate::InBlackout(CSeesareClock &clock, const datetime utc, string &which) const
  {
   which = "";
   for(int i = 0; i < ArraySize(m_bo_from); i++)
     {
      ENUM_SEESARE_VENUE v = (ENUM_SEESARE_VENUE)m_bo_venue[i];
      int minute = CSeesareDst::MinuteOfDay(clock.VenueTime(v, utc));
      if(InMinuteRange(minute, m_bo_from[i], m_bo_to[i]))
        {
         which = CSeesareDst::VenueName(v) + " " + CSeesareDst::HHMM(m_bo_from[i]) + "-" + CSeesareDst::HHMM(m_bo_to[i]);
         return true;
        }
     }
   return false;
  }

ENUM_SEESARE_GATE CSeesareSpreadGate::Done(SSeesareGateResult &r, const ENUM_SEESARE_GATE v, const string reason) const
  {
   r.verdict = v;
   r.reason  = reason;
   return v;
  }

//--- side: +1 buy, -1 sell. boundary_distance: |entry - lower boundary| in price units (0 = use the point cap only).
ENUM_SEESARE_GATE CSeesareSpreadGate::Check(const string symbol, const int side, const double boundary_distance,
                                            const SSeesareUtcWindow &win, CSeesareClock &clock, SSeesareGateResult &res) const
  {
   res.verdict       = SEESARE_GATE_VETO_CLOCK;
   res.spread_points = 0.0;
   res.cap_points    = 0.0;
   res.quote_age_sec = 0;
   res.reason        = "";
   if(!clock.Healthy())
      return Done(res, SEESARE_GATE_VETO_CLOCK, "clock: " + clock.LastError());
   datetime now = clock.UtcNow();
   if(now < win.start_utc || now >= win.end_utc)
      return Done(res, SEESARE_GATE_VETO_WINDOW, CSeesareDst::IsoUtc(now) + " is outside " + win.id + " " +
                  CSeesareDst::IsoUtc(win.start_utc) + " - " + CSeesareDst::IsoUtc(win.end_utc));
   if(SymbolInfoInteger(symbol, SYMBOL_EXIST) == 0 || SymbolInfoInteger(symbol, SYMBOL_SELECT) == 0)
      return Done(res, SEESARE_GATE_VETO_SYMBOL, symbol + ": unknown or not in Market Watch");
   long trade_mode = SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE);
   if(trade_mode == SYMBOL_TRADE_MODE_DISABLED || trade_mode == SYMBOL_TRADE_MODE_CLOSEONLY ||
      (side > 0 && trade_mode == SYMBOL_TRADE_MODE_SHORTONLY) || (side < 0 && trade_mode == SYMBOL_TRADE_MODE_LONGONLY))
      return Done(res, SEESARE_GATE_VETO_SYMBOL, symbol + ": the broker does not allow this entry now");
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   if(point <= 0.0)
      return Done(res, SEESARE_GATE_VETO_SYMBOL, symbol + ": no point size");
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick) || tick.bid <= 0.0 || tick.ask <= 0.0 || tick.ask < tick.bid)
      return Done(res, SEESARE_GATE_VETO_NO_QUOTE, symbol + ": no valid quote");
   long age = (long)clock.ServerNow() - (long)tick.time;
   res.quote_age_sec = age;
   if(age < -(long)m_max_age_sec)
      return Done(res, SEESARE_GATE_VETO_CLOCK, symbol + ": quote time is " + IntegerToString(-age) +
                  " s ahead of the server clock: check the VPS clock");
   if(age > (long)m_max_age_sec)
      return Done(res, SEESARE_GATE_VETO_STALE, symbol + ": last quote is " + IntegerToString(age) + " s old");
   string which = "";
   if(InBlackout(clock, now, which))
      return Done(res, SEESARE_GATE_VETO_BLACKOUT, "blackout " + which);
   double spread = (tick.ask - tick.bid) / point;
   double cap = (m_max_points > 0.0 ? m_max_points : DBL_MAX);
   if(m_max_frac > 0.0 && boundary_distance > 0.0)
      cap = MathMin(cap, m_max_frac * boundary_distance / point);
   res.spread_points = spread;
   res.cap_points    = cap;
   if(cap == DBL_MAX)
      return Done(res, SEESARE_GATE_VETO_SPREAD, "no spread cap applies: give a boundary distance or a point cap");
   string text = "spread " + DoubleToString(spread, 1) + " vs cap " + DoubleToString(cap, 1) + " points";
   if(spread <= cap + 1e-9)
      return Done(res, SEESARE_GATE_PASS, text);
   if((long)now < (long)win.start_utc + m_patience_sec)
      return Done(res, SEESARE_GATE_WAIT, text + ": waiting");
   return Done(res, SEESARE_GATE_VETO_SPREAD, text + ": patience used up");
  }

#endif

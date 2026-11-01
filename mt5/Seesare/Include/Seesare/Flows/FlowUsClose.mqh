//+------------------------------------------------------------------+
//|                                    Seesare/Flows/FlowUsClose.mqh |
//| Module 2: US closing-auction imbalance, US500 / NAS100.          |
//| UNCOMPILED SOURCE.                                               |
//|                                                                  |
//| Owner's spec: at 15:50 New York read the published NYSE/Nasdaq   |
//| closing imbalance; trade only if |net imbalance| >= a dollar     |
//| threshold, in its direction; target 4 x the stop; leave at 16:00 |
//| New York (DST from America/New_York).                            |
//| Data: MT5 has no imbalance data and research/data has none, so   |
//| the module reads it from a file that an outside feed writes into |
//| the terminals' Common\Files folder, one line per day:            |
//|   YYYY-MM-DD,HH:MM,net_usd   (New York date and publication time;|
//|                               net > 0 = buy imbalance)           |
//|   lines starting with # are comments.                            |
//| The figure must be published at or before the entry instant and |
//| at most 5 minutes old. Stop: 0.3% of price (catastrophe, like    |
//| the Tokyo module; the spec names no stop).                       |
//| Evidence: UNTESTED (no data). Status: PAPER at most. The closest |
//| testable version, momentum into the last half hour, is queued    |
//| (OPEN_QUESTIONS Q19).                                            |
//+------------------------------------------------------------------+
#ifndef SEESARE_FLOWS_USCLOSE_MQH
#define SEESARE_FLOWS_USCLOSE_MQH

#include <Seesare\Flows\FlowModule.mqh>
#include <Seesare\Ledger\StateStore.mqh>

#define SEESARE_USC_ENTRY_MIN     (15 * 60 + 50)
#define SEESARE_USC_EXIT_MIN      (16 * 60)
#define SEESARE_USC_RATIO         4.0
#define SEESARE_USC_STOP_PCT      0.003
#define SEESARE_USC_MAX_AGE_SEC   300

class CSeesareFlowUsClose : public CSeesareFlowModule
  {
private:
   string            m_feed;
   double            m_threshold;
   double            m_max_spread_points;

public:
                     CSeesareFlowUsClose(const string symbol, const string feed_path, const double threshold_usd,
                                         const double max_spread_points);
   virtual bool      SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot);
   virtual bool      Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan);
   virtual double    DeclaredRatio(void) const { return SEESARE_USC_RATIO; }
   //--- "YYYY-MM-DD,HH:MM,net_usd" -> New York date (midnight), minute of day, net USD; false if malformed
   static bool       ParseFeedLine(const string line, datetime &ny_date, int &minute, double &net_usd);
   //--- the last line for this New York date; false if none
   bool              ReadImbalance(const datetime ny_date, int &minute, double &net_usd) const;
  };

CSeesareFlowUsClose::CSeesareFlowUsClose(const string symbol, const string feed_path, const double threshold_usd,
                                         const double max_spread_points)
  {
   m_id                = "US_CLOSE_" + symbol;
   m_symbol            = symbol;
   m_domain            = "indices";
   m_evidence          = SEESARE_EVIDENCE_UNTESTED;
   m_evidence_ref      = "no NYSE/Nasdaq closing-imbalance data in MT5 or in research/data";
   m_feed              = feed_path;
   m_threshold         = threshold_usd;
   m_max_spread_points = max_spread_points;
  }

bool CSeesareFlowUsClose::ParseFeedLine(const string line, datetime &ny_date, int &minute, double &net_usd)
  {
   ny_date = 0;
   minute = -1;
   net_usd = 0.0;
   string parts[];
   if(StringSplit(line, ',', parts) != 3)
      return false;
   datetime t = 0;
   if(!CSeesareDst::IsoToTime(parts[0] + "T00:00:00Z", t))
      return false;
   int m = CSeesareDst::ParseHHMM(parts[1]);
   if(m < 0)
      return false;
   string v = parts[2];
   int n = StringLen(v);
   if(n < 1 || n > 24)
      return false;
   bool digit = false;
   int dots = 0;
   for(int i = 0; i < n; i++)
     {
      ushort c = StringGetCharacter(v, i);
      if(CSeesareText::IsDigit(c))
        {
         digit = true;
         continue;
        }
      if(c == '.')
        {
         dots++;
         continue;
        }
      if(!((c == '-' || c == '+') && i == 0))
         return false;
     }
   if(!digit || dots > 1)
      return false;
   ny_date = t;
   minute = m;
   net_usd = StringToDouble(v);
   return true;
  }

bool CSeesareFlowUsClose::ReadImbalance(const datetime ny_date, int &minute, double &net_usd) const
  {
   minute = -1;
   net_usd = 0.0;
   string lines[];
   int n = CSeesareFiles::ReadLines(m_feed, lines);
   bool found = false;
   for(int i = 0; i < n; i++)
     {
      if(StringGetCharacter(lines[i], 0) == '#')
         continue;
      datetime d = 0;
      int m = -1;
      double v = 0.0;
      if(ParseFeedLine(lines[i], d, m, v) && d == ny_date)
        {
         minute = m;
         net_usd = v;
         found = true;
        }
     }
   return found;
  }

bool CSeesareFlowUsClose::SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot)
  {
   m_error = "";
   datetime d0 = CSeesareDst::Midnight(utc_day);
   int dow = CSeesareDst::DayOfWeek(d0);
   if(dow == 0 || dow == 6)
      return false;
   slot.module_id = m_id;
   slot.day_utc   = d0;
   slot.entry_utc = CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, (datetime)((long)d0 + SEESARE_USC_ENTRY_MIN * 60));
   slot.exit_utc  = CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, (datetime)((long)d0 + SEESARE_USC_EXIT_MIN * 60));
   return true;
  }

bool CSeesareFlowUsClose::Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan)
  {
   SeesareClearPlan(plan);
   int minute = -1;
   double net = 0.0;
   if(!ReadImbalance(slot.day_utc, minute, net))
     {
      plan.note = "no imbalance figure for today in " + m_feed;
      return false;                                                  // the feed may still be writing it: ask again
     }
   datetime published = CSeesareDst::VenueToUtc(SEESARE_VENUE_NEW_YORK, (datetime)((long)slot.day_utc + (long)minute * 60));
   datetime now = clock.UtcNow();
   if(published > now)
     {
      plan.note = "imbalance figure is time-stamped in the future";
      return true;
     }
   if((long)now - (long)published > SEESARE_USC_MAX_AGE_SEC)
     {
      plan.note = "imbalance figure is older than 5 minutes";
      return true;
     }
   if(MathAbs(net) < m_threshold)
     {
      plan.note = "imbalance " + DoubleToString(net / 1e6, 0) + "M USD is below the threshold";
      return true;
     }
   MqlTick tick;
   if(!SymbolInfoTick(m_symbol, tick) || tick.bid <= 0.0 || tick.ask <= 0.0)
     {
      plan.note = "no quote yet";
      return false;
     }
   plan.side              = (net > 0.0 ? 1 : -1);
   plan.stop_distance     = (plan.side > 0 ? tick.ask : tick.bid) * SEESARE_USC_STOP_PCT;
   plan.ratio             = SEESARE_USC_RATIO;
   plan.place_target      = true;
   plan.max_spread_points = m_max_spread_points;
   plan.note              = "imbalance " + DoubleToString(net / 1e6, 0) + "M USD";
   return true;
  }

#endif

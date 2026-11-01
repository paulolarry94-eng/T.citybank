//+------------------------------------------------------------------+
//|                                  Seesare/Flows/FlowLondonFix.mqh |
//| Module 3: London 4 pm WM/R fix reversion, EURUSD / GBPUSD.       |
//| UNCOMPILED SOURCE.                                               |
//|                                                                  |
//| Owner's spec, coded exactly as tested in the Truth Lab           |
//| (research/truth/strategies/wmr_fix_reversion_v1.py, structure    |
//| stop, all weekdays):                                             |
//|   drift = close of the 15:50-15:55 London M5 bar minus the open  |
//|   of the 15:30 bar; at 15:55 London enter against the drift;     |
//|   stop 1 pip beyond the 15:30-15:55 extreme; target 5 x the stop |
//|   distance; time exit 16:05 London (DST from Europe/London).    |
//| Evidence: REJECTED. 0 of 4 configurations passed; development   |
//|   2011-19 -0.10R per trade (t -5.2) with this stop and target,  |
//|   -0.017R (t -4.7) with a wide stop; month-ends -0.03 to -0.12R; |
//|   2020-22 negative too. The documented timing (fade after the    |
//|   fix, 16:00-17:00) was also rejected (wmr_fix_postfade_v1:      |
//|   month-ends +0.046R in 2011-19, +0.018R t 0.5 in 2023-25).      |
//| Status: PAPER at most (the router refuses LIVE).                 |
//+------------------------------------------------------------------+
#ifndef SEESARE_FLOWS_LONDONFIX_MQH
#define SEESARE_FLOWS_LONDONFIX_MQH

#include <Seesare\Flows\FlowModule.mqh>

#define SEESARE_LDN_DRIFT_FROM_MIN    (15 * 60 + 30)
#define SEESARE_LDN_ENTRY_MIN         (15 * 60 + 55)
#define SEESARE_LDN_EXIT_MIN          (16 * 60 + 5)
#define SEESARE_LDN_RATIO             5.0
#define SEESARE_LDN_BUFFER_PIPS       1.0
#define SEESARE_LDN_MAX_SPREAD_PIPS   1.5

class CSeesareFlowLondonFix : public CSeesareFlowModule
  {
public:
                     CSeesareFlowLondonFix(const string symbol);
   virtual bool      SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot);
   virtual bool      Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan);
   virtual double    DeclaredRatio(void) const { return SEESARE_LDN_RATIO; }
  };

CSeesareFlowLondonFix::CSeesareFlowLondonFix(const string symbol)
  {
   m_id           = "LDN_FIX_" + symbol;
   m_symbol       = symbol;
   m_domain       = "forex";
   m_evidence     = SEESARE_EVIDENCE_REJECTED;
   m_evidence_ref = "research/results/truth/wmr_fix_reversion_v1, 0 of 4 configurations, -0.017 to -0.12R";
  }

bool CSeesareFlowLondonFix::SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot)
  {
   m_error = "";
   datetime d0 = CSeesareDst::Midnight(utc_day);
   int dow = CSeesareDst::DayOfWeek(d0);
   if(dow == 0 || dow == 6)
      return false;
   slot.module_id = m_id;
   slot.day_utc   = d0;
   slot.entry_utc = CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, (datetime)((long)d0 + SEESARE_LDN_ENTRY_MIN * 60));
   slot.exit_utc  = CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, (datetime)((long)d0 + SEESARE_LDN_EXIT_MIN * 60));
   return true;
  }

bool CSeesareFlowLondonFix::Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan)
  {
   SeesareClearPlan(plan);
   datetime from_utc = CSeesareDst::VenueToUtc(SEESARE_VENUE_LONDON, (datetime)((long)slot.day_utc + SEESARE_LDN_DRIFT_FROM_MIN * 60));
   datetime last_utc = (datetime)((long)slot.entry_utc - 300);   // the M5 bar that closes at the entry instant
   datetime from_srv = clock.UtcToServer(from_utc);
   int want = (int)(((long)last_utc - (long)from_utc) / 300) + 1;
   MqlRates r[];
   int n = CopyRates(m_symbol, PERIOD_M5, from_srv, clock.UtcToServer(last_utc), r);
   if(n != want)
     {
      plan.note = "M5 bars 15:30-15:55 London not complete yet";
      return false;
     }
   for(int i = 0; i < n; i++)
      if((long)r[i].time != (long)from_srv + (long)i * 300)
        {
         plan.note = "a 5-minute bar is missing in the drift window";
         return true;                                              // side 0: no trade today (the lab skipped such days)
        }
   double drift = r[n - 1].close - r[0].open;
   if(drift == 0.0)
     {
      plan.note = "no drift";
      return true;
     }
   double hi = r[0].high;
   double lo = r[0].low;
   for(int i = 1; i < n; i++)
     {
      if(r[i].high > hi)
         hi = r[i].high;
      if(r[i].low < lo)
         lo = r[i].low;
     }
   MqlTick tick;
   if(!SymbolInfoTick(m_symbol, tick) || tick.bid <= 0.0 || tick.ask <= 0.0)
     {
      plan.note = "no quote yet";
      return false;
     }
   double buffer = SEESARE_LDN_BUFFER_PIPS * PipSize();
   if(drift > 0.0)
     {
      plan.side = -1;
      plan.stop_distance = (hi + buffer) - tick.bid;
     }
   else
     {
      plan.side = 1;
      plan.stop_distance = tick.ask - (lo - buffer);
     }
   if(plan.stop_distance <= 0.0)
     {
      plan.side = 0;
      plan.note = "price is already beyond the drift window's extreme";
      return true;
     }
   plan.ratio             = SEESARE_LDN_RATIO;
   plan.place_target      = true;
   plan.max_spread_points = PipsToPoints(SEESARE_LDN_MAX_SPREAD_PIPS);
   plan.note              = "fade drift " + DoubleToString(drift / PipSize(), 1) + " pips";
   return true;
  }

#endif

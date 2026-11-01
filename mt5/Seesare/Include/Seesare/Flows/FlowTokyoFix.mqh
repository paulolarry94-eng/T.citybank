//+------------------------------------------------------------------+
//|                                   Seesare/Flows/FlowTokyoFix.mqh |
//| Module 1: Tokyo fix on gotobi days, USDJPY. UNCOMPILED SOURCE.   |
//|                                                                  |
//| Rules = research/truth/strategies/tokyo_fix_gotobi_v1.py,        |
//| configuration pre2300 (Truth Lab Tier B, forward-test candidate):|
//|   buy at 23:00 UTC (08:00 JST) on the evening before a gotobi    |
//|   fix (the 5th, 10th, 15th, 20th, 25th or last day of the month, |
//|   moved to the previous Tokyo business day), sell at the 00:55   |
//|   UTC fix (09:55 JST, no DST in Japan); protective stop 0.3% of  |
//|   price; no target (time exit).                                  |
//| Evidence: 2011-19 +0.041R (644 trades), 2020-22 +0.064R,         |
//|   2023-25 +0.052R (214 trades, t 1.45, PF 1.28); R = 0.3% of     |
//|   price, about 36-45 pips. Average win 11-18 pips, average loss  |
//|   11-20 pips: a payoff ratio near 1, not 5:1. A declared 7:1     |
//|   target is reached on 0.1-3.3% of mornings depending on the     |
//|   stop (research/flows study, 2026-11-01).                       |
//| Declared ratio 1.04 = average win / average loss of the 2011-19  |
//|   lab trades. SEESARE multiplier at 1.04: 0.0882; planned delta  |
//|   at L0 $0.12, while one 0.01 lot at the 0.3% stop risks $3.00:  |
//|   at $1,000 this module can only run SHADOW (paper) in SEESARE.  |
//| Spread guard: 2.0 pips (not in the research; Exness spreads at   |
//|   23:00 UTC were ~0 most months, 4.8 pips in one winter sample). |
//+------------------------------------------------------------------+
#ifndef SEESARE_FLOWS_TOKYOFIX_MQH
#define SEESARE_FLOWS_TOKYOFIX_MQH

#include <Seesare\Flows\FlowModule.mqh>

#define SEESARE_TOKYO_ENTRY_MIN        (23 * 60)   // 23:00 UTC on the UTC day before the fix
#define SEESARE_TOKYO_EXIT_MIN         55          // 00:55 UTC on the fix date
#define SEESARE_TOKYO_STOP_PCT         0.003
#define SEESARE_TOKYO_RATIO            1.04
#define SEESARE_TOKYO_MAX_SPREAD_PIPS  2.0

class CSeesareFlowTokyoFix : public CSeesareFlowModule
  {
public:
                     CSeesareFlowTokyoFix(const string symbol);
   virtual bool      SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot);
   virtual bool      Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan);
   virtual double    DeclaredRatio(void) const { return SEESARE_TOKYO_RATIO; }
  };

CSeesareFlowTokyoFix::CSeesareFlowTokyoFix(const string symbol)
  {
   m_id           = "TOKYO_FIX";
   m_symbol       = symbol;
   m_domain       = "forex";
   m_evidence     = SEESARE_EVIDENCE_CANDIDATE;
   m_evidence_ref = "research/results/truth/tokyo_fix_gotobi_v1, Tier B, 2023-25 +0.052R over 214 trades";
  }

bool CSeesareFlowTokyoFix::SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot)
  {
   m_error = "";
   datetime d0 = CSeesareDst::Midnight(utc_day);
   datetime fix = (datetime)((long)d0 + SEESARE_DAY_SEC);       // the Tokyo date of the fix (23:00 UTC = 08:00 JST next day)
   bool known = false;
   if(!CSeesareCalendar::IsGotobiFix(fix, known))
     {
      if(!known)
         m_error = "TOKYO_FIX: the Japanese holiday table does not cover " + CSeesareDst::IsoUtc(fix) +
                   ": regenerate Calendar.mqh (python3 tools/seesare_flows.py --holidays)";
      return false;
     }
   slot.module_id = m_id;
   slot.day_utc   = d0;
   slot.entry_utc = (datetime)((long)d0 + SEESARE_TOKYO_ENTRY_MIN * 60);
   slot.exit_utc  = (datetime)((long)fix + SEESARE_TOKYO_EXIT_MIN * 60);
   return true;
  }

bool CSeesareFlowTokyoFix::Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan)
  {
   SeesareClearPlan(plan);
   MqlTick tick;
   if(!SymbolInfoTick(m_symbol, tick) || tick.ask <= 0.0)
     {
      plan.note = "no quote yet";
      return false;
     }
   plan.side              = 1;
   plan.stop_distance     = tick.ask * SEESARE_TOKYO_STOP_PCT;
   plan.ratio             = SEESARE_TOKYO_RATIO;
   plan.place_target      = false;
   plan.max_spread_points = PipsToPoints(SEESARE_TOKYO_MAX_SPREAD_PIPS);
   plan.note              = "gotobi fix " + StringSubstr(CSeesareDst::IsoUtc(slot.exit_utc), 0, 10);
   return true;
  }

#endif

//+------------------------------------------------------------------+
//|                                      Seesare/Risk/Exposure.mqh   |
//| SEESARE router, Phase 2: from the ledger's planned delta to a    |
//| broker volume (SEESARE 9.1). UNCOMPILED SOURCE.                  |
//| Twin: tools/seesare_flows.py size().                             |
//|                                                                  |
//| plan     = CSeesareCycleLedger::PlanUsdAt(module weight): the    |
//|            drawdown-keyed ladder, 0.30 x weight x room left      |
//| per lot  = loss at the stop for 1.0 lot (OrderCalcProfit) +      |
//|            commission per lot                                    |
//| volume   = floor((plan / per lot) / volume step) x step, never   |
//|            rounded up (rounding up would break the envelope)     |
//| feasible = volume >= broker minimum AND the envelope guard       |
//|            allows volume x per lot; otherwise the event runs as  |
//|            SHADOW with the unrounded "shadow lot" plan / per lot.|
//|                                                                  |
//| Cent accounts (Phase 3, e.g. RoboForex ProCent): the account is  |
//| kept in US cents (USC) and one lot is 1/100 of a standard lot.   |
//| Nothing here assumes a contract size: OrderCalcProfit uses the   |
//| broker's own contract, and its result (in account money) is      |
//| divided by UnitsPerUsd (USD 1, USC 100) so the plan, the risk    |
//| and the envelope stay in dollars of the $1,000 virtual baseline. |
//| A cent account lowers the smallest tradeable risk 100x, but a    |
//| plan below 0.01 lot of the cent contract is still SHADOW (twin:  |
//| tools/seesare_outbox.py level_table; USDJPY at a 0.3% stop with  |
//| weight 0.57: real at every level from L0 to L14).                |
//+------------------------------------------------------------------+
#ifndef SEESARE_RISK_EXPOSURE_MQH
#define SEESARE_RISK_EXPOSURE_MQH

#include <Seesare\Ledger\CycleLedger.mqh>

struct SSeesareSizing
  {
   bool              feasible;
   double            plan_usd;
   double            loss_per_lot;    // USD lost per 1.0 lot at the stop (price move only)
   double            per_lot;         // loss_per_lot + commission per lot
   double            virtual_volume;  // plan / per lot: the shadow lot
   double            volume;          // rounded down to the step; 0 when not feasible
   double            risk_usd;        // volume x per lot
   string            why;
  };

class CSeesareExposure
  {
public:
   //--- account money units per US dollar: USD 1, US cents 100, anything else 0 (refuse: no conversion is guessed)
   static double     UnitsPerUsd(const string currency)
     {
      string c = currency;
      StringTrimLeft(c);
      StringTrimRight(c);
      StringToUpper(c);
      if(c == "USD")
         return 1.0;
      if(c == "USC" || c == "USX" || c == "USCENT" || c == "US CENT" || c == "CENT")
         return 100.0;
      return 0.0;
     }
   static double     AccountUnitsPerUsd(void)
     {
      return UnitsPerUsd(AccountInfoString(ACCOUNT_CURRENCY));
     }
   //--- planned risk at a drawdown level, rounded exactly as the ledger writes it (PlanUsdAt)
   static double     PlanAtLevel(const int level, const double weight)
     {
      return StringToDouble(CSeesareLadder::PlanText(level, weight));
     }
   //--- lots = floor((plan / per lot) / step) x step, capped at vmax; feasible if >= vmin
   static double     Volume(const double plan_usd, const double per_lot_usd, const double step, const double vmin,
                            const double vmax, double &virtual_volume, bool &feasible)
     {
      virtual_volume = 0.0;
      feasible = false;
      if(plan_usd <= 0.0 || per_lot_usd <= 0.0 || step <= 0.0)
         return 0.0;
      virtual_volume = plan_usd / per_lot_usd;
      double vol = MathFloor(virtual_volume / step + 1e-9) * step;
      if(vol > vmax)
         vol = vmax;
      feasible = (vol >= vmin - 1e-12);
      return vol;
     }
   //--- deepest drawdown level (0-14) whose plan still buys the broker minimum; -1 if none (L15 never trades)
   static int        LowestFeasibleLevel(const double weight, const double per_lot_usd, const double step, const double vmin)
     {
      int lowest = -1;
      for(int lv = 0; lv < SEESARE_LEVELS; lv++)
        {
         double virtual_volume = 0.0;
         bool ok = false;
         Volume(PlanAtLevel(lv, weight), per_lot_usd, step, vmin, DBL_MAX, virtual_volume, ok);
         if(ok)
            lowest = lv;
        }
      return lowest;
     }
   //--- USD lost by 1.0 lot between entry and stop (positive), from the broker's own contract maths;
   //--- units_per_usd converts the account money (USD 1, US cents 100) back to dollars
   static bool       LossPerLot(const string symbol, const int side, const double entry, const double stop,
                                const double units_per_usd, double &loss)
     {
      loss = 0.0;
      if(units_per_usd <= 0.0)
         return false;
      double profit = 0.0;
      ENUM_ORDER_TYPE type = (side > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
      if(!OrderCalcProfit(type, symbol, 1.0, entry, stop, profit))
         return false;
      loss = -profit / units_per_usd;
      return (loss > 0.0);
     }
   static bool       Size(const CSeesareCycleLedger &ledger, const string symbol, const int side, const double entry,
                          const double stop, const double weight, const double commission_per_lot,
                          const double units_per_usd, SSeesareSizing &out)
     {
      out.feasible       = false;
      out.plan_usd       = ledger.PlanUsdAt(weight);
      out.loss_per_lot   = 0.0;
      out.per_lot        = 0.0;
      out.virtual_volume = 0.0;
      out.volume         = 0.0;
      out.risk_usd       = 0.0;
      out.why            = "";
      if(out.plan_usd < 0.0)
        {
         out.why = "the ledger is not open or the weight is outside (0, 1.00]";
         return false;
        }
      if(!LossPerLot(symbol, side, entry, stop, units_per_usd, out.loss_per_lot))
        {
         out.why = "OrderCalcProfit failed for " + symbol + " or the account currency is not USD or US cents";
         return false;
        }
      out.per_lot = out.loss_per_lot + (commission_per_lot > 0.0 ? commission_per_lot : 0.0);
      bool ok = false;
      double vol = Volume(out.plan_usd, out.per_lot, SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP),
                          SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN), SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX),
                          out.virtual_volume, ok);
      if(!ok)
        {
         out.why = "plan " + CSeesareText::Fmt(out.plan_usd, 4) + " USD buys " + CSeesareText::Fmt(out.virtual_volume, 4) +
                   " lots, below the broker minimum: SHADOW";
         return true;
        }
      out.volume   = vol;
      out.risk_usd = vol * out.per_lot;
      if(!ledger.AllowsRealRisk(out.risk_usd))
        {
         out.why = "the envelope guard refuses " + CSeesareText::Fmt(out.risk_usd, 2) + " USD of risk: SHADOW";
         out.volume = 0.0;
         return true;
        }
      out.feasible = true;
      out.why = CSeesareText::Fmt(vol, 2) + " lots, risk " + CSeesareText::Fmt(out.risk_usd, 2) + " USD";
      return true;
     }
  };

#endif

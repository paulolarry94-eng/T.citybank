//+------------------------------------------------------------------+
//| NorthStarRisk.mqh — shared exposure library + client API          |
//|                                                                  |
//| STATUS: SOURCE ONLY. NOT COMPILED. Written in a sandbox without   |
//| MetaEditor; compile in MetaEditor and fix any errors before use.  |
//|                                                                  |
//| Every strategy EA calls NS_RequestRisk() before sending an order. |
//| It returns the risk % it may use (0 = do not trade). It enforces  |
//| the North Star caps against ALL open positions on the account and |
//| obeys the state published by NorthStarGovernor.mq5. If the        |
//| governor is not running (stale heartbeat) it returns 0 (fail-safe)|
//|                                                                  |
//| Rules: research/northstar/PREREGISTRATION.md §6 + amendments 2-3. |
//+------------------------------------------------------------------+
#ifndef NORTHSTAR_RISK_MQH
#define NORTHSTAR_RISK_MQH

#define NS_GV_STATE      "NS_STATE"       // 0 GREEN, 1 AMBER, 2 RED
#define NS_GV_MULT       "NS_MULT"        // size multiplier published by the governor (1.0 or 0.5)
#define NS_GV_HEARTBEAT  "NS_HEARTBEAT"   // server time of the governor's last cycle
#define NS_GV_CAP_TRADE  "NS_CAP_TRADE"   // caps in % of equity, published by the governor
#define NS_GV_CAP_TOTAL  "NS_CAP_TOTAL"
#define NS_GV_CAP_INST   "NS_CAP_INST"
#define NS_GV_CAP_DIR    "NS_CAP_DIR"
#define NS_GV_CAP_USD    "NS_CAP_USD"
#define NS_HEARTBEAT_MAX 120              // seconds

//--- USD direction of a position: +1 = USD-short exposure, -1 = USD-long, 0 = no USD leg
int NS_UsdSign(const string sym, const int side)
{
   string base = SymbolInfoString(sym, SYMBOL_CURRENCY_BASE);
   string quote = SymbolInfoString(sym, SYMBOL_CURRENCY_PROFIT);
   if(quote == "USD") return  side;      // long XAUUSD / EURUSD / GBPUSD = short USD
   if(base == "USD")  return -side;      // long USDJPY = long USD
   return 0;
}

//--- money lost if price moves from `price` to `stop` with `volume` lots
double NS_RiskMoney(const string sym, const double price, const double stop, const double volume)
{
   double tick_size  = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tick_value <= 0.0) tick_value = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE);
   if(tick_size <= 0.0 || tick_value <= 0.0) return -1.0;
   return MathAbs(price - stop) / tick_size * tick_value * volume;
}

struct NSExposure
{
   double total;        // % of equity at risk, all positions
   double inst;         // same symbol
   double same_dir;     // same symbol and same direction
   double usd_net;      // signed USD-short exposure
   bool   unprotected;  // a position without a stop exists
};

//--- current exposure (initial-stop risk of every open position, % of equity)
NSExposure NS_Exposure(const string sym, const int side)
{
   NSExposure e; e.total = 0; e.inst = 0; e.same_dir = 0; e.usd_net = 0; e.unprotected = false;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(eq <= 0) { e.unprotected = true; return e; }
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0 || !PositionSelectByTicket(tk)) continue;
      string ps = PositionGetString(POSITION_SYMBOL);
      int    pd = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
      double sl = PositionGetDouble(POSITION_SL);
      if(sl <= 0) { e.unprotected = true; continue; }
      double rm = NS_RiskMoney(ps, PositionGetDouble(POSITION_PRICE_OPEN), sl, PositionGetDouble(POSITION_VOLUME));
      // a stop beyond entry (locked profit) carries no risk
      double po = PositionGetDouble(POSITION_PRICE_OPEN);
      if((pd > 0 && sl >= po) || (pd < 0 && sl <= po)) rm = 0;
      if(rm < 0) { e.unprotected = true; continue; }
      double pct = 100.0 * rm / eq;
      e.total += pct;
      if(ps == sym) { e.inst += pct; if(pd == side) e.same_dir += pct; }
      e.usd_net += pct * NS_UsdSign(ps, pd);
   }
   return e;
}

//--- client API: risk % this order may use (0 = skip). desired_pct = base risk x leg weight.
double NS_RequestRisk(const string sym, const int side, const double desired_pct, string &why)
{
   why = "";
   if(!GlobalVariableCheck(NS_GV_HEARTBEAT) ||
      (double)TimeCurrent() - GlobalVariableGet(NS_GV_HEARTBEAT) > NS_HEARTBEAT_MAX)
   { why = "governor not running (fail-safe: no new trades)"; return 0.0; }
   int state = (int)GlobalVariableGet(NS_GV_STATE);
   if(state == 2) { why = "RED: no new entries"; return 0.0; }
   double mult = GlobalVariableCheck(NS_GV_MULT) ? GlobalVariableGet(NS_GV_MULT) : 1.0;
   double f = desired_pct * mult;
   double cap_trade = GlobalVariableGet(NS_GV_CAP_TRADE), cap_total = GlobalVariableGet(NS_GV_CAP_TOTAL);
   double cap_inst = GlobalVariableGet(NS_GV_CAP_INST), cap_dir = GlobalVariableGet(NS_GV_CAP_DIR);
   double cap_usd = GlobalVariableGet(NS_GV_CAP_USD);
   f = MathMin(f, cap_trade);
   NSExposure e = NS_Exposure(sym, side);
   if(e.unprotected)                         { why = "an open position has no confirmed stop"; return 0.0; }
   if(e.total + f > cap_total + 1e-9)        { why = "total open-risk cap"; return 0.0; }
   if(e.inst + f > cap_inst + 1e-9)          { why = "instrument cap"; return 0.0; }
   if(e.same_dir + f > cap_dir + 1e-9)       { why = "same instrument + direction cap"; return 0.0; }
   if(MathAbs(e.usd_net + f * NS_UsdSign(sym, side)) > cap_usd + 1e-9) { why = "net USD-direction cap"; return 0.0; }
   return f;
}

//--- client helper: lots for a given risk % and stop (rounded DOWN to the volume step; 0 if below minimum)
double NS_LotsForRisk(const string sym, const double risk_pct, const double entry, const double stop)
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double per_lot = NS_RiskMoney(sym, entry, stop, 1.0);
   if(per_lot <= 0 || risk_pct <= 0) return 0.0;
   double lots = eq * risk_pct / 100.0 / per_lot;
   double step = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   if(step > 0) lots = MathFloor(lots / step) * step;
   if(lots < vmin) return 0.0;               // never round UP into more risk than allowed
   return MathMin(lots, vmax);
}

#endif

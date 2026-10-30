//+------------------------------------------------------------------+
//| NorthStarGovernor.mq5 — portfolio risk governor + weekly logs     |
//|                                                                  |
//| STATUS: SOURCE ONLY. NOT COMPILED, NOT TESTED IN MT5. Written in  |
//| a sandbox without MetaEditor. Compile in MetaEditor, fix errors,  |
//| then run on DEMO only (see research/northstar/NORTHSTAR_REPORT.md)|
//|                                                                  |
//| Attach to ONE chart. It does not open trades. It:                |
//|  * computes GREEN / AMBER / RED (PREREGISTRATION.md §6, amend. 2-3)|
//|  * publishes state, size multiplier and caps as GlobalVariables;  |
//|    strategy EAs call NS_RequestRisk() from NorthStarRisk.mqh      |
//|  * closes a position at market ONLY if it has no server stop      |
//|    (optional, default on) — it never widens or adds to a stop     |
//|  * writes trades.csv / equity.csv / events.csv (Common\Files\     |
//|    NorthStar\) for research/northstar/weekly.py                   |
//| Demo policy (amendment 3): FF+RED — AMBER is shadow-only (logged, |
//| no size change). Set InpAmberHalvesRisk=true for the RAG policy.  |
//+------------------------------------------------------------------+
#property copyright "North Star research"
#property version   "1.00"
#property description "Portfolio risk governor (uncompiled source). Demo only until compiled, parity-tested and forward-tested."

#include <Trade\Trade.mqh>
#include "NorthStarRisk.mqh"

input group "=== Caps (% of equity, initial-stop risk) ==="
input double InpCapTrade      = 2.0;    // per trade
input double InpCapTotal      = 10.0;   // all open positions
input double InpCapInstrument = 4.0;    // per instrument
input double InpCapSameDir    = 3.0;    // same instrument and direction
input double InpCapUsd        = 6.0;    // net USD direction
input group "=== AMBER (shadow unless InpAmberHalvesRisk) ==="
input bool   InpAmberHalvesRisk = false; // false = FF+RED demo policy; true = RAG
input double InpAmberDD       = 10.0;   // drawdown from peak, %
input double InpAmberDayLoss  = 3.0;    // day's loss, %
input double InpAmber5DayLoss = 6.0;    // rolling 5-trading-day loss, %
input double InpAmberOpenRisk = 80.0;   // open risk above this % of the total cap
input group "=== RED (circuit breaker) ==="
input double InpRedDD         = 20.0;   // drawdown from peak, %
input double InpRedRearm      = 5.0;    // after acknowledgement, re-arm on a further loss of this %
input double InpRedDayLoss    = 6.0;    // day's loss, %
input int    InpStaleMinutes  = 5;      // no tick for this long in trading hours
input int    InpMaxRejects    = 3;      // order rejections in one day
input double InpSpreadMult    = 4.0;    // spread above this x the rolling median
input double InpMinMarginLvl  = 300.0;  // margin level %, with open positions
input bool   InpCloseUnprotected = true; // close a position that has no stop after 60 s
input group "=== Monitoring ==="
input string InpSymbols = "XAUUSD,EURUSD,GBPUSD,USDJPY,GBPJPY,EURGBP"; // symbols checked for stale feed / spread
input string InpLegMap  = "";           // "magic:leg,magic:leg" — names used in trades.csv
input int    InpTimerSeconds = 10;

#define DIR "NorthStar\\"
CTrade   g_trade;
string   g_syms[];
double   g_peak = 0, g_day_start_eq = 0, g_ack_eq = -1;
int      g_state = 0, g_day = -1, g_rejects = 0, g_red_reason_n = 0;
double   g_day_eq[];              // start-of-day equity, last 6 trading days
double   g_spread_hist[];         // per symbol ring of 240 samples (x symbols)
int      g_spread_n[];
datetime g_unprot_since[];
ulong    g_unprot_ticket[];
datetime g_last_equity_log = 0, g_last_shadow = 0;
// per-position memory for trades.csv
ulong    g_pos_id[]; double g_pos_sl[]; double g_pos_spread[]; double g_pos_req[];

string Iso(datetime t) { MqlDateTime d; TimeToStruct(t, d); return StringFormat("%04d-%02d-%02d %02d:%02d:%02d", d.year, d.mon, d.day, d.hour, d.min, d.sec); }

void Append(string file, string header, string line)
{
   bool exists = FileIsExist(DIR + file, FILE_COMMON);
   int h = FileOpen(DIR + file, FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ);
   if(h == INVALID_HANDLE) { Print("NorthStar: cannot open ", file, " err ", GetLastError()); return; }
   if(!exists || FileSize(h) == 0) FileWriteString(h, header + "\n");
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, line + "\n");
   FileClose(h);
}

void Event(string type, string detail)
{
   StringReplace(detail, ",", ";");
   Append("events.csv", "time,type,detail", Iso(TimeGMT()) + "," + type + "," + detail);
   Print("NorthStar ", type, ": ", detail);
}

string LegName(long magic)
{
   string parts[]; int n = StringSplit(InpLegMap, ',', parts);
   for(int i = 0; i < n; i++)
   {
      string kv[]; if(StringSplit(parts[i], ':', kv) == 2 && (long)StringToInteger(kv[0]) == magic) return kv[1];
   }
   return "magic" + IntegerToString(magic);
}

void Persist()
{
   GlobalVariableSet("NS_PEAK", g_peak);
   GlobalVariableSet("NS_ACK_EQ", g_ack_eq);
   GlobalVariableSet("NS_RED_LATCH", g_state == 2 ? 1.0 : 0.0);
}

int OnInit()
{
   int n = StringSplit(InpSymbols, ',', g_syms);
   ArrayResize(g_spread_hist, n * 240); ArrayInitialize(g_spread_hist, 0);
   ArrayResize(g_spread_n, n); ArrayInitialize(g_spread_n, 0);
   ArrayResize(g_day_eq, 6); ArrayInitialize(g_day_eq, 0);
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   g_peak = GlobalVariableCheck("NS_PEAK") ? MathMax(GlobalVariableGet("NS_PEAK"), eq) : eq;
   g_ack_eq = GlobalVariableCheck("NS_ACK_EQ") ? GlobalVariableGet("NS_ACK_EQ") : -1;
   if(GlobalVariableCheck("NS_RED_LATCH") && GlobalVariableGet("NS_RED_LATCH") > 0) g_state = 2;   // RED survives restarts
   g_day_start_eq = eq;
   GlobalVariableSet(NS_GV_CAP_TRADE, InpCapTrade); GlobalVariableSet(NS_GV_CAP_TOTAL, InpCapTotal);
   GlobalVariableSet(NS_GV_CAP_INST, InpCapInstrument); GlobalVariableSet(NS_GV_CAP_DIR, InpCapSameDir);
   GlobalVariableSet(NS_GV_CAP_USD, InpCapUsd);
   if(!GlobalVariableCheck("NS_ACK")) GlobalVariableSet("NS_ACK", 0);
   EventSetTimer(InpTimerSeconds);
   Event("START", StringFormat("equity %.2f peak %.2f state %d", eq, g_peak, g_state));
   Cycle();
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); Persist(); Comment(""); }

double MedianSpread(int s)
{
   int m = MathMin(g_spread_n[s], 240); if(m < 30) return -1;
   double v[]; ArrayResize(v, m);
   for(int i = 0; i < m; i++) v[i] = g_spread_hist[s * 240 + i];
   ArraySort(v); return v[m / 2];
}

bool TradingHours(string sym)
{
   MqlDateTime d; TimeToStruct(TimeGMT(), d);
   if(d.day_of_week == 0 || d.day_of_week == 6) return false;
   if(d.day_of_week == 5 && d.hour >= 20) return false;
   int mins = d.hour * 60 + d.min;
   return !(mins >= 20 * 60 + 30 && mins < 23 * 60);      // rollover block is not "trading hours"
}

void OnTimer() { Cycle(); }

void Cycle()
{
   datetime now = TimeGMT();
   double eq = AccountInfoDouble(ACCOUNT_EQUITY), bal = AccountInfoDouble(ACCOUNT_BALANCE);
   MqlDateTime d; TimeToStruct(now, d);
   int day = (int)(now / 86400);
   if(day != g_day)
   {
      if(d.day_of_week != 0 && d.day_of_week != 6)
      {
         for(int i = 5; i > 0; i--) g_day_eq[i] = g_day_eq[i - 1];
         g_day_eq[0] = eq;
      }
      g_day = day; g_day_start_eq = eq; g_rejects = 0;
   }
   if(eq > g_peak) g_peak = eq;
   double dd = 100.0 * (1.0 - eq / g_peak);
   double day_loss = g_day_start_eq > 0 ? 100.0 * (1.0 - eq / g_day_start_eq) : 0;
   double ref5 = g_day_eq[5] > 0 ? g_day_eq[5] : (g_day_eq[4] > 0 ? g_day_eq[4] : 0);
   double loss5 = ref5 > 0 ? 100.0 * (1.0 - eq / ref5) : 0;
   NSExposure e = NS_Exposure("", 0);

   // ---- RED checks
   string red = "";
   bool red_dd = dd >= InpRedDD && (g_ack_eq < 0 || eq <= g_ack_eq * (1.0 - InpRedRearm / 100.0));
   if(red_dd) red += StringFormat("drawdown %.1f%%; ", dd);
   if(day_loss >= InpRedDayLoss) red += StringFormat("day loss %.1f%%; ", day_loss);
   if(g_rejects >= InpMaxRejects) red += StringFormat("%d rejections today; ", g_rejects);
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   if(PositionsTotal() > 0 && ml > 0 && ml < InpMinMarginLvl) red += StringFormat("margin level %.0f%%; ", ml);
   for(int s = 0; s < ArraySize(g_syms); s++)
   {
      string sym = g_syms[s];
      if(!SymbolSelect(sym, true)) continue;
      MqlTick tk;
      if(!SymbolInfoTick(sym, tk)) continue;
      if(TradingHours(sym) && (double)(TimeCurrent() - tk.time) > InpStaleMinutes * 60)
         red += sym + " feed stale; ";
      double sp = (double)SymbolInfoInteger(sym, SYMBOL_SPREAD);
      double med = MedianSpread(s);
      if(med > 0 && sp > InpSpreadMult * med && TradingHours(sym)) red += StringFormat("%s spread %.0f vs median %.0f; ", sym, sp, med);
      g_spread_hist[s * 240 + (g_spread_n[s] % 240)] = sp; g_spread_n[s]++;
   }
   // ---- AMBER checks (shadow unless InpAmberHalvesRisk)
   string amber = "";
   if(dd >= InpAmberDD) amber += StringFormat("drawdown %.1f%%; ", dd);
   if(day_loss >= InpAmberDayLoss) amber += StringFormat("day loss %.1f%%; ", day_loss);
   if(loss5 >= InpAmber5DayLoss) amber += StringFormat("5-day loss %.1f%%; ", loss5);
   if(e.total > InpAmberOpenRisk / 100.0 * InpCapTotal) amber += StringFormat("open risk %.1f%%; ", e.total);

   // ---- state machine
   int prev = g_state;
   if(g_state == 2)
   {
      bool ack = GlobalVariableGet("NS_ACK") > 0;
      bool live_ok = StringFind(red, "stale") < 0 && StringFind(red, "spread") < 0 && StringFind(red, "margin") < 0 && StringFind(red, "rejection") < 0;
      if(ack && live_ok)
      {
         GlobalVariableSet("NS_ACK", 0); g_ack_eq = eq;
         g_state = InpAmberHalvesRisk ? 1 : 0;
         Event("ACK", StringFormat("operator acknowledgement; resume in %s; RED re-arms below %.2f", g_state == 1 ? "AMBER" : "GREEN", eq * (1 - InpRedRearm / 100.0)));
      }
   }
   else
   {
      if(red != "") { g_state = 2; Event("RED", red); }
      else if(amber != "")
      {
         if(InpAmberHalvesRisk) g_state = 1;
         else if(now - g_last_shadow >= 3600) { Event("AMBER_SHADOW", amber); g_last_shadow = now; }   // at most hourly
      }
      else if(g_state == 1 && dd < InpAmberDD) g_state = 0;
      if(dd < InpAmberDD) g_ack_eq = -1;
   }
   if(g_state == 1 && prev != 1) Event("AMBER", amber);
   if(g_state == 0 && prev != 0) Event("GREEN", StringFormat("drawdown %.1f%%", dd));

   // ---- unprotected positions (no server stop): close at market after 60 s
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0 || !PositionSelectByTicket(tk) || PositionGetDouble(POSITION_SL) > 0) continue;
      datetime opened = (datetime)PositionGetInteger(POSITION_TIME);
      if(InpCloseUnprotected && TimeCurrent() - opened > 60)
      {
         Event("UNPROTECTED", StringFormat("ticket %I64u %s has no stop; closing at market", tk, PositionGetString(POSITION_SYMBOL)));
         g_trade.PositionClose(tk);
      }
   }

   // ---- publish
   GlobalVariableSet(NS_GV_STATE, g_state);
   GlobalVariableSet(NS_GV_MULT, g_state == 1 ? 0.5 : 1.0);
   GlobalVariableSet(NS_GV_HEARTBEAT, (double)TimeCurrent());
   Persist();
   if(now - g_last_equity_log >= 3600 || g_state != prev)
   {
      string st = g_state == 0 ? "GREEN" : (g_state == 1 ? "AMBER" : "RED");
      Append("equity.csv", "time,balance,equity,open_risk_pct,state", StringFormat("%s,%.2f,%.2f,%.3f,%s", Iso(now), bal, eq, e.total, st));
      g_last_equity_log = now;
   }
   Comment(StringFormat("NORTH STAR GOVERNOR (uncompiled-source build)\nstate %s | DD %.2f%% | day %.2f%% | 5-day %.2f%% | open risk %.2f%%\n%s%s",
           g_state == 0 ? "GREEN" : (g_state == 1 ? "AMBER" : "RED"), dd, day_loss, loss5, e.total,
           red != "" ? "RED: " + red + "\n" : "", amber != "" ? "AMBER" + (InpAmberHalvesRisk ? "" : " (shadow)") + ": " + amber : ""));
}

int PosIndex(ulong id) { for(int i = 0; i < ArraySize(g_pos_id); i++) if(g_pos_id[i] == id) return i; return -1; }

void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &request, const MqlTradeResult &result)
{
   if(trans.type == TRADE_TRANSACTION_REQUEST)
   {
      if(result.retcode != TRADE_RETCODE_DONE && result.retcode != TRADE_RETCODE_PLACED && result.retcode != TRADE_RETCODE_DONE_PARTIAL)
      {
         g_rejects++;
         Event("REJECT", StringFormat("%s retcode %u (%s)", request.symbol, result.retcode, result.comment));
      }
      return;
   }
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD || !HistoryDealSelect(trans.deal)) return;
   long entry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   ulong pid = (ulong)HistoryDealGetInteger(trans.deal, DEAL_POSITION_ID);
   string sym = HistoryDealGetString(trans.deal, DEAL_SYMBOL);
   if(entry == DEAL_ENTRY_IN)
   {
      int k = ArraySize(g_pos_id);
      ArrayResize(g_pos_id, k + 1); ArrayResize(g_pos_sl, k + 1); ArrayResize(g_pos_spread, k + 1); ArrayResize(g_pos_req, k + 1);
      g_pos_id[k] = pid; g_pos_sl[k] = 0; g_pos_spread[k] = (double)SymbolInfoInteger(sym, SYMBOL_SPREAD); g_pos_req[k] = 0;
      if(PositionSelectByTicket(pid)) g_pos_sl[k] = PositionGetDouble(POSITION_SL);
      ulong ord = (ulong)HistoryDealGetInteger(trans.deal, DEAL_ORDER);
      if(HistoryOrderSelect(ord)) g_pos_req[k] = HistoryOrderGetDouble(ord, ORDER_PRICE_OPEN);
      return;
   }
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY) return;
   if(!HistorySelectByPosition(pid)) return;
   double p_in = 0, vol = 0, swap = 0, comm = 0, pnl = 0, p_out = HistoryDealGetDouble(trans.deal, DEAL_PRICE);
   datetime t_in = 0, t_out = (datetime)HistoryDealGetInteger(trans.deal, DEAL_TIME);
   long magic = 0; int side = 0;
   for(int i = 0; i < HistoryDealsTotal(); i++)
   {
      ulong dl = HistoryDealGetTicket(i);
      long en = HistoryDealGetInteger(dl, DEAL_ENTRY);
      swap += HistoryDealGetDouble(dl, DEAL_SWAP); comm += HistoryDealGetDouble(dl, DEAL_COMMISSION); pnl += HistoryDealGetDouble(dl, DEAL_PROFIT);
      if(en == DEAL_ENTRY_IN)
      {
         p_in = HistoryDealGetDouble(dl, DEAL_PRICE); vol = HistoryDealGetDouble(dl, DEAL_VOLUME);
         t_in = (datetime)HistoryDealGetInteger(dl, DEAL_TIME); magic = HistoryDealGetInteger(dl, DEAL_MAGIC);
         side = HistoryDealGetInteger(dl, DEAL_TYPE) == DEAL_TYPE_BUY ? 1 : -1;
      }
   }
   long gmt_off = (long)MathRound((double)(TimeGMT() - TimeCurrent()) / 900.0) * 900;   // server -> UTC, 15-min grid
   t_in = (datetime)((long)t_in + gmt_off); t_out = (datetime)((long)t_out + gmt_off);
   int k = PosIndex(pid);
   double sl = k >= 0 ? g_pos_sl[k] : 0, spread = k >= 0 ? g_pos_spread[k] : -1, req = k >= 0 ? g_pos_req[k] : 0;
   double risk = sl > 0 ? NS_RiskMoney(sym, p_in, sl, vol) : -1;
   double net = pnl + swap + comm;
   double r = risk > 0 ? net / risk : 0;
   double point = SymbolInfoDouble(sym, SYMBOL_POINT);
   double slip = (req > 0 && point > 0) ? side * (p_in - req) / point : 0;     // + = worse than requested
   double slip_r = (sl > 0 && MathAbs(p_in - sl) > 0) ? slip * point / MathAbs(p_in - sl) : 0;
   Append("trades.csv", "ticket,leg,symbol,side,t_open,t_close,entry,exit,stop,risk_money,pnl_money,r,spread_entry,slippage_pts,slippage_r,swap,commission",
          StringFormat("%I64u,%s,%s,%d,%s,%s,%.5f,%.5f,%.5f,%.2f,%.2f,%.4f,%.1f,%.1f,%.4f,%.2f,%.2f", pid, LegName(magic), sym, side, Iso(t_in), Iso(t_out),
                       p_in, p_out, sl, risk, net, r, spread, slip, slip_r, swap, comm));
}

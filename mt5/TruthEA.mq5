//+------------------------------------------------------------------+
//| TruthEA.mq5 — template EA for strategies that pass the Truth Lab  |
//|                                                                  |
//| STATUS: SOURCE ONLY. NOT COMPILED, NOT TESTED IN MT5 (written     |
//| without MetaEditor). Compile with F7, fix any errors, then run    |
//| the parity check before any demo.                                 |
//|                                                                  |
//| It reproduces the lab's execution rules:                         |
//|  * decisions on CLOSED bars of InpTF; market entry on the first   |
//|    tick of the next bar, stop sent with the order                 |
//|  * optional target in R, chandelier trail N x ATR(14) on closed   |
//|    bars, time stop in bars, H4 EMA50 bias filter                  |
//|  * no entries 20:30-23:00 UTC (rollover), one position per magic  |
//|  * risk from the NorthStar governor (NorthStarRisk.mqh) or fixed %|
//|  * every closed trade appended to Common\Files\TruthEA_<magic>.csv |
//|    (t_in_utc, t_out_utc, side, entry, stop, exit, r) for          |
//|    tools/parity_check.py                                          |
//| To build a strategy: implement Signal() (bottom of this file)     |
//| from the strategy's EA_SPEC.md; the example is a Donchian break.  |
//+------------------------------------------------------------------+
#property version "1.00"
#property description "Truth Lab template EA (uncompiled source)."
#include <Trade\Trade.mqh>
#include "NorthStarRisk.mqh"

input group "=== Strategy (from EA_SPEC.md) ==="
input ENUM_TIMEFRAMES InpTF        = PERIOD_H4;  // signal timeframe
input double InpP1                 = 20;         // strategy parameter 1 (example: Donchian n)
input double InpP2                 = 3.0;        // strategy parameter 2 (example: stop in ATR)
input double InpP3                 = 0;          // strategy parameter 3
input double InpTargetR            = 0.0;        // take-profit in R (0 = none)
input double InpTrailATR           = 3.0;        // chandelier trail in ATR (0 = none)
input int    InpTimeStopBars       = 50;         // close after this many InpTF bars
input bool   InpBiasFilter         = false;      // only trade with the last closed H4 bar vs its EMA50
input double InpStopCapATR         = 5.0;        // skip signals whose stop is wider than this x ATR
input int    InpSides              = 0;          // 0 both, 1 long only, -1 short only
input group "=== Risk ==="
input bool   InpUseGovernor        = true;       // ask NorthStarGovernor for the allowed risk
input double InpRiskPct            = 1.0;        // % of equity per trade (x leg weight, decided in EA_SPEC)
input group "=== Housekeeping ==="
input ulong  InpMagic              = 990001;
input bool   InpLogTrades          = true;

CTrade g_trade;
int    g_atr = INVALID_HANDLE, g_ema = INVALID_HANDLE;
datetime g_last_bar = 0;
// state of the open position (one per magic)
double g_entry = 0, g_stop0 = 0, g_best = 0; datetime g_tin = 0; int g_side = 0; int g_bars_held = 0;

int OnInit()
{
   g_atr = iATR(_Symbol, InpTF, 14);                 // MT5 ATR is a smoothed average; the lab uses a 14-bar SMA of true range
   g_ema = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
   if(g_atr == INVALID_HANDLE || g_ema == INVALID_HANDLE) return INIT_FAILED;
   g_trade.SetExpertMagicNumber(InpMagic);
   return INIT_SUCCEEDED;
}

double AtrSma(int shift)                              // 14-bar SMA of true range on closed bars, as in the lab
{
   double s = 0;
   for(int i = shift; i < shift + 14; i++)
   {
      double h = iHigh(_Symbol, InpTF, i), l = iLow(_Symbol, InpTF, i), pc = iClose(_Symbol, InpTF, i + 1);
      s += MathMax(h, pc) - MathMin(l, pc);
   }
   return s / 14.0;
}

bool InRollover()
{
   MqlDateTime d; TimeToStruct(TimeGMT(), d);
   int m = d.hour * 60 + d.min;
   return m >= 20 * 60 + 30 && m < 23 * 60;
}

int BiasH4()
{
   double e[1]; if(CopyBuffer(g_ema, 0, 1, 1, e) != 1) return 0;
   double c = iClose(_Symbol, PERIOD_H4, 1);
   return c > e[0] ? 1 : (c < e[0] ? -1 : 0);
}

bool HavePosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk > 0 && PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC) == (long)InpMagic && PositionGetString(POSITION_SYMBOL) == _Symbol)
         return true;
   }
   return false;
}

void LogTrade(double exitpx, datetime tout)
{
   if(!InpLogTrades || g_side == 0) return;
   string f = StringFormat("TruthEA_%I64u.csv", InpMagic);
   bool exists = FileIsExist(f, FILE_COMMON);
   int h = FileOpen(f, FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ);
   if(h == INVALID_HANDLE) return;
   if(!exists || FileSize(h) == 0) FileWriteString(h, "t_in_utc,t_out_utc,side,entry,stop,exit,r\n");
   FileSeek(h, 0, SEEK_END);
   long off = (long)MathRound((double)(TimeGMT() - TimeCurrent()) / 900.0) * 900;
   double d = MathAbs(g_entry - g_stop0);
   double r = d > 0 ? g_side * (exitpx - g_entry) / d : 0;
   FileWriteString(h, StringFormat("%s,%s,%d,%.5f,%.5f,%.5f,%.4f\n", TimeToString((datetime)((long)g_tin + off), TIME_DATE | TIME_SECONDS),
                   TimeToString((datetime)((long)tout + off), TIME_DATE | TIME_SECONDS), g_side, g_entry, g_stop0, exitpx, r));
   FileClose(h);
}

void ManageOpen()
{
   if(!HavePosition()) return;
   g_bars_held++;
   ulong tk = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t > 0 && PositionSelectByTicket(t) && PositionGetInteger(POSITION_MAGIC) == (long)InpMagic && PositionGetString(POSITION_SYMBOL) == _Symbol) { tk = t; break; }
   }
   if(tk == 0) return;
   if(g_bars_held >= InpTimeStopBars) { g_trade.PositionClose(tk); return; }
   if(InpTrailATR > 0)
   {
      double a = AtrSma(1), hi = iHigh(_Symbol, InpTF, 1), lo = iLow(_Symbol, InpTF, 1);
      if(g_side > 0) g_best = MathMax(g_best, hi); else g_best = (g_best == 0 ? lo : MathMin(g_best, lo));
      double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
      double ns = g_side > 0 ? g_best - InpTrailATR * a : g_best + InpTrailATR * a;
      if((g_side > 0 && ns > sl) || (g_side < 0 && (sl == 0 || ns < sl)))     // never loosen
         g_trade.PositionModify(tk, NormalizeDouble(ns, _Digits), tp);
   }
}

void OnTick()
{
   datetime bt = iTime(_Symbol, InpTF, 0);
   if(bt == g_last_bar) return;
   g_last_bar = bt;                                   // first tick of a new bar: the previous bar has closed
   if(HavePosition()) { ManageOpen(); return; }
   if(InRollover()) return;
   int side = 0; double stop = 0;
   if(!Signal(side, stop)) return;
   if(InpSides != 0 && side != InpSides) return;
   if(InpBiasFilter && BiasH4() != side) return;
   double a = AtrSma(1);
   double px = side > 0 ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double dist = side > 0 ? px - stop : stop - px;
   double spread = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(dist <= 0 || dist < 3 * spread || (a > 0 && dist > InpStopCapATR * a)) return;
   double risk = InpRiskPct; string why = "";
   if(InpUseGovernor) { risk = NS_RequestRisk(_Symbol, side, InpRiskPct, why); if(risk <= 0) { Print("TruthEA: skipped (", why, ")"); return; } }
   double lots = NS_LotsForRisk(_Symbol, risk, px, stop);
   if(lots <= 0) { Print("TruthEA: lot size below minimum for the allowed risk"); return; }
   double tp = InpTargetR > 0 ? (side > 0 ? px + InpTargetR * dist : px - InpTargetR * dist) : 0;
   bool ok = side > 0 ? g_trade.Buy(lots, _Symbol, 0, NormalizeDouble(stop, _Digits), tp > 0 ? NormalizeDouble(tp, _Digits) : 0)
                      : g_trade.Sell(lots, _Symbol, 0, NormalizeDouble(stop, _Digits), tp > 0 ? NormalizeDouble(tp, _Digits) : 0);
   if(ok) { g_entry = g_trade.ResultPrice(); g_stop0 = stop; g_side = side; g_tin = TimeCurrent(); g_bars_held = 0; g_best = side > 0 ? g_entry : g_entry; }
}

void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &req, const MqlTradeResult &res)
{
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD || !HistoryDealSelect(trans.deal)) return;
   if(HistoryDealGetInteger(trans.deal, DEAL_MAGIC) != (long)InpMagic) return;
   long en = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(en == DEAL_ENTRY_OUT || en == DEAL_ENTRY_OUT_BY)
   {
      LogTrade(HistoryDealGetDouble(trans.deal, DEAL_PRICE), (datetime)HistoryDealGetInteger(trans.deal, DEAL_TIME));
      g_side = 0; g_best = 0;
   }
}

//+------------------------------------------------------------------+
//| Signal(): THE ONLY PART TO WRITE PER STRATEGY.                    |
//| Use closed bars only (shift >= 1). Return true with side (+1/-1)  |
//| and the stop price. Example: Donchian close breakout,            |
//| n = InpP1, stop = InpP2 x ATR from the signal close.              |
//+------------------------------------------------------------------+
bool Signal(int &side, double &stop)
{
   int n = (int)InpP1;
   double c = iClose(_Symbol, InpTF, 1), a = AtrSma(1);
   if(a <= 0) return false;
   int ih = iHighest(_Symbol, InpTF, MODE_HIGH, n, 2), il = iLowest(_Symbol, InpTF, MODE_LOW, n, 2);   // the n bars BEFORE the signal bar
   if(ih < 0 || il < 0) return false;
   double hh = iHigh(_Symbol, InpTF, ih), ll = iLow(_Symbol, InpTF, il);
   if(c > hh) { side = 1;  stop = c - InpP2 * a; return true; }
   if(c < ll) { side = -1; stop = c + InpP2 * a; return true; }
   return false;
}

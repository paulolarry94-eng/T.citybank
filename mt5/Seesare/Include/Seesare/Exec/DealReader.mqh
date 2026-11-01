//+------------------------------------------------------------------+
//|                                      Seesare/Exec/DealReader.mqh |
//| SEESARE P26 router, Phase 3: read a closed position back from    |
//| the broker's deal history and turn it into a REAL ledger event.  |
//| READ ONLY: it never sends, changes or closes anything.           |
//| UNCOMPILED SOURCE. Twin: tools/seesare_outbox.py DEAL_REASONS.   |
//|                                                                  |
//| What it takes from the terminal (HistorySelectByPosition):       |
//|   deals    every BUY/SELL deal of the position, in time order,   |
//|            as "ticket;ticket" (the ledger field, max 200 chars)  |
//|   net      sum of DEAL_PROFIT + DEAL_COMMISSION + DEAL_SWAP +    |
//|            DEAL_FEE, in account money, divided by units per USD  |
//|            (USD 1, US cents 100) -> the event's delta in USD     |
//|   prices   volume-weighted entry and exit                        |
//|   times    DEAL_TIME (server) -> UTC through the clock           |
//|   close_by the reason of the last closing deal:                  |
//|            SL -> STOP, TP -> TARGET, SO -> BROKER,               |
//|            EXPERT -> TIME (the router closes only at the time    |
//|            exit), CLIENT/MOBILE/WEB -> HUMAN, anything else      |
//|            (rollover, variation margin, split, newer reasons)    |
//|            -> BROKER, which the ledger always counts NEGATIVE.   |
//| Not covered: commissions a broker books as separate balance      |
//| operations (daily or monthly) carry no position id and are not   |
//| in the delta; RoboForex ProCent charges no commission.           |
//| A reversal deal (netting account) is refused: SEESARE positions  |
//| are opened and closed, never reversed.                           |
//+------------------------------------------------------------------+
#ifndef SEESARE_EXEC_DEALREADER_MQH
#define SEESARE_EXEC_DEALREADER_MQH

#include <Seesare\Core\Text.mqh>
#include <Seesare\Core\Clock.mqh>
#include <Seesare\Ledger\CycleLedger.mqh>

struct SSeesareDealSummary
  {
   ulong              position_id;
   bool               closed;        // the closing volume equals the opening volume
   int                count;         // deals read
   string             deals;         // "ticket;ticket", time order
   string             symbol;
   int                side;          // +1 buy, -1 sell (first opening deal)
   double             volume_in;
   double             volume_out;
   double             entry_price;   // volume-weighted
   double             exit_price;    // volume-weighted
   datetime           open_utc;      // first opening deal
   datetime           close_utc;     // last closing deal
   ENUM_SEESARE_CLOSE close_by;      // from the last closing deal's reason
   double             money;         // profit + commission + swap + fee, account money
   double             net_usd;       // money / units per USD
   string             why;
   void               Clear(void)
     {
      position_id = 0;
      closed = false;
      count = 0;
      deals = "";
      symbol = "";
      side = 0;
      volume_in = 0.0;
      volume_out = 0.0;
      entry_price = 0.0;
      exit_price = 0.0;
      open_utc = 0;
      close_utc = 0;
      close_by = SEESARE_BY_BROKER;
      money = 0.0;
      net_usd = 0.0;
      why = "";
     }
  };

class CSeesareDealReader
  {
public:
   //--- the broker's reason for a closing deal -> how the SEESARE event closed
   static ENUM_SEESARE_CLOSE CloseFromReason(const ENUM_DEAL_REASON reason)
     {
      if(reason == DEAL_REASON_SL)
         return SEESARE_BY_STOP;
      if(reason == DEAL_REASON_TP)
         return SEESARE_BY_TARGET;
      if(reason == DEAL_REASON_SO)
         return SEESARE_BY_BROKER;
      if(reason == DEAL_REASON_EXPERT)
         return SEESARE_BY_TIME;
      if(reason == DEAL_REASON_CLIENT || reason == DEAL_REASON_MOBILE || reason == DEAL_REASON_WEB)
         return SEESARE_BY_HUMAN;
      return SEESARE_BY_BROKER;
     }
   //--- account money -> USD (USD 1, US cents 100); 0 when the currency is unknown
   static double     NetUsd(const double money, const double units_per_usd)
     {
      if(units_per_usd <= 0.0)
         return 0.0;
      return money / units_per_usd;
     }
   //--- "a;b" + ticket (the ledger's deals field)
   static string     AppendTicket(const string list, const ulong ticket)
     {
      string t = IntegerToString((long)ticket);
      if(list == "")
         return t;
      return list + ";" + t;
     }
   static bool       FromPosition(const ulong position_id, const CSeesareClock &clock, const double units_per_usd,
                                  SSeesareDealSummary &out);
   static bool       ToEvent(const SSeesareDealSummary &d, const string module, const string domain, const int digits,
                             const double ratio, const double risk_usd, const double lower, const double upper,
                             SSeesareEvent &e);
  };

bool CSeesareDealReader::FromPosition(const ulong position_id, const CSeesareClock &clock, const double units_per_usd,
                                      SSeesareDealSummary &out)
  {
   out.Clear();
   out.position_id = position_id;
   if(units_per_usd <= 0.0)
     {
      out.why = "the account currency is not USD or US cents";
      return false;
     }
   if(!HistorySelectByPosition(position_id))
     {
      out.why = "HistorySelectByPosition failed for position " + IntegerToString((long)position_id);
      return false;
     }
//--- collect the position's trade deals, then order them by time and ticket
   ulong tk[];
   long  ms[];
   int n = 0;
   int total = HistoryDealsTotal();
   for(int i = 0; i < total; i++)
     {
      ulong t = HistoryDealGetTicket(i);
      if(t == 0)
         continue;
      if((ulong)HistoryDealGetInteger(t, DEAL_POSITION_ID) != position_id)
         continue;
      ENUM_DEAL_TYPE type = (ENUM_DEAL_TYPE)HistoryDealGetInteger(t, DEAL_TYPE);
      if(type != DEAL_TYPE_BUY && type != DEAL_TYPE_SELL)
         continue;
      ArrayResize(tk, n + 1, 16);
      ArrayResize(ms, n + 1, 16);
      tk[n] = t;
      ms[n] = HistoryDealGetInteger(t, DEAL_TIME_MSC);
      n++;
     }
   for(int i = 1; i < n; i++)
     {
      ulong t = tk[i];
      long m = ms[i];
      int j = i - 1;
      while(j >= 0 && (ms[j] > m || (ms[j] == m && tk[j] > t)))
        {
         tk[j + 1] = tk[j];
         ms[j + 1] = ms[j];
         j--;
        }
      tk[j + 1] = t;
      ms[j + 1] = m;
     }
   if(n == 0)
     {
      out.why = "no deals for position " + IntegerToString((long)position_id);
      return false;
     }
//--- add them up
   double in_value = 0.0;
   double out_value = 0.0;
   for(int i = 0; i < n; i++)
     {
      ulong t = tk[i];
      ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(t, DEAL_ENTRY);
      ENUM_DEAL_TYPE type = (ENUM_DEAL_TYPE)HistoryDealGetInteger(t, DEAL_TYPE);
      double vol = HistoryDealGetDouble(t, DEAL_VOLUME);
      double price = HistoryDealGetDouble(t, DEAL_PRICE);
      datetime srv = (datetime)HistoryDealGetInteger(t, DEAL_TIME);
      if(entry == DEAL_ENTRY_INOUT)
        {
         out.why = "deal " + IntegerToString((long)t) + " reverses the position (netting account): not a SEESARE position";
         return false;
        }
      out.money += HistoryDealGetDouble(t, DEAL_PROFIT) + HistoryDealGetDouble(t, DEAL_COMMISSION) +
                   HistoryDealGetDouble(t, DEAL_SWAP) + HistoryDealGetDouble(t, DEAL_FEE);
      out.deals = AppendTicket(out.deals, t);
      out.count++;
      if(entry == DEAL_ENTRY_IN)
        {
         if(out.volume_in <= 0.0)
           {
            out.symbol = HistoryDealGetString(t, DEAL_SYMBOL);
            out.side = (type == DEAL_TYPE_BUY ? 1 : -1);
            out.open_utc = clock.ServerToUtc(srv);
           }
         out.volume_in += vol;
         in_value += vol * price;
        }
      else
        {
         //--- DEAL_ENTRY_OUT or DEAL_ENTRY_OUT_BY
         out.volume_out += vol;
         out_value += vol * price;
         out.close_utc = clock.ServerToUtc(srv);
         out.close_by = CloseFromReason((ENUM_DEAL_REASON)HistoryDealGetInteger(t, DEAL_REASON));
        }
     }
   if(out.volume_in <= 0.0)
     {
      out.why = "position " + IntegerToString((long)position_id) + " has no opening deal in the history";
      return false;
     }
   out.entry_price = in_value / out.volume_in;
   if(out.volume_out > 0.0)
      out.exit_price = out_value / out.volume_out;
   out.closed = (MathAbs(out.volume_in - out.volume_out) < 1e-8);
   out.net_usd = NetUsd(out.money, units_per_usd);
   if(!CSeesareText::IsDeals(out.deals))
     {
      out.why = IntegerToString(out.count) + " deals do not fit the ledger's 200-character deals field";
      return false;
     }
   if(!out.closed)
      out.why = "position " + IntegerToString((long)position_id) + " is still open (" + CSeesareText::Fmt(out.volume_out, 2) +
                " of " + CSeesareText::Fmt(out.volume_in, 2) + " lots closed)";
   return true;
  }

//--- a closed position -> a REAL event for CSeesareCycleLedger::Record (the ledger derives the resolution itself)
bool CSeesareDealReader::ToEvent(const SSeesareDealSummary &d, const string module, const string domain, const int digits,
                                 const double ratio, const double risk_usd, const double lower, const double upper,
                                 SSeesareEvent &e)
  {
   e.Clear();
   if(!d.closed || d.count < 2 || d.side == 0)
      return false;
   e.mode       = SEESARE_REAL;
   e.module     = module;
   e.domain     = domain;
   e.symbol     = d.symbol;
   e.side       = d.side;
   e.digits     = digits;
   e.utc_open   = d.open_utc;
   e.utc_close  = d.close_utc;
   e.close_by   = d.close_by;
   e.ratio      = ratio;
   e.risk_usd   = risk_usd;
   e.volume     = d.volume_in;
   e.entry      = d.entry_price;
   e.lower      = lower;
   e.upper      = upper;
   e.exit_price = d.exit_price;
   e.delta_usd  = d.net_usd;
   e.deals      = d.deals;
   return true;
  }

#endif

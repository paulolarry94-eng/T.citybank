//+------------------------------------------------------------------+
//|                                      Seesare/Exec/PaperBook.mqh  |
//| SEESARE router, Phase 2: paper execution on live quotes for      |
//| PAPER modules (forward-test journal) and for SEESARE SHADOW      |
//| events (Shadow-Lot Engine). UNCOMPILED SOURCE.                   |
//|                                                                  |
//| Entry at the ask (buy) or bid (sell) of the entry instant; exits |
//| at the first tick that reaches the stop or the target, or at the |
//| first tick at/after the time exit (a buy leaves at the bid, a    |
//| sell at the ask). Every tick since the last check is scanned     |
//| (CopyTicksRange), so a spike between timer calls is not missed.  |
//| P&L per lot from OrderCalcProfit minus the commission per lot.   |
//| Open positions survive restarts (checksummed file); a position   |
//| whose exit passed while the terminal was off is closed at the    |
//| first tick after its exit time and flagged "late".               |
//| Journal: <root>\paper\<module>.csv, one line per closed position.|
//+------------------------------------------------------------------+
#ifndef SEESARE_EXEC_PAPERBOOK_MQH
#define SEESARE_EXEC_PAPERBOOK_MQH

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Ledger\StateStore.mqh>
#include <Seesare\Ledger\CycleLedger.mqh>

#define SEESARE_PAPER_HEADER "open_utc,close_utc,module,symbol,mode,side,volume,entry,lower,upper,exit,by,pnl_per_lot_usd,r_net,spread_points,late"
#define SEESARE_PAPER_RECENT 64

struct SSeesarePaper
  {
   string            key;             // module id @ entry time: one position per slot
   string            module_id;
   string            symbol;
   string            domain;
   bool              live;            // SEESARE SHADOW event (ledger) rather than a forward-test entry
   int               side;
   int               digits;
   double            volume;          // shadow lot (LIVE) or 1.0 (PAPER)
   double            entry;
   double            lower;           // SEESARE boundaries, as recorded in the ledger
   double            upper;
   double            stop;
   double            target;          // 0 = no live target (time exit)
   double            ratio;
   double            loss_per_lot;    // USD per lot at the stop, price move only
   double            commission;      // USD per lot, round trip
   double            spread_points;   // spread when entered
   datetime          open_utc;
   datetime          exit_utc;        // time exit
   long              last_msc;        // last tick scanned (server time, ms)
  };

struct SSeesarePaperResult
  {
   string            key;
   string            module_id;
   string            symbol;
   string            domain;
   bool              live;
   int               side;
   int               digits;
   double            volume;
   double            entry;
   double            lower;
   double            upper;
   double            exit_price;
   double            ratio;
   double            spread_points;
   datetime          open_utc;
   datetime          close_utc;
   ENUM_SEESARE_CLOSE by;
   double            pnl_per_lot;     // USD per lot after commission
   double            pnl_usd;         // pnl_per_lot x volume
   double            r_net;           // pnl_per_lot / loss_per_lot
   bool              late;            // closed from tick history after a restart
  };

void SeesareCopyPaper(const SSeesarePaper &a, SSeesarePaper &b)
  {
   b.key = a.key;
   b.module_id = a.module_id;
   b.symbol = a.symbol;
   b.domain = a.domain;
   b.live = a.live;
   b.side = a.side;
   b.digits = a.digits;
   b.volume = a.volume;
   b.entry = a.entry;
   b.lower = a.lower;
   b.upper = a.upper;
   b.stop = a.stop;
   b.target = a.target;
   b.ratio = a.ratio;
   b.loss_per_lot = a.loss_per_lot;
   b.commission = a.commission;
   b.spread_points = a.spread_points;
   b.open_utc = a.open_utc;
   b.exit_utc = a.exit_utc;
   b.last_msc = a.last_msc;
  }

void SeesareCopyPaperResult(const SSeesarePaperResult &a, SSeesarePaperResult &b)
  {
   b.key = a.key;
   b.module_id = a.module_id;
   b.symbol = a.symbol;
   b.domain = a.domain;
   b.live = a.live;
   b.side = a.side;
   b.digits = a.digits;
   b.volume = a.volume;
   b.entry = a.entry;
   b.lower = a.lower;
   b.upper = a.upper;
   b.exit_price = a.exit_price;
   b.ratio = a.ratio;
   b.spread_points = a.spread_points;
   b.open_utc = a.open_utc;
   b.close_utc = a.close_utc;
   b.by = a.by;
   b.pnl_per_lot = a.pnl_per_lot;
   b.pnl_usd = a.pnl_usd;
   b.r_net = a.r_net;
   b.late = a.late;
  }

class CSeesarePaperBook
  {
private:
   SSeesarePaper     m_pos[];
   string            m_recent[];
   string            m_dir;
   string            m_state;
   string            m_error;
   bool              Save(void);
   void              Remember(const string key);
   void              RemoveAt(const int i);
   void              Fill(const int i, const double price, const datetime utc, const ENUM_SEESARE_CLOSE by, const bool late,
                          SSeesarePaperResult &res) const;
   static string     Num(const double v) { return DoubleToString(v, 10); }

public:
                     CSeesarePaperBook(void) { m_dir = ""; m_state = ""; m_error = ""; }
   bool              Init(const string root_dir);
   int               Count(void) const { return ArraySize(m_pos); }
   bool              Seen(const string key) const;
   bool              HasLive(void) const;
   bool              Open(const SSeesarePaper &p);
   int               Step(CSeesareClock &clock, SSeesarePaperResult &closed[]);
   bool              Journal(const SSeesarePaperResult &r);
   string            LastError(void) const { return m_error; }
   static bool       PnlPerLot(const string symbol, const int side, const double entry, const double exit_price,
                               const double commission, double &pnl);
  };

bool CSeesarePaperBook::PnlPerLot(const string symbol, const int side, const double entry, const double exit_price,
                                  const double commission, double &pnl)
  {
   pnl = 0.0;
   double profit = 0.0;
   ENUM_ORDER_TYPE type = (side > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   if(!OrderCalcProfit(type, symbol, 1.0, entry, exit_price, profit))
      return false;
   pnl = profit - commission;
   return true;
  }

bool CSeesarePaperBook::Init(const string root_dir)
  {
   m_error = "";
   m_dir = root_dir + "\\paper";
   m_state = m_dir + "\\open.dat";
   ArrayResize(m_pos, 0);
   ArrayResize(m_recent, 0);
   CSeesareFiles::EnsureFolder(m_dir);
   CSeesareKV kv;
   int st = CSeesareStateStore::Load(m_state, kv);
   if(st == 0)
      return true;
   if(st < 0)
     {
      m_error = m_state + " is damaged: open paper positions were lost (journal lines up to now are intact)";
      return false;
     }
   string recent = kv.Get("recent");
   if(recent != "")
      StringSplit(recent, ',', m_recent);
   int n = (int)StringToInteger(kv.Get("n"));
   for(int i = 0; i < n; i++)
     {
      string p = "p" + IntegerToString(i) + ".";
      SSeesarePaper x;
      x.key           = kv.Get(p + "key");
      x.module_id     = kv.Get(p + "module");
      x.symbol        = kv.Get(p + "symbol");
      x.domain        = kv.Get(p + "domain");
      x.live          = (kv.Get(p + "live") == "1");
      x.side          = (int)StringToInteger(kv.Get(p + "side"));
      x.digits        = (int)StringToInteger(kv.Get(p + "digits"));
      x.volume        = StringToDouble(kv.Get(p + "volume"));
      x.entry         = StringToDouble(kv.Get(p + "entry"));
      x.lower         = StringToDouble(kv.Get(p + "lower"));
      x.upper         = StringToDouble(kv.Get(p + "upper"));
      x.stop          = StringToDouble(kv.Get(p + "stop"));
      x.target        = StringToDouble(kv.Get(p + "target"));
      x.ratio         = StringToDouble(kv.Get(p + "ratio"));
      x.loss_per_lot  = StringToDouble(kv.Get(p + "loss_per_lot"));
      x.commission    = StringToDouble(kv.Get(p + "commission"));
      x.spread_points = StringToDouble(kv.Get(p + "spread"));
      x.last_msc      = StringToInteger(kv.Get(p + "last_msc"));
      datetime t0 = 0;
      datetime t1 = 0;
      if(x.key == "" || (x.side != 1 && x.side != -1) || !CSeesareDst::IsoToTime(kv.Get(p + "open"), t0) ||
         !CSeesareDst::IsoToTime(kv.Get(p + "exit"), t1))
        {
         m_error = m_state + ": position " + IntegerToString(i) + " is malformed and was dropped";
         continue;
        }
      x.open_utc = t0;
      x.exit_utc = t1;
      int k = ArraySize(m_pos);
      ArrayResize(m_pos, k + 1);
      SeesareCopyPaper(x, m_pos[k]);
     }
   return (m_error == "");
  }

bool CSeesarePaperBook::Seen(const string key) const
  {
   for(int i = 0; i < ArraySize(m_pos); i++)
      if(m_pos[i].key == key)
         return true;
   for(int i = 0; i < ArraySize(m_recent); i++)
      if(m_recent[i] == key)
         return true;
   return false;
  }

bool CSeesarePaperBook::HasLive(void) const
  {
   for(int i = 0; i < ArraySize(m_pos); i++)
      if(m_pos[i].live)
         return true;
   return false;
  }

void CSeesarePaperBook::Remember(const string key)
  {
   int n = ArraySize(m_recent);
   if(n >= SEESARE_PAPER_RECENT)
     {
      for(int i = 1; i < n; i++)
         m_recent[i - 1] = m_recent[i];
      n--;
      ArrayResize(m_recent, n);
     }
   ArrayResize(m_recent, n + 1);
   m_recent[n] = key;
  }

void CSeesarePaperBook::RemoveAt(const int i)
  {
   int n = ArraySize(m_pos);
   for(int j = i + 1; j < n; j++)
      SeesareCopyPaper(m_pos[j], m_pos[j - 1]);
   ArrayResize(m_pos, n - 1);
  }

bool CSeesarePaperBook::Open(const SSeesarePaper &p)
  {
   if(Seen(p.key))
     {
      m_error = "slot " + p.key + " was already traded";
      return false;
     }
   int k = ArraySize(m_pos);
   ArrayResize(m_pos, k + 1);
   SeesareCopyPaper(p, m_pos[k]);
   Remember(p.key);
   if(!Save())
     {
      m_error = "could not save " + m_state;
      return false;
     }
   return true;
  }

bool CSeesarePaperBook::Save(void)
  {
   CSeesareKV kv;
   string recent = "";
   for(int i = 0; i < ArraySize(m_recent); i++)
     {
      if(i > 0)
         recent += ",";
      recent += m_recent[i];
     }
   kv.Set("recent", recent);
   kv.Set("n", IntegerToString(ArraySize(m_pos)));
   for(int i = 0; i < ArraySize(m_pos); i++)
     {
      string p = "p" + IntegerToString(i) + ".";
      kv.Set(p + "key", m_pos[i].key);
      kv.Set(p + "module", m_pos[i].module_id);
      kv.Set(p + "symbol", m_pos[i].symbol);
      kv.Set(p + "domain", m_pos[i].domain);
      kv.Set(p + "live", (m_pos[i].live ? "1" : "0"));
      kv.Set(p + "side", IntegerToString(m_pos[i].side));
      kv.Set(p + "digits", IntegerToString(m_pos[i].digits));
      kv.Set(p + "volume", Num(m_pos[i].volume));
      kv.Set(p + "entry", Num(m_pos[i].entry));
      kv.Set(p + "lower", Num(m_pos[i].lower));
      kv.Set(p + "upper", Num(m_pos[i].upper));
      kv.Set(p + "stop", Num(m_pos[i].stop));
      kv.Set(p + "target", Num(m_pos[i].target));
      kv.Set(p + "ratio", Num(m_pos[i].ratio));
      kv.Set(p + "loss_per_lot", Num(m_pos[i].loss_per_lot));
      kv.Set(p + "commission", Num(m_pos[i].commission));
      kv.Set(p + "spread", Num(m_pos[i].spread_points));
      kv.Set(p + "open", CSeesareDst::IsoUtc(m_pos[i].open_utc));
      kv.Set(p + "exit", CSeesareDst::IsoUtc(m_pos[i].exit_utc));
      kv.Set(p + "last_msc", IntegerToString(m_pos[i].last_msc));
     }
   return CSeesareStateStore::Save(m_state, kv);
  }

void CSeesarePaperBook::Fill(const int i, const double price, const datetime utc, const ENUM_SEESARE_CLOSE by, const bool late,
                             SSeesarePaperResult &res) const
  {
   res.key           = m_pos[i].key;
   res.module_id     = m_pos[i].module_id;
   res.symbol        = m_pos[i].symbol;
   res.domain        = m_pos[i].domain;
   res.live          = m_pos[i].live;
   res.side          = m_pos[i].side;
   res.digits        = m_pos[i].digits;
   res.volume        = m_pos[i].volume;
   res.entry         = m_pos[i].entry;
   res.lower         = m_pos[i].lower;
   res.upper         = m_pos[i].upper;
   res.exit_price    = price;
   res.ratio         = m_pos[i].ratio;
   res.spread_points = m_pos[i].spread_points;
   res.open_utc      = m_pos[i].open_utc;
   res.close_utc     = (utc < m_pos[i].open_utc ? m_pos[i].open_utc : utc);
   res.by            = by;
   res.late          = late;
   double pnl = 0.0;
   if(!PnlPerLot(m_pos[i].symbol, m_pos[i].side, m_pos[i].entry, price, m_pos[i].commission, pnl))
      pnl = 0.0;
   res.pnl_per_lot = pnl;
   res.pnl_usd     = pnl * m_pos[i].volume;
   res.r_net       = (m_pos[i].loss_per_lot > 0.0 ? pnl / m_pos[i].loss_per_lot : 0.0);
  }

//--- scans every tick since the last call; returns the positions closed now (they leave the book)
int CSeesarePaperBook::Step(CSeesareClock &clock, SSeesarePaperResult &closed[])
  {
   ArrayResize(closed, 0);
   int nclosed = 0;
   bool changed = false;
   datetime now = clock.UtcNow();
   ulong to_msc = (ulong)clock.ServerNow() * 1000 + 999;
   int i = 0;
   while(i < ArraySize(m_pos))
     {
      bool done = false;
      SSeesarePaperResult res;
      MqlTick ticks[];
      int n = CopyTicksRange(m_pos[i].symbol, ticks, COPY_TICKS_INFO, (ulong)(m_pos[i].last_msc + 1), to_msc);
      for(int j = 0; j < n && !done; j++)
        {
         m_pos[i].last_msc = ticks[j].time_msc;
         double bid = ticks[j].bid;
         double ask = ticks[j].ask;
         if(bid <= 0.0 || ask <= 0.0)
            continue;
         datetime tu = clock.ServerToUtc(ticks[j].time);
         bool late = ((long)now - (long)tu > 60);
         double px_out = (m_pos[i].side > 0 ? bid : ask);
         if(tu >= m_pos[i].exit_utc)
           {
            Fill(i, px_out, tu, SEESARE_BY_TIME, late, res);
            done = true;
           }
         else if((m_pos[i].side > 0 && bid <= m_pos[i].stop) || (m_pos[i].side < 0 && ask >= m_pos[i].stop))
           {
            Fill(i, px_out, tu, SEESARE_BY_STOP, late, res);
            done = true;
           }
         else if(m_pos[i].target > 0.0 && ((m_pos[i].side > 0 && bid >= m_pos[i].target) || (m_pos[i].side < 0 && ask <= m_pos[i].target)))
           {
            Fill(i, px_out, tu, SEESARE_BY_TARGET, late, res);
            done = true;
           }
        }
      if(!done && now >= m_pos[i].exit_utc)
        {
         MqlTick t;
         if(SymbolInfoTick(m_pos[i].symbol, t) && t.bid > 0.0 && t.ask > 0.0)
           {
            bool late = ((long)now - (long)m_pos[i].exit_utc > 60);
            Fill(i, (m_pos[i].side > 0 ? t.bid : t.ask), now, SEESARE_BY_TIME, late, res);
            done = true;
           }
        }
      if(done)
        {
         ArrayResize(closed, nclosed + 1);
         SeesareCopyPaperResult(res, closed[nclosed]);
         nclosed++;
         RemoveAt(i);
         changed = true;
        }
      else
         i++;
     }
   if(changed)
      Save();
   return nclosed;
  }

bool CSeesarePaperBook::Journal(const SSeesarePaperResult &r)
  {
   string path = m_dir + "\\" + r.module_id + ".csv";
   if(!CSeesareFiles::Exists(path))
      CSeesareFiles::AppendLine(path, SEESARE_PAPER_HEADER);
   string mode = "PAPER";
   if(r.live)
      mode = "SHADOW";
   string side = "SELL";
   if(r.side > 0)
      side = "BUY";
   string late = "0";
   if(r.late)
      late = "1";
   string line = CSeesareDst::IsoUtc(r.open_utc);
   line += "," + CSeesareDst::IsoUtc(r.close_utc);
   line += "," + r.module_id;
   line += "," + r.symbol;
   line += "," + mode;
   line += "," + side;
   line += "," + DoubleToString(r.volume, 4);
   line += "," + DoubleToString(r.entry, r.digits);
   line += "," + DoubleToString(r.lower, r.digits);
   line += "," + DoubleToString(r.upper, r.digits);
   line += "," + DoubleToString(r.exit_price, r.digits);
   line += "," + CSeesareLadder::CloseName(r.by);
   line += "," + DoubleToString(r.pnl_per_lot, 2);
   line += "," + DoubleToString(r.r_net, 4);
   line += "," + DoubleToString(r.spread_points, 1);
   line += "," + late;
   return CSeesareFiles::AppendLine(path, line);
  }

#endif

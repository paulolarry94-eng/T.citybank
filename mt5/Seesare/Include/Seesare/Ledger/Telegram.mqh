//+------------------------------------------------------------------+
//|                                     Seesare/Ledger/Telegram.mqh  |
//| SEESARE P26 router, Phase 3: plain-text messages for the relay   |
//| service (Telegram). UNCOMPILED SOURCE.                           |
//| Twin: tools/seesare_outbox.py (fmt_*, message_body).             |
//|                                                                  |
//| The formatter only rearranges fields of a ledger, anchor or      |
//| lifecycle line: no number is printed again, so MQL5 and Python  |
//| produce the same bytes. Every message ends with                  |
//|   Record: <the full line>                                        |
//| so anyone can recompute the hash chain from the public posts     |
//| (python3 tools/seesare_verify.py). The chain is keyless SHA-256: |
//| it proves the posts match each other and the ledger file, not    |
//| who wrote them; the deal tickets on REAL lines are matched       |
//| against the broker statement.                                    |
//|                                                                  |
//| A REAL event reads, for example:                                 |
//|   SEESARE P26 | P26-001 | Cycle 3/36 | Step 7/10 | REAL          |
//|   TOKYO_FIX USDJPY BUY                                           |
//|   Open ... | Close ... | by TIME                                 |
//|   Result NEGATIVE | -3.0000 USD | level L0 -> L1 | drawdown      |
//|     before 0.0000 USD                                            |
//|   Entry ... | Lower ... | Upper ... | Exit ...                   |
//|   Weight 0.57 | planned ... USD | risk ... USD | volume ...      |
//|   Deals 50001000, 50001001                                       |
//|   Chain k=.. | hash ..                                           |
//|   Prev ..                                                        |
//|   Record: v=1|life=...|hash=...                                  |
//| A malformed record gives "" and the outbox refuses to write it.  |
//+------------------------------------------------------------------+
#ifndef SEESARE_LEDGER_TELEGRAM_MQH
#define SEESARE_LEDGER_TELEGRAM_MQH

#include <Seesare\Ledger\StateStore.mqh>

#define SEESARE_TG_HEAD   "SEESARE P26"
#define SEESARE_TG_MAX    4096          // Telegram's limit for one message, in characters

class CSeesareTelegram
  {
private:
   //--- content and hash of a "...|hash=<64 hex>" line; a line without that suffix is all content (twin: _kv)
   static bool       Load(const string line, CSeesareKV &kv, string &hash, const string need)
     {
      hash = "";
      string content = line;
      int len = StringLen(line);
      if(len >= 71 && StringSubstr(line, len - 70, 6) == "|hash=")
        {
         content = StringSubstr(line, 0, len - 70);
         hash = StringSubstr(line, len - 64);
        }
      if(!kv.ParsePipes(content))
         return false;
      string keys[];
      int n = StringSplit(need, ',', keys);
      for(int i = 0; i < n; i++)
         if(!kv.Has(keys[i]))
            return false;
      return true;
     }

public:
   //--- "+" in front of a positive decimal string; zero and negatives unchanged (text only, twin: signed)
   static string     Signed(const string v)
     {
      int n = StringLen(v);
      if(n == 0 || StringGetCharacter(v, 0) == '-')
         return v;
      for(int i = 0; i < n; i++)
        {
         ushort c = StringGetCharacter(v, i);
         if(c >= '1' && c <= '9')
            return "+" + v;
        }
      return v;
     }

   static string     Genesis(const string line)
     {
      CSeesareKV kv;
      string h = "";
      string need = "life,created,baseline,events,cycle_size,envelope_pct,sizing,levels,band,room_mult,max_weight";
      need += ",time_policy";
      if(!Load(line, kv, h, need) || h == "")
         return "";
      string t = SEESARE_TG_HEAD;
      t += " | " + kv.Get("life") + " | lifecycle opened " + kv.Get("created");
      t += "\nBaseline " + kv.Get("baseline") + " USD | " + kv.Get("events") + " events in cycles of " + kv.Get("cycle_size") +
           " | envelope " + kv.Get("envelope_pct") + "%";
      t += "\nSizing " + kv.Get("sizing") + ": " + kv.Get("levels") + " levels of " + kv.Get("band") +
           " USD drawdown | risk = " + kv.Get("room_mult") + " x weight x room left | weight <= " + kv.Get("max_weight");
      t += "\nTime exits " + kv.Get("time_policy");
      t += "\nGenesis hash " + h;
      return t;
     }

   static string     Event(const string line)
     {
      CSeesareKV kv;
      string h = "";
      string need = "life,k,mode,cycle,step,module,symbol,side,open,close,by,res,dd,lvl_before,lvl_after,weight,plan,risk";
      need += ",vol,entry,lower,upper,exit,delta,deals,prev";
      if(!Load(line, kv, h, need) || h == "")
         return "";
      bool real = (kv.Get("mode") == "REAL");
      string where = "Cycle " + kv.Get("cycle") + "/36 | ";
      if(real)
         where += "Step " + kv.Get("step") + "/10 | REAL";
      else
         where += "SHADOW (paper, not counted)";
      string deals = "none (paper)";
      if(real)
        {
         deals = kv.Get("deals");
         StringReplace(deals, ";", ", ");
        }
      string t = SEESARE_TG_HEAD;
      t += " | " + kv.Get("life") + " | " + where;
      t += "\n" + kv.Get("module") + " " + kv.Get("symbol") + " " + kv.Get("side");
      t += "\nOpen " + kv.Get("open") + " | Close " + kv.Get("close") + " | by " + kv.Get("by");
      t += "\nResult " + kv.Get("res") + " | " + Signed(kv.Get("delta")) + " USD | level L" + kv.Get("lvl_before") + " -> L" +
           kv.Get("lvl_after") + " | drawdown before " + kv.Get("dd") + " USD";
      t += "\nEntry " + kv.Get("entry") + " | Lower " + kv.Get("lower") + " | Upper " + kv.Get("upper") + " | Exit " + kv.Get("exit");
      t += "\nWeight " + kv.Get("weight") + " | planned " + kv.Get("plan") + " USD | risk " + kv.Get("risk") + " USD | volume " +
           kv.Get("vol");
      t += "\nDeals " + deals;
      t += "\nChain k=" + kv.Get("k") + " | hash " + h;
      t += "\nPrev " + kv.Get("prev");
      return t;
     }

   static string     Audit(const string line)
     {
      CSeesareKV kv;
      string h = "";
      string need = "life,cycle,events,pos,neg,man,shadow,pos_rate,net,net_pct,max_dd,max_dd_pct,life_net,life_dd,lvl_start";
      need += ",lvl_end,root,head";
      if(!Load(line, kv, h, need) || h == "")
         return "";
      string t = SEESARE_TG_HEAD;
      t += " | " + kv.Get("life") + " | Cycle " + kv.Get("cycle") + "/36 closed | events " + kv.Get("events");
      t += "\nPositive " + kv.Get("pos") + " | negative " + kv.Get("neg") + " | manual " + kv.Get("man") + " | shadow " +
           kv.Get("shadow") + " | positive rate " + kv.Get("pos_rate");
      t += "\nCycle net " + Signed(kv.Get("net")) + " USD (" + Signed(kv.Get("net_pct")) + "%) | cycle max drawdown " +
           kv.Get("max_dd") + " USD (" + kv.Get("max_dd_pct") + "%)";
      t += "\nLifecycle net " + Signed(kv.Get("life_net")) + " USD | lifecycle max drawdown " + kv.Get("life_dd") + " USD";
      t += "\nLevel L" + kv.Get("lvl_start") + " -> L" + kv.Get("lvl_end");
      t += "\nBlock root " + kv.Get("root");
      t += "\nChain head " + kv.Get("head");
      t += "\nAnchor " + h;
      return t;
     }

   static string     Lifecycle(const string line)
     {
      CSeesareKV kv;
      string h = "";
      if(!Load(line, kv, h, "life,events,cycles,pos,neg,man,shadow,net,net_pct,max_dd,max_dd_pct,violations,head"))
         return "";
      string t = SEESARE_TG_HEAD;
      t += " | " + kv.Get("life") + " | lifecycle complete: " + kv.Get("events") + " events in " + kv.Get("cycles") + " cycles";
      t += "\nPositive " + kv.Get("pos") + " | negative " + kv.Get("neg") + " | manual " + kv.Get("man") + " | shadow " +
           kv.Get("shadow");
      t += "\nNet " + Signed(kv.Get("net")) + " USD (" + Signed(kv.Get("net_pct")) + "%) | max drawdown " + kv.Get("max_dd") +
           " USD (" + kv.Get("max_dd_pct") + "%) | envelope violations " + kv.Get("violations");
      t += "\nFinal head " + kv.Get("head");
      return t;
     }

   //--- what the outbox writes after its "---" line: the formatted text, then the record ("" if the record is malformed)
   static string     Body(const string kind, const string record)
     {
      string t = "";
      if(kind == "GENESIS")
         t = Genesis(record);
      else if(kind == "EVENT")
         t = Event(record);
      else if(kind == "AUDIT")
         t = Audit(record);
      else if(kind == "LIFECYCLE")
         t = Lifecycle(record);
      if(t == "")
         return "";
      t += "\nRecord: " + record;
      return t;
     }
  };

#endif

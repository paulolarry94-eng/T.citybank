//+------------------------------------------------------------------+
//|                                       Seesare/Ledger/Outbox.mqh  |
//| SEESARE P26 router, Phase 1: numbered outbox files for the relay |
//| service (dual-service design: the EA never calls the network).   |
//| Phase 3: the body is the plain-text Telegram message             |
//| (Telegram.mqh) followed by "Record: <line>". UNCOMPILED SOURCE.  |
//| Twin: tools/seesare_outbox.py outbox_message().                  |
//|                                                                  |
//| <lifecycle folder>\outbox\0000000001.msg, 0000000002.msg, ...    |
//| Each message is written to NNNNNNNNNN.tmp and then renamed to    |
//| .msg, so the relay never sees half a file. Numbers are never     |
//| reused: a number that exists in outbox\ or outbox\sent\ is       |
//| skipped. The relay (later phase) sends the lowest .msg, then     |
//| moves it to outbox\sent\ and never deletes it.                   |
//|                                                                  |
//| Message:                                                         |
//|   SEESARE-OUTBOX/2                                               |
//|   seq=0000000001                                                 |
//|   kind=GENESIS | EVENT | AUDIT | LIFECYCLE                       |
//|   life=<lifecycle id>                                            |
//|   ref=<chain index k | cycle number | real events>               |
//|   utc=<event time, ISO-8601>                                     |
//|   ---                                                            |
//|   <body: Telegram text, several lines, no empty line>            |
//|   Record: <the ledger, anchor or lifecycle line>                 |
//|   sum=<SHA-256 of all lines above, each followed by "\n">        |
//| The relay checks sum=, then posts the lines between "---" and    |
//| "sum=" as one plain-text message (at most 4096 characters; an    |
//| event message is about 1,300).                                   |
//| Files are written with CRLF line ends; the checksum is over LF.  |
//| Delivery is at least once (a crash between writing a message and |
//| saving state.dat queues it again); the relay drops duplicates by |
//| (life, kind, ref).                                               |
//+------------------------------------------------------------------+
#ifndef SEESARE_LEDGER_OUTBOX_MQH
#define SEESARE_LEDGER_OUTBOX_MQH

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Ledger\Sha256.mqh>
#include <Seesare\Ledger\StateStore.mqh>
#include <Seesare\Ledger\Telegram.mqh>

#define SEESARE_OUTBOX_FORMAT "SEESARE-OUTBOX/2"

class CSeesareOutbox
  {
private:
   string            m_dir;
   long              m_seq;
   string            m_error;

public:
                     CSeesareOutbox(void) { m_dir = ""; m_seq = 0; m_error = ""; }
   bool              Init(const string dir, const long last_seq);
   bool              Push(const string kind, const string life, const long ref, const datetime utc, const string record);
   long              LastSeq(void) const { return m_seq; }
   string            Dir(void) const { return m_dir; }
   string            LastError(void) const { return m_error; }
   static string     Name(const long seq) { return IntegerToString(seq, 10, '0'); }
  };

bool CSeesareOutbox::Init(const string dir, const long last_seq)
  {
   m_dir = dir;
   m_seq = (last_seq > 0 ? last_seq : 0);
   m_error = "";
   CSeesareFiles::EnsureFolder(dir + "\\sent");
   return true;
  }

bool CSeesareOutbox::Push(const string kind, const string life, const long ref, const datetime utc, const string record)
  {
   if(m_dir == "")
     {
      m_error = "outbox not initialised";
      return false;
     }
   string body = CSeesareTelegram::Body(kind, record);
   if(body == "")
     {
      m_error = "cannot format the " + kind + " record for the relay";
      return false;
     }
   for(int attempt = 0; attempt < 1000; attempt++)
     {
      long seq = m_seq + 1;
      string name = Name(seq);
      string msg  = m_dir + "\\" + name + ".msg";
      string sent = m_dir + "\\sent\\" + name + ".msg";
      if(CSeesareFiles::Exists(msg) || CSeesareFiles::Exists(sent))
        {
         m_seq = seq;
         continue;
        }
      string text = SEESARE_OUTBOX_FORMAT;
      text += "\n";
      text += "seq=" + name + "\n";
      text += "kind=" + kind + "\n";
      text += "life=" + life + "\n";
      text += "ref=" + IntegerToString(ref) + "\n";
      text += "utc=" + CSeesareDst::IsoUtc(utc) + "\n";
      text += "---\n";
      text += body + "\n";
      string sum = CSeesareSha256::Hex(text);
      if(sum == "")
        {
         m_error = "SHA-256 unavailable";
         return false;
        }
      text += "sum=" + sum + "\n";
      string disk = text;
      StringReplace(disk, "\n", "\r\n");
      string tmp = m_dir + "\\" + name + ".tmp";
      if(!CSeesareFiles::WriteAll(tmp, disk))
        {
         m_error = "cannot write " + tmp;
         return false;
        }
      if(!FileMove(tmp, FILE_COMMON, msg, FILE_COMMON))
        {
         FileDelete(tmp, FILE_COMMON);
         if(CSeesareFiles::Exists(msg))
           {
            m_seq = seq;
            continue;
           }
         m_error = "cannot publish " + msg;
         return false;
        }
      m_seq = seq;
      m_error = "";
      return true;
     }
   m_error = "no free outbox number after 1000 tries";
   return false;
  }

#endif

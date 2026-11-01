//+------------------------------------------------------------------+
//|                                   Seesare/Ledger/StateStore.mqh  |
//| SEESARE P26 router, Phase 1: key/value parsing, VPS disk I/O in  |
//| Common\Files, and the checksummed state snapshot.                |
//| UNCOMPILED SOURCE.                                               |
//|                                                                  |
//| Files are text (one record per line, CRLF), opened, written,     |
//| flushed and closed on every call: no handle stays open, so a     |
//| crash or VPS restart loses at most the line being written.       |
//| Snapshots are written to <file>.tmp and moved over the old file  |
//| (FileMove with FILE_REWRITE); the previous good copy is kept as  |
//| <file>.bak.                                                      |
//+------------------------------------------------------------------+
#ifndef SEESARE_LEDGER_STATESTORE_MQH
#define SEESARE_LEDGER_STATESTORE_MQH

#include <Seesare\Ledger\Sha256.mqh>

#define SEESARE_STATE_HEADER "SEESARE-STATE/1"

//+------------------------------------------------------------------+
//| Ordered key/value list; parses "k=v|k=v|flag" lines strictly     |
//+------------------------------------------------------------------+
class CSeesareKV
  {
private:
   string            m_k[];
   string            m_v[];

public:
   void              Clear(void);
   int               Count(void) const { return ArraySize(m_k); }
   int               IndexOf(const string key) const;
   bool              Has(const string key) const { return (IndexOf(key) >= 0); }
   bool              Add(const string key, const string val);
   void              Set(const string key, const string val);
   string            Get(const string key) const;
   string            Key(const int i) const;
   string            Val(const int i) const;
   bool              ParsePipes(const string content);
   bool              KeysAre(const string csv) const;
  };

void CSeesareKV::Clear(void)
  {
   ArrayResize(m_k, 0);
   ArrayResize(m_v, 0);
  }

int CSeesareKV::IndexOf(const string key) const
  {
   for(int i = 0; i < ArraySize(m_k); i++)
      if(m_k[i] == key)
         return i;
   return -1;
  }

bool CSeesareKV::Add(const string key, const string val)
  {
   if(IndexOf(key) >= 0)
      return false;
   int n = ArraySize(m_k);
   ArrayResize(m_k, n + 1, 32);
   ArrayResize(m_v, n + 1, 32);
   m_k[n] = key;
   m_v[n] = val;
   return true;
  }

void CSeesareKV::Set(const string key, const string val)
  {
   int i = IndexOf(key);
   if(i >= 0)
      m_v[i] = val;
   else
      Add(key, val);
  }

string CSeesareKV::Get(const string key) const
  {
   int i = IndexOf(key);
   if(i < 0)
      return "";
   return m_v[i];
  }

string CSeesareKV::Key(const int i) const
  {
   if(i < 0 || i >= ArraySize(m_k))
      return "";
   return m_k[i];
  }

string CSeesareKV::Val(const int i) const
  {
   if(i < 0 || i >= ArraySize(m_v))
      return "";
   return m_v[i];
  }

//--- "k=v|k=v|flag": no empty part, no empty key, no repeated key (twin: parse)
bool CSeesareKV::ParsePipes(const string content)
  {
   Clear();
   int len = StringLen(content);
   if(len == 0 || StringFind(content, "||") >= 0 || StringGetCharacter(content, 0) == '|' ||
      StringGetCharacter(content, len - 1) == '|')
      return false;
   string parts[];
   int n = StringSplit(content, '|', parts);
   if(n <= 0)
      return false;
   for(int i = 0; i < n; i++)
     {
      int plen = StringLen(parts[i]);
      if(plen == 0)
        {
         Clear();
         return false;
        }
      int e = StringFind(parts[i], "=");
      string key = (e < 0 ? parts[i] : StringSubstr(parts[i], 0, e));
      string val = ((e < 0 || e + 1 >= plen) ? "" : StringSubstr(parts[i], e + 1));
      if(StringLen(key) == 0 || !Add(key, val))
        {
         Clear();
         return false;
        }
     }
   return true;
  }

//--- the keys, in order, are exactly the comma-separated list
bool CSeesareKV::KeysAre(const string csv) const
  {
   string keys[];
   int n = StringSplit(csv, ',', keys);
   if(n != ArraySize(m_k))
      return false;
   for(int i = 0; i < n; i++)
      if(m_k[i] != keys[i])
         return false;
   return true;
  }

//+------------------------------------------------------------------+
//| Text files in the terminals' Common\Files folder                 |
//+------------------------------------------------------------------+
class CSeesareFiles
  {
public:
   static string     StripEol(const string s)
     {
      int n = StringLen(s);
      while(n > 0)
        {
         ushort c = StringGetCharacter(s, n - 1);
         if(c != '\r' && c != '\n')
            break;
         n--;
        }
      if(n == StringLen(s))
         return s;
      if(n == 0)
         return "";
      return StringSubstr(s, 0, n);
     }
   static bool       Exists(const string path)
     {
      return FileIsExist(path, FILE_COMMON);
     }
   //--- creates each folder level (FolderCreate leaves existing folders alone)
   static void       EnsureFolder(const string path)
     {
      string parts[];
      int n = StringSplit(path, '\\', parts);
      string cur = "";
      for(int i = 0; i < n; i++)
        {
         if(i == 0)
            cur = parts[i];
         else
            cur = cur + "\\" + parts[i];
         FolderCreate(cur, FILE_COMMON);
        }
     }
   //--- non-empty lines without their line ends; -1 if the file cannot be opened
   static int        ReadLines(const string path, string &lines[])
     {
      ArrayResize(lines, 0);
      int h = FileOpen(path, FILE_READ | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE, '\t', CP_UTF8);
      if(h == INVALID_HANDLE)
         return -1;
      int n = 0;
      for(int guard = 0; guard < 2000000 && !FileIsEnding(h); guard++)
        {
         string s = StripEol(FileReadString(h));
         if(n == 0 && StringLen(s) > 0 && StringGetCharacter(s, 0) == 0xFEFF)
            s = StringSubstr(s, 1);
         if(StringLen(s) == 0)
            continue;
         ArrayResize(lines, n + 1, 1024);
         lines[n] = s;
         n++;
        }
      FileClose(h);
      return n;
     }
   static string     LastLine(const string path)
     {
      string lines[];
      int n = ReadLines(path, lines);
      if(n <= 0)
         return "";
      return lines[n - 1];
     }
   //--- appends one line + CRLF and flushes
   static bool       AppendLine(const string path, const string line)
     {
      int h = FileOpen(path, FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ, '\t', CP_UTF8);
      if(h == INVALID_HANDLE)
         return false;
      bool ok = FileSeek(h, 0, SEEK_END);
      if(ok)
         ok = (FileWriteString(h, line + "\r\n") > 0);
      FileFlush(h);
      FileClose(h);
      return ok;
     }
   //--- replaces the whole file
   static bool       WriteAll(const string path, const string text)
     {
      int h = FileOpen(path, FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON, '\t', CP_UTF8);
      if(h == INVALID_HANDLE)
         return false;
      bool ok = true;
      if(StringLen(text) > 0)
         ok = (FileWriteString(h, text) > 0);
      FileFlush(h);
      FileClose(h);
      return ok;
     }
   //--- writes path.tmp, then moves it over path
   static bool       WriteAtomic(const string path, const string text)
     {
      string tmp = path + ".tmp";
      if(!WriteAll(tmp, text))
         return false;
      if(!FileMove(tmp, FILE_COMMON, path, FILE_COMMON | FILE_REWRITE))
        {
         FileDelete(tmp, FILE_COMMON);
         return false;
        }
      return true;
     }
  };

//+------------------------------------------------------------------+
//| Checksummed snapshot:                                            |
//|   SEESARE-STATE/1                                                |
//|   key=value ...                                                  |
//|   sha256=<SHA-256 of the lines above, each followed by "\n">     |
//+------------------------------------------------------------------+
class CSeesareStateStore
  {
public:
   static bool       LoadFile(const string path, CSeesareKV &kv)
     {
      kv.Clear();
      if(!CSeesareFiles::Exists(path))
         return false;
      string lines[];
      int n = CSeesareFiles::ReadLines(path, lines);
      if(n < 2 || lines[0] != SEESARE_STATE_HEADER || StringSubstr(lines[n - 1], 0, 7) != "sha256=")
         return false;
      string body = SEESARE_STATE_HEADER;
      body += "\n";
      for(int i = 1; i < n - 1; i++)
        {
         int p = StringFind(lines[i], "=");
         int len = StringLen(lines[i]);
         if(p <= 0)
           {
            kv.Clear();
            return false;
           }
         string val = (p + 1 < len ? StringSubstr(lines[i], p + 1) : "");
         if(!kv.Add(StringSubstr(lines[i], 0, p), val))
           {
            kv.Clear();
            return false;
           }
         body += lines[i] + "\n";
        }
      if(CSeesareSha256::Hex(body) != StringSubstr(lines[n - 1], 7))
        {
         kv.Clear();
         return false;
        }
      return true;
     }
   //--- 1 = loaded, 2 = the backup was used, 0 = neither file exists, -1 = damaged
   static int        Load(const string path, CSeesareKV &kv)
     {
      if(LoadFile(path, kv))
         return 1;
      if(LoadFile(path + ".bak", kv))
         return 2;
      if(!CSeesareFiles::Exists(path) && !CSeesareFiles::Exists(path + ".bak"))
         return 0;
      return -1;
     }
   static bool       Save(const string path, CSeesareKV &kv)
     {
      string body = SEESARE_STATE_HEADER;
      body += "\n";
      string text = SEESARE_STATE_HEADER;
      text += "\r\n";
      for(int i = 0; i < kv.Count(); i++)
        {
         string k = kv.Key(i);
         string v = kv.Val(i);
         if(StringLen(k) == 0 || StringFind(k, "=") >= 0 || StringFind(k, "\n") >= 0 || StringFind(k, "\r") >= 0 ||
            StringFind(v, "\n") >= 0 || StringFind(v, "\r") >= 0)
            return false;
         body += k + "=" + v + "\n";
         text += k + "=" + v + "\r\n";
        }
      string sum = CSeesareSha256::Hex(body);
      if(sum == "")
         return false;
      text += "sha256=" + sum + "\r\n";
      CSeesareKV old;
      if(LoadFile(path, old))
         FileCopy(path, FILE_COMMON, path + ".bak", FILE_COMMON | FILE_REWRITE);
      return CSeesareFiles::WriteAtomic(path, text);
     }
  };

#endif

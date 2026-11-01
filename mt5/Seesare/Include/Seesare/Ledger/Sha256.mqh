//+------------------------------------------------------------------+
//|                                       Seesare/Ledger/Sha256.mqh  |
//| SEESARE P26 router, Phase 1: keyless SHA-256 (public chain).     |
//| UNCOMPILED SOURCE. Twin: hashlib.sha256 in tools/seesare_verify. |
//+------------------------------------------------------------------+
#ifndef SEESARE_LEDGER_SHA256_MQH
#define SEESARE_LEDGER_SHA256_MQH

#define SEESARE_SHA256_EMPTY "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

class CSeesareSha256
  {
public:
   //--- lowercase hex SHA-256 of the UTF-8 bytes of text, without the terminating zero that
   //--- StringToCharArray appends; "" if the terminal refused (callers treat "" as fatal)
   static string     Hex(const string text)
     {
      uchar data[];
      int n = StringToCharArray(text, data, 0, WHOLE_ARRAY, CP_UTF8);
      if(n > 0 && data[n - 1] == 0)
         n--;
      if(n <= 0)
         return SEESARE_SHA256_EMPTY;
      if(ArrayResize(data, n) != n)
         return "";
      uchar key[];
      uchar digest[];
      if(CryptEncode(CRYPT_HASH_SHA256, data, key, digest) != 32)
         return "";
      string hex = "";
      for(int i = 0; i < 32; i++)
         hex += StringFormat("%02x", (int)digest[i]);
      return hex;
     }
  };

#endif

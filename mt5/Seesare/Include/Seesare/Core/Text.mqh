//+------------------------------------------------------------------+
//|                                           Seesare/Core/Text.mqh  |
//| SEESARE P26 router, Phase 1: number formatting and validators.   |
//| UNCOMPILED SOURCE. Python twin: tools/seesare_verify.py          |
//| (num, floor_dp, is_decimal, decimals, is_* functions).           |
//+------------------------------------------------------------------+
#ifndef SEESARE_CORE_TEXT_MQH
#define SEESARE_CORE_TEXT_MQH

class CSeesareText
  {
public:
   static bool       IsDigit(const ushort c)
     {
      return (c >= '0' && c <= '9');
     }
   static bool       IsHexLower(const ushort c)
     {
      return ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'));
     }
   //--- 10^digits by repeated multiplication: exact for the small powers used here
   static double     Pow10(const int digits)
     {
      double m = 1.0;
      for(int i = 0; i < digits; i++)
         m *= 10.0;
      return m;
     }
   //--- fixed decimals; a value that would print as -0 prints as 0 (twin: num)
   static string     Fmt(const double x, const int digits)
     {
      double v = x;
      if(MathAbs(v) < 0.5 / Pow10(digits))
         v = 0.0;
      return DoubleToString(v, digits);
     }
   //--- round a non-negative value DOWN to `digits` decimals (twin: floor_dp).
   //--- Each step is one IEEE operation, so MQL5 and Python get the same bits, and the result k/10^d
   //--- prints identically in both: no rounding tie is left to DoubleToString.
   static double     FloorDp(const double x, const int digits)
     {
      double m = Pow10(digits);
      return MathFloor(x * m + 1e-6) / m;
     }
   //--- "0" or a digit string without a leading zero, at most 18 digits
   static bool       IsUInt(const string s)
     {
      int n = StringLen(s);
      if(n < 1 || n > 18)
         return false;
      for(int i = 0; i < n; i++)
         if(!IsDigit(StringGetCharacter(s, i)))
            return false;
      return (n == 1 || StringGetCharacter(s, 0) != '0');
     }
   //--- canonical decimal with exactly `decimals` places: -?(0|[1-9][0-9]*)(\.[0-9]{decimals})?, no negative zero
   static bool       IsDecimal(const string s, const int decimals)
     {
      int n = StringLen(s);
      if(n == 0 || decimals < 0)
         return false;
      int i = 0;
      bool neg = (StringGetCharacter(s, 0) == '-');
      if(neg)
         i = 1;
      int start = i;
      while(i < n && IsDigit(StringGetCharacter(s, i)))
         i++;
      int int_len = i - start;
      if(int_len == 0)
         return false;
      if(int_len > 1 && StringGetCharacter(s, start) == '0')
         return false;
      if(decimals > 0)
        {
         if(i >= n || StringGetCharacter(s, i) != '.')
            return false;
         i++;
         int fstart = i;
         while(i < n && IsDigit(StringGetCharacter(s, i)))
            i++;
         if(i - fstart != decimals)
            return false;
        }
      if(i != n)
         return false;
      if(neg)
        {
         for(int j = 1; j < n; j++)
           {
            ushort c = StringGetCharacter(s, j);
            if(c != '0' && c != '.')
               return true;
           }
         return false;
        }
      return true;
     }
   //--- number of decimals of a canonical decimal string, -1 if it is not one (twin: decimals)
   static int        Decimals(const string s)
     {
      int dot = StringFind(s, ".");
      if(dot < 0)
         return (IsDecimal(s, 0) ? 0 : -1);
      int d = StringLen(s) - dot - 1;
      return ((d >= 1 && IsDecimal(s, d)) ? d : -1);
     }
   //--- printable ASCII without the separators | = ; ,  (module ids, symbols)
   static bool       IsToken(const string s, const int max_len)
     {
      int n = StringLen(s);
      if(n < 1 || n > max_len)
         return false;
      for(int i = 0; i < n; i++)
        {
         ushort c = StringGetCharacter(s, i);
         if(c < 33 || c > 126 || c == '|' || c == '=' || c == ';' || c == ',')
            return false;
        }
      return true;
     }
   //--- lifecycle id: 1-32 of A-Z a-z 0-9 _ -
   static bool       IsLifeId(const string s)
     {
      int n = StringLen(s);
      if(n < 1 || n > 32)
         return false;
      for(int i = 0; i < n; i++)
        {
         ushort c = StringGetCharacter(s, i);
         if(!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || IsDigit(c) || c == '_' || c == '-'))
            return false;
        }
      return true;
     }
   static bool       IsHex64(const string s)
     {
      if(StringLen(s) != 64)
         return false;
      for(int i = 0; i < 64; i++)
         if(!IsHexLower(StringGetCharacter(s, i)))
            return false;
      return true;
     }
   //--- "-" or deal tickets "123;124"
   static bool       IsDeals(const string s)
     {
      if(s == "-")
         return true;
      int n = StringLen(s);
      if(n < 1 || n > 200)
         return false;
      bool need_digit = true;
      for(int i = 0; i < n; i++)
        {
         ushort c = StringGetCharacter(s, i);
         if(IsDigit(c))
           {
            need_digit = false;
            continue;
           }
         if(c != ';' || need_digit)
            return false;
         need_digit = true;
        }
      return !need_digit;
     }
   //--- folder path under Common\Files: segments of A-Z a-z 0-9 _ - . separated by backslashes
   static bool       IsFolderPath(const string s)
     {
      if(StringLen(s) < 1 || StringLen(s) > 200)
         return false;
      string parts[];
      int n = StringSplit(s, '\\', parts);
      if(n < 1)
         return false;
      for(int i = 0; i < n; i++)
        {
         int len = StringLen(parts[i]);
         if(len < 1 || len > 64 || parts[i] == "." || parts[i] == "..")
            return false;
         for(int j = 0; j < len; j++)
           {
            ushort c = StringGetCharacter(parts[i], j);
            if(!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || IsDigit(c) || c == '_' || c == '-' || c == '.'))
               return false;
           }
        }
      return true;
     }
  };

#endif

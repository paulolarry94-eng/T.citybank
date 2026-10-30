//+------------------------------------------------------------------+
//| NorthStarExport.mq5 — SCRIPT: export broker data for research     |
//|                                                                  |
//| STATUS: SOURCE ONLY, NOT COMPILED (written without MetaEditor).   |
//| Compile in MetaEditor (F7); fix any error it reports.             |
//|                                                                  |
//| Writes to <MT5 data folder>\MQL5\Files\NorthStarExport\ :        |
//|   specs.csv          every symbol: digits, contract size, tick    |
//|                      value, swaps (long/short/mode/3-day), spread,|
//|                      volume limits, first date of server history  |
//|   <SYM>_M1_<YEAR>.csv minute bars: time (UTC ms), OHLC (bid),     |
//|                      tick volume, spread in points (the broker's  |
//|                      real spread, minute by minute)               |
//|   calendar.csv       economic calendar history (UTC time,         |
//|                      currency, importance, event, actual,        |
//|                      forecast, previous)                         |
//| Before running: Tools > Options > Charts > Max bars in chart =    |
//| Unlimited, then restart MT5. Put the symbols you want in Market   |
//| Watch (or list them in InpSymbols). Zip the folder and upload it. |
//+------------------------------------------------------------------+
#property script_show_inputs
#property version "1.00"

input string InpSymbols      = "";      // comma list; empty = every symbol in Market Watch
input int    InpYearFrom     = 2011;    // first year of minute bars
input bool   InpExportSpecs  = true;
input bool   InpExportBars   = true;
input bool   InpExportCalendar = true;

#define DIR "NorthStarExport\\"
long g_off = 0;                          // seconds to add to server time to get UTC

string Iso(datetime t) { MqlDateTime d; TimeToStruct(t, d); return StringFormat("%04d-%02d-%02d %02d:%02d:%02d", d.year, d.mon, d.day, d.hour, d.min, d.sec); }

int Symbols(string &out[])
{
   ArrayResize(out, 0);
   if(StringLen(InpSymbols) > 0)
   {
      string parts[]; int n = StringSplit(InpSymbols, ',', parts);
      for(int i = 0; i < n; i++)
      {
         StringTrimLeft(parts[i]); StringTrimRight(parts[i]);
         if(StringLen(parts[i]) > 0 && SymbolSelect(parts[i], true)) { int k = ArraySize(out); ArrayResize(out, k + 1); out[k] = parts[i]; }
         else PrintFormat("NorthStarExport: symbol %s not found at this broker", parts[i]);
      }
   }
   else
   {
      int n = SymbolsTotal(true);
      ArrayResize(out, n);
      for(int i = 0; i < n; i++) out[i] = SymbolName(i, true);
   }
   return ArraySize(out);
}

void ExportSpecs(string &syms[])
{
   int h = FileOpen(DIR + "specs.csv", FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(h == INVALID_HANDLE) { Print("cannot write specs.csv ", GetLastError()); return; }
   FileWrite(h, "symbol", "description", "path", "digits", "point", "contract_size", "tick_size", "tick_value",
             "currency_base", "currency_profit", "currency_margin", "swap_mode", "swap_long", "swap_short", "swap_3day",
             "spread_now", "spread_float", "volume_min", "volume_step", "volume_max", "margin_initial", "trade_mode",
             "server_history_first_date", "gmt_offset_seconds");
   for(int i = 0; i < ArraySize(syms); i++)
   {
      string s = syms[i];
      datetime first = (datetime)SeriesInfoInteger(s, PERIOD_M1, SERIES_SERVER_FIRSTDATE);
      FileWrite(h, s, SymbolInfoString(s, SYMBOL_DESCRIPTION), SymbolInfoString(s, SYMBOL_PATH),
                (int)SymbolInfoInteger(s, SYMBOL_DIGITS), DoubleToString(SymbolInfoDouble(s, SYMBOL_POINT), 10),
                SymbolInfoDouble(s, SYMBOL_TRADE_CONTRACT_SIZE), DoubleToString(SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE), 10),
                SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), SymbolInfoString(s, SYMBOL_CURRENCY_BASE),
                SymbolInfoString(s, SYMBOL_CURRENCY_PROFIT), SymbolInfoString(s, SYMBOL_CURRENCY_MARGIN),
                (int)SymbolInfoInteger(s, SYMBOL_SWAP_MODE), SymbolInfoDouble(s, SYMBOL_SWAP_LONG), SymbolInfoDouble(s, SYMBOL_SWAP_SHORT),
                (int)SymbolInfoInteger(s, SYMBOL_SWAP_ROLLOVER3DAYS), (int)SymbolInfoInteger(s, SYMBOL_SPREAD),
                (int)SymbolInfoInteger(s, SYMBOL_SPREAD_FLOAT), SymbolInfoDouble(s, SYMBOL_VOLUME_MIN),
                SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), SymbolInfoDouble(s, SYMBOL_VOLUME_MAX),
                SymbolInfoDouble(s, SYMBOL_MARGIN_INITIAL), (int)SymbolInfoInteger(s, SYMBOL_TRADE_MODE),
                first > 0 ? Iso(first) : "", g_off);
   }
   FileClose(h);
   PrintFormat("NorthStarExport: specs.csv written (%d symbols)", ArraySize(syms));
}

void ExportBars(string s)
{
   MqlDateTime now; TimeToStruct(TimeTradeServer(), now);
   for(int y = InpYearFrom; y <= now.year; y++)
   {
      datetime a = StringToTime(StringFormat("%04d.01.01 00:00", y));
      datetime b = StringToTime(StringFormat("%04d.01.01 00:00", y + 1)) - 60;
      MqlRates r[]; int n = -1;
      for(int k = 0; k < 10 && !IsStopped(); k++)          // the terminal downloads history on demand: retry
      {
         ResetLastError();
         n = CopyRates(s, PERIOD_M1, a, b, r);
         if(n > 0) break;
         Sleep(1500);
      }
      if(n <= 0) { PrintFormat("%s %d: no M1 history (err %d)", s, y, GetLastError()); continue; }
      int h = FileOpen(DIR + StringFormat("%s_M1_%d.csv", s, y), FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
      if(h == INVALID_HANDLE) { PrintFormat("cannot write %s %d: %d", s, y, GetLastError()); continue; }
      FileWrite(h, "time_utc_ms", "open", "high", "low", "close", "tick_volume", "spread_points");
      int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
      for(int i = 0; i < n; i++)
         FileWrite(h, IntegerToString(((long)r[i].time + g_off) * 1000), DoubleToString(r[i].open, dg), DoubleToString(r[i].high, dg),
                   DoubleToString(r[i].low, dg), DoubleToString(r[i].close, dg), IntegerToString(r[i].tick_volume), IntegerToString(r[i].spread));
      FileClose(h);
      PrintFormat("%s %d: %d bars", s, y, n);
   }
}

string Val(long v) { return v == LONG_MIN ? "" : DoubleToString(v / 1000000.0, 6); }

void ExportCalendar()
{
   int h = FileOpen(DIR + "calendar.csv", FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(h == INVALID_HANDLE) { Print("cannot write calendar.csv ", GetLastError()); return; }
   FileWrite(h, "time_utc", "country", "currency", "importance", "event", "actual", "forecast", "previous", "revised_previous");
   MqlDateTime now; TimeToStruct(TimeTradeServer(), now);
   int total = 0;
   for(int y = 2007; y <= now.year && !IsStopped(); y++)
   {
      MqlCalendarValue v[];
      datetime a = StringToTime(StringFormat("%04d.01.01 00:00", y)), b = StringToTime(StringFormat("%04d.01.01 00:00", y + 1));
      int n = CalendarValueHistory(v, a, b, NULL, NULL);
      for(int i = 0; i < n; i++)
      {
         MqlCalendarEvent ev; MqlCalendarCountry c;
         if(!CalendarEventById(v[i].event_id, ev)) continue;
         CalendarCountryById(ev.country_id, c);
         string name = ev.name; StringReplace(name, ",", ";");
         FileWrite(h, Iso((datetime)((long)v[i].time + g_off)), c.code, c.currency, (int)ev.importance, name,
                   Val(v[i].actual_value), Val(v[i].forecast_value), Val(v[i].prev_value), Val(v[i].revised_prev_value));
      }
      total += MathMax(n, 0);
   }
   FileClose(h);
   PrintFormat("NorthStarExport: calendar.csv written (%d values)", total);
}

void OnStart()
{
   g_off = (long)MathRound((double)(TimeGMT() - TimeTradeServer()) / 900.0) * 900;
   PrintFormat("NorthStarExport: server time + %d s = UTC", g_off);
   string syms[];
   int n = Symbols(syms);
   if(InpExportSpecs) ExportSpecs(syms);
   if(InpExportBars)
      for(int i = 0; i < n && !IsStopped(); i++) ExportBars(syms[i]);
   if(InpExportCalendar) ExportCalendar();
   Print("NorthStarExport: done. Folder: ", TerminalInfoString(TERMINAL_DATA_PATH), "\\MQL5\\Files\\", DIR);
}

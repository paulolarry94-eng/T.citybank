//+------------------------------------------------------------------+
//|                                              TimelessCity.mq5    |
//|                                                                  |
//|   T I M E L E S S C I T Y  —  EA v2.42  (THE FULL PORTFOLIO)     |
//|   A Deterministic Operating System for Precious-Metal & FX Trade |
//|                                                                  |
//|   CODE-COMPLETE for all THREE strategies. InpStrategyMode picks:  |
//|   * MODE_REVERSION  = S1: market breakout, M20+M30, gap 1.0-2.0   |
//|     xATR, long, flat 1:1. Gold+EUR. 13/yr, 62% win, +0.24R,       |
//|     PF 1.63, 14/15 pos. Preset: S1_Production_{XAU,EUR}USD.set.   |
//|   * MODE_TREND_DONCHIAN = S2/S3: H4 Donchian-20 close breakout,   |
//|     stop = 2xATR, 1.5R chandelier trail, no TP. S2 USDJPY long    |
//|     (24/yr +0.28R), S3 gold both (30/yr +0.16R). Presets:         |
//|     S2_Trend_USDJPY.set, S3_Trend_XAUUSD.set.                     |
//|   Portfolio: -0.09/+0.01/+0.03 correlations, 67/yr, +0.22R,       |
//|   PF 1.43, Sharpe 1.14, Sortino 2.39, maxDD 22.6%, 0% ruin,       |
//|   0.52 harvests/mo. FIXED sizing locked (ladder in code, unused). |
//|   Heat cap 8% shared across all instances. DEMO-VALIDATE FIRST.   |
//|   (Legacy limit-entry reversion remains NEGATIVE; do not use it.) |
//|                                                                  |
//|   *** READ THIS BEFORE FUNDING ANYTHING *********************** |
//|   v2.30 CORRECTION: the backtest scanner that produced every     |
//|   prior headline number (52-62% win, +0.72R, 15/15 positive      |
//|   years) had a FILL-TIMING FLAW — it began scoring at the OPEN   |
//|   of the fill bar, crediting take-profits from price action that |
//|   happened BEFORE the limit order was touched. Re-scored with a  |
//|   corrected scanner (position exists only after the touch):      |
//|     win 21% (not 52%), expectancy -0.33R (not +0.72R),           |
//|     1/15 positive years. THE EDGE, AS CONFIGURED, IS NEGATIVE.   |
//|   DO NOT TRADE THIS CONFIGURATION WITH REAL MONEY. The EA        |
//|   remains sound INFRASTRUCTURE (see below) awaiting a strategy   |
//|   that survives corrected scoring. Full record:                  |
//|   TimelessCity_Correction_Report.pdf + SESSION_FINDINGS.md.      |
//|   **************************************************************|
//|                                                                  |
//|   What remains valid and valuable:                               |
//|   THE VAULT (v2.30): triple-layer state persistence — checksum-  |
//|   med GlobalVariables + atomic file mirror + a state guard that  |
//|   validates/re-anchors every loaded field. Built to hold state   |
//|   uncorrupted for years, across restarts, reinstalls, and VPS    |
//|   migrations.                                                    |
//|   PORTFOLIO HEAT GUARD: cross-instance risk cap (shared 10%).    |
//|   RESTRAINT ENGINE: 3 losing days -> 7-day pause.                |
//|   NEWS FILTER (live): blocks arming around high-impact events.   |
//|   CAPITAL ADVISOR: harvest milestones with virtual ledgers.      |
//|   HARD 10% RISK WALL: compiled, not an input.                    |
//|   PRIORITY ENGINE: H2 > H1 > M30 > M20 > M15 > M10 > M5 > M1,    |
//|   one position ever, broker-truth position adoption.             |
//+------------------------------------------------------------------+
#property copyright "TimelessCity"
#property version   "2.42"
#property description "CORRECTION build: corrected backtest shows NEGATIVE expectancy. Demo/research only — do not fund."

//--- THE WALLS (compiled, deliberately not inputs) -----------------
#define HARD_RISK_CAP    10.0    // absolute risk ceiling, %
#define MIN_KIDS         1
#define MAX_ENGULF_BARS  6
#define MAX_BASE_BARS    30
#define LIMIT_LIFE_BARS  20
#define DETECT_WINDOW    80
#define HARVEST_MULT_DEF 1.20
#define NTF              8
#define NPROF            3

enum ENUM_RISK_MODE      { RISK_ADAPTIVE, RISK_FIXED };
enum ENUM_HARVEST_PROF   { PROFILE_PRESERVE, PROFILE_SUSTAIN, PROFILE_HARVEST };
enum ENUM_STRATEGY_MODE  { MODE_REVERSION, MODE_TREND_DONCHIAN };
enum ENUM_HARVEST_MODE   { HARVEST_STRICT, HARVEST_MANUAL_CYCLE };
enum ENUM_SIDE_FILTER    { SIDES_BOTH, SIDES_BUY_ONLY, SIDES_SELL_ONLY };
enum ENUM_ENTRY_MODE     { ENTRY_LIMIT_BASE, ENTRY_MARKET_BRK };

input group "=== ENGINE: TIMEFRAME LAYERS ==="
input bool           InpUseH2           = true;   // H2 layer  (priority 1) — rare, 79% win, ballast
input bool           InpUseH1           = true;   // H1 layer  (priority 2, one-counter legs)
input bool           InpUseM30          = true;   // M30 layer (priority 3)
input bool           InpUseM20          = true;   // M20 layer (priority 4) — TIMELESS default ends here
input bool           InpUseM15          = false;  // M15 layer (priority 5) — frequency dial (more trades, lower win)
input bool           InpUseM10          = false;  // M10 layer (priority 6) — frequency dial (lower edge)
input bool           InpUseM5           = false;  // M5 layer  (priority 7) — tested negative
input bool           InpUseM1           = false;  // M1 layer  (priority 8)
input ENUM_SIDE_FILTER InpSides         = SIDES_BOTH; // Direction filter
input ENUM_ENTRY_MODE  InpEntryMode     = ENTRY_LIMIT_BASE; // LIMIT_BASE = legacy; MARKET_BRK = market at breakout close (the honest-search candidate)

input group "=== STRATEGY MODE (S1 reversion vs S2/S3 Donchian trend) ==="
input ENUM_STRATEGY_MODE InpStrategyMode = MODE_REVERSION;  // REVERSION = S1 (this chart runs impulse); TREND_DONCHIAN = S2/S3
input ENUM_TIMEFRAMES  InpTrendTF        = PERIOD_H4;        // Donchian timeframe (validated: H4)
input int              InpDonchianN      = 20;              // Donchian channel length (bars)
input double           InpTrendATRmult   = 2.0;             // Initial stop = N x ATR14 (validated: 2.0)
input double           InpTrendTrailR    = 1.5;             // Chandelier trail distance in R; activates at +this R (validated: 1.5)

input group "=== IMPULSE STYLE (v1.60) ==="
input bool            InpAllowOneCounter = true;       // Allow 1 counter candle in the leg (M30+ only)
input ENUM_TIMEFRAMES InpCounterMinTF    = PERIOD_M30; // Smallest TF for one-counter legs

input group "=== ENGINE: STRATEGY (validated; change = new system) ==="
input int            InpMinEngulf       = 2;      // Min engulf candles (type-2)
input bool           InpRequireC4EMA    = true;   // Candle-4 must open beyond EMA-10
input double         InpTargetRR        = 2.0;    // Risk:Reward (flat-exit target; winning setup = 1.0)
input bool           InpUseBreakeven    = true;   // Stop to entry at +BEatR
input double         InpBEatR           = 1.5;    // BE trigger in R (floored at 1.0)

input group "=== SPLIT-EXIT RUNNER (optional; scan says flat 1:1 wins — off) ==="
input bool           InpUseRunner       = false;  // Bank a fraction at +1R, run the rest
input double         InpRunnerBankFrac  = 0.5;    // Fraction closed at +1R (0.5 = half)
input double         InpRunnerTargetR   = 2.0;    // Runner take-profit in R
input double         InpRunnerTrailR    = 1.0;    // Runner trailing distance in R (0 = ride to target, no trail)
input double         InpMaxStopATR      = 3.0;    // Max impulse height (x ATR14, scale-free)
input double         InpMinStopATR      = 0.0;    // Min impulse height (x ATR14; 0 = off)
input double         InpMaxGapATR       = 0.60;   // GAP BAND ceiling (x ATR14) — 0.60 = 15/15-year core
input double         InpMinGapATR       = 0.30;   // GAP FLOOR: min stop (x ATR14) — kills micro-stop/slippage trades
input double         InpMinEntrySpreadX = 1.5;    // Entry->SL must be >= this x current spread

input group "=== FVG FILTER (tested 8y: hurts — off by default) ==="
input bool           InpRequireFVG      = false;  // Impulse must create a Fair Value Gap
input double         InpMinFVG_ATR      = 0.20;   // Min FVG height (x ATR14)

input group "=== SESSION FILTER (tested 8y: hurts — off by default) ==="
input bool           InpUseSessionFilter = false; // Only trade London (08-11) & NY (13-16) GMT

input group "=== RISK ENGINE ==="
input ENUM_RISK_MODE InpRiskMode        = RISK_ADAPTIVE; // Fixed or adaptive
input double         InpLadderStart     = 2.0;    // Ladder: starting risk % (2-4 default: half the drawdown, same floor)
input double         InpLadderStep      = 1.0;    // Ladder: +/- per closed trade
input double         InpLadderMin       = 1.0;    // Ladder: minimum % (floors at 1% on a losing run)
input double         InpLadderMax       = 4.0;    // Ladder: maximum %
input double         InpFixedRisk       = 1.0;    // Fixed mode risk %
input double         InpPortfolioHeatCap = 8.0;    // Max TOTAL open risk across ALL TimelessCity instances (%, 0=off) — 8% = 3-strategy stack

input group "=== CAPITAL ADVISOR ==="
input ENUM_HARVEST_PROF InpProfile      = PROFILE_SUSTAIN;  // Harvest profile
input ENUM_HARVEST_MODE InpHarvestMode  = HARVEST_STRICT;   // Reference update mode
input double         InpHarvestMult     = 1.02;   // Milestone: equity >= ref x this (1.02 ~= 1 harvest/month with the 2-4 ladder; 1.015 for firmer 1/mo)
input bool           InpResetHarvestRef = false;  // ONE-TIME: reset reference to current equity now

input group "=== RESTRAINT ENGINE ==="
input int            InpMaxLossDays     = 3;      // Consecutive losing days before pause
input int            InpPauseDays       = 7;      // Pause length (calendar days)

input group "=== THE CLOCK (GMT/UTC — broker-independent) ==="
input bool           InpUseDeadzone     = true;   // Block new setups in the deadzone
input int            InpDeadStartHour   = 16;     // Deadzone start hour (GMT)
input int            InpDeadEndHour     = 20;     // Deadzone end hour (GMT)

input group "=== NEWS FILTER (LIVE only — MT5 economic calendar) ==="
input bool           InpUseNewsFilter   = true;   // Block new setups around high-impact news
input int            InpNewsMinsBefore  = 20;     // Do not arm within N mins BEFORE an event
input int            InpNewsMinsAfter   = 15;     // Do not arm within N mins AFTER an event
input bool           InpNewsHighOnly    = true;   // true = high-impact only; false = moderate+high

input group "=== FOUNDATION ==="
input ulong          InpMagicNumber     = 888001; // Unique per chart instance
input double         InpMaxSpreadPips   = 100;    // Sanity net only (~$1.00); real guard = cost-ratio law
input double         InpMinEquityFloor  = 20.0;   // Gates close below this equity ($)
input bool           InpShowDashboard   = true;   // On-chart panel

//--- market info ---------------------------------------------------
double   g_point, g_pip;
int      g_digits, g_lotDigits;
double   g_minLot, g_maxLot, g_lotStep, g_tickSize, g_tickValue;
bool     g_init = false;

//--- timeframe layers ----------------------------------------------
ENUM_TIMEFRAMES g_tf[NTF] = { PERIOD_H2, PERIOD_H1, PERIOD_M30, PERIOD_M20, PERIOD_M15, PERIOD_M10, PERIOD_M5, PERIOD_M1 };
bool     g_tfOn[NTF];
int      g_ema[NTF];
int      g_atr[NTF];
datetime g_lastBar[NTF];
datetime g_lastSig[NTF];

//--- trend (Donchian) mode ----------------------------------------
int      g_trendATR = INVALID_HANDLE;   // ATR14 on the trend timeframe
datetime g_trendLastBar = 0;            // last processed trend-TF bar

//--- trade state ---------------------------------------------------
ulong    g_pendingTicket[NTF];
bool     g_inTrade = false;
long     g_posId = 0;
double   g_entry = 0, g_dist = 0, g_eqAtEntry = 0;
int      g_side = 0;
bool     g_beMoved = false;
bool     g_partialDone = false;   // runner: +1R bank already taken
double   g_runnerPeakR = 0;       // runner: best favourable excursion in R

//--- risk ladder ---------------------------------------------------
double   g_riskPct = 2.0;
double   g_committedRisk = 0;   // this instance's live/pending risk %, for portfolio heat

//--- capital advisor -----------------------------------------------
double   g_harvestRef = 0;
double   g_vEq[NPROF], g_vBank[NPROF], g_vRef[NPROF];  // virtual ledgers
double   g_noHarvestEq = 0;                            // pure-compounding ledger
double   g_startEq = 0;
int      g_harvests = 0;

//--- restraint engine ----------------------------------------------
datetime g_curDay = 0;
double   g_dayNet = 0;
int      g_lossDayStreak = 0;
datetime g_pauseUntil = 0;
bool     g_pausedNotified = false;

//--- stats ---------------------------------------------------------
int      g_wins = 0, g_losses = 0, g_bes = 0;

string   PROF_NAME[NPROF] = { "Preserve", "Sustain", "Harvest" };
double   PROF_PCT[NPROF]  = { 30.0, 40.0, 50.0 };

//+------------------------------------------------------------------+
//| THE VAULT — persistence built to survive years                   |
//|                                                                  |
//| Three layers, because a system meant to run unattended for years |
//| must assume every layer eventually fails:                        |
//|  1. GlobalVariables (fast, every change) + CHECKSUM — MT5 GVs    |
//|     expire ~4 weeks after last use and die with a reinstall.     |
//|  2. FILE MIRROR in MQL5\Files (atomic tmp+move, schema+checksum) |
//|     — survives GV expiry, terminal reinstall, VPS migration      |
//|     (the user can copy one file to move the city's memory).      |
//|  3. STATE GUARD on every load — no value is trusted: NaN/inf,    |
//|     out-of-band and cross-inconsistent fields are clamped or     |
//|     re-anchored to live account truth, and every repair is       |
//|     journaled. Corrupt state degrades to a safe re-anchor,       |
//|     never to a wrong trade size or a harvest storm.              |
//+------------------------------------------------------------------+
#define STATE_SCHEMA  4
#define NSTATE        (31 + 2 * NTF)

string K(const string s)
  { return "TLC_" + IntegerToString((long)InpMagicNumber) + "_" + _Symbol + "_" + s; }

string VaultFile()
  { return "TLC_" + IntegerToString((long)InpMagicNumber) + "_" + _Symbol + "_state.txt"; }

int StatePack(double &v[])
  {
   ArrayResize(v, NSTATE);
   int c = 0;
   v[c++] = g_riskPct;      v[c++] = g_harvestRef;  v[c++] = g_noHarvestEq;
   v[c++] = g_startEq;      v[c++] = g_harvests;
   for(int p = 0; p < NPROF; p++)
     { v[c++] = g_vEq[p];   v[c++] = g_vBank[p];    v[c++] = g_vRef[p]; }
   v[c++] = g_wins;         v[c++] = g_losses;      v[c++] = g_bes;
   v[c++] = (double)g_pauseUntil;                   v[c++] = g_pausedNotified ? 1 : 0;
   v[c++] = (double)g_curDay;                       v[c++] = g_dayNet;
   v[c++] = g_lossDayStreak;
   v[c++] = g_inTrade ? 1 : 0;                      v[c++] = (double)g_posId;
   v[c++] = g_entry;        v[c++] = g_dist;        v[c++] = g_eqAtEntry;
   v[c++] = g_side;         v[c++] = g_beMoved ? 1 : 0;
   v[c++] = g_partialDone ? 1 : 0;                  v[c++] = g_runnerPeakR;
   for(int i = 0; i < NTF; i++) v[c++] = (double)(long)g_pendingTicket[i];
   for(int i = 0; i < NTF; i++) v[c++] = (double)g_lastSig[i];
   return c;
  }

void StateUnpack(const double &v[])
  {
   int c = 0;
   g_riskPct = v[c++];      g_harvestRef = v[c++];  g_noHarvestEq = v[c++];
   g_startEq = v[c++];      g_harvests = (int)v[c++];
   for(int p = 0; p < NPROF; p++)
     { g_vEq[p] = v[c++];   g_vBank[p] = v[c++];    g_vRef[p] = v[c++]; }
   g_wins = (int)v[c++];    g_losses = (int)v[c++]; g_bes = (int)v[c++];
   g_pauseUntil = (datetime)(long)v[c++];           g_pausedNotified = v[c++] > 0.5;
   g_curDay = (datetime)(long)v[c++];               g_dayNet = v[c++];
   g_lossDayStreak = (int)v[c++];
   g_inTrade = v[c++] > 0.5;                        g_posId = (long)v[c++];
   g_entry = v[c++];        g_dist = v[c++];        g_eqAtEntry = v[c++];
   g_side = (int)v[c++];    g_beMoved = v[c++] > 0.5;
   g_partialDone = v[c++] > 0.5;                    g_runnerPeakR = v[c++];
   for(int i = 0; i < NTF; i++) g_pendingTicket[i] = (ulong)(long)v[c++];
   for(int i = 0; i < NTF; i++) g_lastSig[i] = (datetime)(long)v[c++];
  }

double StateChecksum(const double &v[])
  {
   double chk = 0;
   for(int i = 0; i < NSTATE; i++)
     {
      double x = MathIsValidNumber(v[i]) ? v[i] : -777777.0;
      chk = MathMod(chk * 31.0 + x * (i + 7), 1000000007.0);
     }
   return chk;
  }

void WriteStateFile(const double &v[], const double chk)
  {
   string tmp = VaultFile() + ".tmp";
   int h = FileOpen(tmp, FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(h == INVALID_HANDLE) return;              // GVs still hold; retry next save
   FileWriteString(h, "SCHEMA=" + IntegerToString(STATE_SCHEMA) + "\n");
   FileWriteString(h, "N=" + IntegerToString(NSTATE) + "\n");
   for(int i = 0; i < NSTATE; i++)
      FileWriteString(h, "V" + IntegerToString(i) + "=" +
                      DoubleToString(v[i], 8) + "\n");
   FileWriteString(h, "CHK=" + DoubleToString(chk, 8) + "\n");
   FileWriteString(h, "TS=" + IntegerToString((long)TimeCurrent()) + "\n");
   FileClose(h);
   FileMove(tmp, 0, VaultFile(), FILE_REWRITE); // atomic swap: never half-written
  }

bool ReadStateFile(double &v[])
  {
   if(!FileIsExist(VaultFile())) return false;
   int h = FileOpen(VaultFile(), FILE_READ | FILE_TXT | FILE_ANSI);
   if(h == INVALID_HANDLE) return false;
   ArrayResize(v, NSTATE);
   ArrayInitialize(v, 0);
   int schema = -1, n = -1, got = 0;
   double chk = 0; bool hasChk = false;
   while(!FileIsEnding(h))
     {
      string line = FileReadString(h);
      int eq = StringFind(line, "=");
      if(eq <= 0) continue;
      string key = StringSubstr(line, 0, eq);
      string val = StringSubstr(line, eq + 1);
      if(key == "SCHEMA") schema = (int)StringToInteger(val);
      else if(key == "N") n = (int)StringToInteger(val);
      else if(key == "CHK") { chk = StringToDouble(val); hasChk = true; }
      else if(StringSubstr(key, 0, 1) == "V")
        {
         int idx = (int)StringToInteger(StringSubstr(key, 1));
         if(idx >= 0 && idx < NSTATE) { v[idx] = StringToDouble(val); got++; }
        }
     }
   FileClose(h);
   if(schema != STATE_SCHEMA || n != NSTATE || got != NSTATE || !hasChk)
     { Print("VAULT: state file schema/shape mismatch — ignored"); return false; }
   if(MathAbs(StateChecksum(v) - chk) > 0.001)
     { Print("VAULT: state file CHECKSUM FAILED — ignored"); return false; }
   return true;
  }

void SaveState()
  {
   GlobalVariableSet(K("RISK"), g_riskPct);
   GlobalVariableSet(K("REF"), g_harvestRef);
   GlobalVariableSet(K("NHEQ"), g_noHarvestEq);
   GlobalVariableSet(K("SEQ"), g_startEq);
   GlobalVariableSet(K("HRV"), g_harvests);
   for(int p = 0; p < NPROF; p++)
     {
      GlobalVariableSet(K("VE" + IntegerToString(p)), g_vEq[p]);
      GlobalVariableSet(K("VB" + IntegerToString(p)), g_vBank[p]);
      GlobalVariableSet(K("VR" + IntegerToString(p)), g_vRef[p]);
     }
   GlobalVariableSet(K("W"), g_wins);
   GlobalVariableSet(K("L"), g_losses);
   GlobalVariableSet(K("B"), g_bes);
   GlobalVariableSet(K("PAUSE"), (double)g_pauseUntil);
   GlobalVariableSet(K("PNOTE"), g_pausedNotified ? 1 : 0);
   GlobalVariableSet(K("CDAY"), (double)g_curDay);
   GlobalVariableSet(K("DNET"), g_dayNet);
   GlobalVariableSet(K("LDS"), g_lossDayStreak);
   GlobalVariableSet(K("INTR"), g_inTrade ? 1 : 0);
   GlobalVariableSet(K("PID"), (double)g_posId);
   GlobalVariableSet(K("ENT"), g_entry);
   GlobalVariableSet(K("DST"), g_dist);
   GlobalVariableSet(K("EAE"), g_eqAtEntry);
   GlobalVariableSet(K("SIDE"), g_side);
   GlobalVariableSet(K("BEM"), g_beMoved ? 1 : 0);
   GlobalVariableSet(K("PART"), g_partialDone ? 1 : 0);
   GlobalVariableSet(K("RPK"), g_runnerPeakR);
   for(int i = 0; i < NTF; i++)
      GlobalVariableSet(K("PEND" + IntegerToString(i)), (double)(long)g_pendingTicket[i]);
   for(int i = 0; i < NTF; i++)
      GlobalVariableSet(K("SIG" + IntegerToString(i)), (double)g_lastSig[i]);
   double v[]; StatePack(v);
   double chk = StateChecksum(v);
   GlobalVariableSet(K("CHK"), chk);
   GlobalVariableSet(K("VER"), STATE_SCHEMA);
   GlobalVariableSet(K("TS"), (double)(long)TimeCurrent());
   WriteStateFile(v, chk);
  }

double Gv(const string s, const double d)
  { return GlobalVariableCheck(K(s)) ? GlobalVariableGet(K(s)) : d; }

//+------------------------------------------------------------------+
//| STATE GUARD — trust nothing, repair loudly, re-anchor safely.    |
//| Returns the number of repairs (0 = state was perfectly sane).    |
//+------------------------------------------------------------------+
int StateGuard(const double eq)
  {
   int fixes = 0;
   double loRisk = InpLadderMin;
   double hiRisk = MathMin(InpLadderMax, HARD_RISK_CAP);
   if(!MathIsValidNumber(g_riskPct) || g_riskPct < 0.05 || g_riskPct > HARD_RISK_CAP)
     { g_riskPct = InpLadderStart; fixes++;
       Print("VAULT-GUARD: risk state invalid -> reset to start ",
             DoubleToString(InpLadderStart, 1), "%"); }
   if(InpRiskMode == RISK_ADAPTIVE &&
      (g_riskPct < loRisk || g_riskPct > hiRisk))
     { g_riskPct = MathMax(loRisk, MathMin(hiRisk, g_riskPct)); fixes++;
       Print("VAULT-GUARD: risk clamped into ladder band"); }

   // reference anchors: any ref wildly inconsistent with live equity is
   // re-anchored to live equity — a fresh anchor is safe (no harvest fires,
   // sizing unaffected); a corrupt anchor is not.
   if(!MathIsValidNumber(g_harvestRef) || g_harvestRef <= 0 ||
      g_harvestRef > eq * 50 || g_harvestRef < eq / 50)
     { g_harvestRef = eq; fixes++;
       Print("VAULT-GUARD: harvest reference re-anchored to live equity"); }
   if(!MathIsValidNumber(g_noHarvestEq) || g_noHarvestEq <= 0 ||
      g_noHarvestEq > eq * 1000 || g_noHarvestEq < eq / 1000)
     { g_noHarvestEq = eq; fixes++; }
   if(!MathIsValidNumber(g_startEq) || g_startEq <= 0 || g_startEq > eq * 1000)
     { g_startEq = eq; fixes++; }
   for(int p = 0; p < NPROF; p++)
     {
      if(!MathIsValidNumber(g_vEq[p]) || g_vEq[p] <= 0 ||
         g_vEq[p] > eq * 1000 || g_vEq[p] < eq / 1000)
        { g_vEq[p] = eq; fixes++; }
      if(!MathIsValidNumber(g_vRef[p]) || g_vRef[p] <= 0 ||
         g_vRef[p] > eq * 1000 || g_vRef[p] < eq / 1000)
        { g_vRef[p] = g_vEq[p]; fixes++; }
      if(!MathIsValidNumber(g_vBank[p]) || g_vBank[p] < 0 ||
         g_vBank[p] > eq * 10000)
        { g_vBank[p] = 0; fixes++; }
     }

   if(g_wins   < 0 || g_wins   > 10000000) { g_wins = 0;   fixes++; }
   if(g_losses < 0 || g_losses > 10000000) { g_losses = 0; fixes++; }
   if(g_bes    < 0 || g_bes    > 10000000) { g_bes = 0;    fixes++; }
   if(g_harvests < 0 || g_harvests > 10000000) { g_harvests = 0; fixes++; }

   datetime now = TimeCurrent();
   if(g_pauseUntil < 0 || g_pauseUntil > now + 40 * 86400)
     { g_pauseUntil = 0; g_pausedNotified = false; fixes++;
       Print("VAULT-GUARD: pause timestamp corrupt -> cleared"); }
   if(g_curDay < 0 || g_curDay > now + 2 * 86400) { g_curDay = 0; fixes++; }
   if(!MathIsValidNumber(g_dayNet)) { g_dayNet = 0; fixes++; }
   if(g_lossDayStreak < 0 || g_lossDayStreak > 100)
     { g_lossDayStreak = 0; fixes++; }

   // open-trade bookkeeping: if marked in-trade with impossible geometry,
   // drop the flag — broker-truth adoption re-resolves the real position.
   if(g_inTrade && (!MathIsValidNumber(g_entry) || g_entry <= 0 ||
                    !MathIsValidNumber(g_dist) || g_dist <= 0 ||
                    (g_side != 1 && g_side != -1)))
     { g_inTrade = false; g_posId = 0; g_side = 0; g_beMoved = false;
       g_partialDone = false; g_runnerPeakR = 0; fixes++;
       Print("VAULT-GUARD: open-trade state inconsistent -> deferred to broker truth"); }
   if(!MathIsValidNumber(g_eqAtEntry) || g_eqAtEntry <= 0) { g_eqAtEntry = eq; fixes++; }
   if(!MathIsValidNumber(g_runnerPeakR) || g_runnerPeakR < 0) { g_runnerPeakR = 0; fixes++; }
   if(!g_inTrade) { g_partialDone = false; g_runnerPeakR = 0; }
   for(int i = 0; i < NTF; i++)
      if(g_lastSig[i] < 0 || g_lastSig[i] > now + 86400)
        { g_lastSig[i] = 0; fixes++; }
   return fixes;
  }

void LoadState()
  {
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   bool haveGv = GlobalVariableCheck(K("SEQ"));
   bool loaded = false;
   string src = "cold start";

   if(haveGv)
     {
      g_startEq      = Gv("SEQ", eq);
      g_riskPct      = Gv("RISK", InpLadderStart);
      g_harvestRef   = Gv("REF", eq);
      g_noHarvestEq  = Gv("NHEQ", eq);
      g_harvests     = (int)Gv("HRV", 0);
      for(int p = 0; p < NPROF; p++)
        {
         g_vEq[p]   = Gv("VE" + IntegerToString(p), eq);
         g_vBank[p] = Gv("VB" + IntegerToString(p), 0);
         g_vRef[p]  = Gv("VR" + IntegerToString(p), eq);
        }
      g_wins         = (int)Gv("W", 0);
      g_losses       = (int)Gv("L", 0);
      g_bes          = (int)Gv("B", 0);
      g_pauseUntil   = (datetime)(long)Gv("PAUSE", 0);
      g_pausedNotified = Gv("PNOTE", 0) > 0.5;
      g_curDay       = (datetime)(long)Gv("CDAY", 0);
      g_dayNet       = Gv("DNET", 0);
      g_lossDayStreak = (int)Gv("LDS", 0);
      g_inTrade      = Gv("INTR", 0) > 0.5;
      g_posId        = (long)Gv("PID", 0);
      g_entry        = Gv("ENT", 0);
      g_dist         = Gv("DST", 0);
      g_eqAtEntry    = Gv("EAE", eq);
      g_side         = (int)Gv("SIDE", 0);
      g_beMoved      = Gv("BEM", 0) > 0.5;
      g_partialDone  = Gv("PART", 0) > 0.5;
      g_runnerPeakR  = Gv("RPK", 0);
      for(int i = 0; i < NTF; i++)
         g_pendingTicket[i] = (ulong)(long)Gv("PEND" + IntegerToString(i), 0);
      for(int i = 0; i < NTF; i++)
         g_lastSig[i] = (datetime)(long)Gv("SIG" + IntegerToString(i), 0);

      if(GlobalVariableCheck(K("CHK")))
        {
         double v[]; StatePack(v);
         if(MathAbs(StateChecksum(v) - Gv("CHK", -1)) <= 0.001)
           { loaded = true; src = "globals (checksum OK)"; }
         else
            Print("VAULT: GLOBALS CHECKSUM FAILED — trying file mirror");
        }
      else
        { loaded = true; src = "globals (legacy, pre-checksum)"; }
     }

   if(!loaded)
     {
      double v[];
      if(ReadStateFile(v))
        { StateUnpack(v); loaded = true; src = "FILE MIRROR (checksum OK)"; }
     }

   if(!loaded)
     {
      // cold start: anchor everything to live equity
      g_startEq = eq; g_riskPct = InpLadderStart; g_harvestRef = eq;
      g_noHarvestEq = eq; g_harvests = 0;
      for(int p = 0; p < NPROF; p++)
        { g_vEq[p] = eq; g_vBank[p] = 0; g_vRef[p] = eq; }
      g_wins = 0; g_losses = 0; g_bes = 0;
      g_pauseUntil = 0; g_pausedNotified = false;
      g_curDay = 0; g_dayNet = 0; g_lossDayStreak = 0;
      g_inTrade = false; g_posId = 0; g_entry = 0; g_dist = 0;
      g_eqAtEntry = eq; g_side = 0; g_beMoved = false;
      g_partialDone = false; g_runnerPeakR = 0;
      for(int i = 0; i < NTF; i++) { g_pendingTicket[i] = 0; g_lastSig[i] = 0; }
      Print("CITY: first awakening. Start equity $", DoubleToString(eq, 2),
            " | Harvest Reference $", DoubleToString(eq, 2));
     }

   int fixes = StateGuard(eq);
   if(loaded)
      Print("VAULT: state restored from ", src,
            fixes > 0 ? StringFormat(" — %d field(s) repaired by guard", fixes)
                      : " — all fields sane");
   double ts = Gv("TS", 0);
   if(loaded && ts > 0 && TimeCurrent() - (datetime)(long)ts > 45 * 86400)
      Print("VAULT: note — state is ", (long)((TimeCurrent() - (long)ts) / 86400),
            " days old (city was asleep); guard has re-validated it");
   SaveState();   // re-seal immediately: adds checksum/file to legacy state
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   g_point  = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   g_digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   g_pip    = (g_digits == 5 || g_digits == 3) ? g_point * 10 : g_point;
   g_minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   g_maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   g_lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   g_tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   g_tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(g_point <= 0 || g_tickSize <= 0 || g_lotStep <= 0)
      return INIT_FAILED;
   g_lotDigits = 0;
   for(double s = g_lotStep; s < 1.0 - 1e-9 && g_lotDigits < 8; s *= 10)
      g_lotDigits++;

   g_tfOn[0] = InpUseH2;
   g_tfOn[1] = InpUseH1;
   g_tfOn[2] = InpUseM30;
   g_tfOn[3] = InpUseM20;
   g_tfOn[4] = InpUseM15;
   g_tfOn[5] = InpUseM10;
   g_tfOn[6] = InpUseM5;
   g_tfOn[7] = InpUseM1;
   bool any = false;
   for(int i = 0; i < NTF; i++)
     {
      g_ema[i] = INVALID_HANDLE;
      g_atr[i] = INVALID_HANDLE;
      g_lastBar[i] = 0;
      g_pendingTicket[i] = 0;
      if(!g_tfOn[i]) continue;
      g_ema[i] = iMA(_Symbol, g_tf[i], 10, 0, MODE_EMA, PRICE_CLOSE);
      g_atr[i] = iATR(_Symbol, g_tf[i], 14);
      if(g_ema[i] == INVALID_HANDLE || g_atr[i] == INVALID_HANDLE)
         return INIT_FAILED;
      any = true;
     }

   if(InpStrategyMode == MODE_TREND_DONCHIAN)
     {
      g_trendATR = iATR(_Symbol, InpTrendTF, 14);
      if(g_trendATR == INVALID_HANDLE) return INIT_FAILED;
      g_trendLastBar = 0;
     }
   else if(!any)
     {
      Print("CITY: no timeframe layer enabled — nothing to do.");
      return INIT_PARAMETERS_INCORRECT;
     }

   LoadState();

   if(InpResetHarvestRef)
     {
      double eq = AccountInfoDouble(ACCOUNT_EQUITY);
      g_harvestRef = eq;
      Print("CITY: Harvest Reference manually reset to $",
            DoubleToString(eq, 2),
            " — set InpResetHarvestRef back to false.");
     }

   ReconcileState();
   // sync portfolio heat after restart (globals persist; reconcile to reality)
   bool anyPend0 = false;
   for(int i = 0; i < NTF; i++) if(g_pendingTicket[i] > 0) anyPend0 = true;
   PublishHeat((g_inTrade || anyPend0) ? CurrentRiskPct() : 0.0);
   EventSetTimer(60);
   string engine = (InpStrategyMode == MODE_TREND_DONCHIAN)
      ? StringFormat("TREND Donchian-%d %s stop %.1fxATR trail %.1fR",
                     InpDonchianN, EnumToString(InpTrendTF),
                     InpTrendATRmult, InpTrendTrailR)
      : StringFormat("REVERSION layers %s%s%s%s%s%s%s%s",
                     InpUseH2 ? "H2 " : "", InpUseH1 ? "H1 " : "",
                     InpUseM30 ? "M30 " : "", InpUseM20 ? "M20 " : "",
                     InpUseM15 ? "M15 " : "", InpUseM10 ? "M10 " : "",
                     InpUseM5 ? "M5 " : "", InpUseM1 ? "M1" : "");
   PrintFormat("TIMELESSCITY v2.42 awake | %s | %s | risk %s | heat cap %.0f%% | ref $%.2f",
               _Symbol, engine,
               InpRiskMode == RISK_ADAPTIVE ?
                  StringFormat("ladder %.0f%% [%.0f-%.0f]", g_riskPct, InpLadderMin,
                               MathMin(InpLadderMax, HARD_RISK_CAP)) :
                  StringFormat("fixed %.1f%%", MathMin(InpFixedRisk, HARD_RISK_CAP)),
               InpPortfolioHeatCap, g_harvestRef);
   if(AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
     {
      Print("================================================================");
      Print("CITY WARNING — THIS IS A REAL-MONEY ACCOUNT.");
      Print("The v2.30 CORRECTED backtest shows NEGATIVE expectancy for this");
      Print("strategy (-0.33R, 21% win, 1/15 positive years). The prior");
      Print("positive numbers came from a fill-timing flaw in the scanner.");
      Print("This build is for DEMO / RESEARCH use. Do not fund it.");
      Print("================================================================");
     }
   g_init = true;
   Dashboard();
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   EventKillTimer();
   SaveState();
   if(!g_inTrade) PublishHeat(0.0);   // release heat if we hold no position
   PrintLedger("SESSION END — THE LEDGER");
   Comment("");
   for(int i = 0; i < NTF; i++)
     {
      if(g_ema[i] != INVALID_HANDLE) IndicatorRelease(g_ema[i]);
      if(g_atr[i] != INVALID_HANDLE) IndicatorRelease(g_atr[i]);
     }
   if(g_trendATR != INVALID_HANDLE)
     {
      IndicatorRelease(g_trendATR); g_trendATR = INVALID_HANDLE;
     }
  }

//+------------------------------------------------------------------+
void PrintLedger(string title)
  {
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   Print("================================================================");
   Print("TIMELESSCITY — ", title);
   PrintFormat("Start equity $%.2f | actual equity now $%.2f | harvests: %d",
               g_startEq, eq, g_harvests);
   PrintFormat("Record: %dW / %dL / %dBE", g_wins, g_losses, g_bes);
   Print("If this was invested, each profile would now hold:");
   for(int p = 0; p < NPROF; p++)
      PrintFormat("  %-9s(%2.0f%%): in-account $%10.2f + banked $%10.2f = TOTAL $%10.2f",
                  PROF_NAME[p], PROF_PCT[p], g_vEq[p], g_vBank[p],
                  g_vEq[p] + g_vBank[p]);
   PrintFormat("  %-14s: in-account $%10.2f (nothing ever banked)",
               "No-harvest", g_noHarvestEq);
   Print("Banked money cannot be lost to a later streak. That is the point.");
   Print("================================================================");
  }

//+------------------------------------------------------------------+
void ReconcileState()
  {
   if(g_inTrade && !OurPositionExists()) ResolveClose();
   if(!g_inTrade) AdoptPosition();
   for(int i = 0; i < NTF; i++)
      if(g_pendingTicket[i] > 0 && !OrderSelect(g_pendingTicket[i]))
         g_pendingTicket[i] = 0;
   SaveState();
  }

bool OurPositionExists()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         return true;
     }
   return false;
  }

long OurPositionId()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         return PositionGetInteger(POSITION_IDENTIFIER);
     }
   return 0;
  }

//+------------------------------------------------------------------+
//| Adopt trade context from the live broker position. With one      |
//| pending per timeframe, globals set at arm time may belong to a   |
//| DIFFERENT limit than the one that filled — broker reality is the |
//| only trustworthy source for entry/SL/side.                       |
//+------------------------------------------------------------------+
bool AdoptPosition()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol ||
         (ulong)PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;
      g_inTrade = true;
      g_posId = PositionGetInteger(POSITION_IDENTIFIER);
      g_entry = PositionGetDouble(POSITION_PRICE_OPEN);
      g_side = ((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE)
                == POSITION_TYPE_BUY) ? 1 : -1;
      double sl = PositionGetDouble(POSITION_SL);
      bool beDone = (sl > 0) &&
                    ((g_side > 0) ? (sl >= g_entry - g_point)
                                  : (sl <= g_entry + g_point));
      if(sl > 0 && !beDone) g_dist = MathAbs(g_entry - sl);
      g_beMoved = beDone;
      return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   if(!g_init) return;

   // Reconcile pending orders
   for(int i = 0; i < NTF; i++)
     {
      if(g_pendingTicket[i] == 0) continue;
      if(!OrderSelect(g_pendingTicket[i]))
        {
         if(!g_inTrade && AdoptPosition())
           {
            g_eqAtEntry = AccountInfoDouble(ACCOUNT_EQUITY);
            Print("CITY: limit filled from ", EnumToString(g_tf[i]), " (id ", g_posId, ")");
            for(int j = 0; j < NTF; j++)
              {
               if(j != i && g_pendingTicket[j] > 0)
                 {
                  MqlTradeRequest req; MqlTradeResult res;
                  ZeroMemory(req); ZeroMemory(res);
                  req.action = TRADE_ACTION_REMOVE;
                  req.order = g_pendingTicket[j];
                  OrderSend(req, res);
                  g_pendingTicket[j] = 0;
                 }
              }
           }
         g_pendingTicket[i] = 0;
         SaveState();
         continue;
        }
      if(g_inTrade)
        {
         MqlTradeRequest req; MqlTradeResult res;
         ZeroMemory(req); ZeroMemory(res);
         req.action = TRADE_ACTION_REMOVE;
         req.order = g_pendingTicket[i];
         OrderSend(req, res);
         g_pendingTicket[i] = 0;
         SaveState();
        }
     }

   // Market entries carry no pending ticket — adopt the fill immediately so
   // we never re-signal into a second position on the same instance.
   if(!g_inTrade && OurPositionExists())
     {
      if(AdoptPosition())
        {
         if(g_eqAtEntry <= 0) g_eqAtEntry = AccountInfoDouble(ACCOUNT_EQUITY);
         SaveState();
        }
     }

   if(g_inTrade)
     {
      if(!OurPositionExists()) { ResolveClose(); return; }
      if(InpStrategyMode == MODE_TREND_DONCHIAN) ManageTrendTrail();
      else if(InpUseRunner)                      ManageRunner();
      else                                        ManageBreakeven();
      return;
     }

   // --- TREND (Donchian) mode: one signal check per closed trend bar ---
   if(InpStrategyMode == MODE_TREND_DONCHIAN)
     {
      datetime tb = iTime(_Symbol, InpTrendTF, 0);
      if(tb != g_trendLastBar)
        {
         g_trendLastBar = tb;
         if(DetectDonchian()) Dashboard();
        }
      return;
     }

   // --- REVERSION mode: the impulse engine over the enabled layers ---
   for(int i = 0; i < NTF; i++)
     {
      if(!g_tfOn[i]) continue;
      datetime bar = iTime(_Symbol, g_tf[i], 0);
      if(bar == g_lastBar[i]) continue;
      g_lastBar[i] = bar;
      if(g_pendingTicket[i] > 0) continue;
      if(DetectAndArm(i))
        { Dashboard(); return; }
     }
  }

void OnTrade()
  {
   if(g_init && g_inTrade && !OurPositionExists())
      ResolveClose();
  }

//+------------------------------------------------------------------+
//| Detect a completed Impulse4 whose breakout bar is within the     |
//| last 3 closed bars. The impulse must create a Fair Value Gap,    |
//| and the base (kids) must form inside it.                         |
//+------------------------------------------------------------------+
bool DetectAndArm(int tfIdx)
  {
   if(!CanTrade()) return false;

   MqlRates r[];
   if(CopyRates(_Symbol, g_tf[tfIdx], 1, DETECT_WINDOW, r) < DETECT_WINDOW)
      return false;
   double ema[];
   if(CopyBuffer(g_ema[tfIdx], 0, 1, DETECT_WINDOW, ema) < DETECT_WINDOW)
      return false;
   double atrBuf[];
   if(CopyBuffer(g_atr[tfIdx], 0, 1, 1, atrBuf) < 1 || atrBuf[0] <= 0)
      return false;
   double atr = atrBuf[0];
   int last = DETECT_WINDOW - 1;
   if(r[last].time == g_lastSig[tfIdx]) return false;

   for(int sideIdx = 0; sideIdx < 2; sideIdx++)
     {
      int side = (sideIdx == 0) ? 1 : -1;
      if(InpSides == SIDES_BUY_ONLY && side < 0) continue;
      if(InpSides == SIDES_SELL_ONLY && side > 0) continue;
      bool up = side > 0;

      for(int a = 1; a <= last - 6; a++)
        {
         int d = -1;
         double slLvl = 0;

         // --- pattern A: strict exactly-4 leg -----------------------
         bool ok4 = true;
         for(int k = 0; k < 4; k++)
           {
            bool bl = r[a+k].close > r[a+k].open;
            if(up != bl || r[a+k].close == r[a+k].open) { ok4 = false; break; }
           }
         if(ok4)
           {
            bool prevSame = up ? (r[a-1].close > r[a-1].open)
                               : (r[a-1].close < r[a-1].open);
            bool nextSame = up ? (r[a+4].close > r[a+4].open)
                               : (r[a+4].close < r[a+4].open);
            if(!prevSame && !nextSame)
              {
               d = a + 3;
               slLvl = up ? r[a].low : r[a].high;
              }
           }

         // --- pattern B: one-counter leg (v1.60) --------------------
         // 5 candles: 4 with the trend + 1 strictly interior counter.
         // Measured better than strict on M30 and above only; SL at
         // the whole leg's extreme wick.
         if(d < 0 && InpAllowOneCounter && a + 5 <= last &&
            PeriodSeconds(g_tf[tfIdx]) >= PeriodSeconds(InpCounterMinTF))
           {
            int trend = 0, counter = 0, cpos = -1;
            bool clean = true;
            for(int k = 0; k < 5; k++)
              {
               bool bl = r[a+k].close > r[a+k].open;
               bool br = r[a+k].close < r[a+k].open;
               if((up && bl) || (!up && br)) trend++;
               else if((up && br) || (!up && bl)) { counter++; cpos = k; }
               else { clean = false; break; }   // doji breaks the leg
              }
            if(clean && trend == 4 && counter == 1 && cpos > 0 && cpos < 4)
              {
               bool prevSame = up ? (r[a-1].close > r[a-1].open)
                                  : (r[a-1].close < r[a-1].open);
               bool nextSame = up ? (r[a+5].close > r[a+5].open)
                                  : (r[a+5].close < r[a+5].open);
               bool net = up ? (r[a+4].close > r[a].open)
                             : (r[a+4].close < r[a].open);
               if(!prevSame && !nextSame && net)
                 {
                  d = a + 4;
                  slLvl = up ? r[a].low : r[a].high;
                  for(int k = 1; k < 5; k++)
                     slLvl = up ? MathMin(slLvl, r[a+k].low)
                                : MathMax(slLvl, r[a+k].high);
                 }
              }
           }

         if(d < 0) continue;
         double entryLvl = r[d].close;
         double lastExt = up ? r[d].low : r[d].high;
         double risk0 = MathAbs(entryLvl - slLvl);
         if(risk0 <= 0) continue;
         if(risk0 > InpMaxStopATR * atr) continue;
         if(risk0 < InpMinStopATR * atr) continue;

         if(InpRequireC4EMA)
           {
            if(up && !(r[a].open < ema[a])) continue;
            if(!up && !(r[a].open > ema[a])) continue;
           }

         int eng = -1;
         for(int j = d + 1; j <= MathMin(d + MAX_ENGULF_BARS, last); j++)
           {
            if(up && (r[j].low < slLvl || r[j].close > entryLvl)) break;
            if(!up && (r[j].high > slLvl || r[j].close < entryLvl)) break;
            if((up && r[j].close < lastExt) || (!up && r[j].close > lastExt))
              { eng = j; break; }
           }
         if(eng < 0 || eng - d < InpMinEngulf) continue;

         int brk = -1;
         for(int j = eng + 1; j <= MathMin(eng + 1 + MAX_BASE_BARS, last); j++)
           {
            if(up && r[j].low < slLvl) break;
            if(!up && r[j].high > slLvl) break;
            if((up && r[j].close > entryLvl) || (!up && r[j].close < entryLvl))
              { brk = j; break; }
           }
         if(brk < last - 2) continue;   // breakout within last 3 closed bars
         if(brk - eng - 1 < MIN_KIDS) continue;

         double baseExt = up ? r[eng].low : r[eng].high;
         for(int j = eng; j < brk; j++)
           {
            if(up) baseExt = MathMin(baseExt, r[j].low);
            else   baseExt = MathMax(baseExt, r[j].high);
           }
         if(up && baseExt <= slLvl) continue;
         if(!up && baseExt >= slLvl) continue;

         // THE GAP LAW (v1.50) + GAP FLOOR (v1.70).
         // For the base-extreme entry, the limit-to-SL gap IS the stop
         // distance. Cap it at InpMaxGapATR (far entries are coin flips)
         // AND floor it at InpMinGapATR: stops below ~0.3 ATR were the
         // backtest's fill artifact (assumes a perfect fill at the exact
         // extreme) — live they are micro-stops that blast through and
         // overshoot the risk budget on slippage. Trade the believable
         // 0.3-1.0 ATR core, not the illusory tail.
         double gapAtr = MathAbs(baseExt - slLvl);
         if(InpMaxGapATR > 0 && gapAtr > InpMaxGapATR * atr) continue;
         if(InpMinGapATR > 0 && gapAtr < InpMinGapATR * atr) continue;

         //+--------------------------------------------------------+
         //| FVG FILTER                                             |
         //| The 4-candle impulse must create a Fair Value Gap,     |
         //| and the base extreme (limit price) must sit inside it. |
         //+--------------------------------------------------------+
         if(InpRequireFVG)
           {
            bool fvgFound = false;
            // Check the two possible FVGs in a 4-candle impulse:
            // (a, a+2) and (a+1, a+3)
            for(int fi = a; fi <= a+1; fi++)
              {
               int fj = fi + 2;
               if(fj > a + 3) continue;

               double fvgTop, fvgBot, fvgSize;

               if(up) // Bullish FVG: Low[fj] > High[fi]
                 {
                  if(r[fj].low <= r[fi].high) continue;
                  fvgBot = r[fi].high;
                  fvgTop = r[fj].low;
                  fvgSize = fvgTop - fvgBot;
                  if(fvgSize < InpMinFVG_ATR * atr) continue;

                  // Freshness: no candle between fj and eng touched the FVG
                  bool fresh = true;
                  for(int fc = fj + 1; fc < eng; fc++)
                    {
                     if(r[fc].low <= fvgTop && r[fc].high >= fvgBot)
                       { fresh = false; break; }
                    }
                  if(!fresh) continue;

                  // Limit price (baseExt) must be inside the FVG zone
                  if(baseExt >= fvgBot && baseExt <= fvgTop)
                    { fvgFound = true; break; }
                 }
               else // Bearish FVG: High[fj] < Low[fi]
                 {
                  if(r[fj].high >= r[fi].low) continue;
                  fvgBot = r[fj].high;
                  fvgTop = r[fi].low;
                  fvgSize = fvgTop - fvgBot;
                  if(fvgSize < InpMinFVG_ATR * atr) continue;

                  bool fresh = true;
                  for(int fc = fj + 1; fc < eng; fc++)
                    {
                     if(r[fc].low <= fvgTop && r[fc].high >= fvgBot)
                       { fresh = false; break; }
                    }
                  if(!fresh) continue;

                  if(baseExt >= fvgBot && baseExt <= fvgTop)
                    { fvgFound = true; break; }
                 }
              }
            if(!fvgFound) continue;
           }

         if(ArmLimit(tfIdx, side, baseExt, slLvl, r[last].time))
            return true;
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
double CurrentRiskPct()
  {
   double r = (InpRiskMode == RISK_ADAPTIVE) ? g_riskPct : InpFixedRisk;
   r = MathMax(InpLadderMin, r);
   return MathMin(r, HARD_RISK_CAP);
  }

//+------------------------------------------------------------------+
//| PORTFOLIO HEAT — cross-instance risk coordination.               |
//| Every TimelessCity instance publishes its live/pending risk to a |
//| shared global (visible across symbols/charts). Before arming, an |
//| instance sums the OTHER instances' heat and refuses if the total |
//| would breach InpPortfolioHeatCap. This makes 3-instrument         |
//| (gold+EUR+GBP) deployment safe: 3 slots can never collectively    |
//| risk more than the cap, even if all fire at once.                 |
//+------------------------------------------------------------------+
string HeatKey()
  { return "TLC_HEAT_" + IntegerToString((long)InpMagicNumber); }

void PublishHeat(double pct)
  {
   g_committedRisk = pct;
   GlobalVariableSet(HeatKey(), pct);
  }

double PortfolioHeatOthers()
  {
   double sum = 0;
   string mine = HeatKey();
   int total = GlobalVariablesTotal();
   for(int i = 0; i < total; i++)
     {
      string nm = GlobalVariableName(i);
      if(StringFind(nm, "TLC_HEAT_") == 0 && nm != mine)
         sum += GlobalVariableGet(nm);
     }
   return sum;
  }

//+------------------------------------------------------------------+
bool ArmLimit(int tfIdx, int side, double price, double sl, datetime sigBar)
  {
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick)) return false;
   bool up = side > 0;
   bool trendMode = (InpStrategyMode == MODE_TREND_DONCHIAN);
   bool marketMode = trendMode || (InpEntryMode == ENTRY_MARKET_BRK);
   if(marketMode)
     {
      // Market entry (trend Donchian breakout, or reversion breakout close).
      // Fill moment is exact — the entry style the corrected scanner never
      // mis-scored. Entry price = current ask/bid.
      price = up ? tick.ask : tick.bid;
      if(up && price <= sl) return false;
      if(!up && price >= sl) return false;
     }
   else
     {
      if(up && tick.ask <= price) return false;
      if(!up && tick.bid >= price) return false;
     }

   double dist = MathAbs(price - sl);
   double sprNow = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * g_point;
   if(dist < InpMinEntrySpreadX * MathMax(sprNow, g_point))
     { Print("CITY: skip — stop would be dust vs spread (cost-ratio law)");
       return false; }
   // Trend mode has NO take-profit — the chandelier trail exits the winner
   // (letting it run is the edge). Flat exit uses InpTargetRR; runner mode
   // rides to the runner target and banks +1R manually via ManageRunner().
   double tp = 0.0;
   if(!trendMode)
     {
      double rr = InpUseRunner ? MathMax(1.0, MathMin(InpRunnerTargetR, 10.0))
                               : MathMax(0.5, MathMin(InpTargetRR, 10.0));
      tp = up ? price + rr * dist : price - rr * dist;
     }

   double riskPct = CurrentRiskPct();
   // PORTFOLIO HEAT GUARD: refuse if other instances + this trade breach cap
   if(InpPortfolioHeatCap > 0 &&
      PortfolioHeatOthers() + riskPct > InpPortfolioHeatCap + 1e-6)
     { Print("CITY: skip — portfolio heat cap (others ",
             DoubleToString(PortfolioHeatOthers(), 1), "% + ",
             DoubleToString(riskPct, 1), "% > ",
             DoubleToString(InpPortfolioHeatCap, 1), "%)"); return false; }
   double riskMoney = AccountInfoDouble(ACCOUNT_EQUITY) * riskPct / 100.0;
   double riskPerLot = dist / g_tickSize * g_tickValue;
   if(riskPerLot <= 0) return false;
   double lots = MathFloor(riskMoney / riskPerLot / g_lotStep) * g_lotStep;
   if(lots < g_minLot)
     {
      if(g_minLot * riskPerLot > riskMoney * 2)
        { Print("CITY: skip — min lot would risk >2x budget"); return false; }
      lots = g_minLot;
     }
   lots = MathMin(lots, g_maxLot);
   double margin = 0;
   if(!OrderCalcMargin(up ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lots,
                       price, margin)) return false;
   if(margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.95)
     { Print("CITY: skip — margin"); return false; }
   lots = NormalizeDouble(lots, g_lotDigits);

   MqlTradeRequest req;
   MqlTradeResult res;
   ZeroMemory(req); ZeroMemory(res);
   req.symbol = _Symbol;
   req.volume = lots;
   req.sl = NormalizeDouble(sl, g_digits);
   req.tp = NormalizeDouble(tp, g_digits);
   req.magic = InpMagicNumber;
   string tflabel = trendMode ? ("DON" + EnumToString(InpTrendTF))
                              : EnumToString(g_tf[tfIdx]);
   req.comment = "TLC|" + tflabel + (up ? "|B" : "|S");

   long fill = SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
   if((fill & SYMBOL_FILLING_FOK) != 0)
      req.type_filling = ORDER_FILLING_FOK;
   else if((fill & SYMBOL_FILLING_IOC) != 0)
      req.type_filling = ORDER_FILLING_IOC;
   else
      req.type_filling = ORDER_FILLING_RETURN;

   if(marketMode)
     {
      req.action = TRADE_ACTION_DEAL;
      req.type = up ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
      req.price = NormalizeDouble(price, g_digits);
      req.deviation = 10;
     }
   else
     {
      req.action = TRADE_ACTION_PENDING;
      req.type = up ? ORDER_TYPE_BUY_LIMIT : ORDER_TYPE_SELL_LIMIT;
      req.price = NormalizeDouble(price, g_digits);
      req.type_time = ORDER_TIME_SPECIFIED;
      req.expiration = (datetime)(TimeCurrent() +
                       LIMIT_LIFE_BARS * PeriodSeconds(g_tf[tfIdx]));
     }

   if(!OrderSend(req, res) ||
      (res.retcode != TRADE_RETCODE_DONE && res.retcode != TRADE_RETCODE_PLACED))
     { Print("CITY: ", marketMode ? "market order" : "limit",
             " rejected rc=", res.retcode); return false; }

   if(!marketMode)
      g_pendingTicket[tfIdx] = res.order;   // market fills adopt via broker truth
   g_side = side;
   g_entry = price;
   g_dist = dist;
   g_beMoved = false;
   g_partialDone = false;
   g_runnerPeakR = 0.0;
   if(trendMode) g_eqAtEntry = AccountInfoDouble(ACCOUNT_EQUITY);
   g_lastSig[tfIdx] = sigBar;
   PublishHeat(riskPct);   // this instance now holds committed risk
   SaveState();
   PrintFormat("CITY: %s %s %s @ %s | SL %s | TP %s | %.2f lots | risk %.1f%%",
               tflabel, up ? "BUY" : "SELL",
               marketMode ? "MARKET entry" : "limit armed",
               DoubleToString(price, g_digits), DoubleToString(sl, g_digits),
               tp > 0 ? DoubleToString(tp, g_digits) : "trail", lots, CurrentRiskPct());
   return true;
  }

//+------------------------------------------------------------------+
//| News blackout — LIVE only (MT5 economic calendar).               |
//| Returns true if a high-impact event for this symbol's currencies |
//| falls inside [now-after, now+before]. In the Strategy Tester the |
//| calendar is empty, so this is a no-op there (the backtest never  |
//| modelled news cost; this protects the LIVE account only).        |
//+------------------------------------------------------------------+
bool NewsBlackout()
  {
   if(!InpUseNewsFilter) return false;
   datetime now  = TimeCurrent();
   datetime from = now - (datetime)InpNewsMinsAfter  * 60;
   datetime to   = now + (datetime)InpNewsMinsBefore * 60;

   // relevant currencies: this symbol's base + profit, and always USD
   string curs[3];
   curs[0] = SymbolInfoString(_Symbol, SYMBOL_CURRENCY_BASE);
   curs[1] = SymbolInfoString(_Symbol, SYMBOL_CURRENCY_PROFIT);
   curs[2] = "USD";
   ENUM_CALENDAR_EVENT_IMPORTANCE need =
      InpNewsHighOnly ? CALENDAR_IMPORTANCE_HIGH : CALENDAR_IMPORTANCE_MODERATE;

   for(int k = 0; k < 3; k++)
     {
      string cur = curs[k];
      if(cur == "" || cur == "XAU" || cur == "XAG") continue; // no metal calendar
      // skip a currency already checked
      bool dup = false;
      for(int p = 0; p < k; p++) if(curs[p] == cur) { dup = true; break; }
      if(dup) continue;

      MqlCalendarValue values[];
      int n = CalendarValueHistory(values, from, to, NULL, cur);
      for(int i = 0; i < n; i++)
        {
         if(values[i].time < from || values[i].time > to) continue;
         MqlCalendarEvent ev;
         if(!CalendarEventById(values[i].event_id, ev)) continue;
         if(ev.importance >= need) return true;   // inside a news window
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
bool CanTrade()
  {
   datetime now = TimeCurrent();
   if(g_pauseUntil > 0 && now < g_pauseUntil) return false;
   if(g_pauseUntil > 0 && now >= g_pauseUntil) ResumeFromPause();
   if(AccountInfoDouble(ACCOUNT_EQUITY) < InpMinEquityFloor) return false;
   if(NewsBlackout()) return false;

   if(InpUseSessionFilter)
     {
      MqlDateTime gmt; TimeToStruct(TimeGMT(), gmt);
      bool london = (gmt.hour >= 8 && gmt.hour < 11);
      bool ny     = (gmt.hour >= 13 && gmt.hour < 16);
      if(!london && !ny) return false;
     }

   if(InpUseDeadzone)
     {
      MqlDateTime d; TimeToStruct(TimeGMT(), d);
      int hs = InpDeadStartHour, he = InpDeadEndHour;
      bool inside = (he < hs) ? (d.hour >= hs || d.hour < he)
                              : (d.hour >= hs && d.hour < he);
      if(inside) return false;
     }
   long spr = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spr * g_point / g_pip > InpMaxSpreadPips) return false;
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED) ||
      !TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return false;
   return true;
  }

//+------------------------------------------------------------------+
void ResumeFromPause()
  {
   g_pauseUntil = 0;
   g_lossDayStreak = 0;
   g_pausedNotified = false;
   SaveState();
   string msg = "TimelessCity\n\nEA Active\n\nTrading has resumed.";
   Print("CITY: ", msg);
   if(TerminalInfoInteger(TERMINAL_NOTIFICATIONS_ENABLED)) SendNotification(msg);
  }

//+------------------------------------------------------------------+
void ManageBreakeven()
  {
   if(!InpUseBreakeven || g_beMoved || g_dist <= 0) return;
   double trig = g_dist * MathMax(1.0, InpBEatR);
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick)) return;
   bool reached = (g_side > 0) ? (tick.bid >= g_entry + trig)
                               : (tick.ask <= g_entry - trig);
   if(!reached) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol ||
         (ulong)PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;
      MqlTradeRequest req; MqlTradeResult res;
      ZeroMemory(req); ZeroMemory(res);
      req.action = TRADE_ACTION_SLTP;
      req.symbol = _Symbol;
      req.position = t;
      req.sl = NormalizeDouble(g_entry, g_digits);
      req.tp = PositionGetDouble(POSITION_TP);
      if(OrderSend(req, res) && res.retcode == TRADE_RETCODE_DONE)
        { g_beMoved = true; SaveState(); Print("CITY: stop to entry"); }
      return;
     }
  }

//+------------------------------------------------------------------+
//| SPLIT-EXIT RUNNER — bank a fraction at +1R, ride the rest.        |
//| Step 1: at +1R, close InpRunnerBankFrac of the volume at market   |
//|         and move the stop to breakeven (locks the banked 1:1).    |
//| Step 2: with the remainder, trail the stop by InpRunnerTrailR (in |
//|         R units) behind the best excursion, never below breakeven;|
//|         the order TP (runner target) closes the winner. Trail=0    |
//|         rides straight to target. Off unless InpUseRunner.        |
//+------------------------------------------------------------------+
void ManageRunner()
  {
   if(g_dist <= 0) return;
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick)) return;
   bool up = g_side > 0;
   double px = up ? tick.bid : tick.ask;                 // conservative side
   double favR = up ? (px - g_entry) / g_dist : (g_entry - px) / g_dist;

   // locate our position
   ulong tkt = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
        { tkt = t; break; }
     }
   if(tkt == 0) return;
   if(!PositionSelectByTicket(tkt)) return;
   double curSL = PositionGetDouble(POSITION_SL);
   double curTP = PositionGetDouble(POSITION_TP);
   double vol   = PositionGetDouble(POSITION_VOLUME);

   // --- Step 1: bank the fraction at +1R and go to breakeven ---
   if(!g_partialDone && favR >= 1.0)
     {
      double closeVol = MathFloor(vol * MathMax(0.0, MathMin(InpRunnerBankFrac, 0.95))
                                  / g_lotStep) * g_lotStep;
      closeVol = NormalizeDouble(MathMax(closeVol, 0.0), g_lotDigits);
      if(closeVol >= g_minLot && vol - closeVol >= g_minLot)
        {
         MqlTradeRequest req; MqlTradeResult res; ZeroMemory(req); ZeroMemory(res);
         req.action = TRADE_ACTION_DEAL;
         req.symbol = _Symbol;
         req.position = tkt;
         req.volume = closeVol;
         req.type = up ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
         req.price = up ? tick.bid : tick.ask;
         req.deviation = 10;
         long fm = SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
         req.type_filling = (fm & SYMBOL_FILLING_FOK) ? ORDER_FILLING_FOK :
                            (fm & SYMBOL_FILLING_IOC) ? ORDER_FILLING_IOC :
                                                        ORDER_FILLING_RETURN;
         if(OrderSend(req, res) &&
            (res.retcode == TRADE_RETCODE_DONE || res.retcode == TRADE_RETCODE_PLACED))
           {
            g_partialDone = true; g_beMoved = true; g_runnerPeakR = favR;
            // move stop to breakeven on the remainder
            MqlTradeRequest s; MqlTradeResult sr; ZeroMemory(s); ZeroMemory(sr);
            s.action = TRADE_ACTION_SLTP; s.symbol = _Symbol; s.position = tkt;
            s.sl = NormalizeDouble(g_entry, g_digits); s.tp = curTP;
            OrderSend(s, sr);
            SaveState();
            PrintFormat("CITY: runner — banked %.2f lots at +1R, stop to BE, "
                        "%.2f lots riding to %.1fR", closeVol, vol - closeVol,
                        InpRunnerTargetR);
           }
        }
      else if(vol - closeVol < g_minLot)
        {
         // remainder would be sub-min: treat as a flat 1:1 exit instead
         MqlTradeRequest req; MqlTradeResult res; ZeroMemory(req); ZeroMemory(res);
         req.action = TRADE_ACTION_DEAL; req.symbol = _Symbol; req.position = tkt;
         req.volume = vol; req.type = up ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
         req.price = up ? tick.bid : tick.ask; req.deviation = 10;
         long fm = SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
         req.type_filling = (fm & SYMBOL_FILLING_FOK) ? ORDER_FILLING_FOK :
                            (fm & SYMBOL_FILLING_IOC) ? ORDER_FILLING_IOC :
                                                        ORDER_FILLING_RETURN;
         if(OrderSend(req, res)) { g_partialDone = true; SaveState();
            Print("CITY: runner — size too small to split, flat 1:1 exit"); }
        }
      return;
     }

   // --- Step 2: trail the runner behind its best excursion ---
   if(g_partialDone && InpRunnerTrailR > 0.0 && favR > g_runnerPeakR)
     {
      g_runnerPeakR = favR;
      double trailR = g_runnerPeakR - InpRunnerTrailR;      // stop level in R
      if(trailR > 0.0)                                       // only lock profit
        {
         double newSL = up ? g_entry + trailR * g_dist
                           : g_entry - trailR * g_dist;
         bool better = up ? (newSL > curSL + g_point)
                          : (newSL < curSL - g_point);
         if(better)
           {
            MqlTradeRequest s; MqlTradeResult sr; ZeroMemory(s); ZeroMemory(sr);
            s.action = TRADE_ACTION_SLTP; s.symbol = _Symbol; s.position = tkt;
            s.sl = NormalizeDouble(newSL, g_digits); s.tp = curTP;
            if(OrderSend(s, sr) && sr.retcode == TRADE_RETCODE_DONE)
              { SaveState();
                PrintFormat("CITY: runner trail -> stop %.1fR", trailR); }
           }
        }
      SaveState();
     }
  }

//+------------------------------------------------------------------+
//| DETECT DONCHIAN — S2/S3 trend entry.                             |
//| On each closed InpTrendTF bar: BUY if its close is above the      |
//| N-bar Donchian high (the high of the N bars BEFORE it), SELL if   |
//| below the N-bar low. Candle-close confirmation (not intrabar) by  |
//| construction. Stop = InpTrendATRmult x ATR14. Market entry, no    |
//| take-profit — the chandelier trail (ManageTrendTrail) exits.      |
//+------------------------------------------------------------------+
bool DetectDonchian()
  {
   if(!CanTrade()) return false;
   int need = InpDonchianN + 2;
   MqlRates rt[];
   ArraySetAsSeries(rt, true);
   if(CopyRates(_Symbol, InpTrendTF, 0, need, rt) < need) return false;
   // rt[0] = forming bar, rt[1] = last CLOSED bar, rt[2..N+1] = the prior N
   double donHigh = -DBL_MAX, donLow = DBL_MAX;
   for(int k = 2; k <= InpDonchianN + 1; k++)
     {
      if(rt[k].high > donHigh) donHigh = rt[k].high;
      if(rt[k].low  < donLow)  donLow  = rt[k].low;
     }
   double cbar = rt[1].close;
   int side = 0;
   if(cbar > donHigh)      side = 1;
   else if(cbar < donLow)  side = -1;
   if(side == 0) return false;
   if(InpSides == SIDES_BUY_ONLY  && side < 0) return false;
   if(InpSides == SIDES_SELL_ONLY && side > 0) return false;

   double atrBuf[];
   if(CopyBuffer(g_trendATR, 0, 1, 1, atrBuf) < 1 || atrBuf[0] <= 0) return false;
   double atr = atrBuf[0];
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick)) return false;
   double price = (side > 0) ? tick.ask : tick.bid;
   double sl    = (side > 0) ? price - InpTrendATRmult * atr
                             : price + InpTrendATRmult * atr;
   return ArmLimit(0, side, price, sl, rt[1].time);
  }

//+------------------------------------------------------------------+
//| MANAGE TREND TRAIL — chandelier stop in R units.                 |
//| Initial stop is the N x ATR (-1R) set on the order. Once the      |
//| trade reaches +InpTrendTrailR, trail the stop InpTrendTrailR      |
//| behind the best excursion (at +1.5R peak -> stop to breakeven;    |
//| at +3R -> stop to +1.5R; ...). Never loosens the stop. No TP.     |
//+------------------------------------------------------------------+
void ManageTrendTrail()
  {
   if(g_dist <= 0) return;
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick)) return;
   bool up = g_side > 0;
   double px = up ? tick.bid : tick.ask;
   double favR = up ? (px - g_entry) / g_dist : (g_entry - px) / g_dist;
   if(favR <= g_runnerPeakR) return;          // no new high; initial stop holds
   g_runnerPeakR = favR;
   if(g_runnerPeakR < InpTrendTrailR) { SaveState(); return; }   // trail not armed yet
   double trailR = g_runnerPeakR - InpTrendTrailR;               // >= 0 once armed
   double newSL = up ? g_entry + trailR * g_dist
                     : g_entry - trailR * g_dist;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tkt = PositionGetTicket(i);
      if(tkt == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol ||
         (ulong)PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;
      double curSL = PositionGetDouble(POSITION_SL);
      bool better = up ? (newSL > curSL + g_point) : (newSL < curSL - g_point);
      if(better)
        {
         MqlTradeRequest s; MqlTradeResult sr; ZeroMemory(s); ZeroMemory(sr);
         s.action = TRADE_ACTION_SLTP; s.symbol = _Symbol; s.position = tkt;
         s.sl = NormalizeDouble(newSL, g_digits); s.tp = 0.0;
         if(OrderSend(s, sr) && sr.retcode == TRADE_RETCODE_DONE)
           { if(!g_beMoved) g_beMoved = true;
             PrintFormat("CITY: trend trail -> stop %.2fR (peak %.2fR)",
                         trailR, g_runnerPeakR); }
        }
      break;
     }
   SaveState();
  }

//+------------------------------------------------------------------+
void ResolveClose()
  {
   if(g_posId <= 0) { ClearTrade(); return; }
   if(!HistorySelectByPosition(g_posId)) return;
   int deals = HistoryDealsTotal();
   double net = 0;
   bool sawExit = false;
   for(int i = 0; i < deals; i++)
     {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0) continue;
      net += HistoryDealGetDouble(tk, DEAL_PROFIT)
           + HistoryDealGetDouble(tk, DEAL_COMMISSION)
           + HistoryDealGetDouble(tk, DEAL_SWAP);
      ENUM_DEAL_ENTRY e = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_OUT_BY) sawExit = true;
     }
   if(!sawExit) return;

   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double band = eq * 0.0005;

   if(g_eqAtEntry > 0)
     {
      double ratio = net / g_eqAtEntry;
      g_noHarvestEq *= (1.0 + ratio);
      for(int p = 0; p < NPROF; p++)
        {
         g_vEq[p] *= (1.0 + ratio);
         if(g_vEq[p] >= g_vRef[p] * InpHarvestMult)
           {
            double w = PROF_PCT[p] / 100.0 * (g_vEq[p] - g_vRef[p]);
            g_vBank[p] += w;
            g_vEq[p] -= w;
            g_vRef[p] = g_vEq[p];
           }
        }
     }

   if(net > band)
     {
      g_wins++;
      if(InpRiskMode == RISK_ADAPTIVE)
         g_riskPct = MathMin(MathMin(InpLadderMax, HARD_RISK_CAP),
                             g_riskPct + InpLadderStep);
      PrintFormat("CITY: WIN $%.2f | ladder -> %.1f%%", net, CurrentRiskPct());
     }
   else if(net < -band)
     {
      g_losses++;
      if(InpRiskMode == RISK_ADAPTIVE)
         g_riskPct = MathMax(InpLadderMin, g_riskPct - InpLadderStep);
      PrintFormat("CITY: LOSS $%.2f | ladder -> %.1f%%", net, CurrentRiskPct());
     }
   else
     { g_bes++; PrintFormat("CITY: BREAKEVEN $%.2f | ladder unchanged", net); }

   TrackDay(net);

   if(eq >= g_harvestRef * InpHarvestMult)
      HarvestSuggestion(eq);

   ClearTrade();
  }

//+------------------------------------------------------------------+
void TrackDay(double net)
  {
   MqlDateTime d; TimeToStruct(TimeCurrent(), d);
   d.hour = 0; d.min = 0; d.sec = 0;
   datetime today = StructToTime(d);
   if(g_curDay != 0 && today != g_curDay)
      FinalizeDay();
   if(g_curDay != today) { g_curDay = today; g_dayNet = 0; }
   g_dayNet += net;
   SaveState();
  }

//+------------------------------------------------------------------+
void FinalizeDay()
  {
   if(g_curDay == 0) return;
   if(g_dayNet < 0)
     {
      g_lossDayStreak++;
      PrintFormat("CITY: losing day closed (net $%.2f), streak %d/%d",
                  g_dayNet, g_lossDayStreak, InpMaxLossDays);
      if(g_lossDayStreak >= InpMaxLossDays && g_pauseUntil == 0)
        {
         g_pauseUntil = TimeCurrent() + InpPauseDays * 86400;
         g_pausedNotified = true;
         string msg = StringFormat(
            "TimelessCity\n\nEA Paused\n\nTrading paused for %d days.\n\nAutomatic Resume\n\n%s",
            InpPauseDays, TimeToString(g_pauseUntil, TIME_DATE));
         Print("CITY: ", msg);
         if(TerminalInfoInteger(TERMINAL_NOTIFICATIONS_ENABLED)) SendNotification(msg);
        }
     }
   else if(g_dayNet > 0)
      g_lossDayStreak = 0;
   g_dayNet = 0;
   g_curDay = 0;
  }

//+------------------------------------------------------------------+
void OnTimer()
  {
   if(!g_init) return;
   MqlDateTime d; TimeToStruct(TimeCurrent(), d);
   d.hour = 0; d.min = 0; d.sec = 0;
   datetime today = StructToTime(d);
   if(g_curDay != 0 && today != g_curDay)
     { FinalizeDay(); SaveState(); }
   if(g_pauseUntil > 0 && TimeCurrent() >= g_pauseUntil)
      ResumeFromPause();
   Dashboard();
  }

//+------------------------------------------------------------------+
void HarvestSuggestion(double eq)
  {
   g_harvests++;
   double profit = eq - g_harvestRef;
   double growth = (eq / g_harvestRef - 1.0) * 100.0;
   int sel = (int)InpProfile;
   double suggested = PROF_PCT[sel] / 100.0 * profit;

   string msg = StringFormat(
      "TimelessCity\n\nHarvest Suggested\n\nCurrent Equity:\n$%.2f\n\n"
      "Harvest Reference:\n$%.2f\n\nGrowth:\n%.2f%%\n\n"
      "Profit Above Reference:\n$%.2f\n\nSuggested Withdrawal:\n$%.2f\n\n"
      "Profile:\n%s (%.0f%%)",
      eq, g_harvestRef, growth, profit, suggested,
      PROF_NAME[sel], PROF_PCT[sel]);
   Alert(msg);
   if(TerminalInfoInteger(TERMINAL_NOTIFICATIONS_ENABLED)) SendNotification(msg);

   Print("================================================================");
   PrintFormat("CITY MILESTONE #%d | equity $%.2f | reference $%.2f | growth %.2f%%",
               g_harvests, eq, g_harvestRef, growth);
   Print("Suggested withdrawal at this milestone, by profile:");
   for(int p = 0; p < NPROF; p++)
      PrintFormat("  %-9s(%2.0f%%): withdraw $%.2f, keep compounding $%.2f",
                  PROF_NAME[p], PROF_PCT[p],
                  PROF_PCT[p] / 100.0 * profit, eq - PROF_PCT[p] / 100.0 * profit);
   PrintLedger("RUNNING LEDGER (virtual, per profile)");

   if(InpHarvestMode == HARVEST_STRICT)
      g_harvestRef = eq;
   SaveState();
  }

//+------------------------------------------------------------------+
void ClearTrade()
  {
   g_inTrade = false; g_posId = 0; g_entry = 0; g_dist = 0;
   g_side = 0; g_beMoved = false; g_eqAtEntry = 0;
   g_partialDone = false; g_runnerPeakR = 0;
   bool anyPend = false;
   for(int i = 0; i < NTF; i++) if(g_pendingTicket[i] > 0) anyPend = true;
   if(!anyPend) PublishHeat(0.0);   // slot free — release portfolio heat
   SaveState();
   Dashboard();
  }

//+------------------------------------------------------------------+
void Dashboard()
  {
   if(!InpShowDashboard) return;
   int pendingCount = 0;
   for(int i = 0; i < NTF; i++) if(g_pendingTicket[i] > 0) pendingCount++;
   string state = g_inTrade ? "IN TRADE" :
                  pendingCount > 0 ? "LIMIT ARMED (" + IntegerToString(pendingCount) + ")" :
                  (g_pauseUntil > 0 && TimeCurrent() < g_pauseUntil) ?
                  "PAUSED -> " + TimeToString(g_pauseUntil, TIME_DATE) : "HUNTING";
   int total = g_wins + g_losses;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   Comment(
      "\n  ~~~ T I M E L E S S C I T Y ~~~  v2.10\n",
      "  ", _Symbol, "  layers: ", InpUseH2 ? "H2 " : "", InpUseH1 ? "H1 " : "",
      InpUseM30 ? "M30 " : "", InpUseM20 ? "M20 " : "", InpUseM15 ? "M15 " : "",
      InpUseM10 ? "M10 " : "", InpUseM5 ? "M5 " : "", InpUseM1 ? "M1" : "", "\n",
      "  state    : ", state, "\n",
      "  record   : ", g_wins, "W / ", g_losses, "L / ", g_bes, "BE",
      total > 0 ? "  (" + DoubleToString(100.0 * g_wins / total, 1) + "%)" : "", "\n",
      "  risk     : ", DoubleToString(CurrentRiskPct(), 1), "% ",
      InpRiskMode == RISK_ADAPTIVE ? "(adaptive ladder)" : "(fixed)",
      "  wall ", DoubleToString(HARD_RISK_CAP, 0), "%\n",
      "  equity   : $", DoubleToString(eq, 2), "\n",
      "  harvest  : ref $", DoubleToString(g_harvestRef, 2),
      "  next @ $", DoubleToString(g_harvestRef * InpHarvestMult, 2),
      "  [", PROF_NAME[(int)InpProfile], "]\n",
      "  banked*  : P $", DoubleToString(g_vBank[0], 2),
      " | S $", DoubleToString(g_vBank[1], 2),
      " | H $", DoubleToString(g_vBank[2], 2), "  (*virtual ledgers)\n",
      "  heat     : this ", DoubleToString(g_committedRisk, 1),
      "% | others ", DoubleToString(PortfolioHeatOthers(), 1),
      "% | cap ", DoubleToString(InpPortfolioHeatCap, 0), "%  (portfolio)\n",
      "  law      : one position | 1:2 | gap<=",
      DoubleToString(InpMaxGapATR, 1), "xATR | leg 4",
      InpAllowOneCounter ? "|4+1(M30+)" : "", " | FVG ",
      InpRequireFVG ? "on" : "off", " | session ",
      InpUseSessionFilter ? "L/NY" : "off", " | deadzone ",
      InpUseDeadzone ? IntegerToString(InpDeadStartHour) + "-" +
                       IntegerToString(InpDeadEndHour) + "h GMT" : "off",
      " | news ",
      InpUseNewsFilter ? ("-" + IntegerToString(InpNewsMinsBefore) + "/+" +
                          IntegerToString(InpNewsMinsAfter) + "m " +
                          (InpNewsHighOnly ? "hi" : "mod+") +
                          (NewsBlackout() ? " [BLOCK]" : "")) : "off", "\n");
  }
//+------------------------------------------------------------------+
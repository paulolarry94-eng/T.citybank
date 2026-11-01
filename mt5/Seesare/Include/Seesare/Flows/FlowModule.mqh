//+------------------------------------------------------------------+
//|                                     Seesare/Flows/FlowModule.mqh |
//| SEESARE router, Phase 2: the interface every payer-flow module   |
//| implements (the owner's "CPlayerFlowStrategy"). UNCOMPILED SOURCE.|
//|                                                                  |
//| A module answers three questions and nothing else:               |
//|   SlotForUtcDay  does it trade on this UTC day, and when does it  |
//|                  enter and leave (UTC)?                          |
//|   Decide         at the entry instant: which side, how far is    |
//|                  the stop, is the target a live order? (closed   |
//|                  bars and published data only)                   |
//|   DeclaredRatio  the reward:risk it declares to SEESARE, taken   |
//|                  from its measured research payoff.              |
//| The router owns timing, the spread gate, sizing, execution and   |
//| the ledger, so every module is held to the same rules.           |
//|                                                                  |
//| Evidence gates status: a REJECTED or UNTESTED module can run on  |
//| PAPER only (a forward-test journal, never the SEESARE ledger);   |
//| LIVE needs at least a Truth Lab pass (CANDIDATE).                |
//+------------------------------------------------------------------+
#ifndef SEESARE_FLOWS_FLOWMODULE_MQH
#define SEESARE_FLOWS_FLOWMODULE_MQH

#include <Seesare\Core\Clock.mqh>
#include <Seesare\Core\Calendar.mqh>

enum ENUM_SEESARE_EVIDENCE
  {
   SEESARE_EVIDENCE_UNTESTED  = 0,   // never tested, or the data it needs does not exist here
   SEESARE_EVIDENCE_REJECTED  = 1,   // failed the Truth Lab
   SEESARE_EVIDENCE_CANDIDATE = 2,   // passed the lab (Tier B): forward test next
   SEESARE_EVIDENCE_VERIFIED  = 3    // passed the lab and a forward test
  };

enum ENUM_SEESARE_STATUS
  {
   SEESARE_STATUS_OFF   = 0,         // not run
   SEESARE_STATUS_PAPER = 1,         // forward test on live quotes: journal only, never the ledger
   SEESARE_STATUS_LIVE  = 2          // SEESARE lifecycle event (REAL when allowed and feasible, else SHADOW)
  };

struct SSeesareSlot
  {
   int               module;         // index in the router's module list
   string            module_id;
   datetime          day_utc;        // UTC date of the entry: one SEESARE event per UTC day
   datetime          entry_utc;
   datetime          exit_utc;       // time exit: the position is closed at this instant if still open
  };

struct SSeesareOrderPlan
  {
   int               side;           // +1 buy, -1 sell, 0 = no trade today
   double            stop_distance;  // price distance from the entry to the stop (lower boundary for a buy)
   double            ratio;          // declared ratio: target distance = ratio x stop_distance
   bool              place_target;   // true: the target is a live take-profit; false: recorded only (time exit)
   double            max_spread_points;
   string            note;
  };

void SeesareClearPlan(SSeesareOrderPlan &p)
  {
   p.side              = 0;
   p.stop_distance     = 0.0;
   p.ratio             = 0.0;
   p.place_target      = false;
   p.max_spread_points = 0.0;
   p.note              = "";
  }

void SeesareCopySlot(const SSeesareSlot &src, SSeesareSlot &dst)
  {
   dst.module    = src.module;
   dst.module_id = src.module_id;
   dst.day_utc   = src.day_utc;
   dst.entry_utc = src.entry_utc;
   dst.exit_utc  = src.exit_utc;
  }

class CSeesareFlowModule
  {
protected:
   string            m_id;
   string            m_symbol;
   string            m_domain;
   ENUM_SEESARE_EVIDENCE m_evidence;
   string            m_evidence_ref;
   ENUM_SEESARE_STATUS m_status;
   string            m_error;
   double            PipSize(void) const;
   double            PipsToPoints(const double pips) const;

public:
                     CSeesareFlowModule(void);
   virtual          ~CSeesareFlowModule(void) {}
   string            Id(void) const { return m_id; }
   string            Market(void) const { return m_symbol; }
   string            Domain(void) const { return m_domain; }
   ENUM_SEESARE_EVIDENCE Evidence(void) const { return m_evidence; }
   string            EvidenceRef(void) const { return m_evidence_ref; }
   ENUM_SEESARE_STATUS Status(void) const { return m_status; }
   string            LastError(void) const { return m_error; }
   bool              SetStatus(const ENUM_SEESARE_STATUS status);
   static string     StatusName(const ENUM_SEESARE_STATUS s);
   static string     EvidenceName(const ENUM_SEESARE_EVIDENCE e);
   //--- the slot that opens on this UTC day; false = no slot (LastError() says why when it is not simply a day off)
   virtual bool      SlotForUtcDay(const datetime utc_day, SSeesareSlot &slot) = 0;
   //--- at the entry instant: true = plan filled (side 0 = no trade today); false = data not ready yet, ask again
   virtual bool      Decide(const SSeesareSlot &slot, CSeesareClock &clock, SSeesareOrderPlan &plan) = 0;
   virtual double    DeclaredRatio(void) const = 0;
  };

CSeesareFlowModule::CSeesareFlowModule(void)
  {
   m_id           = "";
   m_symbol       = "";
   m_domain       = "";
   m_evidence     = SEESARE_EVIDENCE_UNTESTED;
   m_evidence_ref = "";
   m_status       = SEESARE_STATUS_OFF;
   m_error        = "";
  }

//--- LIVE needs a Truth Lab pass; a refused LIVE request falls back to PAPER and returns false
bool CSeesareFlowModule::SetStatus(const ENUM_SEESARE_STATUS status)
  {
   m_error = "";
   if(status == SEESARE_STATUS_LIVE && m_evidence < SEESARE_EVIDENCE_CANDIDATE)
     {
      m_status = SEESARE_STATUS_PAPER;
      m_error = m_id + " is " + EvidenceName(m_evidence) + " (" + m_evidence_ref + "): it runs on PAPER only";
      return false;
     }
   m_status = status;
   return true;
  }

string CSeesareFlowModule::StatusName(const ENUM_SEESARE_STATUS s)
  {
   if(s == SEESARE_STATUS_PAPER)
      return "PAPER";
   if(s == SEESARE_STATUS_LIVE)
      return "LIVE";
   return "OFF";
  }

string CSeesareFlowModule::EvidenceName(const ENUM_SEESARE_EVIDENCE e)
  {
   if(e == SEESARE_EVIDENCE_REJECTED)
      return "REJECTED";
   if(e == SEESARE_EVIDENCE_CANDIDATE)
      return "CANDIDATE";
   if(e == SEESARE_EVIDENCE_VERIFIED)
      return "VERIFIED";
   return "UNTESTED";
  }

//--- 10 points on 3- and 5-digit quotes (one pip), else one point
double CSeesareFlowModule::PipSize(void) const
  {
   double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
   long digits = SymbolInfoInteger(m_symbol, SYMBOL_DIGITS);
   if(digits == 3 || digits == 5)
      return 10.0 * point;
   return point;
  }

double CSeesareFlowModule::PipsToPoints(const double pips) const
  {
   double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
   if(point <= 0.0)
      return 0.0;
   return pips * PipSize() / point;
  }

#endif

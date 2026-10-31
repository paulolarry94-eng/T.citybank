"""Breadth test of the equity-index RSI(2) family on three NEW indices (Nasdaq 100, FTSE 100, Nikkei 225).
index_rsi2_v1 (US500, GER40) was positive in every period (2011-19 +0.040R, 2020-22 +0.026R, 2023-25 +0.094R) but failed
the strict criteria on sample size and stress. Rules and grid are UNCHANGED (all four settings, not only its candidate);
only the markets differ, and they were fixed in this file before any strategy was run on them (data checked for quality
only). HistData M1, EST->UTC. Costs and swaps: the lab's conservative estimates (costs.json)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from index_rsi2_v1 import signals, EXECUTOR, GRID, MANAGEMENT, TIMEFRAMES, STOP_CAP_ATR, RULES, HYPOTHESIS  # identical rules

NAME = "index_rsi2_breadth_v1"
FAMILY = ["mean-reversion", "dip-buying", "rsi2", "index", "daily", "breadth"]
MARKETS = ["NAS100", "UK100", "JP225"]

"""Truth Lab entry point.

    python3 research/truth/run.py research/truth/strategies/<idea>.py              # full protocol incl. the logged 2023-25 look
    python3 research/truth/run.py research/truth/strategies/<idea>.py --no-look    # stop before the final look
    python3 research/truth/run.py <file> --markets XAUUSD,USDJPY                    # subset of markets with data in data/
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protocol

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("strategy"); ap.add_argument("--no-look", action="store_true"); ap.add_argument("--markets"); ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    protocol.run(os.path.abspath(a.strategy), look=not a.no_look, markets=a.markets.split(",") if a.markets else None, procs=a.procs)

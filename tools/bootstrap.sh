#!/bin/bash
# One-time setup for a fresh container: python packages, and optionally pysystemtrade's public futures data
# (needed only for research/multiasset). Usage: bash tools/bootstrap.sh [--with-futures-data]
set -e
cd "$(dirname "$0")/.."
python3 -c "import numpy, pandas, numba, holidays" 2>/dev/null || pip install -q -r requirements.txt
python3 -c "import numpy, pandas, numba; print('python packages ok')"
echo "market data files: $(ls data/*_M1_bid_*.npz 2>/dev/null | wc -l)"
if [ "$1" = "--with-futures-data" ] && [ ! -d /home/user/robcarver17/pysystemtrade/data/futures ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 https://github.com/robcarver17/pysystemtrade /home/user/robcarver17/pysystemtrade
  echo "pysystemtrade futures data cloned"
fi

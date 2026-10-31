#!/bin/bash
# T.citybank SessionStart hook: make the container ready, then load the research memory into context.
set -euo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}"

# 1. Python packages (system pip; checked every start, installed only when missing). Cloud sessions only.
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  if ! python3 -c "import numpy, pandas, numba" >/dev/null 2>&1; then
    pip install -q -r requirements.txt >&2
  fi
fi

# 2. The project's memory (ledger, principles, open questions, last journal entry) -> session context.
python3 research/truth/memory.py --digest 2>/dev/null || echo "(research memory unavailable: run python3 research/truth/memory.py --digest)"

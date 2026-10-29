# Recovered Edge Room modules — partial, best-effort

The cloud container holding the full Edge Room build was reset before any of it
reached GitHub (every push had been refused with 403). This folder is what could
be rebuilt from the session transcript: the 14 modules that were written in full
during the session, with every later edit replayed in order.

NOT recoverable from the transcript (they existed before it began):
- edge_room/app.py, voice.py, present.py, claude_narrator.py, phases.py,
  tests_narration.py
- backi/ (engine, lessons ledger, tests)
- backtest/ (true_outcomes.py, backtest.py, corrected_search*.py)
- all data (.npz event grids, M1 archives), SESSION_FINDINGS.md, TIMELESSCITY.md

The recovered files compile. They have not been run against the original app,
because the app is gone. Treat them as source material, not a working build.

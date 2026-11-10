# Verification evidence — 2026-11-10

Executed locally:

- `pytest -q`: 88 passed, 0 failed, 0 skipped; 13 dependency deprecation warnings.
- `python -m compileall -q app.py scripts/build_lab_report.py`: passed.
- `git diff --check`: passed after generating CSV with LF line endings.
- `.venv/bin/python -m pytest -q` after UI dependency installation: 88 passed, no warnings reported.
- `.venv/bin/python scripts/check_ui.py`: passed page rendering, word_count tool loop, transcript saving and blocking send before execution; all offline with a fake provider.
- Streamlit local server on 127.0.0.1:8501: started; `/_stcore/health` returned HTTP 200 with `ok`.
- Live 9router base eval: v0 14/20, v1 16/20, v2 19/20, v3 19/20.
- Live 9router group eval v3: 10/10 (5 single-turn, 5 multi-turn).
- Live CLI chat: three answered turns in `transcripts/v3_9router_20261110T155328283829.transcript.json`.

Model for these runs: `ag/gemini-3.8-flash-low`.
See `REPORT.md` and original run JSON for hashes and per-case failures.

External tool execution remains limited by missing TAVILY_API_KEY, FIRECRAWL_API_KEY and RAPIDAPI_KEY. Public deployment has not been performed.

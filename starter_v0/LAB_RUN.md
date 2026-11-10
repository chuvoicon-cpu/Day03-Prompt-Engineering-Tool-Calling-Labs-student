# Research Agent — 9router

Run from starter_v0, with the virtual environment activated.

Fill ROUTER9_API_KEY and ROUTER9_BASE_URL in .env. Do not commit keys.

```bash
pip install -r requirements-ui.txt
streamlit run app.py --server.address 127.0.0.1
python3 chat.py --provider 9router --model ag/gemini-3.8-flash-low --version v3 --system-prompt artifacts/versions/v3/system_prompt.md
python3 run_eval.py --provider 9router --model ag/gemini-3.8-flash-low --version v3 --system-prompt artifacts/versions/v3/system_prompt.md --suite group --eval-cases data/eval_group.json
pytest -q
python3 scripts/check_ui.py
```

UI: http://localhost:8501. Local URL is not a public deployment URL.
Tool results from external sources are untrusted data. UI disables send; use the CLI only with explicit confirmation. A routing PASS does not imply successful tool execution.

## Live tools

Set TAVILY_API_KEY for lookup, FIRECRAWL_API_KEY for fetch, and RAPIDAPI_KEY for timeline/social_search. Local tools (policy, format, clarify, word_count) require no external key. arXiv tools require internet but no API key.

## Reproduce all versions

```bash
python3 run_eval.py --provider 9router --model ag/gemini-3.8-flash-low --version v1 --system-prompt artifacts/versions/v1/system_prompt.md --suite base --eval-cases data/eval_base.json
python3 run_eval.py --provider 9router --model ag/gemini-3.8-flash-low --version v2 --system-prompt artifacts/versions/v2/system_prompt.md --suite base --eval-cases data/eval_base.json
python3 run_eval.py --provider 9router --model ag/gemini-3.8-flash-low --version v3 --system-prompt artifacts/versions/v3/system_prompt.md --suite base --eval-cases data/eval_base.json
python3 scripts/build_lab_report.py
```

Each command records a new run. Report generation picks the most recent base run per version; it leaves historical run JSON untouched. Never rename a prompt version after collecting evidence with it.

The recorded v3 baseline is 19/20 and group evaluation 10/10. R12 still asks for missing message text instead of yes/no confirmation. Do not treat the result as proof that publishing is secure.


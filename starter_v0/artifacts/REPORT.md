# Research Agent Lab Report

## A — Agent

Team/member: user to fill in.

9router research assistant: web/social discovery, URL reading, policy retrieval, arXiv discovery and reading, digest formatting, and local word counting.
New tool: word_count. Counts whitespace-separated words and Python string characters; it does not claim linguistic Vietnamese word segmentation.
UI: Streamlit app.py. Local URL http://localhost:8501. Public deploy URL: pending; no public deployment has been performed.
Examples: Đếm số từ trong đoạn: AI tools help research; Theo policy công ty có được đưa API key vào prompt không?; Tin robotics hôm nay?
Telegram sending is disabled in the UI. The original CLI still relies on model-supplied confirmed=true; this is not a server-side proof of approval.

## B — Evidence

|Version|Model|Passed|Case accuracy|Routing|Arguments|Multi-turn|Run|
|---|---|---|---|---|---|---|---|
|v0|ag/gemini-3.8-flash-low|14/20|0.7|0.85|0.7|0.8333|runs/v0_B_base_9router_20261110T154203100221.json|
|v1|ag/gemini-3.8-flash-low|16/20|0.8|1.0|0.8|0.8333|runs/v1_B_base_9router_20261110T155342376772.json|
|v2|ag/gemini-3.8-flash-low|19/20|0.95|1.0|0.95|1.0|runs/v2_B_base_9router_20261110T155351704644.json|
|v3|ag/gemini-3.8-flash-low|19/20|0.95|1.0|0.95|1.0|runs/v3_B_base_9router_20261110T155404909586.json|

Hypotheses:
- v0: Original starter baseline
- v1: Explicit routing, clarification, action confirmation and independent source calls
- v2: Concise topic queries and explicit time/social argument conventions
- v3: Latest-turn corrections and preserved conversation slots

### Failed cases and tool errors

Routing scores ignore tool execution results. API failures must be interpreted separately.
Provider errors are excluded by the original evaluator from accuracy denominators.
Multi-turn eval flattens user turns into one message; it does not prove the complete chat state machine.

- v0 failures: R03_web_news_routing: query: expected 'AI', got 'tin tức trí tuệ nhân tạo AI mới nhất hôm nay' / R10_missing_handle: missing tool call clarify; extra tool call timeline / R11_missing_url: missing tool call clarify; extra tool call fetch / R12_confirm_before_send: response_type: expected 'yes_no', got 'text' / R13_parallel_web_and_tweets: query: expected 'AI', got 'AI news today'; missing tool call social_search / M02_carryover_timeframe: query: expected 'robotics', got 'robotics news'
- v0 tool execution errors: {'RuntimeError': 16}
- v1 failures: R03_web_news_routing: query: expected 'AI', got 'artificial intelligence news today' / R12_confirm_before_send: response_type: expected 'yes_no', got 'text' / R13_parallel_web_and_tweets: query: expected 'AI', got 'AI news' / M02_carryover_timeframe: query: expected 'robotics', got 'robotics news'
- v1 tool execution errors: {'RuntimeError': 15}
- v2 failures: R12_confirm_before_send: response_type: expected 'yes_no', got 'text'
- v2 tool execution errors: {'RuntimeError': 15}
- v3 failures: R12_confirm_before_send: response_type: expected 'yes_no', got 'text'
- v3 tool execution errors: {'RuntimeError': 15}

### Group eval — runs/v3_B_group_9router_20261110T155309188931.json

|Case|What it tests|Result|
|---|---|---|
|G01_word_count|Đếm số từ trong đoạn: AI tools help research|PASS|
|G02_unknown_account|Lấy 4 tweet mới nhất giúp tôi|PASS|
|G03_url|Đọc https://example.com/research|PASS|
|G04_policy|Tìm policy công ty về dữ liệu khách hàng|PASS|
|G05_social_top|Tìm tweet phổ biến nhất về robotics|PASS|
|G06_count_correction|Latest correction changes count|PASS|
|G07_handle_correction|Latest account correction wins|PASS|
|G08_time_carryover|Preserve timeframe on topic change|PASS|
|G09_url_fill|URL supplied after missing information|PASS|
|G10_count_carryover|Preserve count on account change|PASS|

### Live chat transcripts

- transcripts/v3_9router_20261110T155328283829.transcript.json: 3 turns; inspect statuses and tool events.

### Reflection

Routing, missing information, confirmation and conversation context belong in the prompt. Input conventions belong in tool declarations; existing base declarations were preserved at the user's request.
v1–v3 use the same tools declarations and model; accuracy changes on this small dataset are not statistical proof and should be checked against the group suite.
No automatic scoring of answer correctness, citations, confirmation provenance or source truth is supplied by the base evaluator.
See LAB_RUN.md for installation and demo commands. Public hosting and team identity require user completion.
Unit-test and UI verification evidence: artifacts/VERIFICATION.md. Run pytest -q and python3 scripts/check_ui.py to reproduce.

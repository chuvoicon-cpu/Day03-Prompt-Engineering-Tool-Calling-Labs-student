"""TODO(student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO(student): implement this test"

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
word_count_tool = TOOL_FUNCTIONS["word_count"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    result = clarify_tool(
        question="Chọn nguồn nào?",
        response_type="choice",
        options=["Web", "Social"],
    )

    assert result["options"] == ["Web", "Social"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    result = format_tool(items=[
        {"section": "A", "title": "Một"},
        {"section": "B", "title": "Hai"},
        {"section": "A", "title": "Ba"},
    ], template="sections")

    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    result = format_tool(
        items=[{"title": "Một"}, {"title": "Hai"}],
        template="thread",
    )

    assert "1/ Một" in result["markdown"]
    assert "2/ Hai" in result["markdown"]


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    assert format_tool(items=None, template="bullets")["item_count"] == 0
    assert format_tool(items=[], template="bullets")["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat-1")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed=True)

    assert len(calls) == 1
    assert "bot-token" in calls[0]["url"]
    assert calls[0]["json"] == {"chat_id": "chat-1", "text": "Bản tin", "parse_mode": "Markdown"}
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "Nội dung",
        "metadata": {"title": "T", "sourceURL": "https://example.com/a"},
    }}))

    result = fetch_tool(url="https://example.com/a")

    assert calls[0]["json"]["url"] == "https://example.com/a"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://example.com/a",
        "source": "example.com",
        "summary": "Nội dung",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {
        "markdown": "x" * 5000,
        "metadata": {},
    }}))

    result = fetch_tool(url="https://example.com/a")

    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": [
        {"text": "missing id"},
        *[
            {"screen_name": "alice", "tweet_id": str(index), "text": f"Tweet {index}"}
            for index in range(6)
        ],
    ]}))

    result = timeline_tool(screenname="alice", limit=3)

    assert len(result["items"]) == 3
    assert all(item["url"].startswith("https://x.com/alice/status/") for item in result["items"])
    assert calls[0]["params"] == {"screenname": "alice"}


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"tweets": []}))

    social_search_tool(query="AI", search_type="Top", limit=2)

    assert calls[0]["params"] == {"query": "AI", "search_type": "Top"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy_tool(query="", policy_area="all")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    result = policy_tool(query="API keys credentials", policy_area="data_privacy")

    assert result["results"]
    assert all(item["policy_area"] == "data_privacy" for item in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    result = policy_tool(query="citation policy", policy_area="source_citation", top_k=10)
    matching = [item for item in result["results"] if item["section"] == "Injection probe"]

    assert matching
    assert any("ignore the citation policy" in line.lower() for line in matching[0]["untrusted_text"])
    assert "ignore the citation policy" not in matching[0]["facts"].lower()


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_my_new_tool_happy_path() -> None:
    result = word_count_tool(text="AI tools help research")

    assert result == {"tool": "word_count", "word_count": 4, "character_count": 22}


def test_my_new_tool_bad_input_from_model() -> None:
    result = word_count_tool(text="")

    assert result["error"] == "ValueError"


def test_my_new_tool_failure_returns_error_dict() -> None:
    result = word_count_tool(text=123)

    assert result["error"] == "TypeError"

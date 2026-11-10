from pathlib import Path
import json
from versioning import file_hash

ROOT = Path(__file__).resolve().parents[1]


def test_group_has_five_single_and_five_multiturn_cases():
    cases = json.loads((ROOT / "data/eval_group.json").read_text())["cases"]
    assert len(cases) == 10
    assert sum("turns" in case for case in cases) == 5
    assert sum("query" in case for case in cases) == 5
    assert len({case["id"] for case in cases}) == 10
    assert any(call["name"] == "word_count" for case in cases for call in case["expect"]["tool_calls"])


def test_versioned_prompts_match_recorded_evidence():
    for version in ("v1", "v2", "v3"):
        matches = list((ROOT / "runs").glob(f"{version}_B_base_9router_*.json"))
        assert matches, f"Missing live evidence for {version}"
        run = json.loads(sorted(matches)[-1].read_text())
        assert run["prompt_hash"] == file_hash(ROOT / f"artifacts/versions/{version}/system_prompt.md")
        assert run["tools_hash"] == file_hash(ROOT / "artifacts/tools.yaml")


def test_live_demo_has_three_successful_turns():
    matches = list((ROOT / "transcripts").glob("v3_9router_*.transcript.json"))
    assert matches
    transcript = json.loads(sorted(matches)[-1].read_text())
    assert len(transcript["turns"]) >= 3
    assert all(turn["status"] == "answered" for turn in transcript["turns"])


"""Build the lab report from saved eval evidence; never invent metrics."""
from pathlib import Path
import csv
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
HYPOTHESES = {
    "v0": "Original starter baseline",
    "v1": "Explicit routing, clarification, action confirmation and independent source calls",
    "v2": "Concise topic queries and explicit time/social argument conventions",
    "v3": "Latest-turn corrections and preserved conversation slots",
}
def main():
    runs = [json.loads(path.read_text()) | {"file": str(path.relative_to(ROOT))}
            for path in sorted((ROOT / "runs").glob("*.json"))]
    selected = {}
    for run in runs:
        if run.get("version") in HYPOTHESES and run.get("suite") == "base":
            selected[run["version"]] = run
    fields = "version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_before,metric_after,run_file".split(",")
    previous = ""
    with (ROOT / "artifacts/version_log.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for version, hypothesis in HYPOTHESES.items():
            if version not in selected:
                continue
            run = selected[version]
            score = run["summary"]["case_accuracy"]
            writer.writerow(dict(version=version, author="Lab participant (name pending)",
                changed_artifact=run["system_prompt"], artifact_version=run["artifact_version"],
                prompt_hash=run["prompt_hash"], tools_hash=run["tools_hash"], reason=hypothesis,
                hypothesis=hypothesis, metric_before=previous, metric_after=score, run_file=run["file"]))
            previous = score
    lines = ["# Research Agent Lab Report", "", "## A — Agent", "",
        "Team/member: user to fill in.", "",
        "9router research assistant: web/social discovery, URL reading, policy retrieval, arXiv discovery and reading, digest formatting, and local word counting.",
        "New tool: word_count. Counts whitespace-separated words and Python string characters; it does not claim linguistic Vietnamese word segmentation.",
        "UI: Streamlit app.py. Local URL http://localhost:8501. Public deploy URL: pending; no public deployment has been performed.",
        "Examples: Đếm số từ trong đoạn: AI tools help research; Theo policy công ty có được đưa API key vào prompt không?; Tin robotics hôm nay?",
        "Telegram sending is disabled in the UI. The original CLI still relies on model-supplied confirmed=true; this is not a server-side proof of approval.", "",
        "## B — Evidence", "",
        "|Version|Model|Passed|Case accuracy|Routing|Arguments|Multi-turn|Run|",
        "|---|---|---|---|---|---|---|---|"]
    for version, run in selected.items():
        s = run["summary"]
        lines.append(f"|{version}|{run['model']}|{s['passed_cases']}/{s['total_cases']}|{s['case_accuracy']}|{s.get('tool_routing_accuracy')}|{s.get('argument_accuracy')}|{s.get('multiturn_accuracy')}|{run['file']}|")
    lines += ["", "Hypotheses:"] + [f"- {v}: {h}" for v,h in HYPOTHESES.items()]
    lines += ["", "### Failed cases and tool errors", "",
              "Routing scores ignore tool execution results. API failures must be interpreted separately.",
              "Provider errors are excluded by the original evaluator from accuracy denominators.",
              "Multi-turn eval flattens user turns into one message; it does not prove the complete chat state machine.", ""]
    for version, run in selected.items():
        failures = [f"{item['id']}: " + "; ".join(item["result"].get("failures", []))
                    for item in run["results"] if not item["result"]["passed"]]
        errors = Counter(event.get("result", {}).get("error", event.get("error", ""))
                         for item in run["results"] for event in item.get("tool_results", [])
                         if event.get("error") or event.get("result", {}).get("error"))
        lines += [f"- {version} failures: " + (" / ".join(failures) or "none"),
                  f"- {version} tool execution errors: {dict(errors)}"]
    groups = [r for r in runs if r.get("suite") == "group" and r.get("version") == "v3"]
    if groups:
        group = groups[-1]
        lines += ["", f"### Group eval — {group['file']}", "",
                  "|Case|What it tests|Result|", "|---|---|---|"]
        for item in group["results"]:
            lines.append(f"|{item['id']}|{item.get('metadata', {}).get('what_it_tests', '')}|{'PASS' if item['result']['passed'] else 'FAIL'}|")
    lines += ["", "### Live chat transcripts", ""]
    transcripts = sorted((ROOT / "transcripts").glob("*v3*.transcript.json"))
    for path in transcripts:
        data = json.loads(path.read_text())
        lines.append(f"- {path.relative_to(ROOT)}: {len(data.get('turns', []))} turns; inspect statuses and tool events.")
    lines += ["", "### Reflection", "",
        "Routing, missing information, confirmation and conversation context belong in the prompt. Input conventions belong in tool declarations; existing base declarations were preserved at the user's request.",
        "v1–v3 use the same tools declarations and model; accuracy changes on this small dataset are not statistical proof and should be checked against the group suite.",
        "No automatic scoring of answer correctness, citations, confirmation provenance or source truth is supplied by the base evaluator.",
        "See LAB_RUN.md for installation and demo commands. Public hosting and team identity require user completion.",
        "Unit-test and UI verification evidence: artifacts/VERIFICATION.md. Run pytest -q and python3 scripts/check_ui.py to reproduce."]
    (ROOT / "artifacts/REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()


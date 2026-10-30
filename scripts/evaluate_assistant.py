"""Evaluate synthetic labelled requests; demo results are never AI evidence."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.integrations import assistant
from backend.config import settings


def score(case, result):
    clarification = result.get("clarification")
    items = result.get("items", [])
    if case.get("clarification"):
        return isinstance(clarification, str) and bool(clarification.strip()) and items == []
    if clarification or not isinstance(items, list):
        return False
    try:
        actual = sorted((item["product_id"], item["quantity"]) for item in items)
        expected = sorted((item["product_id"], item["quantity"]) for item in case["items"])
        return actual == expected and all(type(item["quantity"]) is int for item in items)
    except (KeyError, TypeError):
        return False


def evaluate(suite, mode, limit=None):
    if mode not in {"demo", "gemini"}:
        raise ValueError("Choose demo or gemini mode.")
    if mode == "gemini" and not settings.gemini_key:
        raise ValueError("Set GEMINI_API_KEY locally before running a Gemini evaluation.")
    settings.ai_mode = mode
    rows = []
    for case in suite["cases"][:limit]:
        started = time.monotonic()
        try:
            result = assistant.interpret(case["text"], suite["catalogue"])
            passed = score(case, result)
            error = None
        except Exception as exc:
            # Reports must not contain provider error bodies, credentials, or request headers.
            result, passed, error = None, False, type(exc).__name__
        rows.append({"id": case["id"], "language": case["language"], "tag": case["tag"],
                     "text": case["text"], "expected": {"items": case.get("items"), "clarification": case.get("clarification", False)},
                     "actual": result, "passed": passed, "error_type": error,
                     "duration_ms": round((time.monotonic() - started) * 1000)})
    groups = defaultdict(lambda: {"passed": 0, "total": 0})
    for row in rows:
        for group in ["language:" + row["language"], "tag:" + row["tag"]]:
            groups[group]["total"] += 1
            groups[group]["passed"] += int(row["passed"])
    return {"evaluated_at": datetime.now(timezone.utc).isoformat(), "suite_version": suite["version"],
            "mode": mode, "model": settings.gemini_model if mode == "gemini" else None,
            "note": "Synthetic development set; review Swahili with native speakers. Demo parser results are not AI performance.",
            "passed": sum(row["passed"] for row in rows), "total": len(rows), "groups": dict(groups), "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["demo", "gemini"], default="demo")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit is not None and not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    suite = json.loads((ROOT / "evaluations" / "assistant-cases.json").read_text(encoding="utf-8"))
    try:
        report = evaluate(suite, args.mode, args.limit)
    except ValueError as exc:
        parser.error(str(exc))
    output = args.output or ROOT / "data" / "evaluations" / f"assistant-{args.mode}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    label = "DEMO PARSER (not AI)" if args.mode == "demo" else f"GEMINI ({report['model']})"
    print(f"{label}: {report['passed']}/{report['total']} labelled cases passed.")
    print("Report:", output)
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

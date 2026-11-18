#!/usr/bin/env python3
"""Validate blast-radius-review eval artifacts and optional human grade results."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.name}: {exc}") from exc


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate():
    eval_doc = load_json(ROOT / "evals.json")
    trigger_doc = load_json(ROOT / "trigger-evals.json")
    require(set(eval_doc) == {"skill_name", "evals"}, "evals.json has unexpected/missing top-level keys")
    require(eval_doc["skill_name"] == "blast-radius-review", "unexpected eval skill_name")
    require(isinstance(eval_doc["evals"], list) and len(eval_doc["evals"]) == 6, "expected six behavioral evals")
    ids = set()
    for index, case in enumerate(eval_doc["evals"], 1):
        require(set(case) == {"id", "prompt", "expected_output", "files", "expectations"}, f"eval {index}: invalid keys")
        require(type(case["id"]) is int and case["id"] > 0 and case["id"] not in ids, f"eval {index}: id must be a unique positive integer")
        ids.add(case["id"])
        require(all(isinstance(case[key], str) and case[key].strip() for key in ("prompt", "expected_output")), f"{case['id']}: prompt/output must be nonempty strings")
        require("snapshot" in case["prompt"].lower() and "live filesystem" in case["prompt"].lower(), f"{case['id']}: prompt must mark facts as snapshot rather than live state")
        require(isinstance(case["files"], list) and all(isinstance(file, str) for file in case["files"]), f"{case['id']}: files must be string array")
        require(case["files"] == [], f"{case['id']}: expected self-contained prompt with no file dependencies")
        expectations = case["expectations"]
        require(isinstance(expectations, list) and 3 <= len(expectations) <= 5, f"{case['id']}: expected 3-5 behavioral expectations")
        require(all(isinstance(item, str) and item.strip() for item in expectations), f"{case['id']}: invalid expectation")
    require(set(trigger_doc) == {"skill_name", "cases"} and trigger_doc["skill_name"] == "blast-radius-review", "invalid trigger-evals top-level schema")
    cases = trigger_doc["cases"]
    require(isinstance(cases, list) and len(cases) >= 6, "expected positive and negative trigger examples")
    seen_queries = set()
    values = set()
    for index, case in enumerate(cases, 1):
        require(set(case) == {"query", "should_trigger"}, f"trigger case {index}: invalid keys")
        require(isinstance(case["query"], str) and case["query"].strip(), f"trigger case {index}: empty query")
        require(case["query"] not in seen_queries, f"trigger case {index}: duplicate query")
        require(type(case["should_trigger"]) is bool, f"trigger case {index}: should_trigger must be boolean")
        seen_queries.add(case["query"])
        values.add(case["should_trigger"])
    require(values == {True, False}, "trigger evals must include positive and negative examples")
    return eval_doc


def summarize_runs(eval_doc, run_path):
    runs = load_json(run_path)
    require(isinstance(runs, list), "run results must be a JSON array")
    by_id = {case["id"]: case for case in eval_doc["evals"]}
    require(len(runs) == len(by_id), "run results must contain exactly one record per eval")
    seen = set()
    total = passed = cases_passed = 0
    for row in runs:
        require(isinstance(row, dict) and set(row) == {"id", "output", "expectation_results"}, "run record must contain id, output, expectation_results")
        case_id = row["id"]
        require(type(case_id) is int and case_id in by_id and case_id not in seen, f"unknown or duplicate run id: {case_id}")
        seen.add(case_id)
        require(isinstance(row["output"], str), f"{case_id}: output must be a string")
        checks = row["expectation_results"]
        require(isinstance(checks, list) and len(checks) == len(by_id[case_id]["expectations"]), f"{case_id}: grader results must match expectation count")
        require(all(type(result) is bool for result in checks), f"{case_id}: expectation results must be booleans")
        case_pass = all(checks)
        cases_passed += case_pass
        total += len(checks)
        passed += sum(checks)
        print(f"{case_id}: {'PASS' if case_pass else 'FAIL'} ({sum(checks)}/{len(checks)} expectations)")
    print(f"Summary: {cases_passed}/{len(by_id)} cases pass; {passed}/{total} expectations pass")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, help="optional JSON of post-run human grader results")
    args = parser.parse_args()
    try:
        eval_doc = validate()
        print(f"Validated {len(eval_doc['evals'])} behavioral evals and trigger examples.")
        if args.runs:
            summarize_runs(eval_doc, args.runs)
    except ValueError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

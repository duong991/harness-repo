#!/usr/bin/env python3
"""Validate the repository's executable SDLC/Harness contract."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
BASE_DIR = ROOT / ".harness-core" / "base"
MANIFEST_PATH = ROOT / ".harness-core" / "manifest.json"
ROUTER_PATH = SKILLS_DIR / "work-router" / "SKILL.md"
SKILLS = (
    "work-router", "grill-me", "diagnosing-bugs", "tdd", "code-review",
    "implementation-walkthrough", "test-walkthrough", "verification-before-completion",
)
WORK_TYPES = (
    "read-only-analysis", "tiny-fix", "bounded-change", "ambiguous-product-change",
    "multi-session-initiative", "orchestrated-multi-agent-work",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.split())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(relative_path: str) -> object:
    return json.loads(read(ROOT / relative_path))


def validate_managed_skills(errors: list[str]) -> None:
    manifest = json.loads(read(MANIFEST_PATH))
    entries = {item["path"]: item["upstream_sha256"] for item in manifest["files"]}
    for skill in SKILLS:
        files = sorted(path for path in (SKILLS_DIR / skill).rglob("*") if path.is_file())
        if not files:
            errors.append(f"missing installed skill: {skill}")
        for live_path in files:
            relative = live_path.relative_to(ROOT).as_posix()
            base_path = BASE_DIR / relative
            if relative not in entries:
                errors.append(f"manifest does not own {relative}")
            elif not base_path.is_file():
                errors.append(f"missing base snapshot for {relative}")
            elif sha256(live_path) != sha256(base_path):
                errors.append(f"installed/base drift for {relative}")
            elif entries[relative] != sha256(base_path):
                errors.append(f"manifest hash mismatch for {relative}")


def validate_routing_contract(errors: list[str]) -> None:
    router = read(ROUTER_PATH)
    for work_type in WORK_TYPES:
        if work_type not in router:
            errors.append(f"router is missing work type {work_type}")
    cases = load_json("tests/harness/routing-cases.json")
    expected_ids = {
        "large-change-comprehension", "test-comprehension", "test-adequacy-review",
        "large-change-findings", "one-line-bug", "review-only",
    }
    if {case["id"] for case in cases} != expected_ids:
        errors.append("routing fixture IDs do not match the required contract")
    for case in cases:
        if case["work_type"] not in WORK_TYPES:
            errors.append(f"unknown work type in routing case {case['id']}")
        for skill in case["skills"]:
            skill_path = SKILLS_DIR / skill / "SKILL.md"
            if not skill_path.is_file():
                errors.append(f"routing case {case['id']} references missing skill {skill}")
                continue
            content = normalized(read(skill_path))
            for text in case["assertions"].get(skill, []):
                if normalized(text) not in content:
                    errors.append(f"routing case {case['id']} lost assertion in {skill}: {text}")


def validate_boundaries(errors: list[str]) -> None:
    for boundary in load_json("tests/harness/skill-boundaries.json"):
        content = normalized(read(SKILLS_DIR / boundary["skill"] / "SKILL.md"))
        for text in boundary["must_contain"]:
            if normalized(text) not in content:
                errors.append(f"boundary missing from {boundary['skill']}: {text}")


def validate_ownership_docs(errors: list[str]) -> None:
    agents = read(ROOT / "AGENTS.md")
    workflow = read(ROOT / "docs" / "WORKFLOW.md")
    guide = read(ROOT / "docs" / "HARNESS_WORKFLOW_GUIDE.md")
    if "It owns the work-type taxonomy and downstream routing table" not in normalized(agents):
        errors.append("AGENTS.md does not delegate taxonomy ownership to work-router")
    if "- read-only-analysis" in agents:
        errors.append("AGENTS.md duplicates the router taxonomy")
    if "`work-router` owns the work-type taxonomy" not in normalized(workflow):
        errors.append("WORKFLOW.md does not state taxonomy ownership")
    if "Guide này không lặp taxonomy đó" not in guide:
        errors.append("human guide duplicates routing taxonomy")
    if "`SOURCE.md` ghi lại provenance, không phải update mechanism" not in normalized(guide):
        errors.append("guide does not distinguish provenance from updater ownership")


def validate_three_way_update(errors: list[str]) -> None:
    """Exercise the non-conflicting three-way merge contract used by the updater."""
    for case in load_json("tests/harness/update-cases.json"):
        with tempfile.TemporaryDirectory(prefix="harness-update-") as directory:
            root = Path(directory)
            local = root / "local"
            base = root / "base"
            upstream = root / "upstream"
            local.write_text(case["local"], encoding="utf-8")
            base.write_text(case["base"], encoding="utf-8")
            upstream.write_text(case["upstream"], encoding="utf-8")
            result = subprocess.run(
                ["git", "merge-file", "-p", str(local), str(base), str(upstream)],
                text=True,
                capture_output=True,
                check=False,
            )
        if result.returncode != 0:
            errors.append(
                f"three-way update case failed: {case['id']}: "
                f"stdout={result.stdout.strip()!r} stderr={result.stderr.strip()!r}"
            )
            continue
        for expected in case["must_include"]:
            if expected not in result.stdout:
                errors.append(f"three-way update case lost {expected}: {case['id']}")


def main() -> int:
    errors: list[str] = []
    validate_managed_skills(errors)
    validate_routing_contract(errors)
    validate_boundaries(errors)
    validate_ownership_docs(errors)
    validate_three_way_update(errors)
    if errors:
        print("Harness SDLC validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Harness SDLC validation passed: managed skills, routing, boundaries, ownership docs, and three-way updates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

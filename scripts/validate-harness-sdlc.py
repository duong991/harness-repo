#!/usr/bin/env python3
"""Validate the repository's executable SDLC/Harness contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
BASE_DIR = ROOT / ".harness-core" / "base"
MANIFEST_PATH = ROOT / ".harness-core" / "manifest.json"
CLAUDE_SKILLS_DIR = ROOT / ".claude" / "skills"
ROUTER_PATH = SKILLS_DIR / "work-router" / "SKILL.md"
WORKFLOW_SKILLS = (
    "work-router", "grill-me", "diagnosing-bugs", "tdd", "code-review",
    "implementation-walkthrough", "test-walkthrough", "verification-before-completion",
)
SUPPORTING_SKILLS = (
    "writing-for-agents", "handoff", "codebase-design", "domain-modeling",
    "prototype", "resolving-merge-conflicts", "minimal-implementation", "teach",
    "encode-invariant", "improve-harness", "grill-with-docs", "improve-codebase-architecture",
    "system-log-tracer",
)
MANAGED_SKILLS = WORKFLOW_SKILLS + SUPPORTING_SKILLS
MANAGED_ASSETS = (
    "docs/HARNESS_WORKFLOW_GUIDE.md",
    "scripts/test-harness-skills",
    "scripts/sync-harness-source.py",
    "scripts/link-claude-skills.py",
    "scripts/validate-harness-sdlc.py",
    "tests/harness/routing-cases.json",
    "tests/harness/skill-boundaries.json",
    "tests/harness/update-cases.json",
    "tests/harness/test-sync-harness-source.py",
    "tests/harness/test-system-log-tracer.py",
)
MANAGED_EXECUTABLES = (
    "scripts/test-harness-skills",
    "scripts/sync-harness-source.py",
    "scripts/link-claude-skills.py",
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


def validate_managed_skills(errors: list[str], require_pristine_baseline: bool) -> None:
    manifest = json.loads(read(MANIFEST_PATH))
    entries = {item["path"]: item["upstream_sha256"] for item in manifest["files"]}
    for skill in MANAGED_SKILLS:
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
            elif require_pristine_baseline and sha256(live_path) != sha256(base_path):
                errors.append(f"installed/base drift for {relative}")
            elif entries[relative] != sha256(base_path):
                errors.append(f"manifest hash mismatch for {relative}")


def validate_managed_assets(errors: list[str], require_pristine_baseline: bool) -> None:
    manifest = json.loads(read(MANIFEST_PATH))
    entries = {item["path"]: item["upstream_sha256"] for item in manifest["files"]}
    for relative in MANAGED_ASSETS:
        live_path = ROOT / relative
        base_path = BASE_DIR / relative
        if relative not in entries:
            errors.append(f"manifest does not own managed asset {relative}")
        elif not live_path.is_file():
            errors.append(f"missing managed asset {relative}")
        elif not base_path.is_file():
            errors.append(f"missing base snapshot for managed asset {relative}")
        elif require_pristine_baseline and sha256(live_path) != sha256(base_path):
            errors.append(f"installed/base drift for managed asset {relative}")
        elif entries[relative] != sha256(base_path):
            errors.append(f"manifest hash mismatch for managed asset {relative}")


def validate_manifest_entries(errors: list[str], require_pristine_baseline: bool) -> None:
    """Validate updater baselines while allowing normal consumer customizations."""
    manifest = json.loads(read(MANIFEST_PATH))
    for entry in manifest["files"]:
        relative = entry["path"]
        live_path = ROOT / relative
        base_path = BASE_DIR / relative
        if not live_path.is_file():
            errors.append(f"missing manifest-owned live file {relative}")
        elif not base_path.is_file():
            errors.append(f"missing manifest-owned base snapshot {relative}")
        elif require_pristine_baseline and sha256(live_path) != sha256(base_path):
            errors.append(f"manifest-owned installed/base drift for {relative}")
        elif entry["upstream_sha256"] != sha256(base_path):
            errors.append(f"manifest-owned hash mismatch for {relative}")


def validate_managed_executables(errors: list[str], require_pristine_baseline: bool) -> None:
    if os.name == "nt":
        return
    for relative in MANAGED_EXECUTABLES:
        live_path = ROOT / relative
        base_path = BASE_DIR / relative
        if live_path.is_file() and not os.access(live_path, os.X_OK):
            errors.append(f"managed executable is not executable: {relative}")
        if require_pristine_baseline and base_path.is_file() and not os.access(base_path, os.X_OK):
            errors.append(f"baseline executable is not executable: {relative}")


def validate_claude_skill_links(errors: list[str]) -> None:
    """Every managed skill must be exposed to Claude Code via `.claude/skills/<skill>`."""
    expected_root = SKILLS_DIR.resolve()
    for skill in MANAGED_SKILLS:
        link = CLAUDE_SKILLS_DIR / skill
        if not link.is_symlink():
            errors.append(f"missing Claude skill link .claude/skills/{skill} (run scripts/link-claude-skills.py)")
        elif link.resolve() != expected_root / skill:
            errors.append(f"Claude skill link .claude/skills/{skill} does not point to .agents/skills/{skill}")


def validate_routing_contract(errors: list[str]) -> None:
    router = read(ROUTER_PATH)
    for work_type in WORK_TYPES:
        if work_type not in router:
            errors.append(f"router is missing work type {work_type}")
    cases = load_json("tests/harness/routing-cases.json")
    expected_ids = {
        "large-change-comprehension", "test-comprehension", "test-adequacy-review",
        "large-change-findings", "one-line-bug", "review-only",
        "agent-document-maintenance", "design-analysis", "domain-modeling",
        "merge-conflict-resolution", "prototype-ui-exploration",
        "prototype-logic-exploration", "prototype-full-stack-implications",
        "settled-design-no-prototype", "settled-api-no-prototype",
        "bounded-implementation-minimalism", "avoid-unnecessary-dependency",
        "accepted-design-preserved", "runtime-log-evidence",
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
        policy = boundary.get("policy")
        if policy:
            policy_path = SKILLS_DIR / boundary["skill"] / "agents" / "openai.yaml"
            if not policy_path.is_file():
                errors.append(f"missing invocation policy for {boundary['skill']}")
            elif normalized(policy) not in normalized(read(policy_path)):
                errors.append(f"policy missing from {boundary['skill']}: {policy}")


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


def merge_update_case(case: dict[str, object]) -> tuple[bool, str]:
    """Model the updater's file-level three-way contract without mutating a consumer."""
    base = case["base"]
    local = case["local"]
    upstream = case["upstream"]
    if base is None:
        if local is None:
            return False, upstream or ""
        if local == upstream:
            return False, local
        return True, f"<<<<<<< local\n{local}=======\n{upstream or ''}>>>>>>> upstream\n"
    if upstream is None:
        if local == base:
            return False, ""
        return True, f"<<<<<<< local\n{local}=======\n(deleted upstream)\n>>>>>>> upstream\n"
    if local is None:
        return (False, upstream) if upstream == base else (True, "")
    if local == base:
        return False, upstream
    if upstream == base:
        return False, local

    with tempfile.TemporaryDirectory(prefix="harness-update-") as directory:
        root = Path(directory)
        local_path = root / "local"
        base_path = root / "base"
        upstream_path = root / "upstream"
        local_path.write_text(local, encoding="utf-8")
        base_path.write_text(base, encoding="utf-8")
        upstream_path.write_text(upstream, encoding="utf-8")
        result = subprocess.run(
            ["git", "merge-file", "-p", str(local_path), str(base_path), str(upstream_path)],
            text=True,
            capture_output=True,
            check=False,
        )
    return result.returncode != 0, result.stdout


def validate_three_way_merge_contract_model(errors: list[str]) -> None:
    """Exercise the file-level merge model; real updater behavior needs E2E proof."""
    expected_ids = {
        "upstream-only-modification", "local-only-modification",
        "preserve-local-and-apply-upstream", "conflicting-modification",
        "upstream-adds-managed-file", "upstream-deletes-managed-file",
        "local-modification-upstream-deletion",
    }
    cases = load_json("tests/harness/update-cases.json")
    if {case["id"] for case in cases} != expected_ids:
        errors.append("update fixture IDs do not match the required contract")
    for case in load_json("tests/harness/update-cases.json"):
        conflict, output = merge_update_case(case)
        if conflict != case["expect_conflict"]:
            errors.append(f"three-way update conflict result changed: {case['id']}")
            continue
        if conflict:
            if case["local"] not in output:
                errors.append(f"conflicting update lost recoverable local state: {case['id']}")
            if "<<<<<<<" not in output:
                errors.append(f"conflicting update did not surface a conflict: {case['id']}")
        for expected in case["must_include"]:
            if expected not in output:
                errors.append(f"three-way update case lost {expected}: {case['id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-pristine-baseline",
        action="store_true",
        help="require every managed live file to equal its release baseline",
    )
    args = parser.parse_args()
    errors: list[str] = []
    validate_managed_skills(errors, args.require_pristine_baseline)
    validate_managed_assets(errors, args.require_pristine_baseline)
    validate_manifest_entries(errors, args.require_pristine_baseline)
    validate_managed_executables(errors, args.require_pristine_baseline)
    validate_claude_skill_links(errors)
    validate_routing_contract(errors)
    validate_boundaries(errors)
    validate_ownership_docs(errors)
    validate_three_way_merge_contract_model(errors)
    if errors:
        print("Harness SDLC validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    mode = "pristine release baseline" if args.require_pristine_baseline else "consumer customization"
    print(f"Harness SDLC validation passed ({mode}): managed skills and assets, Claude skill links, routing, boundaries, ownership docs, and three-way merge contract model.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

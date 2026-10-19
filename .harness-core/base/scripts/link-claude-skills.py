#!/usr/bin/env python3
"""Expose `.agents/skills/*` to Claude Code through `.claude/skills/*` symlinks.

`.agents/skills/` stays the single source of truth. Each skill directory that
contains a `SKILL.md` gets a relative symlink `.claude/skills/<name>` pointing at
`../../.agents/skills/<name>`. Stale symlinks that point into `.agents/skills/`
are removed; real directories and foreign links in `.claude/skills/` are never
touched.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source_skills(root: Path) -> list[str]:
    skills_dir = root / ".agents" / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        path.name
        for path in skills_dir.iterdir()
        if path.is_dir() and not path.is_symlink() and (path / "SKILL.md").is_file()
    )


def expected_target(name: str) -> str:
    return os.path.join("..", "..", ".agents", "skills", name)


def points_into_agents(link: Path) -> bool:
    return os.readlink(link).replace("\\", "/").startswith("../../.agents/skills/")


def plan(root: Path) -> tuple[list[str], list[str], list[str]]:
    """Return (missing-or-wrong links to create, stale links to remove, conflicts)."""
    claude_dir = root / ".claude" / "skills"
    skills = source_skills(root)
    create: list[str] = []
    remove: list[str] = []
    conflicts: list[str] = []
    for name in skills:
        link = claude_dir / name
        if link.is_symlink():
            if os.readlink(link) != expected_target(name):
                if points_into_agents(link):
                    create.append(name)
                else:
                    conflicts.append(f".claude/skills/{name} is a foreign symlink")
        elif link.exists():
            conflicts.append(f".claude/skills/{name} exists and is not a symlink")
        else:
            create.append(name)
    if claude_dir.is_dir():
        for link in sorted(claude_dir.iterdir()):
            if link.is_symlink() and link.name not in skills and points_into_agents(link):
                remove.append(link.name)
    return create, remove, conflicts


def apply(root: Path, create: list[str], remove: list[str]) -> None:
    claude_dir = root / ".claude" / "skills"
    claude_dir.mkdir(parents=True, exist_ok=True)
    for name in remove:
        (claude_dir / name).unlink()
    for name in create:
        link = claude_dir / name
        if link.is_symlink():
            link.unlink()
        link.symlink_to(expected_target(name), target_is_directory=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--check", action="store_true", help="report drift without changing files")
    args = parser.parse_args()
    root = args.root.resolve()

    create, remove, conflicts = plan(root)
    for conflict in conflicts:
        print(f"CONFLICT {conflict}", file=sys.stderr)
    if args.check:
        for name in create:
            print(f"missing link .claude/skills/{name}", file=sys.stderr)
        for name in remove:
            print(f"stale link .claude/skills/{name}", file=sys.stderr)
        if create or remove or conflicts:
            print("Claude skill links are out of sync; run scripts/link-claude-skills.py", file=sys.stderr)
            return 1
        print(f"Claude skill links in sync ({len(source_skills(root))} skills).")
        return 0
    if conflicts:
        return 2
    apply(root, create, remove)
    print(
        f"Claude skill links synced: {len(create)} linked, {len(remove)} pruned, "
        f"{len(source_skills(root))} total."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

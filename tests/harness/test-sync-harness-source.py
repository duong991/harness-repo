#!/usr/bin/env python3
"""Integration contract for the local-source Harness migration bridge."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts" / "sync-harness-source.py"


def write(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def manifest(root: Path, files: dict[str, str]) -> None:
    entries = []
    for relative, content in files.items():
        write(root / ".harness-core" / "base" / relative, content)
        write(root / relative, content)
        entries.append({"path": relative, "upstream_sha256": hashlib.sha256(content.encode()).hexdigest()})
    write(root / ".harness-core" / "manifest.json", json.dumps({"schema_version": 1, "core_version": "test", "files": entries}) + "\n")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="harness-source-sync-test-") as directory:
        root = Path(directory)
        source = root / "source"
        target = root / "target"
        write(source / "scripts" / "test-harness-skills", "#!/usr/bin/env bash\nexit 0\n", executable=True)
        write(
            source / "scripts" / "link-claude-skills.py",
            (ROOT / "scripts" / "link-claude-skills.py").read_text(encoding="utf-8"),
            executable=True,
        )
        manifest(
            source,
            {
                "managed.txt": "one=new\nstable=1\nkeep=1\n",
                "conflict.txt": "state=source\n",
                "legacy.txt": "legacy=new\n",
            },
        )
        write(target / ".git", "gitdir: synthetic\n")
        manifest(
            target,
            {
                "managed.txt": "one=old\nstable=1\nkeep=1\n",
                "conflict.txt": "state=base\n",
            },
        )
        write(target / "managed.txt", "one=old\nstable=1\nkeep=local\n")
        write(target / "conflict.txt", "state=target\n")
        write(target / "legacy.txt", "legacy=local\n")
        write(target / ".agents" / "skills" / "demo" / "SKILL.md", "---\nname: demo\n---\n")
        (target / ".claude" / "skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/removed", target / ".claude" / "skills" / "removed")

        blocked = subprocess.run(
            [str(TOOL), "--source", str(source), "--target", str(target)],
            text=True,
            capture_output=True,
            check=False,
        )
        if blocked.returncode != 2 or "legacy path has no merge base" not in blocked.stderr:
            raise AssertionError(f"expected legacy refusal, got {blocked.returncode}: {blocked.stderr}")
        merge_blocked = subprocess.run(
            [str(TOOL), "--source", str(source), "--target", str(target), "--adopt-legacy"],
            text=True,
            capture_output=True,
            check=False,
        )
        if merge_blocked.returncode != 2 or "three-way merge conflict: conflict.txt" not in merge_blocked.stderr:
            raise AssertionError(f"expected merge conflict, got {merge_blocked.returncode}: {merge_blocked.stderr}")
        applied = subprocess.run(
            [
                str(TOOL),
                "--source",
                str(source),
                "--target",
                str(target),
                "--adopt-legacy",
                "--replace-conflict",
                "conflict.txt",
                "--apply",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if applied.returncode:
            raise AssertionError(f"migration failed: {applied.stdout}\n{applied.stderr}")
        if (target / "managed.txt").read_text() != "one=new\nstable=1\nkeep=local\n":
            raise AssertionError("three-way merge did not preserve the local change")
        if (target / "conflict.txt").read_text() != "state=source\n":
            raise AssertionError("explicit conflict replacement did not install source content")
        if (target / "legacy.txt").read_text() != "legacy=new\n":
            raise AssertionError("authorized legacy adoption did not install source content")
        migrated = json.loads((target / ".harness-core" / "manifest.json").read_text())
        if len(migrated["files"]) != 3:
            raise AssertionError("target manifest was not replaced by source manifest")
        if not list((target / ".harness-core" / "source-sync-backups").iterdir()):
            raise AssertionError("migration did not retain a recoverable backup")
        demo_link = target / ".claude" / "skills" / "demo"
        if not demo_link.is_symlink() or not (demo_link / "SKILL.md").is_file():
            raise AssertionError("migration did not link target skills into .claude/skills")
        if (target / ".claude" / "skills" / "removed").is_symlink():
            raise AssertionError("migration did not prune a stale Claude skill link")
    print(
        "Harness source sync integration passed: refusal, merge, explicit replacement, "
        "legacy adoption, backup, and Claude skill links."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

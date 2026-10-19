#!/usr/bin/env python3
"""Synchronize a verified local Harness source tree into a consumer repository.

This is a developer migration bridge for an unpublished Harness baseline. It is
not a replacement for the immutable-release updater: it uses the consumer's
existing base snapshots for three-way merges and copies the source baseline only
after every operation is conflict-free.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Operation:
    path: str
    action: str
    content: bytes | None
    reason: str


def fail(message: str) -> None:
    raise RuntimeError(message)


def safe_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not relative:
        fail(f"unsafe manifest path: {relative!r}")
    return path


def read_manifest(root: Path) -> tuple[dict[str, object], dict[str, str]]:
    path = root / ".harness-core" / "manifest.json"
    if not path.is_file():
        fail(f"missing Harness manifest: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries: dict[str, str] = {}
    for entry in manifest.get("files", []):
        relative = entry.get("path")
        digest = entry.get("upstream_sha256")
        if not isinstance(relative, str) or not isinstance(digest, str):
            fail(f"invalid manifest entry in {path}")
        safe_path(relative)
        if relative in entries:
            fail(f"duplicate manifest path in {path}: {relative}")
        entries[relative] = digest
    return manifest, entries


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_source(source: Path) -> tuple[dict[str, object], dict[str, str]]:
    validator = source / "scripts" / "test-harness-skills"
    if not validator.is_file():
        fail(f"source validation command is missing: {validator}")
    result = subprocess.run([str(validator), "--release-baseline"], cwd=source, check=False)
    if result.returncode:
        fail("source does not pass pristine release-baseline validation")
    manifest, entries = read_manifest(source)
    for relative, expected in entries.items():
        base = source / ".harness-core" / "base" / safe_path(relative)
        live = source / safe_path(relative)
        if not base.is_file() or not live.is_file():
            fail(f"source managed path is missing: {relative}")
        if sha256(base) != expected or sha256(live) != expected:
            fail(f"source manifest/base/live mismatch: {relative}")
    return manifest, entries


def three_way(local: bytes, base: bytes, upstream: bytes) -> tuple[bytes | None, str]:
    if local == base:
        return upstream, "update"
    if upstream == base:
        return local, "preserve-local"
    with tempfile.TemporaryDirectory(prefix="harness-source-sync-") as directory:
        root = Path(directory)
        local_path = root / "local"
        base_path = root / "base"
        upstream_path = root / "upstream"
        local_path.write_bytes(local)
        base_path.write_bytes(base)
        upstream_path.write_bytes(upstream)
        result = subprocess.run(
            ["git", "merge-file", "-p", str(local_path), str(base_path), str(upstream_path)],
            capture_output=True,
            check=False,
        )
    if result.returncode == 0:
        return result.stdout, "merge"
    if result.returncode == 1:
        return None, "conflict"
    fail(f"git merge-file failed: {result.stderr.decode(errors='replace').strip()}")


def plan_sync(
    source: Path,
    target: Path,
    source_entries: dict[str, str],
    target_entries: dict[str, str],
    adopt_legacy: bool,
    replace_conflicts: set[str],
) -> tuple[list[Operation], list[str], list[str]]:
    operations: list[Operation] = []
    conflicts: list[str] = []
    retained: list[str] = []
    for relative in sorted(source_entries):
        path = safe_path(relative)
        upstream = (source / ".harness-core" / "base" / path).read_bytes()
        target_live = target / path
        if relative not in target_entries:
            if not target_live.exists():
                operations.append(Operation(relative, "create", upstream, "new managed path"))
            elif target_live.is_file() and target_live.read_bytes() == upstream:
                operations.append(Operation(relative, "adopt", None, "legacy file already matches source"))
            elif adopt_legacy:
                operations.append(Operation(relative, "replace-legacy", upstream, "legacy path has no merge base"))
            else:
                conflicts.append(f"legacy path has no merge base: {relative}")
            continue

        target_base = target / ".harness-core" / "base" / path
        if not target_base.is_file():
            conflicts.append(f"target manifest path has no base snapshot: {relative}")
        elif not target_live.is_file():
            conflicts.append(f"target manifest path is missing live file: {relative}")
        else:
            merged, action = three_way(target_live.read_bytes(), target_base.read_bytes(), upstream)
            if merged is None:
                if relative in replace_conflicts:
                    operations.append(
                        Operation(
                            relative,
                            "replace-conflict",
                            upstream,
                            "explicit source preference after three-way merge conflict",
                        )
                    )
                else:
                    conflicts.append(f"three-way merge conflict: {relative}")
            else:
                operations.append(Operation(relative, action, merged, "target base → source base"))

    for relative in sorted(set(target_entries) - set(source_entries)):
        retained.append(relative)
    return operations, conflicts, retained


def copy_atomic(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.harness-sync")
    shutil.copy2(source, temporary)
    temporary.replace(destination)


def write_atomic(destination: Path, content: bytes, mode_source: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.harness-sync")
    temporary.write_bytes(content)
    shutil.copymode(mode_source, temporary)
    temporary.replace(destination)


def backup_existing(target: Path, paths: set[Path]) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = target / ".harness-core" / "source-sync-backups" / stamp
    for path in sorted(paths):
        if path.is_file():
            destination = backup / path.relative_to(target)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    return backup


def apply_sync(
    source: Path,
    target: Path,
    source_manifest: dict[str, object],
    source_entries: dict[str, str],
    operations: list[Operation],
) -> Path:
    backup_paths = {target / ".harness-core" / "manifest.json"}
    for operation in operations:
        if operation.content is not None:
            backup_paths.add(target / safe_path(operation.path))
    for relative in source_entries:
        backup_paths.add(target / ".harness-core" / "base" / safe_path(relative))
    backup = backup_existing(target, backup_paths)

    for operation in operations:
        if operation.content is not None:
            write_atomic(target / safe_path(operation.path), operation.content, source / safe_path(operation.path))
    for relative in source_entries:
        path = safe_path(relative)
        copy_atomic(source / ".harness-core" / "base" / path, target / ".harness-core" / "base" / path)
    manifest_path = target / ".harness-core" / "manifest.json"
    temporary = manifest_path.with_name(".manifest.json.harness-sync")
    temporary.write_text(json.dumps(source_manifest, indent=2) + "\n", encoding="utf-8")
    shutil.copymode(source / ".harness-core" / "manifest.json", temporary)
    temporary.replace(manifest_path)
    return backup


def link_claude_skills(source: Path, target: Path) -> None:
    """Expose the target's `.agents/skills` to Claude Code via `.claude/skills` symlinks."""
    linker = source / "scripts" / "link-claude-skills.py"
    if not linker.is_file():
        print(f"skip-claude-links (source has no {linker.name})")
        return
    result = subprocess.run([sys.executable, str(linker), "--root", str(target)], check=False)
    if result.returncode:
        fail("Claude skill link sync reported conflicts in target .claude/skills")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="consumer repository root")
    parser.add_argument("--source", type=Path, default=ROOT, help="Harness source root")
    parser.add_argument("--apply", action="store_true", help="write the planned migration")
    parser.add_argument(
        "--adopt-legacy",
        action="store_true",
        help="backup and replace unmanaged legacy Harness files that differ from source",
    )
    parser.add_argument(
        "--replace-conflict",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "for this manifest-tracked path only, replace a three-way merge conflict with "
            "the source version; the target version is retained in the migration backup"
        ),
    )
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    replace_conflicts = set(args.replace_conflict)
    for relative in replace_conflicts:
        safe_path(relative)
    if source == target:
        fail("source and target must be different repositories")
    if not (target / ".git").exists():
        fail(f"target is not a Git repository root: {target}")

    source_manifest, source_entries = validate_source(source)
    _, target_entries = read_manifest(target)
    operations, conflicts, retained = plan_sync(
        source,
        target,
        source_entries,
        target_entries,
        args.adopt_legacy,
        replace_conflicts,
    )
    print(f"Harness source: {source} ({len(source_entries)} managed files)")
    print(f"Consumer target: {target} ({len(target_entries)} managed files before sync)")
    for operation in operations:
        print(f"{operation.action:15} {operation.path} ({operation.reason})")
    for relative in retained:
        print(f"retain-legacy   {relative} (not deleted by source migration)")
    for conflict in conflicts:
        print(f"CONFLICT {conflict}", file=sys.stderr)
    if conflicts:
        print(
            "No files changed. Resolve conflicts or rerun with --adopt-legacy or "
            "--replace-conflict PATH when the overwrite is authorized.",
            file=sys.stderr,
        )
        return 2
    if not args.apply:
        print("Dry-run complete. Re-run with --apply to write this migration.")
        return 0
    backup = apply_sync(source, target, source_manifest, source_entries, operations)
    print(f"Applied {len(operations)} operations. Backup: {backup}")
    link_claude_skills(source, target)
    print("No target files were staged or committed. Run target validation and review its Git diff before committing.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Harness source sync failed: {error}", file=sys.stderr)
        raise SystemExit(1)

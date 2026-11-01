#!/usr/bin/env python3
"""Synchronize agent skills between a canonical source repository and consumer repositories.

The source repository acts as the authoritative source of trust for skills.
This script provides inspection (scan), structured JSON output, selective syncing,
pruning of obsolete skills, automatic backups, and Claude Code symlink maintenance.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_NAMES = {".DS_Store", "__pycache__", ".git"}
EXCLUDED_EXTS = {".pyc", ".pyo", ".swp"}


@dataclass
class FileDiff:
    relative_path: str
    status: str  # "added_in_source", "modified", "only_in_target"


@dataclass
class SkillComparison:
    name: str
    status: str  # "IN_SYNC", "SOURCE_ONLY", "DIVERGED", "TARGET_ONLY"
    description: str = ""
    source_files_count: int = 0
    target_files_count: int = 0
    diverged_files: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ClaudeLinkStatus:
    name: str
    exists: bool
    is_symlink: bool
    target: str | None
    valid: bool


@dataclass
class ScanReport:
    source_root: str
    target_root: str
    source_skills_count: int
    target_skills_count: int
    in_sync: list[SkillComparison] = field(default_factory=list)
    source_only: list[SkillComparison] = field(default_factory=list)
    diverged: list[SkillComparison] = field(default_factory=list)
    target_only: list[SkillComparison] = field(default_factory=list)
    claude_links_ok: bool = True
    claude_links_issues: list[str] = field(default_factory=list)


def fail(message: str) -> None:
    raise RuntimeError(message)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def read_skill_description(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return ""
    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    # Check YAML frontmatter description
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                line = line.strip()
                if line.startswith("description:"):
                    desc = line.split("description:", 1)[1].strip().strip("\"'")
                    if desc:
                        return desc[:120]

    # Fallback to first non-heading paragraph
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
            return stripped[:120]
    return ""


def get_skill_files(skill_dir: Path) -> dict[str, str]:
    """Return relative_path -> sha256 for all relevant files in a skill directory."""
    files: dict[str, str] = {}
    if not skill_dir.is_dir():
        return files
    for root, dirs, filenames in os.walk(skill_dir):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_NAMES]
        for fname in filenames:
            if fname in EXCLUDED_NAMES or any(fname.endswith(ext) for ext in EXCLUDED_EXTS):
                continue
            full_path = Path(root) / fname
            if full_path.is_file() and not full_path.is_symlink():
                rel_path = str(full_path.relative_to(skill_dir)).replace("\\", "/")
                files[rel_path] = file_sha256(full_path)
    return files


def collect_skills(repo_root: Path) -> dict[str, Path]:
    """Find all valid skill directories under .agents/skills/."""
    skills_dir = repo_root / ".agents" / "skills"
    if not skills_dir.is_dir():
        return {}
    skills: dict[str, Path] = {}
    for entry in sorted(skills_dir.iterdir()):
        if entry.is_dir() and not entry.is_symlink() and (entry / "SKILL.md").is_file():
            skills[entry.name] = entry
    return skills


def compare_skill(name: str, source_dir: Path | None, target_dir: Path | None) -> SkillComparison:
    if source_dir is not None and target_dir is None:
        desc = read_skill_description(source_dir)
        files = get_skill_files(source_dir)
        return SkillComparison(
            name=name,
            status="SOURCE_ONLY",
            description=desc,
            source_files_count=len(files),
            target_files_count=0,
            recommendation="Thêm mới từ chuẩn (Missing in target)",
        )
    if source_dir is None and target_dir is not None:
        desc = read_skill_description(target_dir)
        files = get_skill_files(target_dir)
        return SkillComparison(
            name=name,
            status="TARGET_ONLY",
            description=desc,
            source_files_count=0,
            target_files_count=len(files),
            recommendation="Kỹ năng riêng của target hoặc đã xoá ở source",
        )
    assert source_dir is not None and target_dir is not None
    desc = read_skill_description(source_dir) or read_skill_description(target_dir)
    source_files = get_skill_files(source_dir)
    target_files = get_skill_files(target_dir)

    all_keys = sorted(set(source_files) | set(target_files))
    diverged: list[str] = []
    for k in all_keys:
        if k not in target_files:
            diverged.append(f"+ {k}")
        elif k not in source_files:
            diverged.append(f"- {k}")
        elif source_files[k] != target_files[k]:
            diverged.append(f"~ {k}")

    if not diverged:
        return SkillComparison(
            name=name,
            status="IN_SYNC",
            description=desc,
            source_files_count=len(source_files),
            target_files_count=len(target_files),
            recommendation="Đã đồng bộ (In sync)",
        )
    return SkillComparison(
        name=name,
        status="DIVERGED",
        description=desc,
        source_files_count=len(source_files),
        target_files_count=len(target_files),
        diverged_files=diverged,
        recommendation=f"Cập nhật nội dung khác biệt ({len(diverged)} files)",
    )


def check_claude_links(repo_root: Path, expected_skills: list[str]) -> tuple[bool, list[str]]:
    claude_dir = repo_root / ".claude" / "skills"
    issues: list[str] = []
    if not claude_dir.exists():
        return False, [".claude/skills does not exist"]
    if claude_dir.is_symlink():
        return False, [f".claude/skills is a directory symlink -> {os.readlink(claude_dir)} (needs per-skill symlinks)"]
    if not claude_dir.is_dir():
        return False, [".claude/skills is not a directory"]

    for name in expected_skills:
        link = claude_dir / name
        expected_target = f"../../.agents/skills/{name}"
        if not link.exists() and not link.is_symlink():
            issues.append(f"missing link: .claude/skills/{name}")
        elif not link.is_symlink():
            issues.append(f"not a symlink: .claude/skills/{name}")
        else:
            target = os.readlink(link).replace("\\", "/")
            if target != expected_target:
                issues.append(f"wrong link target: .claude/skills/{name} -> {target} (expected {expected_target})")
    return len(issues) == 0, issues


def run_scan(source_root: Path, target_root: Path) -> ScanReport:
    source_skills = collect_skills(source_root)
    target_skills = collect_skills(target_root)
    all_names = sorted(set(source_skills) | set(target_skills))

    report = ScanReport(
        source_root=str(source_root),
        target_root=str(target_root),
        source_skills_count=len(source_skills),
        target_skills_count=len(target_skills),
    )

    for name in all_names:
        comp = compare_skill(name, source_skills.get(name), target_skills.get(name))
        if comp.status == "IN_SYNC":
            report.in_sync.append(comp)
        elif comp.status == "SOURCE_ONLY":
            report.source_only.append(comp)
        elif comp.status == "DIVERGED":
            report.diverged.append(comp)
        elif comp.status == "TARGET_ONLY":
            report.target_only.append(comp)

    ok, issues = check_claude_links(target_root, list(target_skills.keys()))
    report.claude_links_ok = ok
    report.claude_links_issues = issues
    return report


def print_scan_report(report: ScanReport) -> None:
    print(f"================================================================================")
    print(f" BÁO CÁO SCAN SO SÁNH KỸ NĂNG (SKILLS COMPARISON REPORT)")
    print(f"================================================================================")
    print(f"• Repo chuẩn (Source of Trust) : {report.source_root} ({report.source_skills_count} skills)")
    print(f"• Repo đích (Target Consumer)  : {report.target_root} ({report.target_skills_count} skills)")
    print(f"--------------------------------------------------------------------------------")

    # 1. New in source
    print(f"\n1. KỸ NĂNG MỚI TỪ CHUẨN (Cần thêm mới vào target): {len(report.source_only)}")
    if report.source_only:
        for s in report.source_only:
            desc = f" - {s.description}" if s.description else ""
            print(f"   [+] {s.name:<30} ({s.source_files_count} files){desc}")
    else:
        print("   (Không có kỹ năng mới)")

    # 2. Diverged
    print(f"\n2. KỸ NĂNG CÓ CẬP NHẬT/KHÁC BIỆT (Cần đồng bộ nội dung): {len(report.diverged)}")
    if report.diverged:
        for s in report.diverged:
            files_preview = ", ".join(s.diverged_files[:3])
            if len(s.diverged_files) > 3:
                files_preview += f" (+{len(s.diverged_files)-3} files)"
            print(f"   [~] {s.name:<30} [{files_preview}]")
    else:
        print("   (Toàn bộ kỹ năng chung đều khớp nội dung)")

    # 3. Target-only
    print(f"\n3. KỸ NĂNG RIÊNG TẠI TARGET (Consumer-local / hoặc đã gỡ ở source): {len(report.target_only)}")
    if report.target_only:
        for s in report.target_only:
            desc = f" - {s.description}" if s.description else ""
            print(f"   [?] {s.name:<30} ({s.target_files_count} files){desc}")
    else:
        print("   (Không có kỹ năng riêng ngoài chuẩn)")

    # 4. In sync
    print(f"\n4. KỸ NĂNG ĐÃ ĐỒNG BỘ CHUẨN: {len(report.in_sync)}")
    if report.in_sync:
        names = [s.name for s in report.in_sync]
        print(f"   [✓] {', '.join(names)}")

    # 5. Claude links
    print(f"\n5. TRẠNG THÁI LIÊN KẾT CLAUDE (.claude/skills/):")
    if report.claude_links_ok:
        print(f"   [✓] Tất cả symlink đều hợp lệ và trỏ đúng vào .agents/skills/")
    else:
        print(f"   [!] Phát hiện {len(report.claude_links_issues)} vấn đề về link:")
        for issue in report.claude_links_issues[:5]:
            print(f"       - {issue}")
        if len(report.claude_links_issues) > 5:
            print(f"       ... và {len(report.claude_links_issues) - 5} vấn đề khác.")

    print(f"\n================================================================================")


def backup_target(target_root: Path, skill_names: set[str]) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = target_root / ".harness-core" / "source-sync-backups" / f"skills-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    skills_dir = target_root / ".agents" / "skills"
    for name in sorted(skill_names):
        src = skills_dir / name
        if src.is_dir():
            dest = backup_dir / name
            shutil.copytree(src, dest, symlinks=True)
    return backup_dir


def copy_skill(source_dir: Path, target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir, symlinks=True)


def prune_skill(target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)


def run_claude_link_script(source_root: Path, target_root: Path) -> None:
    linker = source_root / "scripts" / "link-claude-skills.py"
    if not linker.is_file():
        linker = target_root / "scripts" / "link-claude-skills.py"
    if not linker.is_file():
        print(f"Lưu ý: Không tìm thấy scripts/link-claude-skills.py để cập nhật link Claude.")
        return

    # Check if target's .claude/skills is a directory symlink
    target_claude_skills = target_root / ".claude" / "skills"
    if target_claude_skills.is_symlink():
        print(f"Chuyển đổi {target_claude_skills} từ directory symlink thành thư mục...")
        target_claude_skills.unlink()
        target_claude_skills.mkdir(parents=True, exist_ok=True)

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    res = subprocess.run([sys.executable, str(linker), "--root", str(target_root)], env=env, check=False)
    if res.returncode == 0:
        print(f"[✓] Đã đồng bộ liên kết .claude/skills thành công.")
    else:
        print(f"[!] Link Claude báo lỗi (exit {res.returncode}).", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=None, help="Target consumer repository path")
    parser.add_argument("target_path", nargs="?", type=Path, default=None, help="Target path fallback")
    parser.add_argument("--source", type=Path, default=ROOT, help="Authoritative source repository path")
    parser.add_argument("--scan", action="store_true", help="Scan and display comparison table (dry-run)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON format")
    parser.add_argument("--apply", action="store_true", help="Execute the synchronization")
    parser.add_argument("--sync-all", action="store_true", help="Sync all skills (install new + update diverged)")
    parser.add_argument("--sync", type=str, default="", help="Comma-separated skill names to sync")
    parser.add_argument("--prune", type=str, default="", help="Comma-separated skill names to delete from target")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--skip-claude-links", action="store_true", help="Skip updating .claude/skills links")
    parser.add_argument("--validate", action="store_true", help="Run validation in target after sync")

    args = parser.parse_args()
    target_raw = args.target or args.target_path
    if not target_raw:
        fail("Missing target repository: provide --target <PATH> or <PATH>")

    source_root = args.source.resolve()
    target_root = target_raw.resolve()

    if source_root == target_root:
        fail("Source and target must be different repositories.")
    if not (target_root / ".git").exists() and not (target_root / ".agents").exists():
        fail(f"Target does not appear to be a Git repository or agent project: {target_root}")

    report = run_scan(source_root, target_root)

    if args.json:
        # Convert dataclasses to dict
        data = asdict(report)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    if not args.apply or args.scan:
        print_scan_report(report)
        if not args.apply:
            print("Chế độ kiểm tra (Dry-run). Sử dụng --apply kết hợp --sync-all hoặc --sync <name> để thực thi.\n")
            return 0

    # Determine skills to sync and prune
    skills_to_sync: set[str] = set()
    if args.sync_all:
        for s in report.source_only:
            skills_to_sync.add(s.name)
        for s in report.diverged:
            skills_to_sync.add(s.name)
    elif args.sync:
        for item in args.sync.split(","):
            item = item.strip()
            if item:
                skills_to_sync.add(item)

    skills_to_prune: set[str] = set()
    if args.prune:
        for item in args.prune.split(","):
            item = item.strip()
            if item:
                skills_to_prune.add(item)

    if not skills_to_sync and not skills_to_prune:
        print("Không có skill nào được chọn để đồng bộ hoặc xoá. Chỉ định --sync-all hoặc --sync <skills> hoặc --prune <skills>.")
        return 0

    source_skills = collect_skills(source_root)
    target_skills = collect_skills(target_root)

    # Validate requested skills
    for name in skills_to_sync:
        if name not in source_skills:
            fail(f"Skill '{name}' không tồn tại trong source repository: {source_root}")

    # Backup affected target skills
    affected_target_skills = (skills_to_sync & set(target_skills)) | (skills_to_prune & set(target_skills))
    if not args.no_backup and affected_target_skills:
        backup = backup_target(target_root, affected_target_skills)
        print(f"[✓] Đã tạo bản sao lưu tại: {backup}")

    # Apply sync
    target_skills_dir = target_root / ".agents" / "skills"
    target_skills_dir.mkdir(parents=True, exist_ok=True)

    synced_count = 0
    for name in sorted(skills_to_sync):
        src = source_skills[name]
        dest = target_skills_dir / name
        action = "Cập nhật" if dest.exists() else "Thêm mới"
        copy_skill(src, dest)
        print(f"[{action}] .agents/skills/{name}")
        synced_count += 1

    # Apply prune
    pruned_count = 0
    for name in sorted(skills_to_prune):
        dest = target_skills_dir / name
        if dest.exists():
            prune_skill(dest)
            print(f"[Xoá bỏ] .agents/skills/{name}")
            pruned_count += 1
        else:
            print(f"[Bỏ qua] .agents/skills/{name} không tồn tại trên target")

    print(f"\nTổng kết: Đã đồng bộ {synced_count} skills, xoá bỏ {pruned_count} skills.")

    # Link Claude skills
    if not args.skip_claude_links:
        run_claude_link_script(source_root, target_root)

    # Validate target
    if args.validate:
        validator = target_root / "scripts" / "test-harness-skills"
        if validator.is_file():
            print(f"Đang chạy kiểm thử xác minh trên target: {validator.name}...")
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            res = subprocess.run([str(validator)], cwd=target_root, env=env, check=False)
            if res.returncode == 0:
                print(f"[✓] Kiểm định target hoàn tất thành công.")
            else:
                print(f"[!] Kiểm định target phát hiện lỗi (exit {res.returncode}).", file=sys.stderr)

    print("\nHoàn tất! Các file đã được đồng bộ an toàn (chưa staged/committed vào git của target).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as err:
        print(f"Lỗi: {err}", file=sys.stderr)
        raise SystemExit(1)

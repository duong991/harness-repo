#!/usr/bin/env python3
"""Integration tests for scripts/sync-skills.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "sync-skills.py"


class SyncSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="test-sync-skills-")
        self.base = Path(self.temp_dir.name)
        self.source = self.base / "source"
        self.target = self.base / "target"
        self.source.mkdir()
        self.target.mkdir()

        # Seed source skills
        self._create_skill(self.source, "skill-a", "Skill A description", {"helper.py": "print('a')"})
        self._create_skill(self.source, "skill-b", "Skill B description", {"config.json": '{"v": 1}'})
        self._create_skill(self.source, "skill-c", "Skill C description", {"rule.md": "Rule 1"})

        # Seed target skills
        self._create_skill(self.target, "skill-a", "Skill A description", {"helper.py": "print('a')"})  # IN_SYNC
        self._create_skill(self.target, "skill-b", "Skill B description", {"config.json": '{"v": 2}'})  # DIVERGED
        self._create_skill(self.target, "skill-local", "Local target skill", {"local.py": "pass"})      # TARGET_ONLY

        # Claude links in target
        (self.target / ".claude" / "skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/skill-a", self.target / ".claude" / "skills" / "skill-a")
        os.symlink("../../.agents/skills/skill-b", self.target / ".claude" / "skills" / "skill-b")
        os.symlink("../../.agents/skills/skill-local", self.target / ".claude" / "skills" / "skill-local")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_skill(self, repo: Path, name: str, description: str, extra_files: dict[str, str]) -> None:
        skill_dir = repo / ".agents" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        content = f"---\nname: {name}\ndescription: \"{description}\"\n---\n# {name}\n"
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        for rel_path, text in extra_files.items():
            p = skill_dir / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")

    def run_cmd(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(SCRIPT), "--source", str(self.source), "--target", str(self.target), *args]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        res = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
        if check and res.returncode != 0:
            raise RuntimeError(f"Command failed ({res.returncode}):\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
        return res

    def test_scan_identifies_status_groups(self) -> None:
        res = self.run_cmd("--scan")
        self.assertIn("BÁO CÁO SCAN SO SÁNH KỸ NĂNG", res.stdout)
        self.assertIn("skill-c", res.stdout)       # New from source
        self.assertIn("skill-b", res.stdout)       # Diverged
        self.assertIn("skill-local", res.stdout)   # Target-only
        self.assertIn("skill-a", res.stdout)       # In sync

    def test_json_output_structure(self) -> None:
        res = self.run_cmd("--json")
        data = json.loads(res.stdout)
        self.assertEqual(data["source_skills_count"], 3)
        self.assertEqual(data["target_skills_count"], 3)

        source_only_names = [s["name"] for s in data["source_only"]]
        self.assertEqual(source_only_names, ["skill-c"])

        diverged_names = [s["name"] for s in data["diverged"]]
        self.assertEqual(diverged_names, ["skill-b"])

        target_only_names = [s["name"] for s in data["target_only"]]
        self.assertEqual(target_only_names, ["skill-local"])

        in_sync_names = [s["name"] for s in data["in_sync"]]
        self.assertEqual(in_sync_names, ["skill-a"])

    def test_selective_sync_applies_single_skill(self) -> None:
        # Sync only skill-c (new)
        res = self.run_cmd("--apply", "--sync", "skill-c", "--skip-claude-links")
        self.assertIn("[Thêm mới] .agents/skills/skill-c", res.stdout)
        target_c = self.target / ".agents/skills/skill-c/SKILL.md"
        self.assertTrue(target_c.is_file())

        # Verify skill-b is still diverged (not updated)
        target_b_cfg = self.target / ".agents/skills/skill-b/config.json"
        self.assertIn('"v": 2', target_b_cfg.read_text(encoding="utf-8"))

    def test_sync_all_and_backup(self) -> None:
        # Sync all
        res = self.run_cmd("--apply", "--sync-all", "--skip-claude-links")
        self.assertIn("[Thêm mới] .agents/skills/skill-c", res.stdout)
        self.assertIn("[Cập nhật] .agents/skills/skill-b", res.stdout)

        # Check backup created
        backup_dir = self.target / ".harness-core" / "source-sync-backups"
        self.assertTrue(backup_dir.is_dir())
        backups = list(backup_dir.glob("skills-*"))
        self.assertGreaterEqual(len(backups), 1)

        # Verify skill-b was updated to match source
        target_b_cfg = self.target / ".agents/skills/skill-b/config.json"
        self.assertIn('"v": 1', target_b_cfg.read_text(encoding="utf-8"))

    def test_prune_removes_target_skill(self) -> None:
        res = self.run_cmd("--apply", "--prune", "skill-local", "--skip-claude-links")
        self.assertIn("[Xoá bỏ] .agents/skills/skill-local", res.stdout)
        self.assertFalse((self.target / ".agents/skills/skill-local").exists())


if __name__ == "__main__":
    unittest.main()

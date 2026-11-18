#!/usr/bin/env python3
"""Regression checks for accepting genuine grading records, rejecting corrupt ones."""
import sys
sys.dont_write_bytecode = True
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from aggregate import aggregate

ROOT = Path(__file__).resolve().parent

class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / 'iteration'
        shutil.copytree(ROOT/'runs'/'iteration-1', self.run)
        self.grade = self.run/'eval-1'/'with_skill'/'grading.json'

    def check_run(self):
        with contextlib.redirect_stdout(io.StringIO()):
            aggregate(self.run)

    def test_accepts_complete_evidence_records(self):
        self.check_run()
        result=json.loads((self.run/'benchmark.json').read_text())
        self.assertEqual(len(result['runs']),12)
        self.assertEqual(result['trigger_probe']['total'],9)

    def test_rejects_unsubstantiated_grade(self):
        data=json.loads(self.grade.read_text())
        data['expectations'][0]['evidence']=''
        self.grade.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'requires evidence'):
            self.check_run()

    def test_rejects_inconsistent_score(self):
        data=json.loads(self.grade.read_text())
        data['summary']['passed'] += 1
        self.grade.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'summary does not match'):
            self.check_run()

if __name__=='__main__':
    unittest.main()

from __future__ import annotations

import json
import shlex
import sys
import unittest
from pathlib import Path

from common import load_fixtures
from run import generate_prompt_pack, run_fixture

ROOT = Path(__file__).resolve().parent


def aggregate(results):
    checks = 0
    passed = 0
    premature = 0
    for result in results:
        for item in result["timeline"]:
            verdict = item.get("verdict")
            if not verdict:
                continue
            checks += verdict["total"]
            passed += verdict["passed"]
            for check in verdict["checks"]:
                if check["field"] == "final_cause_timing" and not check["passed"]:
                    premature += 1
    return passed, checks, premature


class SupportProcessExperimentTest(unittest.TestCase):
    def test_prompt_pack_has_one_prompt_per_turn(self):
        fixtures = load_fixtures()
        expected_turns = sum(len(fixture["transcript_turns"]) for fixture in fixtures)
        self.assertEqual(len(generate_prompt_pack(fixtures)), expected_turns)

    def test_deterministic_reference_passes(self):
        results = [run_fixture(fixture) for fixture in load_fixtures()]
        passed, checks, premature = aggregate(results)
        self.assertEqual(passed, checks)
        self.assertEqual(premature, 0)

    def test_process_mock_passes_without_premature_final_cause(self):
        command = f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT / 'mock_llm.py'))} --profile process"
        results = [run_fixture(fixture, mode="llm", llm_command=command) for fixture in load_fixtures()]
        passed, checks, premature = aggregate(results)
        self.assertEqual(passed, checks)
        self.assertEqual(premature, 0)

    def test_predictive_mock_fails_on_premature_final_cause(self):
        command = f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT / 'mock_llm.py'))} --profile predictive"
        results = [run_fixture(fixture, mode="llm", llm_command=command) for fixture in load_fixtures()]
        passed, checks, premature = aggregate(results)
        self.assertLess(passed, checks)
        self.assertGreaterEqual(premature, 1)


if __name__ == "__main__":
    unittest.main()

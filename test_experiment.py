from __future__ import annotations

import json
import shlex
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from common import load_fixtures
from prototype.report import case_verdict, render_report, select_case_ids
from prototype.replay import build_replay
from run import extract_anthropic_text, extract_response_text, generate_prompt_pack, run_fixture

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

    def test_prototype_replay_waits_for_context_before_final_cause(self):
        result = build_replay("access_after_migration", "process-mock")
        timeline = result["timeline"]
        self.assertEqual([item["turn"]["turn"] for item in timeline], [1, 2, 3])
        self.assertEqual(timeline[0]["state"]["final_cause"], "")
        self.assertEqual(timeline[1]["state"]["final_cause"], "")
        self.assertEqual(timeline[2]["state"]["final_cause"], "missing_workspace_role_inheritance")
        self.assertEqual(timeline[0]["llm_patch"]["final_cause"], "")
        self.assertEqual(timeline[2]["llm_patch"]["final_cause"], "missing_workspace_role_inheritance")
        self.assertEqual(result["final_state"]["final_cause"], "missing_workspace_role_inheritance")

    def test_prototype_replay_cleans_resolved_unknowns_and_ruled_out_branches(self):
        for case_id in [
            "corrected_billing_after_access_report",
            "invite_email_not_arriving",
            "invite_with_irrelevant_billing_context",
        ]:
            with self.subTest(case_id=case_id):
                state = build_replay(case_id, "process-mock")["final_state"]
                overlap = set(state["candidate_branches"]) & set(state["ruled_out_branches"])
                self.assertEqual(state["unknowns"], [])
                self.assertEqual(overlap, set())

    def test_prototype_report_includes_all_cases_by_default(self):
        html = render_report(select_case_ids())
        for fixture in load_fixtures():
            self.assertIn(fixture["case_id"], html)
        self.assertIn('<details class="case"', html)
        self.assertIn('<summary class="case-summary">', html)

    def test_prototype_report_single_case_mode(self):
        html = render_report(select_case_ids("access_after_migration"))
        self.assertIn("access_after_migration", html)
        self.assertNotIn("billing_plan_mismatch", html)

    def test_prototype_report_verdict_marks_process_mock_timing_pass(self):
        result = build_replay("access_after_migration", "process-mock")
        self.assertEqual(case_verdict(result)["premature_turns"], [])
        self.assertIn("final-cause timing: pass", render_report(["access_after_migration"]))

    def test_prototype_report_ignored_context_does_not_pollute_state(self):
        result = build_replay("invite_with_irrelevant_billing_context", "process-mock")
        first_state = result["timeline"][0]["state"]
        self.assertNotIn("invoice_plan:pro", first_state["facts"])
        html = render_report(["invite_with_irrelevant_billing_context"])
        self.assertIn("ignored context", html)

    def test_predictive_mock_fails_on_premature_final_cause(self):
        command = f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT / 'mock_llm.py'))} --profile predictive"
        results = [run_fixture(fixture, mode="llm", llm_command=command) for fixture in load_fixtures()]
        passed, checks, premature = aggregate(results)
        self.assertLess(passed, checks)
        self.assertGreaterEqual(premature, 1)

    def test_openai_provider_requires_environment_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                run_fixture(
                    load_fixtures()[0],
                    mode="real-model",
                    provider="openai",
                    model="test-model",
                )

    def test_anthropic_provider_requires_environment_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "ANTHROPIC_API_KEY"):
                run_fixture(
                    load_fixtures()[0],
                    mode="real-model",
                    provider="anthropic",
                    model="test-model",
                )

    def test_provider_output_text_extraction(self):
        response = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "{\"facts_add\": [], \"unknowns_add\": []}",
                        }
                    ]
                }
            ]
        }
        self.assertIn("facts_add", extract_response_text(response))

    def test_anthropic_text_extraction(self):
        response = {
            "content": [
                {
                    "type": "text",
                    "text": "{\"facts_add\": [], \"unknowns_add\": []}",
                }
            ]
        }
        self.assertIn("facts_add", extract_anthropic_text(response))


if __name__ == "__main__":
    unittest.main()

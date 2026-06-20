from __future__ import annotations

import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from common import load_fixtures
from prototype.generated_review import (
    generated_review,
    outcome_coverage_notes,
    outcome_distribution,
    render_generated_review,
    review_outcome,
    write_generated_review,
)
from prototype.import_generated import import_cases
from prototype.leader_demo import render_support_leader_demo, write_support_leader_demo
from prototype.report import case_verdict, render_report, select_case_ids
from prototype.replay import build_replay
from prototype.support_language import (
    BANNED_SUPPORT_PHRASES,
    contains_internal_language,
    translate_facts,
    translate_next_action,
    translate_outcome,
    translate_unknowns,
)
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

    def test_prototype_report_supports_unresolved_handoff_case(self):
        result = build_replay("level2_unresolved_workspace_handoff", "process-mock")
        verdict = case_verdict(result)
        self.assertTrue(verdict["passed"])
        self.assertTrue(verdict["expects_handoff"])
        self.assertEqual(result["final_state"]["final_cause"], "")
        self.assertIn("cache_status", result["final_state"]["unknowns"])
        html = render_report(["level2_unresolved_workspace_handoff"])
        self.assertIn("Post-Case Handoff", html)
        self.assertIn("Unresolved; hand off", html)

    def test_generated_fixture_importer_stages_valid_case(self):
        fixture = json.loads((ROOT / "fixtures" / "access_after_migration.json").read_text())
        fixture["case_id"] = "generated_access_after_migration"
        envelope = {"schema_version": "support_process_fixture.v1", "cases": [fixture]}
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "generated.json"
            staging_dir = Path(tmp) / "staging"
            input_path.write_text(json.dumps(envelope))
            written = import_cases(input_path, staging_dir)
            self.assertEqual(len(written), 1)
            self.assertTrue((staging_dir / "generated_access_after_migration.json").exists())

    def test_generated_fixture_importer_accepts_single_schema_fixture(self):
        fixture = json.loads((ROOT / "fixtures" / "access_after_migration.json").read_text())
        fixture["schema_version"] = "support_process_fixture.v1"
        fixture["case_id"] = "single_generated_access_after_migration"
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "generated.json"
            staging_dir = Path(tmp) / "staging"
            input_path.write_text(json.dumps(fixture))
            written = import_cases(input_path, staging_dir)
            self.assertEqual(len(written), 1)
            self.assertTrue((staging_dir / "single_generated_access_after_migration.json").exists())

    def test_generated_review_renders_staged_cases_without_root_promotion(self):
        fixture = json.loads((ROOT / "fixtures" / "access_after_migration.json").read_text())
        fixture["schema_version"] = "support_process_fixture.v1"
        fixture["case_id"] = "review_generated_access_after_migration"
        fixture["difficulty_profile"] = "hard"
        fixture["expected_outcome"] = "resolved"
        with tempfile.TemporaryDirectory() as tmp:
            staging_dir = Path(tmp) / "staging"
            staging_dir.mkdir()
            (staging_dir / "review_generated_access_after_migration.json").write_text(json.dumps(fixture))
            html = render_generated_review([fixture])
            self.assertIn("Generated Support Fixture Review", html)
            self.assertIn("review_generated_access_after_migration", html)
            output_path = Path(tmp) / "generated_review.html"
            written = write_generated_review(staging_dir=staging_dir, path=output_path)
            self.assertEqual(written, output_path)
            self.assertTrue(output_path.exists())

    def test_generated_review_reports_promotion_diagnostics(self):
        fixture = json.loads((ROOT / "fixtures" / "access_after_migration.json").read_text())
        fixture["schema_version"] = "support_process_fixture.v1"
        fixture["case_id"] = "diagnostic_generated_access_after_migration"
        fixture["difficulty_profile"] = "hard"
        fixture["expected_outcome"] = "resolved"
        result = run_fixture(fixture)
        review = generated_review(result)
        self.assertEqual(review["exact_passed"], review["exact_total"])
        self.assertEqual(review["relevant_context_count"], 1)
        self.assertEqual(review["ignored_context_count"], 0)
        self.assertEqual(review["final_cause_event_count"], 1)
        self.assertEqual(review["structural_misses"], 0)
        self.assertEqual(review["next_check_misses"], 0)
        self.assertEqual(review["blockers"], [])
        self.assertTrue(review["ready_for_promotion"])

    def test_generated_review_maps_escalated_resolution_to_handoff(self):
        fixture = json.loads((ROOT / "fixtures" / "level2_unresolved_workspace_handoff.json").read_text())
        fixture["schema_version"] = "support_process_fixture.v1"
        fixture["case_id"] = "generated_escalated_handoff_case"
        fixture["expected_outcome"] = "handoff"
        fixture["resolution_type"] = "escalated"
        fixture["next_owner"] = "engineering/product support"
        fixture["safe_customer_summary"] = "Access issue needs engineering cache investigation."
        result = run_fixture(fixture)
        review = generated_review(result)
        self.assertEqual(review_outcome(fixture), "handoff")
        self.assertTrue(review["final_cause_ok"])
        self.assertTrue(review["transfer_ready"])
        self.assertTrue(review["outcome_ok"])

    def test_generated_review_maps_unresolved_resolution_to_handoff(self):
        fixture = json.loads((ROOT / "fixtures" / "level2_unresolved_workspace_handoff.json").read_text())
        fixture["schema_version"] = "support_process_fixture.v1"
        fixture["case_id"] = "generated_unresolved_handoff_case"
        fixture["expected_outcome"] = "handoff"
        fixture["resolution_type"] = "unresolved"
        fixture["next_owner"] = "follow-up support owner"
        fixture["safe_customer_summary"] = "The case needs follow-up because verification was not complete during the call."
        result = run_fixture(fixture)
        review = generated_review(result)
        self.assertEqual(review_outcome(fixture), "handoff")
        self.assertTrue(review["final_cause_ok"])
        self.assertTrue(review["transfer_ready"])
        self.assertTrue(review["outcome_ok"])

    def test_generated_review_reports_outcome_distribution_gaps(self):
        fixtures = [
            {"expected_outcome": "resolved"},
            {"expected_outcome": "probable_cause"},
            {"expected_outcome": "handoff"},
            {"resolution_type": "escalated"},
            {"resolution_type": "unresolved"},
        ]
        self.assertEqual(outcome_distribution(fixtures)["handoff"], 3)
        self.assertEqual(outcome_coverage_notes(fixtures), [])
        self.assertIn("missing handoff", "; ".join(outcome_coverage_notes(fixtures[:2])))

    def test_support_leader_demo_renders_three_plain_language_outcomes(self):
        staging_dir = ROOT / "outputs" / "generated_fixture_staging"
        fixtures = [json.loads(path.read_text()) for path in sorted(staging_dir.glob("*.json"))]
        html = render_support_leader_demo(fixtures)
        self.assertIn("Support Copilot Demo", html)
        self.assertIn("Resolved", html)
        self.assertIn("Probable Cause", html)
        self.assertIn("Handoff", html)
        self.assertIn("Customer Situation", html)
        self.assertIn("Next Best Action", html)
        self.assertNotIn("Exact Checks", html)
        self.assertNotIn("ready for promotion", html)
        for phrase in BANNED_SUPPORT_PHRASES:
            self.assertNotIn(phrase, html.lower())
        self.assertNotIn("comparison:config_differs", html)
        self.assertNotIn("sso_group:membership", html)

    def test_support_leader_demo_writes_output_file(self):
        staging_dir = ROOT / "outputs" / "generated_fixture_staging"
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "support_leader_demo.html"
            written = write_support_leader_demo(staging_dir, output_path)
            self.assertEqual(written, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("A support copilot that works the case", output_path.read_text())

    def test_support_language_translates_compact_labels(self):
        facts = translate_facts(["sso_group:membership", "comparison:config_differs"])
        unknowns = translate_unknowns(["workspace_role_assignment"])
        self.assertIn("Group membership is relevant", facts[0])
        self.assertIn("working example", facts[1])
        self.assertIn("workspace role", unknowns[0])
        self.assertFalse(any(":" in item for item in facts + unknowns))

    def test_support_language_next_actions_are_outcome_specific(self):
        fixture = json.loads((ROOT / "outputs" / "generated_fixture_staging" / "call_8c0a974e28.json").read_text())
        result = run_fixture(fixture)
        review = generated_review(result)
        action = translate_next_action(result, review)
        outcome = translate_outcome(result, review)
        self.assertIn("engineering/product support", action)
        self.assertIn("evidence summary", action)
        self.assertIn("engineering/product support", outcome)
        self.assertFalse(contains_internal_language(action))

    def test_support_language_probable_cause_preserves_uncertainty(self):
        fixture = json.loads((ROOT / "outputs" / "generated_fixture_staging" / "call_4ae34b2a60.json").read_text())
        result = run_fixture(fixture)
        review = generated_review(result)
        action = translate_next_action(result, review)
        outcome = translate_outcome(result, review)
        self.assertIn("before treating", action)
        self.assertIn("one more product signal", outcome)
        self.assertFalse(contains_internal_language(action))

    def test_support_language_resolved_action_is_closure_oriented(self):
        fixture = json.loads((ROOT / "outputs" / "generated_fixture_staging" / "call_a700c9bbc2.json").read_text())
        result = run_fixture(fixture)
        review = generated_review(result)
        action = translate_next_action(result, review)
        outcome = translate_outcome(result, review)
        self.assertIn("Confirm the customer can complete", action)
        self.assertNotIn("one more product signal", outcome)
        self.assertFalse(contains_internal_language(action))

    def test_generated_fixture_importer_rejects_premature_final_cause_leakage(self):
        fixture = json.loads((ROOT / "fixtures" / "access_after_migration.json").read_text())
        fixture["case_id"] = "leaky_generated_case"
        fixture["transcript_turns"][0]["text"] = "This is definitely missing_workspace_role_inheritance."
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "generated.json"
            input_path.write_text(json.dumps({"schema_version": "support_process_fixture.v1", "cases": [fixture]}))
            with self.assertRaisesRegex(ValueError, "leaks final_cause"):
                import_cases(input_path, Path(tmp) / "staging")

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

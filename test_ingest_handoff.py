from __future__ import annotations

import re
import unittest

from prototype.ingest_handoff_notes import (
    BANNER,
    CASE_IDS,
    build_cases,
    render_case,
    render_index,
)

BANNED = [r"\bdeterministic", r"\bevals?\b", r"\bJSONL\b", r"\bfixtures?\b"]


class IngestHandoffTest(unittest.TestCase):
    def setUp(self):
        self.cases = build_cases()

    def test_six_cases_with_expected_ids(self):
        self.assertEqual([c["id"] for c in self.cases], CASE_IDS)

    def test_required_sections_non_empty(self):
        for c in self.cases:
            self.assertTrue(c["utterance"], f"{c['id']} utterance empty")
            self.assertTrue(c["claim"], f"{c['id']} claim/summary empty")
            self.assertTrue(c["final_risk"], f"{c['id']} final risk empty")
            self.assertTrue(c["gate_verdict"], f"{c['id']} gate verdict empty")
            self.assertEqual(len(c["judges"]), 5, f"{c['id']} not five reviewers")
            for j in c["judges"]:
                self.assertTrue(j["name"] and j["status"] and j["reason"])

    def test_h1_carries_ticket_and_identity(self):
        h1 = next(c for c in self.cases if c["id"] == "H1")
        self.assertTrue(h1["reference"], "H1 must carry a Ticket reference")
        self.assertTrue(h1["identity"], "H1 must carry customer identity")

    def test_rendered_pages_have_banner_and_no_banned_words(self):
        pages = [render_case(c) for c in self.cases] + [render_index(self.cases)]
        for html in pages:
            self.assertIn(BANNER, html)
            for pat in BANNED:
                self.assertIsNone(
                    re.search(pat, html, re.I),
                    f"banned word {pat!r} leaked into a case screen",
                )

    def test_index_lists_all_six(self):
        idx = render_index(self.cases)
        for cid in CASE_IDS:
            self.assertIn(f'href="{cid}.html"', idx)


if __name__ == "__main__":
    unittest.main()

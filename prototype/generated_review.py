#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import OUTPUT_DIR, ensure_output_dir, esc
from prototype.import_generated import DEFAULT_STAGING_DIR
from prototype.report import render_case
from run import run_fixture

REVIEW_PATH = OUTPUT_DIR / "generated_support_review.html"


def load_staged_fixtures(staging_dir: Path = DEFAULT_STAGING_DIR, case_id: str = "") -> list[dict[str, Any]]:
    if not staging_dir.exists():
        raise SystemExit(f"Generated fixture staging directory does not exist: {staging_dir}")
    fixtures = [json.loads(path.read_text()) for path in sorted(staging_dir.glob("*.json"))]
    if case_id:
        fixtures = [fixture for fixture in fixtures if fixture.get("case_id") == case_id]
        if not fixtures:
            raise SystemExit(f"Unknown staged generated case_id: {case_id}")
    if not fixtures:
        raise SystemExit(f"No staged generated fixtures found in {staging_dir}")
    return fixtures


def generated_review(result: dict[str, Any]) -> dict[str, Any]:
    exact_passed = 0
    exact_total = 0
    missing_next_checks = []
    next_check_wording_misses = []
    premature_turns = []
    field_failures: dict[str, int] = {}
    for item in result["timeline"]:
        state = item["state"]
        if not state.get("next_check"):
            missing_next_checks.append(item["turn"]["turn"])
        if state.get("final_cause") and not state.get("root_cause_evidence_seen"):
            premature_turns.append(item["turn"]["turn"])
        verdict = item.get("verdict")
        if verdict:
            exact_passed += verdict["passed"]
            exact_total += verdict["total"]
            for check in verdict["checks"]:
                if check["passed"]:
                    continue
                field = check["field"]
                field_failures[field] = field_failures.get(field, 0) + 1
                if field == "next_check" and state.get("next_check"):
                    next_check_wording_misses.append(item["turn"]["turn"])

    final_state = result["final_state"]
    fixture = result["fixture"]
    overlaps = sorted(set(final_state["candidate_branches"]) & set(final_state["ruled_out_branches"]))
    expected_outcome = fixture.get("expected_outcome", "resolved")
    expects_handoff = expected_outcome == "handoff"
    final_cause_ok = (
        not final_state.get("final_cause")
        if expects_handoff
        else (not fixture.get("final_cause") or final_state.get("final_cause") == fixture.get("final_cause"))
    )
    relevant_context = [
        event
        for event in fixture.get("context_events", [])
        if event.get("relevant", True)
    ]
    ignored_context = [
        event
        for event in fixture.get("context_events", [])
        if event.get("relevant", True) is False
    ]
    final_cause_events = [
        event
        for event in relevant_context
        if event.get("final_cause") or event.get("reveals_final_cause")
    ]
    unresolved_unknowns = list(final_state["unknowns"])
    handoff_ok = (
        bool(unresolved_unknowns) and not final_state.get("final_cause")
        if expects_handoff
        else not unresolved_unknowns
    )
    structural_fields = {"facts", "unknowns", "candidate_branches", "ruled_out_branches", "final_cause_timing"}
    structural_misses = sum(count for field, count in field_failures.items() if field in structural_fields)
    next_check_misses = field_failures.get("next_check", 0)
    blockers = []
    if structural_misses:
        blockers.append(f"{structural_misses} structural state miss(es)")
    if missing_next_checks:
        blockers.append(f"{len(missing_next_checks)} turn(s) with no next check")
    elif next_check_misses:
        blockers.append(f"{next_check_misses} next-check wording miss(es)")
    if premature_turns:
        blockers.append("premature final cause")
    if overlaps:
        blockers.append("candidate/ruled-out overlap")
    if not final_cause_ok:
        blockers.append("final cause mismatch")
    if not handoff_ok:
        blockers.append("handoff/unknown status mismatch")
    if not relevant_context:
        blockers.append("no relevant context")

    ready_for_promotion = (
        exact_total > 0
        and exact_passed == exact_total
        and not missing_next_checks
        and not premature_turns
        and not overlaps
        and final_cause_ok
        and handoff_ok
        and bool(relevant_context)
    )
    return {
        "exact_passed": exact_passed,
        "exact_total": exact_total,
        "missing_next_checks": missing_next_checks,
        "next_check_wording_misses": next_check_wording_misses,
        "premature_turns": premature_turns,
        "field_failures": field_failures,
        "overlaps": overlaps,
        "final_cause_ok": final_cause_ok,
        "expects_handoff": expects_handoff,
        "handoff_ok": handoff_ok,
        "unresolved_unknowns": unresolved_unknowns,
        "relevant_context_count": len(relevant_context),
        "ignored_context_count": len(ignored_context),
        "final_cause_event_count": len(final_cause_events),
        "structural_misses": structural_misses,
        "next_check_misses": next_check_misses,
        "blockers": blockers,
        "ready_for_promotion": ready_for_promotion,
    }


def render_review_detail(review: dict[str, Any]) -> str:
    if review["ready_for_promotion"]:
        return "ready"
    if not review["blockers"]:
        return "manual review"
    return "; ".join(review["blockers"])


def render_review_summary(results: list[dict[str, Any]]) -> str:
    rows = []
    for result in results:
        fixture = result["fixture"]
        review = generated_review(result)
        exact = f"{review['exact_passed']}/{review['exact_total']}"
        context = f"{review['relevant_context_count']} relevant / {review['ignored_context_count']} ignored"
        rows.append(
            "<tr>"
            f"<td><a href=\"#{esc(fixture['case_id'])}\">{esc(fixture['case_id'])}</a></td>"
            f"<td>{esc(fixture.get('difficulty_profile', '-'))}</td>"
            f"<td>{esc(fixture.get('expected_outcome', 'resolved'))}</td>"
            f"<td>{esc(exact)}</td>"
            f"<td>{esc(context)}</td>"
            f"<td>{'pass' if not review['premature_turns'] else 'check'}</td>"
            f"<td>{'pass' if not review['next_check_misses'] else 'review'}</td>"
            f"<td>{'ready' if review['ready_for_promotion'] else 'stage only'}</td>"
            f"<td>{esc(render_review_detail(review))}</td>"
            "</tr>"
        )
    return "".join(rows)


def render_generated_review(fixtures: list[dict[str, Any]], show_patches: bool = False) -> str:
    results = [run_fixture(fixture, mode="deterministic") for fixture in fixtures]
    ready_count = sum(1 for result in results if generated_review(result)["ready_for_promotion"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Generated Support Fixture Review</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin:0; background:#11100f; color:#f4eee8; }}
main {{ max-width:1180px; margin:0 auto; padding:32px 20px 64px; }}
h1 {{ font-size:30px; margin:0 0 8px; }}
h2 {{ font-size:22px; margin:4px 0 8px; }}
h3, h4 {{ margin:0 0 8px; }}
p {{ color:#c8beb5; max-width:860px; line-height:1.45; }}
code {{ color:#e8a08a; }}
table {{ width:100%; border-collapse:collapse; margin:22px 0 30px; font-size:14px; }}
th, td {{ border-bottom:1px solid #352f2a; text-align:left; padding:10px; vertical-align:top; }}
th {{ color:#a99c90; font-size:12px; text-transform:uppercase; letter-spacing:.08em; }}
a {{ color:#e8a08a; }}
.hero, .case {{ border:1px solid #352f2a; border-radius:8px; padding:20px; background:#171513; margin-bottom:14px; }}
.case-summary {{ cursor:pointer; list-style:none; }}
.case-summary::-webkit-details-marker {{ display:none; }}
.case-summary::before {{ content:"Expand case"; display:inline-block; margin-bottom:10px; color:#e8a08a; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; text-transform:uppercase; letter-spacing:.08em; }}
.case[open] .case-summary::before {{ content:"Collapse case"; }}
.case-head {{ display:flex; justify-content:space-between; gap:18px; align-items:flex-start; }}
.case-body {{ border-top:1px solid #352f2a; padding-top:14px; margin-top:14px; }}
.case-verdict {{ font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:13px; border:1px solid; border-radius:999px; padding:6px 10px; }}
.case-verdict.pass, .badge.ok {{ color:#8fd19e; border-color:#376b43; }}
.case-verdict.warn, .badge.bad {{ color:#f0c36a; border-color:#7a5d22; }}
.badges {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }}
.badge {{ font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; border:1px solid; border-radius:999px; padding:5px 8px; }}
.notes, .empty, .facts-inline {{ color:#a99c90; font-size:13px; }}
.turn {{ border-top:1px solid #352f2a; padding-top:18px; margin-top:18px; }}
.turn-header, .eyebrow {{ font-family:ui-monospace, SFMono-Regular, Menlo, monospace; color:#a99c90; font-size:12px; text-transform:uppercase; letter-spacing:.08em; }}
blockquote {{ margin:8px 0 14px; padding:12px 14px; background:#201d1a; border-left:3px solid #c4674a; color:#fff7ef; }}
.context-wrap {{ margin-bottom:14px; }}
.context-item {{ border:1px solid #3c352f; border-radius:8px; padding:10px; margin:8px 0; background:#1d1a17; }}
.context-item.ignored {{ opacity:.75; }}
.state-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; }}
.state-grid section, .next-check, .final {{ border:1px solid #352f2a; border-radius:8px; padding:12px; background:#151311; }}
.handoff {{ border:1px solid #3c352f; border-radius:8px; padding:12px; margin:14px 0; background:#151311; }}
.handoff-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; }}
ul {{ margin:0; padding-left:18px; }}
li {{ margin:4px 0; }}
.next-check, .final {{ margin-top:12px; }}
.next-check strong {{ color:#fff7ef; }}
.final-cause {{ color:#8fd19e; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; }}
details {{ margin-top:12px; }}
summary {{ cursor:pointer; color:#e8a08a; }}
pre {{ overflow:auto; background:#0d0c0b; border:1px solid #352f2a; border-radius:8px; padding:12px; color:#f4eee8; }}
</style>
</head>
<body>
<main>
  <section class="hero">
    <div class="eyebrow">Generated fixture review</div>
    <h1>Generated Support Fixture Review</h1>
    <p>This is the expansion lane for support-call-generator output. These cases are staged for review and are not source-of-truth fixtures until manually promoted.</p>
    <h3>{ready_count}/{len(results)} ready for promotion by strict generated-review checks</h3>
  </section>
  <table>
    <thead>
      <tr><th>Case</th><th>Difficulty</th><th>Outcome</th><th>Exact Checks</th><th>Context</th><th>Final Timing</th><th>Next Check</th><th>Status</th><th>Review Focus</th></tr>
    </thead>
    <tbody>{render_review_summary(results)}</tbody>
  </table>
  {"".join(render_case(result, show_patches) for result in results)}
</main>
</body>
</html>
"""


def write_generated_review(
    staging_dir: Path = DEFAULT_STAGING_DIR,
    case_id: str = "",
    show_patches: bool = False,
    path: Path = REVIEW_PATH,
) -> Path:
    fixtures = load_staged_fixtures(staging_dir, case_id)
    ensure_output_dir()
    path.write_text(render_generated_review(fixtures, show_patches=show_patches))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render staged generated support fixtures for review.")
    parser.add_argument("--staging-dir", default=str(DEFAULT_STAGING_DIR), help="Generated fixture staging directory.")
    parser.add_argument("--case", default="", help="Optional staged generated case_id.")
    parser.add_argument("--show-patches", action="store_true", help="Include raw state patches when available.")
    args = parser.parse_args()
    path = write_generated_review(
        staging_dir=Path(args.staging_dir),
        case_id=args.case,
        show_patches=args.show_patches,
    )
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

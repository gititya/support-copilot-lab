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

from common import OUTPUT_DIR, ensure_output_dir, esc, load_fixtures
from prototype.replay import build_replay

REPORT_PATH = OUTPUT_DIR / "prototype_support_panel_report.html"


def select_case_ids(case_id: str = "") -> list[str]:
    case_ids = [fixture["case_id"] for fixture in load_fixtures()]
    if not case_id:
        return case_ids
    if case_id not in case_ids:
        available = ", ".join(case_ids)
        raise SystemExit(f"Unknown case_id: {case_id}. Available cases: {available}")
    return [case_id]


def case_verdict(result: dict[str, Any]) -> dict[str, Any]:
    final_state = result["final_state"]
    expected_outcome = result["fixture"].get("expected_outcome", "resolved")
    expects_handoff = expected_outcome == "handoff"
    final_expected = result["fixture"].get("final_cause", "")
    overlaps = sorted(set(final_state["candidate_branches"]) & set(final_state["ruled_out_branches"]))
    premature_turns = [
        item["turn"]["turn"]
        for item in result["timeline"]
        if item["state"].get("final_cause") and not item["state"].get("root_cause_evidence_seen")
    ]
    missing_next_checks = [
        item["turn"]["turn"]
        for item in result["timeline"]
        if not item["state"].get("next_check")
    ]
    unresolved_unknowns = list(final_state["unknowns"])
    final_cause_ok = (
        not final_state.get("final_cause")
        if expects_handoff
        else (not final_expected or final_state.get("final_cause") == final_expected)
    )
    unknowns_ok = bool(unresolved_unknowns) if expects_handoff else not unresolved_unknowns
    passed = not premature_turns and unknowns_ok and not overlaps and final_cause_ok
    notes = []
    if premature_turns:
        notes.append("final cause appeared before evidence")
    if unresolved_unknowns and not expects_handoff:
        notes.append("final state has unresolved unknowns")
    if expects_handoff and not unresolved_unknowns:
        notes.append("handoff case should preserve unresolved unknowns")
    if overlaps:
        notes.append("candidate branches overlap with ruled-out branches")
    if not final_cause_ok:
        notes.append("final cause does not match fixture")
    if missing_next_checks:
        notes.append("one or more turns have no next check")
    if not notes:
        notes.append("state progression is clean and evidence-timed")
    return {
        "passed": passed,
        "expects_handoff": expects_handoff,
        "premature_turns": premature_turns,
        "unresolved_unknowns": unresolved_unknowns,
        "unknowns_ok": unknowns_ok,
        "overlaps": overlaps,
        "final_cause_ok": final_cause_ok,
        "missing_next_checks": missing_next_checks,
        "notes": notes,
    }


def render_badge(label: str, ok: bool) -> str:
    cls = "ok" if ok else "bad"
    text = "pass" if ok else "check"
    return f'<span class="badge {cls}">{esc(label)}: {text}</span>'


def render_list(items: list[str]) -> str:
    if not items:
        return '<div class="empty">-</div>'
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def render_context(events: list[dict[str, Any]]) -> str:
    if not events:
        return '<div class="empty">No new product/support context.</div>'
    parts = []
    for event in events:
        relevant = event.get("relevant", True)
        label = "context" if relevant else "ignored context"
        facts = event.get("facts", [])
        parts.append(
            f'<div class="context-item {"ignored" if not relevant else ""}">'
            f'<div class="eyebrow">{esc(label)}</div>'
            f'<div>{esc(event.get("description", "-"))}</div>'
            f'<div class="facts-inline">{esc(", ".join(facts) or "-")}</div>'
            "</div>"
        )
    return "".join(parts)


def render_state_panel(state: dict[str, Any]) -> str:
    final_cause = state.get("final_cause")
    final_html = (
        f'<div class="final-cause">{esc(final_cause)}</div>'
        if final_cause
        else '<div class="empty">Hidden until evidence exists.</div>'
    )
    return f"""
    <div class="state-grid">
      <section>
        <h4>Known Facts</h4>
        {render_list(state["facts"])}
      </section>
      <section>
        <h4>Open Unknowns</h4>
        {render_list(state["unknowns"])}
      </section>
      <section>
        <h4>Active Branches</h4>
        {render_list(state["candidate_branches"])}
      </section>
      <section>
        <h4>Ruled Out</h4>
        {render_list(state["ruled_out_branches"])}
      </section>
    </div>
    <div class="next-check">
      <div class="eyebrow">Next Check</div>
      <strong>{esc(state.get("next_check") or "-")}</strong>
    </div>
    <div class="final">
      <div class="eyebrow">Final Cause</div>
      {final_html}
    </div>
    """


def render_handoff(result: dict[str, Any]) -> str:
    state = result["final_state"]
    fixture = result["fixture"]
    final_cause = state.get("final_cause")
    if final_cause:
        outcome = f"Resolved with evidence-backed cause: {final_cause}"
    elif fixture.get("expected_outcome") == "handoff":
        outcome = "Unresolved; hand off with open checks instead of naming a final cause."
    else:
        outcome = "No final cause recorded."
    return f"""
    <section class="handoff">
      <div class="eyebrow">Post-Case Handoff</div>
      <h4>Outcome</h4>
      <p>{esc(outcome)}</p>
      <h4>Customer-Safe Summary</h4>
      <p>{esc(fixture.get("handoff_summary") or fixture["scenario"])}</p>
      <div class="handoff-grid">
        <section>
          <h4>Known Facts</h4>
          {render_list(state["facts"])}
        </section>
        <section>
          <h4>Unresolved Unknowns</h4>
          {render_list(state["unknowns"])}
        </section>
        <section>
          <h4>Recommended Follow-Up</h4>
          <p>{esc(state.get("next_check") or "-")}</p>
        </section>
      </div>
    </section>
    """


def render_patch(item: dict[str, Any], show_patches: bool) -> str:
    if not show_patches:
        return ""
    patch = item.get("llm_patch")
    raw = json.dumps(patch, indent=2) if patch is not None else "-"
    return f"""
    <details>
      <summary>Raw state patch</summary>
      <pre>{esc(raw)}</pre>
    </details>
    """


def render_case(result: dict[str, Any], show_patches: bool) -> str:
    fixture = result["fixture"]
    verdict = case_verdict(result)
    turn_html = []
    for item in result["timeline"]:
        turn = item["turn"]
        turn_html.append(f"""
        <article class="turn">
          <div class="turn-header">
            <span>Turn {esc(turn["turn"])} · {esc(turn["speaker"])}</span>
          </div>
          <blockquote>{esc(turn["text"])}</blockquote>
          <div class="context-wrap">{render_context(item["context_applied"])}</div>
          {render_state_panel(item["state"])}
          {render_patch(item, show_patches)}
        </article>
        """)

    badges = [
        render_badge("final-cause timing", not verdict["premature_turns"]),
        render_badge("unknown status", verdict["unknowns_ok"]),
        render_badge("branch hygiene", not verdict["overlaps"]),
        render_badge("final cause", verdict["final_cause_ok"]),
    ]
    return f"""
    <details class="case" id="{esc(fixture["case_id"])}">
      <summary class="case-summary">
        <div class="case-head">
          <div>
            <div class="eyebrow">Case</div>
            <h2>{esc(fixture["title"])}</h2>
            <code>{esc(fixture["case_id"])}</code>
            <p>{esc(fixture["scenario"])}</p>
          </div>
          <div class="case-verdict {"pass" if verdict["passed"] else "warn"}">
            {"PASS" if verdict["passed"] else "REVIEW"}
          </div>
        </div>
      </summary>
      <div class="case-body">
        <div class="badges">{"".join(badges)}</div>
        <div class="notes">{"; ".join(esc(note) for note in verdict["notes"])}</div>
        {render_handoff(result)}
        {"".join(turn_html)}
      </div>
    </details>
    """

def overall_verdict(results: list[dict[str, Any]]) -> str:
    verdicts = [case_verdict(result) for result in results]
    all_clean = all(verdict["passed"] for verdict in verdicts)
    next_checks_readable = all(not verdict["missing_next_checks"] for verdict in verdicts)
    if all_clean and next_checks_readable:
        return "Continue"
    if next_checks_readable:
        return "Revise"
    return "Stop / rethink"


def render_report(case_ids: list[str], show_patches: bool = False) -> str:
    results = [build_replay(case_id, "process-mock") for case_id in case_ids]
    verdict = overall_verdict(results)
    case_rows = []
    for result in results:
        fixture = result["fixture"]
        case_result = case_verdict(result)
        case_rows.append(
            "<tr>"
            f"<td><a href=\"#{esc(fixture['case_id'])}\">{esc(fixture['case_id'])}</a></td>"
            f"<td>{'pass' if not case_result['premature_turns'] else 'check'}</td>"
            f"<td>{'pass' if case_result['unknowns_ok'] else 'check'}</td>"
            f"<td>{'pass' if not case_result['overlaps'] else 'check'}</td>"
            f"<td>{'pass' if case_result['final_cause_ok'] else 'check'}</td>"
            f"<td>{esc('; '.join(case_result['notes']))}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Prototype Support Panel Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin:0; background:#11100f; color:#f4eee8; }}
main {{ max-width:1180px; margin:0 auto; padding:32px 20px 64px; }}
h1 {{ font-size:30px; margin:0 0 8px; }}
h2 {{ font-size:22px; margin:4px 0 8px; }}
h3, h4 {{ margin:0 0 8px; }}
p {{ color:#c8beb5; max-width:780px; line-height:1.45; }}
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
    <div class="eyebrow">Mock-only capability report</div>
    <h1>Prototype Support Panel Report</h1>
    <p>Static replay of transcript turns plus mock product/support context. This report checks whether Live Support State helps work each case without premature final-cause prediction.</p>
    <h3>Prototype Verdict: {esc(verdict)}</h3>
  </section>
  <table>
    <thead>
      <tr><th>Case</th><th>Final-cause timing</th><th>Unknowns</th><th>Branch hygiene</th><th>Final cause</th><th>Notes</th></tr>
    </thead>
    <tbody>{"".join(case_rows)}</tbody>
  </table>
  {"".join(render_case(result, show_patches) for result in results)}
</main>
</body>
</html>
"""


def write_report(case_id: str = "", show_patches: bool = False, path: Path = REPORT_PATH) -> Path:
    case_ids = select_case_ids(case_id)
    ensure_output_dir()
    path.write_text(render_report(case_ids, show_patches=show_patches))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the mock-only support prototype HTML report.")
    parser.add_argument("--case", default="", help="Optional fixture case_id. Defaults to all fixtures.")
    parser.add_argument("--show-patches", action="store_true", help="Include raw state patches in collapsible sections.")
    args = parser.parse_args()
    path = write_report(case_id=args.case, show_patches=args.show_patches)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

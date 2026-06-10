#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from copy import deepcopy
from typing import Any

from common import ensure_output_dir, esc, load_fixtures, markdown_table, normalize

LIST_FIELDS = ("facts", "unknowns", "candidate_branches", "ruled_out_branches")
PATCH_ADD_KEYS = {
    "facts": "facts_add",
    "unknowns": "unknowns_add",
    "candidate_branches": "candidate_branches_add",
    "ruled_out_branches": "ruled_out_branches_add",
}
PATCH_REMOVE_KEYS = {
    "facts": "facts_remove",
    "unknowns": "unknowns_remove",
    "candidate_branches": "candidate_branches_remove",
    "ruled_out_branches": "ruled_out_branches_remove",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip()).strip("_")
    return slug.lower()


def output_paths(out_dir: Any, run_name: str, mode: str) -> dict[str, Any]:
    slug = slugify(run_name) if run_name else ""
    if not slug and mode == "deterministic":
        stem = "support_process"
    elif slug:
        stem = f"support_process_{slug}"
    else:
        stem = f"support_process_{slugify(mode)}"
    return {
        "snapshots": out_dir / f"{stem}_snapshots.json",
        "report": out_dir / f"{stem}_report.md",
        "dashboard": out_dir / f"{stem}_dashboard.html",
    }


def new_state(case_id: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "version": 0,
        "facts": [],
        "unknowns": [],
        "candidate_branches": [],
        "ruled_out_branches": [],
        "next_check": "",
        "handoff_notes": [],
        "final_cause": "",
        "root_cause_evidence_seen": False,
    }


def add_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def remove_item(items: list[str], value: str) -> None:
    while value in items:
        items.remove(value)


def add_fact(state: dict[str, Any], fact: str) -> None:
    add_unique(state["facts"], fact)


def add_unknown(state: dict[str, Any], unknown: str) -> None:
    if unknown not in state["facts"]:
        add_unique(state["unknowns"], unknown)


def resolve_unknown(state: dict[str, Any], unknown: str) -> None:
    remove_item(state["unknowns"], unknown)


def add_branch(state: dict[str, Any], branch: str) -> None:
    if branch not in state["ruled_out_branches"]:
        add_unique(state["candidate_branches"], branch)


def rule_out_branch(state: dict[str, Any], branch: str) -> None:
    remove_item(state["candidate_branches"], branch)
    add_unique(state["ruled_out_branches"], branch)


def set_next_check(state: dict[str, Any], value: str) -> None:
    state["next_check"] = value


def process_turn(state: dict[str, Any], turn: dict[str, Any]) -> None:
    text = normalize(turn["text"])
    state["version"] += 1

    if "lost access" in text:
        add_fact(state, "symptom:workspace_access_loss")
        add_unknown(state, "auth_status")
        add_unknown(state, "workspace_role_assignment")
        add_branch(state, "login_block")
        add_branch(state, "missing_workspace_role")
        add_branch(state, "scim_sync_delay")
        add_branch(state, "stale_entitlement_cache")
        set_next_check(state, "Can the affected users sign in, or are they blocked at login?")

    if "three users" in text:
        add_fact(state, "affected_scope:three_users")

    if "migration" in text:
        add_fact(state, "recent_change:migration")

    speaker = turn.get("speaker", "")
    affirmative_auth = (
        "they can sign in" in text
        or "login works" in text
        or "can log in" in text
    )
    if speaker != "agent" and affirmative_auth:
        add_fact(state, "auth:works")
        resolve_unknown(state, "auth_status")
        rule_out_branch(state, "login_block")
        rule_out_branch(state, "login_failure")
        set_next_check(state, "Check whether the affected users have workspace-level roles.")

    if "workspace" in text:
        add_fact(state, "surface:workspace_access")

    if "cannot log in" in text:
        add_fact(state, "reported_issue:login")
        add_unknown(state, "actual_surface")
        add_branch(state, "login_failure")
        set_next_check(state, "Confirm whether login itself fails or whether a page after login is wrong.")

    if "no login works" in text or "login works" in text:
        add_fact(state, "correction:login_works")
        resolve_unknown(state, "actual_surface")
        rule_out_branch(state, "login_failure")
        set_next_check(state, "Identify which page or entitlement is wrong after login.")

    if "billing" in text or "wrong plan" in text:
        add_fact(state, "surface:billing_plan")
        add_fact(state, "symptom:wrong_plan_shown")
        add_unknown(state, "billing_entitlement_status")
        add_branch(state, "billing_entitlement_refresh_pending")
        add_branch(state, "invoice_app_mismatch")
        set_next_check(state, "Check whether the billing entitlement refresh completed after the upgrade.")

    if "upgraded" in text or "upgrade" in text:
        add_fact(state, "recent_change:upgrade")

    if "invite" in text:
        add_fact(state, "flow:admin_invite")
        add_unknown(state, "invite_created")
        add_unknown(state, "email_delivery_status")
        add_branch(state, "invite_not_created")
        add_branch(state, "email_delivery_suppressed")
        add_branch(state, "domain_policy_rejection")
        set_next_check(state, "Check whether the invite was created and whether email delivery bounced or was suppressed.")

    if "never arrives" in text or "email" in text:
        add_fact(state, "symptom:invite_email_not_received")
        set_next_check(state, "Inspect invite delivery status, suppression list, and domain policy results.")

    refresh_handoff(state)


def apply_context_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    state["version"] += 1
    for fact in event.get("facts", []):
        add_fact(state, fact)
    for unknown in event.get("resolved_unknowns", []):
        resolve_unknown(state, unknown)
    for branch in event.get("candidate_branches", []):
        add_branch(state, branch)
    for branch in event.get("ruled_out_branches", []):
        rule_out_branch(state, branch)
    if event.get("next_check"):
        set_next_check(state, event["next_check"])
    if event.get("final_cause"):
        state["final_cause"] = event["final_cause"]
        state["root_cause_evidence_seen"] = True
        add_branch(state, event["final_cause"])
    refresh_handoff(state)


def public_context_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public = []
    for event in events:
        public.append({
            "description": event.get("description", ""),
            "facts": event.get("facts", []),
        })
    return public


def build_llm_prompt(
    fixture: dict[str, Any],
    turn: dict[str, Any],
    state: dict[str, Any],
    context_events: list[dict[str, Any]],
) -> str:
    payload = {
        "case_id": fixture["case_id"],
        "scenario": fixture["scenario"],
        "previous_live_support_state": state,
        "new_transcript_turn": turn,
        "new_product_support_context": public_context_events(context_events),
        "task": "Return only the JSON state patch. Do not write customer-facing support copy.",
    }
    return """You are the Think step in a text-first LTS support-process experiment.

Update Live Support State incrementally. Track facts, unknowns, candidate branches, ruled-out branches, and the next useful check. Do not predict a final root cause from transcript symptoms alone. Set final_cause only when product/support context provides direct mechanism evidence.

Return JSON only with this shape:
{
  "facts_add": [],
  "facts_remove": [],
  "unknowns_add": [],
  "unknowns_remove": [],
  "candidate_branches_add": [],
  "candidate_branches_remove": [],
  "ruled_out_branches_add": [],
  "ruled_out_branches_remove": [],
  "next_check": "",
  "final_cause": "",
  "root_cause_evidence_seen": false,
  "handoff_note": ""
}

Use short canonical labels like symptom:wrong_plan_shown, auth:works, billing_refresh:pending, or missing_workspace_role_inheritance.

Input:
""" + json.dumps(payload, indent=2)


def parse_json_object(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("LLM output did not contain a JSON object")
        value = json.loads(raw[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("LLM output JSON must be an object")
    return value


def call_llm_command(command: str, prompt: str) -> tuple[dict[str, Any], str]:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("--llm-command cannot be empty")
    completed = subprocess.run(
        argv,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"LLM command failed with exit code {completed.returncode}: {completed.stderr.strip()}"
        )
    return parse_json_object(completed.stdout), completed.stdout


def apply_state_patch(
    state: dict[str, Any],
    patch: dict[str, Any],
    context_events: list[dict[str, Any]],
) -> None:
    state["version"] += 1
    for field in LIST_FIELDS:
        for value in patch.get(PATCH_REMOVE_KEYS[field], []):
            remove_item(state[field], value)
        for value in patch.get(PATCH_ADD_KEYS[field], []):
            add_unique(state[field], value)

    for unknown in patch.get("resolved_unknowns", []):
        resolve_unknown(state, unknown)

    if patch.get("next_check"):
        set_next_check(state, patch["next_check"])

    if context_events or patch.get("root_cause_evidence_seen"):
        state["root_cause_evidence_seen"] = bool(context_events or patch.get("root_cause_evidence_seen"))

    final_cause = patch.get("final_cause") or ""
    if final_cause:
        state["final_cause"] = final_cause
        add_branch(state, final_cause)

    handoff_note = patch.get("handoff_note")
    refresh_handoff(state)
    if handoff_note:
        add_unique(state["handoff_notes"], handoff_note)


def refresh_handoff(state: dict[str, Any]) -> None:
    notes = []
    if state["facts"]:
        notes.append("Known: " + "; ".join(state["facts"][-4:]))
    if state["unknowns"]:
        notes.append("Unknowns: " + "; ".join(state["unknowns"][:4]))
    if state["candidate_branches"]:
        notes.append("Branches: " + "; ".join(state["candidate_branches"][:4]))
    if state["next_check"]:
        notes.append("Next check: " + state["next_check"])
    state["handoff_notes"] = notes


def compare_state(state: dict[str, Any], expected: dict[str, Any], root_cause_evidence_available: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check_list(field: str) -> None:
        actual = set(state[field])
        expected_values = set(expected.get(field, []))
        missing = sorted(expected_values - actual)
        extra = sorted(actual - expected_values)
        checks.append({
            "field": field,
            "passed": not missing,
            "missing": missing,
            "extra": extra,
            "expected": sorted(expected_values),
            "actual": sorted(actual),
        })

    for field in ("facts", "unknowns", "candidate_branches", "ruled_out_branches"):
        check_list(field)

    expected_next = expected.get("next_check_contains", [])
    lowered_next = normalize(state.get("next_check", ""))
    missing_next = [term for term in expected_next if normalize(term) not in lowered_next]
    checks.append({
        "field": "next_check",
        "passed": not missing_next,
        "missing": missing_next,
        "extra": [],
        "expected": expected_next,
        "actual": state.get("next_check", ""),
    })

    premature_final_cause = bool(state.get("final_cause")) and not root_cause_evidence_available
    checks.append({
        "field": "final_cause_timing",
        "passed": not premature_final_cause,
        "missing": ["final cause must wait for product/support evidence"] if premature_final_cause else [],
        "extra": [],
        "expected": "empty until context evidence exists",
        "actual": state.get("final_cause", ""),
    })

    passed = sum(1 for item in checks if item["passed"])
    total = len(checks)
    return {"passed": passed, "total": total, "checks": checks}


def run_fixture(fixture: dict[str, Any], mode: str = "deterministic", llm_command: str = "") -> dict[str, Any]:
    state = new_state(fixture["case_id"])
    context_by_turn: dict[int, list[dict[str, Any]]] = {}
    for event in fixture.get("context_events", []):
        context_by_turn.setdefault(int(event["after_turn"]), []).append(event)

    expected_by_turn = {int(item["after_turn"]): item for item in fixture["expected_by_turn"]}
    timeline = []
    root_cause_evidence_available = False

    for turn in fixture["transcript_turns"]:
        context_applied = context_by_turn.get(int(turn["turn"]), [])
        prompt = ""
        llm_patch = None
        llm_raw = ""

        if mode == "deterministic":
            process_turn(state, turn)
            for event in context_applied:
                apply_context_event(state, event)
        elif mode == "llm":
            prompt = build_llm_prompt(fixture, turn, deepcopy(state), context_applied)
            llm_patch, llm_raw = call_llm_command(llm_command, prompt)
            apply_state_patch(state, llm_patch, context_applied)
        else:
            raise ValueError(f"Unknown run mode: {mode}")

        if context_applied:
            root_cause_evidence_available = True

        expected = expected_by_turn.get(int(turn["turn"]))
        verdict = compare_state(state, expected, root_cause_evidence_available) if expected else None
        timeline.append({
            "turn": turn,
            "context_applied": context_applied,
            "state": deepcopy(state),
            "expected": expected,
            "verdict": verdict,
            "llm_prompt": prompt,
            "llm_patch": llm_patch,
            "llm_raw": llm_raw,
        })

    final_expected = fixture.get("final_cause", "")
    root_cause_ok = not final_expected or state.get("final_cause") == final_expected
    return {"fixture": fixture, "timeline": timeline, "final_state": state, "root_cause_ok": root_cause_ok, "mode": mode}


def generate_prompt_pack(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prompts = []
    for fixture in fixtures:
        state = new_state(fixture["case_id"])
        context_by_turn: dict[int, list[dict[str, Any]]] = {}
        for event in fixture.get("context_events", []):
            context_by_turn.setdefault(int(event["after_turn"]), []).append(event)

        for turn in fixture["transcript_turns"]:
            context_applied = context_by_turn.get(int(turn["turn"]), [])
            prompts.append({
                "case_id": fixture["case_id"],
                "turn": turn["turn"],
                "state_source": "deterministic_reference_previous_state",
                "prompt": build_llm_prompt(fixture, turn, deepcopy(state), context_applied),
            })
            process_turn(state, turn)
            for event in context_applied:
                apply_context_event(state, event)
    return prompts


def render_report(results: list[dict[str, Any]], run_label: str = "deterministic") -> str:
    lines = ["# Support Process Lab Report", ""]
    lines.append(f"Run: `{run_label}`")
    lines.append("")
    lines.append("Offline test of transcript + mock-system support process state.")
    lines.append("")

    summary_rows = []
    for result in results:
        total_passed = 0
        total_checks = 0
        for item in result["timeline"]:
            if item["verdict"]:
                total_passed += item["verdict"]["passed"]
                total_checks += item["verdict"]["total"]
        pct = round((total_passed / total_checks) * 100) if total_checks else 0
        summary_rows.append([
            result["fixture"]["case_id"],
            f"{total_passed}/{total_checks}",
            f"{pct}%",
            "yes" if result["root_cause_ok"] else "no",
            result["final_state"].get("final_cause", ""),
        ])
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(["case", "checks", "pass_rate", "final_cause_ok", "final_cause"], summary_rows))

    for result in results:
        fixture = result["fixture"]
        lines.append(f"## {fixture['title']}")
        lines.append("")
        rows = []
        for item in result["timeline"]:
            turn = item["turn"]
            state = item["state"]
            verdict = item["verdict"]
            missing = []
            if verdict:
                for check in verdict["checks"]:
                    if check["missing"]:
                        missing.append(f"{check['field']}: {', '.join(check['missing'])}")
            rows.append([
                turn["turn"],
                turn["speaker"],
                turn["text"],
                "; ".join(state["facts"]),
                "; ".join(state["unknowns"]),
                "; ".join(state["candidate_branches"]),
                state["next_check"],
                "pass" if verdict and verdict["passed"] == verdict["total"] else ("needs attention" if verdict else "observed"),
                "; ".join(missing) or "-",
            ])
        lines.append(markdown_table(["turn", "speaker", "text", "facts", "unknowns", "branches", "next_check", "status", "missing"], rows))
        lines.append("### Final State")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(result["final_state"], indent=2))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def render_dashboard(results: list[dict[str, Any]], run_label: str = "deterministic") -> str:
    summary_cards = ""
    case_sections = ""
    for result in results:
        fixture = result["fixture"]
        total_passed = 0
        total_checks = 0
        for item in result["timeline"]:
            if item["verdict"]:
                total_passed += item["verdict"]["passed"]
                total_checks += item["verdict"]["total"]
        pct = round((total_passed / total_checks) * 100) if total_checks else 0
        card_cls = "good" if pct >= 85 and result["root_cause_ok"] else "warn"
        summary_cards += f"""
        <div class="card {card_cls}">
          <div class="card-title">{esc(fixture['title'])}</div>
          <div class="metric">{total_passed}/{total_checks} checks</div>
          <div class="muted">Final cause: {esc(result['final_state'].get('final_cause', '-'))}</div>
        </div>"""

        rows = ""
        for item in result["timeline"]:
            turn = item["turn"]
            state = item["state"]
            verdict = item["verdict"]
            missing = []
            if verdict:
                for check in verdict["checks"]:
                    if check["missing"]:
                        missing.append(f"{check['field']}: {', '.join(check['missing'])}")
            status = "pass" if verdict and verdict["passed"] == verdict["total"] else ("needs attention" if verdict else "observed")
            status_cls = "pass" if status == "pass" else ("fail" if status == "needs attention" else "observed")
            context = item["context_applied"]
            context_text = "; ".join(event["description"] for event in context) if context else "-"
            rows += f"""
            <tr>
              <td>{esc(turn['turn'])}</td>
              <td class="text"><strong>{esc(turn['speaker'])}</strong>: {esc(turn['text'])}<div class="context">{esc(context_text)}</div></td>
              <td>{esc('; '.join(state['facts']) or '-')}</td>
              <td>{esc('; '.join(state['unknowns']) or '-')}</td>
              <td>{esc('; '.join(state['candidate_branches']) or '-')}</td>
              <td>{esc(state['next_check'] or '-')}</td>
              <td class="{status_cls}">{esc(status)}</td>
              <td>{esc('; '.join(missing) or '-')}</td>
            </tr>"""

        final_json = esc(json.dumps(result["final_state"], indent=2))
        case_sections += f"""
        <section>
          <h2>{esc(fixture['title'])}</h2>
          <p>{esc(fixture['scenario'])}</p>
          <div class="table-wrap"><table>
            <thead><tr><th>Turn</th><th>Input</th><th>Facts</th><th>Unknowns</th><th>Branches</th><th>Next Check</th><th>Status</th><th>Missing</th></tr></thead>
            <tbody>{rows}</tbody>
          </table></div>
          <h3>Final State</h3>
          <pre>{final_json}</pre>
        </section>"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Support Process Lab</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#101318; color:#e5e7eb; margin:0; padding:32px; }}
h1 {{ font-size:24px; margin-bottom:8px; }}
p {{ color:#9ca3af; max-width:860px; }}
.summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:24px 0 34px; }}
.card {{ border:1px solid #2f3746; background:#161b24; border-radius:8px; padding:14px 16px; }}
.card.good {{ border-color:#166534; }}
.card.warn {{ border-color:#92400e; }}
.card-title {{ font-weight:700; margin-bottom:8px; }}
.metric {{ font-size:22px; color:#f8fafc; }}
.muted, .context {{ color:#94a3b8; font-size:12px; margin-top:4px; }}
section {{ border-top:1px solid #2f3746; padding-top:28px; margin-top:34px; }}
h2 {{ font-size:18px; margin-bottom:6px; }}
h3 {{ font-size:13px; color:#cbd5e1; text-transform:uppercase; letter-spacing:.08em; margin-top:18px; }}
.table-wrap {{ overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ color:#94a3b8; text-align:left; border-bottom:1px solid #374151; padding:8px; white-space:nowrap; }}
td {{ border-bottom:1px solid #222b38; padding:8px; vertical-align:top; min-width:110px; }}
td.text {{ min-width:260px; color:#f8fafc; }}
.pass {{ color:#22c55e; font-weight:700; }}
.fail {{ color:#f59e0b; font-weight:700; }}
.observed {{ color:#94a3b8; font-weight:700; }}
pre {{ background:#0b0e13; border:1px solid #2f3746; border-radius:8px; padding:14px; overflow:auto; color:#cbd5e1; }}
</style>
</head>
<body>
<h1>Support Process Lab</h1>
<p><strong>Run:</strong> {esc(run_label)}</p>
<p>Offline test of LTS-style support process state. Transcript-only replay proves plumbing; transcript plus mock system context is the product-relevant mode.</p>
<div class="summary">{summary_cards}</div>
{case_sections}
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Support Process Lab.")
    parser.add_argument(
        "--mode",
        choices=("deterministic", "prompt-pack", "llm"),
        default="deterministic",
        help="deterministic runs fixture rules; prompt-pack writes LLM prompts; llm calls --llm-command for JSON state patches.",
    )
    parser.add_argument(
        "--llm-command",
        default="",
        help="Command to call in llm mode. The prompt is sent on stdin; JSON patch must be printed on stdout.",
    )
    parser.add_argument(
        "--run-name",
        default="",
        help="Optional output name, for example process_mock or predictive_mock.",
    )
    args = parser.parse_args()

    out_dir = ensure_output_dir()
    fixtures = load_fixtures()

    if args.mode == "prompt-pack":
        prompts = generate_prompt_pack(fixtures)
        path = out_dir / "support_process_llm_prompts.jsonl"
        path.write_text("\n".join(json.dumps(item) for item in prompts) + "\n")
        print(f"Wrote {path}")
        return

    if args.mode == "llm" and not args.llm_command:
        raise SystemExit("--llm-command is required when --mode llm")

    results = [run_fixture(fixture, mode=args.mode, llm_command=args.llm_command) for fixture in fixtures]
    run_label = args.run_name or args.mode
    paths = output_paths(out_dir, args.run_name, args.mode)

    paths["snapshots"].write_text(json.dumps(results, indent=2))
    paths["report"].write_text(render_report(results, run_label=run_label))
    paths["dashboard"].write_text(render_dashboard(results, run_label=run_label))

    print(f"Wrote {paths['snapshots']}")
    print(f"Wrote {paths['report']}")
    print(f"Wrote {paths['dashboard']}")


if __name__ == "__main__":
    main()

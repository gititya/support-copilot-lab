#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import FIXTURE_DIR, OUTPUT_DIR, ensure_output_dir
from run import run_fixture

SIMULATOR_PATH = OUTPUT_DIR / "support_live_simulator.html"
CASE_ID = "level2_conflicting_migration_context"

# ---------------------------------------------------------------------------
# Deterministic fixture pipeline. `build_simulator_data()` is retained as the
# auditable, harness-backed projection of the migration case (covered by the
# experiment tests). The rendered HTML below is driven instead by the polished
# `CASES` design data island.
# ---------------------------------------------------------------------------

FACT_TEXT = {
    "affected_scope:three_users": "Three users are affected.",
    "app_entitlement_plan:starter": "The app still shows the Starter entitlement.",
    "auth:works": "The affected users can sign in.",
    "billing_refresh:pending": "The billing entitlement refresh is still pending.",
    "correction:login_works": "The customer corrected the first report: login works.",
    "domain_policy:dmarc_reject": "The recipient domain rejected the message by DMARC policy.",
    "email_delivery:suppressed": "Email delivery was suppressed.",
    "entitlement_cache:stale": "The entitlement cache is stale for the affected users.",
    "flow:admin_invite": "This is an admin invite flow.",
    "group_membership:Migrated-CSM": "The affected users are in the Migrated-CSM group.",
    "invite_status:created": "The invite exists in the admin system.",
    "invoice_plan:pro": "The invoice shows the Pro plan.",
    "recent_change:migration": "The issue appeared after a migration.",
    "recent_change:upgrade": "The issue appeared after an upgrade.",
    "reported_issue:login": "The customer initially described the issue as login failure.",
    "scim_sync:complete": "SCIM sync has completed.",
    "surface:billing_plan": "The visible issue is on the billing page.",
    "surface:workspace_access": "The visible issue is workspace access.",
    "symptom:invite_email_not_received": "The invite email is not arriving.",
    "symptom:workspace_access_loss": "The customer reports workspace access loss.",
    "symptom:wrong_plan_shown": "The customer sees the wrong plan.",
    "workspace_role_missing:Migrated-CSM": "Migrated-CSM is missing the workspace role.",
    "workspace_role:present": "The workspace role is present.",
}

UNKNOWN_TEXT = {
    "actual_surface": "Which product surface is actually failing?",
    "auth_status": "Can the affected users sign in?",
    "billing_entitlement_status": "Has the billing entitlement refresh completed?",
    "cache_status": "Is cached entitlement state still blocking access?",
    "email_delivery_status": "Did the invite email actually reach the recipient?",
    "invite_created": "Was the invite created successfully?",
    "workspace_role_assignment": "Do affected users have the right workspace role?",
}

CAUSE_TEXT = {
    "billing_entitlement_refresh_pending": "billing entitlement refresh is still pending",
    "domain_policy_rejection": "recipient-domain policy is rejecting the email",
    "email_delivery_suppressed": "email delivery is suppressed",
    "invite_not_created": "the invite was not created",
    "invoice_app_mismatch": "invoice and app entitlement do not match",
    "login_block": "login is blocked",
    "login_failure": "login is failing",
    "missing_workspace_role": "the workspace role is missing",
    "missing_workspace_role_inheritance": "the migrated group did not inherit the workspace role",
    "scim_sync_delay": "SCIM sync has not completed",
    "stale_entitlement_cache": "stale entitlement cache",
    "upstream_service_incident": "an upstream service issue",
}

ROUTE_STAGES = [
    "Intake",
    "Clarify issue",
    "Check context",
    "Narrow cause",
    "Resolve or hand off",
]


def load_fixture(case_id: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{case_id}.json"
    if not path.exists():
        raise SystemExit(f"Missing fixture: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def readable_label(label: str) -> str:
    if label in FACT_TEXT:
        return FACT_TEXT[label]
    if label in UNKNOWN_TEXT:
        return UNKNOWN_TEXT[label]
    if label in CAUSE_TEXT:
        return CAUSE_TEXT[label]
    return label.replace("_", " ").replace(":", " ")


def translate_list(values: list[str]) -> list[str]:
    return [readable_label(value) for value in values]


def context_summary(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for event in events:
        summaries.append({
            "description": event.get("description", ""),
            "facts": translate_list(event.get("facts", [])),
            "relevant": event.get("relevant", True),
        })
    return summaries


def final_outcome(state: dict[str, Any]) -> str:
    cause = state.get("final_cause", "")
    if not cause:
        return "Not ready yet. The copilot should keep investigating instead of naming a final cause."
    return f"Evidence now supports the final outcome: {readable_label(cause)}."


def state_for_display(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "known_facts": translate_list(state.get("facts", [])),
        "still_unknown": translate_list(state.get("unknowns", [])),
        "possible_causes": translate_list(state.get("candidate_branches", [])),
        "ruled_out": translate_list(state.get("ruled_out_branches", [])),
        "next_best_action": state.get("next_check", ""),
        "final_outcome": final_outcome(state),
        "raw": state,
    }


def route_stage(turn: dict[str, Any], state: dict[str, Any], context_events: list[dict[str, Any]]) -> str:
    turn_number = int(turn.get("turn", 0))
    if state.get("final_cause"):
        return "Resolve or hand off"
    if context_events:
        return "Check context"
    if turn_number >= 4:
        return "Narrow cause"
    if turn_number >= 2:
        return "Clarify issue"
    return "Intake"


def handoff_readiness(state: dict[str, Any]) -> dict[str, Any]:
    facts = state.get("facts", [])
    unknowns = state.get("unknowns", [])
    ruled_out = state.get("ruled_out_branches", [])
    next_check = state.get("next_check", "")
    final_cause = state.get("final_cause", "")
    issue_clear = any(fact.startswith("symptom:") or fact.startswith("surface:") for fact in facts)
    checks = [
        {
            "label": "Customer issue is clear",
            "ready": issue_clear,
            "detail": "The handoff names the customer-visible problem." if issue_clear else "Keep clarifying the customer-visible problem.",
        },
        {
            "label": "Known facts are captured",
            "ready": bool(facts),
            "detail": "The next owner can see the facts gathered so far." if facts else "Capture at least one durable fact before handoff.",
        },
        {
            "label": "Open questions are visible",
            "ready": bool(unknowns) or bool(final_cause),
            "detail": "Remaining uncertainty is visible." if unknowns else "No blocking unknowns remain.",
        },
        {
            "label": "Ruled-out paths are preserved",
            "ready": bool(ruled_out),
            "detail": "The next owner can avoid rechecking paths already ruled out." if ruled_out else "Nothing has been ruled out yet.",
        },
        {
            "label": "Next action is specific",
            "ready": bool(next_check),
            "detail": next_check or "Add the next best check before handing off.",
        },
        {
            "label": "Final cause is evidence-supported",
            "ready": bool(final_cause and state.get("root_cause_evidence_seen")) or not final_cause,
            "detail": "Final cause is supported by product context." if final_cause else "No final cause is included yet.",
        },
    ]
    ready_count = sum(1 for check in checks if check["ready"])
    if final_cause and ready_count == len(checks):
        status = "Ready to close or hand off with supported outcome."
    elif not ruled_out:
        status = "Not ready for handoff yet."
    elif ready_count >= 4:
        status = "Usable if the case must move, but keep unresolved checks attached."
    else:
        status = "Not ready for handoff yet."
    return {
        "status": status,
        "ready_count": ready_count,
        "total": len(checks),
        "checks": checks,
    }


def evidence_events_for_turn(
    item: dict[str, Any],
    previous_state: dict[str, Any] | None,
) -> list[dict[str, str]]:
    turn = item["turn"]
    state = item["state"]
    events = [{
        "kind": "Conversation",
        "title": f"Turn {turn.get('turn')}: {turn.get('speaker', 'speaker').title()} update",
        "body": turn.get("text", ""),
    }]
    for context in item.get("context_applied", []):
        if context.get("relevant", True):
            body = context.get("description", "Product or support context arrived.")
        else:
            body = context.get("description", "Context arrived but was not relevant to this case.")
        events.append({
            "kind": "Product context",
            "title": f"After turn {turn.get('turn')}: context arrived",
            "body": body,
        })

    before = previous_state or {
        "facts": [],
        "unknowns": [],
        "ruled_out_branches": [],
        "final_cause": "",
    }
    added_facts = [fact for fact in state.get("facts", []) if fact not in before.get("facts", [])]
    resolved_unknowns = [unknown for unknown in before.get("unknowns", []) if unknown not in state.get("unknowns", [])]
    ruled_out = [
        branch
        for branch in state.get("ruled_out_branches", [])
        if branch not in before.get("ruled_out_branches", [])
    ]
    final_cause = state.get("final_cause", "")
    previous_final_cause = before.get("final_cause", "")

    if added_facts:
        events.append({
            "kind": "Facts added",
            "title": "Known facts changed",
            "body": "; ".join(translate_list(added_facts)),
        })
    if resolved_unknowns:
        events.append({
            "kind": "Unknown resolved",
            "title": "Open question closed",
            "body": "; ".join(translate_list(resolved_unknowns)),
        })
    if ruled_out:
        events.append({
            "kind": "Ruled out",
            "title": "Cause narrowed",
            "body": "; ".join(translate_list(ruled_out)),
        })
    if final_cause and final_cause != previous_final_cause:
        events.append({
            "kind": "Final outcome",
            "title": "Final cause is now supported",
            "body": readable_label(final_cause),
        })
    return events


def build_simulator_data(case_id: str = CASE_ID) -> dict[str, Any]:
    fixture = load_fixture(case_id)
    result = run_fixture(fixture, mode="deterministic")
    steps = []
    conversation_so_far: list[dict[str, Any]] = []
    evidence_timeline: list[dict[str, str]] = []
    previous_state = None
    for item in result["timeline"]:
        turn = item["turn"]
        evidence_timeline.extend(evidence_events_for_turn(item, previous_state))
        previous_state = item["state"]
        conversation_so_far.append({
            "speaker": turn.get("speaker", "speaker"),
            "text": turn.get("text", ""),
        })
        steps.append({
            "turn": turn.get("turn"),
            "speaker": turn.get("speaker", ""),
            "route_stage": route_stage(turn, item["state"], item.get("context_applied", [])),
            "route_stages": ROUTE_STAGES,
            "conversation": list(conversation_so_far),
            "new_context": context_summary(item.get("context_applied", [])),
            "evidence_timeline": list(evidence_timeline),
            "handoff_readiness": handoff_readiness(item["state"]),
            "state": state_for_display(item["state"]),
        })
    return {
        "case_id": fixture["case_id"],
        "title": "Workspace access after migration",
        "subtitle": "A realistic support replay where the tempting early answer is wrong until product context arrives.",
        "customer": "B2B admin account",
        "steps": steps,
    }


# Withheld-outcome copy shared by every locked turn.
NOT_READY = "Holding the diagnosis. The final root cause stays withheld until product or support evidence supports it."

# Three cases, transcribed verbatim from the kora design reference
# (copilot_claude-design/Support Copilot Live.dc.html data island). The per-turn
# state shape matches the live support harness so it can be swapped for a feed.
CASES: dict[str, Any] = {
    "migration": {
        "chip": "Migration access",
        "title": "Workspace access after migration",
        "scenario": "Three users can sign in but cannot open the new workspace after a migration. The tempting early answer is wrong until product context arrives.",
        "steps": [
            {
                "turn": 1,
                "conversation": [
                    {"speaker": "customer", "text": "Three users lost access after our migration yesterday."},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["The customer reports workspace access loss.", "Three users are affected.", "The issue appeared after a migration."],
                    "still_unknown": ["Can the affected users sign in?", "Do affected users have the right workspace role?"],
                    "possible_causes": ["login is blocked", "the workspace role is missing", "SCIM sync has not completed", "stale entitlement cache"],
                    "ruled_out": [],
                    "next_best_action": "Can the affected users sign in, or are they blocked at login?",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 2,
                "conversation": [
                    {"speaker": "customer", "text": "Three users lost access after our migration yesterday."},
                    {"speaker": "agent", "text": "Can they sign in at all, or is login blocked?"},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["The customer reports workspace access loss.", "Three users are affected.", "The issue appeared after a migration."],
                    "still_unknown": ["Can the affected users sign in?", "Do affected users have the right workspace role?"],
                    "possible_causes": ["login is blocked", "the workspace role is missing", "SCIM sync has not completed", "stale entitlement cache"],
                    "ruled_out": [],
                    "next_best_action": "Can the affected users sign in, or are they blocked at login?",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 3,
                "conversation": [
                    {"speaker": "customer", "text": "Three users lost access after our migration yesterday."},
                    {"speaker": "agent", "text": "Can they sign in at all, or is login blocked?"},
                    {"speaker": "customer", "text": "They can sign in, and they reach the workspace switcher, but the new workspace will not open."},
                ],
                "new_context": [
                    {"description": "Admin context shows Migrated-CSM has the workspace role and SCIM completed.", "facts": ["The workspace role is present.", "SCIM sync has completed."], "relevant": True},
                ],
                "state": {
                    "known_facts": ["The customer reports workspace access loss.", "Three users are affected.", "The issue appeared after a migration.", "The affected users can sign in.", "The visible issue is workspace access.", "The workspace role is present.", "SCIM sync has completed."],
                    "still_unknown": ["Is cached entitlement state still blocking access?"],
                    "possible_causes": ["stale entitlement cache"],
                    "ruled_out": ["login is blocked", "login is failing", "the workspace role is missing", "the migrated group did not inherit the workspace role", "SCIM sync has not completed"],
                    "next_best_action": "Check entitlement cache status before naming a final cause.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 4,
                "conversation": [
                    {"speaker": "customer", "text": "Three users lost access after our migration yesterday."},
                    {"speaker": "agent", "text": "Can they sign in at all, or is login blocked?"},
                    {"speaker": "customer", "text": "They can sign in, and they reach the workspace switcher, but the new workspace will not open."},
                    {"speaker": "agent", "text": "I am checking the migrated group role and entitlement cache now."},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["The customer reports workspace access loss.", "Three users are affected.", "The issue appeared after a migration.", "The affected users can sign in.", "The visible issue is workspace access.", "The workspace role is present.", "SCIM sync has completed."],
                    "still_unknown": ["Is cached entitlement state still blocking access?"],
                    "possible_causes": ["stale entitlement cache"],
                    "ruled_out": ["login is blocked", "login is failing", "the workspace role is missing", "the migrated group did not inherit the workspace role", "SCIM sync has not completed"],
                    "next_best_action": "Check entitlement cache status before naming a final cause.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 5,
                "conversation": [
                    {"speaker": "customer", "text": "Three users lost access after our migration yesterday."},
                    {"speaker": "agent", "text": "Can they sign in at all, or is login blocked?"},
                    {"speaker": "customer", "text": "They can sign in, and they reach the workspace switcher, but the new workspace will not open."},
                    {"speaker": "agent", "text": "I am checking the migrated group role and entitlement cache now."},
                    {"speaker": "customer", "text": "It still fails after they refresh their sessions."},
                ],
                "new_context": [
                    {"description": "Entitlement service shows the migrated workspace role is correct, but the entitlement cache remains stale for the three affected users.", "facts": ["The entitlement cache is stale for the affected users."], "relevant": True},
                ],
                "state": {
                    "known_facts": ["The customer reports workspace access loss.", "Three users are affected.", "The issue appeared after a migration.", "The affected users can sign in.", "The visible issue is workspace access.", "The workspace role is present.", "SCIM sync has completed.", "The entitlement cache is stale for the affected users."],
                    "still_unknown": [],
                    "possible_causes": ["stale entitlement cache"],
                    "ruled_out": ["login is blocked", "login is failing", "the workspace role is missing", "the migrated group did not inherit the workspace role", "SCIM sync has not completed"],
                    "next_best_action": "Refresh the entitlement cache and confirm workspace access works after refresh.",
                    "final_outcome": "Evidence supports the final cause: stale entitlement cache. Refresh the cache and confirm access after refresh.",
                    "final_cause_text": "stale entitlement cache",
                    "evidence_seen": True,
                },
            },
        ],
    },
    "billing": {
        "chip": "Billing mismatch",
        "title": "Wrong plan after upgrade",
        "scenario": "The customer first reports a login problem, then corrects it: login works, but the billing page shows the wrong plan. The copilot has to revise the surface, not the symptom.",
        "steps": [
            {
                "turn": 1,
                "conversation": [
                    {"speaker": "customer", "text": "I cannot log in."},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["The customer initially described the issue as login failure."],
                    "still_unknown": ["Which product surface is actually failing?"],
                    "possible_causes": ["login is failing"],
                    "ruled_out": [],
                    "next_best_action": "Pin down where it fails — is login itself blocked, or does a page after login show the problem?",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 2,
                "conversation": [
                    {"speaker": "customer", "text": "I cannot log in."},
                    {"speaker": "customer", "text": "No, login works. The billing page shows the wrong plan."},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["The customer corrected the first report: login works.", "The visible issue is on the billing page.", "The customer sees the wrong plan."],
                    "still_unknown": ["Has the billing entitlement refresh completed?"],
                    "possible_causes": ["billing entitlement refresh is still pending", "invoice and app entitlement do not match"],
                    "ruled_out": ["login is failing"],
                    "next_best_action": "Compare the invoice plan against the live app entitlement and check the refresh job.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 3,
                "conversation": [
                    {"speaker": "customer", "text": "I cannot log in."},
                    {"speaker": "customer", "text": "No, login works. The billing page shows the wrong plan."},
                    {"speaker": "agent", "text": "When did the plan change?"},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["The customer corrected the first report: login works.", "The visible issue is on the billing page.", "The customer sees the wrong plan."],
                    "still_unknown": ["Has the billing entitlement refresh completed?"],
                    "possible_causes": ["billing entitlement refresh is still pending", "invoice and app entitlement do not match"],
                    "ruled_out": ["login is failing"],
                    "next_best_action": "Compare the invoice plan against the live app entitlement and check the refresh job.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 4,
                "conversation": [
                    {"speaker": "customer", "text": "I cannot log in."},
                    {"speaker": "customer", "text": "No, login works. The billing page shows the wrong plan."},
                    {"speaker": "agent", "text": "When did the plan change?"},
                    {"speaker": "customer", "text": "We upgraded yesterday."},
                ],
                "new_context": [
                    {"description": "Billing context shows the invoice has Pro, the app entitlement still shows Starter, and the entitlement refresh is pending.", "facts": ["The invoice shows the Pro plan.", "The app still shows the Starter entitlement.", "The billing entitlement refresh is still pending."], "relevant": True},
                ],
                "state": {
                    "known_facts": ["The customer corrected the first report: login works.", "The visible issue is on the billing page.", "The customer sees the wrong plan.", "The issue appeared after an upgrade.", "The invoice shows the Pro plan.", "The app still shows the Starter entitlement.", "The billing entitlement refresh is still pending."],
                    "still_unknown": [],
                    "possible_causes": ["billing entitlement refresh is still pending"],
                    "ruled_out": ["login is failing", "invoice and app entitlement do not match"],
                    "next_best_action": "Re-run the billing entitlement refresh, then confirm the app shows the Pro plan.",
                    "final_outcome": "Evidence supports the final cause: the billing entitlement refresh is still pending. Re-run the refresh and re-sync the plan.",
                    "final_cause_text": "billing entitlement refresh is still pending",
                    "evidence_seen": True,
                },
            },
        ],
    },
    "invite": {
        "chip": "Invite delivery",
        "title": "Invite email never arrives",
        "scenario": "An admin invite is sent but the email never lands. An unrelated billing signal appears first and must be ignored; the real mechanism arrives later.",
        "steps": [
            {
                "turn": 1,
                "conversation": [
                    {"speaker": "customer", "text": "I sent an admin invite but the email never arrives."},
                ],
                "new_context": [
                    {"description": "Billing context reports the invoice plan is Pro. This is unrelated to invite email delivery.", "facts": ["The invoice shows the Pro plan."], "relevant": False},
                ],
                "state": {
                    "known_facts": ["This is an admin invite flow.", "The invite email is not arriving."],
                    "still_unknown": ["Was the invite created successfully?", "Did the invite email actually reach the recipient?"],
                    "possible_causes": ["the invite was not created", "email delivery is suppressed", "recipient-domain policy is rejecting the email"],
                    "ruled_out": [],
                    "next_best_action": "Check whether the invite was created and whether delivery bounced or was suppressed.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 2,
                "conversation": [
                    {"speaker": "customer", "text": "I sent an admin invite but the email never arrives."},
                    {"speaker": "agent", "text": "I am checking whether the invite was created and whether delivery bounced."},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["This is an admin invite flow.", "The invite email is not arriving."],
                    "still_unknown": ["Was the invite created successfully?", "Did the invite email actually reach the recipient?"],
                    "possible_causes": ["the invite was not created", "email delivery is suppressed", "recipient-domain policy is rejecting the email"],
                    "ruled_out": [],
                    "next_best_action": "Check whether the invite was created and whether delivery bounced or was suppressed.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 3,
                "conversation": [
                    {"speaker": "customer", "text": "I sent an admin invite but the email never arrives."},
                    {"speaker": "agent", "text": "I am checking whether the invite was created and whether delivery bounced."},
                    {"speaker": "customer", "text": "The recipient checked spam and still does not see the invite email."},
                ],
                "new_context": [],
                "state": {
                    "known_facts": ["This is an admin invite flow.", "The invite email is not arriving."],
                    "still_unknown": ["Was the invite created successfully?", "Did the invite email actually reach the recipient?"],
                    "possible_causes": ["the invite was not created", "email delivery is suppressed", "recipient-domain policy is rejecting the email"],
                    "ruled_out": [],
                    "next_best_action": "Check the suppression list and whether the recipient domain rejected the message.",
                    "final_outcome": NOT_READY,
                    "final_cause_text": "",
                    "evidence_seen": False,
                },
            },
            {
                "turn": 4,
                "conversation": [
                    {"speaker": "customer", "text": "I sent an admin invite but the email never arrives."},
                    {"speaker": "agent", "text": "I am checking whether the invite was created and whether delivery bounced."},
                    {"speaker": "customer", "text": "The recipient checked spam and still does not see the invite email."},
                    {"speaker": "agent", "text": "I am checking suppression and recipient-domain policy now."},
                ],
                "new_context": [
                    {"description": "Email delivery context shows the invite was created, delivery was suppressed, and the recipient domain rejected the message by DMARC policy.", "facts": ["The invite exists in the admin system.", "Email delivery was suppressed.", "The recipient domain rejected the message by DMARC policy."], "relevant": True},
                ],
                "state": {
                    "known_facts": ["This is an admin invite flow.", "The invite email is not arriving.", "The invite exists in the admin system.", "Email delivery was suppressed.", "The recipient domain rejected the message by DMARC policy."],
                    "still_unknown": [],
                    "possible_causes": ["recipient-domain policy is rejecting the email", "email delivery is suppressed"],
                    "ruled_out": ["the invite was not created"],
                    "next_best_action": "Inspect email suppression and the recipient domain's DMARC policy, then ask the customer to allowlist the sender.",
                    "final_outcome": "Evidence supports the final cause: the recipient domain rejected the message by DMARC policy.",
                    "final_cause_text": "recipient-domain policy is rejecting the email",
                    "evidence_seen": True,
                },
            },
        ],
    },
}

DEFAULT_CASE = "migration"


def json_script(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=True).replace("</", "<\\/")


def render_live_simulator(cases: dict[str, Any]) -> str:
    data_island = json_script({"cases": cases, "defaultCase": DEFAULT_CASE})
    return _HTML.replace("__SIMULATOR_DATA__", data_island)


# kora design: warm near-black surfaces, Cormorant display, DM Mono labels,
# a single teal accent. Tokens are inlined here (the design's _ds bundle is
# prototyping plumbing we deliberately do not pull in).
_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Real-time Support Copilot · Live Replay</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300;0,400;1,300&family=DM+Mono:wght@300;400&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg-0: #0d0c0b;
  --bg-1: #131210;
  --bg-2: #1a1815;
  --bg-3: #242220;
  --bg-4: #2e2c29;
  --text-primary: #ede8e1;
  --text-secondary: #8c877f;
  --text-tertiary: #4a4740;
  --text-inverse: #0d0c0b;
  --border-subtle: rgba(255,255,255,.06);
  --border-mid: rgba(255,255,255,.10);
  --border-strong: rgba(255,255,255,.18);
  --accent: #4ECDC4;
  --accent-dim: rgba(78,205,196,.10);
  --accent-mid: rgba(78,205,196,.22);
  --accent-border: rgba(78,205,196,.35);
  --accent-text: #4ECDC4;
  --font-display: "Cormorant", Georgia, serif;
  --font-mono: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  --font-sans: "DM Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
html, body { margin: 0; height: 100%; }
* { box-sizing: border-box; }
body { background: var(--bg-0); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.07); border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.12); }
@keyframes enterUp { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: none; } }
@keyframes evPop { from { opacity: 0; transform: translateY(9px); } to { opacity: 1; transform: none; } }
@keyframes livePulse { 0%,100% { opacity: .3; transform: scale(.85); } 50% { opacity: 1; transform: scale(1.1); } }
details > summary { list-style: none; }
details > summary::-webkit-details-marker { display: none; }
button { font: inherit; }
@media (max-width: 880px) {
  main { grid-template-columns: 1fr !important; }
  main > section:first-child { border-right: 0 !important; border-bottom: 1px solid var(--border-subtle); }
}
</style>
</head>
<body>
<div id="app" style="height:100vh;display:flex;flex-direction:column;background:var(--bg-0);color:var(--text-primary);font-family:var(--font-sans);overflow:hidden;"></div>

<script id="simulator-data" type="application/json">__SIMULATOR_DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById("simulator-data").textContent);
const CASES = DATA.cases;
const S = { caseId: DATA.defaultCase || "migration", index: 0, advancing: false };
const app = document.getElementById("app");

const ICON_NEXT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--accent-text);flex:none;"><circle cx="12" cy="12" r="10"></circle><path d="m12 16 4-4-4-4"></path><path d="M8 12h8"></path></svg>';
const ICON_CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--accent-text);flex:none;"><path d="M20 6 9 17l-5-5"></path></svg>';
const ICON_LOCK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-secondary);flex:none;"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>';
const ICON_LOCK_OPEN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--accent-text);flex:none;"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>';

function esc(value) {
  return String(value == null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusOf(state, t) {
  if (state.evidence_seen && t === state.final_cause_text) return "confirmed";
  if (state.ruled_out.includes(t)) return "ruled";
  return "live";
}

function goCase(k) {
  if (k === S.caseId) return;
  S.caseId = k; S.index = 0; S.advancing = false; render();
}
function stepPrev() { if (S.index > 0) { S.index -= 1; S.advancing = false; render(); } }
function stepNext() {
  const c = CASES[S.caseId];
  if (S.index < c.steps.length - 1) { S.index += 1; S.advancing = true; render(); }
}

window.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") { e.preventDefault(); stepNext(); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); stepPrev(); }
});

function render() {
  const c = CASES[S.caseId];
  const i = S.index;
  const step = c.steps[i];
  const prev = i > 0 ? c.steps[i - 1] : null;
  const st = step.state;
  const advancing = S.advancing && !!prev; // animate only when stepping forward

  // ---- header case chips ----
  const chips = Object.keys(CASES).map((k) => {
    const active = k === S.caseId;
    const style = "padding:7px 14px;border-radius:8px;font-family:var(--font-sans);font-size:12px;cursor:pointer;white-space:nowrap;transition:all 120ms ease;border:1px solid " +
      (active ? "var(--accent-border)" : "var(--border-subtle)") + ";background:" +
      (active ? "var(--accent-dim)" : "transparent") + ";color:" +
      (active ? "var(--accent-text)" : "var(--text-secondary)") + ";";
    return '<button type="button" data-case="' + k + '" style="' + style + '">' + esc(CASES[k].chip) + "</button>";
  }).join("");

  // ---- conversation ----
  const lastIdx = step.conversation.length - 1;
  const conversation = step.conversation.map((m, idx) => {
    const agent = m.speaker === "agent";
    const isLast = idx === lastIdx;
    const containerStyle = "border:1px solid " + (agent ? "var(--border-mid)" : "var(--border-subtle)") +
      ";background:" + (agent ? "var(--bg-2)" : "var(--bg-1)") +
      ";border-radius:12px;padding:13px 15px;" + (isLast && advancing ? "animation:enterUp 280ms ease both;" : "");
    const speakerStyle = "font-family:var(--font-mono);font-size:10px;letter-spacing:.14em;margin-bottom:7px;color:" +
      (agent ? "var(--accent-text)" : "var(--text-secondary)") + ";";
    return '<article style="' + containerStyle + '">' +
      '<div style="' + speakerStyle + '">' + (agent ? "AGENT" : "CUSTOMER") + "</div>" +
      '<p style="margin:0;line-height:1.5;font-size:14px;color:var(--text-primary);text-wrap:pretty;">' + esc(m.text) + "</p>" +
      "</article>";
  }).join("");

  // ---- known facts ----
  const pf = prev ? prev.state.known_facts : [];
  const facts = st.known_facts.map((t) => {
    const style = "display:flex;gap:10px;align-items:flex-start;line-height:1.5;color:rgba(237,232,225,.86);font-size:13.5px;" +
      (advancing && !pf.includes(t) ? "animation:enterUp 300ms ease both;" : "");
    return '<div style="' + style + '"><span style="color:var(--accent-text);font-family:var(--font-mono);font-size:13px;line-height:1.2;flex:none;">—</span><span>' + esc(t) + "</span></div>";
  }).join("");

  // ---- still unknown ----
  const pu = prev ? prev.state.still_unknown : [];
  const unknowns = st.still_unknown.map((t) => {
    const style = "display:flex;gap:9px;align-items:flex-start;line-height:1.5;color:var(--text-secondary);font-size:13.5px;" +
      (advancing && !pu.includes(t) ? "animation:enterUp 300ms ease both;" : "");
    return '<div style="' + style + '"><span style="color:var(--text-tertiary);font-family:var(--font-mono);font-size:13px;line-height:1.2;flex:none;">?</span><span>' + esc(t) + "</span></div>";
  }).join("");
  const unknownsEmpty = st.still_unknown.length === 0;
  const unknownsBlock = (unknownsEmpty
    ? '<div style="display:flex;gap:9px;align-items:center;color:var(--accent-text);font-size:13px;">' + ICON_CHECK + "<span>all blocking unknowns resolved</span></div>"
    : "") + unknowns;

  // ---- working hypotheses (stable first-appearance order across all steps) ----
  const seen = [];
  c.steps.forEach((s) => {
    [...s.state.possible_causes, ...s.state.ruled_out].forEach((t) => { if (!seen.includes(t)) seen.push(t); });
  });
  const present = new Set([...st.possible_causes, ...st.ruled_out]);
  const prevStat = {};
  if (prev) {
    [...prev.state.possible_causes, ...prev.state.ruled_out].forEach((t) => { prevStat[t] = statusOf(prev.state, t); });
  }
  let liveCount = 0, ruledCount = 0, confCount = 0;
  const hyps = seen.filter((t) => present.has(t)).map((t) => {
    const status = statusOf(st, t);
    if (status === "live") liveCount++; else if (status === "ruled") ruledCount++; else confCount++;
    const changed = prev ? prevStat[t] !== status : false;
    let rowStyle = "display:flex;align-items:center;gap:11px;padding:11px 10px;border-radius:8px;transition:background 200ms ease;";
    let dot, textStyle, tagText, tagInner;
    if (status === "confirmed") {
      rowStyle += "background:var(--accent-dim);";
      dot = "background:var(--accent);";
      textStyle = "flex:1;color:var(--text-primary);font-size:14px;font-weight:500;";
      tagText = "CONFIRMED"; tagInner = "color:var(--accent-text);border:1px solid var(--accent-border);";
    } else if (status === "ruled") {
      dot = "background:transparent;border:1px solid var(--text-tertiary);";
      textStyle = "flex:1;color:var(--text-tertiary);font-size:13.5px;text-decoration:line-through;";
      tagText = "RULED OUT"; tagInner = "color:var(--text-tertiary);border:1px solid var(--border-subtle);";
    } else {
      dot = "background:var(--text-secondary);";
      textStyle = "flex:1;color:var(--text-primary);font-size:13.5px;";
      tagText = "OPEN"; tagInner = "color:var(--text-secondary);border:1px solid var(--border-subtle);";
    }
    if (advancing && changed) rowStyle += "animation:enterUp 320ms ease both;";
    return '<div style="' + rowStyle + '">' +
      '<span style="width:7px;height:7px;border-radius:50%;flex:none;' + dot + '"></span>' +
      '<span style="' + textStyle + '">' + esc(t) + "</span>" +
      '<span style="font-family:var(--font-mono);font-size:9px;letter-spacing:.1em;padding:3px 7px;border-radius:5px;white-space:nowrap;' + tagInner + '">' + tagText + "</span>" +
      "</div>";
  }).join("");
  const hypSummary = liveCount + " open · " + ruledCount + " ruled out" + (confCount ? " · " + confCount + " confirmed" : "");

  // ---- product & support context ----
  const hasCtx = step.new_context.length > 0;
  const ctx = step.new_context.map((e) => {
    const boxStyle = e.relevant
      ? "background:var(--bg-2);border:1px solid var(--border-mid);border-radius:10px;padding:14px 15px;" + (advancing ? "animation:evPop 340ms ease both;" : "")
      : "background:transparent;border:1px dashed var(--border-mid);border-radius:10px;padding:14px 15px;opacity:.6;";
    const tagStyle = "font-family:var(--font-mono);font-size:9.5px;letter-spacing:.12em;padding:3px 8px;border-radius:5px;" +
      (e.relevant ? "color:var(--accent-text);border:1px solid var(--accent-border);" : "color:var(--text-tertiary);border:1px solid var(--border-subtle);");
    const descStyle = "margin:9px 0 0;line-height:1.5;font-size:13.5px;color:" + (e.relevant ? "var(--text-primary)" : "var(--text-secondary)") + ";";
    const factStyle = "font-family:var(--font-mono);font-size:11.5px;line-height:1.45;color:" +
      (e.relevant ? "var(--accent-text)" : "var(--text-tertiary)") + ";" + (e.relevant ? "" : "text-decoration:line-through;");
    const factsHtml = e.facts.map((f) => '<div style="' + factStyle + '">' + esc(f) + "</div>").join("");
    const note = e.relevant ? "" : '<div style="margin-top:10px;font-size:11.5px;line-height:1.45;color:var(--text-tertiary);font-style:italic;">Left out of the ledger — not relevant to this case.</div>';
    return '<div style="' + boxStyle + '">' +
      '<div style="display:flex;align-items:center;gap:9px;"><span style="' + tagStyle + '">' + (e.relevant ? "EVIDENCE ARRIVED" : "NOISE · IGNORED") + "</span></div>" +
      '<p style="' + descStyle + '">' + esc(e.description) + "</p>" +
      '<div style="display:flex;flex-direction:column;gap:5px;margin-top:9px;">' + factsHtml + "</div>" +
      note + "</div>";
  }).join("");
  const ctxBlock = hasCtx
    ? '<div style="display:flex;flex-direction:column;gap:12px;">' + ctx + "</div>"
    : '<p style="margin:0;font-size:13px;line-height:1.5;color:var(--text-tertiary);">No new product or support evidence arrived at this turn.</p>';

  // ---- readiness ladder / final outcome ----
  let stage;
  if (st.evidence_seen) stage = 4;
  else if (st.possible_causes.length === 1) stage = 3;
  else if (st.ruled_out.length > 0) stage = 2;
  else stage = 1;
  const stageLabels = { 1: "gathering signals", 2: "narrowing causes", 3: "awaiting evidence", 4: "evidence confirmed" };
  const ladder = [1, 2, 3, 4].map((n) => {
    const filled = n <= stage;
    const col = !filled ? "rgba(237,232,225,.10)" : (stage === 4 ? "var(--accent)" : "rgba(237,232,225,.40)");
    return '<span style="flex:1;height:6px;border-radius:3px;background:' + col + ';transition:background 220ms ease;"></span>';
  }).join("");

  const locked = !st.evidence_seen;
  const outcomeIcon = locked ? ICON_LOCK : ICON_LOCK_OPEN;
  const outcomeTextStyle = "margin:0;font-size:15px;line-height:1.55;text-wrap:pretty;color:" +
    (locked ? "var(--text-secondary)" : "var(--text-primary)") + ";";
  const outcomeTag = locked ? "WITHHELD" : "EVIDENCE-BACKED";
  const outcomeTagStyle = "font-family:var(--font-mono);font-size:9.5px;letter-spacing:.12em;padding:3px 8px;border-radius:5px;" +
    (locked ? "color:var(--text-tertiary);border:1px solid var(--border-subtle);" : "color:var(--accent-text);border:1px solid var(--accent-border);");

  // ---- case route map ----
  const routePhases = ["Intake", "Clarify issue", "Check context", "Narrow cause", "Resolve or hand off"];
  const ctxThisTurn = step.new_context.some((e) => e.relevant);
  let ctxSoFar = false;
  for (let j = 0; j <= i; j++) { if (c.steps[j].new_context.some((e) => e.relevant)) ctxSoFar = true; }
  let routeStage;
  if (st.evidence_seen) routeStage = 5;
  else if (ctxThisTurn) routeStage = 3;
  else if (st.possible_causes.length === 1 || ctxSoFar) routeStage = 4;
  else if (step.conversation.length > 1) routeStage = 2;
  else routeStage = 1;
  const route = routePhases.map((label, idx) => {
    const n = idx + 1;
    const done = n < routeStage;
    const active = n === routeStage;
    let nodeBg, nodeBorder, labelColor, nodeSize = "10px";
    if (active) { nodeBg = "var(--accent)"; nodeBorder = null; labelColor = "var(--text-primary)"; nodeSize = "12px"; }
    else if (done) { nodeBg = "var(--accent-mid)"; nodeBorder = null; labelColor = "var(--text-secondary)"; }
    else { nodeBg = "transparent"; nodeBorder = "1px solid var(--text-tertiary)"; labelColor = "var(--text-tertiary)"; }
    const connector = n > 1
      ? '<span style="flex:1;height:1px;min-width:16px;background:' + (n <= routeStage ? "var(--accent-mid)" : "var(--border-mid)") + ';transition:background 200ms ease;"></span>'
      : "";
    const nodeStyle = "width:" + nodeSize + ";height:" + nodeSize + ";border-radius:50%;flex:none;background:" + nodeBg + ";" +
      (nodeBorder ? "border:" + nodeBorder + ";" : "") + (active ? "box-shadow:0 0 0 4px var(--accent-dim);" : "") + "transition:all 200ms ease;";
    const labelStyle = "font-family:var(--font-mono);font-size:10.5px;letter-spacing:.03em;white-space:nowrap;color:" + labelColor + ";transition:color 200ms ease;";
    return connector + '<div style="display:flex;align-items:center;gap:9px;flex:none;padding:0 6px;">' +
      '<span style="' + nodeStyle + '"></span><span style="' + labelStyle + '">' + esc(label) + "</span></div>";
  }).join("");

  // ---- handoff readiness preview (descriptive, not a gate) ----
  const hdot = (kind) => kind === "present"
    ? "width:8px;height:8px;border-radius:50%;background:var(--accent);flex:none;"
    : kind === "partial"
      ? "width:8px;height:8px;border-radius:50%;background:transparent;border:1.5px solid var(--accent);flex:none;"
      : "width:8px;height:8px;border-radius:50%;background:transparent;border:1.5px solid var(--text-tertiary);flex:none;";
  const clarityLevel = routeStage >= 3 ? "clear" : (routeStage === 2 ? "taking shape" : "forming");
  const handoffData = [
    { label: "issue clarity", value: clarityLevel, kind: routeStage >= 3 ? "present" : (routeStage === 2 ? "partial" : "open") },
    { label: "known facts", value: st.known_facts.length + " captured", kind: st.known_facts.length ? "present" : "open" },
    { label: "open unknowns", value: st.still_unknown.length ? st.still_unknown.length + " still in view" : "none blocking", kind: st.still_unknown.length ? "partial" : "present" },
    { label: "ruled-out paths", value: st.ruled_out.length ? st.ruled_out.length + " documented" : "none yet", kind: st.ruled_out.length ? "present" : "open" },
    { label: "next action", value: st.next_best_action ? "named" : "—", kind: st.next_best_action ? "present" : "open" },
    { label: "final cause", value: st.evidence_seen ? "evidence-supported" : "withheld — awaiting evidence", kind: st.evidence_seen ? "present" : "open" },
  ];
  const handoffRows = handoffData.map((r) => {
    const valueStyle = "font-family:var(--font-mono);font-size:11.5px;letter-spacing:.02em;text-align:right;color:" +
      (r.kind === "present" ? "var(--text-primary)" : (r.kind === "partial" ? "var(--text-secondary)" : "var(--text-tertiary)")) + ";";
    return '<div style="display:flex;align-items:center;gap:11px;padding:9px 0;border-top:1px solid var(--border-subtle);">' +
      '<span style="' + hdot(r.kind) + '"></span>' +
      '<span style="flex:1;font-size:13px;color:var(--text-secondary);">' + esc(r.label) + "</span>" +
      '<span style="' + valueStyle + '">' + esc(r.value) + "</span></div>";
  }).join("");
  let handoffSummary;
  if (st.evidence_seen) handoffSummary = "A new owner could pick this up with an evidence-supported cause and a named next step.";
  else if (routeStage >= 3) handoffSummary = "A new owner would inherit the narrowed causes, the open unknowns, and the next check to run.";
  else if (routeStage === 2) handoffSummary = "A new owner would inherit the clarified issue and the current lines of inquiry.";
  else handoffSummary = "A new owner would still be clarifying what the issue is.";

  // ---- evidence & context arrival timeline (accumulated) ----
  const priority = { evidence: 6, context: 5, ruled: 4, resolved: 3, fact: 2, noise: 1, muted: 0 };
  const kindColor = { evidence: "var(--accent-text)", context: "var(--accent-text)", ruled: "var(--text-tertiary)", resolved: "var(--text-secondary)", fact: "var(--text-secondary)", noise: "var(--text-tertiary)", muted: "var(--text-tertiary)" };
  const blanks = { known_facts: [], still_unknown: [], ruled_out: [], evidence_seen: false };
  const tl = [];
  for (let j = 0; j <= i; j++) {
    const s = c.steps[j];
    const ps = j > 0 ? c.steps[j - 1].state : blanks;
    const events = [];
    const ctxFactSet = new Set();
    s.new_context.forEach((e) => {
      if (e.relevant) { e.facts.forEach((f) => ctxFactSet.add(f)); events.push({ kind: "context", tag: "CONTEXT", text: e.description }); }
      else events.push({ kind: "noise", tag: "NOISE", text: e.description });
    });
    const newFacts = s.state.known_facts.filter((f) => !ps.known_facts.includes(f) && !ctxFactSet.has(f));
    if (newFacts.length) events.push({ kind: "fact", tag: "FACTS +" + newFacts.length, text: newFacts.join(" · ") });
    const newRuled = s.state.ruled_out.filter((r) => !ps.ruled_out.includes(r));
    if (newRuled.length) events.push({ kind: "ruled", tag: "RULED OUT +" + newRuled.length, text: newRuled.join(" · ") });
    const resolved = ps.still_unknown.filter((u) => !s.state.still_unknown.includes(u));
    if (resolved.length) events.push({ kind: "resolved", tag: "RESOLVED", text: resolved.join(" · ") });
    if (s.state.evidence_seen && !ps.evidence_seen) events.push({ kind: "evidence", tag: "EVIDENCE", text: "Evidence supports the final cause: " + s.state.final_cause_text + "." });
    if (!events.length) events.push({ kind: "muted", tag: "EXCHANGE", text: "Clarifying turn — case state unchanged." });
    const topKind = events.reduce((a, e) => priority[e.kind] > priority[a] ? e.kind : a, "muted");
    tl.push({ turnNum: j + 1, isCurrent: j === i, notLast: j < i, events, topKind });
  }
  const timeline = tl.map((blk) => {
    const blockStyle = "display:flex;gap:13px;" + (blk.isCurrent && advancing ? "animation:enterUp 320ms ease both;" : "");
    const nodeStyle = "width:9px;height:9px;border-radius:50%;flex:none;margin-top:2px;background:" +
      (blk.topKind === "evidence" || blk.topKind === "context" ? "var(--accent)" :
        (blk.topKind === "ruled" || blk.topKind === "noise" || blk.topKind === "muted" ? "transparent" : "var(--text-secondary)")) + ";" +
      ((blk.topKind === "ruled" || blk.topKind === "noise" || blk.topKind === "muted") ? "border:1px solid var(--text-tertiary);" : "") +
      (blk.topKind === "evidence" ? "box-shadow:0 0 0 4px var(--accent-dim);" : "");
    const connector = blk.notLast ? '<span style="flex:1;width:1px;background:var(--border-mid);margin-top:5px;min-height:16px;"></span>' : "";
    const eventsHtml = blk.events.map((e) => {
      const tagStyle = "font-family:var(--font-mono);font-size:8.5px;letter-spacing:.08em;padding:2px 6px;border-radius:4px;white-space:nowrap;flex:none;color:" +
        kindColor[e.kind] + ";border:1px solid " + (e.kind === "evidence" || e.kind === "context" ? "var(--accent-border)" : "var(--border-subtle)") + ";";
      const textStyle = "font-size:12px;line-height:1.45;color:" + (e.kind === "noise" || e.kind === "ruled" ? "var(--text-tertiary)" : "var(--text-secondary)") + ";" +
        (e.kind === "noise" || e.kind === "ruled" ? "text-decoration:line-through;" : "");
      return '<div style="display:flex;gap:9px;align-items:flex-start;"><span style="' + tagStyle + '">' + esc(e.tag) + '</span><span style="' + textStyle + '">' + esc(e.text) + "</span></div>";
    }).join("");
    return '<div style="' + blockStyle + '">' +
      '<div style="display:flex;flex-direction:column;align-items:center;flex:none;width:9px;"><span style="' + nodeStyle + '"></span>' + connector + "</div>" +
      '<div style="flex:1;min-width:0;padding-bottom:18px;">' +
      '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.1em;color:var(--text-secondary);margin-bottom:8px;">TURN ' + blk.turnNum + "</div>" +
      '<div style="display:flex;flex-direction:column;gap:8px;">' + eventsHtml + "</div></div></div>";
  }).join("");
  const timelineCount = "through turn " + (i + 1);

  // ---- raw eval state ----
  const raw = JSON.stringify({
    case_id: S.caseId,
    turn: step.turn,
    facts: st.known_facts,
    unknowns: st.still_unknown,
    possible_causes: st.possible_causes,
    ruled_out_branches: st.ruled_out,
    next_check: st.next_best_action,
    final_cause: st.final_cause_text || null,
    root_cause_evidence_seen: st.evidence_seen,
  }, null, 2);

  // ---- footer buttons ----
  const baseBtn = "min-width:96px;border-radius:8px;font-family:var(--font-sans);font-size:13px;padding:9px 14px;transition:all 120ms ease;";
  const prevDisabled = i === 0;
  const nextDisabled = i === c.steps.length - 1;
  const prevStyle = baseBtn + (prevDisabled
    ? "border:1px solid rgba(255,255,255,.05);background:transparent;color:var(--text-tertiary);cursor:not-allowed;"
    : "border:1px solid var(--border-mid);background:var(--bg-2);color:var(--text-primary);cursor:pointer;");
  const nextStyle = baseBtn + (nextDisabled
    ? "border:1px solid rgba(255,255,255,.05);background:transparent;color:var(--text-tertiary);cursor:not-allowed;"
    : "border:1px solid var(--accent-border);background:var(--accent-dim);color:var(--accent-text);cursor:pointer;");

  const pulseDot = '<span style="width:8px;height:8px;border-radius:50%;background:var(--accent);animation:livePulse 1.9s ease infinite;"></span>';

  // ---- assemble ----
  app.innerHTML =
    '<header style="display:flex;align-items:flex-start;justify-content:space-between;gap:32px;flex-wrap:wrap;padding:20px 34px 18px;border-bottom:1px solid var(--border-subtle);flex:none;">' +
      '<div style="min-width:300px;">' +
        '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--text-tertiary);">Real-time support copilot · live replay</div>' +
        '<h1 style="font-family:var(--font-display);font-weight:300;font-size:31px;line-height:1.1;margin:9px 0 7px;color:var(--text-primary);letter-spacing:-.01em;">' + esc(c.title) + "</h1>" +
        '<p style="margin:0;max-width:560px;font-size:13.5px;line-height:1.55;color:var(--text-secondary);text-wrap:pretty;">' + esc(c.scenario) + "</p>" +
      "</div>" +
      '<div style="display:flex;flex-direction:column;align-items:flex-end;gap:14px;">' +
        '<div style="display:flex;align-items:center;gap:9px;">' + pulseDot +
          '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;color:var(--accent-text);">WORKING THE CASE</span></div>' +
        '<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;">' + chips + "</div>" +
      "</div>" +
    "</header>" +

    '<div style="display:flex;align-items:center;gap:24px;padding:13px 34px;border-bottom:1px solid var(--border-subtle);flex:none;background:var(--bg-0);">' +
      '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);flex:none;">Case route</span>' +
      '<div style="display:flex;align-items:center;flex:1;min-width:0;">' + route + "</div>" +
    "</div>" +

    '<main style="flex:1;min-height:0;display:grid;grid-template-columns:minmax(340px,440px) 1fr;">' +

      '<section style="display:flex;flex-direction:column;min-height:0;border-right:1px solid var(--border-subtle);">' +
        '<div style="display:flex;align-items:center;justify-content:space-between;padding:18px 24px 12px;flex:none;">' +
          '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);">Case conversation</div>' +
          '<div style="font-family:var(--font-mono);font-size:11px;color:var(--text-secondary);letter-spacing:.06em;">TURN ' + (i + 1) + " OF " + c.steps.length + "</div>" +
        "</div>" +
        '<div style="flex:1;min-height:0;overflow-y:auto;padding:6px 24px 22px;display:flex;flex-direction:column;gap:13px;">' + conversation + "</div>" +
        '<div style="display:flex;align-items:center;justify-content:space-between;gap:14px;padding:15px 24px;border-top:1px solid var(--border-subtle);flex:none;">' +
          '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.08em;color:var(--text-tertiary);">← → to step turns</span>' +
          '<div style="display:flex;gap:9px;">' +
            '<button type="button" data-act="prev"' + (prevDisabled ? " disabled" : "") + ' style="' + prevStyle + '">Previous</button>' +
            '<button type="button" data-act="next"' + (nextDisabled ? " disabled" : "") + ' style="' + nextStyle + '">Next turn</button>' +
          "</div>" +
        "</div>" +
      "</section>" +

      '<section style="min-height:0;overflow-y:auto;padding:22px 30px 44px;display:flex;flex-direction:column;gap:18px;background:var(--bg-0);">' +
        '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);margin-bottom:-4px;">Copilot state · this turn</div>' +

        '<div style="background:var(--accent-dim);border:1px solid var(--accent-border);border-radius:14px;padding:20px 22px;">' +
          '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">' + ICON_NEXT +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;color:var(--accent-text);">NEXT BEST MOVE</span></div>' +
          '<p style="margin:0;font-family:var(--font-display);font-weight:300;font-size:25px;line-height:1.28;color:var(--text-primary);text-wrap:pretty;">' + esc(st.next_best_action) + "</p>" +
        "</div>" +

        '<div style="background:var(--bg-1);border:1px solid var(--border-subtle);border-radius:12px;padding:18px 20px 8px;">' +
          '<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:8px;">' +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);">Working hypotheses</span>' +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.05em;color:var(--text-secondary);">' + esc(hypSummary) + "</span></div>" +
          '<div style="display:flex;flex-direction:column;">' + hyps + "</div>" +
        "</div>" +

        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">' +
          '<div style="background:var(--bg-1);border:1px solid var(--border-subtle);border-radius:12px;padding:18px 20px;">' +
            '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);margin-bottom:13px;">Known facts</div>' +
            '<div style="display:flex;flex-direction:column;gap:11px;">' + facts + "</div></div>" +
          '<div style="background:var(--bg-1);border:1px solid var(--border-subtle);border-radius:12px;padding:18px 20px;">' +
            '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);margin-bottom:5px;">Still unknown</div>' +
            '<div style="font-size:10.5px;line-height:1.4;color:var(--text-tertiary);margin-bottom:12px;">kept in view on purpose</div>' +
            '<div style="display:flex;flex-direction:column;gap:11px;">' + unknownsBlock + "</div></div>" +
        "</div>" +

        '<div style="background:var(--bg-1);border:1px solid var(--border-subtle);border-radius:12px;padding:18px 20px;">' +
          '<div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);margin-bottom:14px;">Product &amp; support context</div>' +
          ctxBlock +
        "</div>" +

        '<div style="background:var(--bg-2);border:1px solid var(--border-mid);border-radius:12px;padding:20px 22px;">' +
          '<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px;">' +
            '<div style="display:flex;align-items:center;gap:9px;">' + outcomeIcon +
              '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);">Final outcome</span></div>' +
            '<span style="' + outcomeTagStyle + '">' + outcomeTag + "</span></div>" +
          '<p style="' + outcomeTextStyle + '">' + esc(st.final_outcome) + "</p>" +
          '<div style="display:flex;gap:6px;margin-top:18px;">' + ladder + "</div>" +
          '<div style="display:flex;align-items:baseline;justify-content:space-between;margin-top:9px;">' +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-secondary);">' + esc(stageLabels[stage]) + "</span>" +
            '<span style="font-family:var(--font-mono);font-size:10px;color:var(--text-tertiary);">' + stage + " of 4</span></div>" +
        "</div>" +

        '<div style="background:var(--bg-1);border:1px solid var(--border-subtle);border-radius:12px;padding:18px 20px;">' +
          '<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:3px;">' +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);">Handoff readiness · preview</span>' +
            '<span style="font-family:var(--font-mono);font-size:9px;letter-spacing:.08em;color:var(--text-tertiary);border:1px solid var(--border-subtle);border-radius:4px;padding:2px 6px;">PREVIEW ONLY</span></div>' +
          '<div style="font-size:10.5px;line-height:1.4;color:var(--text-tertiary);margin-bottom:14px;">what another owner would inherit — descriptive, not a quality gate</div>' +
          '<div style="display:flex;flex-direction:column;">' + handoffRows + "</div>" +
          '<p style="margin:15px 0 0;font-size:13.5px;line-height:1.55;color:var(--text-primary);text-wrap:pretty;">' + esc(handoffSummary) + "</p>" +
        "</div>" +

        '<div style="background:var(--bg-1);border:1px solid var(--border-subtle);border-radius:12px;padding:18px 20px;">' +
          '<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:3px;">' +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-tertiary);">Evidence &amp; context timeline</span>' +
            '<span style="font-family:var(--font-mono);font-size:10px;letter-spacing:.05em;color:var(--text-secondary);">' + esc(timelineCount) + "</span></div>" +
          '<div style="font-size:10.5px;line-height:1.4;color:var(--text-tertiary);margin-bottom:18px;">what changed the case, and when — and why the cause waited</div>' +
          '<div style="display:flex;flex-direction:column;">' + timeline + "</div>" +
        "</div>" +

        '<details style="border:1px solid var(--border-subtle);border-radius:10px;background:var(--bg-1);padding:0;">' +
          '<summary style="cursor:pointer;padding:13px 18px;font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;color:var(--text-secondary);">show raw eval state</summary>' +
          '<pre style="margin:0;padding:0 18px 16px;white-space:pre-wrap;font-family:var(--font-mono);font-size:11px;line-height:1.55;color:var(--text-secondary);">' + esc(raw) + "</pre>" +
        "</details>" +
      "</section>" +
    "</main>";

  app.querySelectorAll("[data-case]").forEach((el) => el.addEventListener("click", () => goCase(el.getAttribute("data-case"))));
  const prevBtn = app.querySelector('[data-act="prev"]');
  const nextBtn = app.querySelector('[data-act="next"]');
  if (prevBtn) prevBtn.addEventListener("click", stepPrev);
  if (nextBtn) nextBtn.addEventListener("click", stepNext);
}

render();
</script>
</body>
</html>
"""


def write_live_simulator(path: Path = SIMULATOR_PATH) -> Path:
    ensure_output_dir()
    path.write_text(render_live_simulator(CASES), encoding="utf-8")
    return path


def main() -> None:
    path = write_live_simulator()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

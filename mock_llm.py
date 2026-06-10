#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def extract_payload(prompt: str) -> dict[str, Any]:
    marker = "Input:\n"
    if marker not in prompt:
        raise SystemExit("prompt missing Input block")
    return json.loads(prompt.split(marker, 1)[1])


def patch() -> dict[str, Any]:
    return {
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
        "root_cause_evidence_seen": False,
        "handoff_note": "",
    }


def add(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def remove(items: list[str], value: str) -> None:
    add(items, value)


def process_patch(payload: dict[str, Any]) -> dict[str, Any]:
    out = patch()
    turn = payload["new_transcript_turn"]
    text = normalize(turn["text"])
    speaker = turn.get("speaker", "")
    context_facts = []
    for event in payload.get("new_product_support_context", []):
        context_facts.extend(event.get("facts", []))

    if "lost access" in text:
        for fact in ["symptom:workspace_access_loss"]:
            add(out["facts_add"], fact)
        for unknown in ["auth_status", "workspace_role_assignment"]:
            add(out["unknowns_add"], unknown)
        for branch in ["login_block", "missing_workspace_role", "scim_sync_delay", "stale_entitlement_cache"]:
            add(out["candidate_branches_add"], branch)
        out["next_check"] = "Can the affected users sign in, or are they blocked at login?"

    if "three users" in text:
        add(out["facts_add"], "affected_scope:three_users")
    if "migration" in text:
        add(out["facts_add"], "recent_change:migration")

    auth_works = "they can sign in" in text or "login works" in text or "can log in" in text
    if speaker != "agent" and auth_works:
        add(out["facts_add"], "auth:works")
        remove(out["unknowns_remove"], "auth_status")
        remove(out["candidate_branches_remove"], "login_block")
        remove(out["candidate_branches_remove"], "login_failure")
        add(out["ruled_out_branches_add"], "login_block")
        add(out["ruled_out_branches_add"], "login_failure")
        out["next_check"] = "Check whether the affected users have workspace-level roles."

    if "workspace" in text:
        add(out["facts_add"], "surface:workspace_access")

    if "cannot log in" in text:
        add(out["facts_add"], "reported_issue:login")
        add(out["unknowns_add"], "actual_surface")
        add(out["candidate_branches_add"], "login_failure")
        out["next_check"] = "Confirm whether login itself fails or whether a page after login is wrong."

    if "no login works" in text or "login works" in text:
        add(out["facts_add"], "correction:login_works")
        remove(out["unknowns_remove"], "actual_surface")
        remove(out["candidate_branches_remove"], "login_failure")
        add(out["ruled_out_branches_add"], "login_failure")
        out["next_check"] = "Identify which page or entitlement is wrong after login."

    if "billing" in text or "wrong plan" in text:
        for fact in ["surface:billing_plan", "symptom:wrong_plan_shown"]:
            add(out["facts_add"], fact)
        add(out["unknowns_add"], "billing_entitlement_status")
        for branch in ["billing_entitlement_refresh_pending", "invoice_app_mismatch"]:
            add(out["candidate_branches_add"], branch)
        out["next_check"] = "Check whether the billing entitlement refresh completed after the upgrade."

    if "upgraded" in text or "upgrade" in text:
        add(out["facts_add"], "recent_change:upgrade")

    if "invite" in text:
        add(out["facts_add"], "flow:admin_invite")
        for unknown in ["invite_created", "email_delivery_status"]:
            add(out["unknowns_add"], unknown)
        for branch in ["invite_not_created", "email_delivery_suppressed", "domain_policy_rejection"]:
            add(out["candidate_branches_add"], branch)
        out["next_check"] = "Check whether the invite was created and whether email delivery bounced or was suppressed."

    if "never arrives" in text or "email" in text:
        add(out["facts_add"], "symptom:invite_email_not_received")
        out["next_check"] = "Inspect invite delivery status, suppression list, and domain policy results."

    if context_facts:
        out["root_cause_evidence_seen"] = True
        for fact in context_facts:
            add(out["facts_add"], fact)

        if "workspace_role_missing:Migrated-CSM" in context_facts:
            remove(out["unknowns_remove"], "workspace_role_assignment")
            for branch in ["scim_sync_delay", "stale_entitlement_cache"]:
                remove(out["candidate_branches_remove"], branch)
                add(out["ruled_out_branches_add"], branch)
            add(out["candidate_branches_add"], "missing_workspace_role_inheritance")
            out["final_cause"] = "missing_workspace_role_inheritance"
            out["next_check"] = "Confirm whether Migrated-CSM should inherit Workspace Member after migration."

        if "billing_refresh:pending" in context_facts:
            remove(out["unknowns_remove"], "billing_entitlement_status")
            add(out["ruled_out_branches_add"], "login_failure")
            add(out["candidate_branches_add"], "billing_entitlement_refresh_pending")
            out["final_cause"] = "billing_entitlement_refresh_pending"
            out["next_check"] = "Check the billing entitlement refresh job and re-sync the plan entitlement."

        if "domain_policy:dmarc_reject" in context_facts:
            for unknown in ["invite_created", "email_delivery_status"]:
                remove(out["unknowns_remove"], unknown)
            remove(out["candidate_branches_remove"], "invite_not_created")
            add(out["ruled_out_branches_add"], "invite_not_created")
            for branch in ["domain_policy_rejection", "email_delivery_suppressed"]:
                add(out["candidate_branches_add"], branch)
            out["final_cause"] = "domain_policy_rejection"
            out["next_check"] = "Inspect email suppression and DMARC policy for the recipient domain."

    return out


def predictive_patch(payload: dict[str, Any]) -> dict[str, Any]:
    out = process_patch(payload)
    text = normalize(payload["new_transcript_turn"]["text"])
    if "migration" in text or "lost access" in text:
        out["final_cause"] = "missing_workspace_role_inheritance"
        add(out["candidate_branches_add"], "missing_workspace_role_inheritance")
        out["handoff_note"] = "Predicted migration role inheritance issue before system evidence."
    elif "cannot log in" in text:
        out["final_cause"] = "login_failure"
        out["handoff_note"] = "Predicted login failure from the first symptom."
    elif "invite" in text:
        out["final_cause"] = "domain_policy_rejection"
        out["handoff_note"] = "Predicted email policy rejection before delivery evidence."
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock LLM for Support Process Lab.")
    parser.add_argument("--profile", choices=("process", "predictive"), default="process")
    args = parser.parse_args()

    payload = extract_payload(sys.stdin.read())
    if args.profile == "process":
        result = process_patch(payload)
    else:
        result = predictive_patch(payload)
    print(json.dumps(result))


if __name__ == "__main__":
    main()

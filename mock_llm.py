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
        if event.get("relevant") is False:
            continue
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

    if "api calls" in text or "rate-limited" in text or "rate limited" in text:
        add(out["facts_add"], "surface:api_delivery")
        add(out["facts_add"], "symptom:rate_limit_errors")
        for unknown in ["traffic_scope", "quota_status", "webhook_auth_status"]:
            add(out["unknowns_add"], unknown)
        for branch in ["quota_exhaustion", "webhook_auth_rotation"]:
            add(out["candidate_branches_add"], branch)
        out["next_check"] = "Confirm whether every API route is failing or only one integration path."

    if "scaled traffic" in text:
        add(out["facts_add"], "recent_change:traffic_scale")

    if "not every route" in text or "subset of webhook" in text:
        add(out["facts_add"], "traffic_scope:subset")
        add(out["facts_add"], "surface:webhook_callbacks")
        add(out["facts_add"], "normal_api_reads:work")
        remove(out["unknowns_remove"], "traffic_scope")
        out["next_check"] = "Compare quota counters with webhook auth status for the failing callback path."

    if "partner service rolled a new deployment" in text:
        add(out["facts_add"], "recent_change:partner_deploy")
        out["next_check"] = "Compare webhook auth status for the failing service before naming a final cause."

    if "legacy worker fails" in text or "new worker callbacks succeed" in text:
        add(out["facts_add"], "failure_scope:legacy_worker")
        add(out["facts_add"], "new_worker:callbacks_succeed")
        out["next_check"] = "Compare webhook auth status for the legacy worker before naming a final cause."

    if "old webhook auth config" in text:
        add(out["facts_add"], "failure_scope:legacy_worker")
        out["next_check"] = "Update the legacy worker signing secret and replay one failed webhook callback."

    if "not entitled" in text or "entitlement block" in text:
        add(out["facts_add"], "surface:entitlement_access")
        add(out["facts_add"], "symptom:entitlement_block")
        for unknown in ["affected_scope", "billing_entitlement_status", "provisioning_status"]:
            add(out["unknowns_add"], unknown)
        for branch in ["billing_entitlement_gap", "provisioning_state_mismatch", "entitlement_cache_delay"]:
            add(out["candidate_branches_add"], branch)
        out["next_check"] = "Confirm whether all users see the entitlement block or only a few seats."

    if "renewal completed" in text:
        add(out["facts_add"], "renewal:completed")

    if "all users" in text and "entitlement block" in text:
        add(out["facts_add"], "affected_scope:all_workspace_users")
        remove(out["unknowns_remove"], "affected_scope")
        out["next_check"] = "Check billing entitlement and provisioning state side by side."

    if "renewal is active" in text:
        add(out["facts_add"], "renewal:active")
        add(out["facts_add"], "billing:entitled")
        previous_facts = payload["previous_live_support_state"].get("facts", [])
        if "provisioning:not_ready" in previous_facts:
            out["next_check"] = "Escalate with provisioning job status and entitlement cache status still open."

    if "provisioning still disagrees" in text:
        add(out["facts_add"], "provisioning:not_ready")
        out["next_check"] = "Escalate with provisioning job status and entitlement cache status still open."

    if "implementation owner" in text:
        add(out["facts_add"], "handoff_need:implementation_owner_update")

    if "handing this to product support" in text:
        out["next_check"] = "Escalate with provisioning job status and entitlement cache status still open."

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

        if "entitlement_cache:stale" in context_facts:
            remove(out["unknowns_remove"], "workspace_role_assignment")
            remove(out["unknowns_remove"], "cache_status")
            for branch in ["missing_workspace_role", "scim_sync_delay"]:
                remove(out["candidate_branches_remove"], branch)
                add(out["ruled_out_branches_add"], branch)
            add(out["candidate_branches_add"], "stale_entitlement_cache")
            out["final_cause"] = "stale_entitlement_cache"
            out["next_check"] = "Refresh the entitlement cache and confirm workspace access works after refresh."

        if "workspace_role:present" in context_facts and "entitlement_cache:stale" not in context_facts:
            remove(out["unknowns_remove"], "workspace_role_assignment")
            remove(out["candidate_branches_remove"], "missing_workspace_role")
            remove(out["candidate_branches_remove"], "missing_workspace_role_inheritance")
            add(out["ruled_out_branches_add"], "missing_workspace_role")
            add(out["ruled_out_branches_add"], "missing_workspace_role_inheritance")
            out["next_check"] = "Check entitlement cache status or product incident signals before naming a final cause."

        if "billing_refresh:pending" in context_facts:
            remove(out["unknowns_remove"], "billing_entitlement_status")
            for branch in ["login_failure", "missing_workspace_role", "scim_sync_delay"]:
                remove(out["candidate_branches_remove"], branch)
                add(out["ruled_out_branches_add"], branch)
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

        if "quota:under_limit" in context_facts:
            remove(out["unknowns_remove"], "quota_status")
            remove(out["candidate_branches_remove"], "quota_exhaustion")
            add(out["ruled_out_branches_add"], "quota_exhaustion")
            add(out["candidate_branches_add"], "webhook_auth_rotation")
            out["next_check"] = "Compare webhook auth status for the failing service before naming a final cause."

        if "webhook_auth:legacy_secret" in context_facts:
            remove(out["unknowns_remove"], "webhook_auth_status")
            remove(out["candidate_branches_remove"], "quota_exhaustion")
            add(out["ruled_out_branches_add"], "quota_exhaustion")
            add(out["candidate_branches_add"], "webhook_auth_rotation")
            out["final_cause"] = "webhook_auth_rotation"
            out["next_check"] = "Update the legacy worker signing secret and replay one failed webhook callback."

        if "billing:entitled" in context_facts and "provisioning:not_ready" in context_facts:
            for unknown in ["billing_entitlement_status", "payment_status"]:
                remove(out["unknowns_remove"], unknown)
            for unknown in ["provisioning_job_status", "entitlement_cache_status"]:
                add(out["unknowns_add"], unknown)
            for branch in ["billing_entitlement_gap", "payment_failure"]:
                remove(out["candidate_branches_remove"], branch)
                add(out["ruled_out_branches_add"], branch)
            for branch in ["provisioning_state_mismatch", "entitlement_cache_delay"]:
                add(out["candidate_branches_add"], branch)
            out["next_check"] = "Escalate with provisioning job status and entitlement cache status still open."

    return out


def predictive_patch(payload: dict[str, Any]) -> dict[str, Any]:
    out = process_patch(payload)
    text = normalize(payload["new_transcript_turn"]["text"])
    if "migration" in text or "lost access" in text:
        out["final_cause"] = "missing_workspace_role_inheritance"
        add(out["candidate_branches_add"], "missing_workspace_role_inheritance")
        out["handoff_note"] = "Predicted migration role inheritance issue before system evidence."
    elif "rate-limited" in text or "rate limited" in text or "api calls" in text:
        out["final_cause"] = "quota_exhaustion"
        add(out["candidate_branches_add"], "quota_exhaustion")
        out["handoff_note"] = "Predicted quota exhaustion before traffic scope or webhook auth evidence."
    elif "cannot log in" in text:
        out["final_cause"] = "login_failure"
        out["handoff_note"] = "Predicted login failure from the first symptom."
    elif "not entitled" in text or "entitlement block" in text:
        out["final_cause"] = "billing_entitlement_gap"
        add(out["candidate_branches_add"], "billing_entitlement_gap")
        out["handoff_note"] = "Predicted billing entitlement gap before provisioning evidence."
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

from __future__ import annotations

from typing import Any

BANNED_SUPPORT_PHRASES = [
    "mechanism evidence",
    "hidden configuration detail",
    "active branches",
    "presenting likely cause",
    "support-process guidance",
    "verify or rule out active",
]

SCENARIO_NAMES = {
    "permissions_access": "Workspace access",
    "onboarding_migration": "Migration",
    "workspace_setup": "Workspace setup",
    "integrations_data_sync": "Integration sync",
    "billing_plan_entitlement": "Billing entitlement",
}

FACT_TEXT = {
    "admin:late_mention": "An admin shared a late detail that changed the investigation.",
    "role_modified:6_months_ago": "The related role was last changed six months ago, so a recent role edit is less likely.",
    "comparison:config_differs": "A working example and an affected example differ in configuration; compare them before closing the case.",
    "logs:warning_dismissed": "A warning appeared in the logs and should be treated as relevant evidence.",
    "recent_change:migration": "The issue appeared after a migration.",
    "sso_group:membership": "Group membership is relevant to the access problem.",
    "surface:billing_plan": "The customer is looking at the billing or plan surface.",
    "symptom:wrong_plan_shown": "The customer sees the wrong plan or entitlement.",
    "seat_count:available": "The account has available seats, so seat exhaustion is less likely.",
    "billing_status:active": "Billing shows the account is active.",
    "payment:current": "Payment is current.",
    "oauth:scope_warning": "The integration shows an OAuth scope warning.",
    "sync:failed_job": "A sync job failed and needs job-level review.",
}

UNKNOWN_TEXT = {
    "auth_status": "Can the affected users sign in successfully?",
    "workspace_role_assignment": "Do affected users have the right workspace role?",
    "billing_entitlement_status": "Has the billing entitlement refresh completed?",
    "cache_status": "Is cached state still affecting what the customer sees?",
    "email_delivery_status": "Did the invite or notification email actually reach the customer?",
    "invite_created": "Was the invite created and attached to the right user?",
    "actual_surface": "Which product surface is actually failing?",
}

CAUSE_TEXT = {
    "direct_assignment_conflict": "a direct assignment conflict",
    "sso_group_mismatch_after_department_change": "an SSO group mismatch after a department change",
    "region_mismatch": "a region mismatch",
    "missing_group_role_after_migration": "a missing group role after migration",
    "archived_team_export_filter": "an archived-team export filter",
    "billing_entitlement_refresh_pending": "a billing entitlement refresh that has not completed",
    "stale_entitlement_cache": "stale entitlement cache",
    "the_access_failure_is_caused_by_missing_group": "a missing access group or role",
    "the_access_failure_is_caused_by_sso_group": "an SSO group mismatch",
    "the_workspace_setup_failure_is_caused_by_region": "a workspace region mismatch",
}


def scenario_name(fixture: dict[str, Any]) -> str:
    return SCENARIO_NAMES.get(fixture.get("scenario", ""), "Support case")


def readable_label(label: str) -> str:
    if label in FACT_TEXT:
        return FACT_TEXT[label]
    if label in UNKNOWN_TEXT:
        return UNKNOWN_TEXT[label]
    return label.replace("_", " ").replace(":", " ")


def translate_facts(facts: list[str]) -> list[str]:
    return [readable_label(fact) for fact in facts]


def translate_unknowns(unknowns: list[str]) -> list[str]:
    return [UNKNOWN_TEXT.get(unknown, readable_label(unknown)) for unknown in unknowns]


def translate_open_questions(result: dict[str, Any], review: dict[str, Any]) -> list[str]:
    unknowns = translate_unknowns(result["final_state"]["unknowns"])
    if unknowns:
        return unknowns
    if review["outcome"] == "probable_cause":
        return ["One more product signal should confirm the likely cause before the case is treated as resolved."]
    if review["outcome"] == "handoff":
        return ["The receiving owner should confirm the remaining product evidence before closing the case."]
    return []


def translate_causes(causes: list[str]) -> list[str]:
    return [CAUSE_TEXT.get(cause, readable_label(cause)) for cause in causes]


def translate_title(result: dict[str, Any], outcome: str) -> str:
    return f"{scenario_name(result['fixture'])} case - {outcome.replace('_', ' ')}"


def _event_fact_text(event: dict[str, Any], fixture: dict[str, Any]) -> str:
    facts = event.get("facts", [])
    if "comparison:config_differs" in facts:
        return f"A working {scenario_name(fixture).lower()} example and an affected example differ; compare the exact setting before closing the case."
    if "logs:warning_dismissed" in facts:
        return "A warning in the logs appears relevant and should be reviewed before deciding the next action."
    if "admin:late_mention" in facts:
        return "A late admin detail changed the investigation path and should be verified against product records."
    if facts:
        return translate_facts(facts)[0]
    return ""


def translate_evidence(result: dict[str, Any]) -> str:
    fixture = result["fixture"]
    relevant = [
        event
        for event in fixture.get("context_events", [])
        if event.get("relevant", True)
    ]
    final_events = [
        event
        for event in relevant
        if event.get("final_cause") or event.get("reveals_final_cause")
    ]
    candidates = final_events or relevant
    for event in reversed(candidates):
        text = _event_fact_text(event, fixture)
        if text:
            return text
    return "Product or support context changed what the agent should check next."


def translate_next_action(result: dict[str, Any], review: dict[str, Any]) -> str:
    fixture = result["fixture"]
    outcome = review["outcome"]
    scenario = fixture.get("scenario", "")
    final_cause = result["final_state"].get("final_cause") or fixture.get("final_cause", "")
    owner = review.get("review_fields", {}).get("next_owner") or fixture.get("next_owner", "next support owner")

    if outcome == "handoff":
        return f"Send the evidence summary and affected examples to {owner}, and keep the unresolved checks attached to the case."
    if outcome == "probable_cause":
        if scenario == "permissions_access":
            return "Compare one blocked user with one working user in the identity provider before treating the access cause as resolved."
        if scenario == "onboarding_migration":
            return "Verify one affected record against the source export before treating the migration cause as resolved."
        if scenario == "billing_plan_entitlement":
            return "Confirm the entitlement refresh status before telling the customer the billing issue is resolved."
        return "Verify the likely cause with one more product signal before treating the case as resolved."
    if final_cause:
        return "Confirm the customer can complete the affected workflow after the fix is applied."
    return "Confirm the customer-visible fix before closing the case."


def translate_outcome(result: dict[str, Any], review: dict[str, Any]) -> str:
    outcome = review["outcome"]
    final_cause = result["final_state"].get("final_cause") or result["fixture"].get("final_cause", "")
    if outcome == "resolved":
        cause = CAUSE_TEXT.get(final_cause, readable_label(final_cause)) if final_cause else "the confirmed cause"
        return f"The case can close once the customer confirms the workflow works again. The supported cause is {cause}."
    if outcome == "probable_cause":
        return "The leading cause is clear enough to guide the customer, but one more product signal should be checked before calling it fully resolved."
    owner = review.get("review_fields", {}).get("next_owner") or result["fixture"].get("next_owner", "the next owner")
    return f"The case should move to {owner} with the evidence summary and open checks preserved."


def contains_internal_language(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in BANNED_SUPPORT_PHRASES)

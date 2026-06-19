# Support Process Lab Report

Run: `deterministic`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| access_after_migration | 18/18 | 100% | yes | missing_workspace_role_inheritance |
| billing_plan_mismatch | 24/24 | 100% | yes | billing_entitlement_refresh_pending |
| corrected_billing_after_access_report | 12/12 | 100% | yes | billing_entitlement_refresh_pending |
| invite_email_not_arriving | 18/18 | 100% | yes | domain_policy_rejection |
| invite_with_irrelevant_billing_context | 18/18 | 100% | yes | domain_policy_rejection |
| level2_conflicting_migration_context | 30/30 | 100% | yes | stale_entitlement_cache |
| level2_irrelevant_then_late_invite_context | 24/24 | 100% | yes | domain_policy_rejection |
| level2_late_billing_evidence | 30/30 | 100% | yes | billing_entitlement_refresh_pending |
| level2_unresolved_workspace_handoff | 24/24 | 100% | yes |  |
| stale_cache_after_migration | 18/18 | 100% | yes | stale_entitlement_cache |

## Access After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 2 | agent | Can they sign in at all, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 3 | customer | They can sign in, but they cannot open the new workspace. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; group_membership:Migrated-CSM; scim_sync:complete; workspace_role_missing:Migrated-CSM |  | missing_workspace_role; missing_workspace_role_inheritance | Confirm whether Migrated-CSM should inherit Workspace Member after migration. | pass | - |

### Final State

```json
{
  "case_id": "access_after_migration",
  "version": 4,
  "facts": [
    "symptom:workspace_access_loss",
    "affected_scope:three_users",
    "recent_change:migration",
    "auth:works",
    "surface:workspace_access",
    "group_membership:Migrated-CSM",
    "scim_sync:complete",
    "workspace_role_missing:Migrated-CSM"
  ],
  "unknowns": [],
  "candidate_branches": [
    "missing_workspace_role",
    "missing_workspace_role_inheritance"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "scim_sync_delay",
    "stale_entitlement_cache"
  ],
  "next_check": "Confirm whether Migrated-CSM should inherit Workspace Member after migration.",
  "handoff_notes": [
    "Known: surface:workspace_access; group_membership:Migrated-CSM; scim_sync:complete; workspace_role_missing:Migrated-CSM",
    "Branches: missing_workspace_role; missing_workspace_role_inheritance",
    "Next check: Confirm whether Migrated-CSM should inherit Workspace Member after migration."
  ],
  "final_cause": "missing_workspace_role_inheritance",
  "root_cause_evidence_seen": true
}
```

## Billing Plan Mismatch

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I cannot log in. | reported_issue:login | actual_surface | login_failure | Confirm whether login itself fails or whether a page after login is wrong. | pass | - |
| 2 | customer | No, login works. The billing page shows the wrong plan. | reported_issue:login; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch | Check whether the billing entitlement refresh completed after the upgrade. | pass | - |
| 3 | agent | When did the plan change? | reported_issue:login; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch | Check whether the billing entitlement refresh completed after the upgrade. | pass | - |
| 4 | customer | We upgraded yesterday. | reported_issue:login; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | billing_entitlement_refresh_pending; invoice_app_mismatch | Check the billing entitlement refresh job and re-sync the plan entitlement. | pass | - |

### Final State

```json
{
  "case_id": "billing_plan_mismatch",
  "version": 5,
  "facts": [
    "reported_issue:login",
    "auth:works",
    "correction:login_works",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "recent_change:upgrade",
    "invoice_plan:pro",
    "app_entitlement_plan:starter",
    "billing_refresh:pending"
  ],
  "unknowns": [],
  "candidate_branches": [
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure"
  ],
  "next_check": "Check the billing entitlement refresh job and re-sync the plan entitlement.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Branches: billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Check the billing entitlement refresh job and re-sync the plan entitlement."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Corrected Billing After Access Report

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after migration. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 2 | customer | Actually, correction: login works and the workspace opens. The billing page is showing the wrong plan after we upgraded. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | stale_entitlement_cache; billing_entitlement_refresh_pending; invoice_app_mismatch | Check the billing entitlement refresh job and re-sync the plan entitlement. | pass | - |

### Final State

```json
{
  "case_id": "corrected_billing_after_access_report",
  "version": 3,
  "facts": [
    "symptom:workspace_access_loss",
    "affected_scope:three_users",
    "recent_change:migration",
    "auth:works",
    "surface:workspace_access",
    "correction:login_works",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "recent_change:upgrade",
    "invoice_plan:pro",
    "app_entitlement_plan:starter",
    "billing_refresh:pending"
  ],
  "unknowns": [],
  "candidate_branches": [
    "stale_entitlement_cache",
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "scim_sync_delay"
  ],
  "next_check": "Check the billing entitlement refresh job and re-sync the plan entitlement.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Branches: stale_entitlement_cache; billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Check the billing entitlement refresh job and re-sync the plan entitlement."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Invite Email Not Arriving

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Um, yeah, so I am trying to invite a new admin. | flow:admin_invite | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | pass | - |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | pass | - |
| 3 | customer | Yes, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

### Final State

```json
{
  "case_id": "invite_email_not_arriving",
  "version": 4,
  "facts": [
    "flow:admin_invite",
    "symptom:invite_email_not_received",
    "invite_status:created",
    "email_delivery:suppressed",
    "domain_policy:dmarc_reject"
  ],
  "unknowns": [],
  "candidate_branches": [
    "email_delivery_suppressed",
    "domain_policy_rejection"
  ],
  "ruled_out_branches": [
    "invite_not_created"
  ],
  "next_check": "Inspect email suppression and DMARC policy for the recipient domain.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Inspect email suppression and DMARC policy for the recipient domain."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Invite With Irrelevant Billing Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I am trying to invite a new admin, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite delivery status, suppression list, and domain policy results. | pass | - |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | pass | - |
| 3 | customer | Yes, the invite exists in the admin page, but no email arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

### Final State

```json
{
  "case_id": "invite_with_irrelevant_billing_context",
  "version": 4,
  "facts": [
    "flow:admin_invite",
    "symptom:invite_email_not_received",
    "invite_status:created",
    "email_delivery:suppressed",
    "domain_policy:dmarc_reject"
  ],
  "unknowns": [],
  "candidate_branches": [
    "email_delivery_suppressed",
    "domain_policy_rejection"
  ],
  "ruled_out_branches": [
    "invite_not_created"
  ],
  "next_check": "Inspect email suppression and DMARC policy for the recipient domain.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Inspect email suppression and DMARC policy for the recipient domain."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Level 2 Conflicting Migration Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 2 | agent | Can they sign in at all, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 3 | customer | They can sign in, and they reach the workspace switcher, but the new workspace will not open. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Check entitlement cache status before naming a final cause. | pass | - |
| 4 | agent | I am checking the migrated group role and entitlement cache now. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Check entitlement cache status before naming a final cause. | pass | - |
| 5 | customer | It still fails after they refresh their sessions. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Refresh the entitlement cache and confirm workspace access works after refresh. | pass | - |

### Final State

```json
{
  "case_id": "level2_conflicting_migration_context",
  "version": 7,
  "facts": [
    "symptom:workspace_access_loss",
    "affected_scope:three_users",
    "recent_change:migration",
    "auth:works",
    "surface:workspace_access",
    "workspace_role:present",
    "scim_sync:complete",
    "entitlement_cache:stale"
  ],
  "unknowns": [],
  "candidate_branches": [
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "missing_workspace_role_inheritance",
    "scim_sync_delay"
  ],
  "next_check": "Refresh the entitlement cache and confirm workspace access works after refresh.",
  "handoff_notes": [
    "Known: surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Branches: stale_entitlement_cache",
    "Next check: Refresh the entitlement cache and confirm workspace access works after refresh."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

## Level 2 Irrelevant Then Late Invite Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I sent an admin invite but the email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite delivery status, suppression list, and domain policy results. | pass | - |
| 2 | agent | I am checking whether the invite was created and whether delivery bounced. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | pass | - |
| 3 | customer | The recipient checked spam and still does not see the invite email. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite delivery status, suppression list, and domain policy results. | pass | - |
| 4 | agent | I am checking suppression and recipient-domain policy now. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

### Final State

```json
{
  "case_id": "level2_irrelevant_then_late_invite_context",
  "version": 5,
  "facts": [
    "flow:admin_invite",
    "symptom:invite_email_not_received",
    "invite_status:created",
    "email_delivery:suppressed",
    "domain_policy:dmarc_reject"
  ],
  "unknowns": [],
  "candidate_branches": [
    "email_delivery_suppressed",
    "domain_policy_rejection"
  ],
  "ruled_out_branches": [
    "invite_not_created"
  ],
  "next_check": "Inspect email suppression and DMARC policy for the recipient domain.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Inspect email suppression and DMARC policy for the recipient domain."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Level 2 Late Billing Evidence

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | One of our admins says they cannot log in after yesterday's upgrade. | reported_issue:login; recent_change:upgrade | actual_surface | login_failure | Confirm whether login itself fails or whether a page after login is wrong. | pass | - |
| 2 | agent | Is login itself failing, or do they get in and then see the wrong page? | reported_issue:login; recent_change:upgrade | actual_surface | login_failure | Confirm whether login itself fails or whether a page after login is wrong. | pass | - |
| 3 | customer | No login works. The billing page is the problem; it still shows the wrong plan. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch | Check whether the billing entitlement refresh completed after the upgrade. | pass | - |
| 4 | agent | I am checking whether the invoice and app entitlement agree after the upgrade. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch | Check whether the billing entitlement refresh completed after the upgrade. | pass | - |
| 5 | customer | The invoice shows Pro, but the app still behaves like Starter. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | billing_entitlement_refresh_pending; invoice_app_mismatch | Check the billing entitlement refresh job and re-sync the plan entitlement. | pass | - |

### Final State

```json
{
  "case_id": "level2_late_billing_evidence",
  "version": 6,
  "facts": [
    "reported_issue:login",
    "recent_change:upgrade",
    "auth:works",
    "correction:login_works",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "invoice_plan:pro",
    "app_entitlement_plan:starter",
    "billing_refresh:pending"
  ],
  "unknowns": [],
  "candidate_branches": [
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "scim_sync_delay"
  ],
  "next_check": "Check the billing entitlement refresh job and re-sync the plan entitlement.",
  "handoff_notes": [
    "Known: symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Branches: billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Check the billing entitlement refresh job and re-sync the plan entitlement."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Level 2 Unresolved Workspace Handoff

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 2 | agent | Can they sign in at all, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 3 | customer | They can sign in, but the workspace still will not open. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache; upstream_service_incident | Escalate with cache status and service incident checks still open. | pass | - |
| 4 | agent | I checked role assignment and SCIM. I am going to hand this to product support with the remaining cache check. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache; upstream_service_incident | Escalate with cache status and service incident checks still open. | pass | - |

### Final State

```json
{
  "case_id": "level2_unresolved_workspace_handoff",
  "version": 5,
  "facts": [
    "symptom:workspace_access_loss",
    "affected_scope:three_users",
    "recent_change:migration",
    "auth:works",
    "surface:workspace_access",
    "workspace_role:present",
    "scim_sync:complete"
  ],
  "unknowns": [
    "cache_status"
  ],
  "candidate_branches": [
    "stale_entitlement_cache",
    "upstream_service_incident"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "missing_workspace_role_inheritance",
    "scim_sync_delay"
  ],
  "next_check": "Escalate with cache status and service incident checks still open.",
  "handoff_notes": [
    "Known: auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete",
    "Unknowns: cache_status",
    "Branches: stale_entitlement_cache; upstream_service_incident",
    "Next check: Escalate with cache status and service incident checks still open."
  ],
  "final_cause": "",
  "root_cause_evidence_seen": false
}
```

## Stale Cache After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 2 | agent | Can they sign in, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Can the affected users sign in, or are they blocked at login? | pass | - |
| 3 | customer | They can sign in, but the workspace still says they do not have access. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Refresh the entitlement cache and confirm workspace access works after refresh. | pass | - |

### Final State

```json
{
  "case_id": "stale_cache_after_migration",
  "version": 4,
  "facts": [
    "symptom:workspace_access_loss",
    "affected_scope:three_users",
    "recent_change:migration",
    "auth:works",
    "surface:workspace_access",
    "workspace_role:present",
    "scim_sync:complete",
    "entitlement_cache:stale"
  ],
  "unknowns": [],
  "candidate_branches": [
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "scim_sync_delay"
  ],
  "next_check": "Refresh the entitlement cache and confirm workspace access works after refresh.",
  "handoff_notes": [
    "Known: surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Branches: stale_entitlement_cache",
    "Next check: Refresh the entitlement cache and confirm workspace access works after refresh."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

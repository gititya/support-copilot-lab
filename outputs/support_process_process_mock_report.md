# Support Process Lab Report

Run: `process_mock`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| access_after_migration | 18/18 | 100% | yes | missing_workspace_role_inheritance |
| billing_plan_mismatch | 24/24 | 100% | yes | billing_entitlement_refresh_pending |
| invite_email_not_arriving | 18/18 | 100% | yes | domain_policy_rejection |

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
  "version": 3,
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
  "version": 4,
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

## Invite Email Not Arriving

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Um, yeah, so I am trying to invite a new admin. | flow:admin_invite | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | pass | - |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | pass | - |
| 3 | customer | Yes, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject | invite_created; email_delivery_status | email_delivery_suppressed; domain_policy_rejection; invite_not_created | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

### Final State

```json
{
  "case_id": "invite_email_not_arriving",
  "version": 3,
  "facts": [
    "flow:admin_invite",
    "symptom:invite_email_not_received",
    "invite_status:created",
    "email_delivery:suppressed",
    "domain_policy:dmarc_reject"
  ],
  "unknowns": [
    "invite_created",
    "email_delivery_status"
  ],
  "candidate_branches": [
    "email_delivery_suppressed",
    "domain_policy_rejection",
    "invite_not_created"
  ],
  "ruled_out_branches": [
    "invite_not_created"
  ],
  "next_check": "Inspect email suppression and DMARC policy for the recipient domain.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Unknowns: invite_created; email_delivery_status",
    "Branches: email_delivery_suppressed; domain_policy_rejection; invite_not_created",
    "Next check: Inspect email suppression and DMARC policy for the recipient domain."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

# Support Process Lab Report

Run: `predictive_mock`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| access_after_migration | 16/18 | 89% | yes | missing_workspace_role_inheritance |
| billing_plan_mismatch | 19/24 | 79% | yes | billing_entitlement_refresh_pending |
| corrected_billing_after_access_report | 11/12 | 92% | yes | billing_entitlement_refresh_pending |
| invite_email_not_arriving | 16/18 | 89% | yes | domain_policy_rejection |
| invite_with_irrelevant_billing_context | 16/18 | 89% | yes | domain_policy_rejection |
| level2_conflicting_migration_context | 28/30 | 93% | yes | stale_entitlement_cache |
| level2_irrelevant_then_late_invite_context | 21/24 | 88% | yes | domain_policy_rejection |
| level2_late_billing_evidence | 24/30 | 80% | yes | billing_entitlement_refresh_pending |
| level2_unresolved_workspace_handoff | 22/24 | 92% | yes | missing_workspace_role_inheritance |
| level3_conflicting_systems_unresolved_handoff | 40/48 | 83% | yes | billing_entitlement_gap |
| level3_misrouted_ratelimit_actually_webhook_auth | 46/54 | 85% | yes | webhook_auth_rotation |
| stale_cache_after_migration | 16/18 | 89% | yes | stale_entitlement_cache |

## Access After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Can they sign in at all, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
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
| 1 | customer | I cannot log in. | reported_issue:login | actual_surface | login_failure | Confirm whether login itself fails or whether a page after login is wrong. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | customer | No, login works. The billing page shows the wrong plan. | reported_issue:login; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch; login_failure | Check whether the billing entitlement refresh completed after the upgrade. | needs attention | ruled_out_branches: login_failure; final_cause_timing: final cause must wait for product/support evidence |
| 3 | agent | When did the plan change? | reported_issue:login; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch; login_failure | Check whether the billing entitlement refresh completed after the upgrade. | needs attention | ruled_out_branches: login_failure; final_cause_timing: final cause must wait for product/support evidence |
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
    "login_failure",
    "missing_workspace_role",
    "scim_sync_delay"
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
| 1 | customer | Three users lost access after migration. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | customer | Actually, correction: login works and the workspace opens. The billing page is showing the wrong plan after we upgraded. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | stale_entitlement_cache; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; invoice_app_mismatch | Check the billing entitlement refresh job and re-sync the plan entitlement. | pass | - |

### Final State

```json
{
  "case_id": "corrected_billing_after_access_report",
  "version": 2,
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
    "missing_workspace_role_inheritance",
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
    "Branches: stale_entitlement_cache; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Check the billing entitlement refresh job and re-sync the plan entitlement."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Invite Email Not Arriving

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Um, yeah, so I am trying to invite a new admin. | flow:admin_invite | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | Yes, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

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
    "Next check: Inspect email suppression and DMARC policy for the recipient domain.",
    "Predicted email policy rejection before delivery evidence."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Invite With Irrelevant Billing Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I am trying to invite a new admin, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite delivery status, suppression list, and domain policy results. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | Yes, the invite exists in the admin page, but no email arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

### Final State

```json
{
  "case_id": "invite_with_irrelevant_billing_context",
  "version": 3,
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
    "Next check: Inspect email suppression and DMARC policy for the recipient domain.",
    "Predicted email policy rejection before delivery evidence."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Level 2 Conflicting Migration Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Can they sign in at all, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | They can sign in, and they reach the workspace switcher, but the new workspace will not open. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache; missing_workspace_role_inheritance | Check entitlement cache status or product incident signals before naming a final cause. | pass | - |
| 4 | agent | I am checking the migrated group role and entitlement cache now. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache; missing_workspace_role_inheritance | Check entitlement cache status or product incident signals before naming a final cause. | pass | - |
| 5 | customer | It still fails after they refresh their sessions. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Refresh the entitlement cache and confirm workspace access works after refresh. | pass | - |

### Final State

```json
{
  "case_id": "level2_conflicting_migration_context",
  "version": 5,
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
    "scim_sync_delay",
    "missing_workspace_role_inheritance"
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
| 1 | customer | I sent an admin invite but the email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite delivery status, suppression list, and domain policy results. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | I am checking whether the invite was created and whether delivery bounced. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the invite was created and whether email delivery bounced or was suppressed. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | The recipient checked spam and still does not see the invite email. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite delivery status, suppression list, and domain policy results. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 4 | agent | I am checking suppression and recipient-domain policy now. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Inspect email suppression and DMARC policy for the recipient domain. | pass | - |

### Final State

```json
{
  "case_id": "level2_irrelevant_then_late_invite_context",
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

## Level 2 Late Billing Evidence

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | One of our admins says they cannot log in after yesterday's upgrade. | reported_issue:login; recent_change:upgrade | actual_surface | login_failure | Confirm whether login itself fails or whether a page after login is wrong. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Is login itself failing, or do they get in and then see the wrong page? | reported_issue:login; recent_change:upgrade | actual_surface | login_failure | Confirm whether login itself fails or whether a page after login is wrong. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | No login works. The billing page is the problem; it still shows the wrong plan. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch; login_failure | Check whether the billing entitlement refresh completed after the upgrade. | needs attention | ruled_out_branches: login_failure; final_cause_timing: final cause must wait for product/support evidence |
| 4 | agent | I am checking whether the invoice and app entitlement agree after the upgrade. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch; login_failure | Check whether the billing entitlement refresh completed after the upgrade. | needs attention | ruled_out_branches: login_failure; final_cause_timing: final cause must wait for product/support evidence |
| 5 | customer | The invoice shows Pro, but the app still behaves like Starter. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | billing_entitlement_refresh_pending; invoice_app_mismatch | Check the billing entitlement refresh job and re-sync the plan entitlement. | pass | - |

### Final State

```json
{
  "case_id": "level2_late_billing_evidence",
  "version": 5,
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
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Can they sign in at all, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | They can sign in, but the workspace still will not open. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache; missing_workspace_role_inheritance | Check entitlement cache status or product incident signals before naming a final cause. | pass | - |
| 4 | agent | I checked role assignment and SCIM. I am going to hand this to product support with the remaining cache check. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache; missing_workspace_role_inheritance | Check entitlement cache status or product incident signals before naming a final cause. | pass | - |

### Final State

```json
{
  "case_id": "level2_unresolved_workspace_handoff",
  "version": 4,
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
    "missing_workspace_role_inheritance"
  ],
  "ruled_out_branches": [
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "scim_sync_delay"
  ],
  "next_check": "Check entitlement cache status or product incident signals before naming a final cause.",
  "handoff_notes": [
    "Known: auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete",
    "Unknowns: cache_status",
    "Branches: stale_entitlement_cache; missing_workspace_role_inheritance",
    "Next check: Check entitlement cache status or product incident signals before naming a final cause."
  ],
  "final_cause": "missing_workspace_role_inheritance",
  "root_cause_evidence_seen": true
}
```

## Level 3 Conflicting Systems Unresolved Handoff

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Our enterprise workspace still says we are not entitled even though the renewal completed. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed | affected_scope; billing_entitlement_status; provisioning_status | billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay | Confirm whether all users see the entitlement block or only a few seats. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Do all users see the entitlement block, or only a few seats? | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users | billing_entitlement_status; provisioning_status; affected_scope | billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay | Check billing entitlement and provisioning state side by side. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | All users in the workspace see the entitlement block. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users | billing_entitlement_status; provisioning_status; affected_scope | billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay | Check billing entitlement and provisioning state side by side. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 4 | agent | I am checking billing entitlement and provisioning state side by side. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready | provisioning_status; affected_scope; provisioning_job_status; entitlement_cache_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch; billing_entitlement_gap | Escalate with provisioning job status and entitlement cache status still open. | needs attention | ruled_out_branches: billing_entitlement_gap |
| 5 | customer | Billing sent us a receipt and the admin page says the renewal is active. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active | provisioning_status; affected_scope; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch; billing_entitlement_gap | Escalate with provisioning job status and entitlement cache status still open. | needs attention | ruled_out_branches: billing_entitlement_gap |
| 6 | agent | Provisioning still disagrees, so I need the job status before I call a root cause. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active | provisioning_status; affected_scope; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch; billing_entitlement_gap | Escalate with provisioning job status and entitlement cache status still open. | needs attention | ruled_out_branches: billing_entitlement_gap |
| 7 | customer | We need an update for our implementation owner today. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update | provisioning_status; affected_scope; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch; billing_entitlement_gap | Escalate with provisioning job status and entitlement cache status still open. | needs attention | ruled_out_branches: billing_entitlement_gap |
| 8 | agent | I am handing this to product support with billing entitled, provisioning blocked, and the job status still open. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update | provisioning_status; affected_scope; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch; billing_entitlement_gap | Escalate with provisioning job status and entitlement cache status still open. | needs attention | ruled_out_branches: billing_entitlement_gap |

### Final State

```json
{
  "case_id": "level3_conflicting_systems_unresolved_handoff",
  "version": 8,
  "facts": [
    "surface:workspace_access",
    "surface:entitlement_access",
    "symptom:entitlement_block",
    "renewal:completed",
    "affected_scope:all_workspace_users",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "billing:entitled",
    "payment:clear",
    "provisioning:not_ready",
    "renewal:active",
    "handoff_need:implementation_owner_update"
  ],
  "unknowns": [
    "provisioning_status",
    "affected_scope",
    "provisioning_job_status",
    "entitlement_cache_status",
    "billing_entitlement_status"
  ],
  "candidate_branches": [
    "provisioning_state_mismatch",
    "entitlement_cache_delay",
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch",
    "billing_entitlement_gap"
  ],
  "ruled_out_branches": [
    "payment_failure"
  ],
  "next_check": "Escalate with provisioning job status and entitlement cache status still open.",
  "handoff_notes": [
    "Known: payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update",
    "Unknowns: provisioning_status; affected_scope; provisioning_job_status; entitlement_cache_status",
    "Branches: provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Escalate with provisioning job status and entitlement cache status still open."
  ],
  "final_cause": "billing_entitlement_gap",
  "root_cause_evidence_seen": true
}
```

## Level 3 Misrouted Rate Limit Actually Webhook Auth

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Our API calls are getting rate-limited after we scaled traffic this week. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale | traffic_scope; quota_status; webhook_auth_status | quota_exhaustion; webhook_auth_rotation | Confirm whether every API route is failing or only one integration path. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Is every API route failing, or only one integration path? | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale | traffic_scope; quota_status; webhook_auth_status | quota_exhaustion; webhook_auth_rotation | Confirm whether every API route is failing or only one integration path. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | It is not every route. A subset of webhook callbacks fails, but normal API reads still work. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work | quota_status; webhook_auth_status | quota_exhaustion; webhook_auth_rotation | Compare quota counters with webhook auth status for the failing callback path. | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 4 | agent | I am checking quota usage and webhook authentication for that service. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit | webhook_auth_status | webhook_auth_rotation; quota_exhaustion | Compare webhook auth status for the failing service before naming a final cause. | needs attention | ruled_out_branches: quota_exhaustion |
| 5 | customer | The failures started right after the partner service rolled a new deployment. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy | webhook_auth_status | webhook_auth_rotation; quota_exhaustion | Compare webhook auth status for the failing service before naming a final cause. | needs attention | ruled_out_branches: quota_exhaustion |
| 6 | agent | Do successful and failed callbacks use the same signing secret? | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy | webhook_auth_status | webhook_auth_rotation; quota_exhaustion | Compare webhook auth status for the failing service before naming a final cause. | needs attention | ruled_out_branches: quota_exhaustion |
| 7 | customer | Only the legacy worker fails. The new worker callbacks succeed. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed | webhook_auth_status | webhook_auth_rotation; quota_exhaustion | Compare webhook auth status for the legacy worker before naming a final cause. | needs attention | ruled_out_branches: quota_exhaustion |
| 8 | agent | I am comparing webhook signing-secret rotation and quota counters now. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed | webhook_auth_status | webhook_auth_rotation; quota_exhaustion | Compare webhook auth status for the legacy worker before naming a final cause. | needs attention | ruled_out_branches: quota_exhaustion |
| 9 | customer | That matches what our service owner suspected: the legacy worker still has old webhook auth config. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed; webhook_signing_secret:rotated; webhook_auth:legacy_secret |  | webhook_auth_rotation | Update the legacy worker signing secret and replay one failed webhook callback. | pass | - |

### Final State

```json
{
  "case_id": "level3_misrouted_ratelimit_actually_webhook_auth",
  "version": 9,
  "facts": [
    "surface:api_delivery",
    "symptom:rate_limit_errors",
    "recent_change:traffic_scale",
    "traffic_scope:subset",
    "surface:webhook_callbacks",
    "normal_api_reads:work",
    "quota:under_limit",
    "recent_change:partner_deploy",
    "failure_scope:legacy_worker",
    "new_worker:callbacks_succeed",
    "webhook_signing_secret:rotated",
    "webhook_auth:legacy_secret"
  ],
  "unknowns": [],
  "candidate_branches": [
    "webhook_auth_rotation"
  ],
  "ruled_out_branches": [
    "quota_exhaustion"
  ],
  "next_check": "Update the legacy worker signing secret and replay one failed webhook callback.",
  "handoff_notes": [
    "Known: failure_scope:legacy_worker; new_worker:callbacks_succeed; webhook_signing_secret:rotated; webhook_auth:legacy_secret",
    "Branches: webhook_auth_rotation",
    "Next check: Update the legacy worker signing secret and replay one failed webhook callback."
  ],
  "final_cause": "webhook_auth_rotation",
  "root_cause_evidence_seen": true
}
```

## Stale Cache After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 2 | agent | Can they sign in, or is login blocked? | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration | auth_status; workspace_role_assignment | login_block; missing_workspace_role; scim_sync_delay; stale_entitlement_cache; missing_workspace_role_inheritance | Can the affected users sign in, or are they blocked at login? | needs attention | final_cause_timing: final cause must wait for product/support evidence |
| 3 | customer | They can sign in, but the workspace still says they do not have access. | symptom:workspace_access_loss; affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache; missing_workspace_role_inheritance | Refresh the entitlement cache and confirm workspace access works after refresh. | pass | - |

### Final State

```json
{
  "case_id": "stale_cache_after_migration",
  "version": 3,
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
    "stale_entitlement_cache",
    "missing_workspace_role_inheritance"
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
    "Branches: stale_entitlement_cache; missing_workspace_role_inheritance",
    "Next check: Refresh the entitlement cache and confirm workspace access works after refresh."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

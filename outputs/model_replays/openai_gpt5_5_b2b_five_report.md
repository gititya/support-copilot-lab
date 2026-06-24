# Support Process Lab Report

Run: `real-model_b2b-five`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| level2_conflicting_migration_context | 30/30 | 100% | yes | stale_entitlement_cache |
| level2_late_billing_evidence | 28/30 | 93% | yes | billing_entitlement_refresh_pending |
| level2_irrelevant_then_late_invite_context | 23/24 | 96% | yes | domain_policy_rejection |
| corrected_billing_after_access_report | 12/12 | 100% | yes | billing_entitlement_refresh_pending |
| stale_cache_after_migration | 17/18 | 94% | yes | stale_entitlement_cache |

## Level 2 Conflicting Migration Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Ask whether the three users can sign in successfully and only lose access after login, or whether login itself fails. | pass | - |
| 2 | agent | Can they sign in at all, or is login blocked? | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Wait for the customer to confirm whether the three users can sign in successfully or whether login is blocked. | pass | - |
| 3 | customer | They can sign in, and they reach the workspace switcher, but the new workspace will not open. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Check the entitlement cache status for the three users on the new workspace, or trigger an entitlement refresh and have them retry opening the workspace. | pass | - |
| 4 | agent | I am checking the migrated group role and entitlement cache now. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Confirm the entitlement cache status for the three affected users on the migrated workspace, and if stale, trigger an entitlement refresh before asking them to retry workspace access. | pass | - |
| 5 | customer | It still fails after they refresh their sessions. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Trigger an entitlement cache refresh for the three affected users on the migrated workspace, then ask them to retry workspace access. | pass | - |

### Final State

```json
{
  "case_id": "level2_conflicting_migration_context",
  "version": 5,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "surface:workspace_access",
    "symptom:workspace_access_loss",
    "auth:works",
    "workspace_role:present",
    "scim_sync:complete",
    "entitlement_cache:stale"
  ],
  "unknowns": [],
  "candidate_branches": [
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "scim_sync_delay",
    "login_block",
    "login_failure",
    "missing_workspace_role",
    "missing_workspace_role_inheritance"
  ],
  "next_check": "Trigger an entitlement cache refresh for the three affected users on the migrated workspace, then ask them to retry workspace access.",
  "handoff_notes": [
    "Known: auth:works; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Branches: stale_entitlement_cache",
    "Next check: Trigger an entitlement cache refresh for the three affected users on the migrated workspace, then ask them to retry workspace access.",
    "New context confirms entitlement_cache:stale while workspace_role:present and scim_sync:complete remain known. Customer reports session refresh did not resolve access failure. Final cause is stale_entitlement_cache; next action is entitlement cache refresh for the three affected users."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

## Level 2 Late Billing Evidence

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | One of our admins says they cannot log in after yesterday's upgrade. | reported_issue:login; recent_change:upgrade | auth_status | login_failure; upstream_service_incident | Ask whether the affected admin can reach the sign-in page and what exact error or behavior occurs during login. | needs attention | unknowns: actual_surface |
| 2 | agent | Is login itself failing, or do they get in and then see the wrong page? | reported_issue:login; recent_change:upgrade | auth_status | login_failure; upstream_service_incident | Wait for the customer to confirm whether login itself is failing or the user can sign in and sees the wrong page. | needs attention | unknowns: actual_surface |
| 3 | customer | No login works. The billing page is the problem; it still shows the wrong plan. | recent_change:upgrade; correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status; cache_status | upstream_service_incident; billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Check the customer's billing/invoice plan and current app entitlement plan, then verify whether a billing entitlement refresh is pending. | pass | - |
| 4 | agent | I am checking whether the invoice and app entitlement agree after the upgrade. | recent_change:upgrade; correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status; cache_status | upstream_service_incident; billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Verify whether the invoice plan and app entitlement plan match, and check whether billing_entitlement_refresh_pending is present. | pass | - |
| 5 | customer | The invoice shows Pro, but the app still behaves like Starter. | recent_change:upgrade; correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending | cache_status | upstream_service_incident; billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Check whether the billing refresh can be completed or expedited, then verify the app entitlement plan changes from Starter to Pro. | pass | - |

### Final State

```json
{
  "case_id": "level2_late_billing_evidence",
  "version": 5,
  "facts": [
    "recent_change:upgrade",
    "correction:login_works",
    "auth:works",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "invoice_plan:pro",
    "app_entitlement_plan:starter",
    "billing_refresh:pending"
  ],
  "unknowns": [
    "cache_status"
  ],
  "candidate_branches": [
    "upstream_service_incident",
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch",
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_failure",
    "missing_workspace_role",
    "scim_sync_delay"
  ],
  "next_check": "Check whether the billing refresh can be completed or expedited, then verify the app entitlement plan changes from Starter to Pro.",
  "handoff_notes": [
    "Known: symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Unknowns: cache_status",
    "Branches: upstream_service_incident; billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache",
    "Next check: Check whether the billing refresh can be completed or expedited, then verify the app entitlement plan changes from Starter to Pro.",
    "New evidence confirms invoice_plan:pro, app_entitlement_plan:starter, and billing_refresh:pending. This directly supports final_cause billing_entitlement_refresh_pending. cache_status remains unknown."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Level 2 Irrelevant Then Late Invite Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I sent an admin invite but the email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Check whether the admin invite record was created and inspect email delivery status for the invited recipient. | pass | - |
| 2 | agent | I am checking whether the invite was created and whether delivery bounced. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Check whether the admin invite record was created and inspect email delivery status for the invited recipient. | pass | - |
| 3 | customer | The recipient checked spam and still does not see the invite email. | flow:admin_invite; symptom:invite_email_not_received; recipient_checked_spam:no_invite_email_found | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Check whether the admin invite record was created and inspect email delivery status for the invited recipient. | pass | - |
| 4 | agent | I am checking suppression and recipient-domain policy now. | flow:admin_invite; symptom:invite_email_not_received; recipient_checked_spam:no_invite_email_found; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | domain_policy_rejection | Tell the customer the invite was created but delivery was suppressed because the recipient domain rejected it by DMARC policy; ask them to adjust recipient-domain mail policy or provide an alternate recipient, then resend the invite. | needs attention | candidate_branches: email_delivery_suppressed |

### Final State

```json
{
  "case_id": "level2_irrelevant_then_late_invite_context",
  "version": 4,
  "facts": [
    "flow:admin_invite",
    "symptom:invite_email_not_received",
    "recipient_checked_spam:no_invite_email_found",
    "invite_status:created",
    "email_delivery:suppressed",
    "domain_policy:dmarc_reject"
  ],
  "unknowns": [],
  "candidate_branches": [
    "domain_policy_rejection"
  ],
  "ruled_out_branches": [
    "invite_not_created"
  ],
  "next_check": "Tell the customer the invite was created but delivery was suppressed because the recipient domain rejected it by DMARC policy; ask them to adjust recipient-domain mail policy or provide an alternate recipient, then resend the invite.",
  "handoff_notes": [
    "Known: recipient_checked_spam:no_invite_email_found; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: domain_policy_rejection",
    "Next check: Tell the customer the invite was created but delivery was suppressed because the recipient domain rejected it by DMARC policy; ask them to adjust recipient-domain mail policy or provide an alternate recipient, then resend the invite.",
    "New delivery context confirms invite_status:created, email_delivery:suppressed, and domain_policy:dmarc_reject. invite_created and email_delivery_status are resolved. invite_not_created is ruled out. Final cause is domain_policy_rejection."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Corrected Billing After Access Report

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after migration. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | login_failure; missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Ask whether the three affected users can sign in successfully, and if they can sign in, whether they can see the migrated workspace. | pass | - |
| 2 | customer | Actually, correction: login works and the workspace opens. The billing page is showing the wrong plan after we upgraded. | affected_scope:three_users; recent_change:migration; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | stale_entitlement_cache; billing_entitlement_refresh_pending; invoice_app_mismatch | Confirm whether the billing page still shows Starter after a refresh/sign-out cycle, and check whether the pending billing entitlement refresh has completed. | pass | - |

### Final State

```json
{
  "case_id": "corrected_billing_after_access_report",
  "version": 2,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
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
    "stale_entitlement_cache",
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch"
  ],
  "ruled_out_branches": [
    "login_failure",
    "scim_sync_delay",
    "missing_workspace_role"
  ],
  "next_check": "Confirm whether the billing page still shows Starter after a refresh/sign-out cycle, and check whether the pending billing entitlement refresh has completed.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Branches: stale_entitlement_cache; billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Confirm whether the billing page still shows Starter after a refresh/sign-out cycle, and check whether the pending billing entitlement refresh has completed.",
    "Customer corrected the issue: login works and the workspace opens; actual surface is billing_plan with wrong_plan_shown after upgrade. Billing context shows invoice_plan:pro, app_entitlement_plan:starter, and billing_refresh:pending."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Stale Cache After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Ask whether the three affected users can successfully sign in/login, and whether the issue happens after login when opening the migrated workspace. | pass | - |
| 2 | agent | Can they sign in, or is login blocked? | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | missing_workspace_role; scim_sync_delay; stale_entitlement_cache | Wait for the customer to confirm whether the three affected users can successfully sign in/login, and whether the issue occurs after login when opening the migrated workspace. | pass | - |
| 3 | customer | They can sign in, but the workspace still says they do not have access. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; correction:login_works; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Refresh or invalidate the affected users' workspace entitlement cache, then have them retry opening the migrated workspace. | needs attention | ruled_out_branches: login_block |

### Final State

```json
{
  "case_id": "stale_cache_after_migration",
  "version": 3,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "surface:workspace_access",
    "symptom:workspace_access_loss",
    "auth:works",
    "correction:login_works",
    "workspace_role:present",
    "scim_sync:complete",
    "entitlement_cache:stale"
  ],
  "unknowns": [],
  "candidate_branches": [
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "scim_sync_delay",
    "missing_workspace_role"
  ],
  "next_check": "Refresh or invalidate the affected users' workspace entitlement cache, then have them retry opening the migrated workspace.",
  "handoff_notes": [
    "Known: correction:login_works; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Branches: stale_entitlement_cache",
    "Next check: Refresh or invalidate the affected users' workspace entitlement cache, then have them retry opening the migrated workspace.",
    "Customer confirmed the affected users can sign in, but still see no workspace access. Admin context shows workspace_role:present and scim_sync:complete, with entitlement_cache:stale. Final cause is stale_entitlement_cache; proceed with cache refresh/invalidation and retry."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

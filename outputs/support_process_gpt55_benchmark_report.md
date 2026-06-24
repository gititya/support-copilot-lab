# Support Process Lab Report

Run: `gpt55_benchmark`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| access_after_migration | 13/18 | 72% | yes | missing_workspace_role_inheritance |
| billing_plan_mismatch | 23/24 | 96% | yes | billing_entitlement_refresh_pending |
| corrected_billing_after_access_report | 10/12 | 83% | yes | billing_entitlement_refresh_pending |
| invite_email_not_arriving | 17/18 | 94% | yes | domain_policy_rejection |
| invite_with_irrelevant_billing_context | 17/18 | 94% | yes | domain_policy_rejection |
| level2_conflicting_migration_context | 26/30 | 87% | yes | stale_entitlement_cache |
| level2_irrelevant_then_late_invite_context | 22/24 | 92% | yes | domain_policy_rejection |
| level2_late_billing_evidence | 25/30 | 83% | yes | billing_entitlement_refresh_pending |
| level2_unresolved_workspace_handoff | 23/24 | 96% | yes |  |
| stale_cache_after_migration | 13/18 | 72% | yes | stale_entitlement_cache |

## Access After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; symptom:workspace_access_loss | workspace_role_assignment; cache_status; billing_entitlement_status | missing_workspace_role; missing_workspace_role_inheritance; scim_sync_delay; stale_entitlement_cache; billing_entitlement_refresh_pending | Check the three affected users' workspace role assignment and inherited group/SCIM membership in the new workspace after migration. | needs attention | unknowns: auth_status; next_check: sign in |
| 2 | agent | Can they sign in at all, or is login blocked? | affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; symptom:workspace_access_loss | workspace_role_assignment; cache_status; billing_entitlement_status | missing_workspace_role; missing_workspace_role_inheritance; scim_sync_delay; stale_entitlement_cache; billing_entitlement_refresh_pending | Check the three affected users' workspace role assignment and inherited group/SCIM membership in the new workspace after migration. | needs attention | unknowns: auth_status; next_check: sign in |
| 3 | customer | They can sign in, but they cannot open the new workspace. | affected_scope:three_users; recent_change:migration; auth:works; surface:workspace_access; symptom:workspace_access_loss; group_membership:Migrated-CSM; scim_sync:complete; workspace_role_missing:Migrated-CSM | cache_status; billing_entitlement_status | missing_workspace_role_inheritance | Assign the appropriate workspace role to Migrated-CSM in the new workspace, then retest workspace access for the three affected users. | needs attention | next_check: inherit |

### Final State

```json
{
  "case_id": "access_after_migration",
  "version": 3,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "auth:works",
    "surface:workspace_access",
    "symptom:workspace_access_loss",
    "group_membership:Migrated-CSM",
    "scim_sync:complete",
    "workspace_role_missing:Migrated-CSM"
  ],
  "unknowns": [
    "cache_status",
    "billing_entitlement_status"
  ],
  "candidate_branches": [
    "missing_workspace_role_inheritance"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "scim_sync_delay",
    "stale_entitlement_cache"
  ],
  "next_check": "Assign the appropriate workspace role to Migrated-CSM in the new workspace, then retest workspace access for the three affected users.",
  "handoff_notes": [
    "Known: symptom:workspace_access_loss; group_membership:Migrated-CSM; scim_sync:complete; workspace_role_missing:Migrated-CSM",
    "Unknowns: cache_status; billing_entitlement_status",
    "Branches: missing_workspace_role_inheritance",
    "Next check: Assign the appropriate workspace role to Migrated-CSM in the new workspace, then retest workspace access for the three affected users.",
    "Direct admin context evidence: affected users are members of Migrated-CSM, SCIM is complete, and Migrated-CSM has no workspace role. This supports final_cause:missing_workspace_role_inheritance. Login remains ruled out because auth:works."
  ],
  "final_cause": "missing_workspace_role_inheritance",
  "root_cause_evidence_seen": true
}
```

## Billing Plan Mismatch

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I cannot log in. | reported_issue:login | auth_status; actual_surface | login_failure | Confirm whether authentication fails, what error appears, and whether the issue is actually on login or another surface after login. | needs attention | next_check: page |
| 2 | customer | No, login works. The billing page shows the wrong plan. | correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status; cache_status | invoice_app_mismatch; billing_entitlement_refresh_pending; stale_entitlement_cache | Verify the customer's current invoice/subscription plan versus the app entitlement plan shown on the billing page, and check whether there was a recent upgrade with pending billing refresh or stale entitlement cache. | pass | - |
| 3 | agent | When did the plan change? | correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status; cache_status | invoice_app_mismatch; billing_entitlement_refresh_pending; stale_entitlement_cache | Ask/confirm when the plan change occurred, then verify invoice_plan versus app_entitlement_plan and whether billing_refresh is pending or entitlement_cache is stale. | pass | - |
| 4 | customer | We upgraded yesterday. | correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending | cache_status | invoice_app_mismatch; billing_entitlement_refresh_pending; stale_entitlement_cache | Confirm/trigger completion of the pending billing entitlement refresh, then re-check app_entitlement_plan updates from Starter to Pro. | pass | - |

### Final State

```json
{
  "case_id": "billing_plan_mismatch",
  "version": 4,
  "facts": [
    "correction:login_works",
    "auth:works",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "recent_change:upgrade",
    "invoice_plan:pro",
    "app_entitlement_plan:starter",
    "billing_refresh:pending"
  ],
  "unknowns": [
    "cache_status"
  ],
  "candidate_branches": [
    "invoice_app_mismatch",
    "billing_entitlement_refresh_pending",
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_failure"
  ],
  "next_check": "Confirm/trigger completion of the pending billing entitlement refresh, then re-check app_entitlement_plan updates from Starter to Pro.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Unknowns: cache_status",
    "Branches: invoice_app_mismatch; billing_entitlement_refresh_pending; stale_entitlement_cache",
    "Next check: Confirm/trigger completion of the pending billing entitlement refresh, then re-check app_entitlement_plan updates from Starter to Pro.",
    "Customer confirmed upgrade occurred yesterday. Product/support context shows invoice_plan:pro, app_entitlement_plan:starter, and billing_refresh:pending, providing direct mechanism evidence for billing_entitlement_refresh_pending."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Corrected Billing After Access Report

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after migration. | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss | actual_surface; auth_status; workspace_role_assignment | login_failure; missing_workspace_role; missing_workspace_role_inheritance; scim_sync_delay | Clarify whether the three users can authenticate and whether the access loss is at login or workspace access; then check workspace role/group assignment after migration. | needs attention | candidate_branches: stale_entitlement_cache; next_check: sign in |
| 2 | customer | Actually, correction: login works and the workspace opens. The billing page is showing the wrong plan after we upgraded. | affected_scope:three_users; recent_change:migration; correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | invoice_app_mismatch; billing_entitlement_refresh_pending | Confirm entitlement refresh completion or trigger entitlement refresh, then recheck whether the billing page reflects invoice_plan:pro. | pass | - |

### Final State

```json
{
  "case_id": "corrected_billing_after_access_report",
  "version": 2,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "correction:login_works",
    "auth:works",
    "surface:billing_plan",
    "symptom:wrong_plan_shown",
    "recent_change:upgrade",
    "invoice_plan:pro",
    "app_entitlement_plan:starter",
    "billing_refresh:pending"
  ],
  "unknowns": [],
  "candidate_branches": [
    "invoice_app_mismatch",
    "billing_entitlement_refresh_pending"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "scim_sync_delay",
    "missing_workspace_role"
  ],
  "next_check": "Confirm entitlement refresh completion or trigger entitlement refresh, then recheck whether the billing page reflects invoice_plan:pro.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Branches: invoice_app_mismatch; billing_entitlement_refresh_pending",
    "Next check: Confirm entitlement refresh completion or trigger entitlement refresh, then recheck whether the billing page reflects invoice_plan:pro.",
    "Customer corrected initial access report: login works and workspace opens. Actual surface is billing_plan with wrong_plan_shown after upgrade. Product context shows invoice_plan:pro, app_entitlement_plan:starter, and billing_refresh:pending, which directly supports billing_entitlement_refresh_pending."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Invite Email Not Arriving

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Um, yeah, so I am trying to invite a new admin. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Check whether the admin invite was created and inspect invite status/email delivery logs for the recipient. | pass | - |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Confirm whether the invite shows as created in the admin page, then inspect invite status/email delivery logs for the recipient. | pass | - |
| 3 | customer | Yes, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Use the email delivery/domain policy evidence to have the recipient domain mail admin address the DMARC rejection or allow the invite sender, then resend the admin invite. | needs attention | next_check: suppression |

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
  "next_check": "Use the email delivery/domain policy evidence to have the recipient domain mail admin address the DMARC rejection or allow the invite sender, then resend the admin invite.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Use the email delivery/domain policy evidence to have the recipient domain mail admin address the DMARC rejection or allow the invite sender, then resend the admin invite.",
    "Product support context directly shows invite_status:created, email_delivery:suppressed, and domain_policy:dmarc_reject. invite_not_created is ruled out. Final cause set to domain_policy_rejection based on direct mechanism evidence."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Invite With Irrelevant Billing Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I am trying to invite a new admin, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Check whether the admin invite was created and inspect email delivery status/logs for suppression or domain rejection. | pass | - |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection; upstream_service_incident | Confirm whether the admin invite shows as created in the admin page, then inspect email delivery status/logs for suppression or domain rejection. | pass | - |
| 3 | customer | Yes, the invite exists in the admin page, but no email arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Proceed with remediation for domain_policy_rejection: ask customer to update/allowlist domain mail policy or provide the rejected message evidence to their mail administrator, then retry the admin invite. | needs attention | next_check: DMARC, suppression |

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
  "next_check": "Proceed with remediation for domain_policy_rejection: ask customer to update/allowlist domain mail policy or provide the rejected message evidence to their mail administrator, then retry the admin invite.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Proceed with remediation for domain_policy_rejection: ask customer to update/allowlist domain mail policy or provide the rejected message evidence to their mail administrator, then retry the admin invite.",
    "Customer confirmed invite exists in admin page. Product/support email context directly shows invite_status:created, email_delivery:suppressed, and domain_policy:dmarc_reject. Billing context remains unrelated. Final cause set to domain_policy_rejection."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Level 2 Conflicting Migration Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | missing_workspace_role_inheritance; scim_sync_delay; login_failure | Check whether the affected users can authenticate and whether their migrated group has workspace role assignments present. | needs attention | candidate_branches: missing_workspace_role, stale_entitlement_cache; next_check: sign in |
| 2 | agent | Can they sign in at all, or is login blocked? | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment | missing_workspace_role_inheritance; scim_sync_delay; login_failure | Check whether the affected users can authenticate and whether their migrated group has workspace role assignments present. | needs attention | candidate_branches: missing_workspace_role, stale_entitlement_cache; next_check: sign in |
| 3 | customer | They can sign in, and they reach the workspace switcher, but the new workspace will not open. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Check cache_status for the affected migrated workspace/users, especially whether entitlement_cache:stale is present. | pass | - |
| 4 | agent | I am checking the migrated group role and entitlement cache now. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Check cache_status for the affected migrated workspace/users, especially whether entitlement_cache:stale is present; confirm migrated group role context without reopening missing_workspace_role_inheritance unless workspace_role:present is contradicted. | pass | - |
| 5 | customer | It still fails after they refresh their sessions. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Proceed with entitlement cache remediation/refresh for the three affected migrated users and verify workspace access after cache refresh completes. | pass | - |

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
    "login_failure",
    "scim_sync_delay",
    "missing_workspace_role_inheritance",
    "login_block",
    "missing_workspace_role"
  ],
  "next_check": "Proceed with entitlement cache remediation/refresh for the three affected migrated users and verify workspace access after cache refresh completes.",
  "handoff_notes": [
    "Known: auth:works; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Branches: stale_entitlement_cache",
    "Next check: Proceed with entitlement cache remediation/refresh for the three affected migrated users and verify workspace access after cache refresh completes.",
    "Product/support context directly shows workspace_role:present and entitlement_cache:stale for the three affected migrated users. cache_status is no longer unknown. Keep missing_workspace_role_inheritance ruled out; final_cause is stale_entitlement_cache."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

## Level 2 Irrelevant Then Late Invite Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I sent an admin invite but the email never arrives. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the admin invite was created and inspect invite email delivery status/logs for suppression or domain rejection. | pass | - |
| 2 | agent | I am checking whether the invite was created and whether delivery bounced. | flow:admin_invite; symptom:invite_email_not_received | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Check whether the admin invite was created and inspect invite email delivery status/logs for suppression or domain rejection. | pass | - |
| 3 | customer | The recipient checked spam and still does not see the invite email. | flow:admin_invite; symptom:invite_email_not_received; recipient_checked_spam:no_invite_email | invite_created; email_delivery_status | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Inspect invite creation status and email delivery logs for the recipient to determine whether the invite was created, delivered, suppressed, or rejected by domain policy. | needs attention | next_check: suppression |
| 4 | agent | I am checking suppression and recipient-domain policy now. | flow:admin_invite; symptom:invite_email_not_received; recipient_checked_spam:no_invite_email; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | domain_policy_rejection | Coordinate with the recipient domain admin to address DMARC rejection or allowlist the sender, then resend the admin invite and verify delivery. | needs attention | candidate_branches: email_delivery_suppressed |

### Final State

```json
{
  "case_id": "level2_irrelevant_then_late_invite_context",
  "version": 4,
  "facts": [
    "flow:admin_invite",
    "symptom:invite_email_not_received",
    "recipient_checked_spam:no_invite_email",
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
  "next_check": "Coordinate with the recipient domain admin to address DMARC rejection or allowlist the sender, then resend the admin invite and verify delivery.",
  "handoff_notes": [
    "Known: recipient_checked_spam:no_invite_email; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: domain_policy_rejection",
    "Next check: Coordinate with the recipient domain admin to address DMARC rejection or allowlist the sender, then resend the admin invite and verify delivery.",
    "Email delivery context confirms the invite was created, delivery was suppressed, and the recipient domain rejected the message by DMARC policy. This rules out invite_not_created and establishes domain_policy_rejection as the final cause."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Level 2 Late Billing Evidence

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | One of our admins says they cannot log in after yesterday's upgrade. | reported_issue:login; recent_change:upgrade | auth_status; actual_surface | login_failure | Confirm whether authentication actually fails for the admin, capture the exact error/screen after sign-in attempt, and verify whether this is limited to one admin or a broader access/billing surface. | needs attention | next_check: login itself |
| 2 | agent | Is login itself failing, or do they get in and then see the wrong page? | reported_issue:login; recent_change:upgrade | auth_status; actual_surface | login_failure | Wait for customer confirmation on whether authentication fails or whether login succeeds and the issue appears after sign-in, then identify the actual surface shown. | needs attention | next_check: login itself |
| 3 | customer | No login works. The billing page is the problem; it still shows the wrong plan. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status; cache_status | billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Check billing records and app entitlement state for the upgraded account: confirm invoice_plan versus app_entitlement_plan and whether billing_refresh is pending or entitlement_cache is stale. | needs attention | next_check: billing entitlement |
| 4 | agent | I am checking whether the invoice and app entitlement agree after the upgrade. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown | billing_entitlement_status; cache_status | billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Await/check product support evidence comparing invoice_plan and app_entitlement_plan after the upgrade, including whether billing_refresh is pending or entitlement_cache is stale. | needs attention | next_check: billing entitlement |
| 5 | customer | The invoice shows Pro, but the app still behaves like Starter. | reported_issue:login; recent_change:upgrade; auth:works; correction:login_works; surface:billing_plan; symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending | cache_status | billing_entitlement_refresh_pending | Confirm billing_refresh completes and app_entitlement_plan updates from starter to pro. | needs attention | next_check: billing entitlement refresh |

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
  "unknowns": [
    "cache_status"
  ],
  "candidate_branches": [
    "billing_entitlement_refresh_pending"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "missing_workspace_role",
    "scim_sync_delay"
  ],
  "next_check": "Confirm billing_refresh completes and app_entitlement_plan updates from starter to pro.",
  "handoff_notes": [
    "Known: symptom:wrong_plan_shown; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Unknowns: cache_status",
    "Branches: billing_entitlement_refresh_pending",
    "Next check: Confirm billing_refresh completes and app_entitlement_plan updates from starter to pro.",
    "Product support context directly shows invoice_plan:pro, app_entitlement_plan:starter, and billing_refresh:pending after upgrade. This provides mechanism evidence for billing_entitlement_refresh_pending."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Level 2 Unresolved Workspace Handoff

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment; cache_status | login_failure; missing_workspace_role; missing_workspace_role_inheritance; scim_sync_delay; stale_entitlement_cache | Verify whether the affected users can authenticate successfully and whether their workspace role/group assignment is present after migration. | needs attention | next_check: sign in |
| 2 | agent | Can they sign in at all, or is login blocked? | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment; cache_status | login_failure; missing_workspace_role; missing_workspace_role_inheritance; scim_sync_delay; stale_entitlement_cache | Confirm auth_status: whether affected users can sign in successfully or login is blocked. | pass | - |
| 3 | customer | They can sign in, but the workspace still will not open. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Check cache_status or escalate for entitlement/cache inspection because auth works, workspace_role:present, and scim_sync:complete, but workspace access still fails. | pass | - |
| 4 | agent | I checked role assignment and SCIM. I am going to hand this to product support with the remaining cache check. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete | cache_status | stale_entitlement_cache | Handoff to product support for entitlement/cache inspection; remaining unresolved check is cache_status because auth:works, workspace_role:present, and scim_sync:complete are already established. | pass | - |

### Final State

```json
{
  "case_id": "level2_unresolved_workspace_handoff",
  "version": 4,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "surface:workspace_access",
    "symptom:workspace_access_loss",
    "auth:works",
    "workspace_role:present",
    "scim_sync:complete"
  ],
  "unknowns": [
    "cache_status"
  ],
  "candidate_branches": [
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_failure",
    "scim_sync_delay",
    "login_block",
    "missing_workspace_role",
    "missing_workspace_role_inheritance"
  ],
  "next_check": "Handoff to product support for entitlement/cache inspection; remaining unresolved check is cache_status because auth:works, workspace_role:present, and scim_sync:complete are already established.",
  "handoff_notes": [
    "Known: symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete",
    "Unknowns: cache_status",
    "Branches: stale_entitlement_cache",
    "Next check: Handoff to product support for entitlement/cache inspection; remaining unresolved check is cache_status because auth:works, workspace_role:present, and scim_sync:complete are already established.",
    "Agent confirmed role assignment and SCIM were checked. Known: affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete. Ruled out: login_failure, login_block, scim_sync_delay, missing_workspace_role, missing_workspace_role_inheritance. Remaining candidate: stale_entitlement_cache. Unknown: cache_status. No direct product/support mechanism evidence yet for final_cause; handoff for cache/entitlement inspection."
  ],
  "final_cause": "",
  "root_cause_evidence_seen": true
}
```

## Stale Cache After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment; cache_status | missing_workspace_role_inheritance; scim_sync_delay; stale_entitlement_cache | Check whether affected users can authenticate, whether their workspace role/group assignment is present after migration, and whether entitlement/cache state matches the assigned role. | needs attention | candidate_branches: missing_workspace_role; next_check: sign in |
| 2 | agent | Can they sign in, or is login blocked? | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss | auth_status; workspace_role_assignment; cache_status | missing_workspace_role_inheritance; scim_sync_delay; stale_entitlement_cache | Confirm whether affected users can authenticate or whether login is blocked. | needs attention | candidate_branches: missing_workspace_role; next_check: sign in |
| 3 | customer | They can sign in, but the workspace still says they do not have access. | affected_scope:three_users; recent_change:migration; surface:workspace_access; symptom:workspace_access_loss; auth:works; workspace_role:present; scim_sync:complete; entitlement_cache:stale |  | stale_entitlement_cache | Refresh or invalidate entitlement cache for the affected users, then retest workspace access. | needs attention | ruled_out_branches: login_block |

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
    "workspace_role:present",
    "scim_sync:complete",
    "entitlement_cache:stale"
  ],
  "unknowns": [],
  "candidate_branches": [
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_failure",
    "scim_sync_delay",
    "missing_workspace_role"
  ],
  "next_check": "Refresh or invalidate entitlement cache for the affected users, then retest workspace access.",
  "handoff_notes": [
    "Known: auth:works; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Branches: stale_entitlement_cache",
    "Next check: Refresh or invalidate entitlement cache for the affected users, then retest workspace access.",
    "Customer confirmed auth:works: users can sign in but workspace denies access. Product/support context directly shows workspace_role:present and scim_sync:complete, ruling out role inheritance and SCIM delay branches. Context also shows entitlement_cache:stale as the access-denial mechanism; final_cause set to stale_entitlement_cache. Next check is cache refresh/invalidation and retest."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

# Support Process Lab Report

Run: `real_model`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| access_after_migration | 17/18 | 94% | yes | missing_workspace_role_inheritance |
| billing_plan_mismatch | 21/24 | 88% | yes | billing_entitlement_refresh_pending |
| corrected_billing_after_access_report | 10/12 | 83% | yes | billing_entitlement_refresh_pending |
| invite_email_not_arriving | 15/18 | 83% | yes | domain_policy_rejection |
| invite_with_irrelevant_billing_context | 17/18 | 94% | yes | domain_policy_rejection |
| stale_cache_after_migration | 16/18 | 89% | yes | stale_entitlement_cache |

## Access After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss | auth_status; billing_entitlement_status; workspace_role_assignment; invite_created; email_delivery_status; actual_surface | missing_workspace_role; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; stale_entitlement_cache; invite_not_created; scim_sync_delay | Confirm whether the three affected users can sign in successfully, and whether the issue is specifically opening the new workspace (surface:workspace_access) vs. login itself — then check workspace role assignments for those users in the migrated workspace. | pass | - |
| 2 | agent | Can they sign in at all, or is login blocked? | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss | auth_status; billing_entitlement_status; workspace_role_assignment; invite_created; email_delivery_status; actual_surface | missing_workspace_role; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; stale_entitlement_cache; invite_not_created; scim_sync_delay | Confirm whether the three affected users can sign in successfully, and whether the issue is specifically opening the new workspace (surface:workspace_access) vs. login itself — then check workspace role assignments for those users in the migrated workspace. | pass | - |
| 3 | customer | They can sign in, but they cannot open the new workspace. | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss; auth:works; surface:workspace_access; group_membership:Migrated-CSM; scim_sync:complete; workspace_role_missing:Migrated-CSM | billing_entitlement_status; invite_created; email_delivery_status | missing_workspace_role; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; stale_entitlement_cache; invite_not_created; scim_sync_delay | Assign a workspace role to the Migrated-CSM group (or directly to the three affected users) in the migrated workspace, then verify access is restored. | needs attention | next_check: inherit |

### Final State

```json
{
  "case_id": "access_after_migration",
  "version": 3,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "symptom:workspace_access_loss",
    "auth:works",
    "surface:workspace_access",
    "group_membership:Migrated-CSM",
    "scim_sync:complete",
    "workspace_role_missing:Migrated-CSM"
  ],
  "unknowns": [
    "billing_entitlement_status",
    "invite_created",
    "email_delivery_status"
  ],
  "candidate_branches": [
    "missing_workspace_role",
    "missing_workspace_role_inheritance",
    "billing_entitlement_refresh_pending",
    "stale_entitlement_cache",
    "invite_not_created",
    "scim_sync_delay"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "scim_sync_delay",
    "invite_not_created",
    "billing_entitlement_refresh_pending",
    "stale_entitlement_cache"
  ],
  "next_check": "Assign a workspace role to the Migrated-CSM group (or directly to the three affected users) in the migrated workspace, then verify access is restored.",
  "handoff_notes": [
    "Known: surface:workspace_access; group_membership:Migrated-CSM; scim_sync:complete; workspace_role_missing:Migrated-CSM",
    "Unknowns: billing_entitlement_status; invite_created; email_delivery_status",
    "Branches: missing_workspace_role; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; stale_entitlement_cache",
    "Next check: Assign a workspace role to the Migrated-CSM group (or directly to the three affected users) in the migrated workspace, then verify access is restored.",
    "Admin context confirms: affected users belong to group Migrated-CSM, SCIM sync is complete, and Migrated-CSM has no workspace role assigned in the migrated workspace. Auth works; surface is workspace_access. Root cause is missing_workspace_role_inheritance \u2014 the SCIM-synced group was not granted a workspace role during migration. Fix: assign the appropriate workspace role to Migrated-CSM (or directly to the three users) in the migrated workspace."
  ],
  "final_cause": "missing_workspace_role_inheritance",
  "root_cause_evidence_seen": true
}
```

## Billing Plan Mismatch

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I cannot log in. | reported_issue:login | actual_surface; auth_status | login_failure | Confirm whether the customer cannot authenticate at all or is experiencing a post-login surface issue; ask them to describe exactly what happens when they attempt to log in. | needs attention | next_check: page |
| 2 | customer | No, login works. The billing page shows the wrong plan. | correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Ask when the upgrade was performed and whether the billing page has ever reflected the correct plan since the upgrade; also confirm what plan is shown versus what was purchased. | needs attention | next_check: entitlement, refresh |
| 3 | agent | When did the plan change? | correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade | billing_entitlement_status | billing_entitlement_refresh_pending; invoice_app_mismatch; stale_entitlement_cache | Await customer response on upgrade timing and whether the correct plan was ever displayed since the upgrade; also confirm what plan is shown versus what was purchased. | needs attention | next_check: entitlement, refresh |
| 4 | customer | We upgraded yesterday. | correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending |  | billing_entitlement_refresh_pending | Confirm billing_refresh:pending resolves by triggering or awaiting entitlement sync; verify app_entitlement_plan updates to pro after refresh completes. | pass | - |

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
  "unknowns": [],
  "candidate_branches": [
    "billing_entitlement_refresh_pending"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "stale_entitlement_cache",
    "invoice_app_mismatch"
  ],
  "next_check": "Confirm billing_refresh:pending resolves by triggering or awaiting entitlement sync; verify app_entitlement_plan updates to pro after refresh completes.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Branches: billing_entitlement_refresh_pending",
    "Next check: Confirm billing_refresh:pending resolves by triggering or awaiting entitlement sync; verify app_entitlement_plan updates to pro after refresh completes.",
    "Product/support context directly confirms: invoice_plan:pro, app_entitlement_plan:starter, billing_refresh:pending. This is a direct mechanism match for billing_entitlement_refresh_pending. Upgrade occurred yesterday; entitlement has not yet propagated to the app. stale_entitlement_cache and invoice_app_mismatch ruled out as the mismatch is explained by a pending refresh, not a cache staleness or invoice discrepancy. Next step: trigger or await entitlement refresh and confirm app plan updates to Pro."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Corrected Billing After Access Report

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after migration. | affected_scope:three_users; recent_change:migration; reported_issue:login; symptom:workspace_access_loss | actual_surface; auth_status; billing_entitlement_status; email_delivery_status; invite_created; workspace_role_assignment | login_failure; missing_workspace_role; missing_workspace_role_inheritance; scim_sync_delay; billing_entitlement_refresh_pending; stale_entitlement_cache; invite_not_created; domain_policy_rejection; email_delivery_suppressed | Clarify what 'lost access' means for the three users: are they unable to log in, blocked from a specific workspace, or seeing a degraded feature set? Confirm whether any error messages are shown and whether the issue appeared immediately after migration. | needs attention | next_check: sign in |
| 2 | customer | Actually, correction: login works and the workspace opens. The billing page is showing the wrong plan after we upgraded. | affected_scope:three_users; recent_change:migration; correction:login_works; auth:works; surface:billing_plan; symptom:wrong_plan_shown; recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending | email_delivery_status; invite_created; workspace_role_assignment | billing_entitlement_refresh_pending; stale_entitlement_cache; invoice_app_mismatch | Confirm whether the billing refresh job has completed or is still pending; check if forcing an entitlement sync resolves the plan mismatch between invoice_plan:pro and app_entitlement_plan:starter. | needs attention | ruled_out_branches: missing_workspace_role |

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
  "unknowns": [
    "email_delivery_status",
    "invite_created",
    "workspace_role_assignment"
  ],
  "candidate_branches": [
    "billing_entitlement_refresh_pending",
    "stale_entitlement_cache",
    "invoice_app_mismatch"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "scim_sync_delay",
    "invite_not_created"
  ],
  "next_check": "Confirm whether the billing refresh job has completed or is still pending; check if forcing an entitlement sync resolves the plan mismatch between invoice_plan:pro and app_entitlement_plan:starter.",
  "handoff_notes": [
    "Known: recent_change:upgrade; invoice_plan:pro; app_entitlement_plan:starter; billing_refresh:pending",
    "Unknowns: email_delivery_status; invite_created; workspace_role_assignment",
    "Branches: billing_entitlement_refresh_pending; stale_entitlement_cache; invoice_app_mismatch",
    "Next check: Confirm whether the billing refresh job has completed or is still pending; check if forcing an entitlement sync resolves the plan mismatch between invoice_plan:pro and app_entitlement_plan:starter.",
    "Customer corrected initial report: login and workspace access are functional. Real issue is billing plan display mismatch post-upgrade. Product/support context confirms invoice shows Pro but app entitlement still reflects Starter with a pending refresh. Ruled out: login_failure, login_block, scim_sync_delay, invite_not_created. Active candidates: billing_entitlement_refresh_pending, stale_entitlement_cache, invoice_app_mismatch. Direct mechanism evidence (billing_refresh:pending + plan mismatch) supports final_cause: billing_entitlement_refresh_pending. Next step: trigger or confirm completion of entitlement refresh job."
  ],
  "final_cause": "billing_entitlement_refresh_pending",
  "root_cause_evidence_seen": true
}
```

## Invite Email Not Arriving

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Um, yeah, so I am trying to invite a new admin. | flow:admin_invite | email_delivery_status; invite_created | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Ask whether the invite was sent successfully from the admin's perspective (e.g., did the UI confirm the invite was sent?) and confirm the recipient email address used. | needs attention | next_check: delivery |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite | email_delivery_status; invite_created | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Await customer response confirming whether the invite shows as created in the admin page. | needs attention | next_check: delivery |
| 3 | customer | Yes, but the invite email never arrives. | flow:admin_invite; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject; symptom:invite_email_not_received |  | email_delivery_suppressed; domain_policy_rejection | Confirm domain DMARC policy configuration and whether the sending domain is aligned; advise customer to check domain DNS DMARC record and coordinate with their email admin to allow or whitelist the sending domain. | needs attention | next_check: suppression |

### Final State

```json
{
  "case_id": "invite_email_not_arriving",
  "version": 3,
  "facts": [
    "flow:admin_invite",
    "invite_status:created",
    "email_delivery:suppressed",
    "domain_policy:dmarc_reject",
    "symptom:invite_email_not_received"
  ],
  "unknowns": [],
  "candidate_branches": [
    "email_delivery_suppressed",
    "domain_policy_rejection"
  ],
  "ruled_out_branches": [
    "invite_not_created"
  ],
  "next_check": "Confirm domain DMARC policy configuration and whether the sending domain is aligned; advise customer to check domain DNS DMARC record and coordinate with their email admin to allow or whitelist the sending domain.",
  "handoff_notes": [
    "Known: invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject; symptom:invite_email_not_received",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Confirm domain DMARC policy configuration and whether the sending domain is aligned; advise customer to check domain DNS DMARC record and coordinate with their email admin to allow or whitelist the sending domain.",
    "Known: flow:admin_invite, invite_status:created, email_delivery:suppressed, domain_policy:dmarc_reject, symptom:invite_email_not_received. Unknowns resolved: invite_created, email_delivery_status. Ruled out: invite_not_created. Root cause confirmed via product/support context: domain_policy_rejection (DMARC reject policy suppressed delivery). Next: customer's email admin should review DMARC policy and allow the sending domain."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Invite With Irrelevant Billing Context

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | I am trying to invite a new admin, but the invite email never arrives. | flow:admin_invite; symptom:invite_email_not_received | email_delivery_status; invite_created | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Confirm whether the invite record was created in the system (check invite_status) and verify email_delivery_status for the recipient address. | pass | - |
| 2 | agent | Does the invite show as created in the admin page? | flow:admin_invite; symptom:invite_email_not_received | email_delivery_status; invite_created | invite_not_created; email_delivery_suppressed; domain_policy_rejection | Await agent response confirming whether the invite record appears as created in the admin page, then check email_delivery_status for the recipient address. | pass | - |
| 3 | customer | Yes, the invite exists in the admin page, but no email arrives. | flow:admin_invite; symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject |  | email_delivery_suppressed; domain_policy_rejection | Confirm domain_policy:dmarc_reject as the delivery block mechanism with the recipient domain's DNS DMARC record, then advise remediation path for email_delivery:suppressed. | needs attention | next_check: suppression |

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
  "next_check": "Confirm domain_policy:dmarc_reject as the delivery block mechanism with the recipient domain's DNS DMARC record, then advise remediation path for email_delivery:suppressed.",
  "handoff_notes": [
    "Known: symptom:invite_email_not_received; invite_status:created; email_delivery:suppressed; domain_policy:dmarc_reject",
    "Branches: email_delivery_suppressed; domain_policy_rejection",
    "Next check: Confirm domain_policy:dmarc_reject as the delivery block mechanism with the recipient domain's DNS DMARC record, then advise remediation path for email_delivery:suppressed.",
    "Product/support context directly confirms: invite_status:created, email_delivery:suppressed, domain_policy:dmarc_reject. invite_not_created is ruled out. Final cause set to domain_policy_rejection based on mechanism evidence in context, not transcript inference. Billing context (invoice_plan:pro, app_entitlement_plan:starter, billing_refresh:pending) remains excluded as unrelated to this case."
  ],
  "final_cause": "domain_policy_rejection",
  "root_cause_evidence_seen": true
}
```

## Stale Cache After Migration

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Three users lost access after our migration yesterday. | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss | actual_surface; auth_status; billing_entitlement_status; workspace_role_assignment | missing_workspace_role; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; stale_entitlement_cache; scim_sync_delay | Confirm which surface users cannot access and whether login/auth itself succeeds or fails, to distinguish auth-layer issues from entitlement/role issues. | needs attention | next_check: sign in |
| 2 | agent | Can they sign in, or is login blocked? | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss | actual_surface; auth_status; billing_entitlement_status; workspace_role_assignment | missing_workspace_role; missing_workspace_role_inheritance; billing_entitlement_refresh_pending; stale_entitlement_cache; scim_sync_delay | Await customer response confirming whether login/auth succeeds or fails for the affected users, to determine if auth_status can be resolved and whether login_block or login_failure branches apply. | needs attention | next_check: sign in |
| 3 | customer | They can sign in, but the workspace still says they do not have access. | affected_scope:three_users; recent_change:migration; symptom:workspace_access_loss; auth:works; surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale | billing_entitlement_status | billing_entitlement_refresh_pending; stale_entitlement_cache | Confirm entitlement cache flush or forced refresh has been performed for the affected users to resolve stale_entitlement_cache as the direct mechanism. | pass | - |

### Final State

```json
{
  "case_id": "stale_cache_after_migration",
  "version": 3,
  "facts": [
    "affected_scope:three_users",
    "recent_change:migration",
    "symptom:workspace_access_loss",
    "auth:works",
    "surface:workspace_access",
    "workspace_role:present",
    "scim_sync:complete",
    "entitlement_cache:stale"
  ],
  "unknowns": [
    "billing_entitlement_status"
  ],
  "candidate_branches": [
    "billing_entitlement_refresh_pending",
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "login_failure",
    "login_block",
    "missing_workspace_role",
    "missing_workspace_role_inheritance",
    "scim_sync_delay"
  ],
  "next_check": "Confirm entitlement cache flush or forced refresh has been performed for the affected users to resolve stale_entitlement_cache as the direct mechanism.",
  "handoff_notes": [
    "Known: surface:workspace_access; workspace_role:present; scim_sync:complete; entitlement_cache:stale",
    "Unknowns: billing_entitlement_status",
    "Branches: billing_entitlement_refresh_pending; stale_entitlement_cache",
    "Next check: Confirm entitlement cache flush or forced refresh has been performed for the affected users to resolve stale_entitlement_cache as the direct mechanism.",
    "Product/admin context confirms workspace_role:present and scim_sync:complete, ruling out role and SCIM branches. entitlement_cache:stale is directly evidenced as the mechanism causing workspace_access_loss despite successful auth. final_cause set to stale_entitlement_cache. Next action: perform cache flush/forced refresh for the three affected users."
  ],
  "final_cause": "stale_entitlement_cache",
  "root_cause_evidence_seen": true
}
```

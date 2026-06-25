# Support Process Lab Report

Run: `gpt55_level3_closeout`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| level3_misrouted_ratelimit_actually_webhook_auth | 43/54 | 80% | yes | webhook_auth_rotation |
| level3_conflicting_systems_unresolved_handoff | 40/48 | 83% | yes |  |

## Level 3 Misrouted Rate Limit Actually Webhook Auth

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Our API calls are getting rate-limited after we scaled traffic this week. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors | quota_status; traffic_scope | quota_exhaustion; upstream_service_incident | Ask the customer for example rate-limit error responses, timestamps, affected endpoints, request IDs, and current request volume so quota_status and traffic_scope can be checked. | needs attention | unknowns: webhook_auth_status; candidate_branches: webhook_auth_rotation; next_check (wording_miss): every API route |
| 2 | agent | Is every API route failing, or only one integration path? | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors | quota_status; traffic_scope | quota_exhaustion; upstream_service_incident | Wait for the customer to answer whether every API route is failing or only one integration path, then use their response to update traffic_scope. | needs attention | unknowns: webhook_auth_status; candidate_branches: webhook_auth_rotation |
| 3 | customer | It is not every route. A subset of webhook callbacks fails, but normal API reads still work. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work | quota_status; webhook_auth_status | quota_exhaustion; upstream_service_incident; webhook_auth_rotation | Check the failed webhook callback delivery logs for the exact response/error and whether signature/auth validation is failing on the affected callbacks. | needs attention | next_check (wording_miss): quota |
| 4 | agent | I am checking quota usage and webhook authentication for that service. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work; quota:under_limit | webhook_auth_status | upstream_service_incident; webhook_auth_rotation | Check webhook_auth_status in the failed webhook callback delivery logs, including whether signature validation is failing on the affected subset. | needs attention | next_check (wording_miss): webhook auth |
| 5 | customer | The failures started right after the partner service rolled a new deployment. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy | webhook_auth_status | upstream_service_incident; webhook_auth_rotation | Ask the customer whether the partner deployment changed webhook signature validation or signing-secret configuration, and check failed webhook callback logs for webhook_auth_status on the affected subset. | needs attention | next_check (wording_miss): webhook auth |
| 6 | agent | Do successful and failed callbacks use the same signing secret? | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy | webhook_auth_status | upstream_service_incident; webhook_auth_rotation | Wait for the customer's answer on whether successful and failed callbacks use the same signing secret, and check failed webhook callback logs for webhook_auth_status on the affected subset. | needs attention | next_check (wording_miss): webhook auth |
| 7 | customer | Only the legacy worker fails. The new worker callbacks succeed. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed | webhook_auth_status | upstream_service_incident; webhook_auth_rotation | Check failed webhook callback logs for the legacy worker and compare its configured signing secret against the new worker's signing secret. | needs attention | next_check (wording_miss): webhook auth |
| 8 | agent | I am comparing webhook signing-secret rotation and quota counters now. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed | webhook_auth_status | upstream_service_incident; webhook_auth_rotation | Review the failed webhook callback logs and signing-secret comparison results for the legacy worker versus the new worker. | needs attention | next_check (wording_miss): webhook auth |
| 9 | customer | That matches what our service owner suspected: the legacy worker still has old webhook auth config. | recent_change:traffic_scale; surface:api_delivery; symptom:rate_limit_errors; surface:webhook_callbacks; traffic_scope:subset; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed; webhook_signing_secret:rotated; webhook_auth:legacy_secret |  | webhook_auth_rotation | Have the implementation owner update the legacy worker to validate against the current webhook signing secret, then replay or verify the failed callback deliveries. | pass | - |

### Final State

```json
{
  "case_id": "level3_misrouted_ratelimit_actually_webhook_auth",
  "version": 9,
  "facts": [
    "recent_change:traffic_scale",
    "surface:api_delivery",
    "symptom:rate_limit_errors",
    "surface:webhook_callbacks",
    "traffic_scope:subset",
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
  "next_check": "Have the implementation owner update the legacy worker to validate against the current webhook signing secret, then replay or verify the failed callback deliveries.",
  "handoff_notes": [
    "Known: failure_scope:legacy_worker; new_worker:callbacks_succeed; webhook_signing_secret:rotated; webhook_auth:legacy_secret",
    "Branches: webhook_auth_rotation",
    "Next check: Have the implementation owner update the legacy worker to validate against the current webhook signing secret, then replay or verify the failed callback deliveries.",
    "Direct mechanism evidence is now available: webhook_signing_secret:rotated and webhook_auth:legacy_secret. Customer confirms the legacy worker still has old webhook auth config. Final cause is webhook_auth_rotation; next step is to update the legacy worker config and verify/replay failed callbacks."
  ],
  "final_cause": "webhook_auth_rotation",
  "root_cause_evidence_seen": true
}
```

## Level 3 Conflicting Systems Unresolved Handoff

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Our enterprise workspace still says we are not entitled even though the renewal completed. | renewal:completed; surface:entitlement_access; symptom:entitlement_block | billing_entitlement_status; provisioning_status; entitlement_cache_status; payment_status; affected_scope | billing_entitlement_refresh_pending; billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache; payment_failure | Check the billing/renewal record for this workspace and confirm whether the entitlement service currently shows an active entitlement or a provisioning/not-ready state. | needs attention | next_check (wording_miss): all users |
| 2 | agent | Do all users see the entitlement block, or only a few seats? | renewal:completed; surface:entitlement_access; symptom:entitlement_block | billing_entitlement_status; provisioning_status; entitlement_cache_status; payment_status; affected_scope | billing_entitlement_refresh_pending; billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache; payment_failure | Wait for the customer to confirm affected_scope: whether all workspace users see the entitlement block or only a few seats. | needs attention | facts: affected_scope:all_workspace_users; next_check (wording_miss): billing, provisioning |
| 3 | customer | All users in the workspace see the entitlement block. | renewal:completed; surface:entitlement_access; symptom:entitlement_block; affected_scope:all_workspace_users | billing_entitlement_status; provisioning_status; entitlement_cache_status; payment_status | billing_entitlement_refresh_pending; billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache; payment_failure | Check internal billing entitlement status and provisioning_status for the workspace to see whether billing shows entitlement while provisioning is not ready or mismatched. | pass | - |
| 4 | agent | I am checking billing entitlement and provisioning state side by side. | renewal:completed; surface:entitlement_access; symptom:entitlement_block; affected_scope:all_workspace_users; billing:entitled; payment:clear; provisioning:not_ready | entitlement_cache_status; provisioning_job_status | provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache | Check the provisioning job/status details for why the workspace is not ready despite billing:entitled and payment:clear. | needs attention | next_check (wording_miss): entitlement cache |
| 5 | customer | Billing sent us a receipt and the admin page says the renewal is active. | renewal:completed; surface:entitlement_access; symptom:entitlement_block; affected_scope:all_workspace_users; billing:entitled; payment:clear; provisioning:not_ready; renewal:active | entitlement_cache_status; provisioning_job_status | provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache | Check the provisioning job/status details for why the workspace is not ready despite billing:entitled, payment:clear, and renewal:active. | needs attention | next_check (wording_miss): entitlement cache |
| 6 | agent | Provisioning still disagrees, so I need the job status before I call a root cause. | renewal:completed; surface:entitlement_access; symptom:entitlement_block; affected_scope:all_workspace_users; billing:entitled; payment:clear; provisioning:not_ready; renewal:active | entitlement_cache_status; provisioning_job_status | provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache | Check the provisioning_job_status details for why provisioning still disagrees despite billing:entitled, payment:clear, and renewal:active. | needs attention | next_check (wording_miss): provisioning job, entitlement cache |
| 7 | customer | We need an update for our implementation owner today. | renewal:completed; surface:entitlement_access; symptom:entitlement_block; affected_scope:all_workspace_users; billing:entitled; payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update | entitlement_cache_status; provisioning_job_status | provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache | Prepare a same-day implementation-owner update noting billing:entitled, payment:clear, renewal:active, provisioning:not_ready, and that entitlement_cache_status and provisioning_job_status are still being checked. | needs attention | next_check (wording_miss): provisioning job, entitlement cache |
| 8 | agent | I am handing this to product support with billing entitled, provisioning blocked, and the job status still open. | renewal:completed; surface:entitlement_access; symptom:entitlement_block; affected_scope:all_workspace_users; billing:entitled; payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update | entitlement_cache_status; provisioning_job_status | provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache | Ask product support to check provisioning_job_status and entitlement_cache_status for the entitled account where provisioning:not_ready is blocking entitlement access. | needs attention | next_check (wording_miss): provisioning job, entitlement cache |

### Final State

```json
{
  "case_id": "level3_conflicting_systems_unresolved_handoff",
  "version": 8,
  "facts": [
    "renewal:completed",
    "surface:entitlement_access",
    "symptom:entitlement_block",
    "affected_scope:all_workspace_users",
    "billing:entitled",
    "payment:clear",
    "provisioning:not_ready",
    "renewal:active",
    "handoff_need:implementation_owner_update"
  ],
  "unknowns": [
    "entitlement_cache_status",
    "provisioning_job_status"
  ],
  "candidate_branches": [
    "provisioning_state_mismatch",
    "entitlement_cache_delay",
    "stale_entitlement_cache"
  ],
  "ruled_out_branches": [
    "billing_entitlement_gap",
    "payment_failure"
  ],
  "next_check": "Ask product support to check provisioning_job_status and entitlement_cache_status for the entitled account where provisioning:not_ready is blocking entitlement access.",
  "handoff_notes": [
    "Known: payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update",
    "Unknowns: entitlement_cache_status; provisioning_job_status",
    "Branches: provisioning_state_mismatch; entitlement_cache_delay; stale_entitlement_cache",
    "Next check: Ask product support to check provisioning_job_status and entitlement_cache_status for the entitled account where provisioning:not_ready is blocking entitlement access.",
    "Agent has handed the case to product support with billing:entitled, payment:clear, renewal:active, provisioning:not_ready, and provisioning_job_status still open. Keep entitlement_cache_status and provisioning_job_status open; candidate branches remain provisioning_state_mismatch, entitlement_cache_delay, and stale_entitlement_cache."
  ],
  "final_cause": "",
  "root_cause_evidence_seen": true
}
```

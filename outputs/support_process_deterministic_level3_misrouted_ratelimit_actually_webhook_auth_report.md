# Support Process Lab Report

Run: `deterministic_level3_misrouted_ratelimit_actually_webhook_auth`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| level3_misrouted_ratelimit_actually_webhook_auth | 54/54 | 100% | yes | webhook_auth_rotation |

## Level 3 Misrouted Rate Limit Actually Webhook Auth

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Our API calls are getting rate-limited after we scaled traffic this week. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale | traffic_scope; quota_status; webhook_auth_status | quota_exhaustion; webhook_auth_rotation | Confirm whether every API route is failing or only one integration path. | pass | - |
| 2 | agent | Is every API route failing, or only one integration path? | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale | traffic_scope; quota_status; webhook_auth_status | quota_exhaustion; webhook_auth_rotation | Confirm whether every API route is failing or only one integration path. | pass | - |
| 3 | customer | It is not every route. A subset of webhook callbacks fails, but normal API reads still work. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work | quota_status; webhook_auth_status | quota_exhaustion; webhook_auth_rotation | Compare quota counters with webhook auth status for the failing callback path. | pass | - |
| 4 | agent | I am checking quota usage and webhook authentication for that service. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit | webhook_auth_status | webhook_auth_rotation | Compare webhook auth status for the failing service before naming a final cause. | pass | - |
| 5 | customer | The failures started right after the partner service rolled a new deployment. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy | webhook_auth_status | webhook_auth_rotation | Compare webhook auth status for the failing service before naming a final cause. | pass | - |
| 6 | agent | Do successful and failed callbacks use the same signing secret? | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy | webhook_auth_status | webhook_auth_rotation | Compare webhook auth status for the failing service before naming a final cause. | pass | - |
| 7 | customer | Only the legacy worker fails. The new worker callbacks succeed. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed | webhook_auth_status | webhook_auth_rotation | Compare webhook auth status for the legacy worker before naming a final cause. | pass | - |
| 8 | agent | I am comparing webhook signing-secret rotation and quota counters now. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed | webhook_auth_status | webhook_auth_rotation | Compare webhook auth status for the legacy worker before naming a final cause. | pass | - |
| 9 | customer | That matches what our service owner suspected: the legacy worker still has old webhook auth config. | surface:api_delivery; symptom:rate_limit_errors; recent_change:traffic_scale; traffic_scope:subset; surface:webhook_callbacks; normal_api_reads:work; quota:under_limit; recent_change:partner_deploy; failure_scope:legacy_worker; new_worker:callbacks_succeed; webhook_signing_secret:rotated; webhook_auth:legacy_secret |  | webhook_auth_rotation | Update the legacy worker signing secret and replay one failed webhook callback. | pass | - |

### Final State

```json
{
  "case_id": "level3_misrouted_ratelimit_actually_webhook_auth",
  "version": 11,
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

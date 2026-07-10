# Support Process Lab Report

Run: `deterministic_level2_unresolved_workspace_handoff`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| level2_unresolved_workspace_handoff | 24/24 | 100% | yes |  |

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

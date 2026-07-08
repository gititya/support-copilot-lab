# Support Process Lab Report

Run: `deterministic_level3_conflicting_systems_unresolved_handoff`

Offline test of transcript + mock-system support process state.

## Summary

| case | checks | pass_rate | final_cause_ok | final_cause |
| --- | --- | --- | --- | --- |
| level3_conflicting_systems_unresolved_handoff | 48/48 | 100% | yes |  |

## Level 3 Conflicting Systems Unresolved Handoff

| turn | speaker | text | facts | unknowns | branches | next_check | status | missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | customer | Our enterprise workspace still says we are not entitled even though the renewal completed. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed | affected_scope; billing_entitlement_status; provisioning_status | billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay | Confirm whether all users see the entitlement block or only a few seats. | pass | - |
| 2 | agent | Do all users see the entitlement block, or only a few seats? | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users | billing_entitlement_status; provisioning_status | billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay | Check billing entitlement and provisioning state side by side. | pass | - |
| 3 | customer | All users in the workspace see the entitlement block. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users | billing_entitlement_status; provisioning_status | billing_entitlement_gap; provisioning_state_mismatch; entitlement_cache_delay | Check billing entitlement and provisioning state side by side. | pass | - |
| 4 | agent | I am checking billing entitlement and provisioning state side by side. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready | provisioning_status; provisioning_job_status; entitlement_cache_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch | Escalate with provisioning job status and entitlement cache status still open. | pass | - |
| 5 | customer | Billing sent us a receipt and the admin page says the renewal is active. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active | provisioning_status; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch | Escalate with provisioning job status and entitlement cache status still open. | pass | - |
| 6 | agent | Provisioning still disagrees, so I need the job status before I call a root cause. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active | provisioning_status; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch | Escalate with provisioning job status and entitlement cache status still open. | pass | - |
| 7 | customer | We need an update for our implementation owner today. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update | provisioning_status; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch | Escalate with provisioning job status and entitlement cache status still open. | pass | - |
| 8 | agent | I am handing this to product support with billing entitled, provisioning blocked, and the job status still open. | surface:workspace_access; surface:entitlement_access; symptom:entitlement_block; renewal:completed; affected_scope:all_workspace_users; surface:billing_plan; symptom:wrong_plan_shown; billing:entitled; payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update | provisioning_status; provisioning_job_status; entitlement_cache_status; billing_entitlement_status | provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch | Escalate with provisioning job status and entitlement cache status still open. | pass | - |

### Final State

```json
{
  "case_id": "level3_conflicting_systems_unresolved_handoff",
  "version": 9,
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
    "provisioning_job_status",
    "entitlement_cache_status",
    "billing_entitlement_status"
  ],
  "candidate_branches": [
    "provisioning_state_mismatch",
    "entitlement_cache_delay",
    "billing_entitlement_refresh_pending",
    "invoice_app_mismatch"
  ],
  "ruled_out_branches": [
    "payment_failure",
    "billing_entitlement_gap"
  ],
  "next_check": "Escalate with provisioning job status and entitlement cache status still open.",
  "handoff_notes": [
    "Known: payment:clear; provisioning:not_ready; renewal:active; handoff_need:implementation_owner_update",
    "Unknowns: provisioning_status; provisioning_job_status; entitlement_cache_status; billing_entitlement_status",
    "Branches: provisioning_state_mismatch; entitlement_cache_delay; billing_entitlement_refresh_pending; invoice_app_mismatch",
    "Next check: Escalate with provisioning job status and entitlement cache status still open."
  ],
  "final_cause": "",
  "root_cause_evidence_seen": false
}
```

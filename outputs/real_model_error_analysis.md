# Real Model Error Analysis

Generated from the structured verdicts in the real-model snapshot.

| case | turn | field | missing | actual | classification |
| --- | --- | --- | --- | --- | --- |
| access_after_migration | 3 | next_check | inherit | Assign a workspace role to the Migrated-CSM group (or directly to the three affected users) in the migrated workspace, then verify access is restored. | evaluator_strictness |
| billing_plan_mismatch | 1 | next_check | page | Confirm whether the customer cannot authenticate at all or is experiencing a post-login surface issue; ask them to describe exactly what happens when they attempt to log in. | evaluator_strictness |
| billing_plan_mismatch | 2 | next_check | entitlement; refresh | Ask when the upgrade was performed and whether the billing page has ever reflected the correct plan since the upgrade; also confirm what plan is shown versus what was purchased. | evaluator_strictness |
| billing_plan_mismatch | 3 | next_check | entitlement; refresh | Await customer response on upgrade timing and whether the correct plan was ever displayed since the upgrade; also confirm what plan is shown versus what was purchased. | evaluator_strictness |
| corrected_billing_after_access_report | 1 | next_check | sign in | Clarify what 'lost access' means for the three users: are they unable to log in, blocked from a specific workspace, or seeing a degraded feature set? Confirm whether any error messages are shown and whether the issue appeared immediately after migration. | evaluator_strictness |
| corrected_billing_after_access_report | 2 | ruled_out_branches | missing_workspace_role | ['invite_not_created', 'login_block', 'login_failure', 'scim_sync_delay'] | model_miss |
| invite_email_not_arriving | 1 | next_check | delivery | Ask whether the invite was sent successfully from the admin's perspective (e.g., did the UI confirm the invite was sent?) and confirm the recipient email address used. | evaluator_strictness |
| invite_email_not_arriving | 2 | next_check | delivery | Await customer response confirming whether the invite shows as created in the admin page. | evaluator_strictness |
| invite_email_not_arriving | 3 | next_check | suppression | Confirm domain DMARC policy configuration and whether the sending domain is aligned; advise customer to check domain DNS DMARC record and coordinate with their email admin to allow or whitelist the sending domain. | evaluator_strictness |
| invite_with_irrelevant_billing_context | 3 | next_check | suppression | Confirm domain_policy:dmarc_reject as the delivery block mechanism with the recipient domain's DNS DMARC record, then advise remediation path for email_delivery:suppressed. | evaluator_strictness |
| stale_cache_after_migration | 1 | next_check | sign in | Confirm which surface users cannot access and whether login/auth itself succeeds or fails, to distinguish auth-layer issues from entitlement/role issues. | evaluator_strictness |
| stale_cache_after_migration | 2 | next_check | sign in | Await customer response confirming whether login/auth succeeds or fails for the affected users, to determine if auth_status can be resolved and whether login_block or login_failure branches apply. | evaluator_strictness |


## Classification Notes

- `evaluator_strictness` means the model gave a non-empty next check but missed the exact expected substring.
- `model_miss` means a required structured state field or final-cause timing check failed.

# Copilot investigation and timing trial — 10 September 2026

This report reads frozen synthetic trial artifacts. It is not a rep outcome study or a live helpdesk integration.

## Investigation comparison

The investigation version carries compact previous state, current observed facts and the latest observation. The baseline sees the full observed history and current facts. Both use the same model, source/question menus and basic support rules. Product data arrives only after a requested read; host-supplied source revisions invalidate older records.

| Approach | Cases | All checks pass (stages) | Supported expected outcome (stages) | Model calls | Provider errors | Questions requested | Answers adding no fact | Median model wait per update | Usage cost estimate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| investigation | 6 | 9/15 | 13/15 | 47 | 0 | 6 | 2 | 14.95s | $0.028531 |
| baseline | 6 | 6/15 | 10/15 | 37 | 0 | 4 | 1 | 11.74s | $0.021372 |

An all-check pass requires supported structured facts, an evidence-backed cause, the authored outcome, retained required facts and no recorded request errors. Supported expected outcome is narrower: it does not imply good wording, efficient investigation or customer recovery. A simulated answer adding no fact is a warning, not proof that the question was unreasonable.

The model is `gpt-5.6-luna`, low reasoning, direct OpenAI. Provider wait includes multiple calls within an update and failed-request wait where recorded. Sources are in-memory fixtures; these are not customer response-time benchmarks. Runs for the two families and timing experiment overlapped, so provider contention may affect latency. Costs are estimates from returned token usage and recorded prices, not invoices.

## Case-level results

| Case | Family | Approach | Passed stages | Final investigation action | Cause | Recorded errors |
| --- | --- | --- | --- | --- | --- | --- |
| C03 | access | investigation | 1/3 | resolve | {'code': 'access_cache_stale', 'evidence': ['access_cache_state']} | none |
| C03 | access | baseline | 0/3 | read | None | missing_cause_field, missing_rep_message, unsupported_action, unsupported_fact |
| C04 | access | baseline | 1/3 | wait | None | none |
| C04 | access | investigation | 1/3 | wait | None | none |
| C05 | access | investigation | 2/2 | resolve | {'code': 'missing_permission', 'evidence': ['permission_change', 'access_denied']} | none |
| C05 | access | baseline | 2/2 | resolve | {'code': 'missing_permission', 'evidence': ['permission_change', 'access_denied']} | none |
| C06 | integration | investigation | 1/2 | resolve | {'code': 'usage_limit', 'evidence': ['rejected_request', 'limit_status', 'usage_state']} | none |
| C06 | integration | baseline | 1/2 | resolve | {'code': 'usage_limit', 'evidence': ['rejected_request', 'limit_status', 'usage_state']} | none |
| C07 | integration | baseline | 1/3 | wait | None | none |
| C07 | integration | investigation | 3/3 | handoff | None | none |
| C08 | integration | investigation | 1/2 | resolve | {'code': 'credential_mismatch', 'evidence': ['auth_error', 'credential_match', 'credential_version']} | none |
| C08 | integration | baseline | 1/2 | resolve | {'code': 'credential_mismatch', 'evidence': ['auth_error', 'credential_match', 'credential_version']} | none |

## Timing: redundant request overhead

Two development cases were replayed with one unfinished fragment before each committed update and one exact repeat afterwards. The eager version called the model on these extras; the gated version held fragments and suppressed repeats. Extra calls were advice-only: their proposed reads were not executed, so this is not a comparison of complete interactive sessions.

| Case | Mode | Committed stages passed | Total calls | Partial calls | Duplicate calls | Duplicate grades failed | All provider calls succeeded | Total provider wait |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | every_update | 2/2 | 10 | 2 | 2 | 1 | True | 44.62s |
| C01 | deduplicate | 2/2 | 6 | 0 | 0 | 0 | True | 25.13s |
| C02 | deduplicate | 2/2 | 7 | 0 | 0 | 0 | True | 29.49s |
| C02 | every_update | 1/2 | 12 | 2 | 2 | 1 | True | 44.97s |

The eager runs made 8 extra fragment/repeat requests, taking 30.34s of accumulated provider wait and an estimated $0.004374. These are directly observed overhead calls, not a promise of that saving on normal customer traffic.

Every committed update still runs. Changed record facts and query scope are not treated as duplicates. The gate withdraws prior advice when a partial correction or new committed update begins. There is no learned semantic trigger, live audio or live streaming UI.

## Limits and provenance

- Six evaluation cases are separate from two development cases. They are author-designed synthetic cases, not independently collected customer cases. The final runner and case hashes were frozen before evaluation; no post-result tuning is included.
- Raw prompts exclude future stages, scenario explanations, descriptive case titles, split and expected answers. The menu still limits the problem to four cause categories and listed questions/records; this does not prove open-ended investigation.
- The evaluator checks structured assertions against observed source values and authored causal evidence. Free-text advice and hypotheses require human review. A valid source citation alone does not guarantee that the prose follows from it.
- A terminal resolve action identifies a diagnosis for the rep. It does not change the product, confirm customer recovery or prove a receiving person read a handoff.
- The two earlier development runs and their inputs are preserved. Their scores use earlier prompts/expectations and must not be pooled with the frozen evaluation.

Sources: [access results](../outputs/cop1/heldout-access-v3.json), [integration results](../outputs/cop1/heldout-integration-v3.json), [timing results](../outputs/cop1/timing-v3.json), [frozen inputs](../outputs/cop1/frozen-inputs-v3.json).

## Saved rep advice for review

### C03 — access — investigation

**Update 1:** The analyst is authenticated, so this is not currently established as a sign-in problem. The cause remains unconfirmed because workspace permission and access-cache state are unknown. Handoff for authorized review of those two areas.

Requested records: identity, workspace_access, access_cache. Questions: none. Missed checks: expected_outcome. Errors: none.

**Update 2:** Both analysts can sign in, have workspace permission, and are blocked from workspace entry. The cause remains uncertain; wait for the access-cache refresh result before advising further.

Requested records: workspace_access, access_cache. Questions: impact. Missed checks: none. Errors: none.

**Update 3:** The migration change has not yet reached the app because the access cache is stale. An authorized administrator should refresh or allow the cache to refresh, then recheck workspace entry; workspace permissions remain unverified.

Requested records: access_cache. Questions: none. Missed checks: required_facts_retained. Errors: none.

### C03 — access — baseline

**Update 1:** No usable response.

Requested records: identity, workspace_access. Questions: none. Missed checks: valid_and_supported_facts, expected_outcome. Errors: missing_cause_field, missing_rep_message, unsupported_action.

**Update 2:** The issue is not explained by sign-in failure or missing workspace permission. A stale access cache is possible after the recent move, but it is unconfirmed because the cache record is unavailable. Handoff with the cache-refresh status and the blocked action still unknown.

Requested records: workspace_access, access_cache. Questions: none. Missed checks: expected_outcome. Errors: none.

**Update 3:** Both analysts can sign in and their workspace permission is present, so missing permission is not currently supported. Read the access-cache state next to determine whether the migration has reached the app; the cache status is still unknown.

Requested records: none. Questions: none. Missed checks: valid_and_supported_facts, expected_outcome, required_facts_retained. Errors: unsupported_fact.

### C04 — access — baseline

**Update 1:** Several workspace members reportedly cannot open the workspace, but sign-in status is still pending and no migration audit record is available. Wait for the identity result before requesting the same sign-in information again or assigning a cause.

Requested records: migration_audit, identity. Questions: none. Missed checks: none. Errors: none.

**Update 2:** The issue remains under investigation: several workspace members reportedly cannot open the workspace, but sign-in status and affected-user scope are not yet confirmed. Wait for the pending identity check and member list before assigning a cause.

Requested records: none. Questions: none. Missed checks: required_facts_retained. Errors: none.

**Update 3:** The issue affects several workspace members, but sign-in status and the cause are still unverified. Please wait for the requested log result before taking the next diagnostic step.

Requested records: none. Questions: none. Missed checks: expected_outcome, required_facts_retained. Errors: none.

### C04 — access — investigation

**Update 1:** The cause is not confirmed. Sign-in status for the affected members is still pending, so wait for that result; workspace permissions and migration access changes remain unknown.

Requested records: migration_audit, identity. Questions: none. Missed checks: none. Errors: none.

**Update 2:** The cause is not confirmed. Wait for the affected-member list and pending sign-in status; workspace permissions and migration access changes remain unknown.

Requested records: none. Questions: none. Missed checks: required_facts_retained. Errors: none.

**Update 3:** The cause is not confirmed. Wait for the requested log to finish collecting; no new result is available yet.

Requested records: identity. Questions: none. Missed checks: expected_outcome, required_facts_retained. Errors: none.

### C05 — access — investigation

**Update 1:** The three affected members are authenticated, so this is less likely to be a sign-in or credential problem. Please ask what specific workspace action is blocked; the cause remains unconfirmed.

Requested records: migration_audit, identity, workspace_access. Questions: impact. Missed checks: none. Errors: none.

**Update 2:** Supported diagnosis: the four members are denied workspace access because the migration permission change was not applied. An authorized administrator should review and apply the required workspace permissions; recovery is not confirmed.

Requested records: workspace_access, migration_audit. Questions: none. Missed checks: none. Errors: none.

### C05 — access — baseline

**Update 1:** The named members are successfully signing in, so this does not currently look like a general credential or login failure. Please ask what specific workspace action is blocked; workspace permissions and migration records could not be read in this update.

Requested records: migration_audit, identity, workspace_access. Questions: impact. Missed checks: none. Errors: none.

**Update 2:** Supported diagnosis: the four members’ workspace permission change was not applied, causing access denial. An authorized administrator should apply or restore the required workspace permissions; customer recovery is not yet confirmed.

Requested records: workspace_access, migration_audit. Questions: none. Missed checks: none. Errors: none.

### C06 — integration — investigation

**Update 1:** The connector has a recorded failed run for one customer account, but the cause is not verified. Please ask when the connector last succeeded; this will help narrow whether the failure is recent or persistent.

Requested records: integration_health, credential, usage_limits. Questions: impact, last_success. Missed checks: none. Errors: none.

**Update 2:** A usage-limit cause is supported: the directory sync request was rejected because the connector allowance is exceeded. An authorized person must address the service limit; customer recovery is not confirmed.

Requested records: usage_limits. Questions: none. Missed checks: required_facts_retained. Errors: none.

### C06 — integration — baseline

**Update 1:** The connector has failed runs for one customer account, but the available credential and usage records are unavailable, so the cause is not established. Ask when it last succeeded.

Requested records: integration_health, credential, usage_limits. Questions: last_success. Missed checks: none. Errors: none.

**Update 2:** Supported diagnosis: the account has exceeded its connector usage allowance, causing the directory sync request to be rejected. An authorized administrator should review the allowance and any reset or increase option; recovery is not confirmed.

Requested records: usage_limits. Questions: none. Missed checks: required_facts_retained. Errors: none.

### C07 — integration — baseline

**Update 1:** The connector health check is still pending, so the cause is not established. Wait for its result before requesting more information or selecting a remediation.

Requested records: integration_health. Questions: none. Missed checks: none. Errors: none.

**Update 2:** The billing connector is reported as failing for some records and billing updates are delayed, but the cause is not established. Wait for the record scope, last successful run, and pending health check before diagnosing further.

Requested records: none. Questions: none. Missed checks: required_facts_retained. Errors: none.

**Update 3:** The reported issue affects a group of customer records and has delayed billing updates, but the cause is not yet established. Wait for the pending connector health check before diagnosing or handing off.

Requested records: none. Questions: none. Missed checks: expected_outcome, required_facts_retained. Errors: none.

### C07 — integration — investigation

**Update 1:** The billing delay is reported but not yet verified as a product failure. The connector health check is still pending, so wait for its result before narrowing the cause.

Requested records: integration_health. Questions: none. Missed checks: none. Errors: none.

**Update 2:** The billing delay is reported but not yet diagnosed. Wait for the affected-record list and last successful run details; the available product reads do not currently support a specific cause.

Requested records: integration_health, credential, usage_limits. Questions: none. Missed checks: none. Errors: none.

**Update 3:** Hand off to a specialist. The billing delay is reported, but no specific cause is supported because the connector run, credential, and usage records are unavailable. The affected records, last successful run, and failed integration action also remain unknown.

Requested records: credential, usage_limits. Questions: none. Missed checks: none. Errors: none.

### C08 — integration — investigation

**Update 1:** The connector is failing for both teams, but the cause is not established. Please determine when it last succeeded so we can distinguish a recent interruption from a persistent failure.

Requested records: integration_health, credential, usage_limits. Questions: impact, last_success. Missed checks: none. Errors: none.

**Update 2:** The supported cause is a credential mismatch: the request signature is rejected, and the credential does not match the current account configuration. An authorized person should update the connector credential, then retry the sync; customer recovery is not yet confirmed.

Requested records: integration_health, credential. Questions: none. Missed checks: required_facts_retained. Errors: none.

### C08 — integration — baseline

**Update 1:** The connector is reported as stale for two teams, and its runs are confirmed failed for both. The cause is not yet established. Please determine when it last succeeded; credential and usage records were unavailable in the current checks.

Requested records: integration_health, credential, usage_limits. Questions: impact, last_success. Missed checks: none. Errors: none.

**Update 2:** Supported diagnosis: the affected team's connector is using a mismatched credential, causing signature rejection. An authorized person should update the connector credential to match the current account configuration, then retry the sync. Recovery is not yet confirmed.

Requested records: integration_health, credential. Questions: none. Missed checks: required_facts_retained. Errors: none.

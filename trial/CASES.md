# COP-1 controlled case fixtures

This fixture set has 8 synthetic cases: 2 development cases and 6 heldout cases. Development contains one access-after-migration case and one integration-failure case. Heldout contains three cases in each family and must remain untouched during tuning.

Each case has fixed source descriptors and fixed question text. Source results and answer results appear only inside a stage after the runner requests them. Every stage starts with a new customer or representative update. A later event can revise a fact; the newest value wins. Reported facts use keys such as `reported_scope` and `reported_login`. Verified facts use keys such as `login_status`, `workspace_permission`, and `credential_version`. Customer or representative answers keep the `reported_*` keys; source reads supply verified observations.

The cause codes are:

- `missing_permission`: the migration did not apply a needed workspace permission.
- `access_cache_stale`: the permission exists, but the app has not refreshed its access cache.
- `credential_mismatch`: the connector credential does not match the current integration configuration, with a scoped rejected-signature observation.
- `usage_limit`: the connector request was rejected because the service allowance was exceeded.

The final endings are deliberately varied. C01 resolves a missing workspace permission. C02 resolves an outdated integration credential with rejected-signature evidence. C03 resolves a stale access cache after a scope correction. C04 hands off because access evidence remains unavailable and includes the required no-change event. C05 resolves a missing permission after a later scope contradiction. C06 resolves a usage limit with a rejected request and exceeded-limit status. C07 hands off because all permitted integration evidence remains unavailable. C08 resolves a credential mismatch after a scope correction.

The JSON uses a top-level list. Each stage allows at most three reads, keeps cause evidence out of early stages, and includes `expected.kinds`, nullable `expected.cause`, `expected.evidence`, required facts, avoided questions, useful reads, and useful questions. Initial stages expose useful non-cause reads, and no stage bans a useful question. Permission causes can use a current reported sign-in fact when the customer report is sufficient; credential causes use scoped authentication evidence and do not require an unrelated health read. Each stage's required facts are available in that stage's current event/read/answer set, so source revisions cannot leave the expectation dependent on stale prior facts. No fixture contains real customer data, credentials, secrets, or paid-model calls.

# Generated Support Fixture Import Contract

This contract is the target shape for `support-call-generator` or any other case generator that wants to feed this repo.

The generator should export support-process fixtures, not just transcripts. The transcript is the visible customer/agent conversation. The context events are timed product/support facts that arrive during the case. Expected state is the answer key for evaluating the Live Support State.

## Supported Envelope

```json
{
  "schema_version": "support_process_fixture.v1",
  "cases": []
}
```

`cases` may contain one or more fixtures with the same shape used by `fixtures/*.json`.

The importer also accepts a single bare fixture object for convenience.
It also accepts one schema-versioned fixture object with `schema_version: support_process_fixture.v1`.

## Required Case Fields

- `case_id`
- `title`
- `scenario`
- `transcript_turns`
- `context_events`
- `expected_by_turn`
- `final_cause`

Optional fields:

- `expected_outcome`: set to `handoff` when no final cause should be named.
- `handoff_summary`: customer-safe summary for unresolved handoff cases.
- `difficulty`: for example `simple`, `hard`, or `harder`.
- `domain`: for example `b2b_saas`.
- `capability_tags`: examples include `late_context`, `irrelevant_context`, `correction`, `handoff`, `conflicting_context`.

## Context Events

Each context event needs:

- `after_turn`: transcript turn after which the context becomes available.
- `description`: human-readable product/support context.
- `facts`: public facts shown to the state updater.

Optional context fields:

- `relevant`: set to `false` for context that must be ignored.
- `unknowns`: new open checks introduced by context.
- `resolved_unknowns`
- `candidate_branches`
- `ruled_out_branches`
- `final_cause`
- `next_check`

## Leakage Rule

Before a relevant context event provides mechanism evidence, the transcript should not reveal the exact final-cause label. Symptoms are allowed. Mechanism labels are not.

For example, early transcript can say:

```text
Three users lost access after migration.
```

It should not say:

```text
This is definitely stale_entitlement_cache.
```

## Import Workflow

Run:

```bash
python3 prototype/import_generated.py path/to/generated_cases.json
```

By default, accepted cases are written to:

```text
outputs/generated_fixture_staging/
```

Do not copy staged cases into `fixtures/` until they are reviewed.

## Generated Review Workflow

Generated fixtures are not source-of-truth fixtures when first imported. Review them separately:

```bash
python3 prototype/generated_review.py
```

This writes:

```text
outputs/generated_support_review.html
```

Use this report to decide whether a generated case should be promoted into `fixtures/`. Promotion is manual and should happen only after the expected state is calibrated to the strict experiment harness.

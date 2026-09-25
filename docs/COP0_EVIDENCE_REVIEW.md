# COP-0 evidence review — 10 September 2026

COP-0 is complete as an evidence and presentation review. This is not a repaired investigation engine or a new model benchmark. The existing code and historical outputs are unchanged.

Reviewed base: `718ead9cd957590a4c4187720fe5f6030424a4a1`. Working tree was clean before these documentation changes. No cloud calls, deployment, publication or live rep trial occurred.

## The readable case

Source: `outputs/support_process_gpt55_benchmark_snapshots.json`, case `access_after_migration`. This is stored GPT-5.5 output, not the process mock. The corresponding [report](../outputs/support_process_gpt55_benchmark_report.md#access-after-migration) makes the same sequence visible.

| Moment | Available at that point in the intended case | Saved behaviour | Assessment |
| --- | --- | --- | --- |
| Turn 1 | Customer: “Three users lost access after our migration yesterday.” No product event. | Raw model patch adds `auth:works`; state has no open sign-in question. Next check moves to workspace roles and group membership. | Sign-in was not yet established by the conversation or a product event. The supplied scenario already said it worked. |
| Turn 2 | Rep asks whether sign-in works. No answer yet. | The state still treats sign-in as working and repeats the permission check. | The support record is ahead of the evidence the rep actually has. |
| Turn 3 | Customer confirms sign-in works. Admin event shows the group is missing its workspace role and user sync completed. | Model identifies missing role inheritance and recommends assigning the permission, then retesting. | The final cause matches this authored case. No permission was changed and no customer resolution was observed. |

The better sequence is: keep sign-in open at turn 1; wait at turn 2; narrow the cause once turn 3 supplies the evidence. This is the reviewer's expected behaviour, not a newly demonstrated model improvement. A product lookup could answer the sign-in question instead if such evidence were actually available.

The saved case scores 13/18 checks. The facts check nevertheless passes on turn 1: `auth:works` is recorded as an extra value rather than a failure. Missing sign-in uncertainty and next-check wording account for two failed checks. Some other misses concern labels or wording; they are not all substantive support failures.

The example supports two lessons: final correctness can conceal a poor investigation sequence, and a test that supplies future information cannot fairly attribute that sequence to an unaided model failure.

## What reached the model

`run.py:build_llm_prompt` sends `case_id`, full `scenario`, prior state, the current turn, current context and a fixed catalogue of labels. It does not directly send `expected_by_turn` or the fixture's top-level `final_cause`. That narrower exclusion does not make the input blind:

- The access scenario says sign-in works before the customer confirms it.
- The stale-cache scenario describes the later cache mechanism before the first turn.
- Correction and unresolved-case scenarios describe the later correction or intended handoff. Descriptive IDs can reveal the same direction.
- The current migration prompt names specific branches and instructs a sign-in check. This is coached behaviour on a familiar case family.

All 36 saved prompts across the ten-case benchmark include their fixture scenario. All 17 saved prompts across the two level-3 cases do too. This counts scenario inclusion, not a claim that every sentence leaks an answer. The saved first access prompt is not byte-identical to the current prompt; the leakage is present in both. Do not imply the saved model run used today's exact source.

`public_context_events` supplies a `relevant` flag with descriptions and facts. The scheduler, not the model, chooses when evidence arrives. `apply_state_patch` also applies the private event's authored resolved questions and ruled-out branches. `reconcile_state` removes ruled-out branches from the active list. Therefore inspect raw `llm_patch` and final `state` separately; a good final state is partly harness behaviour.

`generate_prompt_pack` advances previous state with the deterministic reference. Its exported prompts are coached single-turn inputs, not an independent multi-turn model investigation. The saved provider-run timelines do carry their preceding applied state.

## What the scorer misses

| Finding | Current code | Read-only reproduction or evidence | Consequence |
| --- | --- | --- | --- |
| Extra facts are not penalized | `compare_state`, `check_list`: passes when required values are present; extras are reported only | State with only `invented_fact`, compared against empty expected lists, scores 6/6 | An unsupported assertion can survive a passing score. Not every extra value is wrong; the next scorer needs evidence support, not blanket rejection. |
| Relevant context is treated as sufficient cause evidence | `run_fixture`: any relevant event sets the timing flag; `compare_state` trusts it | A cause with `root_cause_evidence_available=True` passes timing even when the event only says roles are present | Ruling out one cause does not prove another. The engine does not enforce a mechanism-specific gate. |
| Unresolved final outcomes automatically pass | `root_cause_ok = not final_expected or ...` | In a controlled local probe, an empty expected cause plus `invented_cause` returns true | The final-outcome summary can conceal a fabricated diagnosis on a handoff case. |
| An empty patch cannot retract a prior cause | `apply_state_patch`: updates the cause only when the new value is non-empty | Inspection of the update condition; no production change made | A correction needs an explicit way to withdraw the prior conclusion. |
| Useful advice is reduced to expected terms | `missing_next_check_terms`; error analysis labels any non-empty miss as evaluator strictness | Saved “authenticate” advice misses a required “sign in” term | A wording miss is not automatically bad advice; non-empty advice is not automatically good advice. |

Minimal reproduction for the two simplest scorer weaknesses, from the repo root:

```python
from run import new_state, compare_state
s = new_state("review")
s["facts"] = ["invented_fact"]
assert compare_state(s, {}, False)["passed"] == 6
s["final_cause"] = "invented_cause"
assert compare_state(s, {}, True)["checks"][-1]["passed"]
```

These are demonstrations of existing weaknesses, not tests that establish correctness.

## Historical scores and corrected interpretation

| Snapshot family | Cases | Stored checks passed / total | Direct exact final-cause matches |
| --- | --- | --- | --- |
| deterministic | 12 | 318/318 | 12/12 |
| process_mock | 12 | 318/318 | 12/12 |
| predictive_mock | 12 | 275/318 | **10/12**, although the old report says 12/12 |
| gpt55_benchmark | 10 | 189/216 | 10/10, including one intentionally empty cause |
| gpt55_level3_closeout | 2 | 83/102 | 2/2, including one intentionally empty cause |

The predictive mock retains causes on the two unresolved fixtures. Its 29 premature-cause turns are deliberately scripted behaviour. They do not measure how often an actual model does this. The model rows remain limited by supplied scenarios and an incomplete scorer; exact matches are not evidence of independent investigation or successful handoff delivery.

The simulator's main HTML uses authored `CASES` data in `prototype/live_simulator.py`. A separate helper uses deterministic replay. Neither is a live connected rep interface or a rendering of the saved GPT run.

## Verification and next gate

Fresh local verification: `python3 validate_fixtures.py` validated 12 fixtures; `python3 -m unittest test_experiment.py test_ingest_handoff.py` passed 51 tests. Local scoring probes and snapshot recounts above made no model calls. The legacy tests pass while the identified limits remain.

Before COP-1 scores can support a new claim:

1. Separate evaluator-only scenarios, answer keys and future events from model input; use neutral case IDs and verify that boundary. Keep development examples distinct from unseen checks.
2. Score support for facts, withdrawal of old conclusions, cause-specific evidence and explicitly unresolved outcomes. Accept equivalent useful wording and preserve human review of judgement calls.
3. Let the assistant request permitted evidence and record why. Do not supply relevance answers or use authored cleanup as if it were model reasoning. Keep source facts and corrections traceable.
4. Compare with a simple assistant under the same information, permissions and model conditions. Include waiting, corrections, conflicting evidence, unavailable evidence and handoff. Record cost and waiting alongside advice quality.
5. Run a rep trial before claiming reduced effort, stronger technical capability or better outcomes. Until then, report only the controlled task result.

These are prerequisites within the next bounded trial, not authorization to rebuild a platform. Adi still chooses one case family before COP-1 implementation. Voice, a new UI, live integrations and cross-repo dependency changes remain outside this update.

## Snapshot identity

SHA-256 values recorded at review time; original reports and JSON were not regenerated:

- `support_process_deterministic_snapshots.json`: `07471c5d690954d3fb42903088921b38ba179d91e858010b6134368cfc7345ad`
- `support_process_process_mock_snapshots.json`: `fe81b7f1641ce97f7e68ff6bd15fca14308216ce35bf6e6ec92038536f53a779`
- `support_process_predictive_mock_snapshots.json`: `576f8967d047f8addbd03b9b88180831840b5d1fb1e2f344a5bd681e0c8c41fc`
- `support_process_gpt55_benchmark_snapshots.json`: `559c9acb03c1bd513b0f8470179d0fec139e03e2b91282d9193023ffd38cc1e4`
- `support_process_gpt55_level3_closeout_snapshots.json`: `1258212b3d7f54c2229312adec8671ec652dd1d10ff255ac61df3191034582e9`

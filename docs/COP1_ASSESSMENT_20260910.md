# Copilot pilot — assessment and scoring review

The two requested case families and the text-update gate are implemented and exercised. The pilot does not establish that compact investigation state is better than a competent simpler assistant.

## What was built

The new `trial/investigation.py` path supplies only current observations, a permitted source/question menu and records the model chooses to request. Source revisions announce changed records or query scope, and outdated records leave the current fact list. The old values remain in history. Model claims must cite current observed facts. Every intermediate cause is checked, not just the final answer. A later full state can explicitly withdraw a prior cause.

The compact version carries its preceding investigation, current facts and the newest observation. The baseline carries the full observed history and current facts. Both use Luna low with the same evidence access and support rules. Neither can change permissions, edit settings, transmit a case or act on an external app.

The update gate suppresses exact repeats and waits for unfinished text to be committed. It withdraws old advice when a partial correction or changed update begins. This is a small callable mechanism and controlled timing replay, not live audio or a streaming interface.

## What the pilot found

Six separate evaluation cases contained 15 committed updates per approach. The frozen scorer passed 9/15 updates for compact state and 6/15 for the baseline. Compact state made 47 model calls versus 37, requested six customer questions versus four, and had median accumulated model wait per update of 14.95 seconds versus 11.74. Its estimated cost was $0.028531 versus $0.021372.

These are one-run observations, not proof of superiority or a stable speed benchmark. Both approaches use the same small model. Some grading failures concern unnecessary required fields, and one handoff expectation was ambiguous. Do not turn 9/15 versus 6/15 into a public model-quality claim.

There was a concrete positive example: in C07 the compact version handed an unresolved integration case to a specialist after the rep asked; the baseline kept waiting. There were also clear problems. The baseline used an outdated fact in C03 and returned one unusable structured response. The compact version's cache diagnosis in C03 claimed a cause while saying workspace permissions remained unverified. Its frozen cause check was too permissive, although the overall stage failed for missing facts.

## Scoring review after the run

These are reviewer findings, not revised benchmark scores:

| Case | Problem with the frozen criterion | Prepared correction for future regression runs |
| --- | --- | --- |
| C03 | Stale cache alone could pass the cause check without proving the access decision used it or checking current permission. | Require current permission, stale cache and a scoped record that access was denied using the pre-migration cache. |
| C04 | “The requested log is still being collected; no new result yet” was scored as requiring handoff, without a deadline, customer request or risk trigger. | Accept waiting with the cause open; do not escalate merely because another update arrived. |
| C06 | A supported usage-limit diagnosis failed for omitting a separate credential check. | Require the rejected request and exceeded limit, not unrelated verification. |
| C07 | The pending middle update required collecting every unavailable record before waiting. | Preserve the report and open issue while waiting; the later explicit specialist request still requires handoff. |
| C08 | A supported credential mismatch failed for omitting a separate usage check. | Require the scoped signature rejection and credential mismatch, not unrelated verification. |

`trial/reviewed_cases.json` contains these clearly labelled post-evaluation regression cases. They all use the development split because these examples have now been inspected. They validate but have not received a new model run. `trial/cases.json`, the v3 hashes and all raw results stay unchanged. No new independent score is claimed from changing the answer key after seeing results.

## What the timing result means

The eager runs made 22 calls; the gate runs made 13. Eight calls in the eager runs were the deliberately inserted partial/repeat updates. Those eight calls used 30.34 seconds of accumulated provider wait and an estimated $0.004374. The remaining one-call difference came from separate model trajectories, not the gate itself.

This supports suppressing those exact redundant requests. It does not prove equivalent full-session advice or a 41% saving on real customer traffic. Duplicate/partial suggestions were not allowed to execute extra tools. Two duplicate suggestions failed the structured stage checks; all failures remain in the report. A learned trigger or a live voice layer has not earned its cost from this experiment.

## Verification and next owner review

The existing 51 tests and 22 new tests pass: 73 total. They cover hidden input boundaries, selected retrieval, invented facts, cause timing, explicit cause withdrawal, stale-record invalidation, invalid model output, safe tool targets, failed requests, duplicates and partial updates. Paid work across the two development runs, evaluation and timing was 170 requests with $0.101647 estimated usage cost. No source in Voice or its dependencies changed; no commit, push or deployment occurred.

Review three stored moments with Adi before a larger trial: C05's corrected access scope, C07's specialist request and C03's cache diagnosis. The question is whether the rep advice is useful and appropriately cautious. New independent evaluation needs fresh cases; existing ones are regression material. Rep time saved or improved technical capability still requires a rep using the tool.

Sources: [full results and saved advice](COP1_RESULTS_20260910.md), [trial plan](../trial/PLAN.md), [reviewed regression cases](../trial/reviewed_cases.json). The OpenAI model/pricing source is recorded in each run artifact; costs are estimates from usage rather than invoices.

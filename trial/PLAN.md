# COP-1 and COP-2 controlled trial

Approved 10 September 2026: migration/access and integration-failure cases, plus the text-update timing experiment. Voice Support and live app integrations remain deferred.

## Question

Does carrying an explicit investigation record improve a representative's next step compared with a simple summary-and-next-step assistant using the same model, records and permissions?

## Boundaries before results

Two development cases establish whether the runner works. Six separate heldout cases cover both families; do not revise prompts or case expectations after seeing those results. Preserve all initial failures and any repaired follow-up as separate artifacts. Case builders know their authored outcomes; the model sees only observed events, listed read sources/questions and evidence it requested. This is controlled synthetic evaluation, not independent real-world validation.

Both approaches can request the same source records and customer clarifications. The final investigation version carries its preceding structured suggestion, current facts and the latest observation; the baseline receives the full observed history and current facts. Both select the next step and can request the same records. Earlier development versions gave both the full history and are retained separately. Both receive the same basic support rules. Thus this is an incremental-state comparison against a competent baseline, not an intentionally weak straw man.

The test host announces source revision numbers when records or query scope change. Old facts from those sources leave the current ledger and remain in history. A real connection must supply equivalent update notifications; this trial does not prove such an integration. The model cannot act on the product or send an external message. The trial returns fictional read records or predefined customer answers. Source labels describe what can be read, not what the record will say. Gold outcomes and future stages are evaluator-only. The old replay harness remains historical; its percentages must not be combined with these new checks.

## Checks

Score every authored stage, including errors. Report supported structured facts, evidence-backed cause, expected resolved/unresolved investigation outcome, required facts retained and avoidance of redundant questions separately. List read requests, question requests, latency and token costs. Hypotheses and free-text advice require manual review; source IDs alone do not prove a prose assertion follows from evidence. A diagnosis is not confirmation that the customer recovered.

A successful scripted plumbing run is not a successful model experiment. Do not tune until all examples pass and then call those examples unseen. Do not claim rep time saved, technical skill gained or production safety from this trial.

## Timing scope

The update gate suppresses exact duplicate committed updates and holds unfinished text. It clears prior advice when a new meaningful update or partial correction begins. A changed fact must be processed even when the surrounding text is unchanged. There is no learned semantic trigger and no live audio.

Compare two development replays with one injected identical repeat after each stage: process every update versus suppress exact duplicates. Measure actual request counts, token usage and provider wait. Duplicate and partial calls are advice-only in this timing probe; they do not execute additional lookups. Duplicate advice receives the same structured scoring, while partial advice is checked for schema and observed-fact support. Report their failures separately. This measures redundant-request overhead, not equivalent full interactive sessions. Variation between separate model runs limits causal latency comparisons. Distinguish measured provider wait from customer-perceived end-to-end latency.

## Model and spending

Pinned model: `gpt-5.6-luna`, low reasoning, direct OpenAI Responses API, same settings in both approaches. Current official model catalog describes Luna as the cost-sensitive option: https://developers.openai.com/api/docs/models/gpt-5.6-luna . Prices used for estimates: $0.20/million input, $0.02/million cached input, $1.20/million output tokens. Verify returned usage; do not label estimates as invoices. Each run reserves at most $2 and at most 180 requests, with 2,600 output tokens per call, 45-second timeout and no automatic retries. This is a chosen experiment guard, not reinstatement of Adi's old overnight ceiling.

Existing `OpenAI:voice` is the registered shared support-experiment account used by the predecessor experiment. Load into `OPENAI_API_KEY` in memory only; no key copy, keychain change or credential in output. Public artifacts contain fictional prompts/responses and bounded provider metadata.

## Completion

Finish the code, boundary tests, two development cases, six heldout cases, timing comparison and a readable results report. If the explicit-state version does not improve on the baseline, say so. The next owner step is reviewing the rep advice on a few stored journeys, not repeating a live app integration test.

## Final freeze before heldout calls

Development v1 exposed stale unavailable records; v2 verified revision notifications but revealed overly strict required-fact checks. Both runs and their exact inputs are retained. The final fixture expectations require evidence needed for the cause, rather than unrelated extra verification. A question whose simulated answer adds no fact is reported as an observation warning, not automatically called a bad question. Up to eight model decisions per committed update allows the full small evidence/question menu plus a terminal suggestion. No prompt, runner or case edits are permitted after inspecting heldout results; any later repair requires a newly labelled follow-up.

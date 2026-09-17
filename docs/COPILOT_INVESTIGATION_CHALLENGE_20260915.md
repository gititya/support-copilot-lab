# Investigation challenge — corrected assessment

The previous completion examples did not establish investigation ability. The owner review invitation based on them is withdrawn. They remain useful only as prepared workflow/control demonstrations.

## What ran

Thirteen real OpenAI calls through the existing Walkthrough and its existing support rules. No model, prompt or assistant logic changes during the challenge; source hashes match before and after. Three authored synthetic worlds shared byte-identical first prompts and the vague report “The workspace is not working since the migration.” The case file and expected outcomes were frozen before calls. Expected outcomes never entered model inputs. Case-specific request evidence appeared only after the assistant requested it.

Each world first asked a relevant free-text clarification. The initial runner stopped instead of inventing a response to that free-text question. The coordinator inspected the three questions, then supplied the prewritten scope answer: affected users, activity, successful comparisons, timing and request IDs. This was a human-reviewed synthetic customer response, not an independent human participant. No recommendation or diagnosis was included. Once IDs were known, a request lookup became available. The assistant chose whether to read it.

The same conditional support policy was available in all three worlds. It defined authority and when a cache refresh is permitted; it did not assert that any particular case had that fault. This is legitimate product knowledge, unlike supplying a case-specific recommendation as the opening evidence. The source menus and support domain remain narrow and authored.

## Observed results

- Old denied permission versus current allowed permission: asked for details, read request evidence and policy, proposed the permitted administrator cache refresh. Recovery remained unverified.
- Current permission allowed but rendering returned 503: asked for details, read request evidence, prepared a specific engineering request without recommending the cache fix or claiming a known underlying cause.
- Logs unavailable: asked for details, read the unavailable-result record and policy, kept the cause unknown and transferred the investigation with identifiers and scope.
- Failed-fix continuation: the coordinator reconstructed the first case from its saved trace, marked the attempted fix unsuccessful, and supplied only a new customer report and a new available request lookup. A separately frozen retry record showed current permission allowed but rendering returned 503. Copilot read that record, stopped recommending the cache fix and prepared engineering investigation. Case remained open. This continuation tests the engine from a reconstructed state, not an uninterrupted browser journey.

These are observed narrow successes, not a population pass rate. The missing-record “excluded” wording from the earlier run remains a separate known weakness; this challenge did not repair or retest it. No evidence of better rep performance or time saved has been produced.

## What this does not establish

Long conversations, resistance to paraphrased loops, selective corrections, broad product knowledge, live call integration, real tool retrieval or independent rep usefulness. All cases are fictional and authored by the implementing agent. There is no independent test designer or blinded human rating. Do not call this a full repair or send Adi back through the old prepared page as proof.

## Files

- trial/investigation_challenge/worlds.json and FROZEN.sha256: original frozen worlds and expectations.
- results.json: original clarification responses, including the honest harness stop.
- continued-results.json: reviewed scope answers and subsequent decisions.
- failed-fix-world.json and failed-fix-results.json: frozen follow-up and saved result.
- run.py, continue_reviewed.py and check_failed_fix.py: exact harness scripts. They make paid calls and currently use fixed output filenames; preserve the existing artifacts before any rerun. They are not unattended production evaluators.

Input assertions checked identical first prompts, absence of expected outcomes, no private record content before lookup, no cause before request evidence, unchanged assistant source hashes, and no closure after the failed fix. No model edits were justified by these observed results. The immediate repair is the evaluation and its claims.

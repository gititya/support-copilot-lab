# Real-Time Support Updated Roadmap

This roadmap is the locked plan for taking the current offline support-copilot prototype to a completed repo.

The project stays text-first until the B2B process is proven. The root experiment harness remains the source of truth. Prototype work stays under `prototype/` unless a later milestone explicitly says to reorganize.

## Completion Rule

At the end of every milestone, check off the milestone status below and confirm:

- The root experiment harness still runs.
- The prototype still avoids premature final-cause prediction.
- The report still shows facts, unknowns, active branches, ruled-out branches, next check, and final cause timing.
- Generated or imported cases do not replace the hand-authored source-of-truth fixtures until explicitly accepted.

## Milestones

### Milestone 1 - Lock Current Prototype Baseline

Status: Completed

Goal: Preserve the current working prototype state before expanding the test surface.

Deliverables:

- Keep the root experiment harness unchanged as the source of truth.
- Keep `prototype/replay.py` as the console replay entrypoint.
- Keep `prototype/report.py` as the mock-only static report generator.
- Keep `outputs/prototype_support_panel_report.html` as the inspectable report artifact.
- Make report cases collapsible so the artifact is easier to scan.
- Save this roadmap as `Roadmap.MD`.

Checks:

- `python3 validate_fixtures.py`
- `python3 -m unittest test_experiment.py`
- `python3 prototype/report.py`

Exit criteria:

- Current baseline is committed and pushed.
- No experiment harness reorganization.

### Milestone 2 - Add Harder Hand-Authored B2B Fixtures

Status: Completed

Goal: Test whether Live Support State still helps when cases are less toy-like.

Deliverables:

- Add Level 2 B2B fixtures with longer sessions and messier evidence.
- Include at least one case with conflicting context.
- Include at least one case with late mechanism evidence.
- Include at least one case that remains unresolved and requires handoff instead of final cause.
- Include at least one case where the first complaint category is corrected mid-case.

Checks:

- Fixture validation passes.
- Process mock passes timing and state hygiene.
- Predictive mock still exposes premature-answer behavior where relevant.
- Prototype report remains readable with the larger case set.

Exit criteria:

- New fixtures prove more than the original six simple cases.

### Milestone 3 - Add Handoff And Post-Case Record

Status: Completed

Goal: Make the prototype useful when a case does not fully resolve during the session.

Deliverables:

- Add a handoff/post-case section to the prototype report.
- Show customer-safe summary.
- Show known facts.
- Show unresolved unknowns.
- Show active and ruled-out branches.
- Show final cause only if evidence supports it.
- Show recommended follow-up.

Checks:

- Resolved cases show final-cause evidence.
- Unresolved cases do not overclaim.
- Handoff content is derived from Live Support State, not a separate transcript summary.

Exit criteria:

- A support agent could use the handoff section to continue the case.

### Milestone 4 - Define Support-Call-Generator Import Contract

Status: Completed

Goal: Make this repo ready to consume generated cases without depending on generator internals.

Deliverables:

- Document the required generated fixture shape.
- Define required fields for transcript turns, timed context events, expected state, leakage rules, and final cause timing.
- Add a small validation path for imported generated cases.
- Keep generated cases separate from the current accepted root fixtures until reviewed.

Checks:

- Existing fixtures remain valid.
- Import contract is readable without opening the generator repo.
- No direct runtime dependency on the generator is required yet.

Exit criteria:

- The generator has a clear target schema to export into.

### Milestone 5 - Add Generated Fixture Importer

Status: Completed

Goal: Prepare for scaled B2B testing once the support-call-generator can export compatible cases.

Deliverables:

- Add a standard-library importer for generator-produced support-process fixtures.
- Write imported cases to a review/staging location, not directly into accepted fixtures.
- Add checks for missing context, premature mechanism leakage, and unsupported schema versions.
- Add docs for the import workflow.

Checks:

- Importer handles a sample generated fixture.
- Bad generated fixtures fail with clear messages.
- Root fixtures and experiment outputs are not overwritten by import.

Exit criteria:

- This repo can accept generator output safely once the generator evolves.

### Milestone 6 - Run First Generated B2B Batch Through Review Lane

Status: Completed

Goal: Test more B2B support calls without hand-authoring every case, while keeping generated cases separate from the strict root fixture set.

Deliverables:

- Import a small generated batch into `outputs/generated_fixture_staging/`.
- Render generated cases through `prototype/generated_review.py`.
- Write generated review output to `outputs/generated_support_review.html`.
- Promote only accepted generated cases into the main fixture set.
- Capture failure patterns in the roadmap or README.

Checks:

- Process behavior remains evidence-timed.
- Next checks stay actionable.
- Irrelevant or misleading context does not pollute state.
- Generated cases are not loaded by the strict root experiment by default.
- `python3 prototype/generated_review.py` renders staged generated cases.

Exit criteria:

- Generated cases expose useful gaps or confirm robustness beyond the original fixtures without weakening the root experiment harness.
- Generated batches include realistic outcomes: resolved, probable cause, and handoff.

### Milestone 7 - Tighten Evaluation Criteria

Status: Completed

Goal: Move beyond simple field matching into better support-process scoring.

Deliverables:

- Evaluate next-check usefulness more flexibly.
- Track whether unknowns are resolved at the right time.
- Track whether ruled-out branches have evidence.
- Track candidate branch drift.
- Separate wording misses from true process misses.
- Keep generated-case review scoring separate from strict hand-authored fixture scoring until promotion.
- Treat handoff as a valid support outcome, not a failure, when next owner and customer-safe summary are clear. Engineering escalation, customer-admin transfer, identity-team transfer, implementation-owner follow-up, vendor dependency, and unresolved follow-up are represented as handoff details.

Checks:

- Existing 10 baseline fixtures still pass.
- Harder fixtures identify meaningful misses without brittle wording failures.
- Generated fixture review identifies promotion readiness without requiring direct root-fixture insertion.
- Generated fixture review reports outcome distribution and flags missing resolved, probable-cause, or handoff coverage before UI/UX.

Exit criteria:

- The evaluator rewards support discipline, not exact phrasing.

### B2B Real-Testing Checkpoint

Status: In progress

Latest result:

- `main` is now the source branch for the B2B prototype.
- Fresh 15-case harder offline generator batch: 14/15 ready for promotion by generated-review checks.
- Full 67-case historical generator export stress review: 33/67 ready for promotion.
- Stress review outcome mix: 13 resolved, 24 probable cause, 30 handoff.
- The remaining new-batch miss is a next-check wording issue, not premature final-cause prediction.
- Older historical generator cases mostly fail on final-cause mismatch or incomplete probable/resolved outcome details, so they should not be promoted without review.

Next gate before product-demo hardening:

- Human-review the ready generated cases for support usefulness.
- Promote only strong cases into `fixtures/`.
- Keep weak generated cases in staging or send feedback back to `support-call-generator`.
- Treat the current simulator as the B2B prototype surface, not only as a report artifact.
- Keep generated-case promotion separate from UI polish. The prototype can be demonstrated with curated cases, but fixture promotion remains the standard for expanding the accepted test set.

### Milestone 8 - B2B Copilot-Like UI/UX Transformation

Status: Completed

Goal: Turn the static HTML report/demo into a crisper support-copilot workspace that demonstrates how a human support agent would use the copilot during a case.

Deliverables:

- Replace the dense report feel with a clearer Copilot-like support workspace.
- Keep it mock-only and local unless explicitly changed.
- Preserve every audit field: facts, unknowns, active branches, ruled-out branches, next check, final cause timing, and handoff.
- Make case navigation, turn progression, and state changes easier to scan.
- Show the case route: intake, clarify issue, check context, narrow cause, resolve or hand off.
- Show the evidence timeline so the reviewer can see what changed the case and when.
- Show handoff readiness as a preview only, not a pass/block quality gate.
- Expand the demonstrable prototype from one strong case to a small set of three curated cases: access after migration, billing correction, and invite/email noise resistance.
- Do not add voice, real integrations, or customer-facing chat.

Checks:

- UI is easier to understand than the current HTML report.
- It does not hide the evidence trail.
- It still makes premature final-cause prediction obvious.
- It works across the accepted B2B fixture set.
- A support agent could watch the replay and understand what to ask or check next.
- A support leader could see why the copilot would help agents work cases more safely.

Exit criteria:

- B2B prototype is usable enough to test as a product experience before deciding whether B2C is worth adding.
- The prototype can be described honestly as built and demonstrable, but not battle-tested or integrated with real support systems.
- The visual pass from Claude Design is incorporated without changing the root experiment harness.

Result:

- `outputs/support_live_simulator.html` now renders a polished 3-case live simulator.
- The simulator covers migration access, billing mismatch, and invite delivery.
- The screen shows case route, next best move, working hypotheses, known facts, unknowns, product/support context, evidence timeline, handoff readiness preview, and raw eval state behind a toggle.
- Focused tests lock the curated cases so final outcomes remain withheld until evidence arrives.

### Milestone 8.5 - Real Model Feasibility Check

Status: Isolated branch

Goal: Keep real/local model feasibility separate from the product prototype until a model can reliably produce useful Live Support State.

Current evidence:

- Branch `codex/llm-live-replay-orchestration` adds Ollama/MLX adapters and an offline replay runner.
- `ollama:qwen2.5:7b` can return valid JSON for the replay, but scored only 8/18 checks on the first smoke case and missed the next-check standard.
- `gemma4:e4b`, `gemma4:12b-it-qat`, and MLX Qwen3-4B timed out in bounded smoke runs.
- `gpt-5.5` completed the full 10-fixture benchmark at 189/216 checks, 87.5% pass rate, with 0 premature final-cause errors. This proves the architecture is credible with a strong cloud model, but not yet polished enough to make real-model output the default demo behavior.

Next gate:

- Do not merge local-model replay into `main` as core product behavior yet.
- Tune the cloud-model prompt/state contract before local-model tuning.
- Add a smaller benchmark mode for one curated case and the 3-case simulator set.
- Improve next-check scoring so useful support actions are not penalized only because the wording differs.
- Compare another strong cloud model after GPT-5.5 prompt/scoring improvements.
- Treat local models as an optimization problem after the cloud path is stable.

Exit criteria:

- A real model can produce useful Live Support State across a curated B2B case set without premature final-cause guesses.
- Saved model timelines can be loaded into the static simulator only after they are useful enough to compare with the reference trace.

### Milestone 9 - Decide Whether To Add B2C

Status: Not started

Goal: Decide if B2C belongs in this repo after the B2B prototype is demonstrable and at least one real-model feasibility check is understood.

Deliverables:

- Compare B2B and B2C evidence needs.
- Decide whether B2C is a new fixture pack, a separate repo, or out of scope.
- If accepted, add B2C domain rules before adding B2C fixtures.
- Keep the future handoff-agent repo separate. This repo may produce handoff-ready case state; the handoff-agent repo should own pass/block/correct quality gates.

Checks:

- B2C does not dilute the original support-process thesis.
- B2C cases still require evidence-timed state, not early answer prediction.
- B2C is not used to avoid finishing the B2B prototype story.

Exit criteria:

- Clear go/no-go decision for B2C.

### Milestone 10 - Completion Gate

Status: Not started

Goal: Decide that this repo is complete as a support-process evaluation and prototype lab.

Deliverables:

- Stable README.
- Stable roadmap state.
- Passing root experiment harness.
- Passing prototype report generation.
- Accepted B2B fixture set.
- Clear generated-case workflow.
- Clear UI/prototype verdict.

Checks:

- `python3 validate_fixtures.py`
- `python3 -m unittest test_experiment.py`
- `python3 run_all.py`
- `python3 prototype/replay.py --case access_after_migration`
- `python3 prototype/report.py`

Exit criteria:

- The repo can answer: "Did the support assistant work the case correctly as evidence arrived?"

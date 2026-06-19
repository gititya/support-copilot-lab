# Real-Time Support Updated Roadmap

This roadmap is the locked plan for taking the current mock-only support-process lab to a completed repo.

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

### Milestone 7 - Tighten Evaluation Criteria

Status: In progress

Goal: Move beyond simple field matching into better support-process scoring.

Deliverables:

- Evaluate next-check usefulness more flexibly.
- Track whether unknowns are resolved at the right time.
- Track whether ruled-out branches have evidence.
- Track candidate branch drift.
- Separate wording misses from true process misses.
- Keep generated-case review scoring separate from strict hand-authored fixture scoring until promotion.

Checks:

- Existing 10 baseline fixtures still pass.
- Harder fixtures identify meaningful misses without brittle wording failures.
- Generated fixture review identifies promotion readiness without requiring direct root-fixture insertion.

Exit criteria:

- The evaluator rewards support discipline, not exact phrasing.

### Milestone 8 - B2B Copilot-Like UI/UX Transformation

Status: Not started

Goal: After B2B testing is strong, turn the static HTML report into a crisper support-copilot experience that Adi can judge like a product surface.

Deliverables:

- Replace the dense report feel with a clearer Copilot-like support workspace.
- Keep it mock-only and local unless explicitly changed.
- Preserve every audit field: facts, unknowns, active branches, ruled-out branches, next check, final cause timing, and handoff.
- Make case navigation, turn progression, and state changes easier to scan.
- Do not add voice, real integrations, or customer-facing chat.

Checks:

- UI is easier to understand than the current HTML report.
- It does not hide the evidence trail.
- It still makes premature final-cause prediction obvious.
- It works across the accepted B2B fixture set.

Exit criteria:

- B2B prototype is usable enough to test as a product experience before deciding whether B2C is worth adding.

### Milestone 9 - Decide Whether To Add B2C

Status: Not started

Goal: Decide if B2C belongs in this repo after B2B has been proven.

Deliverables:

- Compare B2B and B2C evidence needs.
- Decide whether B2C is a new fixture pack, a separate repo, or out of scope.
- If accepted, add B2C domain rules before adding B2C fixtures.

Checks:

- B2C does not dilute the original support-process thesis.
- B2C cases still require evidence-timed state, not early answer prediction.

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

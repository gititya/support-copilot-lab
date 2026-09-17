---
status: "complete"
current_phase: "Complete B2B support-process proof-of-work."
next_action: "Keep closed unless the engine shape is reused by the Handoff Quality Gate."
things_to_know:
  - "This is the canonical continuation of real-time_support."
  - "The repo intentionally excludes B2C mode, local-model tuning, and a broader UI rebuild."
---

# support-copilot — SKILL.md

This repo is the finished B2B support-process evaluation lab for proving that an AI can work a support case as evidence arrives instead of guessing a final root cause early. Keep changes small, standard-library only, and centered on the accepted fixture harness: `fixtures/`, `run.py`, `mock_llm.py`, `test_experiment.py`, and generated evidence under `outputs/`. The closeout stance is deliberate: B2C belongs in sibling support/handoff work, local-model tuning stays parked, and the reusable part is the engine shape of incremental Live Support State plus evidence-timed final-cause gating.

## 2026-07-30 — Shipped documentation checkpoint

- README and BUILDS now place the B2B process proof inside the wider Support system without
  merging its domain boundary into Voice or B2C.
- The two parked model-replay branches were preserved as patches under
  `Old_files/branch-archives/2026-07-30/`; they are historical experiments, not pending work.

## 2026-07-30 — Active product boundary correction

- Support Copilot is an active rep-side product/proof, not an archived repository. It helps a human
  representative keep facts, unknowns, candidate and ruled-out branches, choose the next check,
  resolve when evidence permits, and avoid unnecessary or premature engineering escalation.
- Only the original early-root-cause-prediction premise and the archived local-model/comparison
  branches are historical experiments.
- Keep the repo independently visible. A later live-desk UI may consume its stable case-state/replay
  seam, but must not absorb its source or history merely to reduce repository count.

## 2026-09-10 — COP-0 evidence review

- COP-0 completed as a local documentation/evidence correction. Read `docs/COP0_EVIDENCE_REVIEW.md` before interpreting historical percentages. Code and saved outputs were not changed.
- Current and saved prompts include scenario information that can reveal future facts; context relevance and parts of state cleanup are authored. The scorer tolerates extra facts, treats any relevant event as sufficient for timing and auto-passes empty expected causes. A non-empty-only patch cannot clear an earlier final cause.
- The predictive mock has 10/12 exact final outcomes, not the stored summary's 12/12. Saved GPT outcomes still match, but are not blind investigation proof. Fresh validation: 12 fixtures, 51 tests.
- Next is one bounded COP-1 trial chosen with Adi. Repair those evidence/scoring boundaries before collecting new results. Compare with a simple assistant; no live voice, new UI or integration work is authorized by COP-0.

## 2026-09-10 — COP-1 and bounded COP-2 pilot

- Adi selected access after migration and integration failures, plus the text-update timing experiment. New stdlib `trial/investigation.py` uses explicit observed-input projection, chosen reads/questions, current-source citations, per-decision cause checks and host-announced source revisions. Old source and reports are unchanged.
- Compact state vs full-history baseline used the same Luna low model. Six separate synthetic evaluation cases: 9/15 vs 6/15 stages under frozen criteria; 47 vs 37 calls. Do not claim superiority: some criteria were flawed and free prose needs rep review. Read `docs/COP1_ASSESSMENT_20260910.md`.
- Duplicate/partial timing: 22 vs 13 requests, with eight explicitly scheduled extra requests suppressed. Advice-only extra calls do not establish full-session equivalence or live latency.
- Evidence under `outputs/cop1/`: original failures/inputs, freeze hashes, both heldout families and timing. `trial/reviewed_cases.json` is post-evaluation regression material, validated but not model-rerun. No post-hoc replacement of recorded scores.
- Verification: 51 old plus 22 new tests passed; 170 total provider calls, estimated usage $0.101647. No Voice changes, live rep trial, commit or push. Next: Adi reviews C05 corrected scope, C07 specialist request and C03 cache diagnosis; fresh cases needed for independent claims.

## 2026-09-11 — owner support review implemented

Latest owner review supersedes the historical closed status above. Private rep assistant, not a customer agent. Current `trial/investigation.py` loads `trial/SUPPORT_RULES.md`, uses `suggest_fix` rather than `resolve`, and integrates `case_progress.py`. Only host rep controls bound to current proposal verify outcome or close; never infer controls from transcript/model. New evidence invalidates old proposal IDs; reject combined controls/new facts and preserve rejected-control evidence. Closed timing paths do not call model. Handoff packets are local, unsent and rep-reviewed. 40 trial + 51 existing tests passed. Six model spot checks preserve known broad-question weaknesses, not superiority. See docs/COPILOT_OWNER_REVIEW_20260911.md. Original v3 runner/inputs archived with hashes. Voice, live integrations and publishing untouched. Next: rep-facing text walkthrough, not another broad benchmark.

## 2026-09-11 — interactive rep walkthrough

`trial/rep_walkthrough.py` and `Start Copilot Walkthrough.command` provide the next owner trial. Real Luna API, two fictional prepared cases C05/C07, full observed history for custom rep notes, current read-only source menu, no fixture answers auto-consumed and no oracle scoring. Explicit advice command only; rep outcome/closure reuse CaseProgress with no model calls. Custom notes retire current prepared ledger/source snapshots conservatively, history remains; `next` loads next prepared stage. Cause citations must include a product record, but this is not semantic causality proof. No customer messages or external handoff. 52 trial + 51 existing tests pass. Traces save under outputs/walkthrough with source hashes; session resume not built. Read docs/TRY_COPILOT.md. No Voice changes or push.

Walkthrough follow-up: explicit `answer TEXT` preserves current product evidence only when the rep asserts the affected scope is unchanged; plain correction notes retire it. Answers remain rep reports and never outcome controls. Prepared source revisions are supplied in prompts. Current tests: 53 trial + 51 existing = 104.

## 2026-09-11 — webpage replaces terminal owner route

Owner rejected terminal UX after repeated unavailable-source read. Added trial/web_walkthrough.py + trial/web/{index.html,app.js,style.css}; Tier 3 approved, Crown consulted. portless copilot-lab python3 trial/web_walkthrough.py -> http://copilot-lab.localhost:1355. Cookie-auth loopback API, Origin/custom-header/version/proposal checks, per-session lock, model key backend-only. 30-call budget shared across case switches; reload keeps browser session in memory, restart does not restore disk state. Repeated reads removed from model choices, one bounded recovery if requested anyway, audit retained. 62 trial + 51 existing tests pass. User route is webpage, not terminal. Read docs/TRY_COPILOT_WEB.md.

Final web review fixes: unclear/untried retract prior success wording; replacement advice clears obsolete pending question. 65 trial + 51 existing tests = 116. Browser CUA verified actual model advice, rep answer, suggested fix, worked preserving open state and explicit close. Final server restarted for owner.

## 2026-09-12 — Investigation focus repair

Walkthrough caches unchanged advice, excludes unavailable reads, removes answered broad questions, and offers precise clarify follow-ups with distinct evidence keys. SUPPORT_RULES constrains questions to the current problem. suggest_check is diagnostic, not a supported fix; worked means original activity recovered. UI shows diagnostic next.reason. 74 trial + 51 existing tests passed. Three approved owner-session checks saved at outputs/cop1/focus-review-20260912.json; reviewed spot checks only. See docs/TRY_COPILOT_WEB.md.


### 2026-09-15 — Bounded HCAI completion pass

Owner requested a finished experiment, no broad product expansion. Read docs/COPILOT_COMPLETION_20260915.md before further work. `finding` preserves the current evidence; `note` remains explicit snapshot correction. Web defaults to three cases in completion_cases.json; older examples remain selectable. `accept_handoff` stops with an unsent local draft and no recovery claim. Exact repeated clarifications stop; semantic repetition remains unproven. 81 trial tests and 46 historical tests pass. Two saved live development runs each have seven workflow and three simple-summary calls; unprompted transfers work on these supplied facts. One “excluded records” assertion overreaches missing-record evidence. Owner usefulness review pending; do not expand or claim rep benefit. Git unavailable due Xcode licence; no commits/pushes.


### 2026-09-15 — Owner rejected answer-fed review; assessment corrected

The earlier ready-for-owner-review claim is withdrawn. Read docs/COPILOT_INVESTIGATION_CHALLENGE_20260915.md. Thirteen real calls tested three identical vague openings with different hidden request evidence, plus a failed-fix continuation reconstructed from trace. Case expectations excluded from inputs; request evidence revealed only after lookup; assistant source hashes unchanged. Observed appropriate divergent actions and revision after failed fix. Synthetic coordinator-authored checks only, not independent rep benefit or long-conversation reliability. Web examples explicitly labelled prepared demonstrations. No new prompt/runtime fix made to chase these results. Harness scripts preserve the recorded procedure but fixed filenames require artifact backup before rerun. Do not ask Adi to repeat those prepared demos as proof.


### 2026-09-16 — Two sequential owner journeys

User approved both resolution and engineering escalation together. Read docs/TWO_JOURNEYS_20260916.md. JourneyWalkthrough uses shared journey_world.json: opening complaint/account only; rep-supplied IDs enable a lookup, model read reveals records. Selected ending never enters model input. Web now offers only resolve_journey/escalate_journey. Rep-only customer-facts disclosure is not model input. 86 trial tests, real-model BrowserSession checks, and real browser controls passed both complete paths. Owner review now appropriate for this narrow experiment; no independent usefulness claim. Public README draft in Obsidian Readmes/Copilot Lab.md; not published.


### 2026-09-16 — Owner-reviewed experiment documented

Owner said the experience seemed to work and requested session review, README and state updates. Latest substantive trace e43b3138-f3aa-43a7-822b-64869ed5807e has 7 calls: clarification, supported fix, reported recovery, later changed symptom/retry evidence, engineering handoff. No worked/close/accept control in owner trace; do not claim two completed owner cases. Separate browser tests establish those controls. Read docs/OWNER_WALKTHROUGH_20260916.md. Repo README, docs/README_COPILOT_DRAFT.md and Obsidian Readmes/Copilot Lab.md synchronized. Use scenario-based evaluation, simulated support data and formative owner walkthrough for the experiment. Historical technical filenames unchanged; raw evidence preserved. Bounded experiment now paused after positive owner review; no further build, Voice work or publication authorized by closeout.

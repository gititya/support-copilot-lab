# Copilot Lab — investigating before concluding

**A useful copilot keeps the investigation honest: what we know, what we suspect, and the next check that can separate the possibilities.**

I built this offline experiment to examine how AI could help a support rep work a case as evidence arrives. It keeps facts, unanswered questions, possible causes, ruled-out causes and the next check in a visible case record.

Early hypotheses are useful. The failure is presenting or acting on one as an established fact before the evidence supports it.

This is a prepared support-process demonstration and evaluation harness. No support representative has used it. It does not receive live helpdesk input or choose and retrieve evidence from a connected product.

## Web walkthrough — preferred

Open [the local Copilot webpage](http://copilot-lab.localhost:1355). Use Get advice, the rep-answer box and explicit outcome buttons. See [web instructions and limits](docs/TRY_COPILOT_WEB.md). The terminal walkthrough below is retained for development; the webpage is the owner-facing route.

## Try the rep walkthrough

Open **Start Copilot Walkthrough.command** in this folder. Choose workspace access or missing integration records, then type `advice`. These are fictional cases with real AI advice; your notes go to OpenAI. You remain the rep and explicitly report outcomes and close cases. See [the short instructions and limits](docs/TRY_COPILOT.md).

The interactive path has no live helpdesk connection. It conservatively retires old prepared records when you add custom notes. 53 current trial tests plus 51 existing tests pass; these are software checks, not proof of rep benefit.

## Rep-reviewed behavior — September 11

Copilot privately advises the human rep. A suggested fix keeps the case open. Only explicit rep feedback can verify success; closure is a separate rep decision. Failed or uncertain outcomes remain open. The rules also distinguish reported scope from confirmed scope and encourage useful investigation while a diagnostic check is pending.

Read [what changed and what remains unproven](docs/COPILOT_OWNER_REVIEW_20260911.md). The [support rules](trial/SUPPORT_RULES.md) are editable and loaded by the current trial. There are 40 current trial tests plus 51 existing tests. Six reviewed-example model checks are saved separately from the original comparison; no live rep interface or call integration is claimed.

## Current trial — September 10

The new trial lets the model choose which fictional product records to read in two families: access after migration and integration failures. It compares compact investigation state with a summary-and-next-step assistant using the same model and evidence access. It also tests exact-duplicate and unfinished-text suppression.

**Built and tested; benefit remains unproven.** The frozen pilot passed 9/15 stages for compact state versus 6/15 for the baseline, but compact state made more calls and the review found grading problems. Do not use those fractions as a claim that the product is better. Read the [assessment](docs/COP1_ASSESSMENT_20260910.md) before the [raw results and rep advice](docs/COP1_RESULTS_20260910.md).

Run the new boundary tests without model calls:

```bash
python3 -m unittest discover -s trial -p 'test_*.py'
```

The September 10 version had 22 passing tests, alongside 51 existing tests. `trial/PLAN.md` records the comparison and limits. `outputs/cop1/frozen-v3-inputs/` preserves the v3 runner and inputs; `trial/cases.json` preserves the frozen pilot; `trial/reviewed_cases.json` contains later-reviewed regression cases and is not unseen evaluation material. Provider runs require an intentionally supplied `OPENAI_API_KEY`; each run has explicit call/output limits and never overwrites a result file.

The sections below describe the earlier experiment. Its code and reports remain for reproduction; the new trial does not silently repair or regrade those historical scores.

## Why I changed the question

The [early-prediction experiment](https://github.com/gititya/support-early-prediction-experiment) asked whether the opening of deliberately difficult synthetic support calls revealed the specific cause. Those results led me to stop pursuing early diagnosis and examine investigation assistance instead. They do not establish that early diagnosis is impossible in every support setting.

The next question is more useful: can an assistant help a rep choose what to check, revise when the customer corrects something, and preserve uncertainty when a person must take over?

## One case, and a mistake worth showing

A customer says: “Three users lost access after our migration yesterday.”

| Stage | What support knows | What remains possible | Useful next step |
| --- | --- | --- | --- |
| Initial report | Three users report lost access after migration. | Sign-in failure, missing workspace permission, delayed user sync or stale access data. | Establish whether sign-in itself works. |
| Customer clarification | They can sign in, but cannot open the workspace. | Workspace permissions, sync and access data still need checking. | Inspect the affected users' permissions and product records. |
| Product evidence | The prepared admin record shows user sync completed, but their group lacks the workspace permission. | That evidence supports the permission cause for this fixture. | Have an authorized person correct the permission, then check whether access works. The replay does not perform that change. |

```text
Initial report → Customer clarification → Product evidence
       At each stage: known / suspected / next check
                       ↓
             Supported cause or unresolved handoff
```

**The saved model did not follow that sequence cleanly.** At the first turn it already recorded that sign-in worked and skipped the sign-in question. It reached the correct final cause later. But the prompt had supplied a case summary containing the later sign-in fact from the start.

That is a test-design problem as well as a flawed support sequence. It would be wrong to present this as an unaided model hallucination, or as a blind investigation success. [Read the saved case and the review](docs/COP0_EVIDENCE_REVIEW.md#the-readable-case).

## What the evidence actually supports

The September 10 review checked saved snapshots and current code. These are historical scores, not new model runs or rep outcome measurements.

| Evidence | Scope | Stored checks | What it establishes |
| --- | --- | --- | --- |
| Deterministic reference | 12 synthetic cases | 318/318 | The programmed reference matches the expected checks. |
| Process mock | 12 synthetic cases | 318/318 | A scripted updater can demonstrate the intended sequence. |
| Predictive mock | 12 synthetic cases | 275/318; 29 premature-cause turns | The scorer catches some deliberately programmed early conclusions. This is not observed model behaviour. |
| Saved GPT-5.5 benchmark | 10 synthetic cases | 189/216; 72–96% per case | A guided model run produced inspectable states. All 10 stored final causes, including one empty unresolved result, match the fixtures. |
| Saved GPT-5.5 level-3 run | 2 synthetic cases | 83/102 | Both stored final causes match, including one empty unresolved result. This also used prepared scenarios. |

The old summary marks the predictive mock's final outcomes as 12/12. A direct comparison finds **10/12**: both unresolved cases incorrectly retain a cause, but the old final-outcome scorer automatically passes fixtures whose expected cause is empty. The original reports remain intact; the [review](docs/COP0_EVIDENCE_REVIEW.md) records the correction.

Four limits matter before interpreting any percentage:

1. **Future information reaches the model.** The prompt includes the full scenario and a descriptive case ID. Some scenarios reveal later facts, corrections or causes. All 36 prompts in the saved ten-case run contain their scenario.
2. **Some investigation work is supplied.** Context arrives on a fixed schedule and carries a relevance label. The harness also applies authored resolved questions and ruled-out causes. It is not all model reasoning.
3. **The scorer is incomplete.** Extra unsupported facts can pass. Any relevant context opens the cause-timing check, even if it only rules out one possibility. An expected unresolved outcome can pass with a claimed cause.
4. **The scores do not measure rep benefit.** Wording checks can reject reasonable phrasing; passing checks does not show fewer questions, less effort or a better customer outcome.

These limits remain in the historical harness. The new trial uses separate input and scoring boundaries; its own limitations and later scoring review are recorded in the current assessment.

## Try the prepared replay

The existing [HTML simulator](outputs/support_live_simulator.html) presents three prepared demos and two level-3 cases. Its main display uses authored design data; it is not a live view of GPT output.

To regenerate it locally:

```bash
python3 prototype/live_simulator.py
```

Open `outputs/support_live_simulator.html`. Use the [saved model report](outputs/support_process_gpt55_benchmark_report.md) and [raw snapshots](outputs/support_process_gpt55_benchmark_snapshots.json) to inspect actual recorded model output.

To check the existing harness without making model calls:

```bash
python3 validate_fixtures.py
python3 -m unittest test_experiment.py test_ingest_handoff.py
```

The September 10 check validated 12 fixtures and passed 51 tests. Those tests do not cover the weaknesses described above.

`python3 run_all.py` regenerates the local reports. It can also run a paid model if `SUPPORT_PROCESS_RUN_REAL_MODEL=1` is set. Preserve historical outputs before rerunning it. `run.py --help` describes the command and provider options; no new model call was made for this review.

## What comes next

Review the saved rep advice with Adi: corrected access scope, an explicit specialist request and the cache diagnosis. The controlled comparison has run; its results do not yet justify a larger build. Use the reviewed cases for regression, then fresh cases for any new independent comparison.

Helping a less technical rep work a technical case is the intended benefit. It needs a rep trial. Lower cost, faster handling and fewer escalations also need evidence; none follows from storing a structured case record.

The work is LTS-inspired in its interest in updating state and giving useful advice as information arrives. It is not a reproduction of a voice-agent method. Live audio and retrieval from real connected products remain future work. The new trial selects fixture records and suppresses exact duplicate or partial updates; it does not reproduce a full voice-agent method.

## Scope and files

This is a rep-facing experiment, separate from Voice Support and Internal Desk. It does not click controls, deliver cases to a helpdesk, or authorize product changes.

- `run.py`, `mock_llm.py`, `run_all.py`: replay, programmed comparisons, provider calls and scoring. The current rules contain specific B2B cases; replacing fixtures alone is not a general product integration.
- `fixtures/`: twelve authored cases, evidence arrival schedules and expected states.
- `prototype/`: prepared screens, replay tools and import utilities. [Import contract](prototype/IMPORT_CONTRACT.md).
- `outputs/`: historical traces, prompts, model responses and generated displays.
- [COP-0 evidence review](docs/COP0_EVIDENCE_REVIEW.md): current findings, exact sources, score corrections and the next trial's prerequisites.

Real transcripts contain customer data. Keep them outside public git history. Provider or external-command runs can send their contents to the configured service.

**The claim I can make:** I built an offline experiment that makes parts of a support investigation inspectable, and used its saved traces to find weaknesses that final-answer scoring concealed. Whether it helps a rep investigate better is the next test.

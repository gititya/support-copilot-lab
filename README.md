# Real-Time Support - Updated

My corrected take on real-time support intelligence. The first version asked the wrong question: can an AI predict the specific root cause from the opening turns of a support conversation? This version asks the support question that actually matters: can the AI work the case properly as evidence arrives?

This repo is now a working offline prototype with an evaluation harness underneath. The prototype shows a support copilot working one case turn by turn, while the harness proves whether the copilot keeps facts, unknowns, possible causes, ruled-out paths, next checks, and final outcomes in the right order.

To try the product surface:

```bash
python3 prototype/live_simulator.py
```

Then open:

```text
outputs/support_live_simulator.html
```

To run the evaluation harness:

```bash
python3 run_all.py
```

## The one idea

The original repo tested early root-cause prediction. It failed for the right reason.

In support, the first few turns usually contain symptoms, not mechanism. A customer says "three users lost access after migration," but that does not prove SCIM delay, stale cache, missing role inheritance, or login failure. Those are branches to investigate, not answers to announce.

So this repo changes the scoreboard.

We do not reward the model for guessing the final cause early. We reward it for maintaining a useful live support state:

1. **Facts stay separate from guesses.** "Three users lost access" is a fact. "Missing role inheritance" is not a fact until system evidence supports it.
2. **Unknowns stay visible.** Can the users sign in? Did SCIM finish? Does the group have a workspace role? The state should hold those open instead of hiding them inside a confident answer.
3. **Branches can be alive without being promoted.** Login issue, role issue, SCIM delay, stale cache can all be candidates. None should become the final cause just because they sound plausible.
4. **The next check matters.** A good support copilot should help the agent decide what to inspect next, not just produce a polished explanation.
5. **Final cause waits for product/support evidence.** The answer can be right and still be bad support if it was said before the evidence existed.

That last point is the whole correction.

## Why this exists

This is an updated extension of [`gititya/real-time_support`](https://github.com/gititya/real-time_support).

The original repo was valuable because it killed the first premise cleanly. Its Phase 1 result showed that specific root-cause prediction from the first six turns collapsed: early specific accuracy was 14% overall and 7% on clean calls, while full-transcript accuracy was 92-97%. That means the model and judge were not broken. The early transcript simply did not contain the mechanism yet.

The mistake was treating LTS/process thinking as early final-answer prediction.

This repo corrects that. It keeps the LTS spirit - listen, update state, speak only when useful - but applies it to support process:

```text
transcript turn + mock system context
        |
        v
Live Support State
        |
        v
facts / unknowns / branches / ruled-out paths / next check
        |
        v
final cause only after mechanism evidence appears
```

## The cases

The harness uses ten support cases, including simple fixtures and harder B2B cases:

1. `access_after_migration` - three users lost access after migration.
2. `billing_plan_mismatch` - customer starts with a login complaint, then corrects to billing plan mismatch.
3. `invite_email_not_arriving` - admin invite exists, but the email never arrives.
4. `stale_cache_after_migration` - migration access symptom where the tempting early role-inheritance answer is wrong.
5. `corrected_billing_after_access_report` - customer corrects an access report into a billing entitlement issue.
6. `invite_with_irrelevant_billing_context` - invite delivery case with unrelated billing context that must be ignored.
7. `level2_conflicting_migration_context` - migration case where the tempting early answer is wrong until late entitlement evidence arrives.
8. `level2_late_billing_evidence` - billing case where final cause waits for late product context.
9. `level2_irrelevant_then_late_invite_context` - invite case with irrelevant context before useful delivery evidence.
10. `level2_unresolved_workspace_handoff` - unresolved workspace case that should hand off instead of inventing a final cause.

Each case has:

- transcript turns
- mock product/support context
- expected support state after each turn
- final cause once evidence exists

The runner compares three baseline behaviors, plus an optional real-model run:

```
deterministic   = hardcoded reference trace, the answer key
process_mock    = behaves like the intended LTS support-process updater
predictive_mock = behaves like the old failed idea and guesses final cause early
real_model      = optional provider-backed run over the same fixtures
```

Current result:

```
deterministic    108/108  100%   premature final causes: 0
process_mock     108/108  100%   premature final causes: 0
predictive_mock   96/108   89%   premature final causes: 12
real_model        opt-in; not faked when no key/model is configured
```

The predictive mock still gets the final cause right by the end. It fails because it says the answer too early.

## What this is not

1. NOT a customer-facing support bot.
2. NOT a voice agent.
3. NOT a real integration with Zendesk, Intercom, Salesforce, Stripe, or product databases.
4. NOT battle-tested production automation.
5. NOT a claim that support AI agents do not already exist.
6. NOT a root-cause prediction benchmark.

It is a working offline prototype for one narrow product question: can a support copilot help an agent work the case correctly as evidence arrives?

## What's in here

1. `run_all.py` - one-command experiment runner. Validates fixtures, runs the reference baseline, writes prompts, runs the process mock, runs the predictive mock, optionally runs a real model, and writes the summary.
2. `run.py` - the core replay runner, provider adapter, command adapter, and evaluator.
3. `mock_llm.py` - two local model behaviors: `process` and `predictive`.
4. `validate_fixtures.py` - schema checks for the support fixtures.
5. `test_experiment.py` - regression tests that prove process passes and predictive fails.
6. `fixtures/` - support-process cases with expected turn-by-turn state.
7. `prototype/live_simulator.py` - static 3-case live replay simulator for judging the support-agent experience.
8. `outputs/` - generated simulator, reports, dashboards, snapshots, model-ready prompt records, and real-model error analysis.
9. `AUDITABLE_SUPPORT_AI.md` - the product idea behind the prototype.

### Run it

```bash
python3 run_all.py
```

Then read:

```text
outputs/experiment_summary.md
outputs/real_model_error_analysis.md
outputs/support_process_process_mock_report.md
outputs/support_process_predictive_mock_report.md
```

Open the dashboards in a browser if you want the table view:

```text
outputs/support_process_process_mock_dashboard.html
outputs/support_process_predictive_mock_dashboard.html
```

### Run the tests

```bash
python3 validate_fixtures.py
python3 -m unittest test_experiment.py
python3 run_all.py
```

### Test a real model

`run.py` can call any command that reads the prompt from stdin and prints a JSON state patch on stdout:

```bash
python3 run.py --mode llm --run-name my_model --llm-command "your-model-command"
```

It can also call OpenAI directly through environment variables only. Do not put keys in commands or files:

```bash
export OPENAI_API_KEY
export SUPPORT_PROCESS_REAL_MODEL_NAME=gpt-5.5
export SUPPORT_PROCESS_REAL_MODEL_REASONING_EFFORT=high
python3 run.py --mode real-model --run-name real_model
```

Or run Anthropic through the same provider interface:

```bash
export ANTHROPIC_API_KEY
export SUPPORT_PROCESS_REAL_MODEL_PROVIDER=anthropic
export SUPPORT_PROCESS_REAL_MODEL_NAME=claude-sonnet-4-6
python3 run.py --mode real-model --run-name real_model
```

To include that same `real_model` row in the full comparison, opt in explicitly:

```bash
export ANTHROPIC_API_KEY
export SUPPORT_PROCESS_REAL_MODEL_PROVIDER=anthropic
export SUPPORT_PROCESS_REAL_MODEL_NAME=claude-sonnet-4-6
export SUPPORT_PROCESS_REAL_MODEL_REASONING_EFFORT=high
export SUPPORT_PROCESS_RUN_REAL_MODEL=1
python3 run_all.py
```

If the key or model is missing, `run_all.py` does not fake a real-model result. It leaves the `real_model` row marked as not run.

The prompt pack is also written to:

```text
outputs/support_process_llm_prompts.jsonl
```


## Methods this is derived from

1. **LTS-style incremental state.** Listen to the stream, update compact state only when something support-relevant changes, and surface a sparse next step instead of re-summarizing the whole conversation.
2. **Support troubleshooting discipline.** Separate symptoms, facts, unknowns, candidate causes, ruled-out paths, and confirmed mechanisms.
3. **Gold trace evaluation.** Compare each turn against an expected process trace, not just the final answer.
4. **Premature-answer penalty.** A final cause before product/support evidence is an error, even if the same answer becomes correct later.
5. **Mock system context.** Use small structured facts to stand in for product logs, helpdesk records, billing state, delivery status, roles, groups, and entitlement checks.

## Why no voice

The paper that inspired this work is about voice agents. The transferable idea is not the microphone. It is semantic triggering plus incremental state.

For support, text is enough to test the core process first. Voice can come later as an input layer: ASR, diarization, interruptions, corrections, and latency. None of that fixes the central support problem: hidden mechanism evidence lives in product and support systems, not in the audio waveform.

So this starts with text on purpose.

## The honest claim

We make support AI auditable by showing whether it worked the case correctly, not just whether it eventually said the right answer.

That is the wedge. Not "another AI support agent." Not "predict root cause from hello." The useful thing here is a process trace you can inspect: facts, unknowns, branches, ruled-out paths, next check, and the exact moment a final cause became justified.

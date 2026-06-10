# AGENTS.md - real-time_support_Updated

## What this repo is

This is a text-first support-process evaluation lab. It is the corrected extension of `gititya/real-time_support`.

The old repo tested early specific root-cause prediction. That failed because early support turns usually contain symptoms, not mechanism. This repo tests whether an AI keeps a useful Live Support State as evidence arrives.

## Working rules

- Keep this repo small and runnable with the Python standard library.
- Do not add frameworks, package managers, TypeScript, or app scaffolding unless explicitly requested.
- Do not turn this into a customer-facing chatbot.
- Do not treat final root-cause accuracy as the only success metric.
- Preserve the distinction between process behavior and predictive behavior.
- A model should fail if it sets `final_cause` before product/support context provides mechanism evidence.

## Main commands

```bash
python3 validate_fixtures.py
python3 -m unittest test_experiment.py
python3 run_all.py
```

## File map

- `README.md` - human-facing thesis and usage.
- `AUDITABLE_SUPPORT_AI.md` - product idea and support-language explanation.
- `run.py` - replay runner, LLM command adapter, evaluator, report/dashboard renderer.
- `run_all.py` - complete experiment runner.
- `mock_llm.py` - process and predictive mock model behaviors.
- `validate_fixtures.py` - fixture validation.
- `test_experiment.py` - regression tests.
- `fixtures/` - support cases and expected process state.
- `outputs/` - generated experiment reports.

## Evaluation principle

The core question is not:

> Did the AI eventually say the right answer?

The core question is:

> Did the AI work the support case correctly as evidence arrived?

Track facts, unknowns, candidate branches, ruled-out paths, next checks, and final-cause timing.

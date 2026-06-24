# Support Process Experiment Summary

This is the end-to-end offline experiment for text-first LTS support-process behavior.

| run | cases | checks | pass_rate | final_cause_ok | premature_final_cause_turns | status |
| --- | --- | --- | --- | --- | --- | --- |
| deterministic | 12 | 318/318 | 100% | 12/12 | 0 | ran |
| process_mock | 12 | 318/318 | 100% | 12/12 | 0 | ran |
| predictive_mock | 12 | 275/318 | 86% | 12/12 | 29 | ran |
| real_model | - | - | - | - | - | not run; set SUPPORT_PROCESS_RUN_REAL_MODEL=1, SUPPORT_PROCESS_REAL_MODEL_NAME, and the provider API key |


## Interpretation

- `deterministic` is the reference state-machine baseline.
- `process_mock` simulates the intended LTS Think step: maintain state and wait for product/support context before final cause.
- `predictive_mock` simulates the old failure mode: early final-cause guesses from transcript symptoms.
- `real_model` is an opt-in provider run over the same fixtures; if no key/model is configured, no result is fabricated.

A useful model should look closer to `process_mock` than `predictive_mock`, especially on `premature_final_cause_turns`.
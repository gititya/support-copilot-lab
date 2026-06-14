# Support Process Experiment Summary

This is the end-to-end offline experiment for text-first LTS support-process behavior.

| run | cases | checks | pass_rate | final_cause_ok | premature_final_cause_turns | status |
| --- | --- | --- | --- | --- | --- | --- |
| deterministic | 6 | 108/108 | 100% | 6/6 | 0 | ran |
| process_mock | 6 | 108/108 | 100% | 6/6 | 0 | ran |
| predictive_mock | 6 | 94/108 | 87% | 6/6 | 12 | ran |
| real_model | 6 | 96/108 | 89% | 6/6 | 0 | ran |


## Interpretation

- `deterministic` is the reference state-machine baseline.
- `process_mock` simulates the intended LTS Think step: maintain state and wait for product/support context before final cause.
- `predictive_mock` simulates the old failure mode: early final-cause guesses from transcript symptoms.
- `real_model` is an opt-in provider run over the same fixtures; if no key/model is configured, no result is fabricated.

A useful model should look closer to `process_mock` than `predictive_mock`, especially on `premature_final_cause_turns`.
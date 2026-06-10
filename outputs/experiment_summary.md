# Support Process Experiment Summary

This is the end-to-end offline experiment for text-first LTS support-process behavior.

| run | cases | checks | pass_rate | final_cause_ok | premature_final_cause_turns |
| --- | --- | --- | --- | --- | --- |
| deterministic | 3 | 60/60 | 100% | 3/3 | 0 |
| process_mock | 3 | 60/60 | 100% | 3/3 | 0 |
| predictive_mock | 3 | 53/60 | 88% | 3/3 | 7 |


## Interpretation

- `deterministic` is the reference state-machine baseline.
- `process_mock` simulates the intended LTS Think step: maintain state and wait for product/support context before final cause.
- `predictive_mock` simulates the old failure mode: early final-cause guesses from transcript symptoms.

A useful model should look closer to `process_mock` than `predictive_mock`, especially on `premature_final_cause_turns`.
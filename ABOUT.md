# About

A text-first support-process eval lab.

This repo is the corrected version of [`gititya/real-time_support`](https://github.com/gititya/real-time_support). The first version tested whether an AI could predict the specific root cause from the opening turns of a support call. That failed because the opening turns had symptoms, not mechanism.

This version tests the thing support teams actually need: whether AI can work the case correctly as evidence arrives.

It tracks facts, unknowns, candidate branches, ruled-out paths, next checks, and final cause timing. A model can eventually get the right answer and still fail if it guessed before product/support evidence existed.

Run:

```bash
python3 run_all.py
```

Read:

```text
outputs/experiment_summary.md
```

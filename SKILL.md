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

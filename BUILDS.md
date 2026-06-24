---
status: "complete"
current_state: "Canonical finished B2B support-process proof-of-work with 12 accepted fixtures, level3 uncertainty cases, simulator, and committed benchmark evidence."
next_action: "Use as a reference artifact; only reopen if the support-process engine is needed by the Handoff Quality Gate."
things_to_know:
  - "This is the canonical continuation of the original real-time support experiment."
  - "The repo is intentionally closed around B2B support-process evaluation, not B2C, local-model tuning, or a broader UI rebuild."
  - "Real transcripts are customer data; do not commit them."
what_it_is: "Updated support replay and evaluation repo for testing support-process and local-model behavior."
read_next:
  - "README.md"
  - "SKILL.md"
  - "Roadmap.MD"
  - "prototype/model_eval.py"
  - "run.py"
agent_notes:
  - "This repo is complete as the B2B proof-of-work."
  - "Reuse the run.py stdin/stdout JSON patch seam if another repo imports the engine shape."
  - "Validate through consumer replay, not schema checks alone."
safe_first_action: "Run python3 validate_fixtures.py, python3 -m unittest test_experiment.py, and python3 run_all.py before trusting changes."
updated_at: "2026-06-25"
updated_by: "codex"
---

## Build inbox
Free-write feature ideas, follow-ups, and "do this next" notes here. Keep coding-agent implementation detail in `SKILL.md`.

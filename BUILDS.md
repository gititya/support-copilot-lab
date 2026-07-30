---
status: "shipped"
current_state: "The B2B support-process proof is shipped and pinned: accepted traces preserve facts, unknowns, branches, next checks, handoff, and evidence-timed final causes."
next_action: "No pending work for the shipped proof; any new model replay or product domain starts as new scope."
things_to_know:
  - "Roadmap source: /Users/aditya/Documents/Projects/support/Old_files/archived-docs/SUPPORT_MASTER_PLAN.md (archived)."
  - "M4 front door: /Users/aditya/Documents/Projects/support/customer-support-ai-os/FRONT_DOOR.md."
  - "M4 Flow 0 trace: /Users/aditya/Documents/Projects/support/customer-support-ai-os/outputs/flow0_H1.json."
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
updated_at: "2026-07-10"
updated_by: "codex"
---

## Build inbox
Free-write feature ideas, follow-ups, and "do this next" notes here. Keep coding-agent implementation detail in `SKILL.md`.

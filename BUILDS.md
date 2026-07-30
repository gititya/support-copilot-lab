---
status: "shipped"
current_state: "The active rep-side B2B product/proof is shipped and pinned: it helps a representative maintain facts, unknowns, branches, next checks, and evidence-timed resolution without premature engineering escalation."
next_action: "No pending build. Keep the product independently visible; any live-desk presentation integration must use its stable seam and starts as new scope."
things_to_know:
  - "Roadmap source: /Users/aditya/Documents/Projects/support/Old_files/archived-docs/SUPPORT_MASTER_PLAN.md (archived)."
  - "M4 front door: /Users/aditya/Documents/Projects/support/customer-support-ai-os/FRONT_DOOR.md."
  - "M4 Flow 0 trace: /Users/aditya/Documents/Projects/support/customer-support-ai-os/outputs/flow0_H1.json."
  - "This is the canonical continuation of the original real-time support experiment."
  - "The product boundary remains B2B rep-side case work; B2C, local-model tuning, and a broader UI rebuild stay outside it."
  - "Only the superseded early-root-cause premise and archived local-model/comparison branches are historical experiments."
  - "Real transcripts are customer data; do not commit them."
what_it_is: "Rep-side support copilot product/proof for evidence-timed case work, backed by a fixed replay and evaluation harness."
read_next:
  - "README.md"
  - "SKILL.md"
  - "Roadmap.MD"
  - "prototype/model_eval.py"
  - "run.py"
agent_notes:
  - "This repo is active as the independently visible B2B rep-side product/proof; the current shipped build has no pending work."
  - "Reuse the run.py stdin/stdout JSON patch seam if another repo imports the engine shape."
  - "Validate through consumer replay, not schema checks alone."
safe_first_action: "Run python3 validate_fixtures.py, python3 -m unittest test_experiment.py, and python3 run_all.py before trusting changes."
updated_at: "2026-07-30"
updated_by: "codex"
---

## Build inbox
Free-write feature ideas, follow-ups, and "do this next" notes here. Keep coding-agent implementation detail in `SKILL.md`.

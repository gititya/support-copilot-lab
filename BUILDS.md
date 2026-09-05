---
status: "in-progress"
current_state: "The public README now presents a fixture-driven offline support-process experiment with saved results. No support representative has used it."
next_action: "Review the public README and historical patch metadata, then decide whether the repository is ready to share."
things_to_know:
  - "The saved replay separates facts, unknowns, possible causes, ruled-out causes, next checks, and evidence-timed resolution."
  - "Evidence lives in outputs/experiment_summary.md and outputs/support_process_gpt55_benchmark_report.md."
  - "Three tracked patch archives contain email-like commit metadata and need owner review before public visibility."
what_it_is: "Offline support-process experiment for evidence-timed case work, backed by fixed replays and an evaluation harness."
read_next:
  - "README.md"
  - "SKILL.md"
  - "Roadmap.MD"
  - "prototype/model_eval.py"
  - "run.py"
agent_notes:
  - "Keep saved model output separate from deterministic and mock lanes."
  - "Do not describe the precomputed simulator as connected helpdesk input."
  - "Validate through the stored replay and named report files."
safe_first_action: "Read README.md and the two named saved reports before making a claim."
updated_at: "2026-09-04"
updated_by: "codex"
---

## Build inbox
Free-write feature ideas, follow-ups, and "do this next" notes here. Keep coding-agent implementation detail in `SKILL.md`.

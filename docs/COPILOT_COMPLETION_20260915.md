> Superseded assessment: the owner review invitation is withdrawn. These prepared cases establish workflow controls, not investigation ability. Read COPILOT_INVESTIGATION_CHALLENGE_20260915.md for the corrected check.

# Copilot bounded completion review — 15 September 2026

## Scope and result

Owner-authorized HCAI experiment closeout, not a general support platform. No Voice or Muesli edits. Owner usefulness review remains pending. Tier 3 remains the previously approved plain interface.

New findings preserve the current evidence and consumed-read list. Explicit corrections still retire the entire prepared snapshot; selective correction handling remains outside this pass. Exact repeated clarification wording stops with an honest unavailable recommendation; paraphrased repetition is still model-dependent. The model sees recent advice and must explain what a question changes. Handoff acceptance is a host-controlled stopping point, not delivery or recovery. Rep-owned recovery and closure remain separate.

## Verification

81 trial tests pass, including seven new completion regressions; 46 historical experiment tests pass; 12 fixture files validate. Live OpenAI Luna low runs are saved in outputs/cop1/bounded-completion-20260915.json and bounded-completion-unprompted-20260915.json. Each used 10 calls: seven workflow calls and three simple summary calls. The first run explicitly requested transfers; the second removed those requests. Both retained, not pooled into an accuracy claim. Browser checks exercised live advice, rep-confirmed success, explicit close, visible handoff draft and acceptance without delivery.

Final unprompted run: supported fix after one record read; diagnostic after one record read; following the negative diagnostic finding, handoff without repeating the check; missing-record case transferred after one record read. No questions were needed because these authored cases supplied the relevant facts. These runs do not establish quality when facts are vague or contradictory across a long conversation.

Recorded model waits in the unprompted run: fix 10.40 seconds across two calls; initial diagnostic 12.86 seconds across two calls; diagnostic-result response 7.73 seconds; missing-record transfer 8.58 seconds across two calls. These are sums of recorded provider request durations, not user-perceived latency benchmarks.

## Remaining weaknesses and interpretation

The simple summary comparator got the same currently observed facts. It was useful and much shorter. It was instructed to summarize, not offer actions: this is a qualitative comparison of interaction formats, not a fair test of model intelligence or proof of superiority over a well-prompted general assistant. No rep performance or workload measurement has happened.

The unprompted missing-record handoff says “why these records were excluded.” The evidence establishes absence, not exclusion. The draft otherwise keeps the cause unconfirmed, but this phrase is an unsupported assumption. It also appeared in browser verification. Preserve it for owner review. Do not quietly score this as flawless. Human review must be useful control, not routine correction of careless claims.

All three cases were authored for this completion exercise. Expected kinds are kept out of model inputs. They are development checks, not held-out research or customer data. Outcome success in automated checks is simulated rep input, not actual customer recovery.

## Reproduce and resume

Canonical repo: /Users/aditya/Documents/Projects/experiments/support-copilot-lab.
Run `python3 -m unittest discover -s trial -p 'test_*.py'`; `python3 validate_fixtures.py`; `python3 -m unittest test_experiment.py`.
Optional paid recheck: `python3 trial/check_completion.py` uses fictional cases only, the existing OpenAI Keychain entry, at most 16 calls and a $0.35 reservation based on the historical pinned price estimate. Rechecks write timestamped evidence. Do not run to chase a perfect score.
Start webpage with `portless copilot-lab /opt/homebrew/bin/python3 trial/web_walkthrough.py`. This Mac currently needs Homebrew Python because Apple developer tools require an unaccepted Xcode licence. Git status was unavailable for that reason; no licence accepted, no Git operations, no publication. Before editing, modified files were backed up under /private/tmp/copilot-bounded-originals-20260915.

Next: owner tries the three cases using the existing Obsidian walkthrough note. If useful, finish the experiment write-up with limits. If not, record a negative result or retain only useful summary/transfer behavior. Do not begin another architecture pass without a new decision.

# Copilot: changes from the three support examples

## What changed for the rep

Copilot advises the human rep privately. It does not speak to the customer. A cause can be supported while the customer's problem remains unresolved.

The former trial action called `resolve` meant “supported diagnosis and next step.” The current trial now calls it `suggest_fix`. It cannot close a case. An explicit rep outcome is separate from a model suggestion or text in the transcript. “Worked” records verified success and leaves the case open. The rep can then close it. “Did not work,” “not tried” and “unclear” keep it open. Feedback identifies the current suggestion; new case evidence or a different suggestion invalidates an older confirmation target.

Rejected feedback is recorded without losing the earlier investigation. Rep control cannot be combined with new product evidence. Closure makes no extra model calls, including in the eager timing test.

## Investigation advice

The editable [support rules](../trial/SUPPORT_RULES.md) are loaded into both model approaches. They capture the owner's decisions: reported scope is not confirmed scope; successful comparisons matter; check whether the same activity worked after a change; establish the pattern of missing/incomplete/delayed records; keep investigating independent unknowns while a check is pending; require mechanism evidence for a cause; follow supplied authority and ownership rather than assume engineering must take over.

The reviewed cases now offer questions about these distinctions. Offering a question does not guarantee the model will choose it at the best time. These are reviewed development cases, not unseen evaluation.

A handoff suggestion now prepares a local packet with current sourced observations, checks and their results, the model's stated unknowns and proposed request. Historical checks retain their original context; they must not be mistaken for current facts. The rep must review the proposed request and unknowns. No destination is invented and no packet is sent. This is not an integration with engineering or Desk.

## Actual model spot checks

Six calls on fictional, reviewed examples produced usable structured output. This is a behavioral spot check, not a new comparison score or evidence of rep time saved.

- Pending diagnostics: it asked whether other records were arriving and whether processing had finished.
- Old permissions without a causal link: it left the cause open. Its follow-up still asked broadly where access failed, although the workspace was already identified; that wording needs refinement.
- Logs connecting the denied attempt to old permissions: it cited that connection and suggested the approved refresh and retry, explicitly saying the outcome was unverified.
- Failed retry: it kept investigating rather than claiming success or presenting the same fix as new. Its follow-up was still broad.
- Specialist preparation: it included the missing interval, successful later records, completed processing, unavailable diagnostic log and unknown relevance of the change.
- Three reported users: it asked where the action failed first. This does not yet prove it will follow through on confirmed affected scope or successful comparisons.

All six passed structural validation; that does not mean every sentence or investigation choice was good. Raw prompts, responses and usage are in `outputs/cop1/owner-review-v4.json`. Estimated usage cost: $0.0042814. Later control-path fixes changed the runner and lifecycle hashes after these calls; the support policy is unchanged, and those code paths were verified offline afterwards.

## Verification and limits

40 current trial tests and 51 existing tests pass: 91 total. The added tests exercise suggested fixes, success without closure, failed/unclear/untried outcomes, explicit rep closure, stale confirmation, new evidence, malicious transcript/model status claims, mixed control/evidence rejection, closed timing paths and saved handoff checks. Scripted flow evidence is in `outputs/cop1/rep-feedback-v4-offline.json`; it is not an AI quality result.

The original v3 runner, cases and plan are preserved in `outputs/cop1/frozen-v3-inputs/`, matching the original hashes. Historical model outputs were not changed. The current CLI defaults to reviewed cases; use the frozen runner with its matching inputs to reproduce the old protocol. No Voice code, live app, customer-facing interface, package, deployment, commit or push changed.

The boundary is implemented in the text trial and callable rep-control code. There is no live call feed or rep interface for this yet. A host must supply rep controls through its trusted input channel; free-form transcript and retrieved data must never be promoted to controls. Cause checks remain authored-case checks, not a universal proof of causality. Prompt instructions do not mechanically guarantee semantic quality or prohibit every misleading phrase.

Next: a short rep-facing text walkthrough that lets Adi use these controls and judge whether the advice saves investigation effort. Keep the current examples as regression tests; use new cases for any later quality comparison.

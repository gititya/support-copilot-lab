When I tested with [Early Prediction](https://github.com/gititya/support-early-prediction-experiment) to find out if an AI can determine the root cause of the customer's complaint early into the call, I ended up realising that I was asking the right question. So, I wanted to test : **can AI help a human support rep decide what to do next, *as new information changes the investigation*?**

A customer saying “three people lost access after a migration” tells one where to begin, but a standard support call requires more information to diagnose. I would want to know who is confirmed affected, what they tried, and what happened. Copilot should help me find that out, then move towards a fix or a useful escalation.

## The experiment

I built two simulated support scenarios with the same opening complaint and basic account information. The case records are prepared, but the model does not receive the answer key or the ending.

It is not intended to replace a human rep, but to complement their efforts during a call. In this experiment, the rep submits each new customer update as text. Copilot uses those updates to request relevant product records and recommend the next step. Each session starts fresh; the underlying case facts are fixed.

1. **A fix works.** Failed requests used old access information, while current permissions allowed access. Copilot recommends an authorised refresh and asks the rep to check whether the affected people can now open the workspace. Recommending the fix does not close the case.

2. **The fix does not solve it.** New evidence shows that access succeeds, but the page still fails to load. Copilot changes its advice and prepares a specific engineering handoff: what failed, what was tried, which records support it and what engineering needs to inspect. It does not pretend to know the final cause.

The rep confirms the outcome, closes the case or accepts the handoff. Copilot does not contact the customer or send the escalation itself.

## What happened

My walkthrough showed the advice changing as I supplied more information, including moving from a proposed fix to an engineering investigation when the problem persisted. Separate checks exercised the close-case and accept-handoff controls.

Earlier versions kept asking questions without moving the case forward. The useful behaviour here is knowing when another question helps, when there is enough evidence to act, and when the next person needs to take over.

## What I took away

**AI should help the rep reason, while the rep owns the decision and confirms the result.** That is the human-centred AI idea I wanted to examine.

The work is inspired by LTS's distinction between maintaining an understanding and deciding when to offer help. This experiment uses submitted text; it does not reproduce that paper's voice system.

These two scenarios show the behaviour I wanted to examine. They do not establish that Copilot handles unfamiliar cases reliably or improves a rep's performance. That would require a broader, independent evaluation.

## Evaluation

[Support Evals](https://github.com/gititya/support-evals) reviews selected saved Copilot journeys, including whether recovery was confirmed and whether a handoff was only proposed or accepted. Copilot also has its own checks. Neither establishes that a real rep works faster or that every suggestion is useful.

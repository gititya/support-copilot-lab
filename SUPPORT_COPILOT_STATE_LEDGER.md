# Support Copilot State Ledger

This is the key for the live simulator headings. The simulator is meant to feel like a support copilot helping an agent work a case, not like a report card.

## Conversation

The customer-agent exchange shown up to the current turn.

This is what the support agent has heard so far. The copilot should not act as if it knows facts that have not appeared in the conversation or in product/support context.

## Copilot State

The working support view at the current turn.

This is not a final answer. It is the case state the copilot would keep beside the agent while evidence is still arriving.

## Known Facts

Facts the copilot can safely treat as established.

Examples:

- The affected users can sign in.
- The issue appeared after a migration.
- SCIM sync has completed.
- The workspace role is present.

Known facts should come from the transcript or from product/support context. They should not include guesses about why the issue happened.

## Still Unknown

Questions or checks that still need evidence.

Examples:

- Can the affected users sign in?
- Do affected users have the right workspace role?
- Is cached entitlement state still blocking access?

Unknowns are useful because they keep the copilot from overclaiming. A good support copilot keeps the remaining uncertainty visible instead of hiding it inside a confident-sounding answer.

## Possible Causes

Live explanations that are still plausible.

Examples:

- Login is blocked.
- The workspace role is missing.
- SCIM sync has not completed.
- Stale entitlement cache.

Possible causes are not final causes. They are branches to investigate. The copilot can use them to choose the next check, but it should not present one as the answer until evidence supports it.

## Ruled Out

Branches that the evidence has made unlikely or impossible.

Examples:

- Login is blocked gets ruled out once the customer confirms the users can sign in.
- SCIM sync delay gets ruled out once product context shows SCIM completed.
- Missing workspace role gets ruled out once product context shows the role is present.

Ruled-out causes matter because they show the copilot is narrowing the case instead of just collecting notes.

## Next Best Question, Check, Or Action

The single most useful next move for the support agent.

Examples:

- Ask whether the affected users can sign in.
- Check whether the affected users have workspace-level roles.
- Check entitlement cache status before naming a final cause.
- Refresh the entitlement cache and confirm workspace access works.

This is the most product-like part of the state. If this line is not useful, the copilot is not useful yet.

## Product And Support Context

System evidence that arrives during the case.

Examples:

- Admin context shows the workspace role is present.
- SCIM has completed.
- Entitlement service shows stale cache for affected users.

This is where the simulator tests the main thesis: support cases usually need product or support-system evidence before the final cause is justified.

## Final Outcome

The resolution or handoff state once evidence supports it.

Before enough evidence arrives, this should say the case is not ready for a final cause. After enough evidence arrives, it can name the supported outcome.

The copilot fails if it names a final outcome too early, even if the eventual answer turns out to be right.

## Raw Eval State

The underlying machine-readable state from the experiment harness.

This is useful for auditing whether the simulator is faithful to the root harness, but it is not the product experience. It should stay hidden by default.

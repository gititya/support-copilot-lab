# Auditable Support AI

> We make support AI auditable by showing whether it reasoned through the case correctly, not just whether it eventually said the right answer.

That sentence came from the failure of the first real-time support experiment.

The old test cared too much about the final answer. If the model eventually said the same root cause as the answer key, it looked good. But support does not work that way. Timing matters. Evidence matters. The path matters.

## The support version

Imagine a customer says:

> Three users lost access after migration.

A predictive system jumps to:

> This is probably missing workspace role inheritance.

That might become true later. But at that moment, it is not support reasoning. It is a guess.

A process system says:

```text
Known:
- three users affected
- access loss happened after migration

Unknown:
- can they sign in?
- did SCIM finish?
- do they have the right workspace role?
- is there a stale entitlement cache?

Candidate branches:
- login block
- missing workspace role
- SCIM sync delay
- stale entitlement cache

Next check:
- confirm whether the affected users can sign in
```

Then product/support context arrives:

```text
- users are in Migrated-CSM
- SCIM completed
- Migrated-CSM has no workspace role
```

Now the final cause is justified:

```text
missing_workspace_role_inheritance
```

## What auditable means

Auditable means a human can inspect the support path:

1. What did the AI know at this point?
2. What was still unknown?
3. What was it considering?
4. What did it rule out?
5. What evidence changed the state?
6. Did it ask the next useful question?
7. Did it claim final cause before the evidence existed?

That is different from normal answer grading.

Normal grading asks:

> Did the AI close with the right answer?

This asks:

> Did the AI work the ticket correctly?

## Why this matters

A support AI that guesses early can look impressive in demos. It can even be right sometimes. But in production, early unsupported certainty creates bad escalations, wasted troubleshooting, wrong customer messaging, and fragile automation.

The useful product layer is not just answer generation. It is process visibility:

```text
facts -> unknowns -> branches -> ruled-out paths -> next check -> evidence-backed final cause
```

That is the idea this repo tests.

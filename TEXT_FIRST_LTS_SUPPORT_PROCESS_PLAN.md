---
title: Text-First LTS Support Process Plan
project: support-voice
date: 2026-06-10
status: planning
purpose: Correct the project from early root-cause prediction to LTS-style incremental support process reasoning.
---

# Text-First LTS Support Process Plan

This note is the corrected direction for applying the LTS-VoiceAgent paper to support.

The useful idea from the paper is not "guess the final answer early." The useful idea is:

> Start thinking while the interaction is still unfolding, trigger deeper reasoning only when the stream adds meaningful information, and maintain state incrementally so the final output is better and faster.

For support, that means a live case-state assistant. It tracks what is known, what is unknown, what has been tried, what changed, which branches are still possible, and what the agent should check next.

It does not need to know the final root cause before the evidence exists.

Primary references:

- `VOICEAGENT_ARCHITECTURE_NOTE.md`
- `FINDINGS_phase1.md`
- `PRD_1st.md`
- `initial_research/LTS-VoiceAgent- A Listen-Think-Speak Framework for Efficient Streaming Voice Interaction via Semantic Triggering and Incremental Reasoning.pdf`

## What Went Wrong

The original implementation turned a process architecture into a predictive test.

The test asked:

> From the first 6 turns, can the model name the specific final root cause?

That is not the same as LTS-style process reasoning.

LTS asks:

> As partial information arrives, can the system decide when to think, update its internal state, handle corrections, and be ready with useful output when enough context exists?

The predictive harness was a valid kill test for the strongest possible claim, but it was the wrong implementation of the paper's support-process philosophy.

### Support Example

Customer says:

> "Three users lost access after our migration yesterday. They can sign in, but they cannot open the new workspace."

The predictive version tries to answer:

> "The root cause is SCIM sync delay."

or:

> "The root cause is stale entitlement cache."

or:

> "The root cause is missing workspace role inheritance."

That fails because all of those are still plausible from the opening turns. The transcript has the symptom, but not the mechanism.

The process version should instead produce a live state:

```text
Known facts
- Three users are affected.
- Issue started after migration.
- Sign-in works.
- Workspace access fails.

Current branch
- Authorization / workspace access after migration.

Open unknowns
- Do affected users show a workspace-level role?
- Are they in the migrated group?
- Did SCIM sync finish?
- Is there a direct assignment conflict?
- Did role inheritance carry over during migration?

Candidate causes
- Missing migrated group role.
- SCIM or entitlement sync delay.
- Stale entitlement cache.
- Inherited role conflict.
- SSO group mismatch.

Next useful check
- Ask the admin to verify whether the affected users show the expected workspace role in the admin panel.
```

That is useful before the final answer is known.

## Why The Predictive Harness Failed

The result in `FINDINGS_phase1.md` was not a model-quality failure.

It failed because the early transcript usually did not contain the specific mechanism.

Important findings:

- The first 6 turns had symptoms, category, and context, but not enough root-cause evidence.
- Full-transcript accuracy was high, so the annotator and judge worked when the evidence existed.
- The `gpt-5.5` frontier-authored run dropped early specific root-cause accuracy to 2%.
- Migration, the earlier hopeful narrow domain, fell to 0% early accuracy on the frontier-authored run.
- Early escalation prediction also failed by firing on nearly every call, giving base-rate precision.

So the key lesson is:

> Transcript-only early root-cause prediction asks the model to infer facts that are not yet present.

That does not invalidate LTS. It invalidates the stronger product assumption that early conversation fragments are enough to name the hidden support mechanism.

## Corrected Product Shape

Build a text-first support-process prototype.

The prototype should answer:

> Can incremental support-state tracking beat naive transcript summarization for technical B2B support cases?

It should not answer:

> Can the model guess the final root cause from the first few turns?

The first useful product is a live case-state assistant:

```text
Transcript replay
        +
Mock product/support context
        |
        v
Support event trigger
        |
        v
Live Support State
        |
        v
State patch + reconciler
        |
        v
Nudge gate
        |
        +-----------------------+
        |                       |
        v                       v
Agent panel             Handoff/post-call record
```

The assistant should help the agent investigate, not pretend to know.

## Product/Support Context Is Required

The text-first prototype should not be transcript-only.

Transcript-only can prove the event loop and state model, but it is not enough to make the product valuable. A support transcript usually contains symptoms. The actual mechanism often lives in product and support systems.

For the side-project prototype, "connect to systems" means mock JSON context first, not real integrations.

Minimum mock systems:

- account state
- users and roles
- workspace memberships
- IdP or SSO group state
- SCIM or entitlement sync status
- migration/job events
- audit-log changes
- prior ticket snippets
- known incident or deploy notes when relevant

This changes the assistant from:

> "The customer says three users lost access after migration. Ask whether they have workspace roles."

to:

> "The users can authenticate, but their migrated group has no workspace role attached. Check whether role inheritance was skipped during migration."

That is the product wedge.

The prototype should support two modes, but only one is product-relevant:

| Mode | Purpose | Product value |
|---|---|---|
| Transcript-only replay | Test event extraction, state updates, corrections, and nudge discipline | Low; proves plumbing and process shape |
| Transcript + mock systems | Test support investigation using conversation plus operational evidence | High; proves the actual diagnostic assistant |

Do not evaluate root-cause quality from transcript-only replay. Evaluate root-cause quality only when the mechanism appears in transcript or mock system context.

## Architecture To Reuse

Reuse the existing shape in `VOICEAGENT_ARCHITECTURE_NOTE.md`. Do not invent a new architecture unless implementation proves the existing objects are too heavy.

### Utterance

Represents a finalized transcript turn.

For text-first replay, all utterances can be clean and pre-diarized. Keep the fields that later matter for voice, such as speaker, sequence, timestamp, and optional confidence placeholders.

### Event

Represents a meaningful support event extracted from an utterance or product context.

Initial event types should stay close to the existing architecture:

- customer symptom
- affected scope
- recent change
- entity mention
- agent question
- troubleshooting instruction
- step outcome
- scope correction
- repeated failure candidate
- repeated loop candidate
- escalation marker
- policy or billing constraint
- workaround acceptance
- unresolved objection

Rules can create candidate events. They should not directly promote diagnoses.

### Live Interaction State

This is the primary product object.

It should include:

- active facts
- superseded facts
- unknowns
- steps attempted
- outcomes
- active hypotheses
- ruled-out or weakened hypotheses
- evidence for and against each hypothesis
- current investigation status
- next verification question
- nudge history
- retraction history

The model updates this state. The UI reads from this state. The UI should not read directly from raw model output.

### State Patch

The slow reasoner should return patches, not full rewrites.

Patch output should include:

- based-on state version
- covered event sequences
- fact patches
- unknown patches
- step patches
- hypothesis patches
- resolution-status patch
- nudge candidates
- nudge retractions

This preserves the LTS idea of incremental state instead of repeated full summarization.

### Semantic Batcher

The batcher decides when slow reasoning is worth running.

Trigger slow reasoning when:

- a symptom plus affected scope appears
- a correction changes an active fact
- a troubleshooting result arrives
- a repeated failure or loop appears
- product/support context adds relevant evidence
- enough meaningful events accumulated since the last update

Suppress slow reasoning when:

- only filler or social text changed
- a turn repeats already-known information
- no operational state changed
- the event was already processed

### Slow State Updater

The slow updater is the "Think" part of support LTS.

It receives:

- current Live Interaction State
- new event batch
- relevant transcript window
- mock product/support context
- narrow support playbook

It returns a state patch.

It must be allowed to say:

> Root cause is not identifiable yet.

That is a correct process state, not a failure.

### Nudge Gate

The nudge gate decides what the agent actually sees.

Show only sparse, concrete, process-useful output:

- next verification question
- branch newly ruled out
- correction that changes scope
- repeated failed step
- escalation/handoff warning
- handoff packet readiness

Do not surface every hypothesis update.

Keep the existing nudge budget:

- average max: 1 visible nudge per 90 seconds
- hard cap: 5 visible nudges per normal call

### Post-Call Record

At call end, freeze the final Live Interaction State.

The post-call record should include:

- active and superseded facts
- hypothesis history
- troubleshooting timeline
- attempted steps and outcomes
- visible nudges and retractions
- unresolved unknowns
- likely repeat-contact or handoff risk
- evidence event IDs for major claims

This should be a structured operational record, not a transcript summary.

## Text-First Prototype

Start with text. Do not build voice yet.

Inputs:

- replayed transcript turns
- mock account state
- mock user/role state
- mock auth or entitlement logs
- mock migration/job events
- prior ticket snippets if useful

The mock system context is important because support root causes usually live outside the transcript.

Transcript says:

> "Three users lost access after migration."

System context can show:

```text
Users authenticate successfully.
Affected users are in group Migrated-CSM.
Group Migrated-CSM has no workspace role attached.
SCIM sync completed successfully.
Migration event: group imported, role inheritance skipped.
```

Now the assistant can reason over evidence:

> "This is not a login failure. Authentication works. The migrated group has no workspace role. Next check: confirm whether Migrated-CSM should inherit Workspace Member."

That is stronger than guessing from transcript.

## Evaluation

Replace early final-answer scoring with process-state scoring.

Each replay fixture should have expected labels by turn:

- facts known so far
- facts not yet knowable
- open unknowns
- reasonable candidate branches
- unreasonable branches
- attempted steps
- ruled-out branches
- expected next check
- expected handoff contents

Score the assistant on:

- fact capture accuracy
- hallucinated fact rate
- unknown tracking
- attempted-step tracking
- branch coverage
- branch over-promotion
- quality of next verification question
- correction handling
- repeated-step detection
- nudge precision
- handoff usefulness

Root cause can still be scored, but only when the evidence has appeared in transcript or system context.

## Success Criteria

The text-first prototype succeeds if:

- important facts are captured correctly
- unknowns remain explicit
- attempted steps and outcomes are preserved
- active hypotheses are ranked without false certainty
- contradicted branches are weakened or ruled out
- the next check helps disambiguate real branches
- nudges stay sparse
- retractions work after corrections
- handoff is useful at any point in the call

The prototype fails if:

- it guesses root cause early without evidence
- it surfaces noisy hypothesis churn
- it repeats steps the agent already tried
- it loses corrections or superseded facts
- the post-call record is just a summary

## Build Order For Later

When implementation resumes, build in this order:

1. Create 3-5 text replay fixtures with matching mock product/support context.
2. Define expected process labels for each fixture.
3. Implement replayed utterance ingestion.
4. Implement candidate event extraction.
5. Implement Live Interaction State and state patches.
6. Implement semantic batching.
7. Implement slow state updater over state plus events plus mock context.
8. Implement reconciler and correction handling.
9. Implement nudge gate.
10. Implement a minimal panel or console view.
11. Implement post-call record generation.
12. Run process-state evaluation before adding voice.

Do not build live STT, telephony, or diarization until the text process loop is useful.

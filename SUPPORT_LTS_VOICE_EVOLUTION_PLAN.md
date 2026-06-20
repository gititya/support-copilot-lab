---
title: Support LTS Voice Evolution Plan
project: support-voice
date: 2026-06-10
status: planning
purpose: Define how the text-first support-process prototype can evolve into voice while staying true to LTS-VoiceAgent.
---

# Support LTS Voice Evolution Plan

This note explains how the corrected support-process architecture can evolve into voice without losing the core LTS idea.

The short answer:

> Build text-first. Add voice later as an input adapter and latency stress test.

That is faithful to the LTS-VoiceAgent paper because the paper's reasoning loop operates over the ASR text stream. Voice matters for streaming, latency, interruptions, diarization, and prosody. It does not magically reveal hidden product root causes.

Primary references:

- `VOICEAGENT_ARCHITECTURE_NOTE.md`
- `FINDINGS_phase1.md`
- `PRD_1st.md`
- `initial_research/LTS-VoiceAgent- A Listen-Think-Speak Framework for Efficient Streaming Voice Interaction via Semantic Triggering and Incremental Reasoning.pdf`

## What Stays True To The PDF

The paper's useful structure is:

```text
Audio stream
        |
        v
ASR text stream
        |
        v
Dynamic semantic trigger
        |
        v
Thinker updates state
        |
        v
Speaker responds quickly
```

For support, the equivalent is:

```text
Support stream
        |
        v
Transcript + product/support events
        |
        v
Support semantic trigger
        |
        v
Thinker updates Live Support State
        |
        v
Agent panel shows sparse nudge or handoff state
```

The transferable idea is incremental reasoning over a stream.

The non-transferable part is customer-facing voice response. The support copilot sits beside a human agent. It should not answer the customer directly in the first prototype.

## Support Mapping

Use this mapping when reading the paper:

| LTS paper concept | Support equivalent |
|---|---|
| Listen | Receive transcript turns, audio-derived events, product events, account/log context |
| Think | Update facts, unknowns, hypotheses, attempted steps, contradictions, next checks |
| Speak | Show sparse internal nudge, next check, retraction, or handoff packet |
| Dynamic Semantic Trigger | Run slow support reasoning only when meaningful operational information arrives |
| Thinker state | Live Support State |
| Speaker | Agent-facing panel / nudge queue, not customer-facing TTS |
| Pause-and-repair | Handle self-corrections, interrupted explanations, speaker overlap, and changed scope |
| Latency metrics | Time from support-relevant event to state update or visible nudge |

So the support version is not less faithful because it starts with text. It is closer to the paper's actual reasoning substrate: streaming text after speech is converted.

## Why Text Comes First

Text-first removes the noisy plumbing while preserving the core experiment.

The core experiment is:

> Can semantic triggering plus incremental state maintenance make a support investigation cleaner while the case unfolds?

Voice is not needed to answer that first.

Starting with voice would add:

- ASR errors
- interim transcript churn
- speaker attribution errors
- overlapping speech
- telephony setup
- recording consent
- streaming latency

Those are real problems, but they are not the first proof.

The first proof is whether the Live Support State is useful when the input stream is already clean.

## System Context Comes Before Voice

For support, the critical upgrade is not voice. The critical upgrade is adding product/support system context.

Voice changes the input stream. System context changes what the assistant can actually know.

The evolution order should be:

```text
Transcript-only replay
        |
        v
Transcript + mock product/support systems
        |
        v
ASR-like text imperfections
        |
        v
Recorded audio through ASR
        |
        v
Live STT / diarization
```

Do not jump from transcript-only directly to voice. That would test audio plumbing before testing the real support value.

The text-first prototype should include mock versions of:

- user and role state
- workspace membership
- IdP/SSO group state
- entitlement or SCIM sync state
- migration/job logs
- audit-log changes
- prior tickets
- incident/deploy notes

This keeps the prototype true to support reality: the transcript gives the symptom, while system context gives the mechanism.

## Voice Evolution Path

### Phase 1: Transcript Replay Only

Use clean support transcripts as a live stream.

Input:

- speaker-labeled transcript turns
- simulated timestamps
- mock account/product/support context

Goal:

- prove the process loop
- validate event extraction
- validate Live Support State
- validate semantic batching
- validate sparse nudge output
- validate handoff/post-call record

Do not include live audio.

Success means the system helps the agent investigate without guessing the final cause too early.

### Phase 2: Simulated ASR Imperfections In Text

Add controlled text noise before real audio.

Simulate:

- missing punctuation
- partial words
- corrected phrases
- repeated phrases
- filler text
- product-name transcription errors
- delayed finalization of a turn
- speaker label uncertainty

Goal:

- test whether the state updater handles messy transcript input
- test correction-aware state
- test stale patch rejection and retractions
- test that high-impact nudges are suppressed when transcript confidence is weak

This phase is still text-first, but it starts preparing for voice.

### Phase 3: Recorded Audio Through ASR

Use recorded calls or scripted audio and send them through an ASR provider.

Input:

- recorded audio
- ASR transcript
- diarization output if available
- ASR confidence if available
- same mock support/product context

Goal:

- compare clean transcript replay vs ASR-derived transcript replay
- measure degradation from transcription errors
- identify domain terms ASR gets wrong
- test whether product names, roles, plan names, and workspace names need normalization

Do not build live agent UI yet. This phase is still replay and analysis.

### Phase 4: Live STT And Diarization

Only after replay works, connect live STT.

Input:

- live or simulated live microphone/audio stream
- interim ASR chunks
- finalized ASR utterances
- diarization/speaker attribution
- timestamps

Goal:

- test real streaming latency
- test interim text churn
- test speaker overlap
- test turn finalization
- test whether semantic batching runs at the right time
- test whether nudges arrive while still useful

Success here is not root-cause accuracy. Success is timely, stable support-state updates.

### Phase 5: Optional Prosody For Escalation And Trust

Prosody is optional and narrow.

Use it only for:

- escalation risk
- frustration markers
- customer confidence shifts
- urgency or stress
- handoff priority

Do not use prosody to infer technical root cause.

Prosody may tell you the customer is upset before the words make it explicit. It will not tell you that the root cause is an archived-team export filter or missing OAuth write scope.

## What Voice May Improve

Voice can improve or stress-test:

- latency realism
- interruption handling
- self-correction handling
- overlap handling
- hesitation handling
- escalation/frustration cues
- when to trigger reasoning before a full turn ends
- whether a nudge arrives while the agent can still use it

This is directly related to the LTS paper.

The paper is about avoiding the failure mode where systems wait too long or reason at the wrong time. Voice makes that timing problem real.

## What Voice Will Not Solve

Voice will not solve:

- hidden product root causes
- missing system evidence
- transcript-only diagnostic ambiguity
- lack of account/admin context
- lack of logs
- lack of product-state access
- bad process labels
- noisy nudge policy

If the opening support conversation does not contain the mechanism, audio will not create it.

For example:

Transcript:

> "Three users lost access after migration. They can sign in but cannot open the workspace."

Audio might add:

```text
Customer sounds frustrated.
Customer pauses before saying migration.
Customer interrupts the agent.
```

That may help escalation handling.

It does not reveal whether the cause is:

- SCIM sync delay
- stale entitlement cache
- missing group role
- inherited role conflict
- disabled role mapping

Those mechanisms usually require product/support context.

## Where Root-Cause Accuracy Can Improve

Root-cause accuracy should improve when the system gets operational evidence, not when it gets audio.

Add context like:

- user roles
- workspace memberships
- IdP/SSO group state
- SCIM sync status
- entitlement cache state
- migration job logs
- audit log changes
- prior tickets
- admin configuration
- recent deploys or incidents

Then the system can move from:

> "Ask whether these users have workspace roles."

to:

> "Authentication works. The affected users are in Migrated-CSM. That group has no workspace role after migration. Check whether role inheritance was skipped."

That is the valuable support product.

Voice is useful for interaction timing. System context is useful for diagnosis.

## Voice-Ready Architecture Constraint

Even in the text-first prototype, keep the interfaces voice-ready.

Utterances should preserve:

- sequence
- speaker
- start and end timestamp fields
- finalized text
- raw text if available
- cleaned text if available
- speaker confidence placeholder
- ASR confidence placeholder

Events should preserve:

- source utterance ID
- source type
- event sequence
- event time
- whether slow validation is needed

State patches should preserve:

- state version
- covered event sequences
- source event IDs
- stale patch handling
- retractions

This keeps the later voice adapter from forcing a rewrite.

## Voice Metrics

When voice is added, measure process and latency, not just accuracy.

Metrics:

- time from utterance finalization to event creation
- time from support-relevant event to state patch
- time from support-relevant event to visible nudge
- slow reasoner calls per call
- suppressed trigger count
- repeated event suppression
- stale patch rejection count
- correction handling accuracy
- nudge count
- nudge retraction count
- handoff completeness at arbitrary stop points
- ASR-caused state errors
- speaker-attribution-caused state errors

Root-cause accuracy remains a later metric and should be scored only after enough transcript or system evidence exists.

## Build Order For Later

Do this after the text-first process prototype is useful:

1. Add ASR-like text noise to existing replay fixtures.
2. Add `raw_text`, `cleaned_text`, `asr_confidence`, and `speaker_confidence` fields where missing.
3. Add suppression rules for low-confidence or interim text.
4. Add correction/retraction test cases.
5. Run recorded audio through ASR and compare against clean transcript output.
6. Add domain term normalization for product names, roles, plans, and workspace terms.
7. Add live STT only after recorded ASR replay is stable.
8. Add prosody only for escalation/trust experiments, not root-cause diagnosis.

## Non-Goals

Do not build these in the side-project prototype:

- customer-facing voice agent
- TTS response generation
- autonomous support resolution
- literal dual-LLM Thinker/Speaker orchestration
- learned semantic trigger
- broad contact-center platform
- generic sentiment dashboard
- live telephony before replay works

The support version should remain:

> A process-oriented live case-state assistant for technical support.

Voice can make it more realistic later. It should not change the product's core job.

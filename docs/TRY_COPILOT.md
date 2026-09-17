# Try Copilot as the rep

Open `Start Copilot Walkthrough.command` from this repo. It opens Terminal. Choose 1 for workspace access or 2 for missing integration records.

This is a fictional case with newly generated AI advice. It is not a live customer call, a connected product or a benchmark. Notes go to OpenAI and are saved locally; use fictional details. The existing OpenAI credential is loaded from the environment or the Mac support-experiment keychain entry. No key is written to a trace. No installation is required.

## First walkthrough

1. Read the customer update and type `advice`. Copilot privately suggests what you should check or ask. It can read the fictional records currently available, but it never supplies a scripted customer answer to its own question.
2. To answer its pending question about the same affected people or records, type `answer ` followed by your answer. If you are correcting the scope or adding a different problem, type the new information directly. This records your update without making a model call. Type `advice` when you want new advice.
3. Type `next` to advance to the next prepared customer/product update. This is an explicit fictional snapshot, not a real lookup. Type `advice` again.
4. Once a fix is suggested, use `failed`, `unsure` or `untried` to keep the case open, or `worked` to verify success. Only then can `close` close it. `worked` alone does not close. For this practice case you are simulating the customer's outcome.
5. Type `quit` whenever you want. The terminal prints the local evidence file it saved.

Each session permits at most 30 model calls, and each advice request at most five product reads/model steps. No model retry runs automatically. The chosen local budget guard is $0.50 per session; that is a conservative request reservation, not a promise about invoices or a revival of the owner's old overnight ceiling. Success/closure and note entry do not call the model.

## What to judge

Does the advice help you choose the next useful question or check? Does it use what you already know? Does it revise the investigation when you correct it? When a retry fails, does it help you continue rather than repeat the same suggestion?

## Boundaries

The walkthrough uses the full observed history for rep notes, rather than claiming the compact-state comparison has already won. It uses the current support rules and rep-owned progress controls. Explicit `answer` input tells the host that the affected scope is unchanged, so it preserves the existing records and marks the answer as a rep report. Use a plain note for corrections. New custom notes conservatively retire the previous prepared facts and records because their scope may no longer apply. They remain in history as old context. To supply new findings, type them as a rep report; `next` explicitly loads the next prepared snapshot. There is no free-form product lookup.

Structured validation rejects invented fact citations, unlisted actions, model-written closure fields and cause claims citing only a report. Requiring product evidence does not prove a correct causal connection. There is no hidden expected answer used to approve live advice. The rep must review explanations; the model can still reason or phrase things badly. The allowed source/question/cause menus remain limited to this lab.

Handoff advice is private and local; nothing is delivered. The saved trace includes observed inputs, checks, actual model output, errors, current outcome and source hashes. Stop/restart creates a separate practice session; resuming a saved session is not implemented.

## Verified terminal run

A real-model fictional access walkthrough reached: investigation → permission/authority question → explicit rep answer → suggested fix → simulated rep success → separate rep closure. Saved trace: `outputs/walkthrough/f2ea103e-536d-4ebd-9649-d76f27967242.json`. The rep inputs in this check were automated fictional inputs, not an owner trial or actual customer recovery. Two earlier attempts are retained: one exposed missing source-revision information, and one correctly refused closure before the rep answered the authority question. All are retained under outputs/walkthrough.

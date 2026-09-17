# Try the two Copilot investigations

From the repository, run `portless copilot-lab python3 trial/web_walkthrough.py`, then open http://copilot-lab.localhost:1355/. Keep the server running.

1. Choose **Investigate and resolve** or **Investigate and escalate**, then click **Get advice**.
2. Expand **Customer facts for this practice**. Use those simulated observations to answer the question in your own words. The section is for you; its contents are not sent automatically.
3. In the resolution scenario, report success with **The original activity works**, then **Close case**.
4. In the escalation scenario, record that the fix did not work, then submit the changed symptom and retry IDs as a **New finding**. Review the engineering request and use **Accept handoff** if appropriate.

The scenarios use simulated support data with real model responses. Initial model information contains the complaint and account details; matching product records become accessible after the rep supplies request IDs, and their contents arrive only on model lookup. Your submitted notes go to OpenAI and are saved locally. Handoffs remain unsent drafts.

A new finding preserves existing evidence. A correction retires the old scope. Confirmation and closure are explicit controls; typing that recovery occurred does not press them for you. Reload preserves an in-memory browser session; server restart does not restore it from disk. The model-call budget is shared across scenario switches.

Tier 3 remains the owner-approved plain interface. No redesign is part of the experiment closeout.

## Current evidence

86 trial software checks passed at implementation. Both complete paths were exercised through real model session checks and browser controls. The owner subsequently explored reported recovery followed by a changed symptom and engineering proposal in one continuing case. That owner session did not use explicit terminal controls. See [the owner review](OWNER_WALKTHROUGH_20260916.md) and [README](../README.md) for the method and limits. No repeated owner test is needed for the agreed bounded experiment.

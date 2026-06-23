#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import FIXTURE_DIR, OUTPUT_DIR, ensure_output_dir, esc
from run import run_fixture

SIMULATOR_PATH = OUTPUT_DIR / "support_live_simulator.html"
CASE_ID = "level2_conflicting_migration_context"

FACT_TEXT = {
    "affected_scope:three_users": "Three users are affected.",
    "app_entitlement_plan:starter": "The app still shows the Starter entitlement.",
    "auth:works": "The affected users can sign in.",
    "billing_refresh:pending": "The billing entitlement refresh is still pending.",
    "correction:login_works": "The customer corrected the first report: login works.",
    "domain_policy:dmarc_reject": "The recipient domain rejected the message by DMARC policy.",
    "email_delivery:suppressed": "Email delivery was suppressed.",
    "entitlement_cache:stale": "The entitlement cache is stale for the affected users.",
    "flow:admin_invite": "This is an admin invite flow.",
    "group_membership:Migrated-CSM": "The affected users are in the Migrated-CSM group.",
    "invite_status:created": "The invite exists in the admin system.",
    "invoice_plan:pro": "The invoice shows the Pro plan.",
    "recent_change:migration": "The issue appeared after a migration.",
    "recent_change:upgrade": "The issue appeared after an upgrade.",
    "reported_issue:login": "The customer initially described the issue as login failure.",
    "scim_sync:complete": "SCIM sync has completed.",
    "surface:billing_plan": "The visible issue is on the billing page.",
    "surface:workspace_access": "The visible issue is workspace access.",
    "symptom:invite_email_not_received": "The invite email is not arriving.",
    "symptom:workspace_access_loss": "The customer reports workspace access loss.",
    "symptom:wrong_plan_shown": "The customer sees the wrong plan.",
    "workspace_role_missing:Migrated-CSM": "Migrated-CSM is missing the workspace role.",
    "workspace_role:present": "The workspace role is present.",
}

UNKNOWN_TEXT = {
    "actual_surface": "Which product surface is actually failing?",
    "auth_status": "Can the affected users sign in?",
    "billing_entitlement_status": "Has the billing entitlement refresh completed?",
    "cache_status": "Is cached entitlement state still blocking access?",
    "email_delivery_status": "Did the invite email actually reach the recipient?",
    "invite_created": "Was the invite created successfully?",
    "workspace_role_assignment": "Do affected users have the right workspace role?",
}

CAUSE_TEXT = {
    "billing_entitlement_refresh_pending": "billing entitlement refresh is still pending",
    "domain_policy_rejection": "recipient-domain policy is rejecting the email",
    "email_delivery_suppressed": "email delivery is suppressed",
    "invite_not_created": "the invite was not created",
    "invoice_app_mismatch": "invoice and app entitlement do not match",
    "login_block": "login is blocked",
    "login_failure": "login is failing",
    "missing_workspace_role": "the workspace role is missing",
    "missing_workspace_role_inheritance": "the migrated group did not inherit the workspace role",
    "scim_sync_delay": "SCIM sync has not completed",
    "stale_entitlement_cache": "stale entitlement cache",
    "upstream_service_incident": "an upstream service issue",
}

ROUTE_STAGES = [
    "Intake",
    "Clarify issue",
    "Check context",
    "Narrow cause",
    "Resolve or hand off",
]


def load_fixture(case_id: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{case_id}.json"
    if not path.exists():
        raise SystemExit(f"Missing fixture: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def readable_label(label: str) -> str:
    if label in FACT_TEXT:
        return FACT_TEXT[label]
    if label in UNKNOWN_TEXT:
        return UNKNOWN_TEXT[label]
    if label in CAUSE_TEXT:
        return CAUSE_TEXT[label]
    return label.replace("_", " ").replace(":", " ")


def translate_list(values: list[str]) -> list[str]:
    return [readable_label(value) for value in values]


def context_summary(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for event in events:
        summaries.append({
            "description": event.get("description", ""),
            "facts": translate_list(event.get("facts", [])),
            "relevant": event.get("relevant", True),
        })
    return summaries


def final_outcome(state: dict[str, Any]) -> str:
    cause = state.get("final_cause", "")
    if not cause:
        return "Not ready yet. The copilot should keep investigating instead of naming a final cause."
    return f"Evidence now supports the final outcome: {readable_label(cause)}."


def state_for_display(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "known_facts": translate_list(state.get("facts", [])),
        "still_unknown": translate_list(state.get("unknowns", [])),
        "possible_causes": translate_list(state.get("candidate_branches", [])),
        "ruled_out": translate_list(state.get("ruled_out_branches", [])),
        "next_best_action": state.get("next_check", ""),
        "final_outcome": final_outcome(state),
        "raw": state,
    }


def route_stage(turn: dict[str, Any], state: dict[str, Any], context_events: list[dict[str, Any]]) -> str:
    turn_number = int(turn.get("turn", 0))
    if state.get("final_cause"):
        return "Resolve or hand off"
    if context_events:
        return "Check context"
    if turn_number >= 4:
        return "Narrow cause"
    if turn_number >= 2:
        return "Clarify issue"
    return "Intake"


def handoff_readiness(state: dict[str, Any]) -> dict[str, Any]:
    facts = state.get("facts", [])
    unknowns = state.get("unknowns", [])
    ruled_out = state.get("ruled_out_branches", [])
    next_check = state.get("next_check", "")
    final_cause = state.get("final_cause", "")
    issue_clear = any(fact.startswith("symptom:") or fact.startswith("surface:") for fact in facts)
    checks = [
        {
            "label": "Customer issue is clear",
            "ready": issue_clear,
            "detail": "The handoff names the customer-visible problem." if issue_clear else "Keep clarifying the customer-visible problem.",
        },
        {
            "label": "Known facts are captured",
            "ready": bool(facts),
            "detail": "The next owner can see the facts gathered so far." if facts else "Capture at least one durable fact before handoff.",
        },
        {
            "label": "Open questions are visible",
            "ready": bool(unknowns) or bool(final_cause),
            "detail": "Remaining uncertainty is visible." if unknowns else "No blocking unknowns remain.",
        },
        {
            "label": "Ruled-out paths are preserved",
            "ready": bool(ruled_out),
            "detail": "The next owner can avoid rechecking paths already ruled out." if ruled_out else "Nothing has been ruled out yet.",
        },
        {
            "label": "Next action is specific",
            "ready": bool(next_check),
            "detail": next_check or "Add the next best check before handing off.",
        },
        {
            "label": "Final cause is evidence-supported",
            "ready": bool(final_cause and state.get("root_cause_evidence_seen")) or not final_cause,
            "detail": "Final cause is supported by product context." if final_cause else "No final cause is included yet.",
        },
    ]
    ready_count = sum(1 for check in checks if check["ready"])
    if final_cause and ready_count == len(checks):
        status = "Ready to close or hand off with supported outcome."
    elif not ruled_out:
        status = "Not ready for handoff yet."
    elif ready_count >= 4:
        status = "Usable if the case must move, but keep unresolved checks attached."
    else:
        status = "Not ready for handoff yet."
    return {
        "status": status,
        "ready_count": ready_count,
        "total": len(checks),
        "checks": checks,
    }


def evidence_events_for_turn(
    item: dict[str, Any],
    previous_state: dict[str, Any] | None,
) -> list[dict[str, str]]:
    turn = item["turn"]
    state = item["state"]
    events = [{
        "kind": "Conversation",
        "title": f"Turn {turn.get('turn')}: {turn.get('speaker', 'speaker').title()} update",
        "body": turn.get("text", ""),
    }]
    for context in item.get("context_applied", []):
        if context.get("relevant", True):
            body = context.get("description", "Product or support context arrived.")
        else:
            body = context.get("description", "Context arrived but was not relevant to this case.")
        events.append({
            "kind": "Product context",
            "title": f"After turn {turn.get('turn')}: context arrived",
            "body": body,
        })

    before = previous_state or {
        "facts": [],
        "unknowns": [],
        "ruled_out_branches": [],
        "final_cause": "",
    }
    added_facts = [fact for fact in state.get("facts", []) if fact not in before.get("facts", [])]
    resolved_unknowns = [unknown for unknown in before.get("unknowns", []) if unknown not in state.get("unknowns", [])]
    ruled_out = [
        branch
        for branch in state.get("ruled_out_branches", [])
        if branch not in before.get("ruled_out_branches", [])
    ]
    final_cause = state.get("final_cause", "")
    previous_final_cause = before.get("final_cause", "")

    if added_facts:
        events.append({
            "kind": "Facts added",
            "title": "Known facts changed",
            "body": "; ".join(translate_list(added_facts)),
        })
    if resolved_unknowns:
        events.append({
            "kind": "Unknown resolved",
            "title": "Open question closed",
            "body": "; ".join(translate_list(resolved_unknowns)),
        })
    if ruled_out:
        events.append({
            "kind": "Ruled out",
            "title": "Cause narrowed",
            "body": "; ".join(translate_list(ruled_out)),
        })
    if final_cause and final_cause != previous_final_cause:
        events.append({
            "kind": "Final outcome",
            "title": "Final cause is now supported",
            "body": readable_label(final_cause),
        })
    return events


def build_simulator_data(case_id: str = CASE_ID) -> dict[str, Any]:
    fixture = load_fixture(case_id)
    result = run_fixture(fixture, mode="deterministic")
    steps = []
    conversation_so_far: list[dict[str, Any]] = []
    evidence_timeline: list[dict[str, str]] = []
    previous_state = None
    for item in result["timeline"]:
        turn = item["turn"]
        evidence_timeline.extend(evidence_events_for_turn(item, previous_state))
        previous_state = item["state"]
        conversation_so_far.append({
            "speaker": turn.get("speaker", "speaker"),
            "text": turn.get("text", ""),
        })
        steps.append({
            "turn": turn.get("turn"),
            "speaker": turn.get("speaker", ""),
            "route_stage": route_stage(turn, item["state"], item.get("context_applied", [])),
            "route_stages": ROUTE_STAGES,
            "conversation": list(conversation_so_far),
            "new_context": context_summary(item.get("context_applied", [])),
            "evidence_timeline": list(evidence_timeline),
            "handoff_readiness": handoff_readiness(item["state"]),
            "state": state_for_display(item["state"]),
        })
    return {
        "case_id": fixture["case_id"],
        "title": "Workspace access after migration",
        "subtitle": "A realistic support replay where the tempting early answer is wrong until product context arrives.",
        "customer": "B2B admin account",
        "steps": steps,
    }


def json_script(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=True).replace("</", "<\\/")


def render_live_simulator(data: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Support Live Simulator</title>
<style>
:root {{
  --bg: #11100f;
  --surface: #171513;
  --surface-2: #201d1a;
  --surface-3: #28231f;
  --line: #3a332d;
  --text: #f6efe8;
  --muted: #a99c90;
  --accent: #c4674a;
  --accent-text: #e8a08a;
  --good: #8fb996;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
main {{
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
}}
header {{
  border-bottom: 1px solid var(--line);
  padding: 20px 24px 18px;
}}
.eyebrow {{
  color: var(--accent-text);
  font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}}
h1 {{
  font-family: Cormorant, Georgia, serif;
  font-size: 34px;
  font-weight: 600;
  line-height: 1.05;
  margin: 8px 0 8px;
}}
.subhead {{
  max-width: 780px;
  color: #d8cec4;
  line-height: 1.45;
  margin: 0;
}}
.workspace {{
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(360px, 1.05fr);
  min-height: 0;
}}
.pane {{
  min-width: 0;
  padding: 20px 24px 28px;
}}
.pane + .pane {{
  border-left: 1px solid var(--line);
}}
.toolbar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}}
.turn-count {{
  color: var(--muted);
  font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}}
.buttons {{
  display: flex;
  gap: 8px;
}}
button {{
  min-width: 92px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-2);
  color: var(--text);
  padding: 9px 12px;
  cursor: pointer;
}}
button:hover {{ border-color: var(--accent); }}
button:disabled {{
  cursor: not-allowed;
  color: #6f655d;
  border-color: #2a2521;
  background: #151311;
}}
.conversation {{
  display: grid;
  gap: 12px;
}}
.route-map {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  padding: 14px;
  margin-bottom: 16px;
}}
.route-steps {{
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}}
.route-step {{
  min-height: 64px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #141210;
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 8px;
  font-size: 12px;
  line-height: 1.25;
}}
.route-step.active {{
  border-color: var(--accent);
  color: var(--text);
  background: #211914;
}}
.message {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  padding: 14px;
}}
.message.agent {{
  background: var(--surface-2);
}}
.speaker {{
  color: var(--accent-text);
  font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 8px;
}}
.message p {{
  margin: 0;
  color: var(--text);
  line-height: 1.45;
}}
.copilot {{
  display: grid;
  gap: 14px;
}}
.next-action {{
  border: 1px solid var(--accent);
  border-radius: 8px;
  background: #211914;
  padding: 16px;
}}
.section {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  padding: 14px;
}}
h2, h3 {{
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--muted);
  font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}}
.next-action h2 {{
  color: var(--accent-text);
}}
.next-action p, .outcome {{
  margin: 0;
  color: var(--text);
  font-size: 18px;
  line-height: 1.35;
}}
ul {{
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}}
li {{
  border-left: 2px solid var(--surface-3);
  padding-left: 10px;
  color: #e7ddd4;
  line-height: 1.35;
}}
.empty {{
  margin: 0;
  color: var(--muted);
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}}
.context-event {{
  border-left: 2px solid var(--good);
  padding-left: 10px;
}}
.context-event.irrelevant {{
  border-left-color: var(--muted);
}}
.context-event p {{
  margin: 0 0 8px;
  line-height: 1.4;
}}
.readiness {{
  display: grid;
  gap: 10px;
}}
.readiness-status {{
  margin: 0;
  color: var(--text);
  line-height: 1.4;
}}
.readiness-count {{
  color: var(--accent-text);
  font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}}
.readiness-check {{
  border-left: 2px solid var(--surface-3);
  padding-left: 10px;
}}
.readiness-check.ready {{
  border-left-color: var(--good);
}}
.readiness-check strong {{
  display: block;
  color: var(--text);
  margin-bottom: 3px;
}}
.readiness-check span {{
  color: var(--muted);
  line-height: 1.35;
}}
.timeline {{
  display: grid;
  gap: 10px;
}}
.timeline-event {{
  border-left: 2px solid var(--surface-3);
  padding-left: 10px;
}}
.timeline-kind {{
  color: var(--accent-text);
  font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}}
.timeline-event strong {{
  display: block;
  color: var(--text);
  margin: 3px 0;
}}
.timeline-event p {{
  margin: 0;
  color: #d8cec4;
  line-height: 1.4;
}}
details {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #141210;
  padding: 12px 14px;
}}
summary {{
  cursor: pointer;
  color: var(--accent-text);
}}
pre {{
  white-space: pre-wrap;
  color: #d8cec4;
  font-size: 12px;
  line-height: 1.45;
}}
@media (max-width: 860px) {{
  .workspace {{
    grid-template-columns: 1fr;
  }}
  .pane + .pane {{
    border-left: 0;
    border-top: 1px solid var(--line);
  }}
  .grid {{
    grid-template-columns: 1fr;
  }}
  .route-steps {{
    grid-template-columns: 1fr;
  }}
  header, .pane {{
    padding-left: 16px;
    padding-right: 16px;
  }}
}}
</style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">Live support simulator</div>
    <h1>{esc(data["title"])}</h1>
    <p class="subhead">{esc(data["subtitle"])}</p>
  </header>
  <section class="workspace">
    <div class="pane">
      <div class="toolbar">
        <div>
          <div class="eyebrow">Conversation</div>
          <div class="turn-count" id="turn-count"></div>
        </div>
        <div class="buttons">
          <button id="previous">Previous</button>
          <button id="next">Next</button>
        </div>
      </div>
      <div class="route-map" id="route-map"></div>
      <div class="conversation" id="conversation"></div>
    </div>
    <div class="pane">
      <div class="toolbar">
        <div>
          <div class="eyebrow">Copilot state</div>
          <div class="turn-count" id="copilot-count"></div>
        </div>
      </div>
      <div class="copilot" id="copilot"></div>
    </div>
  </section>
</main>
<script id="simulator-data" type="application/json">{json_script(data)}</script>
<script>
const data = JSON.parse(document.getElementById("simulator-data").textContent);
let index = 0;

const conversation = document.getElementById("conversation");
const copilot = document.getElementById("copilot");
const routeMap = document.getElementById("route-map");
const turnCount = document.getElementById("turn-count");
const copilotCount = document.getElementById("copilot-count");
const previous = document.getElementById("previous");
const next = document.getElementById("next");

function text(value) {{
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}}

function list(items, emptyText) {{
  if (!items || items.length === 0) {{
    return `<p class="empty">${{emptyText}}</p>`;
  }}
  return `<ul>${{items.map((item) => `<li>${{text(item)}}</li>`).join("")}}</ul>`;
}}

function renderConversation(step) {{
  conversation.innerHTML = step.conversation.map((message) => `
    <article class="message ${{message.speaker === "agent" ? "agent" : "customer"}}">
      <div class="speaker">${{text(message.speaker)}}</div>
      <p>${{text(message.text)}}</p>
    </article>
  `).join("");
}}

function renderRouteMap(step) {{
  routeMap.innerHTML = `
    <h2>Case route</h2>
    <div class="route-steps">
      ${{step.route_stages.map((stage) => `
        <div class="route-step ${{stage === step.route_stage ? "active" : ""}}">
          ${{text(stage)}}
        </div>
      `).join("")}}
    </div>
  `;
}}

function renderContext(events) {{
  if (!events.length) {{
    return `<p class="empty">No new product or support context has arrived at this turn.</p>`;
  }}
  return events.map((event) => `
    <div class="context-event ${{event.relevant ? "" : "irrelevant"}}">
      <p>${{text(event.description)}}</p>
      ${{list(event.facts, "No customer-useful facts were added.")}}
    </div>
  `).join("");
}}

function renderHandoffReadiness(readiness) {{
  return `
    <div class="readiness">
      <p class="readiness-status">${{text(readiness.status)}}</p>
      <div class="readiness-count">${{text(readiness.ready_count)}}/${{text(readiness.total)}} handoff checks ready</div>
      ${{readiness.checks.map((check) => `
        <div class="readiness-check ${{check.ready ? "ready" : ""}}">
          <strong>${{text(check.label)}}</strong>
          <span>${{text(check.detail)}}</span>
        </div>
      `).join("")}}
    </div>
  `;
}}

function renderEvidenceTimeline(events) {{
  if (!events || events.length === 0) {{
    return `<p class="empty">No evidence has arrived yet.</p>`;
  }}
  return `
    <div class="timeline">
      ${{events.map((event) => `
        <div class="timeline-event">
          <div class="timeline-kind">${{text(event.kind)}}</div>
          <strong>${{text(event.title)}}</strong>
          <p>${{text(event.body)}}</p>
        </div>
      `).join("")}}
    </div>
  `;
}}

function renderCopilot(step) {{
  const state = step.state;
  copilot.innerHTML = `
    <section class="next-action">
      <h2>Next best question, check, or action</h2>
      <p>${{text(state.next_best_action || "Keep gathering evidence before advising the customer.")}}</p>
    </section>
    <div class="grid">
      <section class="section">
        <h3>Known facts</h3>
        ${{list(state.known_facts, "No durable facts yet.")}}
      </section>
      <section class="section">
        <h3>Still unknown</h3>
        ${{list(state.still_unknown, "No blocking unknowns remain.")}}
      </section>
      <section class="section">
        <h3>Possible causes</h3>
        ${{list(state.possible_causes, "No possible cause should be named yet.")}}
      </section>
      <section class="section">
        <h3>Ruled out</h3>
        ${{list(state.ruled_out, "Nothing has been ruled out yet.")}}
      </section>
    </div>
    <section class="section">
      <h3>Product and support context</h3>
      ${{renderContext(step.new_context)}}
    </section>
    <section class="section">
      <h3>Evidence timeline</h3>
      ${{renderEvidenceTimeline(step.evidence_timeline)}}
    </section>
    <section class="section">
      <h3>Handoff readiness preview</h3>
      ${{renderHandoffReadiness(step.handoff_readiness)}}
    </section>
    <section class="section">
      <h3>Final outcome</h3>
      <p class="outcome">${{text(state.final_outcome)}}</p>
    </section>
    <details>
      <summary>Show raw eval state</summary>
      <pre>${{JSON.stringify(state.raw, null, 2)}}</pre>
    </details>
  `;
}}

function render() {{
  const step = data.steps[index];
  turnCount.textContent = `Turn ${{index + 1}} of ${{data.steps.length}}`;
  copilotCount.textContent = `${{data.customer}}`;
  previous.disabled = index === 0;
  next.disabled = index === data.steps.length - 1;
  renderRouteMap(step);
  renderConversation(step);
  renderCopilot(step);
}}

previous.addEventListener("click", () => {{
  index = Math.max(0, index - 1);
  render();
}});

next.addEventListener("click", () => {{
  index = Math.min(data.steps.length - 1, index + 1);
  render();
}});

render();
</script>
</body>
</html>
"""


def write_live_simulator(path: Path = SIMULATOR_PATH) -> Path:
    ensure_output_dir()
    data = build_simulator_data()
    path.write_text(render_live_simulator(data), encoding="utf-8")
    return path


def main() -> None:
    path = write_live_simulator()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

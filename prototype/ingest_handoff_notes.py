#!/usr/bin/env python3
"""Render the six real handed-off cases as Copilot case screens.

Reads the recorded Handoff notes from the sealed voice-support run (and H1's
richer note from the Flow 0 trace), and writes one self-contained HTML case
screen per handoff into outputs/handoff_cases/, plus an index listing all six.

Deterministic, no model calls, re-runnable: stale outputs are cleared each run,
matching the pipeline's report generators. Reads output files only — it never
imports or edits voice-support logic, QA outputs, or judge rubrics.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import OUTPUT_DIR, esc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT.parent / "voice-support"
CSAIOS = ROOT.parent / "customer-support-ai-os"

CASE_IDS = ["H1", "H2", "T1", "T2", "PB1", "PB2"]
CASES_DIR = OUTPUT_DIR / "handoff_cases"

BANNER = ("Rendered from the recorded Handoff note of the offline run — "
          "not a live feed. Live delivery is future work.")
NR = '<span class="nr">not recorded</span>'

# keep on-screen language in the approved support taxonomy
_SCRUB = [
    (re.compile(r"\bdeterministic(?:ally)?\b", re.I), "rule-based"),
    (re.compile(r"\bevaluations?\b", re.I), "QA review"),
    (re.compile(r"\bevals?\b", re.I), "QA review"),
    (re.compile(r"\bJSONL\b", re.I), "case log"),
    (re.compile(r"\bfixtures?\b", re.I), "permanent test case"),
]


def scrub(text: str) -> str:
    out = str(text)
    for rx, rep in _SCRUB:
        out = rx.sub(rep, out)
    return out


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def build_cases() -> list[dict]:
    """Assemble a structured case record per handoff from the recorded files."""
    results = _load_json(VOICE / "outputs" / "eval_results.json")
    by_id = {s["scenario_id"]: s for s in results.get("scenarios", [])}
    flow0 = _load_json(CSAIOS / "outputs" / "flow0_H1.json")

    cases = []
    for cid in CASE_IDS:
        row = by_id.get(cid, {})
        routing = row.get("routing", {})
        gate = row.get("gate", {})
        resp = row.get("response", {})
        packet = resp.get("handoff") or {}
        reasons = [scrub(r) for r in resp.get("lane_reasons", [])]

        case = {
            "id": cid,
            "utterance": row.get("utterance", ""),
            "lane": routing.get("actual_lane", ""),
            "identity": None,
            "claim": packet.get("customer_safe_summary", ""),
            "charge_ref": None,
            "confirmed_facts": [],  # list of readable strings
            "open_unknowns": [scrub(u) for u in packet.get("open_unknowns", [])],
            "next_owner": packet.get("next_owner", ""),
            "safety_floor": routing.get("deterministic_floor", ""),
            "llm_risk": routing.get("llm_risk", ""),
            "final_risk": routing.get("final_risk", ""),
            "escalation_reasons": reasons,
            "gate_verdict": gate.get("verdict", ""),
            "gate_reasons": [scrub(r) for r in gate.get("reasons", [])],
            "reference": None,
            "ticket_status": None,
            "judges": [
                {"name": j.get("name", ""), "status": j.get("status", ""),
                 "reason": scrub(j.get("reason", ""))}
                for j in row.get("judges", [])
            ],
        }

        # H1 is the sealed Flow 0 case — enrich it from the richer note + ticket.
        if cid == "H1":
            note = flow0.get("handoff_note", {})
            inbox = flow0.get("inbox_record", {})
            ident = note.get("identity") or {}
            claim = note.get("claim") or {}
            charge = note.get("charge_ref") or {}
            case["identity"] = ident.get("value")
            case["claim"] = note.get("gated_summary") or claim.get("value") or case["claim"]
            case["charge_ref"] = charge.get("value")
            facts = []
            for f in note.get("confirmed_facts", []):
                v = f.get("value")
                if isinstance(v, list):
                    v = "; ".join(str(x) for x in v)
                facts.append(f"{str(f.get('claim', '')).replace('_', ' ')}: {v}")
            case["confirmed_facts"] = facts
            case["reference"] = inbox.get("reference")
            case["ticket_status"] = inbox.get("status")
            if note.get("handoff_reason"):
                case["escalation_reasons"] = [scrub(note["handoff_reason"])] + case["escalation_reasons"]

        cases.append(case)
    return cases


# ---------- rendering (reuses the Copilot's dark case-screen look) ----------

STYLE = """
body{margin:0;background:#11100f;color:#f6efe8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.5}
main{max-width:900px;margin:0 auto;padding:40px 22px 72px}
a{color:#e8a08a;text-decoration:none}
.eyebrow,.label{color:#c4674a;font-size:12px;text-transform:uppercase;letter-spacing:.12em;font-weight:700}
h1{font-size:32px;line-height:1.1;margin:10px 0 6px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#a99c90;margin:26px 0 10px}
.banner{border-left:3px solid #c4674a;background:#201d1a;color:#fff7ef;padding:12px 15px;border-radius:6px;margin:16px 0}
.card{border:1px solid #352f2a;border-radius:8px;background:#171513;padding:18px 20px;margin:12px 0}
blockquote{margin:0;padding:14px 16px;background:#201d1a;border-left:3px solid #c4674a;color:#fff7ef;border-radius:6px}
dl{display:grid;grid-template-columns:210px 1fr;gap:2px 18px;margin:0}
dt{color:#a99c90;padding:8px 0;border-top:1px solid #2b2723}
dd{margin:0;padding:8px 0;border-top:1px solid #2b2723}
dt:first-of-type,dd:first-of-type{border-top:0}
ul{margin:6px 0;padding-left:18px}
li{margin:5px 0}
.pill{display:inline-block;border-radius:20px;padding:3px 11px;font-size:12.5px;font-weight:600;background:#2b2723;color:#f6efe8}
.pill.high{background:#4a2320;color:#ffbcae}
.pill.med{background:#4a3f20;color:#ffe6a0}
.pill.low{background:#20402f;color:#a9f0c7}
.pill.ok{background:#20402f;color:#a9f0c7}
.pill.warn{background:#4a3f20;color:#ffe6a0}
.nr{color:#7c736b;font-style:italic}
.judge{border-top:1px solid #2b2723;padding:11px 0}
.judge:first-child{border-top:0}
.judge .jn{font-weight:700}
.judge .jr{color:#d6ccc2;margin-top:3px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.grid a{display:block;border:1px solid #352f2a;border-radius:8px;background:#171513;padding:16px;color:inherit}
.grid a:hover{border-color:#c4674a}
.note{color:#a99c90;font-size:13px;margin-top:22px}
"""


def _page(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{esc(title)}</title>\n<style>{STYLE}</style>\n</head>\n<body>\n"
        f"<main>{body}</main>\n</body>\n</html>\n"
    )


def _risk_pill(level: str) -> str:
    lv = str(level or "").lower()
    cls = {"high": "high", "medium": "med", "low": "low"}.get(lv, "")
    return f'<span class="pill {cls}">{esc((level or "—").capitalize())}</span>' if level else NR


def _list(items: list[str]) -> str:
    if not items:
        return NR
    return "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"


def render_case(case: dict) -> str:
    gv = case["gate_verdict"]
    gate_cls = "ok" if gv.startswith("pass") else ("warn" if gv else "")
    judges = "".join(
        f'<div class="judge"><span class="jn">{esc(case_reviewer_name(j["name"]))}</span> '
        f'<span class="pill {"ok" if j["status"] == "pass" else "high"}">{esc(j["status"].capitalize())}</span>'
        f'<div class="jr">{esc(j["reason"])}</div></div>'
        for j in case["judges"]
    ) or NR

    body = f"""
<div class="eyebrow">Copilot &middot; Handoff note</div>
<h1>Case {esc(case['id'])} &mdash; {esc(case['lane'].capitalize())} to a person</h1>
<div class="banner">{esc(BANNER)}</div>

<h2>What the customer said</h2>
<blockquote>{esc(case['utterance']) or NR}</blockquote>

<h2>Who &amp; what</h2>
<div class="card"><dl>
  <dt>Customer</dt><dd>{esc(case['identity']) if case['identity'] else NR}</dd>
  <dt>Request</dt><dd>{esc(case['claim']) if case['claim'] else NR}</dd>
  <dt>Billing reference</dt><dd>{esc(case['charge_ref']) if case['charge_ref'] else NR}</dd>
  <dt>Escalates to</dt><dd>{esc(str(case['next_owner']).replace('_', ' ')) if case['next_owner'] else NR}</dd>
</dl></div>

<h2>Confirmed facts vs open unknowns</h2>
<div class="card"><dl>
  <dt>Confirmed facts</dt><dd>{_list(case['confirmed_facts'])}</dd>
  <dt>Open unknowns</dt><dd>{_list(case['open_unknowns'])}</dd>
</dl></div>

<h2>Risk &amp; why it escalated</h2>
<div class="card"><dl>
  <dt>Safety floor</dt><dd>{_risk_pill(case['safety_floor'])}</dd>
  <dt>LLM reader</dt><dd>{_risk_pill(case['llm_risk'])}</dd>
  <dt>Highest warning state</dt><dd>{_risk_pill(case['final_risk'])}</dd>
  <dt>Why it escalated</dt><dd>{_list(case['escalation_reasons'])}</dd>
</dl></div>

<h2>Gate</h2>
<div class="card"><dl>
  <dt>Verdict</dt><dd><span class="pill {gate_cls}">{esc(gv.replace('_', ' ')) if gv else NR}</span></dd>
  <dt>Reason</dt><dd>{_list(case['gate_reasons'])}</dd>
</dl></div>

<h2>Ticket</h2>
<div class="card"><dl>
  <dt>Reference (case number)</dt><dd>{esc(case['reference']) if case['reference'] else NR}</dd>
  <dt>Status</dt><dd>{esc(str(case['ticket_status']).replace('_', ' ')) if case['ticket_status'] else NR}</dd>
</dl></div>

<h2>QA reviewers' verdicts</h2>
<div class="card">{judges}</div>

<p class="note"><a href="index.html">&larr; All handoff cases</a></p>
"""
    return _page(f"Copilot case {case['id']}", body)


def case_reviewer_name(name: str) -> str:
    return str(name or "").replace("_", " ")


def render_index(cases: list[dict]) -> str:
    cards = "".join(
        f'<a href="{esc(c["id"])}.html"><div class="eyebrow">{esc(c["id"])}</div>'
        f'<div style="margin:6px 0 8px;color:#fff7ef">{esc(c["utterance"])}</div>'
        f'<span class="pill">{esc(c["lane"].capitalize())}</span> '
        f'<span class="pill {"high" if c["final_risk"] == "high" else ("med" if c["final_risk"] == "medium" else "low")}">'
        f'{esc((c["final_risk"] or "—").capitalize())} risk</span></a>'
        for c in cases
    )
    body = f"""
<div class="eyebrow">Copilot</div>
<h1>Handoff cases</h1>
<div class="banner">{esc(BANNER)}</div>
<p>The six real cases the pipeline handed to a person, rendered as Copilot case screens
from their recorded Handoff notes. H1 is the sealed Flow&nbsp;0 case and carries a Ticket
reference; the rest are the offline run's recorded notes.</p>
<div class="grid">{cards}</div>
"""
    return _page("Copilot handoff cases", body)


def main(out_dir: Path = CASES_DIR) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    # clear stale outputs each run (same rule as the pipeline's report generators)
    for old in out_dir.glob("*.html"):
        old.unlink()
    cases = build_cases()
    written = []
    for case in cases:
        p = out_dir / f"{case['id']}.html"
        p.write_text(render_case(case))
        written.append(p)
    idx = out_dir / "index.html"
    idx.write_text(render_index(cases))
    written.append(idx)
    for p in written:
        print(f"Wrote {p}")
    return written


if __name__ == "__main__":
    main()

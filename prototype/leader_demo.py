#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import OUTPUT_DIR, ensure_output_dir, esc
from prototype.generated_review import generated_review, load_staged_fixtures, review_outcome
from prototype.support_language import (
    translate_causes,
    translate_evidence,
    translate_facts,
    translate_next_action,
    translate_open_questions,
    translate_outcome,
    translate_title,
)
from run import run_fixture

DEMO_PATH = OUTPUT_DIR / "support_leader_demo.html"
OUTCOME_ORDER = ["resolved", "probable_cause", "handoff"]
OUTCOME_TITLES = {
    "resolved": "Resolved",
    "probable_cause": "Probable Cause",
    "handoff": "Handoff",
}
OUTCOME_EXPLANATIONS = {
    "resolved": "The assistant waited for product evidence, then helped close the case.",
    "probable_cause": "The assistant found the likely cause while keeping the verification need visible.",
    "handoff": "The assistant avoided overclaiming and prepared the next owner to continue.",
}


def short_list(items: list[str], limit: int = 5) -> list[str]:
    if len(items) <= limit:
        return items
    return items[:limit] + [f"+{len(items) - limit} more"]


def render_list(items: list[str], empty: str = "None blocking the next step.") -> str:
    if not items:
        return f'<p class="muted">{esc(empty)}</p>'
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in short_list(items)) + "</ul>"


def customer_opening(result: dict[str, Any]) -> str:
    for turn in result["fixture"]["transcript_turns"]:
        if turn.get("speaker") == "customer":
            return turn.get("text", "")
    return result["fixture"]["transcript_turns"][0].get("text", "")


def select_demo_results(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        result = run_fixture(fixture, mode="deterministic")
        review = generated_review(result)
        outcome = review_outcome(fixture)
        if review["ready_for_promotion"] and outcome in OUTCOME_ORDER and outcome not in selected:
            selected[outcome] = {"result": result, "review": review}
    missing = [outcome for outcome in OUTCOME_ORDER if outcome not in selected]
    if missing:
        raise SystemExit(f"Could not find ready demo case(s) for: {', '.join(missing)}")
    return [selected[outcome] for outcome in OUTCOME_ORDER]


def render_case_card(item: dict[str, Any]) -> str:
    result = item["result"]
    review = item["review"]
    outcome = review["outcome"]
    state = result["final_state"]
    return f"""
    <article class="case-card">
      <div class="label">{esc(OUTCOME_TITLES[outcome])}</div>
      <h2>{esc(translate_title(result, OUTCOME_TITLES[outcome]))}</h2>
      <p class="summary">{esc(OUTCOME_EXPLANATIONS[outcome])}</p>

      <section class="customer">
        <h3>1. Customer Situation</h3>
        <blockquote>{esc(customer_opening(result))}</blockquote>
      </section>

      <div class="grid">
        <section>
          <h3>2. What We Know</h3>
          {render_list(translate_facts(state["facts"]), "No durable facts yet.")}
        </section>
        <section>
          <h3>3. What Is Still Unknown</h3>
          {render_list(translate_open_questions(result, review))}
        </section>
      </div>

      <section>
        <h3>4. Evidence That Changed The Case</h3>
        <p>{esc(translate_evidence(result))}</p>
      </section>

      <section class="next-step">
        <h3>5. Next Best Action</h3>
        <p>{esc(translate_next_action(result, review))}</p>
      </section>

      <section class="outcome">
        <h3>How The Case Ended</h3>
        <p>{esc(translate_outcome(result, review))}</p>
      </section>

      <details>
        <summary>Show internal state details</summary>
        <div class="grid">
          <section>
            <h3>Possible Causes Still Active</h3>
            {render_list(translate_causes(state["candidate_branches"]), "No possible cause left open.")}
          </section>
          <section>
            <h3>Causes Ruled Out</h3>
            {render_list(translate_causes(state["ruled_out_branches"]), "Nothing ruled out yet.")}
          </section>
        </div>
      </details>
    </article>
    """


def render_support_leader_demo(fixtures: list[dict[str, Any]]) -> str:
    items = select_demo_results(fixtures)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Support Copilot Demo</title>
<style>
body {{ margin:0; background:#11100f; color:#f6efe8; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
main {{ max-width:1060px; margin:0 auto; padding:40px 20px 72px; }}
.hero {{ border-bottom:1px solid #352f2a; padding-bottom:28px; margin-bottom:28px; }}
.eyebrow, .label {{ color:#c4674a; font-size:12px; text-transform:uppercase; letter-spacing:.12em; font-weight:700; }}
h1 {{ font-size:38px; line-height:1.05; margin:10px 0 14px; max-width:820px; }}
h2 {{ font-size:24px; margin:8px 0 8px; }}
h3 {{ font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:#a99c90; margin:0 0 8px; }}
p {{ color:#d6ccc2; line-height:1.5; }}
.plain {{ font-size:18px; max-width:860px; }}
.case-card {{ border:1px solid #352f2a; border-radius:8px; background:#171513; padding:24px; margin:18px 0; }}
.summary {{ margin-top:0; color:#fff7ef; }}
blockquote {{ margin:0; padding:14px 16px; background:#201d1a; border-left:3px solid #c4674a; color:#fff7ef; line-height:1.45; }}
.customer, .next-step, .outcome, details, .grid section {{ border:1px solid #352f2a; border-radius:8px; background:#151311; padding:16px; margin-top:14px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:14px; }}
ul {{ margin:0; padding-left:18px; color:#f6efe8; }}
li {{ margin:6px 0; }}
.muted {{ color:#a99c90; margin:0; }}
.next-step p, .outcome p {{ margin:0; color:#fff7ef; font-size:17px; }}
summary {{ cursor:pointer; color:#e8a08a; }}
.note {{ color:#a99c90; font-size:14px; max-width:850px; }}
</style>
</head>
<body>
<main>
  <section class="hero">
    <div class="eyebrow">Support leader demo</div>
    <h1>A support copilot that works the case instead of guessing early.</h1>
    <p class="plain">This prototype follows a support conversation as evidence arrives. It keeps track of what is known, what is unknown, what to check next, and whether the case should resolve, stay probable, or move to another owner.</p>
    <p class="note">This page shows three synthetic B2B examples. The larger audit report still exists, but this is the simpler story to review first.</p>
  </section>
  {"".join(render_case_card(item) for item in items)}
</main>
</body>
</html>
"""


def write_support_leader_demo(
    staging_dir: Path,
    path: Path = DEMO_PATH,
) -> Path:
    fixtures = load_staged_fixtures(staging_dir)
    ensure_output_dir()
    path.write_text(render_support_leader_demo(fixtures), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a simple support-leader demo from ready generated cases.")
    parser.add_argument("--staging-dir", default=str(ROOT / "outputs" / "generated_fixture_staging"))
    args = parser.parse_args()
    path = write_support_leader_demo(Path(args.staging_dir))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import load_fixtures
from run import run_fixture


def find_fixture(case_id: str) -> dict[str, Any]:
    fixtures = load_fixtures()
    for fixture in fixtures:
        if fixture["case_id"] == case_id:
            return fixture
    available = ", ".join(fixture["case_id"] for fixture in fixtures)
    raise SystemExit(f"Unknown case_id: {case_id}. Available cases: {available}")


def render_list(label: str, values: list[str]) -> None:
    print(f"{label}:")
    if not values:
        print("  -")
        return
    for value in values:
        print(f"  - {value}")


def render_state(state: dict[str, Any]) -> None:
    print("Live Support State")
    print(f"  version: {state['version']}")
    render_list("  facts", state["facts"])
    render_list("  unknowns", state["unknowns"])
    render_list("  candidate_branches", state["candidate_branches"])
    render_list("  ruled_out_branches", state["ruled_out_branches"])
    print(f"  next_check: {state['next_check'] or '-'}")
    if state.get("final_cause"):
        print(f"  final_cause: {state['final_cause']}")
    else:
        print("  final_cause: -")


def render_context(events: list[dict[str, Any]]) -> None:
    if not events:
        return
    print("Product/support context applied:")
    for event in events:
        relevant = event.get("relevant", True)
        suffix = "" if relevant else " (ignored: not relevant to this case)"
        print(f"  - {event.get('description', '-')}{suffix}")
        facts = event.get("facts", [])
        if facts:
            print(f"    facts: {', '.join(facts)}")


def render_patch(patch: dict[str, Any] | None) -> None:
    if patch is None:
        print("State patch: -")
        return
    print("State patch:")
    print(json.dumps(patch, indent=2))


def replay(case_id: str, mode: str, show_patches: bool = False) -> None:
    result = build_replay(case_id, mode)
    fixture = result["fixture"]

    print(f"Case: {fixture['case_id']} - {fixture['title']}")
    print(f"Scenario: {fixture['scenario']}")
    print(f"Mode: {mode}")
    print("")

    for item in result["timeline"]:
        turn = item["turn"]
        print("=" * 72)
        print(f"Turn {turn['turn']} | {turn['speaker']}")
        print(turn["text"])
        print("")
        render_context(item["context_applied"])
        if item["context_applied"]:
            print("")
        if show_patches:
            render_patch(item["llm_patch"])
            print("")
        render_state(item["state"])
        print("")

    print("=" * 72)
    print("Final")
    print(json.dumps(result["final_state"], indent=2))


def build_replay(case_id: str, mode: str) -> dict[str, Any]:
    fixture = find_fixture(case_id)
    llm_command = ""
    run_mode = "deterministic"
    if mode == "process-mock":
        run_mode = "llm"
        mock_path = ROOT / "mock_llm.py"
        llm_command = f"{shlex.quote(sys.executable)} {shlex.quote(str(mock_path))} --profile process"
    return run_fixture(fixture, mode=run_mode, llm_command=llm_command)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay one support fixture as a tiny text-first prototype.")
    parser.add_argument("--case", default="access_after_migration", help="Fixture case_id to replay.")
    parser.add_argument(
        "--mode",
        choices=("process-mock", "deterministic"),
        default="process-mock",
        help="Local replay path. No real model calls are supported here.",
    )
    parser.add_argument(
        "--show-patches",
        action="store_true",
        help="Print the local model state patch before the reconciled Live Support State.",
    )
    args = parser.parse_args()
    replay(args.case, args.mode, show_patches=args.show_patches)


if __name__ == "__main__":
    main()

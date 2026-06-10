#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from common import load_fixtures

REQUIRED_TOP_LEVEL = {
    "case_id",
    "title",
    "scenario",
    "transcript_turns",
    "context_events",
    "expected_by_turn",
    "final_cause",
}
REQUIRED_STATE_FIELDS = {"facts", "unknowns", "candidate_branches", "ruled_out_branches", "next_check_contains"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = fixture.get("case_id", "<missing case_id>")
    missing = sorted(REQUIRED_TOP_LEVEL - set(fixture))
    require(not missing, f"{case_id}: missing top-level fields: {', '.join(missing)}", errors)

    turns = fixture.get("transcript_turns", [])
    require(isinstance(turns, list) and bool(turns), f"{case_id}: transcript_turns must be a non-empty list", errors)
    turn_numbers = set()
    for turn in turns:
        require("turn" in turn and "speaker" in turn and "text" in turn, f"{case_id}: each transcript turn needs turn/speaker/text", errors)
        if "turn" in turn:
            turn_numbers.add(int(turn["turn"]))

    for item in fixture.get("expected_by_turn", []):
        after_turn = int(item.get("after_turn", -1))
        require(after_turn in turn_numbers, f"{case_id}: expected_by_turn references missing turn {after_turn}", errors)
        missing_state = sorted(REQUIRED_STATE_FIELDS - set(item))
        require(not missing_state, f"{case_id}: expected turn {after_turn} missing fields: {', '.join(missing_state)}", errors)

    for event in fixture.get("context_events", []):
        after_turn = int(event.get("after_turn", -1))
        require(after_turn in turn_numbers, f"{case_id}: context event references missing turn {after_turn}", errors)
        require("description" in event, f"{case_id}: context event after turn {after_turn} missing description", errors)
        require("facts" in event, f"{case_id}: context event after turn {after_turn} missing facts", errors)

    require(bool(fixture.get("final_cause")), f"{case_id}: final_cause must be set", errors)
    return errors


def main() -> None:
    errors: list[str] = []
    fixtures = load_fixtures()
    require(bool(fixtures), "no fixtures found", errors)
    for fixture in fixtures:
        errors.extend(validate_fixture(fixture))

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print(f"Validated {len(fixtures)} fixtures")


if __name__ == "__main__":
    main()

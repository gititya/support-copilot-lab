#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import OUTPUT_DIR
from validate_fixtures import validate_fixture

SUPPORTED_SCHEMA = "support_process_fixture.v1"
DEFAULT_STAGING_DIR = OUTPUT_DIR / "generated_fixture_staging"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip()).strip("_")
    return slug.lower()


def load_generated_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    if isinstance(payload, dict) and payload.get("schema_version"):
        schema_version = payload.get("schema_version")
        if schema_version != SUPPORTED_SCHEMA:
            raise ValueError(f"Unsupported schema_version: {schema_version}")
        cases = payload.get("cases")
        if cases is not None:
            if not isinstance(cases, list) or not cases:
                raise ValueError("Generated fixture envelope needs a non-empty cases list")
            return cases
        return [payload]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("Generated fixture file must contain an envelope object or one fixture object")


def first_relevant_context_turn(case: dict[str, Any]) -> int | None:
    turns = [
        int(event["after_turn"])
        for event in case.get("context_events", [])
        if event.get("relevant", True)
    ]
    return min(turns) if turns else None


def validate_import_case(case: dict[str, Any]) -> list[str]:
    errors = validate_fixture(case)
    case_id = case.get("case_id", "<missing case_id>")
    if not case.get("context_events"):
        errors.append(f"{case_id}: generated cases must include timed context_events")

    final_cause = case.get("final_cause", "")
    first_context_turn = first_relevant_context_turn(case)
    if final_cause and first_context_turn is None:
        errors.append(f"{case_id}: final_cause requires at least one relevant context event")
    if final_cause and first_context_turn is not None:
        needle = final_cause.replace("_", " ")
        for turn in case.get("transcript_turns", []):
            if int(turn.get("turn", 0)) >= first_context_turn:
                continue
            text = " ".join(str(turn.get("text", "")).lower().split())
            if final_cause.lower() in text or needle.lower() in text:
                errors.append(f"{case_id}: transcript leaks final_cause before context at turn {turn.get('turn')}")
                break
    return errors


def write_staged_cases(cases: list[dict[str, Any]], staging_dir: Path) -> list[Path]:
    staging_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for case in cases:
        case_id = slugify(case["case_id"])
        path = staging_dir / f"{case_id}.json"
        path.write_text(json.dumps(case, indent=2) + "\n")
        written.append(path)
    return written


def import_cases(input_path: Path, staging_dir: Path = DEFAULT_STAGING_DIR) -> list[Path]:
    cases = load_generated_cases(input_path)
    errors = []
    for case in cases:
        errors.extend(validate_import_case(case))
    if errors:
        raise ValueError("\n".join(errors))
    return write_staged_cases(cases, staging_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and stage generated support-process fixtures.")
    parser.add_argument("input", help="Generated fixture JSON file.")
    parser.add_argument(
        "--staging-dir",
        default=str(DEFAULT_STAGING_DIR),
        help="Directory for staged generated fixtures. Defaults under outputs/.",
    )
    args = parser.parse_args()
    try:
        written = import_cases(Path(args.input), Path(args.staging_dir))
    except ValueError as exc:
        raise SystemExit(str(exc))
    for path in written:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()

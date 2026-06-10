#!/usr/bin/env python3
from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import OUTPUT_DIR, ensure_output_dir, markdown_table

ROOT = Path(__file__).resolve().parent


def run_step(args: list[str]) -> None:
    print("$ " + " ".join(shlex.quote(arg) for arg in args))
    subprocess.run(args, cwd=ROOT, check=True)


def summarize(path: Path) -> dict[str, Any]:
    results = json.loads(path.read_text())
    checks = 0
    passed = 0
    final_ok = 0
    premature = 0
    cases = len(results)
    for result in results:
        if result.get("root_cause_ok"):
            final_ok += 1
        for item in result["timeline"]:
            verdict = item.get("verdict")
            if not verdict:
                continue
            checks += verdict["total"]
            passed += verdict["passed"]
            for check in verdict["checks"]:
                if check["field"] == "final_cause_timing" and not check["passed"]:
                    premature += 1
    return {
        "cases": cases,
        "checks": checks,
        "passed": passed,
        "pass_rate": round((passed / checks) * 100) if checks else 0,
        "final_ok": final_ok,
        "premature_final_cause_turns": premature,
    }


def main() -> None:
    out_dir = ensure_output_dir()
    py = sys.executable
    mock = ROOT / "mock_llm.py"

    run_step([py, "validate_fixtures.py"])
    run_step([py, "run.py", "--run-name", "deterministic"])
    run_step([py, "run.py", "--mode", "prompt-pack"])
    run_step([
        py,
        "run.py",
        "--mode",
        "llm",
        "--run-name",
        "process_mock",
        "--llm-command",
        f"{shlex.quote(py)} {shlex.quote(str(mock))} --profile process",
    ])
    run_step([
        py,
        "run.py",
        "--mode",
        "llm",
        "--run-name",
        "predictive_mock",
        "--llm-command",
        f"{shlex.quote(py)} {shlex.quote(str(mock))} --profile predictive",
    ])

    rows = []
    for name in ["deterministic", "process_mock", "predictive_mock"]:
        path = out_dir / f"support_process_{name}_snapshots.json"
        stats = summarize(path)
        rows.append([
            name,
            stats["cases"],
            f"{stats['passed']}/{stats['checks']}",
            f"{stats['pass_rate']}%",
            f"{stats['final_ok']}/{stats['cases']}",
            stats["premature_final_cause_turns"],
        ])

    lines = [
        "# Support Process Experiment Summary",
        "",
        "This is the end-to-end offline experiment for text-first LTS support-process behavior.",
        "",
        markdown_table(["run", "cases", "checks", "pass_rate", "final_cause_ok", "premature_final_cause_turns"], rows),
        "",
        "## Interpretation",
        "",
        "- `deterministic` is the reference state-machine baseline.",
        "- `process_mock` simulates the intended LTS Think step: maintain state and wait for product/support context before final cause.",
        "- `predictive_mock` simulates the old failure mode: early final-cause guesses from transcript symptoms.",
        "",
        "A useful model should look closer to `process_mock` than `predictive_mock`, especially on `premature_final_cause_turns`.",
    ]
    summary_path = OUTPUT_DIR / "experiment_summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()

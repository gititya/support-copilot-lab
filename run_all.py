#!/usr/bin/env python3
from __future__ import annotations

import json
import os
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


def render_error_analysis(path: Path, status: str) -> str:
    lines = [
        "# Real Model Error Analysis",
        "",
        "Generated from the structured verdicts in the real-model snapshot.",
        "",
    ]
    if not path.exists():
        lines.extend([
            f"Real model snapshot not available in this run: {status}.",
            "",
        ])
        return "\n".join(lines)

    results = json.loads(path.read_text())
    rows = []
    for result in results:
        case_id = result["fixture"]["case_id"]
        for item in result["timeline"]:
            verdict = item.get("verdict")
            if not verdict:
                continue
            turn = item["turn"]["turn"]
            for check in verdict["checks"]:
                if not check["missing"]:
                    continue
                field = check["field"]
                classification = "evaluator_strictness" if field == "next_check" and check.get("actual") else "model_miss"
                rows.append([
                    case_id,
                    turn,
                    field,
                    "; ".join(check["missing"]),
                    check.get("actual", ""),
                    classification,
                ])

    if not rows:
        lines.append("No misses found.")
    else:
        lines.append(markdown_table([
            "case",
            "turn",
            "field",
            "missing",
            "actual",
            "classification",
        ], rows))
        lines.extend([
            "",
            "## Classification Notes",
            "",
            "- `evaluator_strictness` means the model gave a non-empty next check but missed the exact expected substring.",
            "- `model_miss` means a required structured state field or final-cause timing check failed.",
        ])
    return "\n".join(lines) + "\n"


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
    row_status = {
        "deterministic": "ran",
        "process_mock": "ran",
        "predictive_mock": "ran",
    }
    real_model_ran = False
    real_model_status = "not run; set SUPPORT_PROCESS_RUN_REAL_MODEL=1, SUPPORT_PROCESS_REAL_MODEL_NAME, and the provider API key"
    if os.environ.get("SUPPORT_PROCESS_RUN_REAL_MODEL") == "1":
        provider = os.environ.get("SUPPORT_PROCESS_REAL_MODEL_PROVIDER", "openai")
        model = os.environ.get("SUPPORT_PROCESS_REAL_MODEL_NAME", "")
        provider_env = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }.get(provider, "")
        provider_ready = bool(provider_env and os.environ.get(provider_env))
        if model and provider_ready:
            run_step([
                py,
                "run.py",
                "--mode",
                "real-model",
                "--run-name",
                "real_model",
            ])
            real_model_ran = True
            row_status["real_model"] = "ran"
        elif not model:
            real_model_status = "not run; SUPPORT_PROCESS_REAL_MODEL_NAME is missing"
        elif provider_env:
            real_model_status = f"not run; {provider_env} is missing"
        else:
            real_model_status = f"not run; unsupported provider {provider}"

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
            row_status[name],
        ])
    if real_model_ran:
        path = out_dir / "support_process_real_model_snapshots.json"
        stats = summarize(path)
        rows.append([
            "real_model",
            stats["cases"],
            f"{stats['passed']}/{stats['checks']}",
            f"{stats['pass_rate']}%",
            f"{stats['final_ok']}/{stats['cases']}",
            stats["premature_final_cause_turns"],
            row_status["real_model"],
        ])
    else:
        rows.append(["real_model", "-", "-", "-", "-", "-", real_model_status])

    lines = [
        "# Support Process Experiment Summary",
        "",
        "This is the end-to-end offline experiment for text-first LTS support-process behavior.",
        "",
        markdown_table(["run", "cases", "checks", "pass_rate", "final_cause_ok", "premature_final_cause_turns", "status"], rows),
        "",
        "## Interpretation",
        "",
        "- `deterministic` is the reference state-machine baseline.",
        "- `process_mock` simulates the intended LTS Think step: maintain state and wait for product/support context before final cause.",
        "- `predictive_mock` simulates the old failure mode: early final-cause guesses from transcript symptoms.",
        "- `real_model` is an opt-in provider run over the same fixtures; if no key/model is configured, no result is fabricated.",
        "",
        "A useful model should look closer to `process_mock` than `predictive_mock`, especially on `premature_final_cause_turns`.",
    ]
    summary_path = OUTPUT_DIR / "experiment_summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"Wrote {summary_path}")

    error_analysis_path = OUTPUT_DIR / "real_model_error_analysis.md"
    real_model_path = out_dir / "support_process_real_model_snapshots.json" if real_model_ran else out_dir / "__real_model_not_run__.json"
    error_analysis_path.write_text(render_error_analysis(real_model_path, real_model_status))
    print(f"Wrote {error_analysis_path}")


if __name__ == "__main__":
    main()

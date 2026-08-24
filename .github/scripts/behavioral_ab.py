#!/usr/bin/env python3
"""Run a repeatable behavioral A/B comparison for one Agent Skill.

The runner is deliberately provider-neutral: it invokes the same command for
the baseline and candidate skill roots, captures the text result, and emits
structured JSON. A model/API login is required for a real behavioral run.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


SCENARIOS: tuple[dict[str, str], ...] = (
    {
        "id": "apns-simulator-boundary",
        "skill": "push-notifications",
        "prompt": "An iOS app needs APNs registration, silent pushes, and a Simulator test. The proposed review says the iOS Simulator can never receive APNs device-token registration and recommends only physical-device testing. Review the proposal and state the correct Simulator/provider/device boundary.",
    },
    {
        "id": "extension-exact-once",
        "skill": "push-notifications",
        "prompt": "A Notification Service Extension starts async media work and also uses serviceExtensionTimeWillExpire(). Review how it must complete, including the race between the normal task and timeout, fallback content, and silent versus alerting payloads.",
    },
    {
        "id": "app-review-payment-rule",
        "skill": "storekit",
        "prompt": "Review an App Store payment plan that says every person-to-person service and every enterprise service can avoid In-App Purchase. Correct the current App Review boundaries and explain when storefront or entitlement evidence is required.",
    },
    {
        "id": "storekit-test-api",
        "skill": "storekit",
        "prompt": "Review StoreKit test code that calls product.purchase with purchaseDate(..., renewalBehavior: .default) and codeOffer. Separate production purchase APIs from StoreKit Test SKTestSession APIs and name the valid renewal behaviors.",
    },
    {
        "id": "cloudkit-sync-recovery",
        "skill": "cloudkit",
        "prompt": "Review a CloudKit sync plan that stores personal data in the public database, polls with a timer, retries throttling immediately, assumes CKSyncEngine resolves failedRecordSaves, and starts every fetch with a nil change token. Correct the design and give a focused verification matrix.",
    },
    {
        "id": "swift-charts-large-accessible",
        "skill": "swift-charts",
        "prompt": "Review a Swift Charts dashboard that renders 10,000 PointMarks individually, connects multiple series without a series encoding, fixes chart height at 200 points, omits accessibility labels, and compares chartAngleSelection directly to category strings. Give focused corrections.",
    },
    {
        "id": "carplay-template-boundary",
        "skill": "carplay",
        "prompt": "Review a CarPlay plan that draws arbitrary SwiftUI in the car window, pushes a CPTabBarTemplate, instantiates CPNowPlayingTemplate directly, ignores category entitlement limits, and may skip template completion handlers. Correct the template and lifecycle boundaries.",
    },
)


def resolve_skill(scenario: dict[str, str], override: str | None) -> str:
    """Use a scenario's skill unless a focused run explicitly overrides it."""

    return override or scenario["skill"]


def runner_command(
    runner: str,
    provider: str,
    model: str,
    root: Path,
    prompt: str,
    budget: str,
    output_path: Path | None = None,
) -> list[str]:
    """Build a non-interactive, read-only command for a supported model runner."""

    if provider == "codex":
        if output_path is None:
            raise ValueError("Codex runs require an output path")
        return [
            runner,
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--model",
            model,
            "--cd",
            str(root),
            "--output-last-message",
            str(output_path),
            prompt,
        ]
    if provider != "claude":
        raise ValueError(f"unsupported provider: {provider}")
    return [
        runner,
        "--bare",
        "--no-session-persistence",
        "--permission-mode",
        "dontAsk",
        "--model",
        model,
        "--max-budget-usd",
        budget,
        "-p",
        prompt,
        "--add-dir",
        str(root),
        "--output-format",
        "text",
    ]


def run_case(
    runner: str,
    provider: str,
    model: str,
    root: Path,
    skill: str,
    scenario: dict[str, str],
    timeout: int,
    budget: str,
) -> dict[str, Any]:
    skill_path = root / "skills" / skill / "SKILL.md"
    prompt = (
        "You are evaluating a documentation skill, not editing files. Read only "
        f"{skill_path} and the direct references it routes for this task. "
        f"{scenario['prompt']} Return exactly four short lines labeled "
        "COVERAGE, CORRECTNESS, ACTIONABILITY, and MISSED. Keep the response "
        "under 180 words and call out any incorrect claim."
    )
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="ios-skills-ab-") as directory:
        output_path = Path(directory) / "last-message.txt"
        command = runner_command(
            runner,
            provider,
            model,
            root,
            prompt,
            budget,
            output_path,
        )
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "text": "",
                "exit_code": None,
                "duration_ms": round((time.monotonic() - started) * 1000),
            }

        if provider == "codex" and output_path.is_file():
            output = output_path.read_text(encoding="utf-8").strip()
        else:
            output = (completed.stdout or completed.stderr).strip()
    duration_ms = round((time.monotonic() - started) * 1000)
    if completed.returncode != 0 or "Not logged in" in output:
        return {
            "status": "unavailable",
            "text": output,
            "exit_code": completed.returncode,
            "duration_ms": duration_ms,
        }
    return {
        "status": "ok",
        "text": output,
        "exit_code": completed.returncode,
        "duration_ms": duration_ms,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-root", type=Path, required=True)
    parser.add_argument("--new-root", type=Path, required=True)
    parser.add_argument(
        "--skill",
        help="Override the skill for every scenario in a focused run; otherwise each scenario selects its own skill.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=tuple(scenario["id"] for scenario in SCENARIOS),
        help="Run only the selected scenario; repeat the option to select multiple scenarios.",
    )
    parser.add_argument("--provider", choices=("claude", "codex"), default="claude")
    parser.add_argument("--runner", help="Runner executable; defaults to the provider name")
    parser.add_argument("--model", help="Model name; defaults to sonnet or gpt-5.4")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--budget-usd", default="0.20")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--allow-unavailable",
        action="store_true",
        help="Return success when the model runner is missing or not authenticated.",
    )
    args = parser.parse_args()

    runner = args.runner or args.provider
    model = args.model or ("sonnet" if args.provider == "claude" else "gpt-5.4")
    runner_path = shutil.which(runner)
    report: dict[str, Any] = {
        "provider": args.provider,
        "runner": runner,
        "model": model,
        "skill_override": args.skill,
        "scenario_filter": args.scenario,
        "old_root": str(args.old_root),
        "new_root": str(args.new_root),
        "scenarios": [],
    }
    if runner_path is None:
        report["status"] = "unavailable"
        report["error"] = f"runner not found: {runner}"
    else:
        selected_ids = set(args.scenario or ())
        selected_scenarios = tuple(
            scenario
            for scenario in SCENARIOS
            if not selected_ids or scenario["id"] in selected_ids
        )
        for scenario in selected_scenarios:
            scenario_skill = resolve_skill(scenario, args.skill)
            report["scenarios"].append(
                {
                    "id": scenario["id"],
                    "skill": scenario_skill,
                    "old": run_case(
                        runner_path,
                        args.provider,
                        model,
                        args.old_root,
                        scenario_skill,
                        scenario,
                        args.timeout_seconds,
                        args.budget_usd,
                    ),
                    "new": run_case(
                        runner_path,
                        args.provider,
                        model,
                        args.new_root,
                        scenario_skill,
                        scenario,
                        args.timeout_seconds,
                        args.budget_usd,
                    ),
                }
            )
        statuses = [
            side["status"]
            for scenario in report["scenarios"]
            for side in (scenario["old"], scenario["new"])
        ]
        report["status"] = "ok" if all(status == "ok" for status in statuses) else "partial"

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    if report["status"] == "ok":
        return 0
    return 0 if args.allow_unavailable else 2


if __name__ == "__main__":
    raise SystemExit(main())

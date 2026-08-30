#!/usr/bin/env python3
"""Verify that Agent Skills discovery exposes exactly the public catalog."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
DISCOVERED_SKILL_PATTERN = re.compile(
    r"^\s*│\s{4}([a-z0-9]+(?:-[a-z0-9]+)*)\s*$"
)
REPORTED_COUNT_PATTERN = re.compile(r"\bFound\s+(\d+)\s+skills?\b")


def parse_discovery_output(output: str) -> tuple[set[str], int | None]:
    clean_output = ANSI_ESCAPE_PATTERN.sub("", output).replace("\r", "\n")
    discovered = {
        match.group(1)
        for line in clean_output.splitlines()
        if (match := DISCOVERED_SKILL_PATTERN.match(line))
    }
    reported_counts = [
        int(match.group(1)) for match in REPORTED_COUNT_PATTERN.finditer(clean_output)
    ]
    return discovered, reported_counts[-1] if reported_counts else None


def expected_public_skills() -> set[str]:
    return {path.parent.name for path in SKILLS_DIR.glob("*/SKILL.md")}


def validation_errors(output: str) -> list[str]:
    discovered, reported_count = parse_discovery_output(output)
    expected = expected_public_skills()
    errors: list[str] = []

    if reported_count is None:
        errors.append("Agent Skills output did not report a discovery count")
    elif reported_count != len(discovered):
        errors.append(
            f"Agent Skills reported {reported_count} skills but the output listed "
            f"{len(discovered)} unique names"
        )

    missing = sorted(expected - discovered)
    unexpected = sorted(discovered - expected)
    if missing:
        errors.append(f"Missing public skills: {', '.join(missing)}")
    if unexpected:
        errors.append(f"Unexpected public skills: {', '.join(unexpected)}")
    return errors


def git_visible_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [
        Path(os.fsdecode(raw_path))
        for raw_path in result.stdout.split(b"\0")
        if raw_path
    ]


def repository_snapshot(destination: Path) -> None:
    for relative_path in git_visible_paths():
        source = ROOT / relative_path
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, target)


def run_discovery() -> tuple[int, str]:
    cli_path = ROOT / "node_modules" / "skills" / "bin" / "cli.mjs"
    if not cli_path.is_file():
        return 1, "Run npm ci before validating public discovery."
    node_path = shutil.which("node")
    if node_path is None:
        return 1, "Node.js is required to validate public discovery."

    with tempfile.TemporaryDirectory(prefix="ios-skills-discovery-") as directory:
        snapshot = Path(directory)
        repository_snapshot(snapshot)
        environment = os.environ.copy()
        environment.update(
            {
                "DISABLE_TELEMETRY": "1",
                "INSTALL_INTERNAL_SKILLS": "0",
            }
        )
        result = subprocess.run(
            [node_path, str(cli_path), "add", str(snapshot), "--list"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
    output = f"{result.stdout}\n{result.stderr}"
    return result.returncode, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="store_true",
        help="discover skills from a snapshot of Git-visible repository files",
    )
    args = parser.parse_args()

    if args.run:
        returncode, output = run_discovery()
        if returncode != 0:
            print(output.strip(), file=sys.stderr)
            return returncode
    else:
        output = sys.stdin.read()
    errors = validation_errors(output)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated exact public discovery of {len(expected_public_skills())} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

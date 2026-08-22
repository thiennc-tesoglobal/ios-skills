#!/usr/bin/env python3
"""Validate the repository's skills, evals, links, and distribution metadata."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"
PUBLISHED_EVALS_DIR = ROOT / "evals"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path, validation: Validation) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validation.error(f"Missing JSON file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as error:
        validation.error(f"Invalid JSON in {path.relative_to(ROOT)}: {error}")
    return None


def parse_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith(("\"", "'")):
        try:
            parsed = ast.literal_eval(value)
            return parsed if isinstance(parsed, str) else value
        except (SyntaxError, ValueError):
            return value.strip("\"'")
    return value


def parse_frontmatter(path: Path, validation: Validation) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        validation.error(f"Missing YAML frontmatter: {path.relative_to(ROOT)}")
        return {}

    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if field:
            values[field.group(1)] = parse_scalar(field.group(2))
    return values


def validate_local_links(path: Path, validation: Validation) -> set[str]:
    text = path.read_text(encoding="utf-8")
    linked_paths: set[str] = set()
    for target in MARKDOWN_LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative_target = target.split("#", 1)[0]
        if not relative_target:
            continue
        linked_paths.add(relative_target)
        if not (path.parent / relative_target).exists():
            validation.error(
                f"Broken local link in {path.relative_to(ROOT)}: {relative_target}"
            )
    return linked_paths


def validate_skill(path: Path, validation: Validation) -> tuple[str, int]:
    folder_name = path.parent.name
    frontmatter = parse_frontmatter(path, validation)
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if name != folder_name:
        validation.error(
            f"Skill name mismatch in {path.relative_to(ROOT)}: {name!r} != {folder_name!r}"
        )
    if not NAME_PATTERN.fullmatch(name):
        validation.error(f"Invalid skill name in {path.relative_to(ROOT)}: {name!r}")
    if not description:
        validation.error(f"Missing description in {path.relative_to(ROOT)}")
    elif len(description) > 1024:
        validation.error(
            f"Description exceeds 1024 characters in {path.relative_to(ROOT)}"
        )
    elif len(description) > 500:
        validation.error(
            f"Long discovery description ({len(description)} chars): {folder_name}"
        )

    line_count = len(path.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        validation.error(f"SKILL.md exceeds 500 lines ({line_count}): {folder_name}")
    elif line_count > 300:
        validation.warn(f"Large SKILL.md ({line_count} lines): {folder_name}")

    linked_paths = validate_local_links(path, validation)
    reference_files = {
        str(reference.relative_to(path.parent))
        for reference in (path.parent / "references").glob("*")
        if reference.is_file()
    }
    for unlinked in sorted(reference_files - linked_paths):
        validation.error(f"Unlinked reference in {folder_name}: {unlinked}")

    return folder_name, len(description)


def validate_local_evals(skill_name: str, validation: Validation) -> int:
    path = SKILLS_DIR / skill_name / "evals" / "evals.json"
    data = load_json(path, validation)
    if not isinstance(data, dict):
        return 0
    if data.get("skill_name") != skill_name:
        validation.error(f"Eval skill_name mismatch in {path.relative_to(ROOT)}")

    cases = data.get("evals")
    if not isinstance(cases, list) or not cases:
        validation.error(f"Missing eval cases in {path.relative_to(ROOT)}")
        return 0

    seen_ids: set[int | str] = set()
    seen_names: set[str] = set()
    for index, case in enumerate(cases, start=1):
        label = f"{path.relative_to(ROOT)} case {index}"
        if not isinstance(case, dict):
            validation.error(f"Eval is not an object: {label}")
            continue
        case_id = case.get("id")
        if case_id is None or case_id in seen_ids:
            validation.error(f"Missing or duplicate eval id: {label}")
        seen_ids.add(case_id)

        case_name = case.get("name")
        if not isinstance(case_name, str) or not NAME_PATTERN.fullmatch(case_name):
            validation.error(f"Missing or invalid eval name in {label}: {case_name!r}")
        elif case_name in seen_names:
            validation.error(f"Duplicate eval name in {label}: {case_name}")
        seen_names.add(case_name)

        for field in ("prompt", "expected_output"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                validation.error(f"Missing {field} in {label}")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions or not all(
            isinstance(assertion, str) and assertion.strip() for assertion in assertions
        ):
            validation.error(f"Invalid assertions in {label}")
        files = case.get("files")
        if not isinstance(files, list):
            validation.error(f"Invalid files list in {label}")
    return len(cases)


def skill_names_from_paths(paths: Any, label: str, validation: Validation) -> list[str]:
    if not isinstance(paths, list):
        validation.error(f"{label} must be a list")
        return []
    names: list[str] = []
    for value in paths:
        if not isinstance(value, str):
            validation.error(f"Non-string skill path in {label}: {value!r}")
            continue
        normalized = value.removeprefix("./")
        path = ROOT / normalized
        if not (path / "SKILL.md").is_file():
            validation.error(f"Unknown skill path in {label}: {value}")
        names.append(Path(normalized).name)
    if len(names) != len(set(names)):
        validation.error(f"Duplicate skill entries in {label}")
    return names


def validate_distribution(skill_names: set[str], validation: Validation) -> None:
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path, validation)
    marketplace_version: str | None = None
    if isinstance(marketplace, dict):
        metadata = marketplace.get("metadata")
        if isinstance(metadata, dict) and isinstance(metadata.get("version"), str):
            marketplace_version = metadata["version"]
        else:
            validation.error("Missing marketplace metadata version")
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            validation.error("marketplace.json plugins must be a list")
        else:
            all_bundle: set[str] | None = None
            for plugin in plugins:
                if not isinstance(plugin, dict):
                    validation.error("Invalid plugin entry in marketplace.json")
                    continue
                plugin_name = plugin.get("name", "<unnamed>")
                if plugin.get("version") != marketplace_version:
                    validation.error(
                        f"Version mismatch in marketplace plugin {plugin_name}"
                    )
                bundle_names = set(
                    skill_names_from_paths(
                        plugin.get("skills"),
                        f"marketplace plugin {plugin_name}",
                        validation,
                    )
                )
                if plugin_name == "all-ios-skills":
                    all_bundle = bundle_names
            if all_bundle is None:
                validation.error("Missing all-ios-skills marketplace bundle")
            elif all_bundle != skill_names:
                validation.error(
                    "all-ios-skills membership does not match the skills directory"
                )

    tessl_path = ROOT / ".tessl-plugin" / "plugin.json"
    tessl = load_json(tessl_path, validation)
    if isinstance(tessl, dict):
        if tessl.get("version") != marketplace_version:
            validation.error("Tessl and marketplace versions do not match")
        tessl_names = set(
            skill_names_from_paths(tessl.get("skills"), "Tessl plugin", validation)
        )
        if tessl_names != skill_names:
            validation.error("Tessl skill membership does not match the skills directory")


def validate_published_evals(
    skill_names: set[str], validation: Validation
) -> int:
    count = 0
    coverage = {skill_name: 0 for skill_name in skill_names}
    skill_prefixes = sorted(skill_names, key=len, reverse=True)
    for directory in sorted(path for path in PUBLISHED_EVALS_DIR.iterdir() if path.is_dir()):
        count += 1
        matching_skill = next(
            (
                skill_name
                for skill_name in skill_prefixes
                if directory.name == skill_name
                or directory.name.startswith(f"{skill_name}-")
            ),
            None,
        )
        if matching_skill is None:
            validation.error(
                f"Published eval does not map to a known skill: {directory.name}"
            )
        else:
            coverage[matching_skill] += 1

        required = {"capability.txt", "task.md", "criteria.json"}
        present = {path.name for path in directory.iterdir() if path.is_file()}
        missing = required - present
        if missing:
            validation.error(
                f"Published eval {directory.name} is missing: {', '.join(sorted(missing))}"
            )
            continue
        criteria = load_json(directory / "criteria.json", validation)
        if not isinstance(criteria, dict):
            continue
        if criteria.get("type") != "weighted_checklist":
            validation.error(f"Unexpected criteria type in eval {directory.name}")
        checklist = criteria.get("checklist")
        if not isinstance(checklist, list) or not checklist:
            validation.error(f"Missing criteria checklist in eval {directory.name}")
            continue
        score = sum(
            item.get("max_score", 0) for item in checklist if isinstance(item, dict)
        )
        if score != 100:
            validation.error(
                f"Criteria weights total {score}, expected 100: {directory.name}"
            )

    for skill_name, scenario_count in sorted(coverage.items()):
        if scenario_count == 0:
            validation.error(f"No published eval scenario covers skill: {skill_name}")
    return count


def main() -> int:
    validation = Validation()
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    skill_results = [validate_skill(path, validation) for path in skill_files]
    skill_names = {name for name, _ in skill_results}
    skill_names.discard("")
    total_description_chars = sum(length for _, length in skill_results)
    if total_description_chars > 32000:
        validation.error(
            "Combined discovery descriptions exceed the 32000-character "
            f"repository budget: {total_description_chars}"
        )
    validate_local_links(ROOT / "README.md", validation)

    local_eval_count = sum(
        validate_local_evals(skill_name, validation)
        for skill_name in sorted(skill_names)
    )
    published_eval_count = validate_published_evals(skill_names, validation)
    validate_distribution(skill_names, validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    print(
        "Validated "
        f"{len(skill_names)} skills, {local_eval_count} local eval cases, "
        f"{published_eval_count} published eval scenarios, and "
        f"{total_description_chars} discovery-description characters."
    )
    if validation.errors:
        print(f"Validation failed with {len(validation.errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validation passed with {len(validation.warnings)} advisory warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / ".github" / "scripts" / "validate_public_discovery.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location("discovery_validator", VALIDATOR)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
VALIDATOR_MODULE = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


class PublicDiscoveryTests(unittest.TestCase):
    def test_release_snapshot_excludes_ignored_maintainer_state(self) -> None:
        visible_paths = VALIDATOR_MODULE.git_visible_paths()

        self.assertIn(Path("skills/ios-app-workflow/SKILL.md"), visible_paths)
        self.assertFalse(any(path.parts[0] == ".claude" for path in visible_paths))

    def test_parses_ansi_spinner_output(self) -> None:
        output = (
            "\x1b[?25l◇  Found \x1b[32m2\x1b[0m skills\r\n"
            "│\n"
            "│    first-skill\n"
            "│\n"
            "│      First description.\n"
            "│\n"
            "│    second-skill\n"
        )

        self.assertEqual(
            VALIDATOR_MODULE.parse_discovery_output(output),
            ({"first-skill", "second-skill"}, 2),
        )

    def test_rejects_missing_and_unexpected_skills(self) -> None:
        expected = VALIDATOR_MODULE.expected_public_skills()
        missing = min(expected)
        listed = sorted((expected - {missing}) | {"internal-maintainer-skill"})
        output = "◇  Found {} skills\n{}".format(
            len(listed),
            "\n".join(f"│    {name}" for name in listed),
        )

        errors = VALIDATOR_MODULE.validation_errors(output)

        self.assertTrue(
            any(
                error.startswith("Missing public skills:") and missing in error
                for error in errors
            )
        )
        self.assertIn(
            "Unexpected public skills: internal-maintainer-skill",
            errors,
        )


if __name__ == "__main__":
    unittest.main()

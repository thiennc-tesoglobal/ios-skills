import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / ".github" / "scripts" / "validate_repository.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location("ios_validator", VALIDATOR)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
VALIDATOR_MODULE = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


class RepositoryStructureTests(unittest.TestCase):
    def test_repository_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}",
        )

    def test_release_changelog_requires_finalized_date(self) -> None:
        version = VALIDATOR_MODULE.EXPECTED_VERSION
        self.assertEqual(
            VALIDATOR_MODULE.release_changelog_errors(f"## {version} - Unreleased\n"),
            [
                f"release metadata requires '## {version} - YYYY-MM-DD'; "
                "the version must not remain Unreleased"
            ],
        )
        self.assertEqual(
            VALIDATOR_MODULE.release_changelog_errors(
                f"## {version} - 2026-08-24\n"
            ),
            [],
        )
        self.assertTrue(
            VALIDATOR_MODULE.release_changelog_errors(
                f"## {version} - 2026-02-30\n"
            )
        )


if __name__ == "__main__":
    unittest.main()

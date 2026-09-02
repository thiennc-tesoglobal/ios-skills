import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "typecheck_skill_fixtures.sh"


class CompileFixtureTests(unittest.TestCase):
    def test_script_has_noninteractive_help(self) -> None:
        result = subprocess.run(
            [str(SCRIPT), "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("stable|beta", result.stdout)

    def test_script_rejects_unknown_lane(self) -> None:
        result = subprocess.run(
            [str(SCRIPT), "nightly"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 64)
        self.assertIn("stable|beta", result.stderr)

    def test_expected_fixture_inventory(self) -> None:
        stable = {path.name for path in (ROOT / ".github/compile-fixtures/stable").glob("*.swift")}
        beta = {path.name for path in (ROOT / ".github/compile-fixtures/beta").glob("*.swift")}

        self.assertEqual(
            stable,
            {
                "HapticPattern.swift",
                "EnergyKitGuidance.swift",
                "MetricKitLegacy.swift",
                "SwiftConcurrency.swift",
                "SwiftDataModel.swift",
            },
        )
        self.assertEqual(beta, {"EnergyKitModern.swift", "MetricKitModern.swift"})


if __name__ == "__main__":
    unittest.main()

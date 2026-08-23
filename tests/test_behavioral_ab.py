import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AB = load_script("behavioral_ab", ".github/scripts/behavioral_ab.py")


class BehavioralABTests(unittest.TestCase):
    def test_builtin_scenarios_route_to_their_own_skills(self) -> None:
        routing = {scenario["id"]: scenario["skill"] for scenario in AB.SCENARIOS}

        self.assertEqual(routing["apns-simulator-boundary"], "push-notifications")
        self.assertEqual(routing["extension-exact-once"], "push-notifications")
        self.assertEqual(routing["app-review-payment-rule"], "storekit")
        self.assertEqual(routing["storekit-test-api"], "storekit")
        self.assertEqual(
            AB.resolve_skill(AB.SCENARIOS[3], None),
            "storekit",
        )
        self.assertEqual(
            AB.resolve_skill(AB.SCENARIOS[3], "push-notifications"),
            "push-notifications",
        )

    def test_runner_report_records_resolved_skill_per_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for skill in ("push-notifications", "storekit"):
                skill_path = root / "skills" / skill
                skill_path.mkdir(parents=True)
                (skill_path / "SKILL.md").write_text("# test\n", encoding="utf-8")

            output = io.StringIO()
            with mock.patch.object(
                sys,
                "argv",
                [
                    "behavioral_ab.py",
                    "--old-root",
                    str(root),
                    "--new-root",
                    str(root),
                    "--runner",
                    "/bin/echo",
                ],
            ), redirect_stdout(output):
                status = AB.main()

        report = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(report["skill_override"], None)
        self.assertEqual(
            [scenario["skill"] for scenario in report["scenarios"]],
            [
                "push-notifications",
                "push-notifications",
                "storekit",
                "storekit",
            ],
        )
        self.assertIn(
            "skills/push-notifications/SKILL.md",
            report["scenarios"][0]["old"]["text"],
        )
        self.assertIn(
            "skills/storekit/SKILL.md",
            report["scenarios"][2]["old"]["text"],
        )
        self.assertTrue(all(scenario["old"]["status"] == "ok" for scenario in report["scenarios"]))


if __name__ == "__main__":
    unittest.main()

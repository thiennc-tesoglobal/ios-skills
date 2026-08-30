import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / ".github" / "scripts" / "check_sosumi_links.py"
CHECKER_SPEC = importlib.util.spec_from_file_location("sosumi_checker", CHECKER)
assert CHECKER_SPEC is not None and CHECKER_SPEC.loader is not None
CHECKER_MODULE = importlib.util.module_from_spec(CHECKER_SPEC)
CHECKER_SPEC.loader.exec_module(CHECKER_MODULE)


class SosumiLinkTests(unittest.TestCase):
    def test_normalizes_markdown_links_with_swift_parentheses(self) -> None:
        self.assertEqual(
            CHECKER_MODULE.normalize_url(
                "https://sosumi.ai/documentation/example/method(_:))"
            ),
            "https://sosumi.ai/documentation/example/method(_:)",
        )

    def test_discovers_bare_and_markdown_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "SKILL.md"
            path.write_text(
                "[API](https://sosumi.ai/documentation/example/method(_:))\n"
                "[https://sosumi.ai/videos/play/example/1]"
                "(https://sosumi.ai/videos/play/example/1)\n"
                "Bare: https://sosumi.ai/documentation/example/type\n",
                encoding="utf-8",
            )

            links = CHECKER_MODULE.discover_sosumi_links(root)

        self.assertEqual(
            set(links),
            {
                "https://sosumi.ai/documentation/example/method(_:)",
                "https://sosumi.ai/documentation/example/type",
                "https://sosumi.ai/videos/play/example/1",
            },
        )


if __name__ == "__main__":
    unittest.main()

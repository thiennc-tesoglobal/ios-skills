import importlib.util
import io
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch


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

    def test_success_needs_one_request(self) -> None:
        url = "https://sosumi.ai/documentation/example"
        response = MagicMock()
        response.__enter__.return_value.status = 200
        with patch.object(
            CHECKER_MODULE.urllib.request, "urlopen", return_value=response
        ) as fetch:
            self.assertEqual(CHECKER_MODULE.check_url(url, 20), (url, None))
        fetch.assert_called_once()
        self.assertEqual(fetch.call_args.kwargs["timeout"], 20)

    def test_permanent_http_errors_are_not_retried(self) -> None:
        url = "https://sosumi.ai/documentation/example"
        for status in (403, 404, 410):
            with self.subTest(status=status):
                error = urllib.error.HTTPError(url, status, "error", {}, io.BytesIO())
                with patch.object(
                    CHECKER_MODULE.urllib.request, "urlopen", side_effect=error
                ) as fetch, patch.object(CHECKER_MODULE.time, "sleep") as sleep:
                    self.assertEqual(
                        CHECKER_MODULE.check_url(url, 20), (url, f"HTTP {status}")
                    )
                fetch.assert_called_once()
                sleep.assert_not_called()

    def test_transient_failures_recover_on_retry(self) -> None:
        url = "https://sosumi.ai/documentation/example"
        errors = [
            urllib.error.HTTPError(url, status, "error", {}, io.BytesIO())
            for status in (408, 429, 500, 502, 503, 504)
        ] + [
            urllib.error.URLError("DNS unavailable"),
            TimeoutError("timed out"),
            ConnectionResetError("reset"),
        ]
        for error in errors:
            with self.subTest(error=str(error)):
                response = MagicMock()
                response.__enter__.return_value.status = 200
                with patch.object(
                    CHECKER_MODULE.urllib.request, "urlopen", side_effect=[error, response]
                ) as fetch, patch.object(CHECKER_MODULE.time, "sleep") as sleep:
                    self.assertEqual(CHECKER_MODULE.check_url(url, 20), (url, None))
                self.assertEqual(fetch.call_count, 2)
                sleep.assert_called_once_with(2)

    def test_persistent_outage_fails_after_three_attempts(self) -> None:
        url = "https://sosumi.ai/documentation/example"
        for error, expected in (
            (urllib.error.HTTPError(url, 503, "error", {}, io.BytesIO()), "HTTP 503"),
            (TimeoutError("timed out"), "timed out"),
        ):
            with self.subTest(error=expected):
                with patch.object(
                    CHECKER_MODULE.urllib.request, "urlopen", side_effect=error
                ) as fetch, patch.object(CHECKER_MODULE.time, "sleep") as sleep:
                    self.assertEqual(
                        CHECKER_MODULE.check_url(url, 20), (url, expected)
                    )
                self.assertEqual(fetch.call_count, 3)
                self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 4])

    def test_retry_stops_if_next_response_is_not_found(self) -> None:
        url = "https://sosumi.ai/documentation/example"
        errors = [
            urllib.error.HTTPError(url, status, "error", {}, io.BytesIO())
            for status in (503, 404)
        ]
        with patch.object(
            CHECKER_MODULE.urllib.request, "urlopen", side_effect=errors
        ) as fetch, patch.object(CHECKER_MODULE.time, "sleep") as sleep:
            self.assertEqual(CHECKER_MODULE.check_url(url, 20), (url, "HTTP 404"))
        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once_with(2)


if __name__ == "__main__":
    unittest.main()

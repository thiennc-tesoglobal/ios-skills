#!/usr/bin/env python3
"""Check Sosumi documentation links in public skill Markdown files."""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"
SOSUMI_URL_PATTERN = re.compile(r"https://sosumi\.ai/[^\s<>\"'\]]+")
TRAILING_PUNCTUATION = ".,;:!?"


def normalize_url(raw_url: str) -> str:
    url = raw_url.rstrip(TRAILING_PUNCTUATION)
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def discover_sosumi_links(root: Path = SKILLS_DIR) -> dict[str, list[Path]]:
    links: dict[str, list[Path]] = {}
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in SOSUMI_URL_PATTERN.finditer(text):
            url = normalize_url(match.group(0))
            links.setdefault(url, []).append(path)
    return links


def check_url(url: str, timeout: float) -> tuple[str, str | None]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ios-skills-link-checker/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        return url, f"HTTP {error.code}"
    except (urllib.error.URLError, TimeoutError) as error:
        return url, str(error)
    if status >= 400:
        return url, f"HTTP {status}"
    return url, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    links = discover_sosumi_links()
    failures: list[tuple[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(check_url, url, args.timeout): url for url in links
        }
        for future in concurrent.futures.as_completed(futures):
            url, error = future.result()
            if error is not None:
                failures.append((url, error))

    for url, error in sorted(failures):
        paths = ", ".join(
            str(path.relative_to(ROOT)) for path in sorted(set(links[url]))
        )
        print(f"ERROR: {error}: {url} ({paths})", file=sys.stderr)

    if failures:
        print(
            f"Sosumi link check failed for {len(failures)} of {len(links)} URLs.",
            file=sys.stderr,
        )
        return 1
    print(f"Validated {len(links)} unique Sosumi documentation links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

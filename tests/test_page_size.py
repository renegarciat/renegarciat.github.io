"""Page-weight tests (see README).

Adds up index.html plus every local file it pulls in (stylesheets, images,
scripts, and anything referenced by url() inside local CSS) and checks the
total stays under budget. Uses only the standard library:

    python3 -m unittest discover tests -v

External resources (e.g. Google Fonts) can't be measured offline, so they
are listed in the output but not counted.
"""

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
BUDGET_BYTES = 5 * 1024 * 1024  # 5 MB (softened budget to accommodate 40+ gallery photos)

CSS_URL = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""")
CSS_IMPORT = re.compile(r"""@import\s+['"]([^'"]+)['"]""")


class ResourceCollector(HTMLParser):
    """Collects src/href of tags the browser actually downloads.

    Commented-out markup is ignored, since HTMLParser hands comments to
    handle_comment rather than handle_starttag.
    """

    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("img", "script", "source", "video", "audio") and attrs.get("src"):
            self.refs.append(attrs["src"])
        if tag == "link" and attrs.get("href"):
            rel = (attrs.get("rel") or "").lower()
            if rel in ("stylesheet", "icon", "shortcut icon", "preload", "apple-touch-icon"):
                self.refs.append(attrs["href"])


def is_external(ref):
    return bool(urlparse(ref).scheme) or ref.startswith("//")


def collect_resources():
    """Return (local Paths, external URLs) needed to render the page."""
    parser = ResourceCollector()
    parser.feed(PAGE.read_text(encoding="utf-8"))

    local, external = {PAGE.resolve()}, set()
    queue = [(ref, ROOT) for ref in parser.refs]
    while queue:
        ref, base = queue.pop()
        if ref.startswith("data:") or ref.startswith("#"):
            continue
        if is_external(ref):
            external.add(ref)
            continue
        path = (base / urlparse(ref).path).resolve()
        if path in local:
            continue
        local.add(path)
        if path.suffix == ".css" and path.exists():
            css = path.read_text(encoding="utf-8")
            for found in CSS_URL.findall(css) + CSS_IMPORT.findall(css):
                queue.append((found, path.parent))
    return sorted(local), sorted(external)


def human(n):
    return f"{n / 1024:,.1f} KB"


class PageSizeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local, cls.external = collect_resources()
        if cls.external:
            print("\nExternal resources (not counted):")
            for url in cls.external:
                print(f"  {url}")

    def test_referenced_files_exist(self):
        missing = [str(p.relative_to(ROOT)) for p in self.local if not p.exists()]
        self.assertEqual(missing, [], "index.html references files that don't exist")

    def test_total_page_weight_under_budget(self):
        sizes = sorted(
            ((p.stat().st_size, p) for p in self.local if p.exists()), reverse=True
        )
        total = sum(size for size, _ in sizes)
        breakdown = "\n".join(
            f"  {human(size):>12}  {p.relative_to(ROOT)}" for size, p in sizes
        )
        self.assertLessEqual(
            total,
            BUDGET_BYTES,
            f"Page weighs {human(total)}, budget is {human(BUDGET_BYTES)} "
            f"({human(total - BUDGET_BYTES)} over):\n{breakdown}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

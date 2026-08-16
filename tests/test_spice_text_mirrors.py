"""Ensure browser-viewable SPICE files remain identical to canonical decks."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r'href=["\'](?P<url>[^"\']+\.cir(?:\.txt)?)["\']')


class SpiceTextMirrorTests(unittest.TestCase):
    def test_every_text_mirror_matches_its_cir_source(self):
        mirrors = sorted(ROOT.rglob("*.cir.txt"))
        self.assertGreater(len(mirrors), 0)
        for mirror in mirrors:
            source = Path(str(mirror)[:-4])
            self.assertTrue(source.is_file(), source)
            self.assertEqual(source.read_bytes(), mirror.read_bytes(), mirror)

    def test_html_spice_links_use_existing_text_mirrors(self):
        html_files = [ROOT / "capstone.html", ROOT / "development-journey.html"]
        html_files.extend(
            path
            for path in (ROOT / "docs").glob("*.html")
            if not path.name.startswith("Top 10 fundamental")
        )

        links: list[tuple[Path, str]] = []
        for html in html_files:
            for match in LINK_RE.finditer(html.read_text(encoding="utf-8")):
                links.append((html, match.group("url")))

        self.assertGreater(len(links), 0)
        for html, url in links:
            self.assertTrue(url.endswith(".cir.txt"), (html, url))
            target = (html.parent / url).resolve()
            self.assertTrue(target.is_file(), target)


if __name__ == "__main__":
    unittest.main()

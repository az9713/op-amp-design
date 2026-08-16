"""Ensure browser-viewable SPICE files remain identical to canonical decks."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r'href=["\'](?P<url>[^"\']*spice-viewer\.html\?deck=[^"\']+)["\']')


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
            parsed = urlparse(url)
            self.assertTrue(parsed.path.endswith("spice-viewer.html"), (html, url))
            deck = unquote(parse_qs(parsed.query)["deck"][0])
            self.assertTrue(deck.endswith(".cir.txt"), (html, url))
            target = (ROOT / deck).resolve()
            self.assertTrue(target.is_file(), target)

        capstone = (ROOT / "capstone.html").read_text(encoding="utf-8")
        self.assertIn('"docs/spice-viewer.html?deck="', capstone)


if __name__ == "__main__":
    unittest.main()

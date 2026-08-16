"""Drive the shipped schematics.html through the Arrow connection checker."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "check_schematic_connections.py"
HTML = ROOT / "schematics.html"

sys.path.insert(0, str(ROOT))
from check_schematic_connections import check_diagram  # noqa: E402


class TestShippedSchematics(unittest.TestCase):
    def test_checker_exists(self):
        self.assertTrue(CHECKER.is_file(), CHECKER)
        self.assertTrue(HTML.is_file(), HTML)

    def test_shipped_html_passes_arrow_rules(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CHECKER),
                "--html",
                str(HTML),
                "--attempt-log",
                str(ROOT / "attempt-log.txt"),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn("diagrams: 24", proc.stdout)
        self.assertEqual(
            proc.returncode,
            0,
            msg=proc.stdout + proc.stderr,
        )
        self.assertNotIn("wire crosses triangle", proc.stdout)

    def test_crossing_segment_is_a_failure(self):
        svg = {
            "aria": "synthetic cross",
            "raw": """
              <use href="#oa" x="100" y="100"/>
              <line x1="50" y1="84" x2="100" y2="84"/>
              <use href="#dot" x="70" y="84"/>
              <line x1="70" y1="84" x2="70" y2="50"/>
              <line x1="70" y1="50" x2="200" y2="50"/>
              <line x1="200" y1="50" x2="200" y2="100"/>
              <use href="#dot" x="200" y="100"/>
              <line x1="174" y1="100" x2="220" y2="100"/>
              <line x1="84" y1="116" x2="100" y2="116"/>
              <use href="#gnd" x="84" y="116"/>
              <line x1="40" y1="140" x2="180" y2="60"/>
            """,
        }
        fails = check_diagram(svg)
        self.assertTrue(
            any("crosses triangle" in f for f in fails),
            msg=fails,
        )

    def test_unmarked_tjoin_is_a_failure(self):
        svg = {
            "aria": "synthetic tjoin",
            "raw": """
              <line x1="0" y1="50" x2="100" y2="50"/>
              <line x1="50" y1="50" x2="50" y2="80"/>
            """,
        }
        fails = check_diagram(svg)
        self.assertTrue(
            any("unmarked T-join" in f for f in fails),
            msg=fails,
        )


if __name__ == "__main__":
    unittest.main()

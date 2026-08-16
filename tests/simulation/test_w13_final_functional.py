"""Regression checks for the executable Week 13 final demonstration."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "simulations" / "week13" / "run_final_demo.py"
DECK = ROOT / "simulations" / "week13" / "w13-final_build-functional.cir"
RECEIPT = ROOT / "simulations" / "week13" / "w13-final_build-functional.receipt.json"


class Week13FinalFunctionalTests(unittest.TestCase):
    def test_deck_runs_and_all_functional_gates_pass(self):
        completed = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertTrue(receipt["simulation_passed"])
        self.assertTrue(all(receipt["gates"].values()), receipt["gates"])
        self.assertEqual(receipt["canonical_source"], "generated/week13/w13-final_build-ideal.cir")

    def test_deck_contains_the_nine_required_demo_elements(self):
        text = DECK.read_text(encoding="utf-8")
        required = (
            ".subckt OPAMP_LP",
            ".model SW_LOAD",
            "RL_MAIN=1k",
            "CL_OUT=47u",
            "VOSC_SQUARE",
            "BOSC_TRI",
            "XREG_ERR",
            "R_TWIN_DRIVE",
            "R_TWIN_LEAK",
            "tran 50u 350m",
            "meas tran REG_OFF",
            "meas tran REG_ON",
            "wrdata simulations/week13/w13-final_build-functional.csv",
        )
        for token in required:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()

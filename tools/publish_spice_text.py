#!/usr/bin/env python3
"""Create browser-viewable text mirrors of tracked SPICE ``.cir`` decks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked_decks() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.cir"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if a text mirror is absent or differs from its .cir source",
    )
    args = parser.parse_args()

    failures: list[str] = []
    decks = tracked_decks()
    for deck in decks:
        mirror = Path(f"{deck}.txt")
        source = deck.read_bytes()
        if args.check:
            if not mirror.is_file():
                failures.append(f"missing: {mirror.relative_to(ROOT)}")
            elif mirror.read_bytes() != source:
                failures.append(f"different: {mirror.relative_to(ROOT)}")
        else:
            mirror.write_bytes(source)

    if failures:
        print("SPICE text mirror check failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    action = "verified" if args.check else "wrote"
    print(f"PASS: {action} {len(decks)} SPICE text mirrors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

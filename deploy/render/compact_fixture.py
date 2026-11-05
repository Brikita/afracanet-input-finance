"""Build fresh labelled public fixtures; never read an operator's local stores."""

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def build(destination):
    from scripts.connected.cohorts import build_overlay
    from scripts.connected.load_relational import verify_overlay, verify_pack
    from scripts.synthetic.generator import generate

    destination.mkdir(parents=True, exist_ok=False)
    pack, overlay = destination / "pack", destination / "overlay"
    generate(pack, farmers=32, months=12, as_of=date(2026, 10, 26))
    build_overlay(pack, overlay)
    verify_pack(pack)
    verify_overlay(pack, overlay)
    # The serving image only needs a small read-only replay file plus the overlay.
    # No credentials, officers, sessions, signing material or payment records are built.
    with sqlite3.connect(pack / "scenario.sqlite") as replay:
        replay.execute("PRAGMA integrity_check").fetchone()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    build(parser.parse_args().destination)

"""Build isolated, labelled graph and relational scenario packs without network calls."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.synthetic.generator import PROFILES, generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default="walkthrough")
    parser.add_argument("--farmers", type=int)
    parser.add_argument("--months", type=int)
    parser.add_argument("--seed", type=int, default=20261026)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date(2026, 10, 26))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = generate(
        args.output, args.profile, args.farmers, args.months, args.seed, args.as_of
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()

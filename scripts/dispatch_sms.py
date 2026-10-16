"""Process durable SMS jobs once. No automatic retry of uncertain sends."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import db, notifications
from backend.config import settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    settings.validate()
    db.initialize()
    count = notifications.dispatch_pending(limit=args.limit)
    print(json.dumps({"processed": count, "mode": settings.sms_mode,
        "note": "SIMULATED means no gateway call; ACCEPTED means sandbox acceptance, not handset delivery."}))


if __name__ == "__main__":
    main()

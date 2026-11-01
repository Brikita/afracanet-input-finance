"""Create an individual local officer account without a command-line password."""

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Backend.identity import provision

parser = argparse.ArgumentParser()
parser.add_argument("officer_id")
parser.add_argument("lender_id")
args = parser.parse_args()
password = getpass.getpass("New individual officer password (16+ characters): ")
if password != getpass.getpass("Confirm password: "):
    raise SystemExit("Passwords do not match.")
provision(args.officer_id, args.lender_id, password)
print(
    "Officer account created. Enroll the officer in the receiver's public-key trust policy separately."
)

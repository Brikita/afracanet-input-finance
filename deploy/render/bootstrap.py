"""Initialize one service's fresh synthetic store, then preserve it across starts.

This process never loads .env files, resets an existing store, contacts PayPal,
or shares a signing key. Public trust export is an explicit operator handoff.
"""

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CREDIT = ROOT / "modules/credit-intelligence"


def prepare(service, fixture, data):
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    os.environ["INPUT_ENV_FILE"] = os.devnull
    os.environ["CREDIT_ENV_FILE"] = os.devnull
    sys.path.insert(0, str(ROOT))
    pack, overlay = fixture / "pack", fixture / "overlay"
    manifest = json.loads((pack / "manifest.json").read_text())
    if (
        manifest.get("source_kind") != "synthetic_replay"
        or manifest.get("farmers") != 32
    ):
        raise ValueError("Only the compact labelled synthetic fixture is accepted.")
    fingerprint = hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    data.mkdir(parents=True, exist_ok=True)
    marker = data / "bootstrap.json"
    database = data / ("inputs.sqlite" if service == "inputs" else "workflow.sqlite")
    if marker.exists():
        previous = json.loads(marker.read_text())
        if previous != {"service": service, "manifest_sha256": fingerprint}:
            raise ValueError(
                "Dataset or service changed. Explicit migration is required."
            )
        if not database.is_file():
            raise ValueError("Bootstrap marker exists but its database is missing.")
        if service == "credit" and not all(
            (data / name).is_file()
            for name in ("signing.pem", "replay.sqlite", "public-trust.json")
        ):
            raise ValueError(
                "Credit bootstrap is incomplete; restore its persistent disk."
            )
    else:
        if database.exists() or any(data.iterdir()):
            raise ValueError(
                "Fresh initialization requires an empty service data directory."
            )
        from scripts.connected.load_relational import verify_overlay, verify_pack

        verify_pack(pack)
        verify_overlay(pack, overlay)
        if service == "inputs":
            os.environ["DATABASE_URL"] = "sqlite:///" + database.as_posix()
            os.environ["SEED_DEMO_DATA"] = "0"
            from scripts.connected.load_execution import load_execution

            load_execution(pack, overlay)
        else:
            initialize_credit(pack, overlay, data, database, fingerprint)
        marker.write_text(
            json.dumps({"service": service, "manifest_sha256": fingerprint})
        )
    if service == "inputs":
        os.environ["DATABASE_URL"] = "sqlite:///" + database.as_posix()
        os.environ["SEED_DEMO_DATA"] = "0"
    else:
        sys.path.insert(0, str(CREDIT))
        credit_environment(data, database)
    return {
        "service": service,
        "source_kind": "synthetic_replay",
        "preserved": database.is_file(),
    }


def credit_environment(data, database):
    os.environ.update(
        CREDIT_DATA_DIR=data.as_posix(),
        CREDIT_DATABASE_URL="sqlite:///" + database.as_posix(),
        REPLAY_SQLITE_FILE=(data / "replay.sqlite").as_posix(),
        CREDIT_SIGNING_KEY_FILE=(data / "signing.pem").as_posix(),
        CREDIT_SIGNING_KEY_IDS=json.dumps(
            {f"SYN-LENDER-{i:03d}": f"render-lender-{i:03d}" for i in range(4)}
        ),
    )


def initialize_credit(pack, overlay, data, database, fingerprint):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    sys.path.insert(0, str(CREDIT))
    credit_environment(data, database)
    replay = data / "replay.sqlite"
    shutil.copyfile(pack / "scenario.sqlite", replay)
    with sqlite3.connect(replay) as conn:
        conn.execute("CREATE TABLE dataset_manifest(fingerprint TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO dataset_manifest VALUES (?)", (fingerprint,))
        conn.execute(
            "CREATE TABLE inventory(product_id TEXT PRIMARY KEY,supplier_id TEXT,tenant_id TEXT,opening_units INTEGER,stock_units INTEGER,reserved_units INTEGER,fulfilled_units INTEGER)"
        )
        with sqlite3.connect(overlay / "workflow.sqlite") as source:
            conn.executemany(
                "INSERT INTO inventory VALUES (?,?,?,?,?,?,?)",
                source.execute("SELECT * FROM inventory"),
            )
    private = Ed25519PrivateKey.generate()
    key_file = data / "signing.pem"
    key_file.write_bytes(
        private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    key_file.chmod(0o600)
    public = base64.b64encode(
        private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode()
    trust = {
        f"render-lender-{i:03d}": {
            "enabled": True,
            "public_key": public,
            "lender_id": f"SYN-LENDER-{i:03d}",
            "officer_ids": [f"officer-synthetic-{i:03d}"],
        }
        for i in range(4)
    }
    (data / "public-trust.json").write_text(json.dumps(trust, indent=2))
    # Load the module-owned operator tool by path; do not merge its namespace
    # with the root scripts package or import any historical environment.
    spec = importlib.util.spec_from_file_location(
        "credit_case_loader", CREDIT / "scripts/load_workflow_cases.py"
    )
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    loader.load(overlay)
    (data / "local-officer-accounts.json").chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("service", choices=["inputs", "credit"])
    parser.add_argument("--fixture", type=Path, default=ROOT / "fixture")
    parser.add_argument("--data", type=Path, default=Path("/var/data/afracanet"))
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    report = prepare(args.service, args.fixture.resolve(), args.data.resolve())
    print(json.dumps(report), flush=True)
    if args.serve:
        if args.service == "credit":
            os.chdir(CREDIT)
        else:
            os.chdir(ROOT)
        os.execv(
            sys.executable,
            [
                sys.executable,
                "-m",
                "uvicorn",
                "Backend.main:app" if args.service == "credit" else "backend.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                os.getenv("PORT", "10000"),
            ],
        )


if __name__ == "__main__":
    main()

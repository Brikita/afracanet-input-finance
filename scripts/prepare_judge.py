"""Create a compact, isolated fictional judge profile; never copy local secrets."""

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDIT = ROOT / "modules/credit-intelligence"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CREDIT))


def profile_paths(name):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name):
        raise ValueError("Use a short profile name, not a path.")
    return ROOT / "data/judge" / name, CREDIT / "data/judge" / name


def private_text(path, value):
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


def write_env(path, fields):
    from dotenv import set_key

    private_text(
        path,
        "# Generated isolated fictional judge profile. No live provider settings.\n",
    )
    for key, value in fields.items():
        set_key(path, key, str(value))


def prepare(name):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from scripts.connected.cohorts import build_overlay
    from scripts.connected.load_relational import verify_overlay, verify_pack
    from scripts.synthetic.generator import generate

    public, credit = profile_paths(name)
    if public.exists() or credit.exists():
        raise FileExistsError(
            "Profile already exists; choose a new name. Nothing was reset."
        )
    public.mkdir(parents=True)
    credit.mkdir(parents=True)
    pack, overlay = public / "pack", public / "overlay"
    generate(pack, farmers=32, months=12, as_of=date(2026, 10, 26))
    build_overlay(pack, overlay)
    manifest = verify_pack(pack)
    verify_overlay(pack, overlay)
    fingerprint = hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    replay_file = credit / "replay.sqlite"
    shutil.copyfile(pack / "scenario.sqlite", replay_file)
    with sqlite3.connect(replay_file) as conn:
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
    access_code = secrets.token_urlsafe(24)
    graph_password = secrets.token_urlsafe(24)
    private_key = Ed25519PrivateKey.generate()
    key_file = credit / "signing.pem"
    key_file.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    key_file.chmod(0o600)
    trust = {
        f"judge-lender-{i:03d}": {
            "enabled": True,
            "public_key": base64.b64encode(
                private_key.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw
                )
            ).decode(),
            "lender_id": f"SYN-LENDER-{i:03d}",
            "officer_ids": [f"officer-synthetic-{i:03d}"],
        }
        for i in range(4)
    }
    (public / "public-trust.json").write_text(
        json.dumps(trust, indent=2), encoding="utf-8"
    )
    inputs = {
        "DATABASE_URL": "sqlite:///" + (public / "inputs.sqlite").as_posix(),
        "SEED_DEMO_DATA": "0",
        "PAYMENT_MODE": "mock",
        "AI_MODE": "demo",
        "SMS_MODE": "demo",
        "DEMO_ACCESS_CODE": access_code,
        "CREDIT_TRUST_FILE": (public / "public-trust.json").as_posix(),
        "PAYPAL_INVOICE_PREFIX": "J" + secrets.token_hex(5).upper(),
    }
    credit_env = {
        "CREDIT_DATABASE_URL": "sqlite:///" + (credit / "workflow.sqlite").as_posix(),
        "CREDIT_DATA_DIR": credit.as_posix(),
        "REPLAY_SQLITE_FILE": replay_file.as_posix(),
        "CREDIT_SIGNING_KEY_FILE": key_file.as_posix(),
        "CREDIT_SIGNING_KEY_IDS": json.dumps(
            {f"SYN-LENDER-{i:03d}": f"judge-lender-{i:03d}" for i in range(4)}
        ),
        "CREDIT_DELIVERY_WORKER": "1",
        "INPUT_FINANCE_URL": "http://127.0.0.1:28000",
        "INPUT_FINANCE_BROWSER_URL": "http://127.0.0.1:25173/",
        "CREDIT_CORS_ORIGINS": "http://127.0.0.1:25174",
        "WORKFLOW_NEO4J_URI": "bolt://127.0.0.1:27687",
        "WORKFLOW_NEO4J_USER": "neo4j",
        "WORKFLOW_NEO4J_PASSWORD": graph_password,
        "WORKFLOW_NEO4J_DATABASE": "neo4j",
    }
    write_env(public / "inputs.env", inputs)
    write_env(credit / "credit.env", credit_env)
    # Module imports happen only after selecting isolated stores. Existing .env
    # files are never read, changed or copied by this preparation command.
    os.environ.update(inputs)
    os.environ.update(credit_env)
    os.environ.update(
        PYTHON_DOTENV_DISABLED="1",
        CREDIT_ENV_FILE=os.devnull,
        INPUT_ENV_FILE=os.devnull,
    )
    from scripts.load_workflow_cases import load

    from scripts.connected.load_execution import load_execution

    execution = load_execution(pack, overlay)
    workflow = load(overlay)
    private_text(
        public / "input-access.json", json.dumps({"access_code": access_code}, indent=2)
    )
    report = {
        "source_kind": "synthetic_replay",
        "profile": name,
        "farmers": manifest["farmers"],
        "manifest_sha256": fingerprint,
        "execution": execution,
        "workflow": workflow,
        "provider_calls": 0,
        "active_credit": 0,
        "payment_mode": "mock",
        "ai_mode": "demo",
        "boundary": "Authored histories; explicit new lender approval required. No GDS, AI or provider success is inferred.",
    }
    (public / "profile.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "profile": name,
                "farmers": manifest["farmers"],
                "active_credit": 0,
                "input_access_file": str(public / "input-access.json"),
                "officer_access_file": str(credit / "local-officer-accounts.json"),
                "provider_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="compact")
    args = parser.parse_args()
    prepare(args.name)

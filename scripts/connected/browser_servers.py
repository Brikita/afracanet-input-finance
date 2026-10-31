"""Isolated accounts, signing keys, and workflow stores for two-module browser QA."""

import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dotenv import dotenv_values
from sqlalchemy import insert

ROOT = Path(__file__).resolve().parents[2]
CREDIT = Path(os.getenv("CREDIT_REPO", ROOT.parent / "afracanet-green-path")).resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CREDIT))


def run():
    baseline = dict(os.environ)
    with tempfile.TemporaryDirectory(
        prefix="afracanet-connected-browser-"
    ) as directory:
        temp = Path(directory)
        os.environ["DATABASE_URL"] = "sqlite:///" + str(temp / "inputs.db")
        os.environ["CREDIT_DATABASE_URL"] = "sqlite:///" + str(temp / "credit.db")
        from Backend import identity, store
        from backend import db

        db.metadata.create_all(db.engine)
        store.initialize()
        farmer = "farmer-synth-000001"
        lender = "SYN-LENDER-000"
        supplier = "SYN-DEALER-000"
        with db.engine.begin() as conn:
            conn.execute(
                insert(db.farmers).values(
                    id=farmer,
                    name="Synthetic Farmer 000001",
                    location="Meru · fictional reference region",
                    lender_id=lender,
                    limit_cents=0,
                    reserved_cents=0,
                    spent_cents=0,
                    expires_at="2026-01-01T00:00:00+00:00",
                    approval_reference="UNAPPROVED-SYNTHETIC-PROFILE",
                )
            )
            conn.execute(
                insert(db.products).values(
                    id="SYN-PRODUCT-000-dap",
                    name="DAP fertilizer",
                    supplier_id=supplier,
                    category="Fertilizer",
                    unit="50 kg bag",
                    price_cents=4500,
                    stock=200,
                    reserved=0,
                )
            )
            conn.execute(
                insert(db.workspace_participants),
                [
                    {
                        "id": lender,
                        "role": "lender",
                        "name": "Synthetic Lender 1",
                        "source_kind": "synthetic_replay",
                    },
                    {
                        "id": supplier,
                        "role": "supplier",
                        "name": "Synthetic Dealer 1",
                        "source_kind": "synthetic_replay",
                    },
                ],
            )
            conn.execute(
                insert(db.approval_mappings).values(
                    id="browser-synthetic-mapping",
                    lender_id=lender,
                    source_system="afracanet-credit",
                    source_farmer_id=farmer,
                    farmer_id=farmer,
                    recorded_by="isolated_browser_fixture",
                    created_at=db.now(),
                )
            )
        identity.provision("browser-officer", lender, "isolated-browser-password")
        with store.engine.begin() as conn:
            conn.execute(
                insert(store.applications).values(
                    id="browser-application-001",
                    farmer_id=farmer,
                    input_farmer_id=farmer,
                    lender_id=lender,
                    status="PENDING",
                    provenance="synthetic",
                    created_at=store.now(),
                    request_id="browser-request-001",
                )
            )
        key = Ed25519PrivateKey.generate()
        private = temp / "private.pem"
        private.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        trust = temp / "public.json"
        trust.write_text(
            json.dumps(
                {
                    "browser-key": {
                        "enabled": True,
                        "public_key": base64.b64encode(
                            key.public_key().public_bytes(
                                serialization.Encoding.Raw,
                                serialization.PublicFormat.Raw,
                            )
                        ).decode(),
                        "lender_id": lender,
                        "officer_ids": ["browser-officer"],
                    }
                }
            )
        )
        # Build each child's environment from the original process environment,
        # before either module loaded .env. Provider credentials never cross repos.
        safe = {
            k: v
            for k, v in baseline.items()
            if not k.startswith(
                (
                    "PAYPAL_",
                    "GEMINI_",
                    "AFRICASTALKING_",
                    "FEATHERLESS_",
                    "CREDIT_",
                    "REPLAY_",
                    "WORKFLOW_NEO4J_",
                )
            )
            and k != "DATABASE_URL"
        }
        input_env = {
            **safe,
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "PAYMENT_MODE": "mock",
            "AI_MODE": "demo",
            "SMS_MODE": "demo",
            "DEMO_ACCESS_CODE": "afracanet-demo",
            "CREDIT_TRUST_FILE": str(trust),
        }
        local = dotenv_values(CREDIT / ".env")
        evidence = {
            k: v
            for k, v in local.items()
            if k.startswith("WORKFLOW_NEO4J_") or k == "REPLAY_DATABASE_URL"
        }
        credit_env = {
            **safe,
            **evidence,
            "CREDIT_DATABASE_URL": os.environ["CREDIT_DATABASE_URL"],
            "CREDIT_SIGNING_KEY_FILE": str(private),
            "CREDIT_SIGNING_KEY_ID": "browser-key",
            "CREDIT_SIGNING_KEY_IDS": "{}",
            "CREDIT_DELIVERY_WORKER": "1",
            "INPUT_FINANCE_URL": "http://127.0.0.1:18000",
            "INPUT_FINANCE_BROWSER_URL": "http://127.0.0.1:15173/",
            "CREDIT_CORS_ORIGINS": "http://127.0.0.1:15174",
            "FEATHERLESS_API_KEY": "",
            "GEMINI_API_KEY": "",
            "CREDIT_AI_API_KEY": "",
        }
        children = []
        try:
            for module, cwd, port, env in [
                ("backend.main:app", ROOT, "18000", input_env),
                ("Backend.main:app", CREDIT, "18001", credit_env),
            ]:
                children.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "uvicorn",
                            module,
                            "--host",
                            "127.0.0.1",
                            "--port",
                            port,
                        ],
                        cwd=cwd,
                        env=env,
                    )
                )
            children[0].wait()
        finally:
            for child in children:
                child.terminate()
            for child in children:
                child.wait(timeout=20)
            db.engine.dispose()
            store.engine.dispose()


if __name__ == "__main__":
    run()

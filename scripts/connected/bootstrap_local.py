"""Loopback-only development services. Generates distinct local credentials.

Never reads or copies provider credentials. Private signing material stays in
the credit repo; only the public verification key crosses the module boundary.
Existing databases and dataset files are not overwritten.
"""

import argparse
import base64
import json
import os
import secrets
import subprocess
from pathlib import Path

import psycopg
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]


def configure(path, fields):
    lines = path.read_text().splitlines() if path.exists() else []
    for key, value in fields.items():
        lines = [line for line in lines if not line.startswith(key + "=")]
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n")


def setup(credit_repo):
    runtime = ROOT / "data/runtimes/postgres/pgsql/bin"
    operator = (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AFRACANet-local"
    )
    operator.mkdir(exist_ok=True)
    config = operator / "services.json"
    if config.exists():
        info = json.loads(config.read_text())
    else:
        info = {"admin_password": secrets.token_hex(24), "port": 15432, "databases": {}}
        for name in ("input", "credit", "replay"):
            info["databases"][name] = {
                "name": "afracanet_" + name + "_dev_v1",
                "role": "afracanet_" + name,
                "password": secrets.token_hex(24),
            }
        config.write_text(json.dumps(info))
    cluster = operator / "postgres"
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    if not (cluster / "PG_VERSION").exists():
        password_file = operator / "bootstrap-password.txt"
        password_file.write_text(info["admin_password"])
        try:
            subprocess.run(
                [
                    str(runtime / "initdb.exe"),
                    "-D",
                    str(cluster),
                    "-U",
                    "postgres",
                    "-A",
                    "scram-sha-256",
                    "--pwfile",
                    str(password_file),
                    "--encoding=UTF8",
                    "--locale=C",
                ],
                check=True,
                capture_output=True,
                **hidden,
            )
        finally:
            password_file.unlink(missing_ok=True)
        with (cluster / "postgresql.conf").open("a") as stream:
            stream.write(
                "\nlisten_addresses='127.0.0.1'\nport=15432\nshared_buffers='64MB'\nwork_mem='4MB'\nmax_connections=30\n"
            )
    running = subprocess.run(
        [str(runtime / "pg_ctl.exe"), "status", "-D", str(cluster)],
        capture_output=True,
        **hidden,
    )
    if running.returncode != 0:
        subprocess.run(
            [
                str(runtime / "pg_ctl.exe"),
                "start",
                "-D",
                str(cluster),
                "-l",
                str(operator / "postgres.log"),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **hidden,
        )
    with psycopg.connect(
        host="127.0.0.1",
        port=info["port"],
        user="postgres",
        password=info["admin_password"],
        autocommit=True,
    ) as conn:
        for item in info["databases"].values():
            if not conn.execute(
                "SELECT 1 FROM pg_roles WHERE rolname=%s", (item["role"],)
            ).fetchone():
                conn.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(item["role"]), sql.Literal(item["password"])
                    )
                )
            if not conn.execute(
                "SELECT 1 FROM pg_database WHERE datname=%s", (item["name"],)
            ).fetchone():
                conn.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(item["name"]), sql.Identifier(item["role"])
                    )
                )

    def url(name, sqlalchemy=False):
        item = info["databases"][name]
        return f"postgresql{'\u002bpsycopg' if sqlalchemy else ''}://{item['role']}:{item['password']}@127.0.0.1:{info['port']}/{item['name']}"

    reader = "afracanet_context_reader"
    if "context_reader_password" not in info:
        info["context_reader_password"] = secrets.token_hex(24)
    with psycopg.connect(
        host="127.0.0.1",
        port=info["port"],
        user="postgres",
        password=info["admin_password"],
        dbname=info["databases"]["replay"]["name"],
        autocommit=True,
    ) as conn:
        if not conn.execute(
            "SELECT 1 FROM pg_roles WHERE rolname=%s", (reader,)
        ).fetchone():
            conn.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(reader), sql.Literal(info["context_reader_password"])
                )
            )
        conn.execute(
            sql.SQL("ALTER ROLE {} SET default_transaction_read_only=on").format(
                sql.Identifier(reader)
            )
        )
        if conn.execute("SELECT to_regclass('replay.entities')").fetchone()[0]:
            conn.execute(
                sql.SQL("GRANT USAGE ON SCHEMA replay TO {}").format(
                    sql.Identifier(reader)
                )
            )
            conn.execute(
                sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA replay TO {}").format(
                    sql.Identifier(reader)
                )
            )
    reader_url = f"postgresql://{reader}:{info['context_reader_password']}@127.0.0.1:{info['port']}/{info['databases']['replay']['name']}"
    key_path = credit_repo / "data/keys/local-credit.pem"
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if not key_path.exists():
        key = Ed25519PrivateKey.generate()
        key_path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
    key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    public = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    officers = [f"officer-synthetic-{index:03d}" for index in range(4)]
    trust = {
        f"local-lender-{index:03d}": {
            "enabled": True,
            "public_key": base64.b64encode(public).decode(),
            "lender_id": f"SYN-LENDER-{index:03d}",
            "officer_ids": [officer],
        }
        for index, officer in enumerate(officers)
    }
    # Each lender can later rotate to its own signing key; initial local service uses
    # one key with an explicit lender/officer binding for each key identifier.
    trust_file = ROOT / "data/keys/credit-public-trust.json"
    trust_file.parent.mkdir(exist_ok=True)
    trust_file.write_text(json.dumps(trust, indent=2))
    configure(
        ROOT / ".env",
        {
            "DATABASE_URL": url("input", True),
            "CREDIT_TRUST_FILE": trust_file.as_posix(),
        },
    )
    configure(
        credit_repo / ".env",
        {
            "CREDIT_DATABASE_URL": url("credit", True),
            "CREDIT_SIGNING_KEY_FILE": key_path.as_posix(),
            "CREDIT_SIGNING_KEY_IDS": json.dumps(
                {f"SYN-LENDER-{i:03d}": f"local-lender-{i:03d}" for i in range(4)}
            ),
            "INPUT_FINANCE_URL": "http://127.0.0.1:8000",
            "INPUT_FINANCE_BROWSER_URL": "http://127.0.0.1:5173/",
            "CREDIT_DELIVERY_WORKER": "1",
            "REPLAY_DATABASE_URL": reader_url,
        },
    )
    # Connection helper is operator-local, outside both repositories.
    info["credit_repo"] = str(credit_repo)
    config.write_text(json.dumps(info))
    return info


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--credit-repo", type=Path, required=True)
    args = parser.parse_args()
    setup(args.credit_repo.resolve())
    print(
        "Loopback PostgreSQL and distinct module accounts configured. Signing key retained only in credit module."
    )

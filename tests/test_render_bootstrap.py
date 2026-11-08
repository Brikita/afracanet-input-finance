"""Hosted initialization must preserve money state and isolate private material."""

import json
import sqlite3
import subprocess
import sys

import pytest

from scripts.workspace_config import ROOT, service_environment


def run_script(name, *arguments):
    return subprocess.run(
        [sys.executable, str(ROOT / "deploy/render" / name), *map(str, arguments)],
        cwd=ROOT,
        env={**service_environment(), "PYTHON_DOTENV_DISABLED": "1"},
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="module")
def fixture_pack(tmp_path_factory):
    path = tmp_path_factory.mktemp("render-fixture") / "fixture"
    result = run_script("compact_fixture.py", path)
    assert result.returncode == 0, result.stderr
    return path


def test_inputs_restart_preserves_existing_balances_and_has_no_signing_key(
    fixture_pack, tmp_path
):
    data = tmp_path / "inputs"
    arguments = ("inputs", "--fixture", fixture_pack, "--data", data)
    first = run_script("bootstrap.py", *arguments)
    assert first.returncode == 0, first.stderr
    database = data / "inputs.sqlite"
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT count(*) FROM farmers").fetchone()[0] == 32
        assert conn.execute("SELECT sum(limit_cents) FROM farmers").fetchone()[0] == 0
        conn.execute(
            "UPDATE farmers SET limit_cents=9876 WHERE id='farmer-synth-000001'"
        )
    second = run_script("bootstrap.py", *arguments)
    assert second.returncode == 0, second.stderr
    with sqlite3.connect(database) as conn:
        assert (
            conn.execute(
                "SELECT limit_cents FROM farmers WHERE id='farmer-synth-000001'"
            ).fetchone()[0]
            == 9876
        )
    assert not (data / "signing.pem").exists()
    assert not (data / "local-officer-accounts.json").exists()


def test_credit_restart_keeps_key_and_officer_accounts(fixture_pack, tmp_path):
    data = tmp_path / "credit"
    arguments = ("credit", "--fixture", fixture_pack, "--data", data)
    first = run_script("bootstrap.py", *arguments)
    assert first.returncode == 0, first.stderr
    private = (data / "signing.pem").read_bytes()
    accounts = (data / "local-officer-accounts.json").read_bytes()
    trust = json.loads((data / "public-trust.json").read_text())
    assert (
        len(trust) == 4 and b"PRIVATE" not in (data / "public-trust.json").read_bytes()
    )
    with sqlite3.connect(data / "workflow.sqlite") as conn:
        assert conn.execute("SELECT count(*) FROM officer_sessions").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM officers").fetchone()[0] == 4
    second = run_script("bootstrap.py", *arguments)
    assert second.returncode == 0, second.stderr
    assert (data / "signing.pem").read_bytes() == private
    assert (data / "local-officer-accounts.json").read_bytes() == accounts
    with sqlite3.connect(data / "replay.sqlite") as conn:
        assert conn.execute("SELECT count(*) FROM dataset_manifest").fetchone()[0] == 1


def test_incomplete_bootstrap_does_not_reset_a_store(fixture_pack, tmp_path):
    data = tmp_path / "partial"
    data.mkdir()
    database = data / "inputs.sqlite"
    database.write_bytes(b"preserve this operator state")
    result = run_script(
        "bootstrap.py", "inputs", "--fixture", fixture_pack, "--data", data
    )
    assert result.returncode != 0
    assert database.read_bytes() == b"preserve this operator state"


def test_render_hostname_is_allowed_without_allowing_other_hosts(tmp_path):
    program = """
from deploy.render.bootstrap import configure_input_host
configure_input_host()
from backend.main import app
from fastapi.testclient import TestClient
with TestClient(app) as client:
    assert client.get('/api/health', headers={'host':'inputs.example.invalid'}).status_code == 200
    assert client.get('/api/health', headers={'host':'untrusted.example.invalid'}).status_code == 400
"""
    result = subprocess.run(
        [sys.executable, "-c", program],
        cwd=ROOT,
        env={
            **service_environment(),
            "PYTHON_DOTENV_DISABLED": "1",
            "RENDER_EXTERNAL_HOSTNAME": "inputs.example.invalid",
            "DATABASE_URL": "sqlite:///" + (tmp_path / "health.sqlite").as_posix(),
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

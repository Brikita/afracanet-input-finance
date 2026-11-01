"""The consolidated checkout must not mix provider credentials between services."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import workspace_config as workspace


def test_nested_credit_loads_its_own_data_without_reading_payment_env(tmp_path):
    env = {
        **workspace.service_environment(),
        "CREDIT_ENV_FILE": os.devnull,
        "CREDIT_DATA_DIR": str(tmp_path),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from Backend import config, store; import json, os; "
            "print(json.dumps({'database':store.engine.url.database, "
            "'payment_key_loaded':bool(os.getenv('PAYPAL_CLIENT_SECRET')), "
            "'gemini_key_loaded':bool(os.getenv('GEMINI_API_KEY'))}))",
        ],
        cwd=workspace.CREDIT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert Path(payload["database"]) == tmp_path / "credit-workflow.db"
    assert not payload["payment_key_loaded"]
    assert not payload["gemini_key_loaded"]


def test_child_environment_does_not_inherit_other_modules_secrets(monkeypatch):
    for key in (
        "PAYPAL_CLIENT_SECRET",
        "GEMINI_API_KEY",
        "AFRICASTALKING_API_KEY",
        "FEATHERLESS_API_KEY",
        "CREDIT_SIGNING_KEY_FILE",
        "REPLAY_DATABASE_URL",
        "WORKFLOW_NEO4J_PASSWORD",
        "DATABASE_URL",
        "VITE_CREDIT_API_URL",
    ):
        monkeypatch.setenv(key, "isolated-test-sentinel")
    monkeypatch.setenv("PATH", "retained-runtime-path")
    environment = workspace.service_environment()
    assert "isolated-test-sentinel" not in environment.values()
    assert environment["PATH"] == "retained-runtime-path"


def test_fresh_checkout_uses_its_own_credit_environment(tmp_path, monkeypatch):
    module = tmp_path / "modules/credit-intelligence"
    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    monkeypatch.setattr(workspace, "CREDIT", module)
    monkeypatch.delenv("CREDIT_ENV_FILE", raising=False)
    assert workspace.credit_env_file(module) == module / ".env"
    assert workspace.credit_data_dir() == module / "data"


def test_operator_can_reference_existing_files_without_copying_secrets(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    monkeypatch.delenv("CREDIT_ENV_FILE", raising=False)
    private = tmp_path / "operator" / ".env"
    private.parent.mkdir()
    private.write_text("GEMINI_API_KEY=isolated-test-sentinel\n", encoding="utf-8")
    config = tmp_path / "data/workspace.local.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"credit_env_file": str(private)}), encoding="utf-8")
    assert workspace.credit_env_file() == private
    assert workspace.local_paths() == {"credit_env_file": private}
    assert not (tmp_path / "modules/credit-intelligence/.env").exists()


def test_local_path_configuration_cannot_become_a_shared_secret_store(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    config = tmp_path / "data/workspace.local.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"GEMINI_API_KEY": "not-a-path"}), encoding="utf-8")
    with pytest.raises(ValueError, match="paths only"):
        workspace.local_paths()

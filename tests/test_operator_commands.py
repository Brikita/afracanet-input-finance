"""Documented operator commands must start without sending or initializing data."""

import subprocess
import sys

from scripts.workspace_config import ROOT, service_environment


def test_sms_help_and_invalid_limit_do_not_create_a_database(tmp_path):
    database = tmp_path / "must-not-be-created.sqlite"
    env = {
        **service_environment(),
        "DATABASE_URL": "sqlite:///" + str(database),
        "PAYMENT_MODE": "mock",
        "AI_MODE": "demo",
        "SMS_MODE": "demo",
        "PYTHON_DOTENV_DISABLED": "1",
    }
    for arguments, expected in [(["--help"], 0), (["--limit", "0"], 2)]:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/dispatch_sms.py"), *arguments],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == expected, result.stderr
        assert not database.exists()
        if not expected:
            assert "--limit" in result.stdout

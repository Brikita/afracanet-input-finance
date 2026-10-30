"""An isolated local backend for browser checks. Never resets the user's database."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="afracanet-ui-") as directory:
    environment = {
        **os.environ,
        "DATABASE_URL": "sqlite:///" + str(Path(directory) / "browser.db"),
        "PAYMENT_MODE": "mock",
        "AI_MODE": "demo",
        "DEMO_ACCESS_CODE": "afracanet-demo",
    }
    result = subprocess.run([
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1", "--port", os.getenv("UI_TEST_API_PORT", "8001"),
    ], env=environment)
    sys.exit(result.returncode)

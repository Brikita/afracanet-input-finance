"""Repository paths and optional operator-local configuration references.

The optional JSON contains file paths, never copied credentials. A fresh checkout
uses each module's own .env and data directory.
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDIT = ROOT / "modules" / "credit-intelligence"


def local_paths():
    path = ROOT / "data" / "workspace.local.json"
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) - {
        "credit_env_file",
        "credit_data_dir",
    }:
        raise ValueError(
            "workspace.local.json accepts credit environment/data paths only"
        )
    return {key: Path(item).expanduser().resolve() for key, item in value.items()}


def credit_env_file(module=CREDIT):
    explicit = os.getenv("CREDIT_ENV_FILE")
    if explicit:
        return Path(explicit).expanduser().resolve()
    if Path(module).resolve() == CREDIT.resolve():
        return local_paths().get("credit_env_file", CREDIT / ".env")
    return Path(module) / ".env"


def credit_data_dir():
    return local_paths().get("credit_data_dir", CREDIT / "data")


def service_environment():
    """Start a child without a different service's inherited provider settings."""
    prefixes = (
        "PAYPAL_",
        "GEMINI_",
        "AFRICASTALKING_",
        "FEATHERLESS_",
        "CREDIT_",
        "REPLAY_",
        "WORKFLOW_NEO4J_",
        "NEO4J_",
        "INPUT_FINANCE_",
        "VITE_",
    )
    fields = {"DATABASE_URL", "PAYMENT_MODE", "AI_MODE", "SMS_MODE", "DEMO_ACCESS_CODE"}
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(prefixes) and key not in fields
    }

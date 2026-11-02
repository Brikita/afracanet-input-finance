"""A fresh compact profile must need no historical checkout or provider secrets."""

import json
import subprocess
import sys

from scripts.workspace_config import CREDIT, ROOT, service_environment


def test_empty_store_does_not_invent_people_or_credit(tmp_path, monkeypatch):
    from sqlalchemy import func, select

    from backend import db
    from backend.config import settings

    engine = db.build_engine("sqlite:///" + str(tmp_path / "blank.sqlite"))
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(settings, "seed_demo_data", False)
    try:
        db.initialize()
        with engine.connect() as conn:
            assert (
                conn.execute(select(func.count()).select_from(db.farmers)).scalar() == 0
            )
            assert (
                conn.execute(select(func.count()).select_from(db.products)).scalar()
                == 0
            )
    finally:
        engine.dispose()


def test_compact_profile_has_no_credit_authority_and_readonly_scoped_history(tmp_path):
    script = """
import json,os,sys,sqlite3
from pathlib import Path
from scripts import prepare_judge
prepare_judge.ROOT=Path(sys.argv[1])
prepare_judge.CREDIT=prepare_judge.ROOT/'modules/credit-intelligence'
prepare_judge.prepare('test')
from Backend import replay,store
from backend import db
from sqlalchemy import select,func
a=replay.farmer_history('farmer-synth-000001','SYN-LENDER-000')
b=replay.farmer_history('farmer-synth-000001','SYN-LENDER-001')
assert a['available'] and a['loan_count']>0
assert b['loan_count']==0 and b['principal_minor']==0
assert replay.summary('SYN-LENDER-000')['provider_payment_evidence'] is False
with replay.connection() as conn:
    try: conn.execute('DELETE FROM loans')
    except sqlite3.OperationalError: pass
    else: raise AssertionError('Replay was writable')
with db.engine.connect() as conn:
    assert conn.execute(select(func.sum(db.farmers.c.limit_cents))).scalar()==0
    assert conn.execute(select(func.count()).select_from(db.orders)).scalar()==0
with store.engine.connect() as conn:
    assert conn.execute(select(func.count()).select_from(store.outbox)).scalar()==0
try: prepare_judge.prepare('test')
except FileExistsError: pass
else: raise AssertionError('Existing profile overwritten')
assert not (prepare_judge.ROOT/'.env').exists()
assert not (prepare_judge.CREDIT/'.env').exists()
print(json.dumps({'read_only':True,'tenant_isolation':True,'no_active_credit':True}))
"""
    env = {
        **service_environment(),
        "PYTHONPATH": str(ROOT)
        + (";" if sys.platform == "win32" else ":")
        + str(CREDIT),
        "PYTHON_DOTENV_DISABLED": "1",
    }
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.splitlines()[-1])["read_only"]

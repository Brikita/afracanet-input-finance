"""Restart a previously imported loopback development graph without reimporting."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from neo4j import GraphDatabase

parser = argparse.ArgumentParser()
parser.add_argument("--instance", default="graph-runtime-v1")
args = parser.parse_args()
if not re.fullmatch(r"[a-z][a-z0-9-]{2,80}", args.instance):
    raise SystemExit("Use an instance directory name, not a path.")
folder = Path(__file__).resolve().parents[1] / "data" / args.instance
runtime = json.loads((folder / "local-runtime.json").read_text())
try:
    with GraphDatabase.driver(
        "bolt://127.0.0.1:17687",
        auth=("neo4j", runtime["password"]),
        connection_timeout=3,
    ) as driver:
        driver.verify_connectivity()
    print("The imported loopback graph is already running.")
except Exception:
    env = {
        **os.environ,
        "JAVA_HOME": runtime["java_home"],
        "NEO4J_HOME": runtime["neo4j_home"],
        "NEO4J_CONF": runtime["conf"],
    }
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    with (folder / "console.log").open("a") as log:
        process = subprocess.Popen(
            [str(Path(runtime["neo4j_home"]) / "bin/neo4j.bat"), "console"],
            env=env,
            stdout=log,
            stderr=log,
            **hidden,
        )
    runtime["pid"] = process.pid
    (folder / "local-runtime.json").write_text(json.dumps(runtime))
    print("Graph startup requested. Inspect the local console log for readiness.")

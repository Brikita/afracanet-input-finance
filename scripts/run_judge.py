"""Run a compact isolated judge graph and all four app services on separate ports."""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from zipfile import is_zipfile

from dotenv import dotenv_values
from neo4j import GraphDatabase
from prepare_judge import CREDIT, ROOT, profile_paths
from workspace_config import service_environment


def graph_process(public, credit, neo4j_home, java_home, gds_jar):
    from run_platform import stop_children

    config = dotenv_values(credit / "credit.env")
    folder = credit / "graph"
    conf = folder / "conf"
    first = not conf.exists()
    for name in ("conf", "store", "logs", "run", "transactions", "plugins"):
        (folder / name).mkdir(parents=True, exist_ok=True)
    if gds_jar:
        if not gds_jar.is_file() or gds_jar.suffix != ".jar" or not is_zipfile(gds_jar):
            raise ValueError("Supply the official compatible GDS 2.13 jar.")
        shutil.copyfile(gds_jar, folder / "plugins" / "gds.jar")
    lines = [
        f"server.directories.{key}={(folder / value).as_posix()}"
        for key, value in {
            "data": "store",
            "logs": "logs",
            "run": "run",
            "transaction.logs.root": "transactions",
            "plugins": "plugins",
        }.items()
    ] + [
        "server.memory.heap.initial_size=256m",
        "server.memory.heap.max_size=512m",
        "server.memory.pagecache.size=64m",
        "server.default_listen_address=127.0.0.1",
        "server.bolt.listen_address=:27687",
        "server.http.listen_address=:27474",
        "server.bolt.advertised_address=127.0.0.1:27687",
        "server.http.advertised_address=127.0.0.1:27474",
        "server.https.enabled=false",
        "dbms.security.auth_enabled=true",
        "dbms.usage_report.enabled=false",
        "dbms.security.procedures.unrestricted=gds.*",
        "dbms.security.procedures.allowlist=gds.*",
    ]
    (conf / "neo4j.conf").write_text("\n".join(lines) + "\n", encoding="utf-8")
    env = {
        **service_environment(),
        "JAVA_HOME": str(java_home),
        "NEO4J_HOME": str(neo4j_home),
        "NEO4J_CONF": str(conf),
    }
    extension = ".bat" if os.name == "nt" else ""
    hidden = (
        {"creationflags": subprocess.CREATE_NO_WINDOW}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    log = (folder / "console.log").open("a", encoding="utf-8")
    if first:
        subprocess.run(
            [
                str(neo4j_home / ("bin/neo4j-admin" + extension)),
                "dbms",
                "set-initial-password",
                config["WORKFLOW_NEO4J_PASSWORD"],
            ],
            env=env,
            stdout=log,
            stderr=log,
            check=True,
            **hidden,
        )
    child = subprocess.Popen(
        [str(neo4j_home / ("bin/neo4j" + extension)), "console"],
        env=env,
        stdout=log,
        stderr=log,
        **hidden,
    )
    try:
        driver = GraphDatabase.driver(
            config["WORKFLOW_NEO4J_URI"],
            auth=(config["WORKFLOW_NEO4J_USER"], config["WORKFLOW_NEO4J_PASSWORD"]),
            connection_timeout=2,
        )
        deadline = time.monotonic() + 100
        while True:
            try:
                driver.verify_connectivity()
                break
            except Exception:
                if child.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(
                        "Judge graph did not start; inspect its private console.log."
                    ) from None
                time.sleep(1)
        sys.path.insert(0, str(CREDIT))
        from scripts.load_judge_graph import load

        from scripts.connected.load_relational import verify_overlay, verify_pack

        verify_pack(public / "pack")
        verify_overlay(public / "pack", public / "overlay")
        with driver, driver.session() as session:
            print(
                json.dumps(load(session, public / "pack", public / "overlay")),
                flush=True,
            )
        return child
    except BaseException:
        stop_children([child])
        raise
    finally:
        log.close()


def main():
    from run_platform import dev, stop_children

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="compact")
    parser.add_argument("--neo4j-home", type=Path)
    parser.add_argument("--java-home", type=Path)
    parser.add_argument("--gds-jar", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Compute bounded GDS for the first synthetic lender before starting apps.",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Request orderly shutdown of this running judge profile.",
    )
    parser.add_argument(
        "--providers",
        action="store_true",
        help="Use each service's existing private provider env file without copying credentials; manual sandbox buyer payment required.",
    )
    args = parser.parse_args()
    public, credit = profile_paths(args.name)
    if not (public / "profile.json").exists():
        parser.error("Prepare this judge profile first.")
    if args.stop:
        (public / ".stop-requested").touch()
        return
    if not args.neo4j_home or not args.java_home:
        parser.error("Supply --neo4j-home and --java-home for startup.")
    (public / ".stop-requested").unlink(missing_ok=True)
    for port in (27687, 27474, 28000, 28001, 25173, 25174):
        with socket.socket() as probe:
            probe.settimeout(0.25)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                parser.error(
                    f"Judge port {port} is occupied; no services were started."
                )
    child = graph_process(
        public,
        credit,
        args.neo4j_home.resolve(),
        args.java_home.resolve(),
        args.gds_jar.resolve() if args.gds_jar else None,
    )
    try:
        if args.analytics:
            subprocess.run(
                [
                    sys.executable,
                    str(CREDIT / "scripts/run_graph_analytics.py"),
                    "--env-file",
                    str(credit / "credit.env"),
                    "--lender",
                    "SYN-LENDER-000",
                ],
                cwd=ROOT,
                env=service_environment(),
                check=True,
            )
        dev(
            check=args.check,
            profile=args.name,
            providers=args.providers,
            inspect_profile=args.analytics,
        )
    finally:
        stop_children([child])


if __name__ == "__main__":
    main()

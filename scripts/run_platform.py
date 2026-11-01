"""One checkout, isolated services. Run `python scripts/run_platform.py --help`."""

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from workspace_config import (
    CREDIT,
    ROOT,
    credit_data_dir,
    credit_env_file,
    service_environment,
)

PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
NPM = shutil.which("npm.cmd" if os.name == "nt" else "npm")
NODE = shutil.which("node")


def run(command, cwd=ROOT, env=None):
    if os.name == "nt" and command[0] == NPM:
        command = [
            NODE,
            Path(NPM).parent / "node_modules/npm/bin/npm-cli.js",
            *command[1:],
        ]
    subprocess.run([str(part) for part in command], cwd=cwd, env=env, check=True)


def setup():
    if not NPM:
        raise SystemExit("Install Node.js 22.16+ with npm first.")
    for folder in (ROOT, CREDIT):
        run([NPM, "ci"], folder)
    if not PYTHON.exists():
        run([sys.executable, "-m", "venv", ROOT / ".venv"])
    run([PYTHON, "-m", "pip", "install", "-r", "requirements-dev.txt"])
    print(
        "Setup complete. Configure each module's .env separately; no credentials were copied."
    )


def check_backend():
    with tempfile.TemporaryDirectory(prefix="afracanet-tests-") as folder:
        env = {
            **service_environment(),
            "PYTHONPATH": os.pathsep.join([str(ROOT), str(CREDIT)]),
            "DATABASE_URL": "sqlite:///" + str(Path(folder) / "inputs.db"),
            "CREDIT_DATABASE_URL": "sqlite:///" + str(Path(folder) / "credit.db"),
            "CREDIT_ENV_FILE": os.devnull,
            "CREDIT_DELIVERY_WORKER": "0",
            "PAYMENT_MODE": "mock",
            "AI_MODE": "demo",
            "SMS_MODE": "demo",
            "GEMINI_API_KEY": "",
            "CREDIT_AI_API_KEY": "",
            "FEATHERLESS_API_KEY": "",
            "WORKFLOW_NEO4J_URI": "",
            "REPLAY_DATABASE_URL": "",
        }
        run([PYTHON, "-m", "pytest", "-q"], env=env)
        run([PYTHON, "-m", "pytest", "-q", "Backend/tests"], CREDIT, env)
        run([PYTHON, "scripts/check_connected_workflow.py"], env=env)


def stop_children(children):
    for child in children:
        if child.poll() is not None:
            continue
        if os.name == "nt":
            # Stop only process trees created by this supervisor. Windows venv
            # redirectors and Vite spawn descendants that terminate() misses.
            subprocess.run(
                ["taskkill", "/PID", str(child.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    for child in children:
        try:
            child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                child.kill()
            else:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            child.wait()


def dev(check=False):
    ports = [8000, 8001, 5173, 5174]
    busy = []
    for port in ports:
        with socket.socket() as probe:
            probe.settimeout(0.25)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                busy.append(port)
    if busy:
        raise SystemExit(
            f"Stop the existing development services on ports {busy} before starting the platform."
        )
    if not PYTHON.exists() or not NODE:
        raise SystemExit("Run npm run setup first.")
    specs = []
    for folder, module, port, envfile in [
        (ROOT, "backend.main:app", 8000, ROOT / ".env"),
        (CREDIT, "Backend.main:app", 8001, credit_env_file()),
    ]:
        env = service_environment()
        if folder == CREDIT:
            env["CREDIT_ENV_FILE"] = str(envfile)
            env["CREDIT_DATA_DIR"] = str(credit_data_dir())
        command = [
            PYTHON,
            "-m",
            "uvicorn",
            module,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]
        if envfile.exists():
            command += ["--env-file", envfile]
        specs.append((command, folder, env))
    for folder, port in [(ROOT, 5173), (CREDIT, 5174)]:
        vite = folder / "node_modules/vite/bin/vite.js"
        if not vite.exists():
            raise SystemExit("Run npm run setup first.")
        env = service_environment()
        if folder == CREDIT:
            env.update(
                VITE_CREDIT_API_URL="http://127.0.0.1:8001",
                VITE_INPUT_FINANCE_URL="http://127.0.0.1:5173/",
            )
        else:
            env["VITE_CREDIT_WORKSPACE_URL"] = "http://127.0.0.1:5174/"
        specs.append(
            (
                [
                    NODE,
                    vite,
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--strictPort",
                ],
                folder,
                env,
            )
        )
    children = []
    try:
        for command, cwd, env in specs:
            children.append(
                subprocess.Popen(
                    [str(part) for part in command],
                    cwd=cwd,
                    env=env,
                    start_new_session=os.name != "nt",
                )
            )
        print(
            "AFRACANet: public/input finance http://127.0.0.1:5173/about | credit http://127.0.0.1:5174/",
            flush=True,
        )
        if check:
            remaining = {
                "http://127.0.0.1:8000/api/health",
                "http://127.0.0.1:8001/api/health",
                "http://127.0.0.1:5173/about",
                "http://127.0.0.1:5174/",
            }
            deadline = time.monotonic() + 150
            while remaining and time.monotonic() < deadline:
                if any(child.poll() is not None for child in children):
                    raise SystemExit("A platform service exited during startup.")
                for url in tuple(remaining):
                    try:
                        request = urllib.request.Request(
                            url, headers={"Accept": "text/html,application/json"}
                        )
                        with urllib.request.urlopen(request, timeout=35) as response:
                            if response.status == 200:
                                remaining.remove(url)
                    except (urllib.error.URLError, TimeoutError):
                        pass
                time.sleep(0.5)
            if remaining:
                raise SystemExit(
                    "Platform startup did not make all four services ready."
                )
            print(
                "All four services returned HTTP 200; stopping smoke-check children.",
                flush=True,
            )
            return
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        raise SystemExit(
            next(
                child.returncode or 1 for child in children if child.poll() is not None
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        stop_children(children)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["setup", "dev", "smoke", "build", "types", "test-backend"]
    )
    args = parser.parse_args()
    if args.command == "setup":
        setup()
    elif args.command == "dev":
        dev()
    elif args.command == "smoke":
        dev(check=True)
    elif args.command == "test-backend":
        check_backend()
    elif args.command == "build":
        run([NPM, "run", "build:inputs"])
        run([NPM, "run", "build"], CREDIT)
    elif args.command == "types":
        run([NPM, "run", "check:types"])
        run([NODE, CREDIT / "node_modules/typescript/bin/tsc", "--noEmit"], CREDIT)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None

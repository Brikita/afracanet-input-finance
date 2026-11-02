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


def dev(check=False, profile=None, providers=False, inspect_profile=False):
    ports = [28000, 28001, 25173, 25174] if profile else [8000, 8001, 5173, 5174]
    input_api, credit_api, input_ui, credit_ui = ports
    if profile:
        from prepare_judge import profile_paths

        public, credit_private = profile_paths(profile)
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
        (
            ROOT,
            "backend.main:app",
            input_api,
            public / "inputs.env" if profile else ROOT / ".env",
        ),
        (
            CREDIT,
            "Backend.main:app",
            credit_api,
            credit_private / "credit.env" if profile else credit_env_file(),
        ),
    ]:
        env = service_environment()
        if profile:
            from dotenv import dotenv_values

            env.update(
                {
                    key: value
                    for key, value in dotenv_values(envfile).items()
                    if value is not None
                }
            )
            if providers:
                envfile = ROOT / ".env" if folder == ROOT else credit_env_file()
                if folder == ROOT:
                    if not env.get("PAYPAL_INVOICE_PREFIX"):
                        import secrets

                        from dotenv import set_key

                        env["PAYPAL_INVOICE_PREFIX"] = (
                            "J" + secrets.token_hex(5).upper()
                        )
                        set_key(
                            public / "inputs.env",
                            "PAYPAL_INVOICE_PREFIX",
                            env["PAYPAL_INVOICE_PREFIX"],
                        )
                    env.update(
                        PAYMENT_MODE="sandbox", AI_MODE="gemini", SMS_MODE="demo"
                    )
        if folder == CREDIT:
            env["CREDIT_ENV_FILE"] = str(envfile)
            env["CREDIT_DATA_DIR"] = str(
                credit_private if profile else credit_data_dir()
            )
        else:
            env["INPUT_ENV_FILE"] = str(envfile)
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
    for folder, port in [(ROOT, input_ui), (CREDIT, credit_ui)]:
        vite = folder / "node_modules/vite/bin/vite.js"
        if not vite.exists():
            raise SystemExit("Run npm run setup first.")
        env = service_environment()
        if folder == CREDIT:
            env.update(
                VITE_CREDIT_API_URL=f"http://127.0.0.1:{credit_api}",
                VITE_INPUT_FINANCE_URL=f"http://127.0.0.1:{input_ui}/",
            )
        else:
            env["VITE_CREDIT_WORKSPACE_URL"] = f"http://127.0.0.1:{credit_ui}/"
            env["VITE_API_TARGET"] = f"http://127.0.0.1:{input_api}"
        if profile:
            env["VITE_CACHE_DIR"] = str(
                (credit_private if folder == CREDIT else public) / "vite-cache"
            )
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
            f"AFRACANet: public/input finance http://127.0.0.1:{input_ui}/about | credit http://127.0.0.1:{credit_ui}/",
            flush=True,
        )
        if check:
            remaining = {
                f"http://127.0.0.1:{input_api}/api/health",
                f"http://127.0.0.1:{credit_api}/api/health",
                f"http://127.0.0.1:{input_ui}/about",
                f"http://127.0.0.1:{credit_ui}/",
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
            if profile and inspect_profile:
                run(
                    [
                        PYTHON,
                        ROOT / "scripts/rehearse_judge.py",
                        "inspect",
                        "--name",
                        profile,
                    ],
                    env=service_environment(),
                )
            print(
                "All four services returned HTTP 200; stopping smoke-check children.",
                flush=True,
            )
            return
        while all(child.poll() is None for child in children):
            if profile and (public / ".stop-requested").exists():
                (public / ".stop-requested").unlink()
                return
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
        "command",
        choices=[
            "setup",
            "dev",
            "smoke",
            "build",
            "types",
            "test-backend",
            "provision",
        ],
    )
    parser.add_argument("identifiers", nargs="*")
    args = parser.parse_args()
    if args.command != "provision" and args.identifiers:
        parser.error("Extra arguments are only accepted by provision.")
    if args.command == "provision":
        if len(args.identifiers) != 2:
            parser.error(
                "provision requires OFFICER_ID LENDER_ID; password is requested privately."
            )
        env = service_environment()
        env["CREDIT_ENV_FILE"] = str(credit_env_file())
        env["CREDIT_DATA_DIR"] = str(credit_data_dir())
        run(
            [PYTHON, CREDIT / "scripts/provision_officer.py", *args.identifiers],
            CREDIT,
            env,
        )
    elif args.command == "setup":
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

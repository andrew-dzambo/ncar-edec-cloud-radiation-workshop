#!/usr/bin/env python3
"""Use an instructor-prepared RRTMGP runtime without participant installation.

This module uses only the standard library until runtime/data checks are set up.
Participant writes are confined to their checkout and their own Jupyter kernel
registration; no packages, data, or kernel files are written to the shared tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

CONFIG_NAME = ".workshop-runtime.json"
PYTHON_LINK = ".workshop-python"
KERNEL_NAME = "rrtmgp-workshop"
KERNEL_DISPLAY = "Python (RRTMGP Workshop)"
THREAD_ENV = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
              "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
              "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
              "JUPYTER_PREFER_ENV_PATH": "0", "PYTHONPATH": ""}
# Hashes from the immutable rrtmgp-data v1.9 archive.
COEFFICIENT_SHA256 = {
    "rrtmgp-gas-lw-g256.nc": "4048360199d1917ed8f2ccaae2ec097d0f990da3bbad9830337b739b4fa01be7",
    "rrtmgp-gas-sw-g224.nc": "584f1dd41ea9fc07d4ee3754eb1dafbd46ad3161cd6fd20fa06b6922b6f0702e",
    "rrtmgp-clouds-lw-bnd.nc": "09d6704c5b863b4c3ceb417d20bb3076ec492e6bf2dfbcc9f3c5996a3706f0b0",
    "rrtmgp-clouds-sw-bnd.nc": "7671835992a45afe66244b591a02c0b3df73d7d59ecb746bbffd9763497651cd",
}


def _environment(data_dir: Path):
    """Apply thread/data settings before importing any numerical packages."""
    os.environ.update(THREAD_ENV)
    os.environ["RRTMGP_DATA"] = str(data_dir)
    sys.dont_write_bytecode = True


def _root(root):
    value = Path(root).expanduser().resolve()
    if not (value / "workshop_model.py").is_file():
        raise RuntimeError(f"Not a workshop checkout: {value}. Open the notebook from your cloned repository.")
    return value


def _settings(root):
    root = _root(root)
    config_path = root / CONFIG_NAME
    if config_path.exists():
        try:
            settings = json.loads(config_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Cannot read {config_path}. Rerun bash configure_workshop.sh with the instructor's shared checkout path.") from exc
        if settings.get("schema_version") != 1:
            raise RuntimeError(f"Unsupported {CONFIG_NAME} format. Rerun bash configure_workshop.sh.")
        for key in ("runtime_prefix", "data_dir", "source_root"):
            if not isinstance(settings.get(key), str) or not Path(settings[key]).is_absolute():
                raise RuntimeError(f"{CONFIG_NAME} requires an absolute {key}. Rerun bash configure_workshop.sh.")
        return {key: Path(settings[key]).resolve() for key in ("runtime_prefix", "data_dir", "source_root")}, "shared"
    return {"runtime_prefix": root / "envs" / "rrtmgp",
            "data_dir": root / ".cache" / "rrtmgp-data", "source_root": root}, "local"


def _check_paths(settings, mode):
    python = settings["runtime_prefix"] / "bin" / "python"
    if not python.is_file() or not os.access(python, os.X_OK):
        if mode == "shared":
            raise RuntimeError(f"Shared Python is unavailable: {python}. Confirm the instructor's path is mounted on this node, then rerun bash configure_workshop.sh SHARED_CHECKOUT.")
        raise RuntimeError("No prepared runtime is configured. In your Linux terminal run bash configure_workshop.sh /path/to/instructor/shared-checkout, then select 'Python (RRTMGP Workshop)'. The timed activity does not install a new environment.")
    if not settings["source_root"].is_dir():
        raise RuntimeError(f"Shared source checkout is unavailable: {settings['source_root']}.")
    data = settings["data_dir"]
    actual = {}
    for filename, expected in COEFFICIENT_SHA256.items():
        path = data / filename
        try:
            value = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    value.update(chunk)
        except OSError as exc:
            raise RuntimeError(f"Cannot read prepared coefficient file {path}. Ask the instructor to repair the shared runtime/data; no participant download is needed.") from exc
        actual[filename] = value.hexdigest()
        if actual[filename] != expected:
            raise RuntimeError(f"Coefficient checksum mismatch: {path}. Ask the instructor to restore pinned rrtmgp-data v1.9 before continuing.")
    return actual


def prepare_notebook(root):
    """Validate and select shared/local inputs before importing workshop_model.

    Returns a JSON-compatible report with mode, three absolute paths, exact
    runtime versions and verified coefficient hashes. Never installs/downloads.
    A wrong kernel raises a readable RuntimeError before any numerical import.
    """
    settings, mode = _settings(root)
    _environment(settings["data_dir"])
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("The workshop kernel runs on the Linux x86_64 server. Use its Jupyter page from your laptop browser.")
    expected = settings["runtime_prefix"].resolve()
    if not (expected / "bin" / "python").is_file():
        _check_paths(settings, mode)  # Gives the missing-runtime setup instruction.
    if Path(sys.prefix).resolve() != expected:
        raise RuntimeError(f"Wrong notebook kernel: {sys.executable}. Select Kernel > Change Kernel > '{KERNEL_DISPLAY}', restart, then rerun this cell. Expected runtime: {expected}. If that kernel is missing, run bash configure_workshop.sh SHARED_CHECKOUT in your Linux terminal.")
    hashes = _check_paths(settings, mode)
    # Local helper uses the selected shared interpreter, without touching it.
    if __package__:
        from .check_runtime import check_runtime
    else:
        from check_runtime import check_runtime
    try:
        versions = check_runtime()
    except (RuntimeError, ImportError, OSError) as exc:
        raise RuntimeError(f"Prepared runtime validation failed: {exc}. Ask the instructor to repair it; participants should not run the installer during the activity.") from exc
    return {"mode": mode, **{key: str(value) for key, value in settings.items()},
            **versions, "coefficient_sha256": hashes}


def configure(root, source_root):
    """Validate shared assets and register only the current user's kernel."""
    root = _root(root)
    source_root = _root(source_root)
    settings = {"runtime_prefix": source_root / "envs" / "rrtmgp",
                "data_dir": source_root / ".cache" / "rrtmgp-data",
                "source_root": source_root}
    _environment(settings["data_dir"])
    if Path(sys.prefix).resolve() != settings["runtime_prefix"].resolve():
        raise RuntimeError("Configure must run with the shared interpreter. Use bash configure_workshop.sh SHARED_CHECKOUT.")
    hashes = _check_paths(settings, "shared")
    if __package__:
        from .check_runtime import check_runtime
    else:
        from check_runtime import check_runtime
    versions = check_runtime()
    python = settings["runtime_prefix"] / "bin" / "python"
    link = root / PYTHON_LINK
    if link.exists() and not link.is_symlink():
        raise RuntimeError(f"Refusing to replace non-symlink {link}. Move it aside and rerun configure.")
    from jupyter_core.paths import jupyter_data_dir
    kernel_destination = Path(jupyter_data_dir()).expanduser().resolve()
    for protected in (source_root, settings["runtime_prefix"], settings["data_dir"]):
        if kernel_destination.is_relative_to(protected.resolve()):
            raise RuntimeError("Your Jupyter user data directory points into the shared checkout. Ask the instructor to set JUPYTER_DATA_DIR to your personal directory before configuring; the shared tree will not be changed.")
    command = [str(python), "-B", "-m", "ipykernel", "install", "--user",
               "--name", KERNEL_NAME, "--display-name", KERNEL_DISPLAY]
    for key, value in {**THREAD_ENV, "RRTMGP_DATA": str(settings["data_dir"])}.items():
        command.extend(["--env", key, value])
    # --user writes to this participant's Jupyter data directory, never the
    # shared prefix. Shared libraries remain usable with read-only permissions.
    subprocess.run(command, check=True, env={**os.environ, "PYTHONPATH": ""})
    payload = {"schema_version": 1, **{key: str(value) for key, value in settings.items()}}
    with tempfile.NamedTemporaryFile(mode="w", prefix=".workshop-runtime-", suffix=".tmp", dir=root, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, indent=2)
        stream.write("\n")
    temporary.replace(root / CONFIG_NAME)
    # A local symlink lets the launcher read JSON using shared Python even when
    # the server has no system-wide python3 command. It contains no environment.
    staged_link = root / (PYTHON_LINK + ".tmp")
    staged_link.unlink(missing_ok=True)
    staged_link.symlink_to(python)
    staged_link.replace(link)
    print(f"Configured your checkout with the prepared shared runtime: {settings['runtime_prefix']}")
    print(f"Kernel: {KERNEL_DISPLAY}. No packages or coefficient files were downloaded.")
    print(f"In JupyterLab, open the notebook and select {KERNEL_DISPLAY}.")
    print("SSH-only access: start Jupyter with bash launch_workshop.sh 8888.")
    return {**payload, **versions, "coefficient_sha256": hashes}


def launch(root, port):
    """Launch shared/local Jupyter with the participant's checkout as root."""
    root = _root(root)
    report = prepare_notebook(root)
    runtime = Path(report["runtime_prefix"])
    os.chdir(root)
    os.environ["PYTHONPATH"] = ""
    command = [str(runtime / "bin" / "python"), "-B", "-m", "jupyterlab",
               "--no-browser", "--ip=127.0.0.1", f"--port={port}",
               "--ServerApp.port_retries=0", f"--ServerApp.root_dir={root}"]
    os.execv(command[0], command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    configure_parser = subparsers.add_parser("configure")
    configure_parser.add_argument("--root", required=True)
    configure_parser.add_argument("--source-root", required=True)
    launch_parser = subparsers.add_parser("launch")
    launch_parser.add_argument("--root", required=True)
    launch_parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
    try:
        if args.command == "configure":
            configure(args.root, args.source_root)
        else:
            if not 1024 <= args.port <= 65535:
                raise RuntimeError("Choose a numeric port between 1024 and 65535.")
            launch(args.root, args.port)
    except (RuntimeError, ImportError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"Workshop setup error: {exc}\n")


if __name__ == "__main__":
    main()

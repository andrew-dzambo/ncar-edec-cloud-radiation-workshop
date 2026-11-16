#!/usr/bin/env python3
"""Fetch immutable, checksum-verified upstream source/data snapshots.

No GitHub account/token is needed for these public read-only downloads.
The compiled runtime comes from conda-forge; the core source snapshot is for
inspection and optional future compilation, not the linked runtime.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = [
    dict(name="rte-rrtmgp", version="1.9.3",
         commit="c4098f552dc362986d67a32377c511d60b1d3d1b",
         sha256="9b56974d624e7385d39edf3b4db17ba402cc23fc9ad39b37138b1f164a8b5699",
         destination="vendor/rte-rrtmgp-v1.9.3"),
    dict(name="pyRTE-RRTMGP", version="0.2.5",
         commit="2fcb4eb306708c8a38974f34371c4206a505ce9f",
         sha256="de64fe212d1b162c0aee85e240500e9a049b7234cc1e89c3267b0dd11d21cdd6",
         destination="vendor/pyRTE-RRTMGP-v0.2.5"),
    dict(name="rrtmgp-data", version="1.9",
         commit="eff0433faf9cbac3ad14fbf608bef0c26ebc4c79",
         sha256="0872e828edba998b43f245a68f27f6605277190e3a251267348e6780e076377a",
         destination=".cache/rrtmgp-data"),
]
COEFFICIENT_SHA256 = {
    "rrtmgp-gas-lw-g256.nc": "4048360199d1917ed8f2ccaae2ec097d0f990da3bbad9830337b739b4fa01be7",
    "rrtmgp-gas-sw-g224.nc": "584f1dd41ea9fc07d4ee3754eb1dafbd46ad3161cd6fd20fa06b6922b6f0702e",
    "rrtmgp-clouds-lw-bnd.nc": "09d6704c5b863b4c3ceb417d20bb3076ec492e6bf2dfbcc9f3c5996a3706f0b0",
    "rrtmgp-clouds-sw-bnd.nc": "7671835992a45afe66244b591a02c0b3df73d7d59ecb746bbffd9763497651cd",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def provision() -> None:
    archive_dir = ROOT / ".cache" / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for spec in SNAPSHOTS:
        destination = ROOT / spec["destination"]
        marker = destination / ".workshop-source.json"
        if marker.exists() and json.loads(marker.read_text()) == spec:
            print(f"Using existing pinned snapshot: {spec['name']} {spec['version']}", flush=True)
            manifest.append(spec)
            continue
        archive = archive_dir / f"{spec['name']}-{spec['commit']}.tar.gz"
        if not archive.exists() or digest(archive) != spec["sha256"]:
            url = f"https://github.com/earth-system-radiation/{spec['name']}/archive/{spec['commit']}.tar.gz"
            temporary = archive.with_suffix(".part")
            print(f"Downloading {spec['name']} {spec['version']} ...", flush=True)
            for attempt in range(3):
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "RRTMGP-Cloud-Workshop/1.0"})
                    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as stream:
                        shutil.copyfileobj(response, stream, 1024 * 1024)
                    if digest(temporary) != spec["sha256"]:
                        raise RuntimeError(f"SHA-256 mismatch for {spec['name']}; refusing this archive.")
                    temporary.replace(archive)
                    break
                except Exception:
                    temporary.unlink(missing_ok=True)
                    if attempt == 2:
                        raise
                    time.sleep(2 * (attempt + 1))
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="rrtmgp-extract-", dir=destination.parent) as stage:
            stage = Path(stage)
            with tarfile.open(archive) as tar:
                # Python 3.11 security releases support filter='data'; it blocks
                # absolute/escaping paths and unsafe special-file extraction.
                tar.extractall(stage, filter="data")
            directories = list(stage.iterdir())
            if len(directories) != 1 or not directories[0].is_dir():
                raise RuntimeError(f"Unexpected archive layout: {archive}")
            if destination.exists():
                # Preserve any earlier snapshot, including local edits.
                backup = destination.with_name(destination.name + ".previous-" + str(time.time_ns()))
                destination.rename(backup)
                print(f"Preserved earlier snapshot: {backup}", flush=True)
            shutil.move(str(directories[0]), destination)
        marker.write_text(json.dumps(spec, indent=2) + "\n")
        manifest.append(spec)
    data_dir = ROOT / ".cache" / "rrtmgp-data"
    coefficients = {filename: digest(data_dir / filename) for filename in COEFFICIENT_SHA256}
    if coefficients != COEFFICIENT_SHA256:
        raise RuntimeError("Coefficient checksum mismatch. Move .cache/rrtmgp-data aside and rerun setup.")
    output = {"snapshots": manifest, "coefficient_sha256": coefficients,
              "compiled_runtime": "conda-forge rte_rrtmgp 1.9.2",
              "python_interface": "pyrte_rrtmgp 0.2.5"}
    (ROOT / "provenance.json").write_text(json.dumps(output, indent=2) + "\n")
    print(f"Sources, coefficients and provenance ready: {ROOT}", flush=True)


if __name__ == "__main__":
    provision()

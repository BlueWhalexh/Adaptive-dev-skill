#!/usr/bin/env python3
"""Prove the handoff pattern with a clean local consumer.

This deterministic eval builds a tiny wheel, installs it into a fresh virtual
environment without network or producer-source imports, and imports it from the
consumer environment. It proves the artifact/onboarding mechanics used by the
skill's handoff gate. It does not prove any project-specific real external
provider chain.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


PACKAGE = "adaptive_handoff_demo"
DIST = "adaptive_handoff_demo-0.1.0.dist-info"
WHEEL = "adaptive_handoff_demo-0.1.0-py3-none-any.whl"


def run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("command failed:\n" + " ".join(args) + "\n" + result.stdout)
    return result


def record_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def build_wheel(dist_dir: Path) -> Path:
    wheel_path = dist_dir / WHEEL
    files: dict[str, bytes] = {
        f"{PACKAGE}/__init__.py": b'def identity():\n    return "fresh-consumer-ok"\n',
        f"{DIST}/METADATA": (
            b"Metadata-Version: 2.1\n"
            b"Name: adaptive-handoff-demo\n"
            b"Version: 0.1.0\n"
            b"Summary: Adaptive workflow fresh consumer demo artifact\n"
        ),
        f"{DIST}/WHEEL": (
            b"Wheel-Version: 1.0\n"
            b"Generator: adaptive-dev-workflow\n"
            b"Root-Is-Purelib: true\n"
            b"Tag: py3-none-any\n"
        ),
    }

    records = []
    for name, data in files.items():
        records.append(f"{name},{record_hash(data)},{len(data)}")
    records.append(f"{DIST}/RECORD,,")
    files[f"{DIST}/RECORD"] = ("\n".join(records) + "\n").encode("utf-8")

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
        for name, data in files.items():
            wheel.writestr(name, data)
    return wheel_path


def venv_python(venv: Path) -> Path:
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-temp", action="store_true", help="print and keep the temp directory")
    args = parser.parse_args()

    temp_dir = Path(tempfile.mkdtemp(prefix="adaptive-handoff-consumer-"))
    try:
        dist_dir = temp_dir / "dist"
        dist_dir.mkdir(parents=True)
        wheel = build_wheel(dist_dir)

        venv = temp_dir / "consumer-venv"
        run([sys.executable, "-m", "venv", str(venv)])
        py = venv_python(venv)
        run([str(py), "-m", "pip", "install", "--no-index", "--disable-pip-version-check", str(wheel)])
        imported = run([
            str(py),
            "-c",
            (
                "import adaptive_handoff_demo; "
                "assert adaptive_handoff_demo.identity() == 'fresh-consumer-ok'; "
                "print(adaptive_handoff_demo.__file__)"
            ),
        ])

        imported_path = imported.stdout.strip()
        if not imported_path or str(dist_dir) in imported_path:
            raise SystemExit("fresh consumer imported from producer dist path, not installed environment")

        print("Fresh consumer handoff eval passed")
        print(f"- artifact: {wheel.name}")
        print(f"- consumer import path: {imported_path}")
        if args.keep_temp:
            print(f"- temp directory kept: {temp_dir}")
            temp_dir = Path()
        return 0
    finally:
        if temp_dir and temp_dir.exists() and not args.keep_temp:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    raise SystemExit(main())

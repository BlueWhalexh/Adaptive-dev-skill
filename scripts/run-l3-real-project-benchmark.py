#!/usr/bin/env python3
"""Prepare or execute a repeatable L3 real-project Codex benchmark.

The default action only prepares isolated SDK fixtures. Pass ``--execute`` to
run Codex and the independent verifier for each selected contract mode.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
OLD_COMMIT = "ab048a7"
MODES = ("old", "current", "none")
CONTRACT_PREFIXES = (
    "skills/adaptive-dev-workflow",
    "skills/workflow-control-plane",
    "skills/change-aware-testing",
    "skills/delivery-verification",
)
IMMUTABLE_PREFIXES = (
    "AGENTS.md",
    ".agent/skills",
    ".agent/runtime/capability-report.json",
    ".agent/runtime/workflow_manifest.json",
    ".benchmark",
    "docs",
    "tests",
)


def clean(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


AGENTS = clean(
    """
    # Fixture Instructions

    This is an isolated benchmark repository for a real, installable Python SDK.

    - The approved product spec, technical design, and eight-task plan are authoritative.
    - The project SOP is `.agent/skills/l3sdk-project/SKILL.md`; read its testing contract.
    - Work only on the eight remaining plan tasks. Preserve public names and acceptance behavior.
    - Do not edit `AGENTS.md`, `.agent/`, `.benchmark/`, `docs/`, `tests/`, or the independent verifier.
    - Runtime code may use only the Python standard library. Packaging may use setuptools.
    - Never commit credentials or print/repr bearer tokens.
    - Run focused tests while implementing, then the independent verifier once at the handoff boundary.
    - This fixture uses fake loopback HTTP only; do not claim a real external provider chain.
    """
)

PROJECT_SKILL = clean(
    """
    ---
    name: l3sdk-project
    description: Ready project SOP for the L3 SDK benchmark fixture.
    ---

    # L3 SDK Project SOP

    Read `references/testing.md`, the approved spec/design/plan, and
    `.agent/runtime/workflow_manifest.json` before implementation.

    ## Boundaries

    - Config migration and filesystem permissions are a data/security boundary.
    - Bearer authentication and HTTP error translation are an auth/external-I/O boundary.
    - Wheel installation and fresh-consumer import are a package handoff boundary.
    - Keep those boundaries separate. Shared low-risk work inside a boundary may be batched.

    ## Implementation

    Use stdlib runtime modules and setuptools only. Preserve immutable benchmark inputs.
    Treat the independent verifier as the final authority for this fake integration fixture.
    """
)

TESTING_CONTRACT = clean(
    """
    # Testing Contract

    Focused signal:

    ```sh
    PYTHONPATH=src python3 -m unittest discover -s tests -v
    ```

    Handoff gate:

    ```sh
    python3 .benchmark/independent_verifier.py .
    ```

    The handoff gate runs unit tests, builds a wheel, installs it into a fresh
    venv, imports from outside the producer tree, migrates a legacy config,
    performs a loopback fake-HTTP bearer-auth call, and scans for its sentinel
    secret. It is fake integration evidence, not a real external call.
    """
)

ANALYSIS = clean(
    """
    # Approved Analysis Pack

    The repository is a runnable setuptools `src/`-layout Python SDK scaffold.
    Current runtime behavior is intentionally incomplete. The approved remaining
    slice adds secure v1-to-v2 config migration, bearer-authenticated stdlib HTTP,
    stable public exports, and an installable wheel handoff.

    Known constraints: Python 3.9+, no runtime dependencies, no real network,
    immutable acceptance tests, and no secret material in source or artifacts.
    """
)

SPEC = clean(
    """
    # L3 SDK Secure Client Product Spec

    Status: APPROVED

    ## Goal

    Deliver an installable `l3sdk-benchmark` wheel whose `l3sdk` package safely
    migrates legacy config and performs bearer-authenticated JSON GET requests.

    ## Acceptance

    - AC-1: `Config` validates an HTTPS or loopback HTTP endpoint and a non-empty token.
    - AC-2: `load_config(path)` accepts v2 JSON and returns a redacted `Config` repr.
    - AC-3: legacy `{base_url, api_key}` JSON migrates atomically to schema version 2.
    - AC-4: migrated config is owner-only on POSIX and repeated loading is idempotent.
    - AC-5: request construction emits exactly `Authorization: Bearer <token>`.
    - AC-6: `Client.get(path)` uses stdlib HTTP, decodes JSON, and maps HTTP/JSON errors.
    - AC-7: `l3sdk` exports the approved API and version `1.0.0` without exposing secrets.
    - AC-8: setuptools builds a wheel that works from a fresh venv outside the source tree.

    ## Non-goals

    Async I/O, retries, OAuth refresh, non-JSON APIs, real provider calls, keyring
    integration, and backward-compatible aliases beyond the documented legacy file.
    """
)

DESIGN = clean(
    """
    # L3 SDK Technical Design

    Status: APPROVED by independent design-reviewer

    ## Modules

    - `errors.py`: stable `SDKError`, `ConfigError`, `AuthError`, `HTTPError` hierarchy.
    - `config.py`: immutable config model, validation, v1 parser, atomic v2 rewrite.
    - `auth.py`: narrow bearer header construction with no logging or repr leakage.
    - `transport.py`: `urllib.request` GET transport and JSON/error translation.
    - `client.py`: public orchestration and relative-path joining.
    - `__init__.py`: approved exports and package version.

    ## Contracts

    V2 config is `{\"schema_version\": 2, \"endpoint\": str, \"auth\": {\"token\": str}}`.
    Legacy input is `{\"base_url\": str, \"api_key\": str}`. Migration writes a
    sibling temporary file, chmods it to `0600` on POSIX, then uses `os.replace`.
    No token appears in exceptions, repr, verifier output, source, or wheel metadata.

    `Client.get(path)` joins a relative path to the configured endpoint, sends one
    GET with bearer auth and an SDK user agent, and returns a decoded JSON object.
    HTTP failures become `HTTPError`; malformed JSON also becomes `HTTPError`.

    ## Boundary checkpoints

    1. Config model + migration + file permissions/security.
    2. Bearer auth + HTTP transport + client composition/external I/O.
    3. Public API + wheel + fresh-consumer package handoff.
    """
)

PLAN = clean(
    """
    # L3 SDK Remaining Slice Plan

    Status: APPROVED

    Exactly eight remaining tasks follow. Preserve their order and use the three
    explicit boundary checkpoints; do not create per-task ceremony.

    1. Implement the stable exception hierarchy in `src/l3sdk/errors.py`.
    2. Implement validated, immutable, secret-redacting `Config` in `config.py`.
    3. Implement v2 loading plus atomic/idempotent v1 migration and POSIX `0600`.
    4. Implement bearer header construction in `auth.py` without secret leakage.
    5. Implement stdlib JSON GET transport and deterministic error translation.
    6. Implement `Client.from_config()` and `Client.get()` path composition.
    7. Publish the approved exports and `__version__ = \"1.0.0\"`.
    8. Complete setuptools metadata and README handoff usage for a fresh consumer.

    Checkpoint after task 3: config migration/security. Checkpoint after task 6:
    auth/external-I/O. Checkpoint after task 8: package handoff. Final acceptance is
    the independent verifier; its HTTP server is a local fake.
    """
)

README = clean(
    """
    # l3sdk benchmark fixture

    This repository is an isolated, stdlib-runtime Python SDK benchmark fixture.
    Follow the approved documents in `docs/`. Usage documentation is intentionally
    incomplete and is part of task 8.
    """
)

SETUP_PY = clean(
    """
    from setuptools import find_packages, setup


    setup(
        name="l3sdk-benchmark",
        version="0.0.0",
        description="L3 secure SDK benchmark fixture",
        package_dir={"": "src"},
        packages=find_packages("src"),
        python_requires=">=3.9",
    )
    """
)

PACKAGE_INIT = '"""L3 SDK benchmark scaffold."""\n\n__version__ = "0.0.0"\n'

STUB_MODULE = '"""Implementation pending in the approved remaining slice."""\n'

UNIT_TESTS = clean(
    """
    import json
    import os
    import tempfile
    import unittest
    from pathlib import Path
    from unittest import mock


    class ConfigTests(unittest.TestCase):
        def test_v2_load_and_repr_redacts_token(self):
            from l3sdk import Config, load_config

            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "config.json"
                path.write_text(json.dumps({
                    "schema_version": 2,
                    "endpoint": "https://example.invalid/api/",
                    "auth": {"token": "unit-token"},
                }), encoding="utf-8")
                config = load_config(path)
            self.assertIsInstance(config, Config)
            self.assertEqual(config.endpoint, "https://example.invalid/api/")
            self.assertEqual(config.token, "unit-token")
            self.assertNotIn("unit-token", repr(config))

        def test_legacy_config_migrates_atomically_and_idempotently(self):
            from l3sdk import load_config

            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "config.json"
                path.write_text(json.dumps({
                    "base_url": "https://example.invalid/api",
                    "api_key": "legacy-token",
                }), encoding="utf-8")
                first = load_config(path)
                migrated_once = path.read_bytes()
                second = load_config(path)
                migrated_twice = path.read_bytes()
                payload = json.loads(migrated_once.decode("utf-8"))
                self.assertEqual(payload, {
                    "schema_version": 2,
                    "endpoint": "https://example.invalid/api",
                    "auth": {"token": "legacy-token"},
                })
                self.assertEqual(migrated_once, migrated_twice)
                self.assertEqual(first, second)
                if os.name == "posix":
                    self.assertEqual(path.stat().st_mode & 0o777, 0o600)

        def test_invalid_or_missing_auth_is_rejected_without_echoing_input(self):
            from l3sdk import ConfigError, load_config

            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "config.json"
                path.write_text('{"base_url":"https://example.invalid","api_key":""}', encoding="utf-8")
                with self.assertRaises(ConfigError) as raised:
                    load_config(path)
            self.assertNotIn("api_key", str(raised.exception))

        def test_endpoint_rejects_non_loopback_plain_http(self):
            from l3sdk import Config, ConfigError

            with self.assertRaises(ConfigError):
                Config(endpoint="http://example.invalid", token="unit-token")


    class ClientTests(unittest.TestCase):
        def test_client_sends_bearer_header_and_decodes_json(self):
            from l3sdk import Client, Config

            response = mock.MagicMock()
            response.__enter__.return_value.read.return_value = b'{"ok": true}'
            response.__enter__.return_value.status = 200
            with mock.patch("urllib.request.urlopen", return_value=response) as opened:
                result = Client(Config("https://example.invalid/api/", "unit-token")).get("status")
            request = opened.call_args.args[0]
            self.assertEqual(request.full_url, "https://example.invalid/api/status")
            self.assertEqual(request.get_header("Authorization"), "Bearer unit-token")
            self.assertEqual(result, {"ok": True})

        def test_http_and_json_failures_use_sdk_error(self):
            from l3sdk import Client, Config, HTTPError

            response = mock.MagicMock()
            response.__enter__.return_value.read.return_value = b'not-json'
            response.__enter__.return_value.status = 200
            with mock.patch("urllib.request.urlopen", return_value=response):
                with self.assertRaises(HTTPError):
                    Client(Config("https://example.invalid", "unit-token")).get("status")

        def test_public_handoff_api(self):
            import l3sdk

            expected = {"AuthError", "Client", "Config", "ConfigError", "HTTPError", "SDKError", "load_config"}
            self.assertTrue(expected.issubset(set(l3sdk.__all__)))
            self.assertEqual(l3sdk.__version__, "1.0.0")


    if __name__ == "__main__":
        unittest.main()
    """
)


VERIFIER_SOURCE = clean(
    r'''
    #!/usr/bin/env python3
    """Independent fake-integration verifier for the L3 SDK fixture."""

    from __future__ import annotations

    import argparse
    import json
    import os
    import re
    import shutil
    import subprocess
    import sys
    import tempfile
    import zipfile
    from pathlib import Path


    SENTINEL = "l3-benchmark-sentinel-7f39c2"
    FORBIDDEN_STATIC = (b"-----BEGIN PRIVATE KEY-----", b"sk-live-", b"sk-prod-")


    def run(command, cwd=None, env=None):
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("command failed: {}\n{}".format(" ".join(command), result.stdout))
        return result.stdout


    def venv_python(root):
        if os.name == "nt":
            return root / "Scripts" / "python.exe"
        return root / "bin" / "python"


    def scan_file(path):
        data = path.read_bytes()
        if SENTINEL.encode("utf-8") in data:
            raise RuntimeError("sentinel secret leaked into {}".format(path))
        for marker in FORBIDDEN_STATIC:
            if marker in data:
                raise RuntimeError("credential-like marker found in {}".format(path))


    def scan_tree(root):
        ignored = {".git", ".benchmark", "__pycache__", "build", "dist", ".eggs"}
        for path in root.rglob("*"):
            if not path.is_file() or any(part in ignored for part in path.parts):
                continue
            scan_file(path)


    def scan_wheel(wheel):
        with zipfile.ZipFile(str(wheel)) as archive:
            for name in archive.namelist():
                data = archive.read(name)
                if SENTINEL.encode("utf-8") in data:
                    raise RuntimeError("sentinel secret leaked into wheel member {}".format(name))
                for marker in FORBIDDEN_STATIC:
                    if marker in data:
                        raise RuntimeError("credential-like marker in wheel member {}".format(name))


    CONSUMER = r"""
    import json
    import os
    import stat
    import tempfile
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from pathlib import Path

    import l3sdk

    seen = {}
    secret = os.environ["L3SDK_BENCH_SECRET"]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen["authorization"] = self.headers.get("Authorization")
            seen["path"] = self.path
            payload = json.dumps({"ok": True, "path": self.path}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.json"
            path.write_text(json.dumps({
                "base_url": "http://127.0.0.1:{}".format(server.server_port),
                "api_key": secret,
            }), encoding="utf-8")
            client = l3sdk.Client.from_config(path)
            result = client.get("v1/status")
            migrated = json.loads(path.read_text(encoding="utf-8"))
            assert migrated["schema_version"] == 2
            assert migrated["auth"]["token"] == secret
            assert "api_key" not in migrated
            assert secret not in repr(client.config)
            if os.name == "posix":
                assert stat.S_IMODE(path.stat().st_mode) == 0o600
            assert result == {"ok": True, "path": "/v1/status"}
    finally:
        thread.join(timeout=5)
        server.server_close()

    assert seen == {"authorization": "Bearer " + secret, "path": "/v1/status"}
    print(json.dumps({"fresh_import": l3sdk.__file__, "migration": "pass", "fake_http_auth": "pass"}))
    """


    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("fixture")
        args = parser.parse_args()
        fixture = Path(args.fixture).resolve()

        unit_env = dict(os.environ)
        unit_env["PYTHONPATH"] = str(fixture / "src") + os.pathsep + unit_env.get("PYTHONPATH", "")
        unit_output = run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=fixture,
            env=unit_env,
        )
        match = re.search(r"Ran (\d+) tests?", unit_output)
        unit_count = int(match.group(1)) if match else 0
        if unit_count < 7:
            raise RuntimeError("expected at least seven unit tests")

        for name in ("build", "dist"):
            target = fixture / name
            if target.exists():
                shutil.rmtree(str(target))
        run([sys.executable, "setup.py", "bdist_wheel", "--dist-dir", "dist"], cwd=fixture)
        wheels = sorted((fixture / "dist").glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("expected exactly one wheel, got {}".format(len(wheels)))
        wheel = wheels[0]
        scan_wheel(wheel)

        with tempfile.TemporaryDirectory(prefix="l3sdk-fresh-consumer-") as tmp:
            root = Path(tmp)
            venv = root / "venv"
            run([sys.executable, "-m", "venv", str(venv)])
            python = venv_python(venv)
            run([str(python), "-m", "pip", "install", "--no-index", "--disable-pip-version-check", str(wheel)])
            consumer = root / "consumer"
            consumer.mkdir()
            env = dict(os.environ)
            env["L3SDK_BENCH_SECRET"] = SENTINEL
            output = run([str(python), "-c", CONSUMER], cwd=consumer, env=env)
            if SENTINEL in output:
                raise RuntimeError("sentinel secret leaked into consumer output")
            payload = json.loads(output.strip().splitlines()[-1])
            imported = Path(payload["fresh_import"]).resolve()
            if str(imported).startswith(str(fixture)):
                raise RuntimeError("fresh consumer imported from producer tree")
            if payload["migration"] != "pass" or payload["fake_http_auth"] != "pass":
                raise RuntimeError("fresh consumer checks did not pass")

        scan_tree(fixture)
        print(json.dumps({
            "status": "pass",
            "evidence_level": "fake_integration_and_fresh_consumer",
            "unit_tests": unit_count,
            "wheel": wheel.name,
            "fresh_venv_import": "pass",
            "config_migration": "pass",
            "fake_http_auth": "pass",
            "secret_scan": "pass",
            "real_external_call": False,
        }, sort_keys=True))
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
    '''
)


FIXTURE_FILES = {
    "AGENTS.md": AGENTS,
    ".agent/skills/l3sdk-project/SKILL.md": PROJECT_SKILL,
    ".agent/skills/l3sdk-project/references/testing.md": TESTING_CONTRACT,
    "docs/analysis/current-truth.md": ANALYSIS,
    "docs/spec/sdk-spec.md": SPEC,
    "docs/design/sdk-design.md": DESIGN,
    "docs/plan/sdk-plan.md": PLAN,
    "docs/tasks/bootstrap.json": json.dumps(
        {
            "task_packet_id": "bootstrap-001",
            "status": "approved",
            "purpose": "Runnable setuptools/src-layout scaffold accepted at architecture checkpoint",
            "remaining_plan_tasks": 8,
        },
        indent=2,
    )
    + "\n",
    "README.md": README,
    "setup.py": SETUP_PY,
    "src/l3sdk/__init__.py": PACKAGE_INIT,
    "src/l3sdk/errors.py": STUB_MODULE,
    "src/l3sdk/config.py": STUB_MODULE,
    "src/l3sdk/auth.py": STUB_MODULE,
    "src/l3sdk/transport.py": STUB_MODULE,
    "src/l3sdk/client.py": STUB_MODULE,
    "tests/test_sdk.py": UNIT_TESTS,
    ".benchmark/independent_verifier.py": VERIFIER_SOURCE,
    ".gitignore": "__pycache__/\n*.py[cod]\nbuild/\ndist/\n*.egg-info/\n.venv/\n",
}


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, str(path))
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def run_checked(command: Sequence[str], cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        fail("command failed: {}\n{}".format(" ".join(command), result.stdout))
    return result


def contract_files_at_commit(commit: str) -> Iterable[Tuple[str, bytes]]:
    command = ["git", "ls-tree", "-r", "--name-only", commit, "--"] + list(CONTRACT_PREFIXES)
    result = run_checked(command, ROOT)
    for relative in result.stdout.splitlines():
        if not relative or "__pycache__" in Path(relative).parts or relative.endswith((".pyc", ".pyo")):
            continue
        content = run_checked(["git", "show", "{}:{}".format(commit, relative)], ROOT).stdout.encode("utf-8")
        yield relative, content


def contract_files_from_worktree() -> Iterable[Tuple[str, bytes]]:
    for prefix in CONTRACT_PREFIXES:
        base = ROOT / prefix
        if not base.exists():
            fail("missing current contract path: " + prefix)
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            yield path.relative_to(ROOT).as_posix(), path.read_bytes()


def inject_contract(fixture: Path, mode: str) -> Dict[str, Any]:
    if mode == "none":
        return {"kind": "none", "revision": None, "file_count": 0, "sha256": None}
    destination = fixture / ".benchmark" / "workflow-contract"
    source = contract_files_at_commit(OLD_COMMIT) if mode == "old" else contract_files_from_worktree()
    digest = hashlib.sha256()
    count = 0
    for relative, content in source:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        digest.update(relative.encode("utf-8") + b"\0" + content + b"\0")
        count += 1
    if not count:
        fail("empty workflow contract for mode " + mode)
    revision = OLD_COMMIT if mode == "old" else "working-tree"
    write_json(destination / "contract-source.json", {"mode": mode, "revision": revision, "files": count, "sha256": digest.hexdigest()})
    return {"kind": mode, "revision": revision, "file_count": count, "sha256": digest.hexdigest()}


def strategy_root(fixture: Path, mode: str) -> Path:
    if mode in {"old", "current"}:
        return fixture / ".benchmark" / "workflow-contract" / "skills" / "workflow-control-plane"
    return ROOT / "skills" / "workflow-control-plane"


def make_manifest(fixture: Path, mode: str) -> Dict[str, Any]:
    workflow = strategy_root(fixture, mode)
    strategy = json.loads((workflow / "references" / "strategies" / "complex-real-slice.json").read_text(encoding="utf-8"))
    schema = json.loads((workflow / "schemas" / "workflow-manifest.schema.json").read_text(encoding="utf-8"))
    schema_version = schema["properties"]["schema_version"]["enum"][0]
    skill_plan = {stage: strategy.get("stage_skills", {}).get(stage, []) for stage in strategy["stages"]}
    validated = ["analysis-001", "context-001", "spec-001", "design-001", "plan-001", "task-bootstrap", "impl-bootstrap"]
    manifest = {
        "schema_version": schema_version,
        "skill_suite_version": "benchmark-{}".format(mode),
        "run_id": "l3sdk-benchmark-{}".format(mode),
        "manifest_revision": 9,
        "strategy_version": strategy["version"],
        "workflow_state": "active",
        "classification": {
            "risk": "L3",
            "mode": "handoff",
            "scope": "cross_module",
            "uncertainty": "low",
            "pattern_familiarity": "known",
            "profiles": ["api", "auth", "security", "data", "release"],
        },
        "routing": {
            "process_depth": strategy["process_depth"],
            "manifest_policy": strategy["manifest_policy"],
            "spec_system": "fallback",
            "execution_engine": strategy["execution_engine"],
            "strategy_id": strategy["id"],
            "required_skills": skill_plan["remaining_slice_execution"],
            "skill_plan": skill_plan,
            "capability_report_ref": ".agent/runtime/capability-report.json",
        },
        "selected_strategy": strategy["id"],
        "current_stage": "remaining_slice_execution",
        "resume": {
            "checkpoint_id": "cp-architecture-checkpoint",
            "resume_from_stage": "remaining_slice_execution",
            "last_validated_artifact_ids": validated,
            "blocked_reason": "",
        },
        "design_control": {
            "policy": "standalone",
            "review": "independent",
            "documentation_topology": "split_design_workspace",
            "triggers": ["data_model", "migration", "auth_permission_security", "external_integration"],
            "artifact_id": "design-001",
            "approval": {
                "status": "approved",
                "reviewer": "design-reviewer",
                "reviewer_kind": "agent",
                "evidence_ids": ["design-review-001"],
            },
        },
        "artifacts": [
            {"id": "analysis-001", "type": "analysis_pack", "status": "approved", "version": 1, "producer": "context-grounding", "depends_on": [], "covers_acceptance": ["AC-1", "AC-8"], "path": "docs/analysis/current-truth.md"},
            {"id": "context-001", "type": "context_manifest", "status": "ready", "version": 1, "producer": "context-grounding", "depends_on": ["analysis-001"], "covers_acceptance": ["AC-1", "AC-8"], "path": ".agent/runtime/capability-report.json"},
            {"id": "spec-001", "type": "spec", "status": "approved", "version": 1, "producer": "specflow", "depends_on": ["analysis-001"], "covers_acceptance": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6", "AC-7", "AC-8"], "path": "docs/spec/sdk-spec.md"},
            {"id": "design-001", "type": "technical_design", "status": "approved", "version": 1, "producer": "technical-design", "depends_on": ["spec-001", "analysis-001", "context-001"], "covers_acceptance": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6", "AC-7", "AC-8"], "path": "docs/design/sdk-design.md"},
            {"id": "plan-001", "type": "plan", "status": "approved", "version": 1, "producer": "superpowers:writing-plans", "depends_on": ["design-001"], "covers_acceptance": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6", "AC-7", "AC-8"], "path": "docs/plan/sdk-plan.md"},
            {"id": "task-bootstrap", "type": "task_packet", "status": "ready", "version": 1, "producer": "workflow-control-plane", "depends_on": ["plan-001", "context-001"], "covers_acceptance": ["AC-8"], "path": "docs/tasks/bootstrap.json"},
            {"id": "impl-bootstrap", "type": "implementation", "status": "ready", "version": 1, "producer": "fixture-builder", "depends_on": ["task-bootstrap"], "covers_acceptance": ["AC-8"], "path": "setup.py"},
        ],
        "claims": {"requested": "none", "validated": []},
        "transition_log": [
            {"transition_id": "advance-{:02d}".format(index + 1), "stage_id": stage, "status": "completed"}
            for index, stage in enumerate(strategy["stages"][: strategy["stages"].index("remaining_slice_execution")])
        ],
    }
    if "execution_policy" in strategy:
        manifest["routing"]["execution_policy"] = strategy["execution_policy"]
    if schema_version >= 6:
        manifest["review_control"] = {
            "stage_id": "architecture_checkpoint",
            "passes_completed": 1,
            "last_severity": "none",
            "decision": "approved",
            "next_action": "none",
            "repair_stage": "slice_execution",
            "finding_refs": [],
        }
    return manifest


def capability_report() -> Dict[str, Any]:
    return {
        "schema_version": 3,
        "repo_revision": "fixture-baseline",
        "spec_systems": [
            {"id": "openspec", "status": "missing", "evidence": []},
            {"id": "repo_native", "status": "available", "evidence": ["docs/spec", "docs/plan"]},
            {"id": "fallback", "status": "available", "evidence": ["approved fixture docs"]},
        ],
        "execution_engines": [{"id": "local", "status": "available", "version": "builtin"}],
        "method_providers": [{"id": "superpowers-native", "status": "unknown", "version": "unknown", "evidence": []}],
        "project_harness": {"status": "present", "version": "1", "evidence": ["AGENTS.md", ".agent"]},
        "project_sop": {
            "status": "ready",
            "evidence": ["AGENTS.md", ".agent/skills/l3sdk-project/SKILL.md", ".agent/skills/l3sdk-project/references/testing.md"],
            "signals": {
                "instructions": ["AGENTS.md"],
                "project_skills": [".agent/skills/l3sdk-project/SKILL.md"],
                "test_contracts": [".agent/skills/l3sdk-project/references/testing.md"],
            },
        },
    }


def validate_manifest(fixture: Path, mode: str) -> Dict[str, Any]:
    workflow = strategy_root(fixture, mode)
    commands = [
        [sys.executable, str(workflow / "scripts" / "validate_workflow_manifest.py"), str(fixture / ".agent/runtime/workflow_manifest.json")],
        [sys.executable, str(workflow / "scripts" / "validate_artifact_graph.py"), str(fixture / ".agent/runtime/workflow_manifest.json")],
    ]
    outputs = []
    for command in commands:
        result = run_checked(command, fixture)
        outputs.append(result.stdout.strip())
    return {"status": "pass", "commands": [command[1].split("/skills/", 1)[-1] for command in commands], "output": outputs}


def initialize_git(fixture: Path) -> str:
    run_checked(["git", "init", "-q"], fixture)
    run_checked(["git", "add", "--all"], fixture)
    run_checked(
        ["git", "-c", "user.name=L3 Benchmark", "-c", "user.email=benchmark@example.invalid", "commit", "-q", "-m", "fixture baseline"],
        fixture,
    )
    return run_checked(["git", "rev-parse", "HEAD"], fixture).stdout.strip()


def immutable_hashes(fixture: Path) -> Dict[str, str]:
    hashes = {}
    for prefix in IMMUTABLE_PREFIXES:
        path = fixture / prefix
        candidates = [path] if path.is_file() else sorted(path.rglob("*")) if path.exists() else []
        for candidate in candidates:
            if candidate.is_file() and "__pycache__" not in candidate.parts and candidate.suffix not in {".pyc", ".pyo"}:
                hashes[candidate.relative_to(fixture).as_posix()] = sha256_bytes(candidate.read_bytes())
    return hashes


def prepare_fixture(run_root: Path, mode: str) -> Tuple[Path, Dict[str, Any], Dict[str, str]]:
    fixture = run_root / "fixtures" / mode
    if fixture.exists():
        fail("fixture already exists; choose a new --output-dir: " + str(fixture))
    fixture.mkdir(parents=True)
    for relative, content in FIXTURE_FILES.items():
        write_text(fixture / relative, content)
    if mode == "none":
        write_text(
            fixture / ".agent/skills/l3sdk-project/SKILL.md",
            PROJECT_SKILL.replace(
                "Read `references/testing.md`, the approved spec/design/plan, and\n`.agent/runtime/workflow_manifest.json` before implementation.",
                "Read `references/testing.md` and the approved spec/design/plan before implementation.",
            ),
        )
    contract = inject_contract(fixture, mode)
    write_json(fixture / ".agent/runtime/capability-report.json", capability_report())
    manifest = None if mode == "none" else make_manifest(fixture, mode)
    validation = {"status": "not_applicable", "commands": [], "output": []}
    if manifest is not None:
        write_json(fixture / ".agent/runtime/workflow_manifest.json", manifest)
        validation = validate_manifest(fixture, mode)
    baseline_commit = initialize_git(fixture)
    hashes = immutable_hashes(fixture)
    prepared = {
        "fixture": str(fixture),
        "contract": contract,
        "workflow": {
            "schema_version": manifest["schema_version"] if manifest else None,
            "strategy": manifest["selected_strategy"] if manifest else None,
            "strategy_version": manifest["strategy_version"] if manifest else None,
            "current_stage": manifest["current_stage"] if manifest else None,
            "remaining_tasks": 8,
            "boundary_checkpoints": 3,
            "validation": validation,
        },
        "project_sop": "ready",
        "baseline_commit": baseline_commit,
        "immutable_file_count": len(hashes),
    }
    return fixture, prepared, hashes


def execution_prompt(mode: str) -> str:
    contract = ""
    if mode == "old":
        contract = clean(
            """
            Benchmark workflow contract mode: {mode}. Read the injected contracts under
            `.benchmark/workflow-contract/skills/`, especially adaptive-dev-workflow,
            workflow-control-plane, and change-aware-testing. Follow only the methods
            active at `remaining_slice_execution`; do not restart approved stages.
            """
        ).format(mode=mode)
    elif mode == "current":
        contract = clean(
            """
            Benchmark workflow contract mode: current. This is continuation work with
            an active manifest, so do not reload adaptive task intake or completed
            lifecycle stages. Validate/resume `.agent/runtime/workflow_manifest.json`,
            then read only the project SOP and the skill named by
            `routing.required_skills` for `remaining_slice_execution`.
            """
        )
    else:
        return clean(
            """
            You are the implementation worker for this isolated real Python SDK fixture.

            No workflow skill or workflow manifest is provided. Read `AGENTS.md`, the
            project SOP, approved spec/design/plan, and tests. Implement exactly the
            eight remaining plan tasks across the three declared boundaries.

            Do not edit immutable benchmark inputs: `AGENTS.md`, `.agent/`, `.benchmark/`,
            `docs/`, or `tests/`. You may edit `src/l3sdk/**`, `setup.py`, and `README.md`.
            Keep runtime dependencies stdlib-only and packaging setuptools-only. Use the
            documented independent verifier for final acceptance. Do not commit, push,
            make a real external call, create unrelated artifacts, or claim more than
            the fake integration/fresh-consumer evidence proves.
            """
        )
    return clean(
        """
        You are the implementation worker for this isolated real Python SDK fixture.

        {contract}

        Read `AGENTS.md`, the ready project SOP, approved spec/design/plan, tests, and
        `.agent/runtime/workflow_manifest.json`. The workflow is already at
        `remaining_slice_execution`. Implement exactly the eight remaining plan tasks
        across the three declared boundaries. Keep runtime dependencies stdlib-only
        and packaging setuptools-only.

        Do not edit immutable benchmark inputs: `AGENTS.md`, `.agent/`, `.benchmark/`,
        `docs/`, or `tests/`. You may edit `src/l3sdk/**`, `setup.py`, and `README.md`.
        Run focused tests while working and the documented independent verifier at the
        package-handoff checkpoint. Perform a final review for correctness, boundary
        behavior, secret leakage, and handoff readiness. Do not commit, push, make a
        real external call, create unrelated artifacts, or claim more than the fake
        integration/fresh-consumer evidence proves.
        """
    ).format(contract=contract.strip())


def nested_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from nested_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from nested_strings(item)


def item_from_event(event: Dict[str, Any]) -> Dict[str, Any]:
    item = event.get("item")
    return item if isinstance(item, dict) else {}


def parse_jsonl(path: Path) -> Dict[str, Any]:
    events = []
    malformed = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            events.append(value)

    usage = {"input_tokens": 0, "cached_input_tokens": 0, "uncached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}
    command_ids = set()
    failed_command_ids = set()
    test_command_ids = set()
    review_ids = set()
    artifact_ids = set()
    subagent_ids = set()
    for index, event in enumerate(events):
        raw_usage = event.get("usage")
        if isinstance(raw_usage, dict):
            for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
                value = raw_usage.get(key, 0)
                if isinstance(value, int):
                    usage[key] += value
            direct_reasoning = raw_usage.get("reasoning_output_tokens")
            if isinstance(direct_reasoning, int):
                usage["reasoning_output_tokens"] += direct_reasoning
            else:
                details = raw_usage.get("output_tokens_details")
                if isinstance(details, dict) and isinstance(details.get("reasoning_tokens"), int):
                    usage["reasoning_output_tokens"] += details["reasoning_tokens"]
        item = item_from_event(event)
        item_type = str(item.get("type", event.get("type", ""))).lower()
        item_id = str(item.get("id", "event-{}".format(index)))
        text_value = "\n".join(nested_strings(item))
        lowered = text_value.lower()
        completed = str(event.get("type", "")).endswith("completed") or item.get("status") in {"completed", "failed"}
        if "command_execution" in item_type and completed:
            command_ids.add(item_id)
            exit_code = item.get("exit_code")
            if isinstance(exit_code, int) and exit_code != 0:
                failed_command_ids.add(item_id)
            if re.search(r"(^|[ /_-])(pytest|unittest|test|verifier|bdist_wheel)([ /_.-]|$)", lowered):
                test_command_ids.add(item_id)
        if ("review" in item_type or "review" in lowered) and completed:
            review_ids.add(item_id)
        if completed and any(marker in lowered for marker in ("review-package", "work-order", "evidence_manifest", "artifact")):
            artifact_ids.add(item_id)
        if completed and ("subagent" in item_type or any(marker in lowered for marker in ("spawn_agent", "send_input", "wait_agent", "close_agent"))):
            subagent_ids.add(item_id)
    usage["uncached_input_tokens"] = max(usage["input_tokens"] - usage["cached_input_tokens"], 0)
    return {
        "events": len(events),
        "malformed_lines": malformed,
        "usage": usage,
        "counts": {
            "commands": len(command_ids),
            "failed_commands": len(failed_command_ids),
            "test_commands": len(test_command_ids),
            "review_events": len(review_ids),
            "artifact_events": len(artifact_ids),
            "subagent_events": len(subagent_ids),
        },
    }


def git_changes(fixture: Path) -> Dict[str, Any]:
    result = run_checked(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], fixture)
    entries = [entry for entry in result.stdout.split("\0") if entry]
    paths = []
    statuses = []
    for entry in entries:
        status = entry[:2]
        path = entry[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        statuses.append(status)
        paths.append(path)
    artifact_paths = [path for path in paths if any(part in path.lower() for part in ("artifact", "evidence", "review", "work-order", "report"))]
    return {
        "files_changed": len(paths),
        "files_added": sum(1 for status in statuses if "A" in status or status == "??"),
        "files_deleted": sum(1 for status in statuses if "D" in status),
        "artifact_files": len(artifact_paths),
        "paths": sorted(paths),
    }


def compare_immutable(fixture: Path, before: Dict[str, str]) -> Dict[str, Any]:
    after = immutable_hashes(fixture)
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    return {"status": "pass" if not changed else "fail", "changed": changed, "checked": len(before)}


def run_codex(fixture: Path, mode: str, run_root: Path, codex_bin: str) -> Dict[str, Any]:
    logs = run_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    jsonl_path = logs / (mode + ".jsonl")
    stderr_path = logs / (mode + ".stderr.log")
    command = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
        "--json",
        "-C",
        str(fixture),
        execution_prompt(mode),
    ]
    started = time.monotonic()
    with jsonl_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
        result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout_handle, stderr=stderr_handle, check=False, text=True)
    wall_time = time.monotonic() - started
    parsed = parse_jsonl(jsonl_path)
    parsed["exit_code"] = result.returncode
    parsed["wall_time_seconds"] = round(wall_time, 3)
    parsed["command"] = command[:-1] + ["<implementation-prompt>"]
    parsed["jsonl"] = str(jsonl_path)
    parsed["stderr"] = str(stderr_path)
    parsed["file_metrics"] = git_changes(fixture)
    parsed["counts"]["files"] = parsed["file_metrics"]["files_changed"]
    parsed["counts"]["artifacts"] = parsed["counts"]["artifact_events"] + parsed["file_metrics"]["artifact_files"]
    return parsed


def run_independent_verifier(fixture: Path, run_root: Path, mode: str) -> Dict[str, Any]:
    verifier_dir = run_root / "independent-verifier"
    verifier_dir.mkdir(parents=True, exist_ok=True)
    verifier = verifier_dir / (mode + "-verifier.py")
    write_text(verifier, VERIFIER_SOURCE)
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(verifier), str(fixture)],
        cwd=str(run_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    wall_time = time.monotonic() - started
    payload = None
    for line in reversed(result.stdout.splitlines()):
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and "status" in candidate:
            payload = candidate
            break
    return {
        "status": "pass" if result.returncode == 0 and payload and payload.get("status") == "pass" else "fail",
        "exit_code": result.returncode,
        "wall_time_seconds": round(wall_time, 3),
        "result": payload,
        "output": result.stdout[-8000:],
    }


def default_output_dir() -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return ROOT / "outputs" / "l3-real-project-benchmark-{}-{}".format(stamp, os.getpid())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        action="append",
        choices=MODES,
        help="contract mode; repeat to select multiple (default: old, current, none)",
    )
    parser.add_argument("--execute", action="store_true", help="run Codex and the independent verifier after preparing fixtures")
    parser.add_argument("--output-dir", type=Path, help="new directory for fixtures, logs, and report JSON")
    parser.add_argument("--codex-bin", default="codex", help="Codex executable used only with --execute (default: codex)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    modes = list(dict.fromkeys(args.mode or MODES))
    run_root = (args.output_dir or default_output_dir()).expanduser().resolve()
    if run_root.exists() and any(run_root.iterdir()):
        fail("--output-dir must not already contain files: " + str(run_root))
    run_root.mkdir(parents=True, exist_ok=True)

    report = {
        "schema_version": 1,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_repository": str(ROOT),
        "old_contract_commit": OLD_COMMIT,
        "execute": bool(args.execute),
        "modes": modes,
        "results": [],
    }
    report_path = run_root / "report.json"
    exit_code = 0
    for mode in modes:
        fixture, prepared, immutable = prepare_fixture(run_root, mode)
        result = {"mode": mode, "status": "prepared", "preparation": prepared}
        report["results"].append(result)
        atomic_write_json(report_path, report)
        print("Prepared {} fixture: {}".format(mode, fixture))
        if not args.execute:
            continue
        codex = run_codex(fixture, mode, run_root, args.codex_bin)
        immutable_result = compare_immutable(fixture, immutable)
        verification = run_independent_verifier(fixture, run_root, mode) if immutable_result["status"] == "pass" else {
            "status": "blocked",
            "reason": "Codex modified immutable benchmark inputs",
        }
        result.update({"codex": codex, "immutable_inputs": immutable_result, "verification": verification})
        if codex["exit_code"] == 0 and immutable_result["status"] == "pass" and verification["status"] == "pass":
            result["status"] = "pass"
        else:
            result["status"] = "fail"
            exit_code = 1
        atomic_write_json(report_path, report)
        print("Executed {} fixture: {}".format(mode, result["status"]))

    atomic_write_json(report_path, report)
    print("Benchmark report: {}".format(report_path))
    if not args.execute:
        print("Preparation only; pass --execute to run Codex.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

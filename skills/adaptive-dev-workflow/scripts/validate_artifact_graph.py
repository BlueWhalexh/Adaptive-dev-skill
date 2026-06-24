#!/usr/bin/env python3
"""Validate workflow artifact dependencies and stale propagation."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path

from validate_json_artifact import load_json
from validate_workflow_manifest import validate as validate_manifest


READY = {"ready", "approved"}
FRESH = {"ready", "approved"}


def has_dep(artifact: dict, by_id: dict[str, dict], artifact_type: str, statuses: set[str]) -> bool:
    for dep_id in artifact["depends_on"]:
        dep = by_id.get(dep_id)
        if dep and dep["type"] == artifact_type and dep["status"] in statuses:
            return True
    return False


def dep_ids_of_type(artifact: dict, by_id: dict[str, dict], artifact_type: str, statuses: set[str] | None = None) -> list[str]:
    matches: list[str] = []
    for dep_id in artifact["depends_on"]:
        dep = by_id.get(dep_id)
        if dep and dep["type"] == artifact_type and (statuses is None or dep["status"] in statuses):
            matches.append(dep_id)
    return matches


def detect_cycles(artifacts: list[dict], by_id: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            errors.append("artifact dependency cycle: " + " -> ".join(stack + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for dep_id in by_id[node]["depends_on"]:
            if dep_id in by_id:
                visit(dep_id, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for artifact in artifacts:
        visit(artifact["id"], [])
    return errors


def validate_stale_closure(artifacts: list[dict], by_id: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    reverse: dict[str, list[str]] = defaultdict(list)
    for artifact in artifacts:
        for dep_id in artifact["depends_on"]:
            if dep_id in by_id:
                reverse[dep_id].append(artifact["id"])

    queue: deque[tuple[str, str]] = deque()
    for artifact in artifacts:
        if artifact["status"] == "stale":
            for downstream in reverse[artifact["id"]]:
                queue.append((artifact["id"], downstream))

    seen: set[tuple[str, str]] = set()
    while queue:
        source, current = queue.popleft()
        if (source, current) in seen:
            continue
        seen.add((source, current))
        artifact = by_id[current]
        if artifact["status"] not in {"stale", "rejected"}:
            errors.append(f"{current} must be stale/rejected because upstream {source} is stale")
        for downstream in reverse[current]:
            queue.append((source, downstream))
    return errors


def validate(path: Path) -> list[str]:
    errors = validate_manifest(path)
    if errors:
        return errors

    manifest = load_json(path)
    artifacts = manifest["artifacts"]
    by_id: dict[str, dict] = {}
    for artifact in artifacts:
        if artifact["id"] in by_id:
            errors.append(f"duplicate artifact id: {artifact['id']}")
        by_id[artifact["id"]] = artifact
    errors.extend(detect_cycles(artifacts, by_id))
    errors.extend(validate_stale_closure(artifacts, by_id))

    for artifact in artifacts:
        for dep_id in artifact["depends_on"]:
            if dep_id not in by_id:
                errors.append(f"{artifact['id']} depends on missing artifact {dep_id}")

    design = manifest["design_control"]
    policy = design["policy"]
    plan_ids = {item["id"] for item in artifacts if item["type"] == "plan"}
    design_id = design.get("artifact_id")
    for artifact in artifacts:
        kind = artifact["type"]
        if kind == "spec" and not artifact.get("lightweight_exception"):
            if not has_dep(artifact, by_id, "analysis_pack", {"approved"}):
                errors.append(f"spec {artifact['id']} requires approved analysis_pack dependency or lightweight_exception")
        if kind == "technical_design":
            if not has_dep(artifact, by_id, "spec", {"approved"}):
                errors.append(f"technical_design {artifact['id']} requires approved spec dependency")
            if policy == "standalone" and artifact["id"] == design_id:
                if artifact["status"] != "approved":
                    errors.append(f"standalone technical_design {artifact['id']} must be approved")
                if not has_dep(artifact, by_id, "analysis_pack", {"approved"}):
                    errors.append(f"standalone technical_design {artifact['id']} requires approved analysis_pack dependency")
                if not has_dep(artifact, by_id, "context_manifest", READY):
                    errors.append(f"standalone technical_design {artifact['id']} requires ready/approved context_manifest dependency")
        if kind == "plan":
            if policy == "standalone":
                if not design_id or not has_dep(artifact, by_id, "technical_design", {"approved"}):
                    errors.append(f"plan {artifact['id']} requires approved technical_design dependency for standalone design")
            elif policy == "embedded":
                if artifact["id"] == design.get("embedded_in"):
                    if design.get("section_ref", "").strip() == "":
                        errors.append(f"embedded plan {artifact['id']} requires non-empty section_ref")
                    if design["approval"]["status"] != "approved":
                        errors.append(f"embedded plan {artifact['id']} requires approved design_control.approval")
                if not has_dep(artifact, by_id, "spec", {"approved"}):
                    errors.append(f"plan {artifact['id']} requires approved spec dependency for embedded design")
            elif policy == "none":
                if not has_dep(artifact, by_id, "spec", {"approved"}) and manifest["classification"]["mode"] not in {"review", "spike"}:
                    errors.append(f"plan {artifact['id']} requires approved spec dependency")
        if kind == "task_packet":
            if not has_dep(artifact, by_id, "plan", {"approved"}):
                errors.append(f"task_packet {artifact['id']} requires approved plan dependency")
            if not has_dep(artifact, by_id, "context_manifest", READY):
                errors.append(f"task_packet {artifact['id']} requires ready/approved context_manifest dependency")
        if kind == "implementation" and not has_dep(artifact, by_id, "task_packet", {"approved", "ready"}):
            errors.append(f"implementation {artifact['id']} requires ready/approved task_packet dependency")
        if kind == "evidence_manifest" and not has_dep(artifact, by_id, "implementation", {"approved", "ready"}):
            errors.append(f"evidence_manifest {artifact['id']} requires ready/approved implementation dependency")

    if policy == "standalone":
        design_artifacts = [item for item in artifacts if item["type"] == "technical_design" and item["status"] not in {"missing", "rejected", "stale"}]
        if len(design_artifacts) != 1:
            errors.append("standalone design requires exactly one active technical_design artifact")
        if design_id and design_id not in by_id:
            errors.append(f"standalone design artifact is missing: {design_id}")
    if policy == "embedded" and design.get("embedded_in") not in plan_ids:
        errors.append(f"embedded design must point to a plan artifact: {design.get('embedded_in')}")

    evidence_ready = any(item["type"] == "evidence_manifest" and item["status"] in READY for item in artifacts)
    implementation_ready = any(item["type"] == "implementation" and item["status"] in READY for item in artifacts)
    requested = manifest["claims"]["requested"]
    if requested != "none":
        if not implementation_ready:
            errors.append(f"{requested} requires ready/approved implementation artifact")
        if not evidence_ready:
            errors.append(f"{requested} requires ready/approved evidence_manifest artifact")
    for signed in manifest["claims"]["validated"]:
        if signed["status"] == "validated" and not evidence_ready:
            errors.append(f"validated claim {signed['claim']} requires ready/approved evidence_manifest artifact")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    args = parser.parse_args()

    errors = validate(Path(args.manifest))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Artifact graph valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Resolve a route_decision.json into a versioned workflow strategy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_json_artifact import load_json, validate_instance


SKILL_DIR = Path(__file__).resolve().parents[1]
ROUTE_SCHEMA = SKILL_DIR / "schemas" / "route-decision.schema.json"
CAPABILITY_SCHEMA = SKILL_DIR / "schemas" / "capability-report.schema.json"
RESOLVED_SCHEMA = SKILL_DIR / "schemas" / "resolved-strategy.schema.json"
STRATEGIES = SKILL_DIR / "references" / "strategies"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_strategy(strategy_id: str) -> dict[str, Any]:
    path = STRATEGIES / f"{strategy_id}.json"
    if not path.exists():
        fail(f"missing strategy registry entry: {strategy_id}")
    return load_json(path)


def available_ids(report: dict[str, Any], key: str) -> list[str]:
    return [item["id"] for item in report[key] if item["status"] == "available"]


def load_capability_report(route: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    ref = route["capability_report_ref"]
    path = Path(ref)
    if not path.is_absolute():
        path = base_dir / path
    if not path.exists():
        fail(f"CAPABILITY_MISSING: capability report not found: {ref}")
    report = load_json(path)
    errors = validate_instance(report, load_json(CAPABILITY_SCHEMA))
    if errors:
        fail("invalid capability report:\n" + "\n".join(errors))
    return report


def choose_spec_system(route: dict[str, Any], report: dict[str, Any]) -> str:
    classification = route["classification"]
    constraints = route["user_constraints"]
    available = available_ids(report, "spec_systems")
    required = constraints["required_spec_system"]
    if required:
        if required == "none" or required in available:
            return required
        fail(f"CAPABILITY_MISSING: required spec system unavailable: {required}")
    if classification["risk"] in {"L0", "L1"} or classification["work_intent"] in {"debug", "review", "research", "verify"}:
        return "none"
    for candidate in ["openspec", "repo_native", "fallback"]:
        if candidate in available:
            return candidate
    return "none"


def choose_execution_engine(route: dict[str, Any], report: dict[str, Any]) -> str:
    mode = route["classification"]["work_intent"]
    risk = route["classification"]["risk"]
    constraints = route["user_constraints"]
    available = available_ids(report, "execution_engines")
    required = constraints["required_execution_engine"]
    if required:
        if required == "none" or required in available:
            return required
        fail(f"CAPABILITY_MISSING: required execution engine unavailable: {required}")
    if mode in {"review", "research", "verify"}:
        return "none"
    if risk == "L0":
        return "local" if "local" in available else "none"
    if "superpowers" in available:
        return "superpowers"
    if "local" in available:
        return "local"
    return "none"


def hard_triggers(route: dict[str, Any]) -> list[str]:
    classification = route["classification"]
    profiles = set(classification["profiles"])
    change_types = set(classification["change_types"])
    triggers: list[str] = []
    if classification["scope"] == "cross_service":
        triggers.append("cross_service_flow")
    elif classification["scope"] == "cross_module":
        triggers.append("cross_module_flow")
    if "api_contract" in change_types:
        triggers.append("public_api")
    if "migration" in change_types:
        triggers.append("migration")
    if "data" in profiles:
        triggers.append("data_model")
    if profiles.intersection({"auth", "security"}):
        triggers.append("auth_permission_security")
    if classification["work_intent"] == "handoff" or profiles.intersection({"release"}):
        triggers.append("external_integration")
    return sorted(set(triggers))


def choose_strategy(route: dict[str, Any]) -> str:
    classification = route["classification"]
    mode = classification["work_intent"]
    risk = classification["risk"]
    change_types = set(classification["change_types"])
    profiles = set(classification["profiles"])
    delivery_shape = classification["delivery_shape"]

    if mode == "review":
        return "review-only"
    if mode == "research" or delivery_shape == "spike":
        return "spike"
    if mode == "debug":
        return "root-cause-debug"
    if "migration" in change_types:
        return "migration-critical"
    if risk == "L0":
        return "quick-change"
    if risk == "L1":
        return "focused-change"
    if risk == "L3":
        return "complex-real-slice"
    if mode == "handoff" or "api_contract" in change_types or profiles.intersection({"release", "auth", "security", "data"}):
        return "complex-real-slice"
    return "spec-driven-feature"


def choose_topology(route: dict[str, Any], strategy: dict[str, Any]) -> str:
    if strategy["design_policy"] != "standalone":
        return "compact"
    classification = route["classification"]
    if classification["scope"] == "cross_service" or classification["delivery_shape"] == "mvp" or "migration" in classification["change_types"]:
        return "split_design_workspace"
    return "single_file_design"


def strategy_gates(strategy: dict[str, Any]) -> dict[str, bool]:
    return {
        "human_design_approval_required": strategy["design_review"] == "human",
        "isolated_review_required": strategy["design_review"] in {"independent", "human"},
        "integration_evidence_required": strategy["max_claim_request"] in {"integration_done", "handoff_done"},
    }


def resolve(route: dict[str, Any], base_dir: Path | None = None) -> dict[str, Any]:
    errors = validate_instance(route, load_json(ROUTE_SCHEMA))
    if errors:
        fail("\n".join(errors))
    if route["ambiguity"]["status"] == "ambiguous":
        reasons = ", ".join(route["ambiguity"]["reasons"]) or "unspecified"
        fail(f"ROUTE_AMBIGUOUS: {reasons}")

    capability_report = load_capability_report(route, base_dir or Path.cwd())
    strategy_id = choose_strategy(route)
    strategy = load_strategy(strategy_id)
    resolved = {
        "schema_version": 1,
        "strategy_id": strategy_id,
        "strategy_version": strategy["version"],
        "spec_system": choose_spec_system(route, capability_report),
        "execution_engine": choose_execution_engine(route, capability_report),
        "required_skills": strategy["required_skills"],
        "design_control": {
            "policy": strategy["design_policy"],
            "review": strategy["design_review"],
            "documentation_topology": choose_topology(route, strategy),
            "triggers": hard_triggers(route),
        },
        "gates": strategy_gates(strategy),
        "capability_report_ref": route["capability_report_ref"],
        "reason": f"{route['classification']['risk']} {route['classification']['work_intent']} resolved by workflow-control-plane",
    }
    resolved_errors = validate_instance(resolved, load_json(RESOLVED_SCHEMA))
    if resolved_errors:
        fail("\n".join(resolved_errors))
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route_decision", help="route_decision.json path")
    parser.add_argument("--output", help="optional resolved_strategy.json path")
    args = parser.parse_args()

    route_path = Path(args.route_decision)
    resolved = resolve(load_json(route_path), route_path.parent)
    text = json.dumps(resolved, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

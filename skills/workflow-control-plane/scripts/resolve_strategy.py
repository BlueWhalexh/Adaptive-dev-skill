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
RESOLVED_SCHEMA = SKILL_DIR / "schemas" / "resolved-strategy.schema.json"
STRATEGIES = SKILL_DIR / "references" / "strategies"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_strategy(strategy_id: str) -> dict[str, Any]:
    path = STRATEGIES / f"{strategy_id}.json"
    if not path.exists():
        fail(f"missing strategy registry entry: {strategy_id}")
    return load_json(path)


def choose_spec_system(route: dict[str, Any]) -> str:
    classification = route["classification"]
    available = route["capabilities"]["spec_systems"]
    if classification["risk"] in {"L0", "L1"} or classification["intent_mode"] in {"debug", "review", "spike"}:
        return "none"
    for candidate in ["openspec", "repo_native", "fallback"]:
        if candidate in available:
            return candidate
    return "none"


def choose_execution_engine(route: dict[str, Any]) -> str:
    mode = route["classification"]["intent_mode"]
    risk = route["classification"]["risk"]
    available = route["capabilities"]["execution_engines"]
    if mode in {"review", "spike"}:
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
    if "migration" in change_types or classification["intent_mode"] == "migration":
        triggers.append("migration")
    if "data" in profiles:
        triggers.append("data_model")
    if profiles.intersection({"auth", "security"}):
        triggers.append("auth_permission_security")
    if profiles.intersection({"delivery", "release"}):
        triggers.append("external_integration")
    return sorted(set(triggers))


def choose_strategy(route: dict[str, Any]) -> str:
    classification = route["classification"]
    mode = classification["intent_mode"]
    risk = classification["risk"]
    change_types = set(classification["change_types"])
    profiles = set(classification["profiles"])

    if mode == "review":
        return "review-only"
    if mode == "spike":
        return "spike"
    if mode == "debug":
        return "root-cause-debug"
    if mode == "migration" or "migration" in change_types:
        return "migration-critical"
    if risk == "L0":
        return "quick-change"
    if risk == "L1":
        return "focused-change"
    if risk == "L3":
        return "complex-real-slice"
    if "api_contract" in change_types or profiles.intersection({"delivery", "release", "auth", "security", "data"}):
        return "complex-real-slice"
    return "spec-driven-feature"


def choose_topology(route: dict[str, Any], strategy: dict[str, Any]) -> str:
    if strategy["design_policy"] != "standalone":
        return "compact"
    classification = route["classification"]
    if classification["scope"] == "cross_service" or classification["delivery_shape"] in {"mvp", "migration"}:
        return "split_design_workspace"
    return "single_file_design"


def resolve(route: dict[str, Any]) -> dict[str, Any]:
    errors = validate_instance(route, load_json(ROUTE_SCHEMA))
    if errors:
        fail("\n".join(errors))
    if route["ambiguity"]["status"] == "ambiguous":
        reasons = ", ".join(route["ambiguity"]["reasons"]) or "unspecified"
        fail(f"ROUTE_AMBIGUOUS: {reasons}")

    strategy_id = choose_strategy(route)
    strategy = load_strategy(strategy_id)
    resolved = {
        "schema_version": 1,
        "strategy_id": strategy_id,
        "strategy_version": strategy["version"],
        "spec_system": choose_spec_system(route),
        "execution_engine": choose_execution_engine(route),
        "required_skills": strategy["required_skills"],
        "design_control": {
            "policy": strategy["design_policy"],
            "review": strategy["design_review"],
            "documentation_topology": choose_topology(route, strategy),
            "triggers": hard_triggers(route),
        },
        "reason": f"{route['classification']['risk']} {route['classification']['intent_mode']} resolved by workflow-control-plane",
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

    resolved = resolve(load_json(Path(args.route_decision)))
    text = json.dumps(resolved, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

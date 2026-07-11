#!/usr/bin/env python3
"""Apply discovered route facts and write a versioned route_decision v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_json_artifact import load_json, validate_instance


SKILL_DIR = Path(__file__).resolve().parents[1]
ROUTE_SCHEMA = SKILL_DIR / "schemas" / "route-decision.schema.json"
DELTA_SCHEMA = SKILL_DIR / "schemas" / "route-facts-delta.schema.json"
RISK_RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
SCOPE_RANK = {"local": 0, "module": 1, "cross_module": 2, "cross_service": 3}
UNCERTAINTY_RANK = {"low": 0, "medium": 1, "high": 2}


def max_by_rank(current: str, candidate: str | None, rank: dict[str, int]) -> str:
    if not candidate:
        return current
    return candidate if rank[candidate] > rank[current] else current


def sorted_unique(values: list[str]) -> list[str]:
    return sorted(set(values))


def apply_delta(route: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    route_errors = validate_instance(route, load_json(ROUTE_SCHEMA))
    delta_errors = validate_instance(delta, load_json(DELTA_SCHEMA))
    if route_errors or delta_errors:
        raise SystemExit("FAIL: " + "; ".join(route_errors + delta_errors))

    facts = delta["discovered_facts"]
    updated = json.loads(json.dumps(route))
    classification = updated["classification"]
    classification["risk"] = max_by_rank(classification["risk"], facts.get("risk_floor"), RISK_RANK)
    classification["scope"] = max_by_rank(classification["scope"], facts.get("scope"), SCOPE_RANK)
    classification["uncertainty"] = max_by_rank(classification["uncertainty"], facts.get("uncertainty"), UNCERTAINTY_RANK)
    if facts.get("pattern_familiarity"):
        classification["pattern_familiarity"] = facts["pattern_familiarity"]
    classification["profiles"] = sorted_unique(classification["profiles"] + facts.get("add_profiles", []))
    classification["change_types"] = sorted_unique(classification["change_types"] + facts.get("add_change_types", []))
    updated["status"] = "provisional"
    updated["user_overrides"] = sorted_unique(updated["user_overrides"] + [f"route_delta:{code}" for code in delta["reason_codes"]])
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route_decision", help="previous route_decision.json")
    parser.add_argument("facts_delta", help="route_facts_delta.json from context-grounding or another narrow skill")
    parser.add_argument("--output", required=True, help="new route_decision.json path")
    args = parser.parse_args()

    updated = apply_delta(load_json(Path(args.route_decision)), load_json(Path(args.facts_delta)))
    errors = validate_instance(updated, load_json(ROUTE_SCHEMA))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    Path(args.output).write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Route decision updated: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

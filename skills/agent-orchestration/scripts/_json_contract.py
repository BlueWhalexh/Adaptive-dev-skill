#!/usr/bin/env python3
"""Small JSON contract helpers for agent orchestration scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "boolean": bool,
    "number": (int, float),
    "null": type(None),
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,120}$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_instance(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        valid = False
        for candidate_type in expected_types:
            expected = TYPE_MAP[candidate_type]
            if candidate_type == "integer":
                valid = isinstance(value, int) and not isinstance(value, bool)
            elif candidate_type == "number":
                valid = isinstance(value, expected) and not isinstance(value, bool)
            else:
                valid = isinstance(value, expected)
            if valid:
                break
        if not valid:
            return [f"{path}: expected {expected_type}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: invalid value {value!r}; expected one of {schema['enum']}"]

    if expected_type == "object":
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in sorted(set(value) - set(properties)):
                errors.append(f"{path}: unexpected property {key!r}")
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_instance(value[key], child_schema, f"{path}.{key}"))

    if expected_type == "array":
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))

    return errors


def safe_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_safe_common(value: Any) -> list[str]:
    errors: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                if key.endswith("_id") and isinstance(child, str) and not SAFE_ID.match(child):
                    errors.append(f"{path}.{key}: unsafe id {child!r}")
                if key.endswith("_path") or key == "path" or key.endswith("_ref"):
                    if isinstance(child, str) and child and not safe_path(child):
                        errors.append(f"{path}.{key}: path/ref must be relative and stay inside repo: {child!r}")
                walk(child, f"{path}.{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{path}[{index}]")

    walk(value, "$")
    return errors


def validate_contract(value: dict[str, Any], schema_path: Path) -> list[str]:
    return validate_instance(value, load_json(schema_path)) + validate_safe_common(value)

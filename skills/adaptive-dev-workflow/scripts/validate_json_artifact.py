#!/usr/bin/env python3
"""Validate a JSON artifact with the skill's small JSON Schema subset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    pass


TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "boolean": bool,
    "number": (int, float),
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def validate_instance(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type:
        expected = TYPE_MAP[expected_type]
        if expected_type == "integer":
            valid = isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "number":
            valid = isinstance(value, expected) and not isinstance(value, bool)
        else:
            valid = isinstance(value, expected)
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
            extra = sorted(set(value) - set(properties))
            for key in extra:
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


def validate(schema_path: Path, artifact_path: Path) -> list[str]:
    schema = load_json(schema_path)
    artifact = load_json(artifact_path)
    return validate_instance(artifact, schema)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", help="JSON schema path")
    parser.add_argument("artifact", help="JSON artifact path")
    args = parser.parse_args()

    errors = validate(Path(args.schema), Path(args.artifact))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"JSON artifact valid: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

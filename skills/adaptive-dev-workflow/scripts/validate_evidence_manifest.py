#!/usr/bin/env python3
"""Validate that an evidence manifest contains the minimum handoff fields."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_TOKENS = {
    "commit": "commit or version evidence",
    "acceptance": "acceptance criteria mapping",
    "validator": "validator command or method",
    "result": "validator result",
    "gap": "known gaps or unproven scope",
    "claim": "claim ceiling",
}

REALITY_LABELS = ("unit", "mock", "fake", "integration", "e2e", "real external", "fresh consumer", "manual")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Path to evidence.md or evidence manifest")
    args = parser.parse_args()

    path = Path(args.manifest)
    if not path.exists():
        raise SystemExit(f"missing evidence manifest: {path}")

    text = path.read_text(encoding="utf-8").lower()
    missing = [label for token, label in REQUIRED_TOKENS.items() if token not in text]
    has_reality_label = any(label in text for label in REALITY_LABELS)

    if missing or not has_reality_label:
        if missing:
            print("missing:")
            for item in missing:
                print(f"- {item}")
        if not has_reality_label:
            print("missing:")
            print("- evidence reality label: unit/mock/fake/integration/e2e/real external/fresh consumer/manual")
        return 1

    print(f"ok: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

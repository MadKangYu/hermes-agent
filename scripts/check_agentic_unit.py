#!/usr/bin/env python3
"""Validate Hermes agentic engineering unit records in markdown files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = (
    "unit_id",
    "surface",
    "goal",
    "current_state",
    "authority_boundary",
    "verification_criteria",
    "log_location",
    "completion_condition",
    "contract_category",
    "status",
)

VALID_STATUSES = {"planned", "working", "blocked", "verified", "closed"}
VALID_SURFACES = {
    "acp",
    "cli",
    "core",
    "cron",
    "docs",
    "gateway",
    "kanban",
    "platform",
    "plugin",
    "profile",
    "skill",
    "test",
    "tui",
    "website",
}
VALID_CONTRACT_CATEGORIES = {
    "api-contract",
    "auth-contract",
    "data-contract",
    "integration-contract",
    "runtime-contract",
    "state-contract",
    "ui-contract",
}

FIELD_RE = re.compile(r"^([a-z_]+):\s*(.*)$")
UNIT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line.strip())
        if not match:
            continue
        key, value = match.groups()
        if key in REQUIRED_FIELDS and key not in fields:
            fields[key] = value.strip()
    return fields


def validate_text(text: str) -> list[str]:
    fields = parse_fields(text)
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"missing required field: {field}")
        elif not fields[field]:
            errors.append(f"empty required field: {field}")

    status = fields.get("status")
    if status and status not in VALID_STATUSES:
        valid = ", ".join(sorted(VALID_STATUSES))
        errors.append(f"invalid status: {status} (expected one of: {valid})")

    surface = fields.get("surface")
    if surface and surface not in VALID_SURFACES:
        valid = ", ".join(sorted(VALID_SURFACES))
        errors.append(f"invalid surface: {surface} (expected one of: {valid})")

    category = fields.get("contract_category")
    if category and category not in VALID_CONTRACT_CATEGORIES:
        valid = ", ".join(sorted(VALID_CONTRACT_CATEGORIES))
        errors.append(
            f"invalid contract_category: {category} (expected one of: {valid})"
        )

    unit_id = fields.get("unit_id")
    if unit_id and not UNIT_ID_RE.fullmatch(unit_id):
        errors.append(
            "invalid unit_id: use lowercase ASCII letters, digits, and hyphens"
        )

    return errors


def validate_file(path: Path) -> list[str]:
    if not path.exists():
        return [f"file does not exist: {path}"]
    if not path.is_file():
        return [f"not a file: {path}"]
    return validate_text(path.read_text(encoding="utf-8"))


def discover_unit_files(paths: list[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in paths:
        candidates = sorted(path.rglob("*.md")) if path.is_dir() else [path]
        for candidate in candidates:
            if not candidate.is_file():
                continue
            text = candidate.read_text(encoding="utf-8")
            if re.search(r"^unit_id:[ \t]*\S+", text, flags=re.MULTILINE):
                discovered.append(candidate)
    return discovered


def missing_paths(paths: list[Path]) -> list[Path]:
    return [path for path in paths if not path.exists()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Hermes agentic engineering unit markdown records."
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="treat paths as files or directories and validate markdown files that contain a unit_id",
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)

    missing = missing_paths(args.paths)
    if missing:
        for path in missing:
            print(f"FAIL {path}", file=sys.stderr)
            print(f"  - path does not exist", file=sys.stderr)
        return 1

    paths = discover_unit_files(args.paths) if args.discover else args.paths
    if not paths:
        print("PASS no agentic unit records found")
        return 0

    failed = False
    for path in paths:
        errors = validate_file(path)
        if not errors:
            print(f"PASS {path}")
            continue

        failed = True
        print(f"FAIL {path}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

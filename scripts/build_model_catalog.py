#!/usr/bin/env python3
"""Build the Hermes Model Catalog — a centralized JSON manifest of curated models.

This script reads the in-repo hardcoded curated lists (``OPENROUTER_MODELS``,
``_PROVIDER_MODELS["nous"]``) and writes them to a JSON manifest that the
Hermes CLI fetches at runtime. Publishing the catalog through the docs site
lets maintainers update model lists without shipping a Hermes release.

The runtime fetcher falls back to the same in-repo hardcoded lists if the
manifest is unreachable, so this script is a convenience for keeping the
manifest in sync — not a source of truth.

Usage::

    python scripts/build_model_catalog.py

Output: ``website/static/api/model-catalog.json``

Live URL (after ``deploy-site.yml`` runs on merge to main):
``https://hermes-agent.nousresearch.com/docs/api/model-catalog.json``
"""

from __future__ import annotations

import json
import os
import sys
from argparse import ArgumentParser
from datetime import datetime, timezone
from typing import Any, Sequence

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

# Ensure HERMES_HOME is set for imports that touch it at module level.
os.environ.setdefault("HERMES_HOME", os.path.join(os.path.expanduser("~"), ".hermes"))

from hermes_cli.models import OPENROUTER_MODELS, _PROVIDER_MODELS  # noqa: E402

OUTPUT_PATH = os.path.join(REPO_ROOT, "website", "static", "api", "model-catalog.json")
CATALOG_VERSION = 1


def build_catalog() -> dict:
    return {
        "version": CATALOG_VERSION,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metadata": {
            "source": "hermes-agent repo",
            "docs": "https://hermes-agent.nousresearch.com/docs/reference/model-catalog",
        },
        "providers": {
            "openrouter": {
                "metadata": {
                    "display_name": "OpenRouter",
                    "note": (
                        "Descriptions drive picker badges. Live /api/v1/models "
                        "filters curated ids by tool-calling support and free pricing."
                    ),
                },
                "models": [
                    {"id": mid, "description": desc}
                    for mid, desc in OPENROUTER_MODELS
                ],
            },
            "nous": {
                "metadata": {
                    "display_name": "Nous Portal",
                    "note": (
                        "Free-tier gating is determined live via Portal pricing "
                        "(partition_nous_models_by_tier), not this manifest."
                    ),
                },
                "models": [
                    {"id": mid}
                    for mid in _PROVIDER_MODELS.get("nous", [])
                ],
            },
        },
    }


def _normalise_for_check(catalog: dict[str, Any]) -> dict[str, Any]:
    """Return a copy suitable for drift checks.

    ``updated_at`` is intentionally generated at write time, so check mode
    compares the provider/model payload and metadata without treating the
    timestamp as drift.
    """
    normalized = json.loads(json.dumps(catalog, sort_keys=True))
    normalized.pop("updated_at", None)
    return normalized


def write_catalog() -> int:
    catalog = build_catalog()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, indent=2)
        fh.write("\n")

    print(f"Wrote {OUTPUT_PATH}")
    for provider, block in catalog["providers"].items():
        print(f"  {provider}: {len(block['models'])} models")
    return 0


def check_catalog() -> int:
    expected = build_catalog()
    try:
        with open(OUTPUT_PATH, encoding="utf-8") as fh:
            current = json.load(fh)
    except FileNotFoundError:
        print(
            f"{OUTPUT_PATH} is missing; run python scripts/build_model_catalog.py",
            file=sys.stderr,
        )
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{OUTPUT_PATH} is unreadable: {exc}", file=sys.stderr)
        return 1

    if _normalise_for_check(current) != _normalise_for_check(expected):
        print(
            f"{OUTPUT_PATH} is stale; run python scripts/build_model_catalog.py",
            file=sys.stderr,
        )
        return 1

    print(f"{OUTPUT_PATH} is up to date")
    for provider, block in expected["providers"].items():
        print(f"  {provider}: {len(block['models'])} models")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the checked-in catalog matches the curated model lists without rewriting it",
    )
    args = parser.parse_args(argv)
    if args.check:
        return check_catalog()
    return write_catalog()


if __name__ == "__main__":
    sys.exit(main())

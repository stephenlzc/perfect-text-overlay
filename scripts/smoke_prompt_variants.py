#!/usr/bin/env python3
"""Smoke test for the P0-4 base-image prompt diversification module.

Verifies ``prompt_variants`` without a test framework:

1. descriptor resolution (exact / unique prefix / ambiguous / unknown)
2. ``build_variants`` returns ``count`` distinct, seed-reproducible prompts
3. explicit dimension overrides are honoured
4. unknown descriptors raise ``ValueError``

Usage::

    .venv/bin/python scripts/smoke_prompt_variants.py
"""

from __future__ import annotations

import os
import sys

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from prompt_variants import build_variants, list_dimensions, resolve_descriptor


def _check(condition: bool, message: str) -> None:
    print(f"  {'PASS' if condition else 'FAIL'}: {message}")
    if not condition:
        raise SystemExit(1)


def main() -> None:
    print("== descriptor resolution ==")
    _check(resolve_descriptor("style", "watercolor") == "watercolor painting", "prefix -> canonical")
    _check(resolve_descriptor("style", "watercolor painting") == "watercolor painting", "exact match")
    _check(resolve_descriptor("palette", "soft pastel palette") == "soft pastel palette", "exact palette")
    _check(resolve_descriptor("style", "bogus") is None, "unknown -> None")

    print("== build_variants ==")
    base = "minimal product shot of a ceramic mug"
    variants = build_variants(base, count=4, seed=7)
    _check(len(variants) == 4, f"count=4 -> {len(variants)}")
    _check(len(set(variants)) == 4, "all variants distinct")
    _check(all(v.startswith(base + ",") for v in variants), "variants extend the base prompt")

    again = build_variants(base, count=4, seed=7)
    _check(variants == again, "seed-reproducible")

    overridden = build_variants(base, count=1, seed=1, style="watercolor", palette="soft pastel")
    _check("watercolor painting" in overridden[0], "style override honoured")
    _check("soft pastel palette" in overridden[0], "palette override honoured")

    try:
        build_variants(base, count=1, style="not-a-real-style")
        _check(False, "unknown descriptor should raise")
    except ValueError:
        _check(True, "unknown descriptor raises ValueError")

    print("\nAll prompt-variant smoke tests passed.")


if __name__ == "__main__":
    main()

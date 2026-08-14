#!/usr/bin/env python3
"""Base-image prompt diversification (P0-4).

A preset ships a single fixed ``base_image_prompt``, which makes every run
produce the same base image.  This module provides a curated **style lexicon**
across five dimensions (art style, mood/lighting, colour palette, material,
composition) and :func:`build_variants`, which derives N distinct image prompts
from one base prompt by appending chosen descriptors.

Used by ``gen_ecommerce.py prompt``.  The descriptors are plain English keyword
phrases, so they can be pasted straight into Midjourney / GPT Image 2 /
Stable Diffusion / Gemini etc.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

# The five variation dimensions, in prompt order.
DIMENSIONS = ("style", "mood", "palette", "material", "composition")

STYLE_LEXICON: Dict[str, List[str]] = {
    "style": [
        "photorealistic product photography",
        "flat vector illustration",
        "minimalist line art",
        "soft 3D render",
        "isometric illustration",
        "cinematic photograph",
        "watercolor painting",
        "editorial magazine style",
        "neon-noir digital art",
        "hand-drawn sketch",
        "low-poly 3D render",
        "retro vintage poster",
    ],
    "mood": [
        "soft morning sunlight",
        "golden hour glow",
        "dramatic rim lighting",
        "moody chiaroscuro lighting",
        "bright airy daylight",
        "neon glow accents",
        "overcast diffused light",
        "warm cozy candlelight",
        "cool moonlight",
        "studio softbox lighting",
    ],
    "palette": [
        "warm earth tones",
        "cool navy and teal gradient",
        "soft pastel palette",
        "monochrome black and white",
        "vibrant saturated palette",
        "muted sage green and cream",
        "black and gold luxury palette",
        "dusty rose and terracotta",
        "icy blue and silver",
        "sunset orange and purple",
    ],
    "material": [
        "matte finish",
        "glossy reflective surface",
        "brushed metal",
        "ceramic and glass",
        "natural linen fabric",
        "rustic wood grain",
        "smooth marble surface",
        "soft paper texture",
        "frosted glass",
        "leather and brass",
    ],
    "composition": [
        "centered symmetrical composition",
        "rule-of-thirds layout",
        "generous negative space",
        "flat-lay top-down view",
        "diagonal dynamic composition",
        "floating elements arrangement",
        "close-up macro framing",
        "wide cinematic framing",
    ],
}


def list_dimensions() -> Dict[str, List[str]]:
    """Return a shallow copy of the style lexicon."""
    return {dim: list(entries) for dim, entries in STYLE_LEXICON.items()}


def resolve_descriptor(dimension: str, value: str) -> Optional[str]:
    """Resolve a user-supplied descriptor to its canonical lexicon entry.

    Matching is case-insensitive and accepts either the full phrase or a prefix
    that identifies exactly one entry (``watercolor`` -> ``watercolor painting``).
    Returns ``None`` when unknown or ambiguous.
    """
    entries = STYLE_LEXICON.get(dimension, [])
    if not entries:
        return None
    v = (value or "").strip().lower()
    if v in ("", "random", "auto"):
        return None
    exact = [e for e in entries if e.lower() == v]
    if exact:
        return exact[0]
    prefix = [e for e in entries if e.lower().startswith(v)]
    if len(prefix) == 1:
        return prefix[0]
    return None


def build_variants(
    base_prompt: str,
    count: int = 1,
    seed: Optional[int] = None,
    style: Optional[str] = None,
    mood: Optional[str] = None,
    palette: Optional[str] = None,
    material: Optional[str] = None,
    composition: Optional[str] = None,
) -> List[str]:
    """Return ``count`` distinct variant prompts derived from ``base_prompt``.

    Dimension overrides:

    * ``None`` / ``"auto"`` — random pick, preferring descriptors that are not
      already present in the base prompt (dedup).
    * ``"random"`` — force a random pick (ignoring dedup).
    * any other string — resolved via :func:`resolve_descriptor`; an unknown or
      ambiguous value raises :class:`ValueError`.

    Each variant is ``base_prompt + ", " + style + ", " + mood + ", " + palette
    + ", " + material + ", " + composition``.
    """
    count = max(1, int(count))
    overrides = {
        "style": style,
        "mood": mood,
        "palette": palette,
        "material": material,
        "composition": composition,
    }
    resolved: Dict[str, Optional[str]] = {}
    for dim in DIMENSIONS:
        raw = overrides[dim]
        if raw is None or str(raw).strip().lower() in ("", "auto"):
            resolved[dim] = None
        elif str(raw).strip().lower() == "random":
            resolved[dim] = "__random__"
        else:
            canonical = resolve_descriptor(dim, str(raw))
            if canonical is None:
                raise ValueError(
                    f"unknown {dim} descriptor {raw!r}; use --list to see options"
                )
            resolved[dim] = canonical

    base = (base_prompt or "").rstrip(" ,.;:")
    rng = random.Random(seed)
    variants: List[str] = []
    seen = {base}
    max_attempts = max(count * 60, 120)
    for _ in range(max_attempts):
        if len(variants) >= count:
            break
        chosen: List[str] = []
        for dim in DIMENSIONS:
            spec = resolved[dim]
            entries = STYLE_LEXICON[dim]
            if spec == "__random__":
                pick = rng.choice(entries)
            elif spec is not None:
                pick = spec
            else:
                lowered_base = base.lower()
                candidates = [e for e in entries if e.lower() not in lowered_base]
                pool = candidates or entries
                pick = rng.choice(pool)
            chosen.append(pick)
        prompt = ", ".join([base] + chosen) if base else ", ".join(chosen)
        if prompt not in seen:
            seen.add(prompt)
            variants.append(prompt)
    return variants


__all__ = ["DIMENSIONS", "STYLE_LEXICON", "list_dimensions", "resolve_descriptor", "build_variants"]

#!/usr/bin/env python3
"""Smoke test for the P0-1 font-weight hierarchy and P0-2 parameterised effects.

Verifies, without a test framework:

1. ``resolve_font_path`` maps ``(language, font_weight)`` to the expected file
   and falls back to Bold when a weight is unavailable.
2. A config using ``gradient`` + soft ``shadow`` + parameterised
   ``backdrop``/``glow`` renders to a non-trivial PNG of the expected size.

Usage::

    .venv/bin/python scripts/smoke_fonts_effects.py
"""

from __future__ import annotations

import os
import sys
import tempfile

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from PIL import Image

from config_loader import TemplateConfig, TextLayerConfig
from font_registry import resolve_font_path
from text_renderer import render_layers_pil


def _check(condition: bool, message: str) -> None:
    print(f"  {'PASS' if condition else 'FAIL'}: {message}")
    if not condition:
        raise SystemExit(1)


def test_font_resolution() -> None:
    print("== font resolution ==")
    cases = [
        ("en", "black", "Roboto-Black.ttf"),
        ("en", "regular", "Roboto-Regular.ttf"),
        ("zh-CN", "black", "NotoSansCJKsc-Black.otf"),
        ("zh-CN", "regular", "NotoSansCJKsc-Regular.otf"),
        ("zh-TW", "black", "NotoSansCJKtc-Black.otf"),
        ("ko", "black", "NotoSansCJKkr-Black.otf"),
        # medium not downloaded for CJK -> graceful fallback to Bold.
        ("ko", "medium", "NotoSansCJKkr-Bold.otf"),
    ]
    for lang, weight, expected in cases:
        layer = TextLayerConfig(
            name="t", type="text", default_font="Roboto-Bold.ttf",
            max_width=500, anchor="top-center", x=0, y=0, font_size=50,
            font_weight=weight,
        )
        path = resolve_font_path(lang, layer)
        _check(os.path.basename(path) == expected, f"{lang}/{weight} -> {os.path.basename(path)}")


def test_effects_render() -> None:
    print("== gradient + soft shadow + parameterised effects render ==")
    w, h = 800, 600
    with tempfile.TemporaryDirectory() as tmp:
        base_path = os.path.join(tmp, "base.png")
        out_path = os.path.join(tmp, "out.png")

        # Synthetic base: a mid-gray canvas.
        Image.new("RGB", (w, h), (120, 120, 130)).save(base_path)

        layers = [
            TextLayerConfig(
                name="title", type="text", default_font="Roboto-Bold.ttf",
                max_width=600, max_lines=1, effects=["gradient", "shadow"],
                anchor="center", x=400, y=240, color="#FFFFFF", font_size=80,
                font_weight="black",
                gradient_from="#FFD700", gradient_to="#FF4500", gradient_angle=90,
                shadow_blur=10, shadow_color="#000000", shadow_opacity=180,
            ),
            TextLayerConfig(
                name="badge", type="badge", default_font="Roboto-Bold.ttf",
                max_width=320, max_lines=1, effects=["backdrop", "outline", "glow"],
                anchor="center", x=400, y=420, color="#FFFFFF", font_size=40,
                backdrop_color="#1a1a1a", backdrop_opacity=140, backdrop_radius=24,
                glow_color="#00ffff", glow_radius=16, glow_strength=2,
                stroke_color="#000000", stroke_width=2,
            ),
        ]
        cfg = TemplateConfig(
            name="smoke", scene_type="banner", canvas_width=w, canvas_height=h,
            base_image_prompt="x", translations_file="translations/en.json",
            text_layers=layers,
        )
        variables = {"title": "Gradient Title", "badge": "BADGE"}

        render_layers_pil(
            base_path,
            cfg,
            variables,
            "en",
            font_resolver=lambda lang, layer: resolve_font_path(lang, layer),
            output_path=out_path,
            smart_layout=False,
        )

        _check(os.path.exists(out_path), "output written")
        out = Image.open(out_path).convert("RGB")
        _check(out.size == (w, h), f"size {out.size} == ({w},{h})")

        # The render must differ from the plain base (text was drawn).
        import numpy as np

        base_arr = np.asarray(Image.open(base_path).convert("RGB"))
        out_arr = np.asarray(out)
        diff = int(
            (np.abs(base_arr.astype(int) - out_arr.astype(int)).sum(axis=2) > 24).sum()
        )
        _check(diff > 500, f"rendered text changed {diff} px vs base")


def main() -> None:
    test_font_resolution()
    test_effects_render()
    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()

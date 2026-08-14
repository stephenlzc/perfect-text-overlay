#!/usr/bin/env python3
"""Smoke test for the P1-5 design-token / theme system.

Verifies ``theme_engine`` without a test framework:

1. template tokens resolve ``$name`` references in text layers
2. a built-in theme overrides the standard token names
3. unknown tokens / unknown themes raise ``ConfigError``
4. two different themes render visibly different images
5. the built-in theme registry contains the expected themes

Usage::

    .venv/bin/python scripts/smoke_themes.py
"""

from __future__ import annotations

import os
import sys
import tempfile

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from PIL import Image, ImageDraw

from config_loader import ConfigError, TemplateConfig, TextLayerConfig
from font_registry import resolve_font_path
from text_renderer import render_layers_pil
from theme_engine import THEMES, list_themes, resolve_theme


def _check(condition: bool, message: str) -> None:
    print(f"  {'PASS' if condition else 'FAIL'}: {message}")
    if not condition:
        raise SystemExit(1)


def _make_config() -> TemplateConfig:
    return TemplateConfig(
        name="smoke_theme",
        scene_type="banner",
        canvas_width=800,
        canvas_height=500,
        base_image_prompt="x",
        translations_file="translations/en.json",
        theme={
            "tokens": {
                "color_heading": "#123456",
                "color_badge_text": "#FFFFFF",
                "color_badge_bg": "#333333",
                "weight_heading": "bold",
                "effect_heading": ["shadow"],
                "effect_badge": ["backdrop"],
            }
        },
        text_layers=[
            TextLayerConfig(
                name="title", type="text", default_font="Roboto-Bold.ttf",
                max_width=600, max_lines=1, effects="$effect_heading",
                anchor="center", x=400, y=150, color="$color_heading",
                font_size=70, font_weight="$weight_heading",
            ),
            TextLayerConfig(
                name="badge", type="badge", default_font="Roboto-Bold.ttf",
                max_width=300, max_lines=1, effects="$effect_badge",
                anchor="center", x=400, y=350, color="$color_badge_text",
                font_size=40, backdrop_color="$color_badge_bg",
            ),
        ],
    )


def _render_to_bytes(cfg: TemplateConfig) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "base.png")
        out = os.path.join(tmp, "out.png")
        img = Image.new("RGB", (cfg.canvas_width, cfg.canvas_height), (90, 90, 100))
        ImageDraw.Draw(img)
        img.save(base)
        render_layers_pil(
            base, cfg, {"title": "Theme Test", "badge": "PILL"},
            "en", font_resolver=lambda lang, layer: resolve_font_path(lang, layer),
            output_path=out, smart_layout=False,
        )
        with open(out, "rb") as fh:
            return fh.read()


def main() -> None:
    print("== registry ==")
    _check(set(list_themes()) == {"minimal", "luxury", "vibrant", "editorial", "tech", "neon", "handmade"}, "7 built-in themes")

    print("== template token resolution ==")
    resolved = resolve_theme(_make_config())
    title = next(l for l in resolved.text_layers if l.name == "title")
    badge = next(l for l in resolved.text_layers if l.name == "badge")
    _check(title.color == "#123456", "color token resolved")
    _check(title.effects == ["shadow"], "effects token resolved")
    _check(title.font_weight == "bold", "font_weight token resolved")
    _check(badge.backdrop_color == "#333333", "backdrop token resolved")

    print("== built-in theme override ==")
    neon = resolve_theme(_make_config(), "neon")
    neon_title = next(l for l in neon.text_layers if l.name == "title")
    _check(neon_title.color == THEMES["neon"]["color_heading"], "theme overrides color_heading")
    _check(neon_title.font_weight == THEMES["neon"]["weight_heading"], "theme overrides weight_heading")

    print("== error handling ==")
    broken = _make_config()
    broken.text_layers[0] = broken.text_layers[0].model_copy(update={"color": "$missing_token"})
    try:
        resolve_theme(broken)
        _check(False, "unknown token should raise")
    except ConfigError:
        _check(True, "unknown token raises ConfigError")
    try:
        resolve_theme(_make_config(), "bogus")
        _check(False, "unknown theme should raise")
    except ConfigError:
        _check(True, "unknown theme raises ConfigError")

    print("== themes change the rendered output ==")
    default_bytes = _render_to_bytes(resolve_theme(_make_config()))
    neon_bytes = _render_to_bytes(resolve_theme(_make_config(), "neon"))
    _check(default_bytes != neon_bytes, "different themes render different pixels")

    print("\nAll theme smoke tests passed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Design tokens / theme system (P1-5).

Templates centralise their look in a ``theme.tokens`` block (see
:class:`config_loader.ThemeConfig`) and text layers reference tokens instead of
hardcoding values, e.g. ``color: "$color_heading"`` or
``effects: "$effect_heading"``.  Built-in named themes (``minimal``, ``luxury``,
``vibrant``, ``editorial``, ``tech``, ``neon``, ``handmade``) bundle token
overrides so one CLI flag re-styles the whole template.

:func:`resolve_theme` merges template tokens with the selected built-in theme
(in that precedence order) and returns a copy of the config whose layers have
every ``$name`` reference resolved.  Unknown tokens raise
:class:`config_loader.ConfigError` with a readable message.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

try:
    from config_loader import ConfigError, TemplateConfig, TextLayerConfig
except ImportError:  # pragma: no cover - exercised when imported differently
    _SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
    if _SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, _SCRIPTS_DIR)
    from config_loader import ConfigError, TemplateConfig, TextLayerConfig  # noqa: E402


# Fields whose values may reference tokens via a leading "$".
TOKEN_FIELDS = (
    "color",
    "font_weight",
    "backdrop_color",
    "stroke_color",
    "glow_color",
    "shadow_color",
    "gradient_from",
    "gradient_to",
    "effects",
)

# Standard token vocabulary used by the built-in themes.  Presets may define
# additional preset-specific tokens (e.g. ``color_note``) that themes ignore.
THEMES: Dict[str, Dict[str, Any]] = {
    "minimal": {
        "color_heading": "#111111",
        "color_subheading": "#333333",
        "color_body": "#444444",
        "color_accent": "#111111",
        "color_accent_bg": "#EEEEEE",
        "color_accent_stroke": "#333333",
        "color_badge_text": "#FFFFFF",
        "color_badge_bg": "#111111",
        "weight_heading": "black",
        "weight_body": "regular",
        "effect_heading": ["shadow"],
        "effect_body": ["shadow"],
        "effect_price": ["shadow", "backdrop"],
        "effect_badge": ["shadow", "backdrop"],
    },
    "luxury": {
        "color_heading": "#1A1A1A",
        "color_heading_glow": "#D4AF37",
        "color_subheading": "#4A3B2C",
        "color_body": "#6B5D4F",
        "color_accent": "#B8860B",
        "color_accent_bg": "#F7EFDF",
        "color_accent_stroke": "#8B6914",
        "color_accent_glow": "#D4AF37",
        "color_badge_text": "#F5E7C8",
        "color_badge_bg": "#1A1A1A",
        "color_badge_glow": "#D4AF37",
        "weight_heading": "black",
        "effect_heading": ["shadow", "gradient"],
        "gradient_from": "#F7E7B0",
        "gradient_to": "#B8860B",
        "effect_body": ["shadow"],
        "effect_price": ["backdrop", "outline"],
        "effect_badge": ["backdrop", "glow", "shadow"],
    },
    "vibrant": {
        "color_heading": "#FF3D00",
        "color_heading_glow": "#FFD600",
        "color_subheading": "#7A1FA2",
        "color_body": "#3D3D3D",
        "color_accent": "#FFD600",
        "color_accent_bg": "#FF3D00",
        "color_accent_stroke": "#B32700",
        "color_accent_glow": "#FF8A00",
        "color_badge_text": "#FFFFFF",
        "color_badge_bg": "#FF3D00",
        "color_badge_glow": "#FF8A00",
        "weight_heading": "black",
        "effect_heading": ["gradient", "shadow"],
        "gradient_from": "#FFD600",
        "gradient_to": "#FF3D00",
        "effect_body": ["shadow"],
        "effect_price": ["shadow", "backdrop"],
        "effect_badge": ["backdrop", "glow", "shadow"],
    },
    "editorial": {
        "color_heading": "#0F0F0F",
        "color_subheading": "#3D3D3D",
        "color_body": "#555555",
        "color_accent": "#C41E3A",
        "color_accent_bg": "#F5F5F5",
        "color_accent_stroke": "#8F1428",
        "color_accent_glow": "#C41E3A",
        "color_badge_text": "#FFFFFF",
        "color_badge_bg": "#0F0F0F",
        "weight_heading": "black",
        "weight_body": "regular",
        "effect_heading": ["shadow", "outline"],
        "effect_body": [],
        "effect_price": ["outline", "shadow"],
        "effect_badge": ["backdrop", "shadow"],
    },
    "tech": {
        "color_heading": "#0EA5E9",
        "color_heading_glow": "#0EA5E9",
        "color_subheading": "#7DD3FC",
        "color_body": "#94A3B8",
        "color_accent": "#22D3EE",
        "color_accent_bg": "#0F172A",
        "color_accent_stroke": "#0EA5E9",
        "color_accent_glow": "#22D3EE",
        "color_badge_text": "#E0F2FE",
        "color_badge_bg": "#0F172A",
        "color_badge_glow": "#22D3EE",
        "weight_heading": "black",
        "effect_heading": ["shadow", "glow"],
        "effect_body": ["shadow"],
        "effect_price": ["backdrop", "glow"],
        "effect_badge": ["backdrop", "glow", "shadow"],
    },
    "neon": {
        "color_heading": "#F0ABFC",
        "color_heading_glow": "#67E8F9",
        "color_subheading": "#FDE68A",
        "color_body": "#A1A1AA",
        "color_accent": "#67E8F9",
        "color_accent_bg": "#18181B",
        "color_accent_stroke": "#F0ABFC",
        "color_accent_glow": "#67E8F9",
        "color_badge_text": "#F0ABFC",
        "color_badge_bg": "#18181B",
        "color_badge_glow": "#67E8F9",
        "weight_heading": "black",
        "effect_heading": ["glow", "shadow"],
        "effect_body": ["shadow"],
        "effect_price": ["glow", "backdrop"],
        "effect_badge": ["backdrop", "glow", "shadow"],
    },
    "handmade": {
        "color_heading": "#7C2D12",
        "color_subheading": "#57534E",
        "color_body": "#57534E",
        "color_accent": "#B45309",
        "color_accent_bg": "#FFF7ED",
        "color_accent_stroke": "#92400E",
        "color_accent_glow": "#F59E0B",
        "color_badge_text": "#7C2D12",
        "color_badge_bg": "#FFF7ED",
        "color_badge_glow": "#F59E0B",
        "weight_heading": "bold",
        "effect_heading": ["shadow"],
        "effect_body": ["shadow"],
        "effect_price": ["shadow", "backdrop"],
        "effect_badge": ["shadow", "backdrop"],
    },
}


def list_themes() -> List[str]:
    """Return the names of the built-in themes, sorted."""
    return sorted(THEMES)


def get_theme(name: str) -> Optional[Dict[str, Any]]:
    """Return a built-in theme's token overrides, or ``None`` if unknown."""
    return THEMES.get(name or "")


def _resolve_field_value(value: Any, tokens: Dict[str, Any], layer_name: str, field: str) -> Any:
    """Resolve ``$token`` references inside one field value."""
    if isinstance(value, str) and value.startswith("$"):
        key = value[1:]
        if key not in tokens:
            raise ConfigError(f"text layer {layer_name!r}: unknown theme token ${key}")
        resolved = tokens[key]
        if field == "effects":
            if isinstance(resolved, (list, tuple)):
                return [str(item) for item in resolved]
            return [str(resolved)]
        if not isinstance(resolved, str):
            raise ConfigError(
                f"text layer {layer_name!r}: theme token ${key} must be a string "
                f"for field {field!r}"
            )
        return resolved
    if isinstance(value, (list, tuple)) and field == "effects":
        out: List[Any] = []
        for item in value:
            if isinstance(item, str) and item.startswith("$"):
                key = item[1:]
                if key not in tokens:
                    raise ConfigError(f"text layer {layer_name!r}: unknown theme token ${key}")
                resolved = tokens[key]
                if isinstance(resolved, (list, tuple)):
                    out.extend(str(entry) for entry in resolved)
                else:
                    out.append(str(resolved))
            else:
                out.append(item)
        return out
    return value


def _resolve_layer(layer: TextLayerConfig, tokens: Dict[str, Any]) -> TextLayerConfig:
    update: Dict[str, Any] = {}
    for field in TOKEN_FIELDS:
        value = getattr(layer, field, None)
        if value is None:
            continue
        resolved = _resolve_field_value(value, tokens, layer.name, field)
        if resolved != value:
            update[field] = resolved
    if not update:
        return layer
    return layer.model_copy(update=update)


def resolve_theme(config: TemplateConfig, theme_name: Optional[str] = None) -> TemplateConfig:
    """Return a copy of ``config`` with every ``$token`` reference resolved.

    Token precedence: template ``theme.tokens`` first, then the built-in theme
    named by ``theme_name`` (when given).  Raises :class:`ConfigError` on
    unknown tokens or an unknown theme name.
    """
    tokens: Dict[str, Any] = {}
    if config.theme is not None:
        tokens.update(config.theme.tokens or {})
    if theme_name:
        builtin = get_theme(theme_name)
        if builtin is None:
            raise ConfigError(
                f"unknown theme {theme_name!r}; available: {', '.join(list_themes())}"
            )
        tokens.update(builtin)
    resolved_layers = [_resolve_layer(layer, tokens) for layer in config.text_layers]
    return config.model_copy(update={"text_layers": resolved_layers})


__all__ = [
    "TOKEN_FIELDS",
    "THEMES",
    "list_themes",
    "get_theme",
    "resolve_theme",
]

#!/usr/bin/env python3
"""Configuration Loader Module for GenImageText.

Loads and validates template configuration files describing text overlay
templates. Supports YAML (``.yaml``/``.yml``) and JSON (``.json``) and uses
Pydantic 2.x for schema validation. :func:`load_config` performs strict
parsing and raises :class:`ConfigError` (a :class:`ValueError` subclass) on
any parse or schema problem; :func:`validate_config_file` additionally
collects human-readable warnings about canvas overflow, safe-zone overflow
and missing fonts.

Schema
------

``TextLayerConfig``
    name, type (``text``/``badge``/``price``), default_font, fallback_fonts,
    max_width, max_lines (default 1), effects
    (``shadow``/``outline``/``glow``/``backdrop``), anchor, x, y,
    color (default ``#FFFFFF``), font_size, rtl_flip (default ``False``).
    Optional PIL-renderer styling knobs (all defaulted, old YAMLs unaffected):
    ``backdrop_color`` (hex or ``auto-dark``/``auto-light``), ``stroke_color``,
    ``stroke_width`` (default 2), ``glow_color``, ``padding`` (default 0).

``TemplateConfig``
    name, scene_type (``product_main``/``banner``/``poster``/``social``/
    ``academic``/``medical``),
    canvas_width, canvas_height, base_image_prompt, safe_zones (list of dicts),
    text_layers (required, unique names), translations_file, output_format
    (default ``png``), output_quality (default 95).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


# ---------------------------------------------------------------------------
# Public schema types and constants
# ---------------------------------------------------------------------------

SceneType = Literal["product_main", "banner", "poster", "social", "academic", "medical"]
LayerType = Literal["text", "badge", "price"]
EffectType = Literal["shadow", "outline", "glow", "backdrop"]

_ALLOWED_EFFECTS = {"shadow", "outline", "glow", "backdrop"}
_ALLOWED_OUTPUT_FORMATS = {"png", "jpg", "jpeg", "webp"}
_FONT_EXTS = {".otf", ".ttf", ".ttc"}
_AUTO_BACKDROP_COLORS = {"auto-dark", "auto-light"}


# ---------------------------------------------------------------------------
# Custom exception (subclass of ValueError so call sites can catch either)
# ---------------------------------------------------------------------------


class ConfigError(ValueError):
    """Raised when a configuration file cannot be parsed or fails validation.

    Inherits from :class:`ValueError` so callers that catch ``ValueError`` see
    it too.
    """


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _assets_fonts_dir() -> Path:
    return _project_root() / "assets" / "fonts"


def available_font_files() -> set[str]:
    """Return font file basenames present in ``assets/fonts/`` at call time.

    The set is computed dynamically so it always reflects what is on disk;
    files with a known font extension (``.otf``, ``.ttf``, ``.ttc``) are
    included.
    """
    fonts_dir = _assets_fonts_dir()
    if not fonts_dir.is_dir():
        return set()
    return {
        p.name
        for p in fonts_dir.iterdir()
        if p.is_file() and p.suffix.lower() in _FONT_EXTS
    }


# ---------------------------------------------------------------------------
# Color helpers (shared by the field validators below)
# ---------------------------------------------------------------------------


def _check_hex_color(value: str) -> str:
    """Validate a ``#RGB``/``#RRGGBB``/``#RRGGBBAA`` color, return it stripped."""
    v = value.strip()
    if not v:
        raise ValueError("color must not be blank")
    if v.startswith("#"):
        hex_part = v.lstrip("#")
        if len(hex_part) not in (3, 6, 8):
            raise ValueError(
                f"hex color must have 3, 6 or 8 hex digits, got {value!r}"
            )
        try:
            int(hex_part, 16)
        except ValueError as exc:
            raise ValueError(f"invalid hex color: {value!r}") from exc
    return v


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class TextLayerConfig(BaseModel):
    """A single text layer placed on the template canvas."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(..., min_length=1)
    type: str = Field(...)
    default_font: str = Field(..., min_length=1)
    fallback_fonts: List[str] = Field(default_factory=list)
    max_width: int = Field(..., gt=0)
    max_lines: int = Field(default=1, gt=0)
    effects: List[str] = Field(default_factory=list)
    anchor: str = Field(..., min_length=1)
    x: int = Field(...)
    y: int = Field(...)
    color: str = Field(default="#FFFFFF")
    font_size: int = Field(..., gt=0)
    rtl_flip: bool = Field(default=False)
    # --- PIL renderer styling knobs (optional; old YAMLs keep working) ---
    backdrop_color: Optional[str] = Field(default=None)
    stroke_color: Optional[str] = Field(default=None)
    stroke_width: int = Field(default=2, ge=0, le=20)
    glow_color: Optional[str] = Field(default=None)
    padding: int = Field(default=0, ge=0)

    @field_validator("type")
    @classmethod
    def _validate_type(cls, value: str) -> str:
        if value not in ("text", "badge", "price"):
            raise ValueError(
                f"type must be one of text/badge/price, got {value!r}"
            )
        return value

    @field_validator("effects")
    @classmethod
    def _validate_effects(cls, value: List[str]) -> List[str]:
        cleaned: List[str] = []
        for raw in value:
            if not isinstance(raw, str):
                raise ValueError(
                    f"effect entries must be strings, got {type(raw).__name__}"
                )
            eff = raw.lower().strip()
            if eff not in _ALLOWED_EFFECTS:
                raise ValueError(
                    f"effect {raw!r} not supported; allowed: {sorted(_ALLOWED_EFFECTS)}"
                )
            cleaned.append(eff)
        return cleaned

    @field_validator("color")
    @classmethod
    def _validate_color(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("color must be a string")
        return _check_hex_color(value)

    @field_validator("stroke_color", "glow_color")
    @classmethod
    def _validate_optional_hex_color(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("color must be a string")
        return _check_hex_color(value)

    @field_validator("backdrop_color")
    @classmethod
    def _validate_backdrop_color(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("backdrop_color must be a string")
        v = value.strip()
        if v.lower() in _AUTO_BACKDROP_COLORS:
            return v.lower()
        return _check_hex_color(v)

    @field_validator("anchor")
    @classmethod
    def _validate_anchor(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("anchor must be a non-blank string")
        return value.strip()


class TemplateConfig(BaseModel):
    """Top-level template configuration."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(..., min_length=1)
    scene_type: str = Field(...)
    canvas_width: int = Field(..., gt=0)
    canvas_height: int = Field(..., gt=0)
    base_image_prompt: str = Field(..., min_length=1)
    safe_zones: List[Dict[str, Any]] = Field(default_factory=list)
    text_layers: List[TextLayerConfig] = Field(...)
    translations_file: str = Field(..., min_length=1)
    output_format: str = Field(default="png")
    output_quality: int = Field(default=95, ge=1, le=100)

    @field_validator("scene_type")
    @classmethod
    def _validate_scene_type(cls, value: str) -> str:
        if value not in ("product_main", "banner", "poster", "social", "academic", "medical"):
            raise ValueError(
                "scene_type must be one of product_main/banner/poster/social/"
                f"academic/medical, got {value!r}"
            )
        return value

    @field_validator("output_format")
    @classmethod
    def _validate_output_format(cls, value: str) -> str:
        v = value.lower().strip()
        if v not in _ALLOWED_OUTPUT_FORMATS:
            raise ValueError(
                f"output_format must be one of {sorted(_ALLOWED_OUTPUT_FORMATS)}, "
                f"got {value!r}"
            )
        return v

    @field_validator("text_layers")
    @classmethod
    def _validate_unique_layer_names(
        cls, value: List[TextLayerConfig]
    ) -> List[TextLayerConfig]:
        seen: set[str] = set()
        duplicates: List[str] = []
        for layer in value:
            if layer.name in seen and layer.name not in duplicates:
                duplicates.append(layer.name)
            seen.add(layer.name)
        if duplicates:
            raise ValueError(
                f"text layer names must be unique; duplicates: {duplicates}"
            )
        return value


# ---------------------------------------------------------------------------
# Loader entry points
# ---------------------------------------------------------------------------


def _read_raw_config(path: str) -> dict:
    """Read and parse a YAML/JSON config file into a Python ``dict``."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"configuration file not found: {path}")
    if not p.is_file():
        raise ConfigError(f"configuration path is not a file: {path}")

    suffix = p.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ConfigError(f"failed to parse YAML file {path}: {exc}") from exc
    elif suffix == ".json":
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"failed to parse JSON file {path}: {exc}") from exc
    else:
        raise ConfigError(
            f"unsupported config file extension {suffix!r}; "
            "expected one of: .yaml, .yml, .json"
        )

    if data is None:
        raise ConfigError(f"configuration file is empty: {path}")
    if not isinstance(data, dict):
        raise ConfigError(
            f"configuration root must be a mapping/object, "
            f"got {type(data).__name__}"
        )
    return data


def _format_validation_error(exc: ValidationError, source: str) -> str:
    lines = [f"Invalid configuration in {source}:"]
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ())) or "<root>"
        msg = err.get("msg", "invalid value")
        err_type = err.get("type", "value_error")
        lines.append(f"  - {loc}: {msg} [{err_type}]")
    return "\n".join(lines)


def load_config(path: str) -> TemplateConfig:
    """Load and validate a template configuration file.

    Supports ``.yaml``, ``.yml`` and ``.json`` by suffix. Raises
    :class:`ConfigError` (a :class:`ValueError` subclass) with a readable
    multi-line message on any parse or schema problem (unknown keys, bad
    types, missing required fields, duplicate layer names, unsupported
    ``scene_type``/format/effect values, ...).
    """
    data = _read_raw_config(path)
    try:
        return TemplateConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(_format_validation_error(exc, path)) from exc


# ---------------------------------------------------------------------------
# Validation warnings
# ---------------------------------------------------------------------------


def _extract_bbox(zone: Dict[str, Any]) -> Optional[Tuple[Any, ...]]:
    """Extract a bbox from a safe_zone dict.

    Supports three forms:

    * ``bbox: [x1, y1, x2, y2]`` — absolute pixel coordinates.
    * ``bbox_norm: [x1, y1, x2, y2]`` — values in ``[0, 1]``, returned as
      ``("norm", (x1, y1, x2, y2))`` so the caller can scale against the canvas.
    * ``x``/``y``/``width``/``height`` keys — converted to ``(x, y, x+w, y+h)``.

    Returns ``None`` if no recognised form is present.
    """
    if not isinstance(zone, dict):
        return None
    bbox = zone.get("bbox")
    if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
        return tuple(bbox)
    bbox_norm = zone.get("bbox_norm")
    if isinstance(bbox_norm, (list, tuple)) and len(bbox_norm) == 4:
        return ("norm", tuple(bbox_norm))
    if all(k in zone for k in ("x", "y", "width", "height")):
        x, y, w, h = zone["x"], zone["y"], zone["width"], zone["height"]
        return (x, y, x + w, y + h)
    return None


def _warn_missing_font(
    layer_name: str,
    default_font: str,
    fallback_fonts: List[str],
    available: List[str],
) -> str:
    """Build a missing-font warning that suggests an actionable fallback."""
    existing_fallbacks = [f for f in fallback_fonts if f in available]
    if existing_fallbacks:
        suggestion = (
            f"select an existing fallback {existing_fallbacks[0]!r} from "
            f"fallback_fonts {fallback_fonts!r}"
        )
    elif available:
        suggestion = (
            f"none of fallback_fonts {fallback_fonts!r} exist; gracefully "
            f"fall back to an existing font file {available[0]!r}"
        )
    else:
        suggestion = "assets/fonts/ is empty or missing; no font files are available"
    return (
        f"text layer {layer_name!r}: default_font {default_font!r} is not available "
        f"in assets/fonts/. Suggested action: {suggestion}. "
        f"Available files: {available}."
    )


def validate_config_file(path: str) -> List[str]:
    """Validate a configuration file and return human-readable warnings.

    Performs the same hard validation as :func:`load_config` first and raises
    :class:`ConfigError` on any parse/schema problem. Returns a list of
    warnings about:

    * text layers whose ``x``/``y`` fall outside the canvas,
    * ``safe_zones`` whose ``bbox`` extends past the canvas,
    * text layers whose ``default_font`` (or fallback entry) is not a font
      file present in ``assets/fonts/``.

    Canvas-overflow coordinates are reported as warnings rather than hard
    errors, so a config that parses cleanly still gets through.
    """
    cfg = load_config(path)
    warnings: List[str] = []
    canvas_w = cfg.canvas_width
    canvas_h = cfg.canvas_height
    available = sorted(available_font_files())

    # Text layer overflow + font warnings
    for layer in cfg.text_layers:
        if layer.x < 0:
            warnings.append(
                f"text layer {layer.name!r}: x={layer.x} is negative; "
                "the text will not be visible."
            )
        elif layer.x >= canvas_w:
            warnings.append(
                f"text layer {layer.name!r}: x={layer.x} is at or beyond canvas "
                f"width {canvas_w}; the text will not be visible."
            )
        if layer.y < 0:
            warnings.append(
                f"text layer {layer.name!r}: y={layer.y} is negative; "
                "the text will not be visible."
            )
        elif layer.y >= canvas_h:
            warnings.append(
                f"text layer {layer.name!r}: y={layer.y} is at or beyond canvas "
                f"height {canvas_h}; the text will not be visible."
            )

        if not available:
            warnings.append(
                f"text layer {layer.name!r}: assets/fonts/ is empty or missing; "
                "no font files are available for rendering."
            )
        else:
            if layer.default_font not in available:
                warnings.append(
                    _warn_missing_font(
                        layer.name,
                        layer.default_font,
                        layer.fallback_fonts,
                        available,
                    )
                )
            for fb in layer.fallback_fonts:
                if fb not in available:
                    warnings.append(
                        f"text layer {layer.name!r}: fallback_font {fb!r} is "
                        f"not available in assets/fonts/ and will be ignored."
                    )

    # Safe-zone overflow warnings
    for idx, zone in enumerate(cfg.safe_zones):
        if isinstance(zone, dict):
            zone_name = zone.get("name", f"#{idx}")
        else:
            zone_name = f"#{idx}"
        bbox = _extract_bbox(zone) if isinstance(zone, dict) else None
        if bbox is None:
            warnings.append(
                f"safe_zone {zone_name!r}: could not extract bbox "
                "(expected 'bbox'[4], 'bbox_norm'[4], or x/y/width/height)."
            )
            continue
        if bbox[0] == "norm":
            x1n, y1n, x2n, y2n = bbox[1]
            x1, y1, x2, y2 = (
                x1n * canvas_w,
                y1n * canvas_h,
                x2n * canvas_w,
                y2n * canvas_h,
            )
            kind = "normalised bbox"
        else:
            x1, y1, x2, y2 = bbox
            kind = "bbox"
        if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
            warnings.append(
                f"safe_zone {zone_name!r}: {kind} ({x1},{y1},{x2},{y2}) is "
                "malformed (negative coords or non-positive area); this zone "
                "will not be usable."
            )
            continue
        if x2 > canvas_w or y2 > canvas_h:
            warnings.append(
                f"safe_zone {zone_name!r}: {kind} ({x1},{y1},{x2},{y2}) extends "
                f"beyond the canvas ({canvas_w}x{canvas_h}); please clip or shrink it."
            )

    return warnings


__all__ = [
    "ConfigError",
    "TemplateConfig",
    "TextLayerConfig",
    "available_font_files",
    "load_config",
    "validate_config_file",
]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python config_loader.py <path-to-config.{yaml,yml,json}>")
        sys.exit(2)

    target = sys.argv[1]
    try:
        cfg = load_config(target)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(f"Loaded config: name={cfg.name}, scene_type={cfg.scene_type}")
    print(f"  canvas: {cfg.canvas_width}x{cfg.canvas_height}")
    print(f"  text_layers: {[layer.name for layer in cfg.text_layers]}")
    warnings = validate_config_file(target)
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("No warnings.")

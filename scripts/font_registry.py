#!/usr/bin/env python3
"""Font registry — resolve a language + text layer to a weight-specific font.

The PIL renderer needs an absolute font path per layer.  Before P0-1 every
layer resolved to a ``*-Bold`` file via
:meth:`i18n_manager.I18nManager.get_font_for_language`.  This module keeps that
language/script precedence (so CJK text still gets a CJK typeface) and adds a
weight dimension: ``layer.font_weight`` selects ``Light/Regular/Medium/Bold/
Black`` from the same family.

The fallback chain never raises: requested weight → family Bold → any existing
weight of the family → language default → layer ``default_font`` → bare
filename (the renderer's system-font fallback handles the rest).
"""

from __future__ import annotations

import os
import sys
from typing import Optional

try:
    from i18n_manager import I18nManager
except ImportError:  # pragma: no cover - exercised when imported differently
    _SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
    if _SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, _SCRIPTS_DIR)
    from i18n_manager import I18nManager  # noqa: E402


# requested weight -> filename suffix.
WEIGHT_SUFFIX = {
    "light": "Light",
    "regular": "Regular",
    "medium": "Medium",
    "bold": "Bold",
    "black": "Black",
}

# Known weight suffixes, longest first so ``-ExtraBold`` is not mistaken for
# ``-Bold`` when splitting a family stem.
_KNOWN_WEIGHTS = ("ExtraBold", "SemiBold", "Black", "Medium", "Light", "Regular", "Bold")


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _assets_fonts_dir() -> str:
    return os.path.join(_project_root(), "assets", "fonts")


def _split_family(filename: str) -> tuple[str, str]:
    """Split a font filename into ``(family, extension)``.

    ``NotoSansCJKsc-Bold.otf`` -> ``("NotoSansCJKsc", ".otf")``;
    ``Roboto-Bold.ttf`` -> ``("Roboto", ".ttf")``.  Absolute paths are reduced
    to their basename first.
    """
    base = os.path.basename(filename or "")
    ext = os.path.splitext(base)[1] or ".ttf"
    stem = os.path.splitext(base)[0]
    for suffix in _KNOWN_WEIGHTS:
        if stem.endswith("-" + suffix):
            return stem[: -len(suffix) - 1], ext
    return stem, ext


def _get_font_for_language(lang: str) -> Optional[str]:
    if I18nManager is None:
        return None
    try:
        return I18nManager.get_font_for_language(lang)
    except Exception:  # noqa: BLE001 - any resolver failure falls back safely
        return None


def _existing_weight(family: str, ext: str, fonts_dir: str) -> Optional[str]:
    """Return any existing ``{family}-*.{ext}`` file, preferring Bold."""
    bold = os.path.join(fonts_dir, f"{family}-Bold{ext}")
    if os.path.exists(bold):
        return bold
    try:
        names = sorted(os.listdir(fonts_dir))
    except OSError:
        return None
    prefix = family + "-"
    for name in names:
        if name.startswith(prefix) and name.endswith(ext):
            return os.path.join(fonts_dir, name)
    return None


def resolve_font_path(lang: str, layer, fonts_dir: Optional[str] = None) -> str:
    """Return an absolute font path for ``layer`` rendered in ``lang``.

    ``layer`` is a ``TextLayerConfig`` (or any object exposing ``font_weight``
    and ``default_font`` attributes).
    """
    fonts_dir = fonts_dir or _assets_fonts_dir()
    weight = str(getattr(layer, "font_weight", None) or "bold").lower()
    suffix = WEIGHT_SUFFIX.get(weight, "Bold")

    # Primary family from the language/script resolver — keeps the existing
    # precedence (CJK text → CJK typeface, Arabic → Arabic, ...).
    lang_path = _get_font_for_language(lang)
    if lang_path:
        family, ext = _split_family(os.path.basename(lang_path))
    else:
        family, ext = _split_family(getattr(layer, "default_font", "") or "")

    # 1) Requested weight.
    candidate = os.path.join(fonts_dir, f"{family}-{suffix}{ext}")
    if os.path.exists(candidate):
        return candidate

    # 2) The family's Bold (the pre-P0-1 behaviour).
    existing = _existing_weight(family, ext, fonts_dir)
    if existing:
        return existing

    # 3) The language resolver's own path (may not exist; renderer falls back).
    if lang_path and os.path.exists(lang_path):
        return lang_path

    # 4) The layer's declared default font.
    default_name = os.path.basename(getattr(layer, "default_font", "") or "")
    if default_name:
        default_path = os.path.join(fonts_dir, default_name)
        if os.path.exists(default_path):
            return default_path

    # 5) Bare filename → the renderer's system-font fallback handles the rest.
    return default_name or "Roboto-Bold.ttf"


__all__ = ["resolve_font_path", "WEIGHT_SUFFIX"]

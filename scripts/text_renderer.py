#!/usr/bin/env python3
"""
Text Renderer Module
Renders SVG text templates onto images with professional typography effects.
"""

from __future__ import annotations

import html
import io
import math
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

import cairosvg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


try:
    # ``scripts`` is intentionally not a package, so this works when the
    # module is imported with scripts/ on sys.path.
    from i18n_manager import I18nManager
except ImportError:  # pragma: no cover - exercised when imported differently
    I18nManager = None  # type: ignore[assignment,misc]


_RTL_LANGUAGES = {"ar", "he", "fa", "ur"}


def render_text_on_image(
    image_path: str,
    output_path: str,
    placements: List[Dict[str, Any]],
    user_choices: Dict[str, Any]
) -> str:
    """Render legacy placement dictionaries through the SVG pipeline.

    The function signature is kept for callers of the original Pillow-based
    renderer.  Placement data is converted to an SVG overlay first, which
    keeps all text effects consistent with :func:`render_svg_template`.
    """
    with Image.open(image_path) as image:
        width, height = image.size
    svg_string = _placements_to_svg(placements, user_choices, width, height)
    output_format = user_choices.get("output_format")
    if not output_format:
        output_format = os.path.splitext(output_path)[1].lstrip(".") or "png"
    return render_svg_template(
        image_path,
        svg_string,
        output_path,
        width=width,
        height=height,
        output_format=output_format,
        quality=int(user_choices.get("quality", 95)),
    )


def render_svg_template(
    base_image_path: str,
    svg_string: str,
    output_path: str,
    width: int | None = None,
    height: int | None = None,
    output_format: str = "png",
    quality: int = 95,
) -> str:
    """Rasterize an SVG overlay and alpha-composite it over a base image.

    CairoSVG produces a transparent PNG for the SVG.  The overlay is resized
    when its raster dimensions differ from the base image, so templates with
    explicit or intrinsic dimensions can safely be used with any source image.
    """
    if not isinstance(svg_string, str):
        raise TypeError("svg_string must be a string")

    render_kwargs: Dict[str, Any] = {
        "bytestring": svg_string.encode("utf-8"),
        "output_width": width,
        "output_height": height,
    }
    overlay_bytes = cairosvg.svg2png(**render_kwargs)
    with Image.open(base_image_path) as base_source:
        base_image = base_source.convert("RGBA")
        with Image.open(io.BytesIO(overlay_bytes)) as overlay_source:
            overlay = overlay_source.convert("RGBA")
            if overlay.size != base_image.size:
                overlay = overlay.resize(base_image.size, Image.Resampling.LANCZOS)
        result = Image.alpha_composite(base_image, overlay)

    normalized_format = output_format.lower().lstrip(".")
    if normalized_format == "jpg":
        normalized_format = "jpeg"
    if normalized_format not in {"png", "jpeg", "webp"}:
        raise ValueError(
            f"unsupported output_format {output_format!r}; "
            "expected png, jpg/jpeg, or webp"
        )

    save_image = result.convert("RGB") if normalized_format == "jpeg" else result
    save_kwargs: Dict[str, Any] = {}
    if normalized_format in {"jpeg", "webp"}:
        save_kwargs["quality"] = max(1, min(int(quality), 100))
    save_image.save(output_path, format=normalized_format.upper(), **save_kwargs)
    return output_path


def _placements_to_svg(
    placements: List[Dict[str, Any]],
    user_choices: Dict[str, Any],
    width: int,
    height: int,
) -> str:
    """Convert legacy placement dictionaries into an SVG overlay."""
    elements: List[str] = []
    definitions: List[str] = []
    default_effects = _as_effects(user_choices.get("effects", []))
    for index, placement in enumerate(placements):
        content = str(placement.get("content", ""))
        if not content:
            continue
        placement_data = placement.get("placement", {}) or {}
        bbox = _coerce_bbox(placement_data.get("bbox"), width, height)
        if bbox is None:
            # Also accept the common flat x/y/width/height form.
            bbox = _coerce_bbox(placement, width, height)
        if bbox is None:
            bbox = (0, 0, width, height)

        effects = set(default_effects)
        effects.update(_as_effects(placement.get("effects", [])))
        style = placement.get("style_suggestions", {}) or {}
        effects.update(_as_effects(style.get("effects", [])))
        if user_choices.get("add_boxes") or "box" in effects:
            effects.add("backdrop-darken")

        font_size = _placement_font_size(bbox, content, user_choices, placement)
        text_color = (
            user_choices.get("text_color")
            or placement.get("text_color")
            or style.get("color")
            or "#FFFFFF"
        )
        text_color = _color_to_svg(text_color)
        placement_type = str(placement_data.get("type", "centered_in_box"))
        x, y = _text_origin(bbox, content, font_size, placement_type)
        rtl = _text_is_rtl(content, placement, user_choices)
        direction = ' direction="rtl"' if rtl else ""
        font_family = _font_family(user_choices.get("font_style", "default"))
        stroke_width = max(1, int(user_choices.get("stroke_width", 2)))
        stroke_color = _color_to_svg(
            user_choices.get("stroke_color")
            or ("#FFFFFF" if _luminance(text_color) < 0.5 else "#000000")
        )
        shadow_offset = user_choices.get("shadow_offset", (3, 3))
        try:
            shadow_x, shadow_y = float(shadow_offset[0]), float(shadow_offset[1])
        except (TypeError, ValueError, IndexError):
            shadow_x, shadow_y = 3.0, 3.0

        curve = "text-on-curve" in effects
        path_id = f"curve-{index}"
        if curve:
            curve_path = _curve_path(bbox)
            definitions.append(f'<path id="{path_id}" d="{curve_path}"/>')

        if "backdrop-darken" in effects:
            padding = max(6, int(font_size * 0.25))
            bx1, by1, bx2, by2 = bbox
            elements.append(
                f'<rect x="{bx1 - padding}" y="{by1 - padding}" '
                f'width="{bx2 - bx1 + 2 * padding}" '
                f'height="{by2 - by1 + 2 * padding}" rx="8" '
                'fill="#000000" fill-opacity="0.48"/>'
            )

        if "shadow" in effects:
            elements.append(
                _svg_text(
                    content, x + shadow_x, y + shadow_y, font_size, "#000000",
                    font_family, direction, path_id if curve else None,
                    opacity="0.55",
                )
            )
        elements.append(
            _svg_text(
                content, x, y, font_size, text_color, font_family, direction,
                path_id if curve else None,
                stroke=stroke_color if {"outline", "stroke"} & effects else None,
                stroke_width=stroke_width,
            )
        )

    connection_elements = _connections_to_svg(user_choices.get("connections", []), user_choices)
    elements.extend(connection_elements)
    defs = f"<defs>{''.join(definitions)}</defs>" if definitions else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(width)}" '
        f'height="{int(height)}" viewBox="0 0 {int(width)} {int(height)}">'
        f"{defs}{''.join(elements)}</svg>"
    )


def _svg_text(
    text: str,
    x: float,
    y: float,
    font_size: int,
    fill: str,
    font_family: str,
    direction: str = "",
    path_id: Optional[str] = None,
    opacity: Optional[str] = None,
    stroke: Optional[str] = None,
    stroke_width: int = 0,
) -> str:
    attrs = (
        f'font-family="{html.escape(font_family, quote=True)}" '
        f'font-size="{font_size}px" fill="{fill}" '
        f'x="{x:.2f}" y="{y:.2f}"{direction}'
    )
    if opacity is not None:
        attrs += f' fill-opacity="{opacity}"'
    if stroke:
        attrs += (
            f' stroke="{stroke}" stroke-width="{stroke_width}" '
            'paint-order="stroke fill" stroke-linejoin="round"'
        )
    escaped_lines = [html.escape(line) for line in text.splitlines() or [""]]
    if path_id:
        body = f'<textPath href="#{path_id}">{html.escape(text)}</textPath>'
        return f'<text {attrs}>{body}</text>'
    if len(escaped_lines) == 1:
        return f'<text {attrs}>{escaped_lines[0]}</text>'
    tspans = [f'<tspan x="{x:.2f}" dy="{0 if i == 0 else font_size * 1.2:.2f}">{line}</tspan>'
              for i, line in enumerate(escaped_lines)]
    return f'<text {attrs}>{"".join(tspans)}</text>'


def _coerce_bbox(value: Any, width: int, height: int) -> Optional[Tuple[float, float, float, float]]:
    if isinstance(value, dict):
        if all(key in value for key in ("x", "y", "width", "height")):
            x, y = float(value["x"]), float(value["y"])
            return x, y, x + float(value["width"]), y + float(value["height"])
        value = value.get("bbox")
    if isinstance(value, (list, tuple)) and len(value) == 4:
        try:
            x1, y1, x2, y2 = (float(item) for item in value)
            # Support normalized bounding boxes from analyzer/config output.
            if max(abs(x1), abs(y1), abs(x2), abs(y2)) <= 1:
                x1, x2 = x1 * width, x2 * width
                y1, y2 = y1 * height, y2 * height
            return x1, y1, x2, y2
        except (TypeError, ValueError):
            return None
    return None


def _placement_font_size(
    bbox: Tuple[float, float, float, float],
    text: str,
    user_choices: Dict[str, Any],
    placement: Dict[str, Any],
) -> int:
    explicit = placement.get("font_size") or user_choices.get("font_size")
    if explicit is not None:
        try:
            return max(12, min(int(explicit), 200))
        except (TypeError, ValueError):
            pass
    integer_bbox = tuple(int(round(value)) for value in bbox)
    return calculate_font_size(integer_bbox, text, user_choices)


def _text_origin(
    bbox: Tuple[float, float, float, float],
    text: str,
    font_size: int,
    placement_type: str,
) -> Tuple[float, float]:
    # SVG's y coordinate is the baseline.  This estimate keeps the legacy
    # centered/top/bottom placement behavior without needing a raster font.
    x1, y1, x2, y2 = bbox
    estimated_width = max(font_size, len(text) * font_size * 0.58)
    text_height = font_size * 1.1
    x = x1 + ((x2 - x1) - estimated_width) / 2
    if placement_type == "top":
        y = y1 + font_size + 10
    elif placement_type == "bottom":
        y = y2 - 10
    else:
        y = y1 + ((y2 - y1) + text_height) / 2
    return x, y


def _curve_path(bbox: Tuple[float, float, float, float]) -> str:
    x1, y1, x2, y2 = bbox
    mid_x = (x1 + x2) / 2
    peak_y = y1 + (y2 - y1) * 0.2
    baseline_y = y1 + (y2 - y1) * 0.65
    return f"M {x1:.2f},{baseline_y:.2f} Q {mid_x:.2f},{peak_y:.2f} {x2:.2f},{baseline_y:.2f}"


def _as_effects(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value.lower().strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).lower().strip() for item in value]
    return []


def _text_is_rtl(text: str, placement: Dict[str, Any], user_choices: Dict[str, Any]) -> bool:
    language = (
        placement.get("language") or placement.get("lang")
        or user_choices.get("language") or user_choices.get("lang")
        or user_choices.get("target_language")
    )
    if language:
        language_code = str(language).lower().replace("_", "-").split("-")[0]
        if I18nManager is not None:
            try:
                return bool(I18nManager.is_rtl(language_code))
            except Exception:
                pass
        if language_code in _RTL_LANGUAGES:
            return True
    return any(
        (0x0590 <= ord(char) <= 0x08FF) or (0xFB1D <= ord(char) <= 0xFEFF)
        for char in text
    )


def _font_family(font_style: Any) -> str:
    families = {
        "modern": "Noto Sans CJK SC",
        "traditional": "Noto Serif CJK SC",
        "traditional_tw": "Noto Sans CJK TC",
        "cartoon": "Noto Sans CJK SC",
        "korean": "Noto Sans CJK KR",
        "english": "Roboto",
        "calligraphy": "Noto Sans CJK SC",
        "default": "Roboto",
    }
    return families.get(str(font_style).lower(), families["default"])


def _luminance(color: str) -> float:
    try:
        rgb = parse_color(color)
        return (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255
    except (TypeError, ValueError, IndexError):
        return 1.0


def _color_to_svg(color: Any) -> str:
    if isinstance(color, str):
        if color.startswith("#"):
            value = color
            if len(value) == 4:
                value = "#" + "".join(char * 2 for char in value[1:])
            return value[:7]
        return color.lower()
    if isinstance(color, (tuple, list)) and len(color) >= 3:
        return "#{:02x}{:02x}{:02x}".format(*[max(0, min(int(v), 255)) for v in color[:3]])
    return "#000000"


def _connections_to_svg(connections: Any, user_choices: Dict[str, Any]) -> List[str]:
    if not user_choices.get("show_connections") or not isinstance(connections, list):
        return []
    color = _color_to_svg(user_choices.get("line_color", "#646464"))
    width = max(1, int(user_choices.get("line_width", 3)))
    elements = []
    for conn in connections:
        try:
            start, end = conn["start_point"], conn["end_point"]
            x1, y1 = float(start[0]), float(start[1])
            x2, y2 = float(end[0]), float(end[1])
        except (KeyError, TypeError, ValueError, IndexError):
            continue
        elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}" marker-end="url(#arrow)"/>'
        )
    if elements:
        # Keep the marker local to this generated SVG.  It is harmless when
        # CairoSVG ignores connections from malformed legacy input.
        marker = ("<defs><marker id=\"arrow\" markerWidth=\"10\" markerHeight=\"10\" "
                  "refX=\"8\" refY=\"3\" orient=\"auto\"><path d=\"M0,0 L0,6 L9,3 z\" "
                  f"fill=\"{color}\"/></marker></defs>")
        elements.insert(0, marker)
    return elements


def render_single_text(
    draw: ImageDraw.ImageDraw,
    img: Image.Image,
    placement: Dict[str, Any],
    user_choices: Dict[str, Any]
):
    """Render a single text element using the retained Pillow helper API."""
    text = placement["content"]
    bbox = placement["placement"]["bbox"]
    font = get_font(
        font_name=user_choices.get("font_style", "default"),
        size=calculate_font_size(bbox, text, user_choices),
        is_title=placement.get("is_title", False),
    )
    text_color = user_choices.get("text_color") or placement["style_suggestions"]["color"]
    if isinstance(text_color, str):
        text_color = parse_color(text_color)
    text_position = calculate_text_position(
        bbox, text, font, draw, placement["placement"]["type"]
    )
    effects = user_choices.get("effects", [])
    if "box" in effects or user_choices.get("add_boxes"):
        draw_text_box(draw, bbox, user_choices)
    if "shadow" in effects:
        shadow_offset = user_choices.get("shadow_offset", (3, 3))
        draw.text(
            (text_position[0] + shadow_offset[0], text_position[1] + shadow_offset[1]),
            text, font=font, fill=(0, 0, 0, 128)
        )
    if "outline" in effects or "stroke" in effects:
        stroke_color = (255, 255, 255) if sum(text_color[:3]) < 384 else (0, 0, 0)
        draw.text(
            text_position, text, font=font, fill=text_color,
            stroke_width=user_choices.get("stroke_width", 2), stroke_fill=stroke_color
        )
    else:
        draw.text(text_position, text, font=font, fill=text_color)


def get_font(font_name: str, size: int, is_title: bool = False) -> ImageFont.FreeTypeFont:
    """Load an available project font, with a system fallback."""
    font_paths = {
        "modern": ["NotoSansCJKsc-Bold.otf"],
        "traditional": ["NotoSerifCJKsc-Bold.otf", "NotoSansCJKsc-Bold.otf"],
        "traditional_tw": ["NotoSansCJKtc-Bold.otf"],
        "cartoon": ["NotoSansCJKsc-Bold.otf"],
        "english": ["Roboto-Bold.ttf", "OpenSans-Bold.ttf"],
        "korean": ["NotoSansCJKkr-Bold.otf"],
        "calligraphy": ["NotoSansCJKsc-Bold.otf"],
        "default": ["NotoSansCJKsc-Bold.otf", "Roboto-Bold.ttf", "OpenSans-Bold.ttf"],
    }
    if is_title:
        size = int(size * 1.2)
    candidates = font_paths.get(font_name, font_paths["default"])
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_fonts_dir = os.path.join(project_root, "assets", "fonts")
    errors = []
    for font_file in candidates:
        font_path = os.path.join(assets_fonts_dir, font_file)
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as exc:
                errors.append(f"assets/{font_file}: {exc}")
    # A generic system font is a final fallback for installations without the
    # project's assets; no unavailable project font names are referenced here.
    for system_path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ):
        if os.path.exists(system_path):
            try:
                return ImageFont.truetype(system_path, size)
            except Exception as exc:
                errors.append(f"system/{system_path}: {exc}")
    print(f"[WARN] Could not load a project font. Using default. Errors: {errors[:3]}")
    return ImageFont.load_default()


def calculate_font_size(bbox: Tuple[int, int, int, int], text: str, user_choices: Dict[str, Any]) -> int:
    """Calculate appropriate font size for the bounding box."""
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    text_length = len(text)
    if text_length <= 4:
        base_size = min(width // 2, height // 2)
    elif text_length <= 10:
        base_size = min(width // 4, height // 3)
    elif text_length <= 20:
        base_size = min(width // 6, height // 4)
    else:
        base_size = min(width // 10, height // 5)
    size_preference = user_choices.get("text_size", "auto")
    if size_preference == "large":
        base_size = int(base_size * 1.3)
    elif size_preference == "small":
        base_size = int(base_size * 0.7)
    return max(12, min(base_size, 200))


def calculate_text_position(
    bbox: Tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.ImageDraw,
    placement_type: str
) -> Tuple[int, int]:
    """Calculate text position within bounding box."""
    bbox_text = draw.textbbox((0, 0), text, font=font)
    text_width = bbox_text[2] - bbox_text[0]
    text_height = bbox_text[3] - bbox_text[1]
    box_width = bbox[2] - bbox[0]
    box_height = bbox[3] - bbox[1]
    if placement_type == "centered_in_box":
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[1] + (box_height - text_height) // 2
    elif placement_type == "top":
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[1] + 10
    elif placement_type == "bottom":
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[3] - text_height - 10
    else:
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[1] + (box_height - text_height) // 2
    return (x, y)


def draw_text_box(draw: ImageDraw.ImageDraw, bbox: Tuple[int, int, int, int], user_choices: Dict[str, Any]):
    """Draw background box for text."""
    padding = 10
    box_bbox = (bbox[0] + padding, bbox[1] + padding, bbox[2] - padding, bbox[3] - padding)
    box_color = user_choices.get("box_color", (255, 255, 255, 180))
    if isinstance(box_color, str):
        box_color = parse_color(box_color, alpha=180)
    draw.rounded_rectangle(box_bbox, radius=8, fill=box_color)


def draw_connection(draw: ImageDraw.ImageDraw, conn: Dict[str, Any], user_choices: Dict[str, Any]):
    """Draw connection line/arrow between nodes."""
    start = conn["start_point"]
    end = conn["end_point"]
    line_color = user_choices.get("line_color", (100, 100, 100))
    if isinstance(line_color, str):
        line_color = parse_color(line_color)
    line_width = user_choices.get("line_width", 3)
    draw.line([start, end], fill=line_color, width=line_width)
    draw_arrow_head(draw, start, end, line_color, line_width + 2)


def draw_arrow_head(draw: ImageDraw.ImageDraw, start: Tuple[int, int], end: Tuple[int, int], color: Tuple[int, ...], size: int):
    """Draw arrow head at the end of a connection line."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    angle = math.atan2(dy, dx)
    arrow_angle = math.pi / 6
    arrow_len = size * 3
    x1 = end[0] - arrow_len * math.cos(angle - arrow_angle)
    y1 = end[1] - arrow_len * math.sin(angle - arrow_angle)
    x2 = end[0] - arrow_len * math.cos(angle + arrow_angle)
    y2 = end[1] - arrow_len * math.sin(angle + arrow_angle)
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color)


def parse_color(color_str: str, alpha: Optional[int] = None) -> Tuple[int, ...]:
    """Parse a named or hexadecimal color into an RGB/RGBA tuple."""
    color_map = {
        "red": (255, 0, 0), "green": (0, 128, 0), "blue": (0, 0, 255),
        "white": (255, 255, 255), "black": (0, 0, 0), "yellow": (255, 255, 0),
        "gold": (255, 215, 0), "gray": (128, 128, 128),
    }
    color_str_lower = color_str.lower()
    if color_str_lower in color_map:
        rgb = color_map[color_str_lower]
    elif color_str.startswith("#"):
        hex_color = color_str.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(char * 2 for char in hex_color)
        if len(hex_color) not in (6, 8) or not re.fullmatch(r"[0-9a-fA-F]+", hex_color):
            raise ValueError(f"invalid color: {color_str!r}")
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        if len(hex_color) == 8 and alpha is None:
            alpha = int(hex_color[6:8], 16)
    else:
        rgb = (0, 0, 0)
    if alpha is not None:
        return (*rgb, alpha)
    return rgb


# ---------------------------------------------------------------------------
# PIL 直绘渲染器（替代 cairosvg 路径 —— cairo 无法解析字体文件路径、
# 用户字体目录族名，也无 HarfBuzz 整形；PIL 按路径加载字体 + raqm 可
# 正确渲染日文/中文/阿拉伯语 RTL 连写）
# ---------------------------------------------------------------------------


_H_ANCHORS = {"left": "start", "start": "start", "center": "middle",
              "middle": "middle", "right": "end", "end": "end"}
_V_ANCHORS = {"top": "top", "center": "middle", "middle": "middle",
              "bottom": "bottom"}


def _parse_anchor(anchor: str) -> Tuple[str, str]:
    """Parse a (possibly composite) anchor into (vertical, horizontal).

    ``bottom-center`` -> ``("bottom", "middle")``; a single token is treated
    as horizontal when it is one of left/center/right/start/middle/end,
    otherwise as vertical (``top``/``bottom``). Defaults: top + start.
    """
    parts = [p for p in str(anchor or "").lower().strip().split("-") if p]
    vertical, horizontal = "top", "start"
    if len(parts) >= 2:
        vertical = _V_ANCHORS.get(parts[0], "top")
        horizontal = _H_ANCHORS.get(parts[-1], "start")
    elif parts:
        token = parts[0]
        if token in _H_ANCHORS:
            horizontal = _H_ANCHORS[token]
        elif token in ("top", "bottom"):
            vertical = token
    return vertical, horizontal


def _is_cjk_char(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF
        or 0x3400 <= cp <= 0x4DBF
        or 0x3040 <= cp <= 0x30FF
        or 0xAC00 <= cp <= 0xD7AF
        or 0x3000 <= cp <= 0x303F
    )


def _measure(draw: ImageDraw.ImageDraw, text: str, font, rtl_kwargs: Dict[str, Any]) -> float:
    """Measure shaped text width; fall back gracefully without raqm."""
    if not text:
        return 0.0
    try:
        return float(draw.textlength(text, font=font, **rtl_kwargs))
    except (TypeError, ValueError):
        return float(draw.textlength(text, font=font))


def _tokenize(text: str) -> List[str]:
    """Split into wrappable tokens: CJK chars individually, latin/digit runs
    as words, spaces as break opportunities, ``\\n`` as a forced break."""
    tokens: List[str] = []
    buf = ""
    for ch in text:
        if ch == "\n":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append("\n")
        elif _is_cjk_char(ch):
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        elif ch.isspace():
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(" ")
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    return tokens


def _wrap_text_pil(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    max_width: int,
    rtl_kwargs: Dict[str, Any],
) -> List[str]:
    """Greedy word/char wrapping against ``max_width`` (px)."""
    lines: List[str] = []
    current = ""
    for token in _tokenize(text):
        if token == "\n":
            lines.append(current.rstrip())
            current = ""
            continue
        if token == " " and not current:
            continue
        candidate = current + token
        if current and _measure(draw, candidate.rstrip(), font, rtl_kwargs) > max_width:
            lines.append(current.rstrip())
            current = "" if token == " " else token
        else:
            current = candidate
    lines.append(current.rstrip())
    return [line for line in lines if line] or [""]


def _load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load ``font_path`` at ``size``; fall back to the project Roboto."""
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    fallback = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "fonts", "Roboto-Bold.ttf",
    )
    try:
        return ImageFont.truetype(fallback, size)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# 混排字体回退：按 Unicode 字符集把一行切成 run，主字体 cmap 不覆盖的 run
# 用回退字体绘制；run 显示顺序由 bidi 算法决定（RTL 行内嵌 LTR 片段等）
# ---------------------------------------------------------------------------

try:  # python-bidi：run 级显示顺序；缺失时退化为整段反转
    from bidi.algorithm import get_display as _bidi_get_display
except Exception:  # pragma: no cover - python-bidi optional at import time
    _bidi_get_display = None

_ASSETS_FONTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts"
)

# cmap 解析结果（path -> frozenset(codepoints) 或 None=无法解析）
_CMAP_CACHE: Dict[str, Optional[frozenset]] = {}
# truetype 字体对象缓存：(path, size) -> font
_FONT_OBJECT_CACHE: Dict[Tuple[str, int], Any] = {}

# 字符集 -> 回退字体链（存在且覆盖该 run 的第一个生效）
_FALLBACK_BY_SCRIPT: Dict[str, List[str]] = {
    "arabic": ["NotoSansArabic-Bold.ttf", "NotoSansCJKsc-Bold.otf", "Roboto-Bold.ttf"],
    "hebrew": ["NotoSansHebrew-Bold.ttf", "NotoSansCJKsc-Bold.otf", "Roboto-Bold.ttf"],
    "cjk": ["NotoSansCJKsc-Bold.otf", "Roboto-Bold.ttf"],
    "latin": ["Roboto-Bold.ttf", "NotoSansCJKsc-Bold.otf"],
}


def _char_script(ch: str) -> str:
    """Classify a character into arabic/hebrew/cjk/latin(=其余含数字符号)."""
    cp = ord(ch)
    if (
        0x0600 <= cp <= 0x06FF  # Arabic
        or 0x0750 <= cp <= 0x077F  # Arabic Supplement
        or 0x08A0 <= cp <= 0x08FF  # Arabic Extended-A
        or 0xFB50 <= cp <= 0xFDFF  # Arabic Presentation Forms-A
        or 0xFE70 <= cp <= 0xFEFF  # Arabic Presentation Forms-B
    ):
        return "arabic"
    if 0x0590 <= cp <= 0x05FF or 0xFB1D <= cp <= 0xFB4F:
        return "hebrew"
    if _is_cjk_char(ch) or 0x1100 <= cp <= 0x11FF or 0xFF00 <= cp <= 0xFFEF:
        return "cjk"
    return "latin"


def _split_runs(text: str) -> List[Tuple[str, str]]:
    """Split ``text`` into ``(run_text, script)`` by Unicode block.

    空白归入相邻 run（跟随前一个非空白字符的字符集；行首空白并入后一个 run）。
    """
    runs: List[List[Any]] = []  # [script_or_None, text]
    for ch in text:
        script = None if ch.isspace() else _char_script(ch)
        if not runs:
            runs.append([script, ch])
        elif script is None or runs[-1][0] is None or script == runs[-1][0]:
            if runs[-1][0] is None:
                runs[-1][0] = script
            runs[-1][1] += ch
        else:
            runs.append([script, ch])
    return [(run_text, script or "latin") for script, run_text in runs]


def _font_cmap(font_path: str) -> Optional[frozenset]:
    """Return the font's covered codepoints (cached); None when unparsable."""
    if font_path not in _CMAP_CACHE:
        cmap: Optional[frozenset] = None
        try:
            from fontTools.ttLib import TTFont

            with TTFont(font_path, fontNumber=0, lazy=True) as ttfont:
                cmap = frozenset(ttfont.getBestCmap().keys())
        except Exception:
            cmap = None
        _CMAP_CACHE[font_path] = cmap
    return _CMAP_CACHE[font_path]


def _font_covers(font_path: str, chars: str) -> bool:
    """True when ``font_path``'s cmap covers every (non-space) char."""
    cmap = _font_cmap(font_path)
    if cmap is None:
        # 无法解析时保持旧行为：假定覆盖（由 raqm/PIL 兜底）
        return True
    return all(ch.isspace() or ord(ch) in cmap for ch in chars)


def _load_font_cached(font_path: str, size: int) -> Any:
    """``_load_font`` with a (path, size) object cache."""
    key = (font_path, int(size))
    if key not in _FONT_OBJECT_CACHE:
        _FONT_OBJECT_CACHE[key] = _load_font(font_path, int(size))
    return _FONT_OBJECT_CACHE[key]


def _resolve_run_font(run_text: str, script: str, primary_path: str, layer) -> str:
    """Pick a font covering ``run_text``: script chain, then layer fallbacks."""
    primary_abs = os.path.abspath(primary_path)
    candidates = list(_FALLBACK_BY_SCRIPT.get(script, []))
    candidates.extend(getattr(layer, "fallback_fonts", None) or [])
    for name in candidates:
        path = os.path.join(_ASSETS_FONTS_DIR, name)
        if not os.path.exists(path) or os.path.abspath(path) == primary_abs:
            continue
        if _font_covers(path, run_text):
            return path
    return primary_path


def _bidi_order_runs(
    items: List[Tuple[str, Any, Dict[str, Any], str]], rtl: bool
) -> List[Tuple[str, Any, Dict[str, Any]]]:
    """Reorder ``(text, font, kwargs, script)`` runs into display order.

    用 bidi 算法作用于代理字符串（每个 run 映射为同类 bidi 属性的唯一字符：
    RTL->Hebrew 字母、纯数字->数字、其余->Latin 字母），再把显示顺序映射回
    run。python-bidi 缺失时 RTL 段落退化为整体反转 run 序列。
    """
    if len(items) <= 1:
        return [(t, f, kw) for t, f, kw, _s in items]
    if _bidi_get_display is None:
        ordered = list(reversed(items)) if rtl else items
        return [(t, f, kw) for t, f, kw, _s in ordered]
    pools = {
        "L": [chr(c) for c in range(ord("a"), ord("z") + 1)]
        + [chr(c) for c in range(ord("A"), ord("Z") + 1)],
        "R": [chr(0x05D0 + i) for i in range(22)],
        "EN": [chr(ord("0") + i) for i in range(10)],
    }
    surrogate: List[str] = []
    back_map: Dict[str, int] = {}
    for idx, (run_text, _f, _kw, script) in enumerate(items):
        if script in ("arabic", "hebrew"):
            cls = "R"
        elif any(ch.isdigit() for ch in run_text) and not any(
            ch.isalpha() for ch in run_text
        ):
            cls = "EN"
        else:
            cls = "L"
        pool = pools[cls] or pools["L"]
        if not pool:  # run 太多耗尽代理字符：退化为简单反转/顺序
            ordered = list(reversed(items)) if rtl else items
            return [(t, f, kw) for t, f, kw, _s in ordered]
        ch = pool.pop(0)
        surrogate.append(ch)
        back_map[ch] = idx
    display = _bidi_get_display("".join(surrogate), base_dir="R" if rtl else "L")
    order = [back_map[ch] for ch in display if ch in back_map]
    if len(order) != len(items):  # 防御：映射不完整时退化
        ordered = list(reversed(items)) if rtl else items
        return [(t, f, kw) for t, f, kw, _s in ordered]
    return [(items[i][0], items[i][1], items[i][2]) for i in order]


def _line_run_items(
    draw: ImageDraw.ImageDraw,
    line: str,
    font: Any,
    font_path: str,
    size: int,
    rtl: bool,
    lang: str,
    layer,
) -> List[Tuple[str, Any, Dict[str, Any]]]:
    """Build display-ordered ``(text, font, kwargs)`` draw items for a line.

    主字体覆盖整行时走单字体快路径（保持既有行为，CJK 字体含拉丁时不误拆）；
    否则按字符集切 run，不覆盖的 run 用回退字体，再按 bidi 显示顺序排列。
    """
    if _font_covers(font_path, line):
        rtl_kwargs = {"direction": "rtl", "language": lang} if rtl else {}
        return [(line, font, rtl_kwargs)]
    items: List[Tuple[str, Any, Dict[str, Any], str]] = []
    for run_text, script in _split_runs(line):
        if _font_covers(font_path, run_text):
            run_path = font_path
        else:
            run_path = _resolve_run_font(run_text, script, font_path, layer)
        run_font = font if run_path == font_path else _load_font_cached(run_path, size)
        if script == "arabic":
            kwargs: Dict[str, Any] = {"direction": "rtl", "language": "ar"}
        elif script == "hebrew":
            kwargs = {"direction": "rtl", "language": "he"}
        else:
            kwargs = {}
        items.append((run_text, run_font, kwargs, script))
    return _bidi_order_runs(items, rtl)


def _resolve_rgba(color_value: Any, default_alpha: int = 255) -> Tuple[int, ...]:
    """Parse a config color into an RGBA tuple."""
    if color_value is None:
        return (0, 0, 0, default_alpha)
    try:
        parsed = parse_color(str(color_value))
    except (ValueError, TypeError):
        return (0, 0, 0, default_alpha)
    if len(parsed) == 3:
        return (*parsed, default_alpha)
    return tuple(parsed[:4])


def _resolve_backdrop_rgba(layer, region_bright: Optional[bool]) -> Tuple[int, ...]:
    """Resolve backdrop fill: explicit hex, or auto-dark/auto-light panel.

    ``layer.backdrop_opacity`` (0–255) overrides the default alpha when set;
    otherwise the pre-P0-2 defaults are preserved (150 for auto panels, 200 for
    explicit hex).
    """
    value = (layer.backdrop_color or "").strip().lower() if layer.backdrop_color else None
    if value in (None, ""):
        value = "auto-dark" if not region_bright else "auto-light"
    opacity = getattr(layer, "backdrop_opacity", None)
    if value == "auto-dark":
        alpha = 150 if opacity is None else max(0, min(int(opacity), 255))
        return (0, 0, 0, alpha)
    if value == "auto-light":
        alpha = 150 if opacity is None else max(0, min(int(opacity), 255))
        return (255, 255, 255, alpha)
    alpha = 200 if opacity is None else max(0, min(int(opacity), 255))
    return _resolve_rgba(value, default_alpha=alpha)


def _fit_font_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    layer,
    rtl_kwargs: Dict[str, Any],
) -> Tuple[Any, List[str]]:
    """Shrink font size until the wrapped text fits ``max_lines`` (>=10px)."""
    size = layer.font_size
    while True:
        font = _load_font(font_path, size)
        lines = _wrap_text_pil(draw, text, font, layer.max_width, rtl_kwargs)
        if len(lines) <= layer.max_lines or size <= 10:
            return font, lines
        # 等比缩小：按行数超出比例缩，再留 5% 余量
        scale = layer.max_lines / len(lines)
        size = max(10, int(size * scale * 0.95))


def _draw_lines(
    draw: ImageDraw.ImageDraw,
    placements: List[Tuple[float, float, str, Any, Dict[str, Any]]],
    fill: Tuple[int, ...],
    stroke_width: int = 0,
    stroke_fill: Optional[Tuple[int, ...]] = None,
) -> None:
    """Draw ``(x, y, text, font, kwargs)`` items;每个 run 可用不同字体。"""
    for line_x, line_y, text, font, kwargs in placements:
        if not text:
            continue
        try:
            draw.text(
                (line_x, line_y), text, font=font, fill=fill,
                stroke_width=stroke_width, stroke_fill=stroke_fill,
                anchor="la", **kwargs,
            )
        except (TypeError, ValueError):
            # raqm 不可用时的兜底：去掉 direction/language 直接绘制
            draw.text(
                (line_x, line_y), text, font=font, fill=fill,
                stroke_width=stroke_width, stroke_fill=stroke_fill,
                anchor="la",
            )


def _clamp_alpha(value: Optional[int], default: int) -> int:
    return default if value is None else max(0, min(int(value), 255))


def _render_backdrop(base, layer, left, right, y0, block_h, size) -> None:
    """Semi-transparent rounded-rect backing (pill for ``type: badge``)."""
    pad = getattr(layer, "padding", 0) or (
        16 if getattr(layer, "type", "") == "badge" else max(6, size // 6)
    )
    box = (left - pad, y0 - pad, right + pad, y0 + block_h + pad)
    explicit_radius = getattr(layer, "backdrop_radius", None)
    if explicit_radius is not None:
        radius = float(max(0, int(explicit_radius)))
    elif getattr(layer, "type", "") == "badge":
        radius = (block_h + 2 * pad) / 2.0  # pill：半径=高度一半
    else:
        radius = max(6.0, size / 6.0)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        box, radius=radius, fill=_resolve_backdrop_rgba(layer, None)
    )
    base.alpha_composite(overlay)


def _render_shadow(base, placements, layer, size) -> None:
    """Offset shadow; ``shadow_blur > 0`` produces a soft (Gaussian) shadow."""
    shadow_rgb = _resolve_rgba(layer.shadow_color or "#000000")[:3]
    alpha = _clamp_alpha(getattr(layer, "shadow_opacity", None), 150)
    shadow_rgba = (*shadow_rgb, alpha)

    off = size // 18 + 1
    dx = off if getattr(layer, "shadow_offset_x", None) is None else int(layer.shadow_offset_x)
    dy = off if getattr(layer, "shadow_offset_y", None) is None else int(layer.shadow_offset_y)
    blur = getattr(layer, "shadow_blur", None)
    blur_radius = 0 if blur is None else max(0, int(blur))

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    _draw_lines(
        ImageDraw.Draw(overlay),
        [(px + dx, py + dy, t, f, kw) for px, py, t, f, kw in placements],
        shadow_rgba,
    )
    if blur_radius > 0:
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    base.alpha_composite(overlay)


def _render_glow(base, placements, layer, size) -> None:
    """Text glow: draw glyphs, blur, composite ``glow_strength`` times."""
    glow_fill = _resolve_rgba(layer.glow_color or layer.color)
    radius = (
        max(2, size // 10)
        if getattr(layer, "glow_radius", None) is None
        else max(0, int(layer.glow_radius))
    )
    strength = (
        3 if getattr(layer, "glow_strength", None) is None
        else max(1, int(layer.glow_strength))
    )
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    _draw_lines(ImageDraw.Draw(overlay), placements, glow_fill)
    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=radius)) if radius > 0 else overlay
    for _ in range(strength):
        base.alpha_composite(blurred)


def _gradient_image(width, height, angle, color_from, color_to):
    """Return an RGB image filled with a linear gradient along ``angle``.

    Returns ``None`` when numpy is unavailable so callers can fall back to a
    flat fill.
    """
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - numpy is a project dependency
        return None
    rad = math.radians(angle % 360)
    ux, uy = math.cos(rad), math.sin(rad)
    cx, cy = (width - 1) / 2.0, (height - 1) / 2.0
    x = np.linspace(0, width - 1, width, dtype=np.float32)
    y = np.linspace(0, height - 1, height, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    proj = (xx - cx) * ux + (yy - cy) * uy
    half_span = ((width - 1) * abs(ux) + (height - 1) * abs(uy)) / 2.0
    t = np.zeros_like(proj) if half_span < 1e-6 else (proj + half_span) / (2.0 * half_span)
    t = np.clip(t, 0.0, 1.0)
    c_from = np.asarray(color_from, dtype=np.float32)
    c_to = np.asarray(color_to, dtype=np.float32)
    arr = c_from[None, None, :] + t[..., None] * (c_to - c_from)[None, None, :]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def _render_gradient_fill(base, placements, layer) -> None:
    """Fill glyphs with a linear gradient using a text alpha mask."""
    color_from = _resolve_rgba(layer.gradient_from or layer.color or "#FFFFFF")[:3]
    color_to = _resolve_rgba(layer.gradient_to or layer.color or "#FFFFFF")[:3]
    angle = 90 if getattr(layer, "gradient_angle", None) is None else int(layer.gradient_angle)
    w, h = base.size

    mask = Image.new("L", base.size, 0)
    _draw_lines(ImageDraw.Draw(mask), placements, 255)
    if mask.getbbox() is None:
        return

    gradient = _gradient_image(w, h, angle, color_from, color_to)
    if gradient is None:
        _draw_lines(ImageDraw.Draw(base), placements, (*color_from, 255))
        return

    layer_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer_img.paste(gradient, (0, 0))
    layer_img.putalpha(mask)
    base.alpha_composite(layer_img)


def _render_text_body(base, placements, layer, text_rgba, effects) -> None:
    """Draw the main text: flat fill or gradient, with optional outline."""
    stroke_w = 0
    stroke_fill = None
    if "outline" in effects:
        stroke_w = max(1, layer.stroke_width)
        if layer.stroke_color:
            stroke_fill = _resolve_rgba(layer.stroke_color)
        else:
            luminance = (0.2126 * text_rgba[0] + 0.7152 * text_rgba[1]
                         + 0.0722 * text_rgba[2]) / 255
            stroke_fill = (0, 0, 0, 255) if luminance > 0.5 else (255, 255, 255, 255)

    if "gradient" in effects:
        if stroke_w:
            # Solid outline beneath the gradient fill.
            _draw_lines(
                ImageDraw.Draw(base), placements, (0, 0, 0, 0),
                stroke_width=stroke_w, stroke_fill=stroke_fill,
            )
        _render_gradient_fill(base, placements, layer)
    else:
        _draw_lines(
            ImageDraw.Draw(base), placements, text_rgba,
            stroke_width=stroke_w, stroke_fill=stroke_fill,
        )


def _render_layer_pil(
    base: Image.Image,
    layer,
    text: str,
    font_path: str,
    lang: str,
    rtl: bool,
) -> None:
    """Draw one text layer (effects included) onto the RGBA ``base``."""
    draw = ImageDraw.Draw(base)
    rtl_kwargs: Dict[str, Any] = {"direction": "rtl", "language": lang} if rtl else {}

    font, lines = _fit_font_size(draw, text, font_path, layer, rtl_kwargs)
    size = getattr(font, "size", layer.font_size) or layer.font_size
    line_height = max(int(size * 1.25), size + 2)
    block_h = line_height * len(lines)

    vertical, horizontal = _parse_anchor(layer.anchor)
    if rtl and layer.rtl_flip:
        # RTL 镜像：start <-> end
        horizontal = {"start": "end", "end": "start"}.get(horizontal, horizontal)

    # 垂直：y 为锚点（top=文本块顶 / middle=中心 / bottom=文本块底）
    if vertical == "middle":
        y0 = layer.y - block_h / 2.0
    elif vertical == "bottom":
        y0 = layer.y - block_h
    else:
        y0 = float(layer.y)

    # 逐行切 run（混排字体回退 + bidi 显示顺序），再按锚点摆放；
    # placements 为扁平的 (x, y, run_text, run_font, run_kwargs)
    placements: List[Tuple[float, float, str, Any, Dict[str, Any]]] = []
    line_extents: List[Tuple[float, float]] = []
    for i, line in enumerate(lines):
        items = _line_run_items(
            draw, line, font, font_path, size, rtl, lang, layer
        )
        run_widths = [_measure(draw, t, f, kw) for t, f, kw in items]
        w = sum(run_widths)
        # 水平：x 为锚点（start=行左缘 / middle=行中心 / end=行右缘）
        if horizontal == "middle":
            line_x = layer.x - w / 2.0
        elif horizontal == "end":
            line_x = layer.x - w
        else:
            line_x = float(layer.x)
        line_y = y0 + i * line_height
        cursor = line_x
        for (t, f, kw), rw in zip(items, run_widths):
            placements.append((cursor, line_y, t, f, kw))
            cursor += rw
        line_extents.append((line_x, line_x + w))

    left = min(e[0] for e in line_extents)
    right = max(e[1] for e in line_extents)
    effects = set(layer.effects or [])
    text_rgba = _resolve_rgba(layer.color)

    # --- backdrop：半透明圆角矩形衬底（badge 默认 pill 形） ---
    if "backdrop" in effects:
        _render_backdrop(base, layer, left, right, y0, block_h, size)

    # --- shadow：偏移拷贝；shadow_blur > 0 时为软阴影 ---
    if "shadow" in effects:
        _render_shadow(base, placements, layer, size)

    # --- glow：文字 -> 高斯模糊 -> 叠加多次再画主文字 ---
    if "glow" in effects:
        _render_glow(base, placements, layer, size)

    # --- 主文字（flat 或 gradient 填充；outline 用 stroke 实现） ---
    _render_text_body(base, placements, layer, text_rgba, effects)


def _apply_layout_plan(template_config, plan: Optional[Dict[str, Any]]):
    """Return ``{layer_name: layer_copy}`` with plan adjustments applied."""
    if not plan:
        return {}
    adjusted = {}
    plan_by_name = {
        entry.get("name"): entry for entry in plan.get("layers", []) if entry.get("name")
    }
    for layer in template_config.text_layers:
        entry = plan_by_name.get(layer.name)
        if not entry:
            continue
        update = {}
        for field in ("x", "y", "color", "effects", "font_size", "backdrop_color"):
            if field in entry and entry[field] is not None:
                update[field] = entry[field]
        if update:
            try:
                adjusted[layer.name] = layer.model_copy(update=update)
            except Exception:
                continue
    return adjusted


def render_layers_pil(
    base_image_path: str,
    template_config,
    variables: Dict[str, Any],
    lang: str = "en",
    font_resolver=None,
    output_path: str = "",
    smart_layout: bool = True,
    output_format: Optional[str] = None,
    quality: Optional[int] = None,
    layout_plan: Optional[Dict[str, Any]] = None,
) -> str:
    """Render every text layer directly with PIL (no SVG/cairo involved).

    Fonts are loaded by absolute path via :func:`ImageFont.truetype`, so CJK
    and Arabic glyphs render with the configured typefaces, and RTL text is
    shaped through raqm (``direction="rtl"``). Effects (shadow/outline/glow/
    backdrop) are composited as transparent overlays.

    ``smart_layout`` runs :func:`layout_composer.compose_layout` on the base
    image and applies the resulting placement/contrast/effect adjustments;
    pass a precomputed ``layout_plan`` to skip the re-analysis.
    """
    plan = layout_plan
    if plan is None and smart_layout:
        try:
            from layout_composer import compose_layout
        except ImportError:  # pragma: no cover - import path fallback
            _scripts = os.path.dirname(os.path.abspath(__file__))
            if _scripts not in sys.path:
                sys.path.insert(0, _scripts)
            try:
                from layout_composer import compose_layout
            except ImportError:
                compose_layout = None
        if compose_layout is not None:
            try:
                plan = compose_layout(base_image_path, template_config, lang=lang)
            except Exception as exc:
                print(f"[WARN] smart layout analysis failed, using raw config: {exc}")
                plan = None

    adjusted = _apply_layout_plan(template_config, plan)
    rtl = bool(I18nManager.is_rtl(lang)) if I18nManager is not None else (
        str(lang).lower() in _RTL_LANGUAGES
    )

    with Image.open(base_image_path) as source:
        base = source.convert("RGBA")

    for layer in template_config.text_layers:
        text = str(variables.get(layer.name, variables.get("text", "")) or "")
        if not text.strip():
            continue
        effective = adjusted.get(layer.name, layer)
        font_path = (
            font_resolver(lang, effective) if font_resolver else effective.default_font
        )
        _render_layer_pil(base, effective, text, font_path, lang, rtl)

    # 输出保存逻辑与 render_svg_template 保持一致
    normalized = (output_format or getattr(template_config, "output_format", "png"))
    normalized = str(normalized).lower().lstrip(".")
    if normalized == "jpg":
        normalized = "jpeg"
    if normalized not in {"png", "jpeg", "webp"}:
        raise ValueError(
            f"unsupported output_format {output_format!r}; "
            "expected png, jpg/jpeg, or webp"
        )
    save_image = base.convert("RGB") if normalized == "jpeg" else base
    save_kwargs: Dict[str, Any] = {}
    if normalized in {"jpeg", "webp"}:
        q = quality if quality is not None else getattr(
            template_config, "output_quality", 95
        )
        save_kwargs["quality"] = max(1, min(int(q), 100))
    save_image.save(output_path, format=normalized.upper(), **save_kwargs)
    return output_path


if __name__ == "__main__":
    print("Text renderer module loaded")
    print("Available functions: render_svg_template, render_layers_pil, render_text_on_image, get_font, calculate_font_size")
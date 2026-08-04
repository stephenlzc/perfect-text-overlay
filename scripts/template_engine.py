#!/usr/bin/env python3
"""Jinja2-backed SVG template rendering for text overlays."""

from __future__ import annotations

import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any

from jinja2 import Environment, Template

try:
    from scripts.i18n_manager import I18nManager
except ImportError:  # scripts is also intended to work as a loose module dir
    sys.path.insert(0, os.path.dirname(__file__))
    from i18n_manager import I18nManager


class SVGTemplateEngine:
    """Render SVG files or generate SVG from a validated TemplateConfig."""

    def __init__(self, template_path: str | None = None):
        self.template_path = template_path
        self._template: Template | None = None
        if template_path is not None:
            with open(template_path, "r", encoding="utf-8") as handle:
                self._template = Environment(autoescape=True).from_string(handle.read())

    def render(self, variables: dict, lang: str = "en") -> str:
        if self._template is None:
            raise ValueError("template_path is required for render(); use build_svg_from_config()")
        context = dict(variables)
        context["lang"] = lang
        svg = self._template.render(**context)
        root = ET.fromstring(svg)
        if I18nManager.is_rtl(lang):
            root.set("direction", "rtl")
            for node in root.iter():
                if node.tag.rsplit("}", 1)[-1] == "text":
                    node.set("direction", "rtl")
        return ET.tostring(root, encoding="unicode")

    def validate(self, variables: dict, required: list | None = None,
                 max_widths: dict | None = None) -> list:
        warnings = []
        for key in required or []:
            if key not in variables or variables[key] is None or str(variables[key]) == "":
                warnings.append(f"缺少必填变量: {key}")
        for key, limit in (max_widths or {}).items():
            value = variables.get(key)
            if value is None:
                continue
            text = str(value)
            size = 48
            if isinstance(limit, dict):
                width = limit.get("max_width", limit.get("width", 0))
                size = limit.get("font_size", size)
                lang = limit.get("lang", "en")
            else:
                width, lang = limit, variables.get("lang", "en")
            estimated = _estimate_width(text, size)
            if estimated > float(width):
                warnings.append(f"{lang} 语文案过长可能溢出")
        return warnings

    @staticmethod
    def auto_resize_text(svg_string: str, max_width: int) -> str:
        root = ET.fromstring(svg_string)
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1] != "text":
                continue
            text = "".join(node.itertext())
            style = node.get("style", "")
            match = re.search(r"font-size\s*:\s*(\d+(?:\.\d+)?)", style)
            raw_size = match.group(1) if match else node.get("font-size", "16")
            try:
                size = float(raw_size)
            except ValueError:
                continue
            estimated = _estimate_width(text, size)
            if estimated > max_width and estimated:
                new_size = max(1.0, size * max_width / estimated)
                if match:
                    node.set("style", style[:match.start(1)] + f"{new_size:g}" + style[match.end(1):])
                else:
                    node.set("font-size", f"{new_size:g}")
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def build_svg_from_config(template_config, variables: dict, lang: str = "en",
                              font_resolver=None) -> str:
        rtl = I18nManager.is_rtl(lang)
        width, height = template_config.canvas_width, template_config.canvas_height
        root = ET.Element("svg", {"width": str(width), "height": str(height),
                                   "xmlns": "http://www.w3.org/2000/svg"})
        if rtl:
            root.set("direction", "rtl")
        defs = ET.SubElement(root, "defs")
        filter_ids = []
        for index, layer in enumerate(template_config.text_layers):
            effects = set(layer.effects)
            if "shadow" in effects:
                fid = f"shadow-{index}"; filter_ids.append(fid)
                f = ET.SubElement(defs, "filter", id=fid)
                ET.SubElement(f, "feDropShadow", {"dx": "3", "dy": "3", "stdDeviation": "2", "flood-opacity": "0.6"})
            if "glow" in effects:
                fid = f"glow-{index}"; filter_ids.append(fid)
                f = ET.SubElement(defs, "filter", id=fid)
                ET.SubElement(f, "feGaussianBlur", {"stdDeviation": "4", "result": "blur"})
        if not filter_ids:
            root.remove(defs)
        for index, layer in enumerate(template_config.text_layers):
            text = str(variables.get(layer.name, variables.get("text", "")))
            font = font_resolver(lang, layer) if font_resolver else layer.default_font
            attrs = {"x": str(layer.x), "y": str(layer.y), "fill": layer.color,
                     "font-size": str(layer.font_size), "font-family": str(font)}
            anchor = (layer.anchor or "start").lower()
            anchor_map = {"left": "start", "center": "middle", "right": "end"}
            # 复合锚点（如 "top-left"、"bottom-center"）取水平分量
            horizontal = anchor.split("-")[-1] if "-" in anchor else anchor
            attrs["text-anchor"] = anchor_map.get(horizontal, horizontal if horizontal in {"start", "middle", "end"} else "start")
            if rtl and layer.rtl_flip:
                attrs.update({"direction": "rtl", "unicode-bidi": "bidi-override"})
                if attrs["text-anchor"] == "start": attrs["text-anchor"] = "end"
                elif attrs["text-anchor"] == "end": attrs["text-anchor"] = "start"
            effects = set(layer.effects)
            if "outline" in effects:
                attrs.update({"stroke": "#000000", "stroke-width": "2", "paint-order": "stroke"})
            if "shadow" in effects: attrs["filter"] = f"url(#{f'shadow-{index}'})"
            elif "glow" in effects: attrs["filter"] = f"url(#{f'glow-{index}'})"
            text_node = ET.SubElement(root, "text", attrs)
            lines = _wrap_text(text, layer.max_width, layer.font_size, layer.max_lines)
            if len(lines) == 1:
                text_node.text = lines[0]
            else:
                text_node.text = lines[0]
                for line_no, line in enumerate(lines[1:], 1):
                    span = ET.SubElement(text_node, "tspan", {"x": str(layer.x), "dy": str(layer.font_size)})
                    span.text = line
        return ET.tostring(root, encoding="unicode")


def _estimate_width(text: str, font_size: float) -> float:
    coeff = {"cjk": 1.0, "latin": 0.55, "arabic": 0.6, "default": 0.55}
    total = 0.0
    for char in text:
        cp = ord(char)
        if (0x4E00 <= cp <= 0x9FFF or 0x3040 <= cp <= 0x30FF or 0xAC00 <= cp <= 0xD7AF): bucket = "cjk"
        elif 0x0590 <= cp <= 0x08FF or 0xFB50 <= cp <= 0xFEFF: bucket = "arabic"
        elif char.isascii() and char.isalpha(): bucket = "latin"
        else: bucket = "default"
        total += coeff[bucket] * font_size
    return total


def _wrap_text(text: str, max_width: int, font_size: int, max_lines: int) -> list[str]:
    if _estimate_width(text, font_size) <= max_width or max_lines <= 1:
        return [text]
    lines, current = [], ""
    for char in text:
        if current and _estimate_width(current + char, font_size) > max_width:
            lines.append(current); current = char
        else: current += char
    if current: lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-1] + "…" if lines[-1] else "…"
    return lines


__all__ = ["SVGTemplateEngine"]

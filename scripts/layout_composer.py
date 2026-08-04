#!/usr/bin/env python3
"""Layout Composer — 美学排版引擎。

在对底图建立整体认知（色彩方案 + 安全区可读性）之后，再对每个文字层做
编排与排版决策，而不是机械地把文字贴到配置坐标上：

1. **位置微调** —— 锚点落区可读性太差时，在同一方位内移向更干净的邻近安全区；
2. **对比度校正** —— 文字色与落点区域亮度对比不足（WCAG 简化版 < 3.0）时，
   切换为与背景相称的深/浅文字色；
3. **效果增强** —— 复杂区域自动追加 shadow / backdrop 衬底；
4. **层级排版** —— 垂直堆叠的文字层按字号比例微调行距，避免粘连。

本模块只产出 ``LayoutPlan``（调整方案的 dict），不修改原
:class:`~config_loader.TemplateConfig`；渲染端（``text_renderer``）把方案
应用到图层副本上，``batch_pipeline`` 把 ``adjustments`` 汇总进报告。
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

try:
    # ``scripts`` 不是包：兼容 scripts/ 已在 sys.path 的直接导入方式
    from image_analyzer import (
        _compute_readability_score,
        analyze_color_scheme,
        analyze_safe_zones,
    )
except ImportError:  # pragma: no cover - exercised when imported differently
    _SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
    if _SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, _SCRIPTS_DIR)
    from image_analyzer import (  # noqa: E402
        _compute_readability_score,
        analyze_color_scheme,
        analyze_safe_zones,
    )


# ---------------------------------------------------------------------------
# 阈值与常量
# ---------------------------------------------------------------------------

READABILITY_POOR = 40.0      # 低于此分：考虑位置微调 + backdrop 衬底
READABILITY_BUSY = 70.0      # 40-70：复杂区域，必要时追加 shadow
CONTRAST_MIN = 3.0           # WCAG 简化版对比度下限
MOVE_LIMIT_RATIO = 0.15      # 位置微调幅度上限（占画布比例）

DARK_TEXT = "#1a1a1a"        # 亮底推荐文字色
LIGHT_TEXT = "#f5f5f5"       # 暗底推荐文字色

_H_ANCHORS = {"left": "start", "start": "start", "center": "middle",
              "middle": "middle", "right": "end", "end": "end"}
_V_ANCHORS = {"top": "top", "center": "middle", "middle": "middle",
              "bottom": "bottom"}


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------


def _parse_anchor(anchor: str) -> Tuple[str, str]:
    """解析（可能是复合的）锚点为 (vertical, horizontal)。"""
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


def _hex_to_rgb(color: str) -> Tuple[int, int, int]:
    v = str(color or "").strip().lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    if len(v) < 6:
        return (255, 255, 255)
    try:
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    except ValueError:
        return (255, 255, 255)


def _rel_luminance(rgb: Tuple[int, int, int]) -> float:
    """WCAG 简化版相对亮度（0-1，省略 gamma 线性化）。"""
    r, g, b = (c / 255.0 for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(rgb_a: Tuple[int, int, int], rgb_b: Tuple[int, int, int]) -> float:
    la, lb = _rel_luminance(rgb_a), _rel_luminance(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _layer_band(vertical: str, horizontal: str) -> Tuple[str, str]:
    """锚点分量换算为方位带：top/center/bottom × left/center/right。"""
    v = vertical if vertical in ("top", "middle", "bottom") else "middle"
    v = "center" if v == "middle" else v
    h = {"start": "left", "middle": "center", "end": "right"}.get(
        horizontal, "center"
    )
    return v, h


def _zone_band(region_name: str) -> Tuple[str, str]:
    """安全区 region 名（如 ``bottom_center``）拆成方位带。"""
    parts = str(region_name or "").split("_")
    v = next((p for p in parts if p in ("top", "center", "bottom")), "center")
    h = next((p for p in reversed(parts) if p in ("left", "center", "right")), "center")
    return v, h


def _sample_region(
    img_array: np.ndarray,
    layer,
    vertical: str,
    horizontal: str,
) -> np.ndarray:
    """取文字层实际落点附近的区域（按锚点方向展开 max_width × 文本块高）。"""
    h, w = img_array.shape[:2]
    win_w = min(int(layer.max_width), w)
    win_h = max(int(layer.font_size * 1.3 * layer.max_lines), 32)

    if horizontal == "end":
        x1, x2 = layer.x - win_w, layer.x
    elif horizontal == "middle":
        x1, x2 = layer.x - win_w // 2, layer.x + win_w // 2
    else:
        x1, x2 = layer.x, layer.x + win_w
    if vertical == "bottom":
        y1, y2 = layer.y - win_h, layer.y
    elif vertical == "middle":
        y1, y2 = layer.y - win_h // 2, layer.y + win_h // 2
    else:
        y1, y2 = layer.y, layer.y + win_h

    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)
    if x2 - x1 < 4 or y2 - y1 < 4:
        # 退化窗口：取锚点附近 40x40 小片，避免空数组
        cx, cy = min(max(int(layer.x), 0), w - 1), min(max(int(layer.y), 0), h - 1)
        x1, x2 = max(0, cx - 20), min(w, cx + 20)
        y1, y2 = max(0, cy - 20), min(h, cy + 20)
    return img_array[y1:y2, x1:x2]


def _region_brightness(region: np.ndarray) -> float:
    """区域平均亮度（0-255，WCAG 权重）。"""
    if region is None or region.size == 0:
        return 255.0
    arr = region.astype(np.float32)
    if arr.ndim == 2:
        return float(np.mean(arr))
    lum = arr[..., 0] * 0.2126 + arr[..., 1] * 0.7152 + arr[..., 2] * 0.0722
    return float(np.mean(lum))


# ---------------------------------------------------------------------------
# 各项排版决策
# ---------------------------------------------------------------------------


def _adjust_position(
    layer_plan: Dict[str, Any],
    layer,
    band: Tuple[str, str],
    score: float,
    zones: List[Dict[str, Any]],
    canvas: Tuple[int, int],
) -> None:
    """可读性过低时，在同方位安全区中选得分更高者，限幅平移锚点。"""
    if score >= READABILITY_POOR or not zones:
        return
    w, h = canvas
    best = None
    for zone in zones:
        if _zone_band(zone.get("region", "")) != band:
            continue
        z_score = float(zone.get("readability_score", 0.0))
        if z_score >= READABILITY_POOR and (best is None or z_score > best[0]):
            best = (z_score, zone)
    if best is None:
        return
    z_score, zone = best
    x1, y1, x2, y2 = zone["bbox"]
    # 目标锚点：安全区中心附近（水平/垂直分量按锚点语义贴边或居中）
    vertical, horizontal = _parse_anchor(layer.anchor)
    if horizontal == "end":
        new_x = x2
    elif horizontal == "middle":
        new_x = (x1 + x2) // 2
    else:
        new_x = x1
    if vertical == "bottom":
        new_y = y2
    elif vertical == "middle":
        new_y = (y1 + y2) // 2
    else:
        new_y = y1

    # 限幅：移动不超过画布 15%，不跨方位，不越界
    max_dx, max_dy = MOVE_LIMIT_RATIO * w, MOVE_LIMIT_RATIO * h
    dx = max(-max_dx, min(max_dx, new_x - layer.x))
    dy = max(-max_dy, min(max_dy, new_y - layer.y))
    if dx == 0 and dy == 0:
        return
    layer_plan["x"] = int(round(max(0, min(w, layer.x + dx))))
    layer_plan["y"] = int(round(max(0, min(h, layer.y + dy))))
    layer_plan["adjustments"].append(
        f"位置微调：落点可读性 {score:.0f} 过低，同方位内移向安全区 "
        f"{zone.get('region')!r}（可读性 {z_score:.0f}），"
        f"({layer.x},{layer.y}) -> ({layer_plan['x']},{layer_plan['y']})"
    )


def _adjust_effects(
    layer_plan: Dict[str, Any],
    layer,
    score: float,
    brightness: float,
) -> None:
    """按落点区域复杂程度自动追加 shadow / backdrop。"""
    effects = layer_plan["effects"]
    has_readability_effect = any(
        e in effects for e in ("backdrop", "shadow", "outline")
    )
    if score < READABILITY_POOR:
        if "backdrop" not in effects:
            effects.append("backdrop")
            backdrop = "auto-dark" if brightness > 128 else "auto-light"
            layer_plan["backdrop_color"] = backdrop
            layer_plan["adjustments"].append(
                f"效果增强：落点可读性 {score:.0f} 过低，自动追加 backdrop 衬底"
                f"（{backdrop}，按区域亮度 {brightness:.0f} 选取）"
            )
    elif score < READABILITY_BUSY and not has_readability_effect:
        effects.append("shadow")
        layer_plan["adjustments"].append(
            f"效果增强：落点区域较复杂（可读性 {score:.0f}），自动追加 shadow"
        )


def _adjust_contrast(
    layer_plan: Dict[str, Any],
    layer,
    region: np.ndarray,
    brightness: float,
) -> None:
    """文字色与有效背景（区域或 backdrop）对比不足时切换深/浅文字色。"""
    text_rgb = _hex_to_rgb(layer_plan["color"])
    region_rgb = tuple(
        int(v) for v in np.mean(region.reshape(-1, region.shape[-1]), axis=0)[:3]
    ) if region is not None and region.size else (255, 255, 255)

    ratio = _contrast_ratio(text_rgb, region_rgb)
    if ratio < CONTRAST_MIN:
        new_color = DARK_TEXT if brightness > 128 else LIGHT_TEXT
        layer_plan["color"] = new_color
        layer_plan["adjustments"].append(
            f"对比度校正：文字色与落点区域对比度 {ratio:.1f} < {CONTRAST_MIN:.1f}，"
            f"按区域亮度 {brightness:.0f} 切换为 {new_color}"
        )
        text_rgb = _hex_to_rgb(new_color)

    # 有 backdrop 时，文字真正面对的是衬底而非底图，再校一次
    if "backdrop" in layer_plan["effects"]:
        backdrop = (layer_plan.get("backdrop_color") or "auto-dark").lower()
        if backdrop == "auto-dark":
            bg_rgb, bg_desc = (10, 10, 10), "深色衬底"
        elif backdrop == "auto-light":
            bg_rgb, bg_desc = (245, 245, 245), "浅色衬底"
        else:
            bg_rgb, bg_desc = _hex_to_rgb(backdrop), "衬底"
        ratio_bg = _contrast_ratio(text_rgb, bg_rgb)
        if ratio_bg < CONTRAST_MIN:
            new_color = (
                LIGHT_TEXT if _rel_luminance(bg_rgb) < 0.5 else DARK_TEXT
            )
            layer_plan["color"] = new_color
            layer_plan["adjustments"].append(
                f"对比度校正：文字色与{bg_desc}对比度 {ratio_bg:.1f} 不足，"
                f"切换为 {new_color}"
            )


def _adjust_stacking(plans: List[Dict[str, Any]], canvas: Tuple[int, int]) -> None:
    """垂直堆叠的文字层（y 差小于两行字高）按字号比例微调行距。"""
    w, h = canvas
    ordered = sorted(plans, key=lambda p: (p["y"], p["name"]))
    for i, upper in enumerate(ordered):
        for lower in ordered[i + 1:]:
            dy = lower["y"] - upper["y"]
            two_lines = upper["font_size"] + lower["font_size"]
            if dy >= two_lines:
                break  # 已按 y 排序，后面的层更远，无需再比
            # 水平方向有交叠才算堆叠
            if abs(lower["x"] - upper["x"]) > 0.4 * w:
                continue
            min_gap = int(two_lines * 0.6)
            if dy < min_gap:
                shift = min_gap - dy
                new_y = min(h, lower["y"] + shift)
                lower["adjustments"].append(
                    f"层级排版：与 {upper['name']!r} 垂直间距 {dy}px 过近，"
                    f"按字号比例下移 {new_y - lower['y']}px 避免粘连"
                )
                lower["y"] = new_y


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def compose_layout(image_path: str, template_config, lang: str = "en") -> Dict[str, Any]:
    """分析底图并为每个 text layer 产出排版调整方案（LayoutPlan）。

    返回结构::

        {
          "layers": [
            {"name", "x", "y", "color", "effects", "font_size",
             "backdrop_color"?, "adjustments": [str, ...]},
            ...
          ],
          "analysis_summary": {...},
        }

    ``adjustments`` 记录每处调整的原因，供渲染报告展示。
    """
    with Image.open(image_path) as img:
        img_array = np.array(img.convert("RGB"))
    h, w = img_array.shape[:2]

    color_scheme = analyze_color_scheme(img_array)
    try:
        zones = analyze_safe_zones(image_path)
    except Exception:
        zones = []

    layer_plans: List[Dict[str, Any]] = []
    for layer in template_config.text_layers:
        plan: Dict[str, Any] = {
            "name": layer.name,
            "x": layer.x,
            "y": layer.y,
            "color": layer.color,
            "effects": list(layer.effects or []),
            "font_size": layer.font_size,
            "adjustments": [],
        }
        if layer.backdrop_color:
            plan["backdrop_color"] = layer.backdrop_color

        vertical, horizontal = _parse_anchor(layer.anchor)
        band = _layer_band(vertical, horizontal)
        region = _sample_region(img_array, layer, vertical, horizontal)
        brightness = _region_brightness(region)
        score = _compute_readability_score(region)

        # 1) 位置微调（先于效果/对比度：落点定了，后面判断才准）
        _adjust_position(plan, layer, band, score, zones, (w, h))
        if plan["x"] != layer.x or plan["y"] != layer.y:
            # 移动后在新落点重新采样
            moved = layer.model_copy(update={"x": plan["x"], "y": plan["y"]})
            region = _sample_region(img_array, moved, vertical, horizontal)
            brightness = _region_brightness(region)
            score = _compute_readability_score(region)

        # 2) 效果增强（先于对比度：backdrop 会改变文字面对的有效背景）
        _adjust_effects(plan, layer, score, brightness)

        # 3) 对比度校正
        _adjust_contrast(plan, layer, region, brightness)

        layer_plans.append(plan)

    # 4) 层级排版（跨图层，最后统一处理）
    _adjust_stacking(layer_plans, (w, h))

    analysis_summary = {
        "image_size": [int(w), int(h)],
        "brightness": round(float(color_scheme.get("brightness", 0.0)), 1),
        "suggested_bg": color_scheme.get("suggested_bg"),
        "suggested_text_color": list(color_scheme.get("suggested_text_color", ())),
        "color_family": color_scheme.get("color_family"),
        "safe_zone_count": len(zones),
        "top_safe_zones": [
            {"region": z.get("region"), "readability_score": z.get("readability_score")}
            for z in zones[:3]
        ],
    }

    return {"layers": layer_plans, "analysis_summary": analysis_summary}


__all__ = ["compose_layout"]


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    import json

    if len(sys.argv) != 3:
        print("Usage: python layout_composer.py <base_image> <template.yaml>")
        sys.exit(2)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config_loader import load_config

    cfg = load_config(sys.argv[2])
    print(json.dumps(compose_layout(sys.argv[1], cfg), ensure_ascii=False, indent=2))

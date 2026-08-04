#!/usr/bin/env python3
"""
Image Analyzer Module
Analyzes image to find suitable areas for text placement.
"""

import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional
import colorsys

try:
    import pytesseract
    _PYTESSERACT_AVAILABLE = True
except ImportError:  # pragma: no cover - pytesseract is in requirements but guard anyway
    pytesseract = None
    _PYTESSERACT_AVAILABLE = False


def analyze_image(image_path: str, text_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main analysis function.
    Returns layout suggestions based on image content.
    """
    img = Image.open(image_path)
    img_array = np.array(img)
    
    analysis = {
        "image_size": img.size,
        "color_scheme": analyze_color_scheme(img_array),
        "safe_zones": find_safe_zones(img_array, text_requirements),
        "complexity_map": analyze_complexity(img_array),
    }
    
    # For flowcharts, detect existing structures
    if text_requirements.get("type") == "flowchart":
        analysis["detected_nodes"] = detect_flowchart_nodes(img_array)
        analysis["suggested_connections"] = suggest_connections(
            analysis["detected_nodes"], 
            text_requirements
        )
    
    return analysis


def analyze_color_scheme(img_array: np.ndarray) -> Dict[str, Any]:
    """Analyze dominant colors and suggest text colors."""
    # Reshape for analysis
    pixels = img_array.reshape(-1, 3)
    
    # Calculate average color
    avg_color = np.mean(pixels, axis=0)
    
    # Calculate brightness
    brightness = np.mean(np.dot(pixels, [0.299, 0.587, 0.114]))
    
    # Determine dominant color family
    avg_normalized = avg_color / 255.0
    h, l, s = colorsys.rgb_to_hls(*avg_normalized)
    
    color_family = "neutral"
    if s > 0.3:
        if 0 <= h < 0.08 or 0.92 <= h <= 1:
            color_family = "warm"  # Red/Orange
        elif 0.08 <= h < 0.17:
            color_family = "warm"  # Yellow
        elif 0.17 <= h < 0.42:
            color_family = "cool"  # Green
        elif 0.42 <= h < 0.75:
            color_family = "cool"  # Blue/Cyan
        else:
            color_family = "warm"  # Purple/Pink
    
    # Suggest text colors for contrast
    if brightness > 128:
        suggested_text_color = (30, 30, 30)  # Dark text
        suggested_bg = "light"
    else:
        suggested_text_color = (240, 240, 240)  # Light text
        suggested_bg = "dark"
    
    return {
        "dominant_rgb": tuple(avg_color.astype(int)),
        "brightness": float(brightness),
        "color_family": color_family,
        "suggested_text_color": suggested_text_color,
        "suggested_bg": suggested_bg,
    }


def find_safe_zones(img_array: np.ndarray, text_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find safe zones for text placement.
    Safe zones are areas with low visual complexity (smooth colors, few edges).
    """
    height, width = img_array.shape[:2]
    
    # Divide image into grid
    grid_size = 8
    cell_h = height // grid_size
    cell_w = width // grid_size
    
    safe_zones = []
    
    for row in range(grid_size):
        for col in range(grid_size):
            y1 = row * cell_h
            y2 = min((row + 1) * cell_h, height)
            x1 = col * cell_w
            x2 = min((col + 1) * cell_w, width)
            
            cell = img_array[y1:y2, x1:x2]
            
            # Calculate complexity (standard deviation of colors)
            complexity = np.std(cell)
            
            # Determine if this is a safe zone
            if complexity < 30:  # Low complexity threshold
                # Calculate position name
                v_pos = "top" if row < 2 else "bottom" if row > 5 else "center"
                h_pos = "left" if col < 2 else "right" if col > 5 else "center"
                
                position_name = f"{v_pos}_{h_pos}" if v_pos != h_pos else v_pos
                
                safe_zones.append({
                    "bbox": (x1, y1, x2, y2),
                    "position_name": position_name,
                    "complexity": float(complexity),
                    "area": (x2 - x1) * (y2 - y1),
                    "avg_color": tuple(np.mean(cell, axis=(0, 1)).astype(int)),
                    # Backward compatible addition: readability_score 0-100
                    # 平坦度越高（亮度方差、饱和度方差、边缘密度越低）分数越高
                    "readability_score": _compute_readability_score(cell),
                })
    
    # Sort by area (largest first) and complexity (lowest first)
    safe_zones.sort(key=lambda z: (-z["area"], z["complexity"]))
    
    return safe_zones[:6]  # Return top 6 safe zones


def analyze_complexity(img_array: np.ndarray) -> np.ndarray:
    """
    Create a complexity heatmap of the image.
    Higher values = more edges/detail = less suitable for text.
    """
    # Simple gradient-based edge detection
    gray = np.mean(img_array, axis=2) if len(img_array.shape) == 3 else img_array
    
    # Calculate gradients
    grad_x = np.abs(np.diff(gray, axis=1, append=gray[:, -1:]))
    grad_y = np.abs(np.diff(gray, axis=0, append=gray[-1:, :]))
    
    complexity = (grad_x + grad_y) / 2
    
    return complexity


def detect_flowchart_nodes(img_array: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect potential node positions for flowcharts.
    Looks for rectangular regions, circles, or blank areas.
    """
    height, width = img_array.shape[:2]
    
    # This is a simplified version - in production would use computer vision
    # For now, divide image into potential node positions
    
    nodes = []
    num_nodes = 3  # Default
    
    # Horizontal layout (default)
    node_width = width // (num_nodes + 1)
    node_height = min(height // 3, 150)
    
    for i in range(num_nodes):
        x = (i + 1) * node_width - node_width // 2
        y = height // 2 - node_height // 2
        
        nodes.append({
            "id": f"node_{i+1}",
            "bbox": (
                max(0, x - node_width // 2),
                max(0, y),
                min(width, x + node_width // 2),
                min(height, y + node_height)
            ),
            "center": (x, y + node_height // 2),
            "type": "box",  # Could be box, diamond, circle
        })
    
    return nodes


def suggest_connections(nodes: List[Dict], text_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Suggest connection lines/arrows between nodes."""
    connections = []
    
    for i in range(len(nodes) - 1):
        start = nodes[i]["center"]
        end = nodes[i + 1]["center"]
        
        connections.append({
            "from": nodes[i]["id"],
            "to": nodes[i + 1]["id"],
            "start_point": start,
            "end_point": end,
            "type": "arrow",
        })
    
    return connections


def get_text_placement_suggestions(
    analysis: Dict[str, Any], 
    text_requirements: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate specific placement suggestions for each text group.
    """
    suggestions = []
    text_groups = text_requirements.get("text_groups", [])
    
    if text_requirements.get("type") == "flowchart":
        # Use detected nodes
        nodes = analysis.get("detected_nodes", [])
        for i, group in enumerate(text_groups):
            if i < len(nodes):
                suggestions.append({
                    "text_id": group["id"],
                    "content": group["content"],
                    "placement": {
                        "bbox": nodes[i]["bbox"],
                        "center": nodes[i]["center"],
                        "type": "centered_in_box",
                    },
                    "style_suggestions": {
                        "color": analysis["color_scheme"]["suggested_text_color"],
                        "max_width": nodes[i]["bbox"][2] - nodes[i]["bbox"][0] - 20,
                    }
                })
    else:
        # Use safe zones
        safe_zones = analysis.get("safe_zones", [])
        
        # Map semantic positions to safe zones
        position_priority = {
            "top": [z for z in safe_zones if "top" in z["position_name"]],
            "bottom": [z for z in safe_zones if "bottom" in z["position_name"]],
            "center": [z for z in safe_zones if z["position_name"] == "center"],
            "left": [z for z in safe_zones if "left" in z["position_name"]],
            "right": [z for z in safe_zones if "right" in z["position_name"]],
            "auto": safe_zones,
        }
        
        for i, group in enumerate(text_groups):
            semantic_pos = group.get("semantic_position", "auto")
            candidates = position_priority.get(semantic_pos, safe_zones)
            
            if candidates:
                zone = candidates[0]  # Best candidate
                suggestions.append({
                    "text_id": group["id"],
                    "content": group["content"],
                    "placement": {
                        "bbox": zone["bbox"],
                        "position_name": zone["position_name"],
                        "type": "overlay",
                    },
                    "style_suggestions": {
                        "color": analysis["color_scheme"]["suggested_text_color"],
                        "contrast_bg": zone["avg_color"],
                        "max_width": zone["bbox"][2] - zone["bbox"][0] - 40,
                    }
                })
    
    return suggestions


# ---------------------------------------------------------------------------
# 新增功能：可读性评分与安全区分析
# ---------------------------------------------------------------------------


# region -> suggested_for 的推荐映射，参考 references/layout_patterns.md
_REGION_TO_SUGGESTED = {
    "top_center": "title",
    "bottom_center": "caption",
    "center": "body",
    "top_left": "subtitle",
    "top_right": "subtitle",
    "bottom_left": "caption",
    "bottom_right": "caption",
    "top": "title",
    "bottom": "caption",
    "left": "body",
    "right": "body",
}


def _region_name_from_bbox(bbox: Tuple[int, int, int, int], img_shape: Tuple[int, int]) -> str:
    """
    根据 bbox 在图像中的相对位置返回语义化区域名，如 "bottom_center"。
    img_shape = (height, width)。
    """
    x1, y1, x2, y2 = bbox
    h, w = img_shape[:2]
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0

    # 垂直分带：top / center / bottom（按图像三等分）
    if cy < h / 3.0:
        v = "top"
    elif cy > 2 * h / 3.0:
        v = "bottom"
    else:
        v = "center"

    # 水平分带：left / center / right
    if cx < w / 3.0:
        h_pos = "left"
    elif cx > 2 * w / 3.0:
        h_pos = "right"
    else:
        h_pos = "center"

    if v == "center" and h_pos == "center":
        return "center"
    if v == h_pos:
        return v
    return f"{v}_{h_pos}"


def _compute_readability_score(region_array: np.ndarray) -> float:
    """
    综合「亮度均匀度 + 饱和度方差 + 边缘密度」评估区域可读性。

    三个维度得分都是「越平坦/越均匀分数越高」，按 0.4/0.3/0.3 加权后归一到 0-100。
    返回 float，保留 1 位小数。
    """
    if region_array is None or region_array.size == 0:
        return 0.0

    arr = region_array
    if arr.ndim == 3:
        # 转灰度用于亮度/边缘分析
        gray = np.mean(arr.astype(np.float32), axis=2)
        rgb = arr.astype(np.float32)
    else:
        gray = arr.astype(np.float32)
        rgb = np.stack([gray, gray, gray], axis=-1)

    # 1) 亮度均匀度：亮度方差越小分越高。用 1 - 归一方差 做线性映射。
    gray_std = float(np.std(gray))
    brightness_uniformity = max(0.0, 1.0 - gray_std / 80.0)  # std>=80 视为完全不平坦

    # 2) 饱和度方差：RGB -> HSV，统计 S 通道方差
    # 归一化到 [0,1]
    rgb_norm = np.clip(rgb / 255.0, 0.0, 1.0)
    max_c = rgb_norm.max(axis=-1)
    min_c = rgb_norm.min(axis=-1)
    sat = np.where(max_c == 0, 0.0, (max_c - min_c) / np.where(max_c == 0, 1.0, max_c))
    sat_std = float(np.std(sat))
    saturation_score = max(0.0, 1.0 - sat_std / 0.4)  # std>=0.4 视为颜色极度不均

    # 3) 边缘密度：用 numpy 梯度近似 sobel，统计平均梯度幅度
    grad_x = np.abs(np.diff(gray, axis=1, append=gray[:, -1:]))
    grad_y = np.abs(np.diff(gray, axis=0, append=gray[-1:, :]))
    edge_mean = float(np.mean(grad_x + grad_y) / 2.0)
    edge_score = max(0.0, 1.0 - edge_mean / 60.0)  # 平均梯度>=60 视为边缘密集

    combined = 0.4 * brightness_uniformity + 0.3 * saturation_score + 0.3 * edge_score
    score = round(float(np.clip(combined, 0.0, 1.0) * 100.0), 1)
    return score


def analyze_safe_zones(image_path: str, forced_zones: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    基于亮度/饱和度/边缘检测识别适合叠加文字的区域。

    输出格式与 prompt_separator 对齐：
        [
          {
            "region": "bottom_center",
            "bbox": [x1, y1, x2, y2],
            "suggested_for": "title",
            "readability_score": 87.5
          },
          ...
        ]

    参数：
        image_path: 图像文件路径。
        forced_zones: 可选。强制采用的用户区域，列表元素须包含 "bbox"。
                       传入时仍会计算 readability_score，覆盖自动分析。
    """
    img = Image.open(image_path)
    img_array = np.array(img.convert("RGB"))
    h, w = img_array.shape[:2]

    results: List[Dict[str, Any]] = []

    # 强制区域模式：直接采用用户提供的 bbox，但保持自动分析的可读性评分。
    if forced_zones:
        for zone in forced_zones:
            bbox = zone.get("bbox")
            if bbox is None:
                continue
            # 统一转成 [x1,y1,x2,y2]
            bbox_list = [int(round(v)) for v in bbox[:4]]
            x1, y1, x2, y2 = bbox_list
            # 与图像边界求交，裁剪越界部分
            x1c = max(0, min(w, x1))
            x2c = max(0, min(w, x2))
            y1c = max(0, min(h, y1))
            y2c = max(0, min(h, y2))
            if x2c <= x1c or y2c <= y1c:
                # 退化 bbox：跳过或给 0 分
                score = 0.0
            else:
                region_arr = img_array[y1c:y2c, x1c:x2c]
                score = _compute_readability_score(region_arr)

            region = zone.get("region") or _region_name_from_bbox(
                (x1c, y1c, x2c, y2c), (h, w)
            )
            suggested = zone.get("suggested_for") or _REGION_TO_SUGGESTED.get(region, "body")
            results.append({
                "region": region,
                "bbox": [x1c, y1c, x2c, y2c],
                "suggested_for": suggested,
                "readability_score": score,
            })
        return results

    # 自动模式：与 find_safe_zones 思路一致（8x8 网格），但按可读性分数选 Top N。
    grid_size = 8
    cell_h = h // grid_size
    cell_w = w // grid_size

    candidates: List[Dict[str, Any]] = []
    for row in range(grid_size):
        for col in range(grid_size):
            y1 = row * cell_h
            y2 = min((row + 1) * cell_h, h) if row < grid_size - 1 else h
            x1 = col * cell_w
            x2 = min((col + 1) * cell_w, w) if col < grid_size - 1 else w

            cell = img_array[y1:y2, x1:x2]
            if cell.size == 0:
                continue

            complexity = float(np.std(cell))
            score = _compute_readability_score(cell)

            # 候选门槛：复杂度低且可读性不至于太糟
            if complexity < 60 and score >= 30.0:
                region = _region_name_from_bbox((x1, y1, x2, y2), (h, w))
                suggested = _REGION_TO_SUGGESTED.get(region, "body")
                candidates.append({
                    "region": region,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "suggested_for": suggested,
                    "readability_score": score,
                    "_complexity": complexity,
                })

    # 按可读性降序排，取前 6 个；若不足则全部返回
    candidates.sort(key=lambda z: -z["readability_score"])
    top = candidates[:6]
    for z in top:
        z.pop("_complexity", None)
    results = top

    # 如果一张图完全没找到候选（例如极端复杂），至少返回整图的中心区域，避免空列表
    if not results:
        cx1, cy1 = w // 4, h // 4
        cx2, cy2 = 3 * w // 4, 3 * h // 4
        score = _compute_readability_score(img_array[cy1:cy2, cx1:cx2])
        results.append({
            "region": "center",
            "bbox": [cx1, cy1, cx2, cy2],
            "suggested_for": "body",
            "readability_score": score,
        })

    return results


def detect_existing_text(image_path: str) -> Dict[str, Any]:
    """
    使用 pytesseract 对底图做 OCR 检测，判断是否存在残留文字。

    返回：
        {
          "has_text": bool | None,        # None 表示不可用
          "detected_text": [str, ...],    # 识别到的非空文本片段
          "warning": str | None           # 不可用/失败时的说明
        }

    优雅降级：tesseract 二进制缺失或任何异常都不会抛错，返回 has_text=None + warning。
    """
    if not _PYTESSERACT_AVAILABLE:
        return {
            "has_text": None,
            "detected_text": [],
            "warning": "OCR unavailable: pytesseract is not installed.",
        }

    try:
        img = Image.open(image_path)
        # 让 pytesseract 处理 RGB，避免 RGBA/P 通道报错
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        # 设超时，避免大图卡死（仅 pytesseract 0.3.10+ 支持）
        try:
            raw_text = pytesseract.image_to_string(img, timeout=10)
        except TypeError:
            # 旧版 pytesseract 不接受 timeout
            raw_text = pytesseract.image_to_string(img)
    except pytesseract.TesseractNotFoundError as e:
        return {
            "has_text": None,
            "detected_text": [],
            "warning": f"OCR unavailable: tesseract binary not found ({e})",
        }
    except pytesseract.TesseractError as e:
        return {
            "has_text": None,
            "detected_text": [],
            "warning": f"OCR unavailable: tesseract error ({e})",
        }
    except Exception as e:  # 兜底：图像格式损坏、权限等
        return {
            "has_text": None,
            "detected_text": [],
            "warning": f"OCR unavailable: {type(e).__name__}: {e}",
        }

    # 清洗：去掉空白行、纯空白片段
    fragments = [line.strip() for line in raw_text.splitlines()]
    detected = [f for f in fragments if f]

    return {
        "has_text": bool(detected),
        "detected_text": detected,
        "warning": None,
    }


if __name__ == "__main__":
    # Test with a sample image
    import sys
    if len(sys.argv) > 1:
        test_req = {
            "type": "single_or_few",
            "text_groups": [{"id": "t1", "content": "Test", "semantic_position": "center"}]
        }
        result = analyze_image(sys.argv[1], test_req)
        print(result)

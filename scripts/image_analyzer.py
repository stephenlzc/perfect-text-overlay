#!/usr/bin/env python3
"""
Image Analyzer Module
Analyzes image to find suitable areas for text placement.
"""

import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple
import colorsys


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

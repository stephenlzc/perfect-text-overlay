#!/usr/bin/env python3
"""
Text Renderer Module
Renders text onto images with professional typography effects.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Tuple, Optional
import os


def render_text_on_image(
    image_path: str,
    output_path: str,
    placements: List[Dict[str, Any]],
    user_choices: Dict[str, Any]
) -> str:
    """
    Main rendering function.
    Renders all text groups onto the image.
    """
    # Load image
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # Process each text placement
    for placement in placements:
        render_single_text(draw, img, placement, user_choices)
    
    # Draw connections for flowcharts
    if user_choices.get("show_connections"):
        connections = user_choices.get("connections", [])
        for conn in connections:
            draw_connection(draw, conn, user_choices)
    
    # Convert to RGB for saving (remove alpha)
    final_img = img.convert("RGB")
    final_img.save(output_path, quality=95)
    
    return output_path


def render_single_text(
    draw: ImageDraw.Draw,
    img: Image.Image,
    placement: Dict[str, Any],
    user_choices: Dict[str, Any]
):
    """Render a single text element."""
    text = placement["content"]
    bbox = placement["placement"]["bbox"]
    
    # Get font
    font = get_font(
        font_name=user_choices.get("font_style", "default"),
        size=calculate_font_size(bbox, text, user_choices),
        is_title=placement.get("is_title", False)
    )
    
    # Get colors
    text_color = user_choices.get("text_color") or placement["style_suggestions"]["color"]
    if isinstance(text_color, str):
        text_color = parse_color(text_color)
    
    # Calculate position
    text_position = calculate_text_position(
        bbox, text, font, draw, 
        placement["placement"]["type"]
    )
    
    # Get effects
    effects = user_choices.get("effects", [])
    
    # Draw background box if requested
    if "box" in effects or user_choices.get("add_boxes"):
        draw_text_box(draw, bbox, user_choices)
    
    # Draw effects
    if "shadow" in effects:
        shadow_color = (0, 0, 0, 128) if isinstance(img, Image.Image) else (0, 0, 0)
        shadow_offset = user_choices.get("shadow_offset", (3, 3))
        draw.text(
            (text_position[0] + shadow_offset[0], text_position[1] + shadow_offset[1]),
            text,
            font=font,
            fill=shadow_color
        )
    
    if "outline" in effects or "stroke" in effects:
        stroke_color = (255, 255, 255) if sum(text_color) < 384 else (0, 0, 0)
        stroke_width = user_choices.get("stroke_width", 2)
        draw.text(
            text_position,
            text,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color
        )
    else:
        # Normal text
        draw.text(text_position, text, font=font, fill=text_color)


def get_font(font_name: str, size: int, is_title: bool = False) -> ImageFont.FreeTypeFont:
    """Load appropriate font."""
    # Font mapping - 优先使用 assets/fonts/ 目录下的免费商用字体
    # 所有字体均为 SIL OFL 或 Apache 2.0 授权，可免费商用
    font_paths = {
        # 简体中文 - 思源黑体 (Noto Sans CJK SC)
        "modern": [
            "NotoSansCJKsc-Bold.otf",      # 思源黑体简体 Bold (SIL OFL)
            "NotoSansCJK-Bold.ttc",
            "SourceHanSans-Bold.ttc",
            "simhei.ttf",
            "Microsoft YaHei.ttf",
            "Arial.ttf",
        ],
        # 简体中文 - 思源宋体 (Noto Serif CJK SC)
        "traditional": [
            "NotoSerifCJKsc-Bold.otf",     # 思源宋体简体 Bold (SIL OFL)
            "NotoSerifCJK-Regular.ttc",
            "SourceHanSerif-Regular.ttc",
            "simsun.ttc",
            "SimSun.ttf",
        ],
        # 繁体中文 - 思源黑体繁体 (Noto Sans CJK TC)
        "traditional_tw": [
            "NotoSansCJKtc-Bold.otf",      # 思源黑体繁体 Bold (SIL OFL)
            "NotoSansCJKtc-Regular.otf",
            "Microsoft JhengHei.ttf",
        ],
        # 书法/艺术字体
        "calligraphy": [
            "STXingkai.ttf",
            "华文行楷.ttf",
            "SIMKAI.ttf",
            "KaiTi.ttf",
        ],
        # 卡通/可爱风格
        "cartoon": [
            "NotoSansCJKsc-Bold.otf",
            "simhei.ttf",
            "Microsoft YaHei.ttf",
            "Arial.ttf",
        ],
        # 英文字体
        "english": [
            "Roboto-Bold.ttf",             # Roboto Bold (Apache 2.0)
            "OpenSans-Bold.ttf",           # Open Sans Bold (SIL OFL)
            "Arial.ttf",
            "Helvetica.ttf",
        ],
        # 韩文字体
        "korean": [
            "NotoSansCJKkr-Bold.otf",      # 思源黑体韩文 Bold (SIL OFL)
            "NotoSansCJKkr-Regular.otf",
            "Malgun Gothic.ttf",
        ],
        # 默认回退
        "default": [
            "NotoSansCJKsc-Bold.otf",      # 简体中文优先
            "NotoSansCJKtc-Bold.otf",      # 繁体中文
            "Roboto-Bold.ttf",             # 英文
            "OpenSans-Bold.ttf",
            "Arial.ttf",
            "DejaVuSans.ttf",
        ],
    }
    
    # Adjust size for titles
    if is_title:
        size = int(size * 1.2)
    
    # Try to load requested font
    candidates = font_paths.get(font_name, font_paths["default"])
    
    # Get skill directory
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_fonts_dir = os.path.join(skill_dir, "assets", "fonts")
    
    # 收集所有错误信息
    errors = []
    
    for font_file in candidates:
        # Check assets/fonts directory first
        font_path = os.path.join(assets_fonts_dir, font_file)
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                errors.append(f"assets/{font_file}: {e}")
                continue
        
        # Try system fonts - 扩展搜索路径
        system_paths = [
            # Linux
            f"/usr/share/fonts/truetype/{font_file}",
            f"/usr/share/fonts/truetype/noto/{font_file}",
            f"/usr/share/fonts/truetype/dejavu/{font_file}",
            f"/usr/share/fonts/opentype/noto/{font_file}",
            f"/usr/share/fonts/{font_file}",
            # macOS
            f"/System/Library/Fonts/{font_file}",
            f"/System/Library/Fonts/Supplemental/{font_file}",
            f"/Library/Fonts/{font_file}",
            f"~/Library/Fonts/{font_file}",
            # Windows
            f"C:/Windows/Fonts/{font_file}",
            f"C:/Windows/Fonts/msyh/{font_file}",
        ]
        for sys_path in system_paths:
            expanded_path = os.path.expanduser(sys_path)
            if os.path.exists(expanded_path):
                try:
                    return ImageFont.truetype(expanded_path, size)
                except Exception as e:
                    errors.append(f"system/{font_file}: {e}")
                    continue
    
    # Try to find any available system font as last resort
    import subprocess
    try:
        # Try fc-list on Linux/macOS
        result = subprocess.run(['fc-list', ':family'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Find a suitable font from system
            common_fonts = ['Arial', 'DejaVu Sans', 'Noto Sans', 'Helvetica', 'sans-serif']
            for family in common_fonts:
                try:
                    # Try to load by family name
                    font = ImageFont.truetype(family, size)
                    return font
                except:
                    continue
    except:
        pass
    
    # Final fallback to default
    print(f"[WARN] Could not load any suitable font. Using default. Errors: {errors[:3]}")
    return ImageFont.load_default()


def calculate_font_size(bbox: Tuple[int, int, int, int], text: str, user_choices: Dict[str, Any]) -> int:
    """Calculate appropriate font size for the bounding box."""
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    
    # Base size calculation
    text_length = len(text)
    if text_length <= 4:
        base_size = min(width // 2, height // 2)
    elif text_length <= 10:
        base_size = min(width // 4, height // 3)
    elif text_length <= 20:
        base_size = min(width // 6, height // 4)
    else:
        base_size = min(width // 10, height // 5)
    
    # Apply user preference
    size_preference = user_choices.get("text_size", "auto")
    if size_preference == "large":
        base_size = int(base_size * 1.3)
    elif size_preference == "small":
        base_size = int(base_size * 0.7)
    
    # Constrain
    return max(12, min(base_size, 200))


def calculate_text_position(
    bbox: Tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.Draw,
    placement_type: str
) -> Tuple[int, int]:
    """Calculate text position within bounding box."""
    # Get text size
    bbox_text = draw.textbbox((0, 0), text, font=font)
    text_width = bbox_text[2] - bbox_text[0]
    text_height = bbox_text[3] - bbox_text[1]
    
    box_width = bbox[2] - bbox[0]
    box_height = bbox[3] - bbox[1]
    
    if placement_type == "centered_in_box":
        # Center in box
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[1] + (box_height - text_height) // 2
    elif placement_type == "top":
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[1] + 10
    elif placement_type == "bottom":
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[3] - text_height - 10
    else:
        # Default: center
        x = bbox[0] + (box_width - text_width) // 2
        y = bbox[1] + (box_height - text_height) // 2
    
    return (x, y)


def draw_text_box(draw: ImageDraw.Draw, bbox: Tuple[int, int, int, int], user_choices: Dict[str, Any]):
    """Draw background box for text."""
    padding = 10
    box_bbox = (
        bbox[0] + padding,
        bbox[1] + padding,
        bbox[2] - padding,
        bbox[3] - padding
    )
    
    # Box color
    box_color = user_choices.get("box_color", (255, 255, 255, 180))
    if isinstance(box_color, str):
        box_color = parse_color(box_color, alpha=180)
    
    # Draw rounded rectangle
    draw.rounded_rectangle(box_bbox, radius=8, fill=box_color)


def draw_connection(draw: ImageDraw.Draw, conn: Dict[str, Any], user_choices: Dict[str, Any]):
    """Draw connection line/arrow between nodes."""
    start = conn["start_point"]
    end = conn["end_point"]
    
    line_color = user_choices.get("line_color", (100, 100, 100))
    if isinstance(line_color, str):
        line_color = parse_color(line_color)
    
    line_width = user_choices.get("line_width", 3)
    
    # Draw line
    draw.line([start, end], fill=line_color, width=line_width)
    
    # Draw arrow head
    draw_arrow_head(draw, start, end, line_color, line_width + 2)


def draw_arrow_head(draw: ImageDraw.Draw, start: Tuple[int, int], end: Tuple[int, int], color: Tuple[int, ...], size: int):
    """Draw arrow head at the end of a line."""
    import math
    
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    
    arrow_angle = math.pi / 6  # 30 degrees
    arrow_len = size * 3
    
    # Calculate arrow points
    x1 = end[0] - arrow_len * math.cos(angle - arrow_angle)
    y1 = end[1] - arrow_len * math.sin(angle - arrow_angle)
    x2 = end[0] - arrow_len * math.cos(angle + arrow_angle)
    y2 = end[1] - arrow_len * math.sin(angle + arrow_angle)
    
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color)


def parse_color(color_str: str, alpha: Optional[int] = None) -> Tuple[int, ...]:
    """Parse color string to RGB/RGBA tuple."""
    color_map = {
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "gold": (255, 215, 0),
        "gray": (128, 128, 128),
    }
    
    color_str_lower = color_str.lower()
    if color_str_lower in color_map:
        rgb = color_map[color_str_lower]
    elif color_str.startswith("#"):
        # Hex color
        hex_color = color_str.lstrip("#")
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    else:
        rgb = (0, 0, 0)  # Default black
    
    if alpha is not None:
        return (*rgb, alpha)
    return rgb


if __name__ == "__main__":
    # Test rendering
    print("Text renderer module loaded")
    print("Available functions: render_text_on_image, get_font, calculate_font_size")

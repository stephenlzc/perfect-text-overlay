#!/usr/bin/env python3
"""
Prompt Separator Module
Separates user prompt into image-only prompt and text requirements.

Supports an optional ``scene_type`` to inject scene-specific guidance
(safe zones and composition instructions) into the image prompt.

Supported scene types:
- product_main: main e-commerce product listing image
- banner: horizontal web/advertising banner
- poster: vertical event/promotion poster
- social: square social media post

Also exposes ``generate_ecommerce_prompt`` to build an English, pure
image-generation prompt for e-commerce listings, with platform-specific
constraints appended (unknown platforms fall back to ``general``).
"""

import re
import json
from typing import List, Dict, Any, Optional


# Scene configuration: safe zones (0-1 normalized bbox) and composition
# instructions that are idempotently appended to the image prompt.
SCENE_CONFIG: Dict[str, Dict[str, Any]] = {
    "product_main": {
        "safe_zones": [
            {"bbox": [0.0, 0.85, 1.0, 1.0], "label": "bottom_caption_area"},
        ],
        "instruction": (
            "Place the product in the upper 85% of the frame. "
            "Keep the bottom 15% clean for caption and price overlay."
        ),
    },
    "banner": {
        "safe_zones": [
            {"bbox": [0.0, 0.0, 1.0, 0.2], "label": "top_title_area"},
            {"bbox": [0.0, 0.8, 1.0, 1.0], "label": "bottom_cta_area"},
        ],
        "instruction": (
            "Keep the top 20% and bottom 20% clean for title and "
            "call-to-action overlay. Place key visual elements in the middle band."
        ),
    },
    "poster": {
        "safe_zones": [
            {"bbox": [0.0, 0.0, 1.0, 0.15], "label": "top_title_area"},
            {"bbox": [0.0, 0.85, 1.0, 1.0], "label": "bottom_footer_area"},
        ],
        "instruction": (
            "Keep the top 15% and bottom 15% clean for title and footer overlay. "
            "Place the main visual content in the middle 70%."
        ),
    },
    "social": {
        "safe_zones": [
            {"bbox": [0.1, 0.4, 0.9, 0.6], "label": "center_text_area"},
        ],
        "instruction": (
            "Keep the central horizontal band clean for text overlay. "
            "Place key visual elements around the edges."
        ),
    },
}


# Platform-specific constraints appended to e-commerce prompts.
PLATFORM_CONSTRAINTS: Dict[str, List[str]] = {
    "amazon": [
        "product fills at least 85% of the frame",
        "pure white background (#FFFFFF)",
        "no text, logos, watermarks, or props",
        "soft even studio lighting",
        "sharp focus, high resolution, 2000x2000 or larger",
    ],
    "shopify": [
        "clean product photography",
        "lifestyle or contextual setting",
        "natural soft lighting",
        "high resolution, sharp focus",
    ],
    "ebay": [
        "product clearly visible and centered",
        "neutral light background",
        "good lighting with minimal shadows",
        "high resolution",
    ],
    "tmall": [
        "product fills the frame",
        "pure white background",
        "no text or logos",
        "studio lighting",
    ],
    "general": [
        "clean professional product photography",
        "even lighting with minimal shadows",
        "high resolution, sharp focus",
    ],
}


def _scene_marker(scene_type: str) -> str:
    """Return a unique marker used to detect prior scene injection."""
    return f"[scene:{scene_type}]"


def _inject_scene_instruction(image_prompt: str, scene_type: str) -> str:
    """Append the scene instruction to image_prompt once (idempotent)."""
    config = SCENE_CONFIG.get(scene_type)
    if not config:
        return image_prompt
    marker = _scene_marker(scene_type)
    if marker in image_prompt:
        return image_prompt
    base = image_prompt.rstrip(" ,.;:\n\t")
    return f"{base} {marker} {config['instruction']}"


def extract_text_mentions(prompt: str) -> List[Dict[str, Any]]:
    """
    Extract text mentions from the prompt.
    Returns list of text items with position info.
    """
    text_items = []

    # 定义引号字符：英文双引号、英文单引号、中文双引号、中文单引号、反引号
    # 使用 Unicode 转义避免语法问题
    QUOTES = '\x22\x27\u201c\u201d\u2018\u2019`'

    # Pattern 1: "写着'xxx'" / "标题是'xxx'" / "加上'xxx'文字"
    # 支持中英文引号
    # 使用 (?:...) 分组避免重复捕获，更精确地匹配中文语境
    patterns_cn = [
        r'(?:标题|主题)[是为写][:：]?\s*[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'写[着为][:：]?\s*[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'加[上入][:：]?\s*[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']?[文]?字?',
        r'文[字内容][:：]?\s*[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'显[示][:：]?\s*[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'标注[:：]?\s*[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
    ]

    # Pattern 2: English patterns - 更通用的模式
    # 支持多种介词和连接词来捕获多个文本
    patterns_en = [
        r'\btext[:\s]+[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'\btitle[:\s]+[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'\bcaption[:\s]+[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'\b(?:with|and|or)\s+[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
        r'\bsay(?:ing)?[:\s]+[' + QUOTES + r']([^' + QUOTES + r']+)[' + QUOTES + r']',
    ]

    seen_contents = set()  # 用于去重

    for pattern in patterns_cn + patterns_en:
        matches = re.finditer(pattern, prompt, re.IGNORECASE)
        for match in matches:
            text_content = match.group(1).strip()
            # 去重：相同内容只保留一次
            if text_content and len(text_content) > 1 and text_content not in seen_contents:
                seen_contents.add(text_content)
                # Determine semantic position from context
                position = infer_position(prompt, match.start())
                text_items.append({
                    "content": text_content,
                    "position": position,
                    "start_idx": match.start(),
                    "end_idx": match.end()
                })

    # Pattern 3: Numbered/bulleted lists for flowcharts
    # e.g., "1.xxx 2.xxx" or "包含：1.xxx 2.xxx"
    # 注意：只使用第一个匹配的模式，避免重复提取
    list_pattern = r'(?:包含|步骤|流程|如[下下]|步骤[:：])?\s*[:：]?\s*(?:\n)?\s*(\d+[.、]\s*[^\d\n]+(?:\n?\s*\d+[.、]\s*[^\d\n]+)*)'

    matches = re.finditer(list_pattern, prompt)
    for match in matches:
        list_text = match.group(1)
        steps = re.findall(r'\d+[.、]\s*([^\d\n]+)', list_text)
        for i, step in enumerate(steps, 1):
            step_clean = step.strip()
            if step_clean:
                text_items.append({
                    "content": step_clean,
                    "position": f"step_{i}",
                    "semantic_type": "flowchart_node",
                    "start_idx": match.start(),
                    "end_idx": match.end()
                })

    return text_items


def infer_position(prompt: str, match_start: int) -> str:
    """Infer text position from surrounding context."""
    context_start = max(0, match_start - 50)
    context = prompt[context_start:match_start].lower()

    position_keywords = {
        "top": ["顶部", "上方", "上面", "header", "top", "upper", "above"],
        "bottom": ["底部", "下方", "下面", "footer", "bottom", "lower", "below"],
        "center": ["中间", "中心", "中央", "center", "middle"],
        "left": ["左侧", "左", "左边", "left"],
        "right": ["右侧", "右", "右边", "right"],
        "top_left": ["左上", "top left", "upper left"],
        "top_right": ["右上", "top right", "upper right"],
        "bottom_left": ["左下", "bottom left", "lower left"],
        "bottom_right": ["右下", "bottom right", "lower right"],
    }

    for position, keywords in position_keywords.items():
        if any(kw in context for kw in keywords):
            return position

    # Default: center for single text, sequential for multiple
    return "auto"


def create_image_prompt(original_prompt: str, text_items: List[Dict]) -> str:
    """
    Create image-only prompt by removing text descriptions.
    Replace with visual equivalents.
    """
    image_prompt = original_prompt

    # Remove text mentions
    for item in sorted(text_items, key=lambda x: x["start_idx"], reverse=True):
        # Get the full match text
        full_match = original_prompt[item["start_idx"]:item["end_idx"]]

        # Replace with visual description or remove
        replacement = get_visual_replacement(item, original_prompt)
        image_prompt = image_prompt[:item["start_idx"]] + replacement + image_prompt[item["end_idx"]:]

    # Clean up and enhance
    image_prompt = clean_prompt(image_prompt)
    image_prompt = enhance_prompt(image_prompt)

    return image_prompt


def get_visual_replacement(item: Dict, original_prompt: str) -> str:
    """Get visual replacement for text mention."""
    semantic_type = item.get("semantic_type", "")

    if semantic_type == "flowchart_node":
        return "a blank node box"

    # For single text, replace with generic description
    replacements = {
        "top": "blank header area at top",
        "bottom": "blank footer area at bottom",
        "center": "blank central focal area",
        "left": "blank area on the left side",
        "right": "blank area on the right side",
        "auto": "blank area suitable for text overlay",
    }

    return replacements.get(item["position"], "blank area for text")


def clean_prompt(prompt: str) -> str:
    """Clean up the prompt."""
    # Remove extra whitespace
    prompt = re.sub(r'\s+', ' ', prompt)
    # Remove duplicate commas/spaces
    prompt = re.sub(r',\s*,', ',', prompt)
    prompt = re.sub(r'\s+,', ',', prompt)
    # Remove leading/trailing punctuation
    prompt = prompt.strip(' ,.:;')
    return prompt


def enhance_prompt(prompt: str) -> str:
    """Add quality enhancements to image prompt."""
    enhancements = [
        "high quality",
        "professional",
        "clean composition",
        "suitable for text overlay"
    ]

    # Check if already has quality terms
    existing_terms = ['high quality', '4k', '8k', 'professional', 'hd']
    has_quality = any(term in prompt.lower() for term in existing_terms)

    if not has_quality:
        prompt += ", " + ", ".join(enhancements)

    return prompt


def create_text_requirements(text_items: List[Dict], original_prompt: str) -> Dict[str, Any]:
    """Create structured text requirements."""
    # Determine if this is a flowchart/diagram scenario
    is_flowchart = any(
        item.get("semantic_type") == "flowchart_node"
        for item in text_items
    )

    requirements = {
        "type": "flowchart" if is_flowchart else "single_or_few",
        "text_groups": [],
        "style_hints": extract_style_hints(original_prompt),
    }

    for i, item in enumerate(text_items):
        group = {
            "id": f"text_{i+1}",
            "content": item["content"],
            "semantic_position": item["position"],
            "node_type": item.get("semantic_type", "text_block"),
        }
        requirements["text_groups"].append(group)

    return requirements


def extract_style_hints(prompt: str) -> Dict[str, Any]:
    """Extract style hints from prompt."""
    hints = {
        "color": None,
        "font_style": None,
        "size": None,
    }

    # Color hints
    color_keywords = {
        "red": ["红色", "red", "红"],
        "blue": ["蓝色", "blue", "蓝"],
        "green": ["绿色", "green", "绿"],
        "gold": ["金色", "gold", "金"],
        "white": ["白色", "white", "白"],
        "black": ["黑色", "black", "黑"],
    }

    prompt_lower = prompt.lower()
    for color, keywords in color_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            hints["color"] = color
            break

    # Font style hints
    font_keywords = {
        "calligraphy": ["书法", "手写", "calligraphy", "handwritten"],
        "modern": ["现代", "简约", "modern", "minimalist"],
        "cartoon": ["卡通", "可爱", "cartoon", "cute"],
        "traditional": ["传统", "古典", "traditional", "classic"],
    }

    for style, keywords in font_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            hints["font_style"] = style
            break

    return hints


def separate_prompt(prompt: str, scene_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to separate prompt into image and text parts.

    Args:
        prompt: The original user prompt.
        scene_type: Optional scene type. One of
            ``product_main``, ``banner``, ``poster``, ``social``.
            When provided, the returned dict includes ``scene_type`` and
            ``safe_zones`` (a list of 0-1 normalized bbox dicts), and the
            scene composition instruction is appended (idempotently) to
            ``image_prompt``. When ``scene_type`` is ``None`` (default),
            ``scene_type`` is ``None`` and ``safe_zones`` is ``[]``.

    Returns:
        Dict with keys: ``has_text``, ``image_prompt``, ``text_requirements``
        (or ``None``), ``original_text_items``, ``scene_type``, ``safe_zones``.
    """
    # Extract text mentions
    text_items = extract_text_mentions(prompt)

    # Resolve scene configuration
    if scene_type is not None and scene_type in SCENE_CONFIG:
        scene_cfg = SCENE_CONFIG[scene_type]
        # Deep-copy safe_zones (bbox list + label) so callers cannot mutate SCENE_CONFIG
        safe_zones = [
            {"bbox": list(zone["bbox"]), "label": zone["label"]}
            for zone in scene_cfg["safe_zones"]
        ]
    else:
        safe_zones = []

    if not text_items:
        image_prompt = prompt
        if scene_type is not None and scene_type in SCENE_CONFIG:
            image_prompt = _inject_scene_instruction(image_prompt, scene_type)
        return {
            "has_text": False,
            "image_prompt": image_prompt,
            "text_requirements": None,
            "scene_type": scene_type,
            "safe_zones": safe_zones,
        }

    # Create image-only prompt
    image_prompt = create_image_prompt(prompt, text_items)

    # Inject scene instruction idempotently
    if scene_type is not None and scene_type in SCENE_CONFIG:
        image_prompt = _inject_scene_instruction(image_prompt, scene_type)

    # Create text requirements
    text_requirements = create_text_requirements(text_items, prompt)

    return {
        "has_text": True,
        "image_prompt": image_prompt,
        "text_requirements": text_requirements,
        "original_text_items": text_items,
        "scene_type": scene_type,
        "safe_zones": safe_zones,
    }


def generate_ecommerce_prompt(
    product_description: str,
    scene_type: str = 'product_main',
    platform: str = 'amazon',
) -> str:
    """
    Generate an English pure-image prompt for e-commerce product photography.

    The output describes the visual content only (no text overlay) and
    appends scenario-specific composition guidance plus platform-specific
    constraints. Unknown platforms fall back to ``general``.

    Args:
        product_description: Free-form description of the product.
        scene_type: One of ``product_main``, ``banner``, ``poster``,
            ``social``. Unknown values are ignored (no scene instruction
            is appended).
        platform: Target platform such as ``amazon``, ``shopify``,
            ``ebay``, ``tmall``. Unknown values fall back to ``general``.

    Returns:
        English image-generation prompt string with platform constraints
        appended.
    """
    # Normalize platform
    platform_key = (platform or "").lower().strip()
    if platform_key not in PLATFORM_CONSTRAINTS:
        platform_key = "general"

    # Build base description
    desc = (product_description or "").strip().rstrip(" ,.;:\n\t")
    if not desc:
        desc = "a product"

    parts = [desc]

    # Add scene-based composition instruction (if known)
    scene_cfg = SCENE_CONFIG.get(scene_type)
    if scene_cfg:
        parts.append(scene_cfg["instruction"])

    # Append platform-specific constraints
    parts.extend(PLATFORM_CONSTRAINTS[platform_key])

    return ", ".join(parts)


if __name__ == "__main__":
    # ---- Original three demos (kept verbatim) ----
    test_prompts = [
        "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围",
        "创建一个用户注册流程图，包含：1.填写信息 2.验证邮箱 3.注册成功",
        "Design a poster with 'Summer Sale' at the top and '50% Off' at the bottom",
    ]

    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Original: {prompt}")
        result = separate_prompt(prompt)
        print(f"\nImage Prompt: {result['image_prompt']}")
        print(f"\nText Requirements:")
        print(json.dumps(result['text_requirements'], indent=2, ensure_ascii=False))

    # ---- Extended demo 1: scene_type support & idempotent injection ----
    print(f"\n{'='*60}")
    print("Extended demo: scene_type + safe_zones + idempotent injection")

    # 1a) scene_type=None still works (backward compatible)
    none_result = separate_prompt(test_prompts[0])
    assert none_result["scene_type"] is None, "scene_type should be None by default"
    assert none_result["safe_zones"] == [], "safe_zones should be [] when scene_type is None"
    print(f"\n[scene_type=None] scene_type={none_result['scene_type']}, "
          f"safe_zones={none_result['safe_zones']}")

    # 1b) each supported scene_type injects once and is idempotent
    for scene in ["product_main", "banner", "poster", "social"]:
        first = separate_prompt(test_prompts[0], scene_type=scene)
        second = separate_prompt(first["image_prompt"], scene_type=scene)
        third = separate_prompt(second["image_prompt"], scene_type=scene)
        print(f"\n[scene_type={scene}]")
        print(f"  safe_zones: {first['safe_zones']}")
        print(f"  has_text: {first['has_text']}")
        print(f"  idempotent (3 calls): {first['image_prompt'] == second['image_prompt'] == third['image_prompt']}")
        print(f"  image_prompt: {first['image_prompt']}")

    # 1c) safe_zones use 0-1 normalized bbox
    for scene in ["product_main", "banner", "poster", "social"]:
        res = separate_prompt(test_prompts[0], scene_type=scene)
        for zone in res["safe_zones"]:
            bb = zone["bbox"]
            assert len(bb) == 4 and all(0.0 <= v <= 1.0 for v in bb), \
                f"bbox must be 4 floats in [0,1]: {bb}"
        print(f"  [bbox-check] {scene}: OK -> {res['safe_zones']}")

    # ---- Extended demo 2: generate_ecommerce_prompt ----
    print(f"\n{'='*60}")
    print("Extended demo: generate_ecommerce_prompt")

    product_desc = "A minimalist ceramic coffee mug with matte finish"
    for platform in ["amazon", "shopify", "ebay", "tmall", "unknown_platform"]:
        prompt = generate_ecommerce_prompt(product_desc, platform=platform)
        print(f"\n[platform={platform}]")
        print(f"  {prompt}")

    # 2a) different scene_type
    poster_prompt = generate_ecommerce_prompt(
        product_desc, scene_type="poster", platform="amazon"
    )
    print(f"\n[scene=poster, platform=amazon]")
    print(f"  {poster_prompt}")

    # 2b) unknown platform falls back to general
    fallback = generate_ecommerce_prompt(product_desc, platform="myspace")
    assert "clean professional product photography" in fallback, \
        "Unknown platform should fall back to general constraints"
    print(f"\n[platform=myspace -> general fallback] OK")
    print(f"  {fallback}")

# GenImageText

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Fix imperfect AI-generated text in images by separating image generation and text overlay.

![GenImageText Hero](assets/hero.png)

🌐 **English** | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## Overview

AI-generated images often contain garbled or imperfect text, especially for Chinese, Japanese, Korean (CJK) and other non-Latin scripts. This tool solves this problem by separating image generation and text rendering into two distinct steps:

1. **Separate** prompt → image-only prompt + text requirements
2. **Generate** clean base image (using your AI tool)
3. **Analyze** image for optimal text placement zones
4. **Render** perfect text with professional typography

---

## For AI Agents (Natural Language Installation)

Copy and paste this prompt to your LLM agent (Claude Code, Kimi Code, Cursor, etc.):

```
Install the GenImageText skill to my workspace.
Clone from: https://github.com/stephenlzc/GenImageText
Set up all dependencies and verify the installation by running a test with Chinese text extraction.
```

---

## Installation

### Requirements
- Python 3.8+
- Python packages: `pip install Pillow numpy`

### Git Clone

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
```

---

## Usage

### Step 1: Separate Prompt

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("Movie poster with 'Interstellar' title")
# result['image_prompt']: Clean visual description without text
# result['text_requirements']: Structured text data
```

### Step 2: Generate Base Image

Use the `image_prompt` with your preferred AI image generator (DALL-E, Midjourney, Stable Diffusion, etc.)

### Step 3: Analyze Image

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### Step 4: Render Text

```python
from scripts.text_renderer import render_text_on_image

output_path = render_text_on_image(
    image_path="base_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices={
        "font_style": "modern",
        "effects": ["shadow", "outline"]
    }
)
```

---

## Font Handling

Fonts are loaded with the following priority:

1. **User-provided font path**: If specified
2. **Skill assets**: Check `assets/fonts/` directory
3. **System fonts**: Search common system font directories
4. **Fallback**: Default PIL font

### Font Recommendations by Language

#### 简体中文 (Simplified Chinese)
| Font File | Font Name | Style | Best For |
|-----------|-----------|-------|----------|
| `NotoSansCJKsc-Bold.otf` | 思源黑体 Bold | Modern | Posters, tech style, business |
| `NotoSerifCJKsc-Bold.otf` | 思源宋体 Bold | Traditional | Cultural themes, formal documents |

#### 繁體中文 (Traditional Chinese)
| Font File | Font Name | Style | Best For |
|-----------|-----------|-------|----------|
| `NotoSansCJKtc-Bold.otf` | 思源黑體 Bold | Modern | Taiwan/Hong Kong, business docs |

#### 한국어 (Korean)
| Font File | Font Name | Style | Best For |
|-----------|-----------|-------|----------|
| `NotoSansCJKkr-Bold.otf` | 본고딕 Bold | Modern | Korean posters, modern design |

#### English / Latin
| Font File | Font Name | Style | Best For |
|-----------|-----------|-------|----------|
| `Roboto-Bold.ttf` | Roboto Bold | Modern | Tech posters, clean designs |
| `OpenSans-Bold.ttf` | Open Sans Bold | Humanist | Web content, versatile use |

### Download Fonts

You can manually download fonts from Google Fonts or Noto Fonts and place them in `assets/fonts/`:

- **Noto CJK Fonts**: https://www.google.com/get/noto/
- **Roboto**: https://fonts.google.com/specimen/Roboto
- **Open Sans**: https://fonts.google.com/specimen/Open+Sans

All fonts are free for commercial use under SIL Open Font License or Apache License 2.0.

---

## Project Structure

```
GenImageText/
├── scripts/                # Python scripts
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # Fonts directory
└── references/             # Reference materials
```

---

## License

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 Languages

- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔  
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

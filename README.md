# Perfect Text Overlay

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Fix imperfect AI-generated text in images by separating image generation and text overlay.

🌐 **English** | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## Overview

AI-generated images often contain garbled or imperfect text, especially for Chinese, Japanese, Korean (CJK) and other non-Latin scripts. This skill solves this problem by separating image generation and text rendering into two distinct steps:

1. **Generate a clean base image** without text
2. **Analyze optimal text placement zones**
3. **Render text** with professional typography and effects

## Features

- 🎯 **Multi-language Support**: Chinese (Simplified/Traditional), Japanese, Korean, English
- 🖼️ **Multiple Image Types**: Posters, flowcharts, infographics, social media graphics
- ✨ **Professional Typography**: Shadows, outlines, background boxes
- 🔤 **Free Commercial Fonts**: Includes 6 open-source fonts (SIL OFL / Apache 2.0)
- 🎨 **Smart Layout Analysis**: Automatic safe zone detection for text placement

## For AI Agents (Natural Language Installation)

Copy and paste this prompt to your LLM agent (Claude Code, Kimi Code, Cursor, etc.):

```
Install the perfect-text-overlay skill to my workspace. 
Clone from: https://github.com/stephenlzc/perfect-text-overlay
Set up all dependencies and verify the installation by running a test with Chinese text extraction.
```

## Workflow

```
Step 1: Prompt Separation
├─ Extract text requirements from user prompt
├─ Generate image-only prompt (no text descriptions)
└─ Output: Image Prompt + Text Requirements

Step 2: Image Generation
├─ Generate base image using image-only prompt
└─ Output: Clean image without text

Step 3: Image Analysis
├─ Analyze image for safe text placement zones
├─ Detect layout structure (for flowcharts)
└─ Output: Layout suggestions with coordinates

Step 4: User Customization
├─ Ask user 5 questions for customization
│  1. Scene Type (poster/flowchart/infographic)
│  2. Text Content Confirmation
│  3. Font Style Selection
│  4. Text Position Preference
│  5. Effects and Style Options
└─ Output: User Choices

Step 5: Text Overlay
├─ Render text with professional typography
└─ Output: Final image with perfect text
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd perfect-text-overlay

# Install dependencies
pip install Pillow numpy

# Optional: Install additional system fonts
# macOS: Fonts are automatically detected
# Linux: sudo apt-get install fonts-noto-cjk
# Windows: Fonts are automatically detected
```

## Usage

### Basic Example

```python
from scripts.prompt_separator import separate_prompt
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions
from scripts.text_renderer import render_text_on_image

# Step 1: Separate prompt
user_input = "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围"
result = separate_prompt(user_input)

# result['image_prompt']: "A festive Chinese New Year promotional poster..."
# result['text_requirements']: {"text_groups": [{"content": "新春大促，全场5折起"}]}

# Step 2: Generate base image (using your preferred image generator)
# ... generate image using result['image_prompt'] ...

# Step 3: Analyze image
text_requirements = result['text_requirements']
analysis = analyze_image("generated_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)

# Step 4: User choices (normally collected via UI)
user_choices = {
    "font_style": "modern",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "text_color": (255, 215, 0),  # Gold
}

# Step 5: Render text
output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices=user_choices
)
```

### Font Styles

The following font styles are supported:

| Style | Font | Language | License |
|-------|------|----------|---------|
| `modern` | Noto Sans CJK SC Bold | Simplified Chinese | SIL OFL 1.1 |
| `traditional` | Noto Serif CJK SC Bold | Simplified Chinese | SIL OFL 1.1 |
| `traditional_tw` | Noto Sans CJK TC Bold | Traditional Chinese (Taiwan) | SIL OFL 1.1 |
| `korean` | Noto Sans CJK KR Bold | Korean | SIL OFL 1.1 |
| `english` | Roboto Bold | English/Latin | Apache 2.0 |
| `cartoon` | Noto Sans CJK SC Bold | Universal | SIL OFL 1.1 |
| `calligraphy` | System fonts | System dependent | Varies |

## Project Structure

```
perfect-text-overlay/
├── assets/
│   └── fonts/              # Free commercial fonts
│       ├── NotoSansCJKsc-Bold.otf
│       ├── NotoSerifCJKsc-Bold.otf
│       ├── NotoSansCJKtc-Bold.otf
│       ├── NotoSansCJKkr-Bold.otf
│       ├── Roboto-Bold.ttf
│       ├── OpenSans-Bold.ttf
│       └── LICENSE.md
├── references/
│   ├── trigger_keywords.md    # Multi-language trigger keywords
│   ├── layout_patterns.md     # Typography best practices
│   └── flowchart_symbols.md   # Flowchart design standards
├── scripts/
│   ├── prompt_separator.py    # Extract text from prompts
│   ├── image_analyzer.py      # Analyze image layouts
│   └── text_renderer.py       # Render text on images
├── SKILL.md                   # Detailed skill documentation
└── README.md                  # This file
```

## Supported Use Cases

### 1. Poster with Title
```
User: "Generate a sci-fi movie poster with title 'Interstellar'"
↓
Step 1: Image prompt = "sci-fi movie poster, space theme..."
        Text = "Interstellar"
↓
Step 2: Generate base image
↓
Step 3: Suggest bottom center placement
↓
Step 4: Modern font, bottom center, shadow+outline
↓
Step 5: Render large title at bottom
```

### 2. Flowchart
```
User: "Create user registration flowchart: 1. Fill info 2. Verify email 3. Complete"
↓
Step 1: Detect flowchart nodes
↓
Step 2: Generate base image
↓
Step 3: Detect 3 node positions
↓
Step 4: Horizontal flow, add boxes+arrows
↓
Step 5: Render 3 boxed nodes with connecting arrows
```

### 3. Infographic
```
User: "Create infographic with 'Sales: $100K' and 'Growth: +50%'"
↓
Step 1: Extract data points
↓
Step 2: Generate base image
↓
Step 3: Find safe zones for each statistic
↓
Step 4: Large numbers, contrasting colors
↓
Step 5: Render professional data visualization
```

## API Reference

### Prompt Separator

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("Create poster with title 'Hello World'")
# Returns: {
#     "has_text": True,
#     "image_prompt": "Create poster...",
#     "text_requirements": {...}
# }
```

### Image Analyzer

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### Text Renderer

```python
from scripts.text_renderer import render_text_on_image

render_text_on_image(
    image_path="input.png",
    output_path="output.png",
    placements=[...],
    user_choices={...}
)
```

## Trigger Keywords

This skill triggers when user input contains:

- **Image type keywords**: poster, flowchart, infographic, banner, etc.
- **Text requirement keywords**: write, title, text, caption, etc.

See [references/trigger_keywords.md](references/trigger_keywords.md) for complete multi-language keyword lists.

## Font Licenses

All included fonts are free for commercial use:

- **Noto Sans/Serif CJK**: SIL Open Font License 1.1
- **Roboto**: Apache License 2.0
- **Open Sans**: SIL Open Font License 1.1

See [assets/fonts/LICENSE.md](assets/fonts/LICENSE.md) for full license details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Noto Fonts](https://github.com/notofonts/noto-cjk) by Google & Adobe
- [Roboto](https://github.com/googlefonts/roboto) by Google
- [Open Sans](https://github.com/googlefonts/opensans) by Google

---

**Read this in other languages:**
[简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

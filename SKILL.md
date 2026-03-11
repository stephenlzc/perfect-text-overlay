---
name: GenImageText
description: Fix imperfect AI-generated text in images by separating image generation and text overlay. Use when user wants to create images with Chinese or English text, especially for posters, social media graphics, flowcharts, diagrams, or any image requiring precise text placement. Triggers on keywords like "生成海报", "create poster", "流程图", "flowchart", "带文字的图片", "image with text", and when text content is specified.
---

# GenImageText

This skill solves the common problem of AI-generated images having imperfect or garbled text (especially Chinese characters) by separating the image generation and text overlay into two distinct steps.

## When to Use This Skill

Trigger this skill when:
1. User requests an image with specific text content
2. Keywords match: poster creation, flowcharts, diagrams, social media graphics
3. User mentions text to be included: "写'xxx'", "标题是", "with 'xxx' text", "saying 'xxx'"

## Workflow Overview

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

Step 4: Text Overlay
        ├─ Ask user 5 questions for customization
        ├─ Render text with professional typography
        └─ Output: Final image with perfect text
```

## Installation

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
pip install Pillow numpy
```

## Step 1: Separate Prompt

Use `scripts/prompt_separator.py` to extract text requirements.

### Example

**User Input:**
> "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围"

**Execution:**
```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt(user_input)
# result['image_prompt']: "A festive Chinese New Year promotional poster, vibrant red and gold color scheme, traditional lanterns and plum blossoms decoration, celebration atmosphere, high quality, professional, clean composition, suitable for text overlay"
# result['text_requirements']: {"type": "single_or_few", "text_groups": [{"id": "text_1", "content": "新春大促，全场5折起", "semantic_position": "auto"}]}
```

**Output:**
- `image_prompt`: Clean visual description without text
- `text_requirements`: Structured text data with content and position hints

## Step 2: Generate Base Image

Generate image using the image-only prompt. User can use:
- External AI image generators (DALL-E, Midjourney, Stable Diffusion)
- Local generation tools
- Provide their own image

Save the generated image and proceed to Step 3.

## Step 3: Analyze Image Layout

Use `scripts/image_analyzer.py` to find optimal text placement.

### Example

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("generated_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

**Output includes:**
- Safe zones for text (low complexity areas)
- Color scheme analysis
- Suggested text colors for contrast
- Flowchart node positions (if applicable)
- Connection line suggestions

## Step 4: Ask User Questions

Before rendering, ask user 5 questions to customize the output:

### Question 1: Scene Type
> **"请选择您的图片类型："**
> - [ ] 海报/封面（单组/少量文字，强调视觉）
> - [ ] 流程图/步骤图（多组文字，强调逻辑顺序）
> - [ ] 信息图/数据图（多组文字，强调信息呈现）
> - [ ] 示意图/标注图（多组文字，强调说明）
> - [ ] 其他：（请描述）

### Question 2: Text Content Confirmation

**For single/few text:**
> "请确认文字内容：'[自动提取的内容]'"
> - [ ] 内容正确
> - [ ] 需要修改：（请填写完整内容）

**For flowchart/multiple text:**
> "检测到多组文字，请确认："
> 
> | 序号 | 文字内容 |
> |-----|---------|
> | 1 | [内容1] |
> | 2 | [内容2] |
> 
> - [ ] 全部正确
> - [ ] 修改第___号：（新内容）

### Question 3: Font Style

**根据用户语言自动推荐合适的字体：**

#### For 简体中文用户：
> **"请选择字体风格："**
> - [ ] **现代简约**（思源黑体 - 适合：海报标题、科技风格、商务场景）⭐推荐
> - [ ] **传统书法**（思源宋体 - 适合：文化主题、书籍封面、正式文档）
> - [ ] **可爱卡通**（适合：儿童、趣味、轻松场景）
> - [ ] **艺术手写**（适合：个人、温馨、创意场景）
> - [ ] **其他**：（自定义字体路径）

#### For 繁體中文用户：
> **"請選擇字體風格："**
> - [ ] **現代簡約**（思源黑體繁體 - 適合：海報標題、商務文件）⭐推薦
> - [ ] **傳統書法**（適合：文化主題、正式場合）
> - [ ] **可愛卡通**（適合：兒童、趣味場景）
> - [ ] **藝術手寫**（適合：個人、溫馨場景）
> - [ ] **其他**：（自定義字體路徑）

#### For Korean users:
> **"폰트 스타일을 선택하세요:"**
> - [ ] **모던/현대적** (본고딕 - 한국어 최적화, 비즈니스/현대 디자인) ⭐추천
> - [ ] **전통적** (전통 주제, 공식 문서)
> - [ ] **귀여운/카툰** (어린이, 재미있는 스타일)
> - [ ] **아티스틱** (개인적, 창의적 작품)
> - [ ] **기타**: (커스텀 폰트 경로)

#### For English users:
> **"Please select font style:"**
> - [ ] **Modern/Minimalist** (Roboto - clean, tech, business) ⭐Recommended
> - [ ] **Traditional/Elegant** (Open Sans - formal, readable)
> - [ ] **Playful/Cartoon** (fun, children-friendly)
> - [ ] **Artistic/Handwritten** (personal, creative)
> - [ ] **Other**: (custom font path)

### Question 4: Text Position
> **"请选择文字位置："**
> - [ ] 顶部居中（标题风格）
> - [ ] 底部居中（电影海报风格）
> - [ ] 中心位置（强调重点）
> - [ ] 自动检测最佳位置
> - [ ] 自定义：（如"右上角避开人脸"、"左侧竖排"）

**For flowcharts:**
> - [ ] 水平流程（左→右）
> - [ ] 垂直流程（上→下）
> - [ ] 分支结构
> - [ ] 精确控制：（描述连接关系）

### Question 5: Effects and Style
> **"请选择文字效果（可多选）："**
> - [ ] 添加阴影（增加立体感）
> - [ ] 添加描边（增强可读性）
> - [ ] 半透明背景框（确保清晰）
> - [ ] 添加框线（流程图节点）
> - [ ] 添加连接箭头（流程图）
> - [ ] 不需要特效
>
> **额外要求：**（如"金色渐变文字"、"品牌色#FF5733"）

## Step 5: Render Text Overlay

Use `scripts/text_renderer.py` to add text to image.

### Example

```python
from scripts.text_renderer import render_text_on_image

user_choices = {
    "font_style": "modern",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "show_connections": True,
}

output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices=user_choices
)
```

## Reference Materials

- **Trigger Keywords**: See `references/trigger_keywords.md` for complete list
- **Layout Patterns**: See `references/layout_patterns.md` for typography best practices
- **Flowchart Symbols**: See `references/flowchart_symbols.md` for diagram standards

## Common Scenarios

### Scenario 1: Poster with Title
```
User: "生成一张电影海报，标题写'星际穿越'，科幻风格"
↓
Step 1: Image prompt = "sci-fi movie poster, space theme, futuristic, cinematic, high quality"
        Text = "星际穿越", position = auto
↓
Step 2: Generate base image
↓
Step 3: Analyze → suggest bottom center placement
↓
Step 4: User choices → modern font, bottom center, shadow+outline
↓
Step 5: Render with large title text at bottom
```

### Scenario 2: Flowchart
```
User: "创建一个用户注册流程图：1.填写信息 2.验证邮箱 3.完成"
↓
Step 1: Image prompt = "clean workflow diagram, professional blue scheme, minimalist"
        Text groups = 3 nodes with sequential positions
↓
Step 2: Generate base image
↓
Step 3: Detect 3 node positions, suggest horizontal flow
↓
Step 4: User choices → modern font, horizontal flow, add boxes+arrows
↓
Step 5: Render 3 boxed nodes with connecting arrows
```

## Font Handling

The skill uses `scripts/text_renderer.py` with the following priority:

1. **User-provided font path**: If specified in Question 3
2. **Skill assets**: Check `assets/fonts/` directory
3. **System fonts**: Search common system font directories
4. **Fallback**: Default PIL font

### Font Recommendations by Language

#### 简体中文 (Simplified Chinese)

| 风格 | 字体文件 | 字体名称 | 适用场景 |
|------|---------|---------|---------|
| **现代** ⭐ | `NotoSansCJKsc-Bold.otf` | 思源黑体 Bold | 海报标题、科技风格、商务场景 |
| **传统** | `NotoSerifCJKsc-Bold.otf` | 思源宋体 Bold | 文化主题、书籍封面、正式文档 |

**推荐映射:**
- 现代简约 → `NotoSansCJKsc-Bold.otf`
- 传统书法 → `NotoSerifCJKsc-Bold.otf`

#### 繁體中文 (Traditional Chinese)

| 风格 | 字体文件 | 字体名称 | 适用场景 |
|------|---------|---------|---------|
| **现代** ⭐ | `NotoSansCJKtc-Bold.otf` | 思源黑體 Bold | 台灣/香港、商務文件、現代海報 |

**推荐映射:**
- 現代簡約 → `NotoSansCJKtc-Bold.otf`
- 傳統書法 → `NotoSerifCJKsc-Bold.otf` (_fallback_)

#### 한국어 (Korean)

| 스타일 | 폰트 파일 | 폰트 이름 | 용도 |
|--------|----------|----------|------|
| **모던** ⭐ | `NotoSansCJKkr-Bold.otf` | 본고딕 Bold | 한국어 포스터、비즈니스、현대 디자인 |

**추천 매핑:**
- 모던/현대적 → `NotoSansCJKkr-Bold.otf`

#### English / Latin

| Style | Font File | Font Name | Best For |
|-------|-----------|-----------|----------|
| **Modern** ⭐ | `Roboto-Bold.ttf` | Roboto Bold | Tech posters, clean designs, business |
| **Humanist** | `OpenSans-Bold.ttf` | Open Sans Bold | Web content, versatile, highly readable |

**Recommendation Mapping:**
- Modern/Minimalist → `Roboto-Bold.ttf`
- Traditional/Elegant → `OpenSans-Bold.ttf`

### Download Fonts

You can manually download fonts from Google Fonts or Noto Fonts and place them in `assets/fonts/`:

- **Noto CJK Fonts**: https://www.google.com/get/noto/
- **Roboto**: https://fonts.google.com/specimen/Roboto
- **Open Sans**: https://fonts.google.com/specimen/Open+Sans

### Built-in Font Support

All fonts in `assets/fonts/` are **free for commercial use** under SIL Open Font License or Apache License 2.0.

| 字体文件 | 字体名称 | Language | License | Size |
|---------|---------|----------|---------|------|
| `NotoSansCJKsc-Bold.otf` | 思源黑体 Bold | 简体中文 | SIL OFL 1.1 | ~16MB |
| `NotoSerifCJKsc-Bold.otf` | 思源宋体 Bold | 简体中文 | SIL OFL 1.1 | ~17MB |
| `NotoSansCJKtc-Bold.otf` | 思源黑體 Bold | 繁體中文 | SIL OFL 1.1 | ~16MB |
| `NotoSansCJKkr-Bold.otf` | 본고딕 Bold | 한국어 | SIL OFL 1.1 | ~16MB |
| `Roboto-Bold.ttf` | Roboto Bold | English | Apache 2.0 | ~170KB |
| `OpenSans-Bold.ttf` | Open Sans Bold | English | SIL OFL 1.1 | ~130KB |

### Font Style Selection

When asking the user to choose a font style (Question 3), **automatically detect the language** from their text content and recommend the appropriate font:

```python
# Detect language and recommend font
def recommend_font(text_content, user_style_choice):
    """
    Detect language and recommend appropriate font
    """
    # Check for Chinese characters
    if any('\u4e00' <= char <= '\u9fff' for char in text_content):
        # Simplified vs Traditional detection
        if is_traditional_chinese(text_content):
            return 'NotoSansCJKtc-Bold.otf'  # 繁體
        else:
            if user_style_choice == 'traditional':
                return 'NotoSerifCJKsc-Bold.otf'  # 思源宋体
            else:
                return 'NotoSansCJKsc-Bold.otf'  # 思源黑体 (default)
    
    # Check for Korean
    elif any('\uac00' <= char <= '\ud7af' for char in text_content):
        return 'NotoSansCJKkr-Bold.otf'  # 본고딕
    
    # Check for Japanese
    elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text_content):
        return 'NotoSansCJKsc-Bold.otf'  # Use Chinese font as fallback for Japanese
    
    # Default to English
    else:
        if user_style_choice == 'traditional':
            return 'OpenSans-Bold.ttf'
        else:
            return 'Roboto-Bold.ttf'  # default
```

## Output Quality Tips

1. **Contrast**: Ensure text color contrasts with background
2. **Size**: Text should be readable at thumbnail size
3. **Spacing**: Maintain safe margins from image edges
4. **Consistency**: Use consistent font styles within one image
5. **Readability**: Use shadow/outline on complex backgrounds

## Error Handling

- **No text detected**: Inform user and proceed with normal image generation
- **Font not found**: Fall back to system default, notify user
- **Text too long**: Suggest shorter text or smaller font
- **No safe zones found**: Suggest adding background box

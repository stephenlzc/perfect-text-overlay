---
name: perfect-text-overlay
description: Fix imperfect AI-generated text in images by separating image generation and text overlay. Use when user wants to create images with Chinese or English text, especially for posters, social media graphics, flowcharts, diagrams, or any image requiring precise text placement. Triggers on keywords like "生成海报", "create poster", "流程图", "flowchart", "带文字的图片", "image with text", and when text content is specified.
---

# Perfect Text Overlay

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
> **"请选择字体风格："**
> - [ ] 现代简约（推荐：科技/商务）
> - [ ] 传统书法（推荐：中式/文化）
> - [ ] 可爱卡通（推荐：儿童/趣味）
> - [ ] 艺术手写（推荐：个人/温馨）
> - [ ] 其他：（如"粗体黑体"、"细体宋体"、品牌字体路径）

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

### Built-in Font Support

All fonts in `assets/fonts/` are **free for commercial use** under SIL Open Font License or Apache License 2.0.

| 字体风格 | 字体文件 | 语言 | 授权 |
|---------|---------|------|------|
| **思源黑体 (现代)** | `NotoSansCJKsc-Bold.otf` | 简体中文 | SIL OFL 1.1 |
| **思源宋体 (传统)** | `NotoSerifCJKsc-Bold.otf` | 简体中文 | SIL OFL 1.1 |
| **思源黑体繁体** | `NotoSansCJKtc-Bold.otf` | 繁体中文(台湾) | SIL OFL 1.1 |
| **韩文字体** | `NotoSansCJKkr-Bold.otf` | 韩文 | SIL OFL 1.1 |
| **Roboto** | `Roboto-Bold.ttf` | 英文/拉丁 | Apache 2.0 |
| **Open Sans** | `OpenSans-Bold.ttf` | 英文/拉丁 | SIL OFL 1.1 |

### Font Style Selection

When asking the user to choose a font style (Question 3), map their choice to the appropriate font:

- **现代简约** → `modern` (思源黑体简体)
- **传统书法** → `traditional` (思源宋体简体)  
- **台湾繁体** → `traditional_tw` (思源黑体繁体)
- **韩文** → `korean` (Noto Sans CJK KR)
- **英文** → `english` (Roboto / Open Sans)
- **可爱卡通** → `cartoon`
- **艺术手写** → `calligraphy`

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

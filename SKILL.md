---
name: GenImageText
description: Add perfect text to AI-generated images. NOT an image generator - this skill overlays text on images created by user's AI tools (Midjourney, GPT Image 2, Stable Diffusion, Gemini, etc.). Solves garbled text in AI-generated images by separating image generation and text rendering. Triggers on keywords like "create poster", "flowchart", "image with text".
---

# GenImageText

> ⚠️ **IMPORTANT**: This skill is NOT an image generator. It adds text to images created by your AI image tools.

This skill solves the common problem of AI-generated images having imperfect or garbled text (especially CJK characters). It separates the workflow into two parts:
1. **User generates image** using their preferred AI tool (Midjourney, GPT Image 2, Stable Diffusion, Gemini, etc.)
2. **This skill adds text** to the generated image with perfect typography

## Supported AI Image Generators

This skill can work with ANY AI image generation tool, including:

| Tool | Platform | Best For |
|------|----------|----------|
| **Midjourney** | Discord | High-quality artistic images |
| **GPT Image 2** | ChatGPT, OpenAI API | Easy to use, great prompt understanding |
| **Stable Diffusion** | Local, Hugging Face, Replicate | Open-source, customizable |
| **Google Gemini/Imagen** | Google AI Studio, Gemini Pro | Integrated with Google's ecosystem |
| **Adobe Firefly** | Adobe Creative Suite | Commercial use, safe for business |
| **Microsoft Bing Image Creator** | Bing, Microsoft Designer | Free, powered by GPT Image |
| **Flux.1** | API, Local | High-quality open-source model |
| **Leonardo.ai** | Web, App | Game assets, concept art |
| **Ideogram** | Web | Text rendering in images |
| **Playground AI** | Web | Free tier available |

**Key Point**: Step 2 (Image Generation) uses YOUR AI tool. This skill handles Steps 1, 3, 4, 5.

## When to Use This Skill

Use this skill when:
1. User wants to add text to an AI-generated image
2. AI-generated image has garbled text that needs to be fixed
3. Keywords match: poster with text, flowcharts, diagrams, social media graphics with captions
4. User mentions text to be included: "write 'xxx'", "title is", "with 'xxx' text", "saying 'xxx'"

## Workflow Overview

```
Step 1: Prompt Separation        ← This Skill
        ├─ Extract text requirements from user prompt
        ├─ Generate image-only prompt (no text descriptions)
        └─ Output: Image Prompt + Text Requirements

Step 2: Image Generation         ← USER'S AI TOOL ⭐
        ├─ User generates base image using their preferred AI
        │  (Midjourney, GPT Image 2, Stable Diffusion, Gemini, etc.)
        ├─ Use the "image-only prompt" from Step 1
        └─ Output: Clean image without text

Step 3: Image Analysis           ← This Skill
        ├─ Analyze the AI-generated image for safe text placement zones
        ├─ Detect layout structure (for flowcharts)
        └─ Output: Layout suggestions with coordinates

Step 4: Ask User Questions       ← This Skill
        ├─ Ask user 5 questions for customization
        └─ Output: User preferences

Step 5: Text Overlay             ← This Skill
        ├─ Render perfect text on the AI-generated image
        └─ Output: Final image with perfect text
```

**Key Point**: Steps 1, 3, 4, 5 use this skill. Step 2 uses user's own AI image generator.

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
> "Create a Chinese New Year promotional poster with title 'Spring Festival Sale, Up to 50% Off', red festive atmosphere"

**Execution:**
```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt(user_input)
# result['image_prompt']: "A festive Chinese New Year promotional poster, vibrant red and gold color scheme, traditional lanterns and plum blossoms decoration, celebration atmosphere, high quality, professional, clean composition, suitable for text overlay"
# result['text_requirements']: {"type": "single_or_few", "text_groups": [{"id": "text_1", "content": "Spring Festival Sale, Up to 50% Off", "semantic_position": "auto"}]}
```

**Output:**
- `image_prompt`: Clean visual description without text
- `text_requirements`: Structured text data with content and position hints

## Step 2: Generate Base Image (User's AI Tool)

> ⚠️ **This step uses USER'S own AI image generator, NOT this skill.**

Use the `image_prompt` from Step 1 to generate the base image using:
- **Midjourney** - Discord-based AI image generation
- **GPT Image 2** (ChatGPT Plus, OpenAI API) - OpenAI's image generator
- **Stable Diffusion** - Local or web-based generation
- **Google Gemini/Imagen** - Google's AI image tool
- **Adobe Firefly** - Adobe's AI image tool
- **Microsoft Bing Image Creator** - Free, powered by GPT Image
- **Flux.1** - Open-source high-quality model
- **Other AI image generators** - Any tool the user prefers

**Important:**
- The image should contain NO text (use the cleaned prompt from Step 1)
- Save the generated image to `outputs/YYYYMMDD/` folder
- Proceed to Step 3 with the generated image

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
> **"Please select your image type:"**
> - [ ] Poster/Cover (single/few text, visual focus)
> - [ ] Flowchart/Step diagram (multiple text, logic sequence)
> - [ ] Infographic/Data chart (multiple text, information display)
> - [ ] Diagram/Annotation (multiple text, explanation)
> - [ ] Other: (please describe)

### Question 2: Text Content Confirmation

**For single/few text:**
> "Please confirm text content: '[auto-extracted content]'"
> - [ ] Content correct
> - [ ] Needs modification: (please fill in complete content)

**For flowchart/multiple text:**
> "Multiple text detected, please confirm:"
> 
> | No. | Text Content |
> |-----|-------------|
> | 1 | [Content 1] |
> | 2 | [Content 2] |
> 
> - [ ] All correct
> - [ ] Modify No.__: (new content)

### Question 3: Font Style

#### For Simplified Chinese users:
> **"Please select font style:"**
> - [ ] **Modern/Minimalist** (Source Han Sans - for: posters, tech, business) ⭐Recommended
> - [ ] **Traditional/Calligraphy** (Source Han Serif - for: cultural, formal documents)
> - [ ] **Cute/Cartoon** (for: children, fun scenes)
> - [ ] **Artistic/Handwritten** (for: personal, creative)
> - [ ] **Other**: (custom font path)

#### For Traditional Chinese users:
> **"請選擇字體風格:"**
> - [ ] **現代簡約** (Source Han Sans TC - for: Taiwan/Hong Kong, business) ⭐推薦
> - [ ] **傳統書法** (for: cultural themes, formal occasions)
> - [ ] **可愛卡通** (for: children, fun scenes)
> - [ ] **藝術手寫** (for: personal, creative)
> - [ ] **其他**: (custom font path)

#### For Korean users:
> **"폰트 스타일을 선택하세요:"**
> - [ ] **모던/현대적** (Noto Sans CJK KR - Korean optimized, business) ⭐추천
> - [ ] **전통적** (traditional themes, formal documents)
> - [ ] **귀여운/카툰** (children, fun styles)
> - [ ] **아티스틱** (personal, creative works)
> - [ ] **기타**: (custom font path)

#### For English users:
> **"Please select font style:"**
> - [ ] **Modern/Minimalist** (Roboto - clean, tech, business) ⭐Recommended
> - [ ] **Traditional/Elegant** (Open Sans - formal, readable)
> - [ ] **Playful/Cartoon** (fun, children-friendly)
> - [ ] **Artistic/Handwritten** (personal, creative)
> - [ ] **Other**: (custom font path)

### Question 4: Text Position
> **"Please select text position:"**
> - [ ] Top center (title style)
> - [ ] Bottom center (movie poster style)
> - [ ] Center (emphasis)
> - [ ] Auto-detect best position
> - [ ] Custom: (e.g., "top-right avoiding face", "left vertical")

**For flowcharts:**
> - [ ] Horizontal flow (left→right)
> - [ ] Vertical flow (top→bottom)
> - [ ] Branch structure
> - [ ] Precise control: (describe connection relationships)

### Question 5: Effects and Style
> **"Please select text effects (multiple choice):"**
> - [ ] Add shadow (3D effect)
> - [ ] Add outline (enhance readability)
> - [ ] Semi-transparent background box (ensure clarity)
> - [ ] Add border (flowchart nodes)
> - [ ] Add connection arrows (flowchart)
> - [ ] No effects
>
> **Additional requirements:** (e.g., "gold gradient text", "brand color #FF5733")

## Step 5: Render Text Overlay (This Skill)

> ✅ **This step uses this skill to add perfect text to the AI-generated image.**

Use `scripts/text_renderer.py` to overlay text on the image generated in Step 2.

### Output File Organization

All output files should be organized in the `outputs/` directory with the following structure:

```
outputs/
└── YYYYMMDD/              # Date-based subfolder (e.g., 20250312/)
    ├── YYYYMMDD_poster_final.png
    ├── YYYYMMDD_flowchart.png
    └── YYYYMMDD_infographic.png
```

**Naming Convention:**
- Folder: `outputs/YYYYMMDD/` (current date)
- Files: `YYYYMMDD_<description>.png`
- This makes it easy to manage and find files by date

### Example

```python
from scripts.text_renderer import render_text_on_image
from datetime import datetime
import os

# Generate date-based paths
today = datetime.now().strftime("%Y%m%d")
output_dir = f"outputs/{today}"
os.makedirs(output_dir, exist_ok=True)

user_choices = {
    "font_style": "modern",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "show_connections": True,
}

output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path=f"{output_dir}/{today}_poster_final.png",
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

**User Request:** "Create a movie poster with title 'Interstellar', sci-fi style"

**Workflow:**
```
Step 1 (This Skill): 
  ├─ Image prompt: "sci-fi movie poster, space theme..." (no text)
  └─ Text: "Interstellar"

Step 2 (User's AI Tool - Midjourney/GPT Image 2):
  └─ Generate base image using the prompt from Step 1

Step 3-5 (This Skill):
  ├─ Analyze the AI-generated image
  ├─ Detect best placement for title
  └─ Render "Interstellar" with perfect typography
```

### Scenario 2: Flowchart

**User Request:** "Create a user registration flowchart: 1.Fill info 2.Verify email 3.Complete"

**Workflow:**
```
Step 1 (This Skill):
  ├─ Image prompt: "clean workflow diagram, professional blue..."
  └─ Text: ["Fill info", "Verify email", "Complete"]

Step 2 (User's AI Tool):
  └─ Generate diagram image using the prompt

Step 3-5 (This Skill):
  ├─ Detect 3 node positions in the AI-generated image
  ├─ Suggest horizontal flow layout
  └─ Render 3 boxed nodes with connecting arrows and text
```

**Remember:** This skill only handles Steps 1, 3, 4, 5. Step 2 is done by user's AI image generator.

## Font Handling

The skill uses `scripts/text_renderer.py` with the following priority:

1. **User-provided font path**: If specified in Question 3
2. **Skill assets**: Check `assets/fonts/` directory
3. **System fonts**: Search common system font directories
4. **Fallback**: Default PIL font

### Font Recommendations by Language

#### Simplified Chinese

| Style | Font File | Font Name | Best For |
|-------|-----------|-----------|----------|
| **Modern** ⭐ | `NotoSansCJKsc-Bold.otf` | Source Han Sans Bold | Posters, tech, business |
| **Traditional** | `NotoSerifCJKsc-Bold.otf` | Source Han Serif Bold | Cultural, books, formal |

**Mapping:**
- Modern/Minimalist → `NotoSansCJKsc-Bold.otf`
- Traditional/Calligraphy → `NotoSerifCJKsc-Bold.otf`

#### Traditional Chinese

| Style | Font File | Font Name | Best For |
|-------|-----------|-----------|----------|
| **Modern** ⭐ | `NotoSansCJKtc-Bold.otf` | Source Han Sans TC Bold | Taiwan/Hong Kong, business |

**Mapping:**
- Modern/Minimalist → `NotoSansCJKtc-Bold.otf`
- Traditional/Calligraphy → `NotoSerifCJKsc-Bold.otf` (fallback)

#### Korean

| Style | Font File | Font Name | Best For |
|-------|-----------|-----------|----------|
| **Modern** ⭐ | `NotoSansCJKkr-Bold.otf` | Noto Sans CJK KR Bold | Korean posters, modern design |

**Mapping:**
- Modern → `NotoSansCJKkr-Bold.otf`

#### English / Latin

| Style | Font File | Font Name | Best For |
|-------|-----------|-----------|----------|
| **Modern** ⭐ | `Roboto-Bold.ttf` | Roboto Bold | Tech, clean designs |
| **Humanist** | `OpenSans-Bold.ttf` | Open Sans Bold | Web, versatile |

**Mapping:**
- Modern/Minimalist → `Roboto-Bold.ttf`
- Traditional/Elegant → `OpenSans-Bold.ttf`

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

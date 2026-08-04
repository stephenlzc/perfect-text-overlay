# GenImageText - 完美文字叠加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚠️ **重要提示**：这不是图像生成器。它为您的 AI 工具生成的图像添加完美文字。

> 通过分离图像生成和文字渲染，解决 AI 生成图像中文字错乱的问题。

![GenImageText Hero](https://raw.githubusercontent.com/stephenlzc/GenImageText/main/assets/hero_zh-CN.png)

🌐 [English](README.md) | **简体中文** | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 本工具的功能

AI 生成的图像经常包含错乱或不完美的文字，特别是对于中文、日文、韩文（CJK）等非拉丁文字。**本工具通过以下方式解决这个问题**：

1. **本技能** 分离您的提示词 → 纯图像提示词 + 文字需求
2. **您的 AI 工具** 生成干净的基础图像（Midjourney、GPT Image 2、Stable Diffusion 等）
3. **本技能** 分析图像找出最佳文字放置区域
4. **本技能** 渲染完美的文字（使用专业排版）

---

## 支持的 AI 图像生成器

第 2 步（图像生成）可以使用以下**任意**工具：

| 工具 | 平台 | 最佳用途 |
|------|------|----------|
| **Midjourney** | Discord | 高质量艺术图片 |
| **GPT Image 2** | ChatGPT、OpenAI API | 易用，prompt 理解好 |
| **Stable Diffusion** | Local、Hugging Face、Replicate | 开源，可定制 |
| **Google Gemini/Imagen** | Google AI Studio、Gemini Pro | Google 生态集成 |
| **Adobe Firefly** | Adobe Creative Suite | 商业使用安全 |
| **Microsoft Bing Image Creator** | Bing、Microsoft Designer | 免费，GPT Image 驱动 |
| **Flux.1** | API、Local | 高质量开源模型 |
| **Leonardo.ai** | Web、App | 游戏资源，概念艺术 |
| **Ideogram** | Web | 图片中文字渲染 |
| **Playground AI** | Web | 免费层可用 |

**关键点**：本技能**不生成图像**。它只给上述工具生成的图像添加文字。

---

## 自然语言安装（适用于 AI Agent）

复制并粘贴以下提示词到您的 LLM Agent（Claude Code、Kimi Code、Cursor 等）：

```
在我的工作区安装 GenImageText 技能。
从以下地址克隆：https://github.com/stephenlzc/GenImageText
设置所有依赖项，并通过运行中文文本提取测试来验证安装。
```

---

## 安装

### 环境要求
- Python 3.8+
- Python 包：`pip install Pillow numpy`

### Git 克隆

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
```

---

## 使用方法

### 步骤 1：分离提示词（本技能）

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("电影海报，标题写'星际穿越'")
# result['image_prompt']: 不含文字的纯视觉描述
# result['text_requirements']: 结构化文字数据
```

### 步骤 2：生成基础图像（您的 AI 工具）

> ⚠️ **此步骤使用您的 AI 图像生成器，不是本技能。**

使用 `image_prompt` 通过您喜欢的 AI 图像生成器生成图像：
- **Midjourney** - 基于 Discord 的生成
- **GPT Image 2**（ChatGPT Plus、OpenAI API）
- **Stable Diffusion** - 本地或云端
- **Google Gemini/Imagen**
- **Adobe Firefly**
- **Microsoft Bing Image Creator**（免费）
- **任何您喜欢的其他 AI 图像工具**

### 步骤 3：分析图像（本技能）

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 步骤 4：渲染文字（本技能）

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

## 多语言批量生成模式（电商 · 学术 · 医学）

除了上面的「单图 + 单语言」流程，本项目还内置了一套**配置驱动的多语言批量系统**——一次渲染即可生成同一张底图的多种语言成品图，覆盖电商、学术、医学等多种场景的素材制作流程。

### 核心理念

**1 张无文字底图 × 7 种语言（en / de / ja / ko / zh-CN / zh-TW / ar）→ N 张成品图**，自动批量化，无需为每个语种重复设计。

### 预设清单

| 分类 | 预设 | 场景 | 画布 |
|------|------|------|------|
| 电商 | `amazon_main_image` | 电子产品主图 | 2000x2000 |
| 电商 | `shopify_banner` | 夏季时尚横幅 | 2400x1200 |
| 电商 | `social_square` | 美妆社媒方图 | 1080x1080 |
| 电商 | `poster_a4` | 智能手表大促海报 | 2480x3508 |
| 电商 | `coffee_promo` | 咖啡餐饮促销 | 1080x1080 |
| 电商 | `home_decor_banner` | 北欧家居横幅 | 2400x1200 |
| 学术与医学 | `academic_flowchart` | 研究流程图 | 2400x1350 |
| 学术与医学 | `medical_mechanism` | 医学机制图 | 1600x2000 |

### 主要特性

- **配置驱动模板**：`presets/` 下内置 8 套开箱即用预设，每套都包含 `template.yaml` 与 7 种语言的翻译文件，简体中文与繁体中文翻译均已内置，复制即可上手。
- **美学排版引擎**（`scripts/layout_composer.py`）：自动分析底图亮度与安全区，智能微调文字位置；按底图局部对比度校正文字颜色；遇到复杂背景时自动追加衬底或投影，保证可读性。
- **丰富的文字效果**：投影、描边、发光、半透明圆角衬底，以及 `badge` 类型自动渲染的胶囊（pill）徽章，全部由 PIL 直绘（`scripts/text_renderer.py` 的 `render_layers_pil`）。
- **RTL 完整支持**：阿拉伯语经 raqm 整形后正确连接、字形正常，可放心用于中东市场素材。
- **4 路并发批量渲染**：`gen_ecommerce.py batch` 多线程并行出图，单一 CLI 即可一次产出全部语种成品。

### Quick Start

```bash
# 1. 用预设搭出一个项目骨架
.venv/bin/python gen_ecommerce.py init \
    --preset amazon_main_image \
    --project-dir projects/winter_2026

# 2. 生成无文字底图（提示词自带 no text / no watermark / no logos）
.venv/bin/python gen_ecommerce.py prompt \
    --config presets/amazon_main_image/template.yaml

# 3. 一键批量出 7 种语言的成品图到 outputs/
.venv/bin/python gen_ecommerce.py batch \
    --config presets/amazon_main_image/template.yaml \
    --base-image projects/winter_2026/base_image.png \
    --output projects/winter_2026/renders
```

> 完整 CLI（`init` / `prompt` / `validate` / `render` / `batch` / `check` 六子命令）、模板字段说明与所有预设详情，请见：
> - [README_ECOMMERCE.md](README_ECOMMERCE.md)
> - [presets/](presets/)

---

## 字体处理

字体按以下优先级加载：

1. **用户提供的字体路径**：如果指定了
2. **Skill 资源**：检查 `assets/fonts/` 目录
3. **系统字体**：搜索常见系统字体目录
4. **回退**：默认 PIL 字体

### 按语言推荐字体

#### 简体中文
| 字体文件 | 字体名称 | 风格 | 适用场景 |
|---------|---------|------|---------|
| `NotoSansCJKsc-Bold.otf` | 思源黑体 Bold | 现代 | 海报标题、科技风格、商务场景 |
| `NotoSerifCJKsc-Bold.otf` | 思源宋体 Bold | 传统 | 文化主题、书籍封面、正式文档 |

#### 繁體中文
| 字体文件 | 字体名称 | 风格 | 适用场景 |
|---------|---------|------|---------|
| `NotoSansCJKtc-Bold.otf` | 思源黑體 Bold | 现代 | 台灣/香港地區、商務文件 |

#### 韩文
| 字体文件 | 字体名称 | 风格 | 适用场景 |
|---------|---------|------|---------|
| `NotoSansCJKkr-Bold.otf` | 본고딕 Bold | 现代 | 한국어 포스터、現代적 디자인 |

#### 英文/拉丁
| 字体文件 | 字体名称 | 风格 | 适用场景 |
|---------|---------|------|---------|
| `Roboto-Bold.ttf` | Roboto Bold | 现代 | 科技海报、简洁设计 |
| `OpenSans-Bold.ttf` | Open Sans Bold | 人文 | 网页内容、通用场景 |

### 下载字体

您可以从 Google Fonts 或 Noto Fonts 手动下载字体并放入 `assets/fonts/` 目录：

- **Noto CJK 字体**：https://www.google.com/get/noto/
- **Roboto**：https://fonts.google.com/specimen/Roboto
- **Open Sans**：https://fonts.google.com/specimen/Open+Sans

所有字体均可免费商用，采用 SIL Open Font License 或 Apache License 2.0 许可。

---

## 项目结构

```
GenImageText/
├── gen_ecommerce.py         # 多场景批量 CLI（init/prompt/validate/render/batch/check）
├── scripts/                 # 核心渲染与排版模块
│   ├── text_renderer.py     # 文字绘制（PIL 直绘 + 效果）
│   ├── layout_composer.py   # 美学排版引擎（亮度/安全区/对比度分析）
│   ├── template_engine.py   # SVG / Jinja2 模板生成
│   ├── i18n_manager.py      # 多语言翻译加载
│   ├── image_analyzer.py    # 底图分析与 OCR 残留检测
│   ├── config_loader.py     # Pydantic 配置校验
│   ├── prompt_separator.py  # 提示词分离
│   └── batch_pipeline.py    # 批量渲染管线
├── presets/                 # 8 套电商、学术与医学预设（template.yaml + 7 语言翻译）
├── templates/hero/          # README hero 图模板
├── assets/fonts/            # 字体目录
├── outputs/                 # 批量渲染输出目录
└── references/              # 参考材料
```

---

## 致谢

本仓库中的所有示例底图（包括 `presets/` 下 8 套预设的样图与 README 顶部 hero 图的底图）均由同作者的姊妹项目 **[codex-image-gen](https://github.com/stephenlzc/codex-image-gen)** 生成。它通过本地 OAuth 登录 Codex CLI 免费生成图片，无需任何 API key，配合本项目即可一键完成「AI 生图 + 多语言文字叠加」的完整多场景素材流水线。强烈推荐搭配使用。

---

## 授权

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 其他语言

- [English](README.md) - English Documentation
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서
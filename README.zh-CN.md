# GenImageText - 完美文字叠加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 通过分离图像生成和文字渲染，解决 AI 生成图像中文字错乱的问题。

🌐 [English](README.md) | **简体中文** | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 功能特点

AI 生成的图像经常包含错乱或不完美的文字，特别是对于中文、日文、韩文（CJK）等非拉丁文字。本工具通过以下步骤解决这个问题：

1. **分离** 提示词 → 纯图像提示词 + 文字需求
2. **生成** 干净的基础图像（使用您的 AI 工具）
3. **分析** 图像找出最佳文字放置区域
4. **渲染** 完美的文字（使用专业排版）

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

### 步骤 1：分离提示词

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("电影海报，标题写'星际穿越'")
# result['image_prompt']: 不含文字的纯视觉描述
# result['text_requirements']: 结构化文字数据
```

### 步骤 2：生成基础图像

使用 `image_prompt` 通过您喜欢的 AI 图像生成器生成图像（DALL-E、Midjourney、Stable Diffusion 等）

### 步骤 3：分析图像

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 步骤 4：渲染文字

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
├── scripts/                # Python 脚本
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 字体目录
└── references/             # 参考材料
```

---

## 授权

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 其他语言

- [English](README.md) - English Documentation
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

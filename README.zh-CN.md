# Perfect Text Overlay - 完美文字叠加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 通过分离图像生成和文字渲染，解决 AI 生成图像中文字错乱的问题。

🌐 [English](README.md) | **简体中文** | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 概述

AI 生成的图像经常包含错乱或不完美的文字，特别是对于中文、日文、韩文（CJK）等非拉丁文字。本技能通过将图像生成和文字渲染分离为两个独立步骤来解决这个问题：

1. **生成干净的基础图像**（不含文字）
2. **分析最佳文字放置区域**
3. **渲染文字**（使用专业排版和效果）

## 功能特点

- 🎯 **多语言支持**：简体中文、繁体中文、日文、韩文、英文
- 🖼️ **多种图像类型**：海报、流程图、信息图、社交媒体图
- ✨ **专业排版**：阴影、描边、背景框
- 🔤 **免费商用字体**：包含 6 款开源字体（SIL OFL / Apache 2.0）
- 🎨 **智能布局分析**：自动检测文字放置的安全区域

## 自然语言安装（适用于 AI Agent）

复制并粘贴以下提示词到您的 LLM Agent（Claude Code、Kimi Code、Cursor 等）：

```
在我的工作区安装 perfect-text-overlay 技能。
从以下地址克隆：https://github.com/stephenlzc/perfect-text-overlay
设置所有依赖项，并通过运行中文文本提取测试来验证安装。
```

## 工作流程

```
步骤 1：提示词分离
├─ 从用户提示词中提取文字需求
├─ 生成纯图像提示词（不含文字描述）
└─ 输出：图像提示词 + 文字需求

步骤 2：图像生成
├─ 使用纯图像提示词生成基础图像
└─ 输出：干净的图像（不含文字）

步骤 3：图像分析
├─ 分析图像，找出文字放置的安全区域
├─ 检测布局结构（针对流程图）
└─ 输出：带坐标的布局建议

步骤 4：用户定制
├─ 询问用户 5 个定制问题
│  1. 场景类型（海报/流程图/信息图）
│  2. 文字内容确认
│  3. 字体风格选择
│  4. 文字位置偏好
│  5. 效果和样式选项
└─ 输出：用户选择

步骤 5：文字叠加
├─ 使用专业排版渲染文字
└─ 输出：带完美文字的最终图像
```

## 安装

```bash
# 克隆仓库
git clone <仓库地址>
cd perfect-text-overlay

# 安装依赖
pip install Pillow numpy

# 可选：安装额外系统字体
# macOS: 字体自动检测
# Linux: sudo apt-get install fonts-noto-cjk
# Windows: 字体自动检测
```

## 使用方法

### 基础示例

```python
from scripts.prompt_separator import separate_prompt
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions
from scripts.text_renderer import render_text_on_image

# 步骤 1：分离提示词
user_input = "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围"
result = separate_prompt(user_input)

# result['image_prompt']: "A festive Chinese New Year promotional poster..."
# result['text_requirements']: {"text_groups": [{"content": "新春大促，全场5折起"}]}

# 步骤 2：生成基础图像（使用您喜欢的图像生成器）
# ... 使用 result['image_prompt'] 生成图像 ...

# 步骤 3：分析图像
text_requirements = result['text_requirements']
analysis = analyze_image("generated_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)

# 步骤 4：用户选择（通常通过 UI 收集）
user_choices = {
    "font_style": "modern",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "text_color": (255, 215, 0),  # 金色
}

# 步骤 5：渲染文字
output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices=user_choices
)
```

### 字体风格

支持以下字体风格：

| 风格 | 字体 | 语言 | 授权 |
|------|------|------|------|
| `modern` | Noto Sans CJK SC Bold | 简体中文 | SIL OFL 1.1 |
| `traditional` | Noto Serif CJK SC Bold | 简体中文 | SIL OFL 1.1 |
| `traditional_tw` | Noto Sans CJK TC Bold | 繁体中文（台湾） | SIL OFL 1.1 |
| `korean` | Noto Sans CJK KR Bold | 韩文 | SIL OFL 1.1 |
| `english` | Roboto Bold | 英文/拉丁 | Apache 2.0 |
| `cartoon` | Noto Sans CJK SC Bold | 通用 | SIL OFL 1.1 |
| `calligraphy` | 系统字体 | 系统依赖 | 各异 |

## 项目结构

```
perfect-text-overlay/
├── assets/
│   └── fonts/              # 免费商用字体
│       ├── NotoSansCJKsc-Bold.otf    # 思源黑体简体
│       ├── NotoSerifCJKsc-Bold.otf   # 思源宋体简体
│       ├── NotoSansCJKtc-Bold.otf    # 思源黑体繁体
│       ├── NotoSansCJKkr-Bold.otf    # 思源黑体韩文
│       ├── Roboto-Bold.ttf           # Roboto 英文
│       ├── OpenSans-Bold.ttf         # Open Sans 英文
│       └── LICENSE.md
├── references/
│   ├── trigger_keywords.md    # 多语言触发关键词
│   ├── layout_patterns.md     # 排版最佳实践
│   └── flowchart_symbols.md   # 流程图设计标准
├── scripts/
│   ├── prompt_separator.py    # 从提示词中提取文字
│   ├── image_analyzer.py      # 分析图像布局
│   └── text_renderer.py       # 在图像上渲染文字
├── SKILL.md                   # 详细技能文档
└── README.md                  # 主文档（英文）
```

## 支持的用例

### 1. 带标题的海报
```
用户："生成一张科幻电影海报，标题写'星际穿越'"
↓
步骤 1：图像提示词 = "sci-fi movie poster, space theme..."
        文字 = "星际穿越"
↓
步骤 2：生成基础图像
↓
步骤 3：建议底部居中放置
↓
步骤 4：现代字体、底部居中、阴影+描边
↓
步骤 5：在底部渲染大标题
```

### 2. 流程图
```
用户："创建用户注册流程图：1.填写信息 2.验证邮箱 3.完成"
↓
步骤 1：检测流程图节点
↓
步骤 2：生成基础图像
↓
步骤 3：检测 3 个节点位置
↓
步骤 4：水平流程、添加方框+箭头
↓
步骤 5：渲染 3 个带连接箭头的方框节点
```

### 3. 信息图
```
用户："创建信息图，显示'销售额：10万元'和'增长：+50%'"
↓
步骤 1：提取数据点
↓
步骤 2：生成基础图像
↓
步骤 3：为每个统计数据找到安全区域
↓
步骤 4：大数字、对比色
↓
步骤 5：渲染专业数据可视化
```

## API 参考

### 提示词分离器

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("创建标题为'Hello World'的海报")
# 返回: {
#     "has_text": True,
#     "image_prompt": "Create poster...",
#     "text_requirements": {...}
# }
```

### 图像分析器

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 文字渲染器

```python
from scripts.text_renderer import render_text_on_image

render_text_on_image(
    image_path="input.png",
    output_path="output.png",
    placements=[...],
    user_choices={...}
)
```

## 触发关键词

当用户输入包含以下内容时，本技能将被触发：

- **图像类型关键词**：海报、流程图、信息图、banner 等
- **文字需求关键词**：写、标题、文字、标注、说明等

详见 [references/trigger_keywords.md](references/trigger_keywords.md) 获取完整的多语言关键词列表。

## 字体授权

所有包含的字体均可免费商用：

- **Noto Sans/Serif CJK**: SIL Open Font License 1.1
- **Roboto**: Apache License 2.0
- **Open Sans**: SIL Open Font License 1.1

详见 [assets/fonts/LICENSE.md](assets/fonts/LICENSE.md) 获取完整授权详情。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 授权

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [Noto Fonts](https://github.com/notofonts/noto-cjk) by Google & Adobe
- [Roboto](https://github.com/googlefonts/roboto) by Google
- [Open Sans](https://github.com/googlefonts/opensans) by Google

---

**其他语言版本：**
[English](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

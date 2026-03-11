# Perfect Text Overlay - 完美文字疊加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 透過分離圖像生成和文字渲染，解決 AI 生成圖像中文字錯亂的問題。

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | **繁體中文** | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 概述

AI 生成的圖像經常包含錯亂或不完美的文字，特別是對於中文、日文、韓文（CJK）等非拉丁文字。本技能透過將圖像生成和文字渲染分離為兩個獨立步驟來解決這個問題：

1. **生成乾淨的基礎圖像**（不含文字）
2. **分析最佳文字放置區域**
3. **渲染文字**（使用專業排版和效果）

## 功能特點

- 🎯 **多語言支援**：簡體中文、繁體中文、日文、韓文、英文
- 🖼️ **多種圖像類型**：海報、流程圖、資訊圖、社交媒體圖
- ✨ **專業排版**：陰影、描邊、背景框
- 🔤 **免費商用字體**：包含 6 款開源字體（SIL OFL / Apache 2.0）
- 🎨 **智慧佈局分析**：自動檢測文字放置的安全區域

## 自然語言安裝（適用於 AI Agent）

複製並貼上以下提示詞到您的 LLM Agent（Claude Code、Kimi Code、Cursor 等）：

```
在我的工作區安裝 perfect-text-overlay 技能。
從以下位址克隆：https://github.com/stephenlzc/perfect-text-overlay
設定所有依賴項，並透過執行繁體中文文本提取測試來驗證安裝。
```

## 工作流程

```
步驟 1：提示詞分離
├─ 從使用者提示詞中提取文字需求
├─ 生成純圖像提示詞（不含文字描述）
└─ 輸出：圖像提示詞 + 文字需求

步驟 2：圖像生成
├─ 使用純圖像提示詞生成基礎圖像
└─ 輸出：乾淨的圖像（不含文字）

步驟 3：圖像分析
├─ 分析圖像，找出文字放置的安全區域
├─ 檢測佈局結構（針對流程圖）
└─ 輸出：帶座標的佈局建議

步驟 4：使用者定製
├─ 詢問使用者 5 個定製問題
│  1. 場景類型（海報/流程圖/資訊圖）
│  2. 文字內容確認
│  3. 字體風格選擇
│  4. 文字位置偏好
│  5. 效果和樣式選項
└─ 輸出：使用者選擇

步驟 5：文字疊加
├─ 使用專業排版渲染文字
└─ 輸出：帶完美文字的最終圖像
```

## 安裝

```bash
# 克隆倉庫
git clone <倉庫位址>
cd perfect-text-overlay

# 安裝依賴
pip install Pillow numpy

# 可選：安裝額外系統字體
# macOS: 字體自動檢測
# Linux: sudo apt-get install fonts-noto-cjk
# Windows: 字體自動檢測
```

## 使用方法

### 基礎示例

```python
from scripts.prompt_separator import separate_prompt
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions
from scripts.text_renderer import render_text_on_image

# 步驟 1：分離提示詞
user_input = "製作一張春節促銷海報，標題寫'新春大促，全場5折起'，要有紅色的喜慶氛圍"
result = separate_prompt(user_input)

# result['image_prompt']: "A festive Chinese New Year promotional poster..."
# result['text_requirements']: {"text_groups": [{"content": "新春大促，全場5折起"}]}

# 步驟 2：生成基礎圖像（使用您喜歡的圖像生成器）
# ... 使用 result['image_prompt'] 生成圖像 ...

# 步驟 3：分析圖像
text_requirements = result['text_requirements']
analysis = analyze_image("generated_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)

# 步驟 4：使用者選擇（通常透過 UI 收集）
user_choices = {
    "font_style": "traditional_tw",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "text_color": (255, 215, 0),  # 金色
}

# 步驟 5：渲染文字
output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices=user_choices
)
```

### 字體風格

支援以下字體風格：

| 風格 | 字體 | 語言 | 授權 |
|------|------|------|------|
| `modern` | Noto Sans CJK SC Bold | 簡體中文 | SIL OFL 1.1 |
| `traditional` | Noto Serif CJK SC Bold | 簡體中文 | SIL OFL 1.1 |
| `traditional_tw` | Noto Sans CJK TC Bold | 繁體中文（台灣） | SIL OFL 1.1 |
| `korean` | Noto Sans CJK KR Bold | 韓文 | SIL OFL 1.1 |
| `english` | Roboto Bold | 英文/拉丁 | Apache 2.0 |
| `cartoon` | Noto Sans CJK SC Bold | 通用 | SIL OFL 1.1 |
| `calligraphy` | 系統字體 | 系統依賴 | 各異 |

## 專案結構

```
perfect-text-overlay/
├── assets/
│   └── fonts/              # 免費商用字體
│       ├── NotoSansCJKsc-Bold.otf    # 思源黑體簡體
│       ├── NotoSerifCJKsc-Bold.otf   # 思源宋體簡體
│       ├── NotoSansCJKtc-Bold.otf    # 思源黑體繁體
│       ├── NotoSansCJKkr-Bold.otf    # 思源黑體韓文
│       ├── Roboto-Bold.ttf           # Roboto 英文
│       ├── OpenSans-Bold.ttf         # Open Sans 英文
│       └── LICENSE.md
├── references/
│   ├── trigger_keywords.md    # 多語言觸發關鍵詞
│   ├── layout_patterns.md     # 排版最佳實踐
│   └── flowchart_symbols.md   # 流程圖設計標準
├── scripts/
│   ├── prompt_separator.py    # 從提示詞中提取文字
│   ├── image_analyzer.py      # 分析圖像佈局
│   └── text_renderer.py       # 在圖像上渲染文字
├── SKILL.md                   # 詳細技能文件
└── README.md                  # 主文件（英文）
```

## 支援的用例

### 1. 帶標題的海報
```
使用者："製作一張科幻電影海報，標題寫'星際效應'"
↓
步驟 1：圖像提示詞 = "sci-fi movie poster, space theme..."
        文字 = "星際效應"
↓
步驟 2：生成基礎圖像
↓
步驟 3：建議底部置中放置
↓
步驟 4：現代字體、底部置中、陰影+描邊
↓
步驟 5：在底部渲染大標題
```

### 2. 流程圖
```
使用者："建立使用者註冊流程圖：1.填寫資訊 2.驗證電子郵件 3.完成"
↓
步驟 1：檢測流程圖節點
↓
步驟 2：生成基礎圖像
↓
步驟 3：檢測 3 個節點位置
↓
步驟 4：水平流程、新增方框+箭頭
↓
步驟 5：渲染 3 個帶連接箭頭的方框節點
```

### 3. 資訊圖表
```
使用者："建立資訊圖表，顯示'銷售額：10萬元'和'成長：+50%'"
↓
步驟 1：提取資料點
↓
步驟 2：生成基礎圖像
↓
步驟 3：為每個統計資料找到安全區域
↓
步驟 4：大數字、對比色
↓
步驟 5：渲染專業資料視覺化
```

## API 參考

### 提示詞分離器

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("建立標題為'Hello World'的海報")
# 返回: {
#     "has_text": True,
#     "image_prompt": "Create poster...",
#     "text_requirements": {...}
# }
```

### 圖像分析器

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

## 觸發關鍵詞

當使用者輸入包含以下內容時，本技能將被觸發：

- **圖像類型關鍵詞**：海報、流程圖、資訊圖、banner 等
- **文字需求關鍵詞**：寫、標題、文字、標註、說明等

詳見 [references/trigger_keywords.md](references/trigger_keywords.md) 獲取完整的多語言關鍵詞列表。

## 字體授權

所有包含的字體均可免費商用：

- **Noto Sans/Serif CJK**: SIL Open Font License 1.1
- **Roboto**: Apache License 2.0
- **Open Sans**: SIL Open Font License 1.1

詳見 [assets/fonts/LICENSE.md](assets/fonts/LICENSE.md) 獲取完整授權詳情。

## 貢獻

歡迎貢獻！請隨時提交 Pull Request。

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件。

## 致謝

- [Noto Fonts](https://github.com/notofonts/noto-cjk) by Google & Adobe
- [Roboto](https://github.com/googlefonts/roboto) by Google
- [Open Sans](https://github.com/googlefonts/opensans) by Google

---

**其他語言版本：**
[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Perfect Text Overlay - 完美文字疊加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 透過分離圖像生成和文字渲染，解決 AI 生成圖像中文字錯亂的問題。

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | **繁體中文** | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 功能特點

AI 生成的圖像經常包含錯亂或不完美的文字，特別是對於中文、日文、韓文（CJK）等非拉丁文字。本工具透過以下步驟解決這個問題：

1. **分離** 提示詞 → 純圖像提示詞 + 文字需求
2. **生成** 乾淨的基礎圖像（使用您的 AI 工具）
3. **分析** 圖像找出最佳文字放置區域
4. **渲染** 完美的文字（使用專業排版）

---

## 自然語言安裝（適用於 AI Agent）

複製並貼上以下提示詞到您的 LLM Agent（Claude Code、Kimi Code、Cursor 等）：

```
在我的工作區安裝 perfect-text-overlay 技能。
從以下位址克隆：https://github.com/stephenlzc/perfect-text-overlay
設定所有依賴項，並透過執行繁體中文文本提取測試來驗證安裝。
```

---

## 安裝

### 環境要求
- Python 3.8+
- Python 套件：`pip install Pillow numpy`

### Git 克隆

```bash
git clone https://github.com/stephenlzc/perfect-text-overlay
cd perfect-text-overlay
```

---

## 使用方法

### 步驟 1：分離提示詞

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("電影海報，標題寫'星際效應'")
# result['image_prompt']: 不含文字的純視覺描述
# result['text_requirements']: 結構化文字資料
```

### 步驟 2：生成基礎圖像

使用 `image_prompt` 透過您喜歡的 AI 圖像生成器生成圖像（DALL-E、Midjourney、Stable Diffusion 等）

### 步驟 3：分析圖像

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 步驟 4：渲染文字

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

## 字體處理

字體按以下優先級載入：

1. **使用者提供的字體路徑**：如果指定了
2. **Skill 資源**：檢查 `assets/fonts/` 目錄
3. **系統字體**：搜尋常見系統字體目錄
4. **回退**：預設 PIL 字體

### 按語言推薦字體

#### 簡體中文
| 字體檔案 | 字體名稱 | 風格 | 適用場景 |
|---------|---------|------|---------|
| `NotoSansCJKsc-Bold.otf` | 思源黑體 Bold | 現代 | 海報標題、科技風格、商務場景 |
| `NotoSerifCJKsc-Bold.otf` | 思源宋體 Bold | 傳統 | 文化主題、書籍封面、正式文件 |

#### 繁體中文
| 字體檔案 | 字體名稱 | 風格 | 適用場景 |
|---------|---------|------|---------|
| `NotoSansCJKtc-Bold.otf` | 思源黑體 Bold | 現代 | 台灣/香港地區、商務文件 |

#### 韓文
| 字體檔案 | 字體名稱 | 風格 | 適用場景 |
|---------|---------|------|---------|
| `NotoSansCJKkr-Bold.otf` | 본고딕 Bold | 現代 | 한국어 포스터、현대적 디자인 |

#### 英文/拉丁
| 字體檔案 | 字體名稱 | 風格 | 適用場景 |
|---------|---------|------|---------|
| `Roboto-Bold.ttf` | Roboto Bold | 現代 | 科技海報、簡潔設計 |
| `OpenSans-Bold.ttf` | Open Sans Bold | 人文 | 網頁內容、通用場景 |

### 下載字體

您可以從 Google Fonts 或 Noto Fonts 手動下載字體並放入 `assets/fonts/` 目錄：

- **Noto CJK 字體**：https://www.google.com/get/noto/
- **Roboto**：https://fonts.google.com/specimen/Roboto
- **Open Sans**：https://fonts.google.com/specimen/Open+Sans

所有字體均可免費商用，採用 SIL Open Font License 或 Apache License 2.0 授權。

---

## 專案結構

```
perfect-text-overlay/
├── scripts/                # Python 腳本
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 字體目錄
└── references/             # 參考材料
```

---

## 授權

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 其他語言

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

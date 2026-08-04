# GenImageText - 完美文字疊加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚠️ **重要提示**：這不是圖像生成器。它為您的 AI 工具生成的圖像添加完美文字。

> 透過分離圖像生成和文字渲染，解決 AI 生成圖像中文字錯亂的問題。

![GenImageText Hero](https://raw.githubusercontent.com/stephenlzc/GenImageText/main/assets/hero_zh-TW.png)

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | **繁體中文** | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 本工具的功能

AI 生成的圖像經常包含錯亂或不完美的文字，特別是對於中文、日文、韓文（CJK）等非拉丁文字。**本工具透過以下方式解決這個問題**：

1. **本技能** 分離您的提示詞 → 純圖像提示詞 + 文字需求
2. **您的 AI 工具** 生成乾淨的基礎圖像（Midjourney、GPT Image 2、Stable Diffusion 等）
3. **本技能** 分析圖像找出最佳文字放置區域
4. **本技能** 渲染完美的文字（使用專業排版）

---

## 支援的 AI 圖像生成器

第 2 步（圖像生成）可以使用以下**任意**工具：

| 工具 | 平台 | 最佳用途 |
|------|------|----------|
| **Midjourney** | Discord | 高品質藝術圖片 |
| **GPT Image 2** | ChatGPT、OpenAI API | 易用，prompt 理解好 |
| **Stable Diffusion** | Local、Hugging Face、Replicate | 開源，可客製化 |
| **Google Gemini/Imagen** | Google AI Studio、Gemini Pro | Google 生態整合 |
| **Adobe Firefly** | Adobe Creative Suite | 商業使用安全 |
| **Microsoft Bing Image Creator** | Bing、Microsoft Designer | 免費，GPT Image 驅動 |
| **Flux.1** | API、Local | 高品質開源模型 |
| **Leonardo.ai** | Web、App | 遊戲資源，概念藝術 |
| **Ideogram** | Web | 圖片中文字渲染 |
| **Playground AI** | Web | 免費層可用 |

**關鍵點**：本技能**不生成圖像**。它只給上述工具生成的圖像添加文字。

---

## 自然語言安裝（適用於 AI Agent）

複製並貼上以下提示詞到您的 LLM Agent（Claude Code、Kimi Code、Cursor 等）：

```
在我的工作區安裝 GenImageText 技能。
從以下位址克隆：https://github.com/stephenlzc/GenImageText
設定所有依賴項，並透過執行繁體中文文本提取測試來驗證安裝。
```

---

## 安裝

### 環境要求
- Python 3.8+
- Python 套件：`pip install Pillow numpy`

### Git 克隆

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
```

---

## 使用方法

### 步驟 1：分離提示詞（本技能）

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("電影海報，標題寫'星際效應'")
# result['image_prompt']: 不含文字的純視覺描述
# result['text_requirements']: 結構化文字資料
```

### 步驟 2：生成基礎圖像（您的 AI 工具）

> ⚠️ **此步驟使用您的 AI 圖像生成器，不是本技能。**

使用 `image_prompt` 透過您喜歡的 AI 圖像生成器生成圖像：
- **Midjourney** - 基於 Discord 的生成
- **GPT Image 2**（ChatGPT Plus、OpenAI API）
- **Stable Diffusion** - 本地或雲端
- **Google Gemini/Imagen**
- **Adobe Firefly**
- **Microsoft Bing Image Creator**（免費）
- **任何您喜歡的其他 AI 圖像工具**

### 步驟 3：分析圖像（本技能）

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 步驟 4：渲染文字（本技能）

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

## 多語言批量生成模式（電商 · 學術 · 醫學）

本工具同時提供 **多場景多語言批量管線**：使用一張無文字底圖 × 七種語言翻譯（en / de / ja / ko / zh-CN / zh-TW / ar），一次性產出 N 張成品圖，適用於電商、學術與醫學素材，大幅縮短多語言內容製作時間。

### 內建預設

`presets/` 目錄下提供 8 套開箱即用預設，全部內建七語翻譯，直接 `init` 即可開始：

| 分類 | 預設 | 場景與畫布 |
|------|------|------------|
| 電商 | `amazon_main_image` | 電子產品主圖（2000 × 2000） |
| 電商 | `shopify_banner` | 夏季時尚橫幅（2400 × 1200） |
| 電商 | `social_square` | 美妝社媒方圖（1080 × 1080） |
| 電商 | `poster_a4` | 智慧手錶大促海報（2480 × 3508） |
| 電商 | `coffee_promo` | 咖啡餐飲促銷（1080 × 1080） |
| 電商 | `home_decor_banner` | 北歐家居橫幅（2400 × 1200） |
| 學術與醫學 | `academic_flowchart` | 研究流程圖（2400 × 1350） |
| 學術與醫學 | `medical_mechanism` | 醫學機制圖（1600 × 2000） |

### 核心特性

- **設定驅動模板**：`presets/` 目錄下提供 8 套開箱即用預設，全部內建七語翻譯，直接 `init` 即可開始。
- **美學排版引擎**：`scripts/layout_composer.py` 自動分析底圖亮度與安全區，智慧微調文字位置、依對比度校正文字顏色；面對複雜背景時，自動加上襯底與陰影以確保可讀性。
- **豐富文字效果**：透過 PIL 直繪（`scripts/text_renderer.py` 的 `render_layers_pil`，`BatchPipeline` 預設 renderer）支援陰影（shadow）、描邊（outline）、發光（glow）、半透明圓角襯底（backdrop），以及 badge 類型自動繪製的膠囊（pill）徽章。
- **RTL 完整支援**：阿拉伯語等從右至左語言享有完整 raqm 字形整形支援，字形渲染品質與其他語言一致。
- **4 路併發批量渲染**：`gen_ecommerce.py batch` 同時處理多語言變體，顯著縮短大批次專案的執行時間。

### Quick Start

```bash
.venv/bin/python gen_ecommerce.py init --preset amazon_main_image --project-dir projects/winter_2026
.venv/bin/python gen_ecommerce.py prompt --config presets/amazon_main_image/template.yaml
.venv/bin/python gen_ecommerce.py batch --config presets/amazon_main_image/template.yaml --base-image base.png --output renders
```

完整文件請見 [`README_ECOMMERCE.md`](README_ECOMMERCE.md)，預設列表請參閱 [`presets/`](presets/)。

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
GenImageText/
├── scripts/                # Python 腳本
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 字體目錄
└── references/             # 參考材料
```

---

## 致謝

本儲存庫 `presets/` 各預設的範例底圖（`sample_base_image.png`），以及 `assets/hero_base.png`，皆由 [**codex-image-gen**](https://github.com/stephenlzc/codex-image-gen) 生成——這是同作者的姊妹專案，透過本機 Codex CLI 登入即可免費生成圖片，無需任何 API key。推薦用作本工具的無文字底圖來源。

---

## 授權

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 其他語言

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

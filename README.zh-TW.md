# Perfect Text Overlay - 完美文字疊加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![npm version](https://badge.fury.io/js/perfect-text-overlay.svg)](https://www.npmjs.com/package/perfect-text-overlay)

> 透過分離圖像生成和文字渲染，解決 AI 生成圖像中文字錯亂的問題。

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | **繁體中文** | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 快速開始

```bash
# 安裝
npm install -g perfect-text-overlay

# 檢查環境
pto check

# 下載字體（可選）
pto download-fonts --all

# 使用
pto separate "製作一張標題為'新春大促'的海報"
```

## 功能特點

AI 生成的圖像經常包含錯亂或不完美的文字，特別是對於中文、日文、韓文（CJK）等非拉丁文字。本工具透過以下步驟解決這個問題：

1. **分離** 提示詞 → 純圖像提示詞 + 文字需求
2. **生成** 乾淨的基礎圖像（使用您的 AI 工具）
3. **分析** 圖像找出最佳文字放置區域
4. **渲染** 完美的文字（使用專業排版）

## 安裝

### 環境要求
- Node.js 18+
- Python 3.8+
- Python 套件：`pip install Pillow numpy`

### NPM 安裝（推薦）
```bash
npm install -g perfect-text-overlay
```

### Git 克隆
```bash
git clone https://github.com/stephenlzc/perfect-text-overlay
cd perfect-text-overlay
npm install
```

## CLI 使用方法

```bash
# 分離提示詞
pto separate -p "電影海報，標題寫'星際效應'"

# 分析圖像
pto analyze -i base.png -r '{"text_groups":[{"content":"新春大促"}]}'

# 渲染文字
pto render -i base.png -o final.png -p placements.json

# 完整工作流程
pto workflow -p "海報，標題'大促銷'" -i base.png -o final.png

# 下載字體
pto download-fonts --list
pto download-fonts --all
```

## Node.js API

```javascript
const { separatePrompt, analyzeImage, renderTextOnImage } = require('perfect-text-overlay');

async function createPoster() {
  // 1. 分離提示詞
  const result = await separatePrompt('海報，標題"新春大促"');
  
  // 2. 分析圖像（使用 result.image_prompt 生成圖像後）
  const analysis = await analyzeImage('base.png', result.text_requirements);
  
  // 3. 渲染文字
  await renderTextOnImage('base.png', 'final.png', 
    analysis.placements, 
    { font_style: 'traditional_tw', effects: ['shadow'] }
  );
}
```

## 字體風格

| 風格 | 語言 | 描述 |
|------|------|------|
| `modern` | 中文 | 現代簡約 |
| `traditional` | 中文 | 傳統宋體 |
| `traditional_tw` | 中文（台灣）| 繁體中文 |
| `korean` | 韓文 | 韓文優化 |
| `english` | 英文/拉丁 | Roboto 字體 |
| `calligraphy` | 任意 | 藝術書法 |
| `cartoon` | 任意 | 可愛卡通 |

下載字體：`pto download-fonts --all`

## 專案結構

```
perfect-text-overlay/
├── bin/cli.js              # CLI 入口
├── lib/index.js            # Node.js API
├── scripts/                # Python 腳本
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 字體（按需下載）
└── types/                  # TypeScript 定義
```

## 文件

- [API Reference](API.md) - 詳細 API 文件
- [Contributing](CONTRIBUTING.md) - 貢獻指南
- [CHANGELOG](CHANGELOG.md) - 版本歷史

## 授權

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 其他語言

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

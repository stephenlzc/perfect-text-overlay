# Perfect Text Overlay - 完美文字叠加

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![npm version](https://badge.fury.io/js/perfect-text-overlay.svg)](https://www.npmjs.com/package/perfect-text-overlay)

> 通过分离图像生成和文字渲染，解决 AI 生成图像中文字错乱的问题。

🌐 [English](README.md) | **简体中文** | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## 快速开始

```bash
# 安装
npm install -g perfect-text-overlay

# 检查环境
pto check

# 下载字体（可选）
pto download-fonts --all

# 使用
pto separate "生成一张标题为'新春大促'的海报"
```

## 功能特点

AI 生成的图像经常包含错乱或不完美的文字，特别是对于中文、日文、韩文（CJK）等非拉丁文字。本工具通过以下步骤解决这个问题：

1. **分离** 提示词 → 纯图像提示词 + 文字需求
2. **生成** 干净的基础图像（使用您的 AI 工具）
3. **分析** 图像找出最佳文字放置区域
4. **渲染** 完美的文字（使用专业排版）

## 安装

### 环境要求
- Node.js 18+
- Python 3.8+
- Python 包：`pip install Pillow numpy`

### NPM 安装（推荐）
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
# 分离提示词
pto separate -p "电影海报，标题写'星际穿越'"

# 分析图像
pto analyze -i base.png -r '{"text_groups":[{"content":"新春大促"}]}'

# 渲染文字
pto render -i base.png -o final.png -p placements.json

# 完整工作流
pto workflow -p "海报，标题'大促销'" -i base.png -o final.png

# 下载字体
pto download-fonts --list
pto download-fonts --all
```

## Node.js API

```javascript
const { separatePrompt, analyzeImage, renderTextOnImage } = require('perfect-text-overlay');

async function createPoster() {
  // 1. 分离提示词
  const result = await separatePrompt('海报，标题"新春大促"');
  
  // 2. 分析图像（使用 result.image_prompt 生成图像后）
  const analysis = await analyzeImage('base.png', result.text_requirements);
  
  // 3. 渲染文字
  await renderTextOnImage('base.png', 'final.png', 
    analysis.placements, 
    { font_style: 'modern', effects: ['shadow'] }
  );
}
```

## 字体风格

| 风格 | 语言 | 描述 |
|------|------|------|
| `modern` | 中文 | 现代简约 |
| `traditional` | 中文 | 传统宋体 |
| `traditional_tw` | 中文（台湾）| 繁体中文 |
| `korean` | 韩文 | 韩文优化 |
| `english` | 英文/拉丁 | Roboto 字体 |
| `calligraphy` | 任意 | 艺术书法 |
| `cartoon` | 任意 | 可爱卡通 |

下载字体：`pto download-fonts --all`

## 项目结构

```
perfect-text-overlay/
├── bin/cli.js              # CLI 入口
├── lib/index.js            # Node.js API
├── scripts/                # Python 脚本
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 字体（按需下载）
└── types/                  # TypeScript 定义
```

## 文档

- [API Reference](API.md) - 详细 API 文档
- [Contributing](CONTRIBUTING.md) - 贡献指南
- [CHANGELOG](CHANGELOG.md) - 版本历史

## 授权

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 其他语言

- [English](README.md) - English Documentation
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

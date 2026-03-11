# Perfect Text Overlay

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![npm version](https://badge.fury.io/js/perfect-text-overlay.svg)](https://www.npmjs.com/package/perfect-text-overlay)

> Fix imperfect AI-generated text in images by separating image generation and text overlay.

🌐 **English** | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

---

## Quick Start

```bash
# Install
npm install -g perfect-text-overlay

# Check environment
pto check

# Download fonts (optional)
pto download-fonts --all

# Use it
pto separate "Generate a poster with 'Summer Sale' title"
```

## What It Does

AI-generated images often have garbled text, especially for Chinese/Japanese/Korean. This tool fixes that by:

1. **Separate** prompt → image-only prompt + text requirements
2. **Generate** clean base image (use your AI of choice)
3. **Analyze** image for best text placement
4. **Render** perfect text with professional typography

## Installation

### Requirements
- Node.js 18+
- Python 3.8+
- Python packages: `pip install Pillow numpy`

### NPM
```bash
npm install -g perfect-text-overlay
```

### Git Clone
```bash
git clone https://github.com/stephenlzc/perfect-text-overlay
cd perfect-text-overlay
npm install
```

## CLI Usage

```bash
# Separate prompt
pto separate -p "Movie poster with 'Interstellar' title"

# Analyze image
pto analyze -i base.png -r '{"text_groups":[{"content":"Hello"}]}'

# Render text
pto render -i base.png -o final.png -p placements.json

# Complete workflow
pto workflow -p "Poster with 'Sale' title" -i base.png -o final.png

# Download fonts
pto download-fonts --list
pto download-fonts --all
```

## Node.js API

```javascript
const { separatePrompt, analyzeImage, renderTextOnImage } = require('perfect-text-overlay');

async function createPoster() {
  // 1. Separate
  const result = await separatePrompt('Poster with "Hello" title');
  
  // 2. Analyze (after generating image with result.image_prompt)
  const analysis = await analyzeImage('base.png', result.text_requirements);
  
  // 3. Render
  await renderTextOnImage('base.png', 'final.png', 
    analysis.placements, 
    { font_style: 'modern', effects: ['shadow'] }
  );
}
```

## Font Styles

| Style | Language | Description |
|-------|----------|-------------|
| `modern` | Chinese | Clean, professional |
| `traditional` | Chinese | Serif, elegant |
| `traditional_tw` | Chinese (TW) | Traditional Chinese |
| `korean` | Korean | Korean optimized |
| `english` | English/Latin | Roboto font |
| `calligraphy` | Any | Artistic style |
| `cartoon` | Any | Fun, playful |

Download fonts: `pto download-fonts --all`

## Project Structure

```
perfect-text-overlay/
├── bin/cli.js              # CLI entry
├── lib/index.js            # Node.js API
├── scripts/                # Python scripts
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # Fonts (downloaded on demand)
└── types/                  # TypeScript definitions
```

## Documentation

- [API Reference](API.md) - Detailed API documentation
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG](CHANGELOG.md) - Version history

## License

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 Languages

- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔  
- [日本語](README.ja.md) - 日本語ドキュメント
- [한국어](README.ko.md) - 한국어 문서

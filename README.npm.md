# Perfect Text Overlay

[![npm version](https://badge.fury.io/js/perfect-text-overlay.svg)](https://www.npmjs.com/package/perfect-text-overlay)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fix imperfect AI-generated text in images by separating image generation and text overlay.

## Problem

AI image generators (DALL-E, Midjourney, Stable Diffusion) often produce garbled or incorrect text, especially for Chinese characters and complex scripts.

## Solution

Perfect Text Overlay solves this by separating the process into two steps:

1. **Generate clean image** without any text descriptions
2. **Overlay perfect text** using professional typography

## Installation

```bash
npm install -g perfect-text-overlay
```

### Prerequisites

- Node.js 14+
- Python 3.7+

The installation script will automatically check and install Python dependencies (`Pillow`, `numpy`).

## CLI Usage

### Commands

#### `pto separate <prompt>`

Separate user prompt into image-only prompt and text requirements.

```bash
pto separate "生成一张春节促销海报，标题写'新春大促，全场5折起'"
```

Output:
```
✓ Text detected and extracted

📷 Image Prompt:
A festive Chinese New Year promotional poster, vibrant red and gold color scheme...

📝 Text Requirements:
{
  "type": "single_or_few",
  "text_groups": [
    { "id": "text_1", "content": "新春大促，全场5折起", ... }
  ]
}
```

#### `pto analyze <image>`

Analyze image to find optimal text placement zones.

```bash
pto analyze ./my-image.png --requirements '{"type":"single_or_few"}'
```

#### `pto render <input> <output>`

Render text onto an image.

```bash
pto render ./input.png ./output.png \
  --file ./placements.json \
  --font modern \
  --effects shadow,outline
```

#### `pto workflow <prompt> <image> <output>`

Complete workflow in one command.

```bash
pto workflow "海报标题'Hello World'" ./base.png ./final.png \
  --font modern \
  --effects shadow,outline
```

#### `pto check`

Check if all dependencies are installed.

```bash
pto check
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--font <style>` | Font style: modern, traditional, calligraphy, cartoon, english, korean |
| `--size <size>` | Text size: small, auto (default), large |
| `--effects <list>` | Comma-separated effects: shadow, outline, box |
| `--color <color>` | Text color (hex or name) |
| `--connections` | Show connections (for flowcharts) |
| `-j, --json` | Output as JSON |

## Node.js API

```javascript
const { separatePrompt, analyzeImage, renderText, workflow } = require('perfect-text-overlay');

// Step 1: Separate prompt
const promptResult = await separatePrompt('生成一张标题为"Hello World"的海报');
console.log(promptResult.image_prompt);
// "A promotional poster, high quality, professional, suitable for text overlay"

// Step 2: Analyze image
const analysis = await analyzeImage('./base-image.png', promptResult.text_requirements);
console.log(analysis.placements);

// Step 3: Render text
const outputPath = await renderText(
  './base-image.png',
  './output.png',
  analysis.placements,
  {
    font_style: 'modern',
    effects: ['shadow', 'outline'],
    text_color: '#FFFFFF'
  }
);

// Or use complete workflow
const results = await workflow(
  '生成一张标题为"Hello World"的海报',
  './base-image.png',
  {
    outputPath: './output.png',
    fontStyle: 'modern',
    effects: ['shadow']
  }
);
```

## API Reference

### `separatePrompt(prompt)`

Separate user prompt into image-only prompt and text requirements.

- **Parameters:** `prompt` (string) - User's original prompt
- **Returns:** Promise<Object>
  - `has_text` (boolean) - Whether text was detected
  - `image_prompt` (string) - Clean image prompt without text
  - `text_requirements` (Object) - Structured text data

### `analyzeImage(imagePath, requirements)`

Analyze image for text placement.

- **Parameters:**
  - `imagePath` (string) - Path to image file
  - `requirements` (Object) - Text requirements from separatePrompt
- **Returns:** Promise<Object>
  - `analysis` - Color scheme, safe zones, complexity map
  - `placements` - Suggested text placements

### `renderText(imagePath, outputPath, placements, userChoices)`

Render text onto an image.

- **Parameters:**
  - `imagePath` (string) - Input image path
  - `outputPath` (string) - Output image path
  - `placements` (Array) - Text placements from analyzeImage
  - `userChoices` (Object) - Customization options
- **Returns:** Promise<string> - Path to rendered image

### `workflow(prompt, imagePath, options)`

Complete workflow: separate prompt, analyze, and render.

- **Parameters:**
  - `prompt` (string) - User prompt
  - `imagePath` (string) - Base image path
  - `options` (Object) - Workflow options
- **Returns:** Promise<Object> - Complete results

## Font Styles

| Style | Description | Best For |
|-------|-------------|----------|
| `modern` | 思源黑体 (Noto Sans CJK) | Tech, Business |
| `traditional` | 思源宋体 (Noto Serif CJK) | Cultural, Classic |
| `calligraphy` | 书法字体 | Artistic, Personal |
| `cartoon` | 卡通风格 | Kids, Fun |
| `english` | Roboto/Open Sans | English text |
| `korean` | Noto Sans CJK KR | Korean text |

## Effects

- `shadow` - Drop shadow for depth
- `outline` / `stroke` - Border around text for readability
- `box` - Semi-transparent background box

## Supported Languages

- ✅ Chinese (Simplified)
- ✅ Chinese (Traditional)
- ✅ English
- ✅ Korean
- ✅ Japanese

## License

MIT © stephenlzc

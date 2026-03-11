# Perfect Text Overlay - API Documentation

Complete API reference for the `perfect-text-overlay` npm package.

---

## Table of Contents

- [Installation](#installation)
- [Core APIs](#core-apis)
  - [separatePrompt](#separateprompt)
  - [analyzeImage](#analyzeimage)
  - [getTextPlacementSuggestions](#gettextplacementsuggestions)
  - [renderTextOnImage](#rendertextonimage)
- [Utility Functions](#utility-functions)
- [Types](#types)
- [Error Handling](#error-handling)
- [CLI Reference](#cli-reference)

---

## Installation

```bash
npm install perfect-text-overlay
```

```javascript
const pto = require('perfect-text-overlay');
// or
import { separatePrompt, analyzeImage, renderTextOnImage } from 'perfect-text-overlay';
```

---

## Core APIs

### separatePrompt

Extracts text requirements from a user prompt and generates a clean image-only prompt.

#### Signature

```javascript
separatePrompt(userInput: string): SeparationResult
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userInput` | `string` | Yes | The user's original prompt containing text requirements |

#### Returns

**`SeparationResult`** - Object containing:

| Property | Type | Description |
|----------|------|-------------|
| `has_text` | `boolean` | Whether text requirements were detected |
| `image_prompt` | `string` | Clean image prompt without text descriptions |
| `text_requirements` | `TextRequirements` | Structured text data with content and position hints |

#### Example

```javascript
const { separatePrompt } = require('perfect-text-overlay');

const result = separatePrompt(
  "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围"
);

console.log(result);
// {
//   has_text: true,
//   image_prompt: "A festive Chinese New Year promotional poster, vibrant red and gold color scheme, traditional lanterns and plum blossoms decoration, celebration atmosphere, high quality, professional, clean composition, suitable for text overlay",
//   text_requirements: {
//     type: "single_or_few",
//     text_groups: [
//       {
//         id: "text_1",
//         content: "新春大促，全场5折起",
//         semantic_position: "auto"
//       }
//     ]
//   }
// }
```

#### TextRequirements Structure

```typescript
interface TextRequirements {
  type: 'single_or_few' | 'flowchart' | 'infographic' | 'diagram';
  text_groups: TextGroup[];
}

interface TextGroup {
  id: string;
  content: string;
  semantic_position: 'auto' | 'top' | 'bottom' | 'center' | string;
}
```

---

### analyzeImage

Analyzes an image to find safe zones for text placement.

#### Signature

```javascript
analyzeImage(imagePath: string, textRequirements: TextRequirements): ImageAnalysis
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `imagePath` | `string` | Yes | Path to the image file to analyze |
| `textRequirements` | `TextRequirements` | Yes | Text requirements from `separatePrompt` |

#### Returns

**`ImageAnalysis`** - Object containing:

| Property | Type | Description |
|----------|------|-------------|
| `safe_zones` | `SafeZone[]` | Array of safe areas for text placement |
| `color_palette` | `number[][]` | Dominant colors in the image (RGB arrays) |
| `dimensions` | `{width: number, height: number}` | Image dimensions |
| `complexity_map` | `number[][]` | 2D array representing visual complexity |

#### Example

```javascript
const { analyzeImage } = require('perfect-text-overlay');

const textRequirements = {
  type: "single_or_few",
  text_groups: [{
    id: "text_1",
    content: "新春大促，全场5折起",
    semantic_position: "auto"
  }]
};

const analysis = analyzeImage("./outputs/base_image.png", textRequirements);

console.log(`Safe zones found: ${analysis.safe_zones.length}`);
console.log(`Dominant colors: ${analysis.color_palette.length}`);
```

#### SafeZone Structure

```typescript
interface SafeZone {
  x: number;
  y: number;
  width: number;
  height: number;
  score: number;  // 0-1, higher is better for text
  avg_color: [number, number, number];
}
```

---

### getTextPlacementSuggestions

Generates optimal text placement suggestions based on image analysis.

#### Signature

```javascript
getTextPlacementSuggestions(
  analysis: ImageAnalysis, 
  textRequirements: TextRequirements
): Placement[]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `analysis` | `ImageAnalysis` | Yes | Result from `analyzeImage` |
| `textRequirements` | `TextRequirements` | Yes | Original text requirements |

#### Returns

**`Placement[]`** - Array of placement suggestions:

| Property | Type | Description |
|----------|------|-------------|
| `id` | `string` | Unique identifier matching text group |
| `text` | `string` | Text content to render |
| `x` | `number` | X coordinate for text placement |
| `y` | `number` | Y coordinate for text placement |
| `width` | `number` | Suggested text box width |
| `height` | `number` | Suggested text box height |
| `font_size` | `number` | Suggested font size in pixels |
| `suggested_color` | `[number, number, number]` | RGB color for best contrast |

#### Example

```javascript
const { analyzeImage, getTextPlacementSuggestions } = require('perfect-text-overlay');

const analysis = analyzeImage("./base.png", textRequirements);
const placements = getTextPlacementSuggestions(analysis, textRequirements);

placements.forEach((placement, i) => {
  console.log(`Text ${i + 1}: "${placement.text}"`);
  console.log(`  Position: (${placement.x}, ${placement.y})`);
  console.log(`  Font size: ${placement.font_size}px`);
  console.log(`  Color: rgb(${placement.suggested_color.join(', ')})`);
});
```

---

### renderTextOnImage

Renders text onto an image with professional typography and effects.

#### Signature

```javascript
renderTextOnImage(options: RenderOptions): string
```

#### Parameters

**`RenderOptions`** object:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `image_path` | `string` | Yes | Path to input image |
| `output_path` | `string` | Yes | Path for output image |
| `placements` | `Placement[]` | Yes | Text placements from `getTextPlacementSuggestions` |
| `user_choices` | `UserChoices` | Yes | User customization options |

#### UserChoices

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `font_style` | `string` | `'modern'` | Font style name |
| `text_size` | `'auto' \| number` | `'auto'` | Text size or auto-detect |
| `text_color` | `[number, number, number] \| null` | `null` | RGB color or auto-detect |
| `effects` | `Effect[]` | `[]` | Array of text effects |
| `show_connections` | `boolean` | `false` | Show arrows between nodes |
| `background_opacity` | `number` | `180` | Background box opacity (0-255) |

#### Effect Types

| Effect | Description |
|--------|-------------|
| `'shadow'` | Add drop shadow for depth |
| `'outline'` | Add outline for readability |
| `'background_box'` | Semi-transparent background box |
| `'border'` | Border around text (for flowcharts) |
| `'arrows'` | Connection arrows (for flowcharts) |

#### Font Styles

| Style | Font File | Language | License |
|-------|-----------|----------|---------|
| `'modern'` | Noto Sans CJK SC Bold | Simplified Chinese | SIL OFL 1.1 |
| `'traditional'` | Noto Serif CJK SC Bold | Simplified Chinese | SIL OFL 1.1 |
| `'traditional_tw'` | Noto Sans CJK TC Bold | Traditional Chinese | SIL OFL 1.1 |
| `'korean'` | Noto Sans CJK KR Bold | Korean | SIL OFL 1.1 |
| `'english'` | Roboto Bold | English/Latin | Apache 2.0 |
| `'cartoon'` | Noto Sans CJK SC Bold | Universal | SIL OFL 1.1 |
| `'calligraphy'` | System dependent | System dependent | Varies |

#### Returns

**`string`** - Path to the generated output image.

#### Example

```javascript
const { renderTextOnImage } = require('perfect-text-overlay');

const outputPath = renderTextOnImage({
  image_path: "./base_image.png",
  output_path: "./final_image.png",
  placements: [
    {
      id: "text_1",
      text: "新春大促，全场5折起",
      x: 400,
      y: 800,
      width: 800,
      height: 100,
      font_size: 72,
      suggested_color: [255, 215, 0]
    }
  ],
  user_choices: {
    font_style: "modern",
    text_size: "auto",
    text_color: [255, 215, 0],  // Gold
    effects: ["shadow", "outline"],
    show_connections: false,
    background_opacity: 180
  }
});

console.log(`Output saved to: ${outputPath}`);
```

---

## Utility Functions

### getAvailableFonts

Returns a list of available fonts on the system.

```javascript
const { getAvailableFonts } = require('perfect-text-overlay');

const fonts = getAvailableFonts();
console.log(fonts);
// [
//   { name: 'Noto Sans CJK SC', path: '/path/to/font.otf', style: 'modern' },
//   { name: 'Roboto', path: '/path/to/roboto.ttf', style: 'english' },
//   ...
// ]
```

### hexToRgb

Converts hex color to RGB array.

```javascript
const { hexToRgb } = require('perfect-text-overlay');

const rgb = hexToRgb('#FFD700');
console.log(rgb);  // [255, 215, 0]
```

### rgbToHex

Converts RGB array to hex color.

```javascript
const { rgbToHex } = require('perfect-text-overlay');

const hex = rgbToHex([255, 215, 0]);
console.log(hex);  // '#FFD700'
```

---

## Types

### Complete TypeScript Definitions

```typescript
// Core types
type TextType = 'single_or_few' | 'flowchart' | 'infographic' | 'diagram';
type FontStyle = 'modern' | 'traditional' | 'traditional_tw' | 'korean' | 'english' | 'cartoon' | 'calligraphy';
type Effect = 'shadow' | 'outline' | 'background_box' | 'border' | 'arrows';
type Position = 'auto' | 'top' | 'bottom' | 'center' | string;

// Data structures
interface TextGroup {
  id: string;
  content: string;
  semantic_position: Position;
}

interface TextRequirements {
  type: TextType;
  text_groups: TextGroup[];
}

interface SeparationResult {
  has_text: boolean;
  image_prompt: string;
  text_requirements: TextRequirements;
}

interface SafeZone {
  x: number;
  y: number;
  width: number;
  height: number;
  score: number;
  avg_color: [number, number, number];
}

interface ImageAnalysis {
  safe_zones: SafeZone[];
  color_palette: [number, number, number][];
  dimensions: { width: number; height: number };
  complexity_map: number[][];
}

interface Placement {
  id: string;
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  font_size: number;
  suggested_color: [number, number, number];
}

interface UserChoices {
  font_style: FontStyle;
  text_size: 'auto' | number;
  text_color: [number, number, number] | null;
  effects: Effect[];
  show_connections: boolean;
  background_opacity: number;
}

interface RenderOptions {
  image_path: string;
  output_path: string;
  placements: Placement[];
  user_choices: UserChoices;
}

// Function signatures
declare function separatePrompt(userInput: string): SeparationResult;
declare function analyzeImage(imagePath: string, textRequirements: TextRequirements): ImageAnalysis;
declare function getTextPlacementSuggestions(
  analysis: ImageAnalysis, 
  textRequirements: TextRequirements
): Placement[];
declare function renderTextOnImage(options: RenderOptions): string;
```

---

## Error Handling

All functions may throw errors. Always wrap calls in try-catch blocks:

```javascript
const { separatePrompt, analyzeImage, renderTextOnImage } = require('perfect-text-overlay');

try {
  const result = separatePrompt(userInput);
  const analysis = analyzeImage(imagePath, result.text_requirements);
  const output = renderTextOnImage({
    image_path: imagePath,
    output_path: outputPath,
    placements: placements,
    user_choices: userChoices
  });
} catch (error) {
  if (error.code === 'IMAGE_NOT_FOUND') {
    console.error('Image file not found:', error.path);
  } else if (error.code === 'FONT_NOT_FOUND') {
    console.error('Font not found:', error.font);
  } else if (error.code === 'INVALID_PLACEMENT') {
    console.error('Invalid text placement:', error.placement);
  } else {
    console.error('Unexpected error:', error.message);
  }
}
```

### Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `IMAGE_NOT_FOUND` | Image file does not exist | Check the file path |
| `FONT_NOT_FOUND` | Specified font not found | Use `getAvailableFonts()` or install fonts |
| `INVALID_PLACEMENT` | Placement coordinates invalid | Check placement bounds |
| `TEXT_TOO_LONG` | Text exceeds available space | Shorten text or reduce font size |
| `INVALID_COLOR` | Color format incorrect | Use RGB array [R, G, B] |
| `NO_SAFE_ZONES` | No suitable text areas found | Use different image or add background_box effect |

---

## CLI Reference

### Global Options

```bash
perfect-text-overlay [command] [options]

Options:
  -v, --version       Show version number
  -h, --help          Show help
  --verbose           Enable verbose logging
  --quiet             Suppress non-error output
  --config <path>     Use custom config file
```

### Commands

#### `separate`

Extract text requirements from prompt.

```bash
perfect-text-overlay separate "<prompt>" [options]

Options:
  -o, --output <path>   Save result to JSON file

Examples:
  perfect-text-overlay separate "Create poster with title 'Hello'"
  perfect-text-overlay separate "生成海报，标题'新春快乐'" --output result.json
```

#### `analyze`

Analyze image for text placement.

```bash
perfect-text-overlay analyze <image-path> [options]

Options:
  -t, --text <json>     Text requirements (JSON string or file path)
  -o, --output <path>   Save result to JSON file

Examples:
  perfect-text-overlay analyze ./image.png --text '{"type":"single","text_groups":[{"content":"Hello"}]}'
  perfect-text-overlay analyze ./image.png --text ./requirements.json
```

#### `render`

Render text on image.

```bash
perfect-text-overlay render [options]

Options:
  -i, --input <path>        Input image path
  -o, --output <path>       Output image path
  -p, --placements <path>   Placements JSON file
  -f, --font <style>        Font style
  -e, --effects <list>      Comma-separated effects
  -c, --color <hex>         Text color (hex)
  -q, --quality <number>    JPEG quality (1-100)

Examples:
  perfect-text-overlay render -i base.png -o final.png -p placements.json
  perfect-text-overlay render -i base.png -o final.png -p placements.json -f modern -e shadow,outline
```

#### `process`

Complete workflow in one command.

```bash
perfect-text-overlay process [options]

Options:
  --prompt <text>       User prompt
  --output <path>       Output image path
  -f, --font <style>    Font style
  -e, --effects <list>  Comma-separated effects
  -c, --color <hex>     Text color

Examples:
  perfect-text-overlay process --prompt "Create poster with title 'Hello'" --output ./out.png
  perfect-text-overlay process --prompt "生成海报，标题'新春快乐'" -f modern -e shadow,outline
```

#### `batch`

Process multiple prompts from file.

```bash
perfect-text-overlay batch [options]

Options:
  -i, --input <path>        Input file (one prompt per line)
  -o, --output-dir <path>   Output directory
  -f, --font <style>        Font style
  -e, --effects <list>      Comma-separated effects

Examples:
  perfect-text-overlay batch -i prompts.txt -o ./outputs/
```

#### `fonts`

List available fonts.

```bash
perfect-text-overlay fonts [options]

Options:
  --json    Output in JSON format

Examples:
  perfect-text-overlay fonts
  perfect-text-overlay fonts --json
```

#### `init`

Generate configuration file.

```bash
perfect-text-overlay init [options]

Options:
  -o, --output <path>   Config file path

Examples:
  perfect-text-overlay init
  perfect-text-overlay init -o ./pto-config.json
```

#### `doctor`

Check installation and dependencies.

```bash
perfect-text-overlay doctor
```

---

## Examples

### Basic Usage

```javascript
const { separatePrompt, analyzeImage, getTextPlacementSuggestions, renderTextOnImage } = require('perfect-text-overlay');

const userInput = "Create a movie poster with title 'Inception'";

// Step 1: Separate prompt
const separated = separatePrompt(userInput);

// Step 2: Generate base image (using your preferred image generator)
// ... generate image using separated.image_prompt ...

// Step 3: Analyze image
const analysis = analyzeImage("./base.png", separated.text_requirements);
const placements = getTextPlacementSuggestions(analysis, separated.text_requirements);

// Step 4: Render text
const output = renderTextOnImage({
  image_path: "./base.png",
  output_path: "./final.png",
  placements: placements,
  user_choices: {
    font_style: "english",
    effects: ["shadow", "outline"],
    text_color: [255, 255, 255]
  }
});
```

### Flowchart Example

```javascript
const { separatePrompt, analyzeImage, getTextPlacementSuggestions, renderTextOnImage } = require('perfect-text-overlay');

const userInput = "Create flowchart: Start -> Process -> End";

const separated = separatePrompt(userInput);
const analysis = analyzeImage("./flowchart_base.png", separated.text_requirements);
const placements = getTextPlacementSuggestions(analysis, separated.text_requirements);

const output = renderTextOnImage({
  image_path: "./flowchart_base.png",
  output_path: "./flowchart_final.png",
  placements: placements,
  user_choices: {
    font_style: "modern",
    effects: ["border", "arrows"],
    show_connections: true
  }
});
```

---

## License

MIT License - see [LICENSE](./LICENSE) file for details.

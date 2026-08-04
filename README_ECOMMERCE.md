# GenImageText — Multi-language E-commerce Listing Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚠️ **IMPORTANT**: This is NOT an image generator. It adds pixel-perfect
> text to images created by your AI tools.

This module extends the upstream **GenImageText** skill into a
**configuration-driven, multi-language batch pipeline** for e-commerce,
academic, and medical scenes. One base image + one `template.yaml` + N
JSON translation files → N language variants, rendered in a single run.

> Upstream skill (image-generation split, analysis, single-image render)
> is still available at the project root; the e-commerce pipeline lives
> in `gen_ecommerce.py`, `scripts/`, and `presets/`.

---

## Core Design Principles

1. **Separate what changes from what does not**
   The base image is generated **once** (by your AI image tool —
   Midjourney, GPT Image 2, Stable Diffusion, Flux, [codex-image-gen](https://github.com/stephenlzc/codex-image-gen),
   etc.). Text is composed in software via Pillow + the smart layout
   engine, and rendered per language. There is no re-generation of the
   artwork per locale.

2. **Configuration-driven**
   Each layout is described declaratively in a single
   `template.yaml` file. The runtime schema is validated by Pydantic 2.x
   (see `scripts/config_loader.py`); unknown keys, bad enums, missing
   fields, or duplicate layer names raise `ConfigError` immediately.

3. **PIL direct-draw as the text path** (default renderer)
   Each text layer is rasterised directly with Pillow from
   `scripts/text_renderer.py::render_layers_pil`. Fonts are loaded by
   absolute file path (`ImageFont.truetype`), which avoids the two
   long-standing issues with the CairoSVG path: cairo can't resolve
   arbitrary font file paths or font directory family names, and it has
   no HarfBuzz-style shaping — so CJK glyphs fell back to system
   defaults and Arabic / Hebrew text could not be shaped into proper
   connected letterforms. With PIL we get the configured typeface for
   every script (including a native Arabic font) and correct RTL
   shaping through raqm. The SVG template engine
   (`scripts/template_engine.py`) is kept as a compatibility fallback
   via `BatchPipeline(renderer="svg")` — every previously-shipped
   `template.yaml` continues to render through either path.

4. **Smart layout before render**
   `scripts/layout_composer.py::compose_layout` analyses the base image
   (overall brightness, per-region readability score, WCAG contrast
   against the local background) and produces a `LayoutPlan` that
   nudges each text layer into a safer landing spot, corrects colour
   contrast, and adds backdrop / shadow where the area is too busy.
   The plan is applied to a *copy* of the layer config — your
   `template.yaml` is never mutated — and the rationale for every
   adjustment is recorded into the batch report.

5. **Batch pipeline, one CLI**
   `gen_ecommerce.py batch` loads every `translations/<lang>.json`,
   matches a font per language, renders one PNG/JPG/WebP per language
   into the output directory, and prints a structured report
   (`success` / `failed` / `outputs` / `overflow_warnings` /
   `base_image_check` / `layout_adjustments` / `timing`).

---

## Installation

### 1. Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate            # macOS / Linux
pip install -r requirements.txt
```

`requirements.txt`:

```text
Pillow>=10.0.0
numpy>=1.24.0
cairosvg>=2.7.0
jinja2>=3.1.0
pydantic>=2.0.0
pyyaml>=6.0
pytesseract>=0.3.10
click>=8.0.0
```

> Note: `cairosvg` is kept in the dependency list because the
> `renderer="svg"` fallback path still uses it. The default
> `renderer="pil"` path does not require cairo at runtime.

### 2. Optional: Tesseract OCR

The `check` subcommand runs OCR on the base image to detect residual
text. It calls the Tesseract binary via `pytesseract`. If the binary is
not on PATH, `check` downgrades gracefully to a `WARN` and prints the
install hint.

```bash
# macOS
brew install tesseract

# Debian / Ubuntu
sudo apt-get install tesseract-ocr
```

### 3. Fonts

`assets/fonts/` ships seven font files (see [Font Matching](#font-matching)).

---

## Quick Start (CLI)

`gen_ecommerce.py` exposes six subcommands. All examples assume the
project root and use `.venv/bin/python`.

```bash
# 1. Scaffold a project from a preset
.venv/bin/python gen_ecommerce.py init \
    --preset amazon_main_image \
    --project-dir projects/winter_2026
```

This copies `presets/amazon_main_image/` (template + 7 translation
files + README + example images) into `projects/winter_2026/`.

```bash
# 2. Print the AI image prompt + a summary of safe zones
.venv/bin/python gen_ecommerce.py prompt \
    --config presets/amazon_main_image/template.yaml
```

Output (real run):

```text
--- base image prompt (copy into Midjourney / Stable Diffusion) ---
Professional product photography of wireless headphones on pure white background, centered composition, soft studio lighting, no text, no watermark, no logos, clean negative space at bottom 20% for text overlay, high detail, 8k quality
---

safe_zones (2):
  1. bottom_center: 400, 1600, 1600, 1900 -> title
  2. bottom_right: 1400, 1700, 1900, 1850 -> badge
```

Paste the first block into your image-generation tool and save the
result, e.g. `projects/winter_2026/base_image.png`.

```bash
# 3. Sanity-check the base image for any leftover text
.venv/bin/python gen_ecommerce.py check \
    --image projects/winter_2026/base_image.png
# OK: no text detected on the base image.
# (or WARN: OCR unavailable — install Tesseract to enable this check)
```

```bash
# 4. Validate the entire project before committing to a full render
.venv/bin/python gen_ecommerce.py validate \
    --config presets/amazon_main_image/template.yaml
```

`validate` runs:
- schema validation (Pydantic 2.x via `load_config`)
- layout warnings (canvas overflow, safe-zone overflow)
- font availability check against `assets/fonts/`
- loads `translations/<lang>.json` via `I18nManager`
- checks that every `text_layer.name` exists in `en.json`

```bash
# 5a. Render one language variant (PIL renderer is the default)
.venv/bin/python gen_ecommerce.py render \
    --config presets/amazon_main_image/template.yaml \
    --base-image projects/winter_2026/base_image.png \
    --lang ja \
    --output projects/winter_2026/out_ja.png

# 5b. Render every loaded language at once
.venv/bin/python gen_ecommerce.py batch \
    --config presets/amazon_main_image/template.yaml \
    --base-image projects/winter_2026/base_image.png \
    --output projects/winter_2026/renders
```

The `batch` report contains `success`, `failed`, per-language `outputs`,
any `overflow_warnings`, the `base_image_check` summary, a
`layout_adjustments[lang]` map (per-layer adjustment rationales
produced by the smart layout engine), and timing information.

---

## Built-in Presets

Eight presets ship in `presets/`. Each one bundles its own
`template.yaml`, seven `translations/<lang>.json` files (`en`, `de`,
`ja`, `ko`, `zh-CN`, `zh-TW`, `ar`), a `sample_base_image.png`
generated by [codex-image-gen](https://github.com/stephenlzc/codex-image-gen)
(the prompt that produced it is in `sample_base_image.md`), three
example renders in `examples/`, and a preset-specific `README.md`.

| Preset                 | Scene          | Product / Topic                       | Canvas (W×H)  | Output | Text layers                                                                          |
|------------------------|----------------|---------------------------------------|---------------|--------|---------------------------------------------------------------------------------------|
| `amazon_main_image`    | `product_main` | Wireless Bluetooth Headphones         | 2000 × 2000   | png    | `product_title` (text), `price` (price), `badge` (badge)                              |
| `shopify_banner`       | `banner`       | Summer fashion / lifestyle            | 2400 × 1200   | png    | `headline` (text), `subheadline` (text), `cta` (badge)                                |
| `social_square`        | `social`       | Skincare serum                        | 1080 × 1080   | png    | `title` (badge), `price_tag` (badge), `hashtag` (text)                                |
| `poster_a4`            | `poster`       | Smartwatch mega-sale                  | 2480 × 3508   | png    | `title` (text), `subtitle` (text), `price` (price), `cta` (badge), `disclaimer` (text)|
| `coffee_promo`         | `social`       | Coffee shop promotion                 | 1080 × 1080   | png    | `title` (text), `offer` (badge), `price_tag` (price)                                  |
| `home_decor_banner`    | `banner`       | Scandinavian home décor               | 2400 × 1200   | png    | `headline` (text), `subheadline` (text), `cta` (badge)                                |
| `academic_flowchart`   | `academic`     | Research workflow figure (4 nodes)    | 2400 × 1350   | png    | `title` (text), `node1`–`node4` (badge), `footer` (text)                             |
| `medical_mechanism`    | `medical`      | Mitochondrial energy production (4 stages) | 1600 × 2000   | png    | `title` (text), `subtitle` (text), `stage1`–`stage4` (badge), `caption` (text)      |

Each preset is a complete, self-contained unit:

```
presets/<name>/
├── README.md            # preset-specific notes
├── template.yaml        # canvas + layers
├── sample_base_image.md # prompt that produced sample_base_image.png
├── sample_base_image.png  # AI-generated base (no text)
├── examples/
│   ├── <name>_en.png      # rendered by this pipeline
│   ├── <name>_ar.png      # rendered by this pipeline (RTL)
│   └── <name>_zh-CN.png   # rendered by this pipeline
└── translations/
    ├── en.json
    ├── de.json
    ├── ja.json
    ├── ko.json
    ├── zh-CN.json
    ├── zh-TW.json
    └── ar.json          # RTL (Arabic)
```

User-defined presets can live in `templates/<your-name>/` (same shape).
The repo ships `templates/hero/` — a banner template used to render
the multi-language `assets/hero*.png` showcase images. `templates/`
ships with a `.gitkeep` placeholder so the directory is always
present.

---

## Preset Gallery

Every preset ships a sample base image (text-free, generated by
[codex-image-gen](https://github.com/stephenlzc/codex-image-gen))
together with three renders produced by this pipeline (`en` / `ar` /
`zh-CN`). The renders exercise the smart layout engine, RTL shaping,
and per-layer effects (backdrop / outline / glow / pill badges).

### `amazon_main_image` — Amazon-style product hero

Square 2000×2000 product photo with a dark headline at the bottom, a
red price tag with a pink rounded backdrop, and a pill "Free Shipping"
badge in the top-right corner.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Amazon base](presets/amazon_main_image/sample_base_image.png) | ![Amazon EN](presets/amazon_main_image/examples/amazon_main_image_en.png) | ![Amazon AR](presets/amazon_main_image/examples/amazon_main_image_ar.png) | ![Amazon ZH](presets/amazon_main_image/examples/amazon_main_image_zh-CN.png) |

### `shopify_banner` — Online-store hero banner

Wide 2400×1200 lifestyle photo with a headline + subheadline stack on
the left and a yellow pill CTA on the right.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Shopify base](presets/shopify_banner/sample_base_image.png) | ![Shopify EN](presets/shopify_banner/examples/shopify_banner_en.png) | ![Shopify AR](presets/shopify_banner/examples/shopify_banner_ar.png) | ![Shopify ZH](presets/shopify_banner/examples/shopify_banner_zh-CN.png) |

### `social_square` — Square social-post card

Square 1080×1080 social card with a hero title pill in the centre, a
yellow price-tag pill in the bottom-right, and a small hashtag at the
bottom.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Social base](presets/social_square/sample_base_image.png) | ![Social EN](presets/social_square/examples/social_square_en.png) | ![Social AR](presets/social_square/examples/social_square_ar.png) | ![Social ZH](presets/social_square/examples/social_square_zh-CN.png) |

### `poster_a4` — Print-ready A4 poster

A4-sized 2480×3508 poster with a glowing display title, soft subtitle,
oversized gold price with a white outline + warm glow, pill CTA, and a
muted fine-print disclaimer at the bottom.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Poster base](presets/poster_a4/sample_base_image.png) | ![Poster EN](presets/poster_a4/examples/poster_a4_en.png) | ![Poster AR](presets/poster_a4/examples/poster_a4_ar.png) | ![Poster ZH](presets/poster_a4/examples/poster_a4_zh-CN.png) |

### `coffee_promo` — Square coffee-shop promo card

Square 1080×1080 social card with a bold serif title at the top, a
pill "offer" badge in the centre, and a yellow price tag near the
bottom — sized for Instagram / Xiaohongshu promo posts.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Coffee base](presets/coffee_promo/sample_base_image.png) | ![Coffee EN](presets/coffee_promo/examples/coffee_promo_en.png) | ![Coffee AR](presets/coffee_promo/examples/coffee_promo_ar.png) | ![Coffee ZH](presets/coffee_promo/examples/coffee_promo_zh-CN.png) |

### `home_decor_banner` — Scandinavian home-decor banner

Wide 2400×1200 lifestyle banner with a serif headline + subheadline
stack on the left and a yellow pill CTA on the right — the layout that
normally fronts a Shopify / Etsy collection page.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Home decor base](presets/home_decor_banner/sample_base_image.png) | ![Home decor EN](presets/home_decor_banner/examples/home_decor_banner_en.png) | ![Home decor AR](presets/home_decor_banner/examples/home_decor_banner_ar.png) | ![Home decor ZH](presets/home_decor_banner/examples/home_decor_banner_zh-CN.png) |

### `academic_flowchart` — Research-workflow figure (academic)

2400×1350 academic figure: a centred title, four pill "node" badges
laid out left-to-right as a research-workflow pipeline, and a small
footer note. Designed to slot straight into a paper or poster's
methods / pipeline section.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Academic base](presets/academic_flowchart/sample_base_image.png) | ![Academic EN](presets/academic_flowchart/examples/academic_flowchart_en.png) | ![Academic AR](presets/academic_flowchart/examples/academic_flowchart_ar.png) | ![Academic ZH](presets/academic_flowchart/examples/academic_flowchart_zh-CN.png) |

### `medical_mechanism` — Mitochondrial energy production figure (medical)

1600×2000 medical figure: a centred title and subtitle, four pill "stage"
badges (Glycolysis → Krebs Cycle → Electron Transport Chain → ATP
Synthesis) aligned to the glowing pathway nodes beside the mitochondrion,
and a fine-print caption at the bottom. Built for cellular-energy pathway
and signaling diagrams on pharma / educational materials.

| Source base (no text) | English | Arabic (RTL) | Simplified Chinese |
|----------------------|---------|--------------|--------------------|
| ![Medical base](presets/medical_mechanism/sample_base_image.png) | ![Medical EN](presets/medical_mechanism/examples/medical_mechanism_en.png) | ![Medical AR](presets/medical_mechanism/examples/medical_mechanism_ar.png) | ![Medical ZH](presets/medical_mechanism/examples/medical_mechanism_zh-CN.png) |

> **All base images in this gallery were produced by
> [codex-image-gen](https://github.com/stephenlzc/codex-image-gen);
> every final render was produced by this pipeline.**

---

## `template.yaml` Reference

The full schema lives in `scripts/config_loader.py`. There are two
Pydantic models: `TemplateConfig` (top-level) and `TextLayerConfig`
(per layer). Models use `extra="forbid"`, so any unknown key is a
hard schema error.

### Top-level — `TemplateConfig`

| Field              | Type                | Required | Default | Notes                                                                                                  |
|--------------------|---------------------|----------|---------|--------------------------------------------------------------------------------------------------------|
| `name`             | string              | yes      | —       | Human-readable identifier (must be non-blank).                                                         |
| `scene_type`       | enum                | yes      | —       | One of `product_main`, `banner`, `poster`, `social`, `academic`, `medical`. `academic` is used for research-figure layouts (e.g. labelled flowchart nodes), `medical` for mechanism-of-action diagrams. Used by downstream tools. |
| `canvas_width`     | int (>0)            | yes      | —       | Output canvas width in pixels.                                                                         |
| `canvas_height`    | int (>0)            | yes      | —       | Output canvas height in pixels.                                                                        |
| `base_image_prompt`| string              | yes      | —       | Prompt for your image-generation tool. `prompt` subcommand appends `no text`, `no watermark`, `no logos` if missing. |
| `safe_zones`       | list of dicts       | no       | `[]`    | Reserved-for-text rectangles. Each entry may use `bbox`, `bbox_norm`, or `x/y/width/height` keys. Names/regions read by `prompt` for display only. |
| `text_layers`      | list of layer dicts | yes      | —       | Each `name` must be **unique**.                                                                        |
| `translations_file` | string             | yes      | —       | Path to the default translation file (relative to the config), e.g. `translations/en.json`.           |
| `output_format`    | enum                | no       | `png`   | One of `png`, `jpg`, `jpeg`, `webp` (case-insensitive).                                               |
| `output_quality`   | int (1–100)         | no       | `95`    | JPEG/WebP quality (ignored for PNG).                                                                   |

### Per-layer — `TextLayerConfig`

| Field            | Type         | Required | Default      | Notes                                                                                                                  |
|------------------|--------------|----------|--------------|------------------------------------------------------------------------------------------------------------------------|
| `name`           | string       | yes      | —            | Unique within the template. Keys the JSON translation files (e.g. `product_title`).                                    |
| `type`           | enum         | yes      | —            | One of `text`, `badge`, `price` — tags the layer's semantic role. With the PIL renderer, `type: badge` automatically draws a pill-shaped backdrop (radius = half height) instead of a plain rounded rectangle. |
| `default_font`   | string       | yes      | —            | Font file basename under `assets/fonts/` (e.g. `Roboto-Bold.ttf`).                                                     |
| `fallback_fonts` | list[string] | no       | `[]`         | Tried in order if `default_font` fails to load.                                                                        |
| `max_width`      | int (>0)     | yes      | —            | Soft wrap / overflow ceiling in pixels.                                                                                |
| `max_lines`      | int (>0)     | no       | `1`          | Maximum wrapped lines before the renderer drops excess (auto-shrink kicks in before exceeding it).                    |
| `effects`        | list[string] | no       | `[]`         | Each entry one of `shadow`, `outline`, `glow`, `backdrop` (case-insensitive). See [Effects](#effects).                 |
| `anchor`         | string       | yes      | —            | Reserved anchor name (`top-left`, `top-center`, ..., `bottom-right`, `center`, ...). Non-blank after trim.            |
| `x`              | int          | yes      | —            | Anchor x in canvas pixels. `validate` warns if `x < 0` or `x >= canvas_width`.                                         |
| `y`              | int          | yes      | —            | Anchor y in canvas pixels. `validate` warns if `y < 0` or `y >= canvas_height`.                                        |
| `color`          | string       | no       | `#FFFFFF`    | 3, 6 or 8-digit hex, e.g. `#1a1a1a`, `#e63946`.                                                                        |
| `font_size`      | int (>0)     | yes      | —            | Nominal font size in pixels. The PIL renderer auto-shrinks until the wrapped text fits within `max_lines`.            |
| `rtl_flip`       | bool         | no       | `False`      | When `True`, the renderer draws the glyph run right-to-left (combined with `direction="rtl"` for Arabic/Hebrew/Persian/Urdu). |
| `backdrop_color` | string/null  | no       | `null`       | Backdrop fill (only used when `backdrop` is in `effects`). Accepts `#RGB` / `#RRGGBB` / `#RRGGBBAA` hex **or** the special tokens `auto-dark` (black, α=150) / `auto-light` (white, α=150). The smart layout engine writes this field too. |
| `stroke_color`   | string/null  | no       | `null`       | Outline / stroke colour (only used when `outline` is in `effects`). `#RGB` / `#RRGGBB` / `#RRGGBBAA`. When unset, the renderer picks an automatic high-contrast colour from `color`'s luminance. |
| `stroke_width`   | int (0–20)   | no       | `2`          | Outline / stroke thickness in pixels. Set to `0` to keep the auto-stem at zero width (the field is still respected as an explicit override). |
| `glow_color`     | string/null  | no       | `null`       | Glow halo colour (only used when `glow` is in `effects`). Defaults to `color` when unset.                              |
| `padding`        | int (≥0)     | no       | `0`          | Backdrop / pill inset in pixels. The renderer adds a default of `font_size // 6` (text) or `16` (badge) when `0`, but an explicit value always wins. |

### Effects

| Effect      | What the PIL renderer does                                                                                                  |
|-------------|------------------------------------------------------------------------------------------------------------------------------|
| `shadow`    | Draws a half-transparent black copy of the glyph run, offset by `font_size // 18 + 1` pixels, then composites the main text on top. |
| `outline`   | Renders the main glyphs with a `stroke_width`-wide stroke (using `stroke_color`, falling back to auto-contrast), then fills on top via Pillow's `paint-order="stroke fill"` equivalent. |
| `glow`      | Renders the glyphs in `glow_color` (or `color`), blurs them with a Gaussian of `font_size // 10`, composites the blurred layer three times for intensity, then draws the crisp text on top. |
| `backdrop`  | Draws a rounded rectangle (or a pill — `radius = half height` — when `type: badge`) behind the text using `backdrop_color`. Pads the text by `padding` (or a sensible default when unset). |

> All four effects are case-insensitive and unknown values trigger a
> schema error at load time.

### Safe-zone shapes (any of three)

```yaml
safe_zones:
  # 1. absolute pixel bbox
  - region: "bottom_center"
    bbox: [400, 1600, 1600, 1900]
    suggested_for: "title"

  # 2. normalised bbox (values in [0, 1])
  - name: "headline_zone"
    bbox_norm: [0.05, 0.20, 0.65, 0.40]

  # 3. explicit x/y/width/height
  - name: "cta_zone"
    x: 1600
    y: 940
    width: 760
    height: 200
```

Display keys (`name`, `region`, `label`) are optional and only consumed
by `prompt` for human-readable output. Rectangles that overflow the
canvas trigger **warnings** at `validate` time but do not fail the run.

---

## Translation File Format

Each language has a flat JSON object keyed by `text_layer.name`. Place
the file at `<project-dir>/translations/<lang>.json`.

```json
{
  "product_title": "Wireless Bluetooth Headphones",
  "price": "$49.99",
  "cta": "Shop Now",
  "badge": "Free Shipping"
}
```

Rules:

- Keys must be plain strings; values must be plain strings (`I18nManager`
  coerces non-string values via `str(...)` and warns at load time).
- The English file (`en.json`) is the **fallback**: if a key is missing
  in another language, `I18nManager.get_translation` returns the English
  text.
- Adding a new language requires no change to `template.yaml`; just drop
  `<code>.json` with the same keys into `translations/`.

The shipped presets each ship **seven** translation files
(`en`, `de`, `ja`, `ko`, `zh-CN`, `zh-TW`, `ar`) covering Latin,
Japanese, Korean, Simplified Chinese, Traditional Chinese, and Arabic
(RTL).

---

## Font Matching

`I18nManager.get_font_for_language(lang, style="modern")` selects a font
file from `assets/fonts/`. The actual choice is based on the files
**present on disk** — adding a new `.otf` / `.ttf` / `.ttc` to the
folder makes it available immediately.

### Font files shipped

| File                              | Script coverage                                                | Notes                                       |
|-----------------------------------|----------------------------------------------------------------|---------------------------------------------|
| `Roboto-Bold.ttf`                 | Latin (default modern)                                         | Tech / clean design                         |
| `OpenSans-Bold.ttf`               | Latin (elegant / traditional style)                            | Humanist, web content                       |
| `NotoSansCJKsc-Bold.otf`          | Simplified Chinese, Japanese (kanto), Korean (fallback)        | Default CJK                                 |
| `NotoSansCJKtc-Bold.otf`          | Traditional Chinese (TW/HK)                                    |                                             |
| `NotoSansCJKkr-Bold.otf`          | Korean                                                         |                                             |
| `NotoSerifCJKsc-Bold.otf`         | Simplified Chinese (serif)                                     | Traditional / formal documents              |
| `NotoSansArabic-Bold.ttf`         | Arabic, Persian, Urdu (RTL)                                    | OFL licensed; native glyph shaping          |

### Language → font mapping (per `get_font_for_language`)

| Language family         | Codes                                                                  | Font chosen                              |
|-------------------------|------------------------------------------------------------------------|------------------------------------------|
| Latin                   | `en`, `de`, `fr`, `es`, `it`, `pt`, `nl`, `pl`, `sv`, `da`, `fi`, `no`, `cs`, `ro`, `tr`, `hu`, `sk`, `sl` | `Roboto-Bold.ttf` (modern) or `OpenSans-Bold.ttf` (elegant/traditional) |
| Japanese                | `ja`                                                                   | `NotoSansCJKsc-Bold.otf`                 |
| Korean                  | `ko`                                                                   | `NotoSansCJKkr-Bold.otf`                 |
| Traditional Chinese     | `zh-tw`, `zh-hant`, `zh_tw`, `zh-hk`, `zh-mo`                          | `NotoSansCJKtc-Bold.otf`                 |
| Simplified Chinese      | `zh`, `zh-cn`, `zh-hans`, `zh-sg`                                       | `NotoSansCJKsc-Bold.otf`                 |
| Arabic / Persian / Urdu | `ar`, `fa`, `ur`                                                       | `NotoSansArabic-Bold.ttf`                |
| Hebrew / other RTL      | `he` and other RTL codes                                               | `NotoSansCJKsc-Bold.otf` (fallback)      |
| Other / unrecognised    | anything else                                                          | `Roboto-Bold.ttf`                        |

### RTL notes

- `I18nManager.is_rtl(lang)` returns `True` for `ar`, `he`, `fa`, `ur`.
- Text layers with `rtl_flip: true` are drawn glyph-by-glyph in
  reverse order so the rightmost character appears at the layer's `x`
  anchor — the natural way RTL languages read. The PIL renderer also
  passes `direction="rtl"` / `language=<code>` to Pillow's text engine
  so raqm can shape connected Arabic letterforms correctly.
- The shipped `NotoSansArabic-Bold.ttf` covers Arabic, Persian
  (Farsi) and Urdu natively; Hebrew continues to fall back to
  `NotoSansCJKsc-Bold.otf`. To add a dedicated Hebrew typeface, drop
  `NotoSansHebrew-Bold.ttf` (or similar) into `assets/fonts/` and
  extend the RTL branch in `scripts/i18n_manager.py` — no other
  configuration changes are required.

---

## Smart Layout Engine

`scripts/layout_composer.py` is the project's "aesthetic typography"
layer. Before any pixel is drawn, it inspects the base image and
decides whether the configured text coordinates are actually a good
landing spot. The engine is invoked by `BatchPipeline` (PIL renderer,
default) per language and the resulting adjustments are surfaced both
in the rendered output and in the `layout_adjustments` field of the
batch report.

`compose_layout(image_path, template_config, lang="en")` returns a
`LayoutPlan` of the shape:

```python
{
    "layers": [
        {"name": ..., "x": ..., "y": ..., "color": ..., "effects": [...],
         "font_size": ..., "backdrop_color": ...?, "adjustments": [str, ...]},
        ...
    ],
    "analysis_summary": {
        "image_size": [w, h], "brightness": ..., "suggested_bg": ...,
        "suggested_text_color": [...], "color_family": ...,
        "safe_zone_count": ..., "top_safe_zones": [...]
    },
}
```

The four decision passes, in order:

1. **Position nudge** — when the local readability score is below
   `READABILITY_POOR` (40), the layer is shifted (within 15 % of the
   canvas) towards a same-band safe zone whose `readability_score` is
   higher. Re-samples the region after the move so subsequent
   decisions see the actual landing pixel window.
2. **Effect enhancement** — readability < 40 → add `backdrop` (auto
   dark/light panel based on region brightness). 40–70 and no existing
   `backdrop` / `shadow` / `outline` → add `shadow` so the text stays
   legible on a busy background.
3. **Contrast correction** — if the text-vs-region contrast ratio is
   below the WCAG-simplified threshold (3.0), the text colour is
   flipped to a dark or light counterpart depending on the region
   brightness; if the layer ends up with a `backdrop`, contrast is
   re-checked against the backdrop (so e.g. dark text on a light panel
   gets corrected to dark text properly, or vice versa).
4. **Stacking** — when two text layers vertically overlap (Δy smaller
   than the sum of their font sizes, in the same horizontal column),
   the lower one is shifted down by `0.6 × (sum of font sizes)` minus
   its current gap, to prevent glyph collision.

The plan is applied to a *copy* of each `TextLayerConfig` (via
Pydantic `model_copy`) inside `text_renderer.render_layers_pil`, so
the original `template.yaml` is never mutated. Every adjustment is
appended to a human-readable `adjustments` list and rolled up into the
batch report:

```json
{
  "layout_adjustments": {
    "ja": [
      {"layer": "product_title",
       "adjustments": [
         "对比度校正：文字色与落点区域对比度 2.1 < 3.0，按区域亮度 240 切换为 #1a1a1a",
         "效果增强：落点区域较复杂（可读性 65），自动追加 shadow"
       ]}
    ]
  }
}
```

To opt out (e.g. for debugging or when comparing the raw config to the
adjusted render), call `render_layers_pil(..., smart_layout=False)`
directly — `BatchPipeline` does this internally only when the renderer
is `svg`.

---

## Workflow

```
+----------------------------------------------------------------+
| 1. template.yaml → base_image_prompt                          |
|    (gen_ecommerce.py prompt --config ...)                     |
+----------------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------------+
| 2. YOUR AI image tool  (Midjourney / GPT Image 2 / SD / Flux / |
|    codex-image-gen / ...)                                     |
|    Feed it base_image_prompt; save as base_image.png          |
+----------------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------------+
| 3. gen_ecommerce.py check --image base_image.png              |
|    OCR-detect any residual text; regenerate if found           |
+----------------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------------+
| 4. gen_ecommerce.py batch                                     |
|    --config template.yaml --base-image base_image.png         |
|    --output  outputs/run-20260101/                            |
|                                                                |
|    For each translations/<lang>.json:                         |
|      compose_layout(base_image, config, lang) → LayoutPlan     |
|      →  PIL draws text layers (shadow/outline/glow/backdrop)  |
|      →  alpha-composite onto base_image                       |
|      →  write out_<lang>.<ext>                                |
+----------------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------------+
| 5. N language variants in --output, plus a batch report        |
|    { success, failed, outputs, overflow_warnings,              |
|      base_image_check, layout_adjustments, timing }           |
+----------------------------------------------------------------+
```

Each preset ships ready-to-render; user projects live under
`projects/<your-name>/` (or any path you choose).

---

## Project Structure

```
GenImageText/
├── gen_ecommerce.py          # CLI entry point (init / prompt / batch
│                             #   / render / validate / check)
├── scripts/                  # Flat module dir; not a Python package
│   ├── config_loader.py      # Pydantic 2.x schema + validate_config_file
│   ├── i18n_manager.py       # Translation loading, RTL detection,
│   │                         #   language → font mapping, overflow estimate
│   ├── template_engine.py    # Jinja2-driven SVG generation per layer
│   │                         #   (used by renderer="svg" fallback path)
│   ├── text_renderer.py      # render_svg_template (cairo fallback) +
│   │                         #   render_layers_pil (default renderer)
│   ├── image_analyzer.py     # Image inspection + residual-text OCR +
│   │                         #   readability / color-scheme helpers
│   ├── layout_composer.py    # Smart layout engine (compose_layout)
│   ├── prompt_separator.py   # Original upstream prompt splitter
│   └── batch_pipeline.py     # BatchPipeline (run, render_single,
│                             #   layout_adjustments report)
├── presets/                  # Built-in templates — copy via `init`
│   ├── amazon_main_image/
│   │   ├── README.md
│   │   ├── template.yaml
│   │   ├── sample_base_image.md
│   │   ├── sample_base_image.png
│   │   ├── examples/{amazon_main_image_en,amazon_main_image_ar,amazon_main_image_zh-CN}.png
│   │   └── translations/{en,de,ja,ko,zh-CN,zh-TW,ar}.json
│   ├── shopify_banner/
│   ├── social_square/
│   ├── poster_a4/
│   ├── coffee_promo/
│   ├── home_decor_banner/
│   ├── academic_flowchart/
│   └── medical_mechanism/
├── templates/                # User-defined templates (empty by default;
│   ├── .gitkeep              #   ships templates/hero/ used to render
│   └── hero/                 #   assets/hero*.png)
│       ├── template.yaml
│       └── translations/{en,ja,ko,zh-CN,zh-TW}.json
├── projects/                 # (User-defined) rendered projects
├── assets/
│   ├── fonts/                # Roboto, OpenSans, NotoSans CJK sc/tc/kr,
│   │                         #   NotoSerif CJK sc, NotoSans Arabic
│   ├── hero.png              # English hero showcase render
│   ├── hero_ja.png           # Japanese hero showcase render
│   ├── hero_ko.png           # Korean hero showcase render
│   ├── hero_zh-CN.png        # Simplified Chinese hero showcase render
│   ├── hero_zh-TW.png        # Traditional Chinese hero showcase render
│   ├── hero_base.png         # Base image used by all hero_* renders
│   └── hero_base.md          # Prompt that produced hero_base.png
├── outputs/                  # Default location for `batch --output`
│   └── .gitkeep              # kept tracked; *.png/*.jpg are git-ignored
├── references/               # Upstream reference material
├── requirements.txt
├── README.md                 # Upstream skill (image-generation split)
└── README_ECOMMERCE.md       # ← this file
```

---

## Output Directory & `.gitignore`

`outputs/` is tracked (via `outputs/.gitkeep`) but actual render files
are ignored. The same pattern is used by `templates/`:

- `templates/.gitkeep` is committed so the directory exists in the repo.
- Add `templates/<your-template>/` directories with the same shape as
  `presets/<name>/` to define custom presets.

---

## Credits

The **base images** used throughout this documentation — every
`presets/<name>/sample_base_image.png` in the [Preset Gallery](#preset-gallery)
and `assets/hero_base.png` — were generated by
[**codex-image-gen**](https://github.com/stephenlzc/codex-image-gen),
a sister project by the same author. codex-image-gen wraps the local
**Codex CLI** (OAuth login, no API key required) and lets you generate
images for free from your terminal.

If you are looking for an AI image tool to pair with this pipeline:

- **codex-image-gen** — local Codex CLI, OAuth login, free, no API key
  ([github.com/stephenlzc/codex-image-gen](https://github.com/stephenlzc/codex-image-gen))
- Midjourney, GPT Image 2, Stable Diffusion, Flux, and any other tool that
  emits a raster base image also work — `check` warns if your base
  accidentally already contains text, and the smart layout engine
  adjusts the per-layer placement against whatever image you feed it.

Every **final render** in the gallery (the right-most three columns of
each preset table, plus all `assets/hero*.png`) was produced by
**this pipeline**.

---

## License

MIT — see [`LICENSE`](LICENSE).
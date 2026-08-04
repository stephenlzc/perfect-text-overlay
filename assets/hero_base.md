Modern wide banner illustration for a developer tool project, sleek wireless headphones product floating over a clean deep-gradient background from indigo to teal, subtle geometric grid and soft light beams, generous empty space on the left half for title text, flat modern tech aesthetic with soft 3D product render, no text, no letters, no watermark, no logos

Output requirements:
- Generate exactly one image at 1600x900 pixels (1600 wide x 900 tall).
- Save the final image as: /var/folders/fy/vl6f7msn3nn8jhk04kj89qn40000gn/T/codex-image-gen.XXXXXX.pWd8JEksGe/output.png
- Enforce exact pixel dimensions if the model produces a non-matching size: use 'sips -z 900 1600' on macOS, or ImageMagick ('magick <file> -resize 1600x900! <file>') elsewhere.
- After saving, print a single line: FINAL_IMAGE_PATH=<absolute path to the saved PNG>

## Archive record

- **Template:** `hero` (`scene_type: banner`), with a `1600x900` pixel canvas.
- **Translation source:** `translations/en.json` (the default flat object for `brand`, `tagline`, and `badge`).
- **Generation prompt:** The exact prompt above was used for the clean headphones base image; it reserves the left half for the later `brand`, `tagline`, and `badge` text layers.
- **Generator output path:** `/var/folders/fy/vl6f7msn3nn8jhk04kj89qn40000gn/T/codex-image-gen.XXXXXX.pWd8JEksGe/output.png`
- **Archived output path:** `assets/hero_base.png`
- **Dimensions:** `1600 × 900` pixels, verified with `sips` and Pillow.
- **Generation exit code:** `0` (successful).
- **Visual no-text verification:** **PASS** — visual inspection of `assets/hero_base.png` found only the headphones illustration and indigo/teal background; no text, letters, signage, watermark, or logos are visible. Automated OCR was unavailable because the `tesseract` executable is not installed.
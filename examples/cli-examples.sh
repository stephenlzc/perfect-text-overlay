#!/bin/bash
# ==============================================================================
# Perfect Text Overlay - CLI Examples
# ==============================================================================
# 
# This file demonstrates all available CLI commands for the perfect-text-overlay
# npm package. These examples work in bash, zsh, and compatible shells.
#
# Usage:
#   chmod +x cli-examples.sh
#   ./cli-examples.sh
#
# Or run individual commands directly in your terminal.
# ==============================================================================

set -e  # Exit on error

echo "=========================================="
echo "Perfect Text Overlay - CLI Examples"
echo "=========================================="

# ==============================================================================
# 1. BASIC COMMANDS
# ==============================================================================

echo ""
echo "=== 1. Help and Version ==="
echo ""

# Show help information
perfect-text-overlay --help

# Show version
perfect-text-overlay --version

# ==============================================================================
# 2. PROMPT SEPARATION
# ==============================================================================

echo ""
echo "=== 2. Prompt Separation ==="
echo ""

# Separate a simple prompt
perfect-text-overlay separate "Create a poster with title 'Hello World'"

# Separate a Chinese prompt
perfect-text-overlay separate "生成一张春节促销海报，标题写'新春大促'"

# Output to JSON file
perfect-text-overlay separate "Movie poster with title 'Inception'" --output prompt_result.json

# ==============================================================================
# 3. IMAGE ANALYSIS
# ==============================================================================

echo ""
echo "=== 3. Image Analysis ==="
echo ""

# Analyze image with text requirements from file
perfect-text-overlay analyze ./outputs/base_image.png --text ./text_requirements.json

# Analyze with inline text requirements
perfect-text-overlay analyze ./outputs/base_image.png \
  --text '{"type":"single_or_few","text_groups":[{"content":"Hello World"}]}'

# Output analysis to file
perfect-text-overlay analyze ./outputs/base_image.png \
  --text ./text_requirements.json \
  --output analysis_result.json

# ==============================================================================
# 4. TEXT RENDERING
# ==============================================================================

echo ""
echo "=== 4. Text Rendering ==="
echo ""

# Basic rendering with placements from file
perfect-text-overlay render \
  --input ./outputs/base_image.png \
  --output ./outputs/final.png \
  --placements ./placements.json

# Render with font style option
perfect-text-overlay render \
  --input ./outputs/base_image.png \
  --output ./outputs/final.png \
  --placements ./placements.json \
  --font modern

# Available font styles:
#   modern          - Clean sans-serif (Noto Sans CJK SC)
#   traditional     - Serif style (Noto Serif CJK SC)
#   traditional_tw  - Traditional Chinese (Noto Sans CJK TC)
#   korean          - Korean font (Noto Sans CJK KR)
#   english         - Latin font (Roboto)
#   cartoon         - Playful style
#   calligraphy     - Handwritten style

# Render with effects
perfect-text-overlay render \
  --input ./outputs/base_image.png \
  --output ./outputs/final.png \
  --placements ./placements.json \
  --effects shadow,outline

# Available effects:
#   shadow          - Add drop shadow
#   outline         - Add text outline
#   background_box  - Add semi-transparent background
#   border          - Add border around text
#   arrows          - Add connection arrows (for flowcharts)

# Render with custom text color
perfect-text-overlay render \
  --input ./outputs/base_image.png \
  --output ./outputs/final.png \
  --placements ./placements.json \
  --color "#FFD700"

# Combined options
perfect-text-overlay render \
  --input ./outputs/base_image.png \
  --output ./outputs/final.png \
  --placements ./placements.json \
  --font english \
  --effects shadow,outline \
  --color "#FFFFFF"

# ==============================================================================
# 5. COMPLETE WORKFLOW (ONE COMMAND)
# ==============================================================================

echo ""
echo "=== 5. Complete Workflow ==="
echo ""

# Process from prompt to final image in one command
perfect-text-overlay process \
  --prompt "Create a sci-fi movie poster with title 'Interstellar'" \
  --output ./outputs/interstellar_poster.png \
  --font english \
  --effects shadow,outline

# Chinese poster example
perfect-text-overlay process \
  --prompt "生成一张春节促销海报，标题写'新春大促，全场5折起'" \
  --output ./outputs/cny_poster.png \
  --font modern \
  --effects shadow,background_box \
  --color "#FFD700"

# Flowchart example
perfect-text-overlay process \
  --prompt "Create flowchart: Start -> Process -> End" \
  --output ./outputs/flowchart.png \
  --font modern \
  --effects border,arrows

# ==============================================================================
# 6. BATCH PROCESSING
# ==============================================================================

echo ""
echo "=== 6. Batch Processing ==="
echo ""

# Process multiple prompts from file
perfect-text-overlay batch \
  --input ./prompts.txt \
  --output-dir ./batch_outputs/ \
  --font modern \
  --effects shadow

# prompts.txt format (one prompt per line):
#   Create poster with title 'Poster 1'
#   Create poster with title 'Poster 2'
#   Create poster with title 'Poster 3'

# ==============================================================================
# 7. CONFIGURATION
# ==============================================================================

echo ""
echo "=== 7. Configuration ==="
echo ""

# Use custom configuration file
perfect-text-overlay process \
  --prompt "Create a poster" \
  --config ./config.json \
  --output ./outputs/poster.png

# Example config.json:
# {
#   "font_style": "modern",
#   "effects": ["shadow", "outline"],
#   "text_color": [255, 215, 0],
#   "output_quality": 95,
#   "output_format": "png"
# }

# ==============================================================================
# 8. ADVANCED OPTIONS
# ==============================================================================

echo ""
echo "=== 8. Advanced Options ==="
echo ""

# Specify custom font path
perfect-text-overlay render \
  --input ./outputs/base.png \
  --output ./outputs/final.png \
  --placements ./placements.json \
  --font-path /path/to/custom/font.ttf

# Specify output quality (for JPEG)
perfect-text-overlay render \
  --input ./outputs/base.png \
  --output ./outputs/final.jpg \
  --placements ./placements.json \
  --quality 95

# Verbose mode (detailed logging)
perfect-text-overlay process \
  --prompt "Create a poster" \
  --output ./outputs/poster.png \
  --verbose

# Quiet mode (minimal output)
perfect-text-overlay process \
  --prompt "Create a poster" \
  --output ./outputs/poster.png \
  --quiet

# ==============================================================================
# 9. UTILITY COMMANDS
# ==============================================================================

echo ""
echo "=== 9. Utility Commands ==="
echo ""

# List available fonts
perfect-text-overlay fonts

# Check installation and dependencies
perfect-text-overlay doctor

# Generate example configuration file
perfect-text-overlay init --output ./pto-config.json

# ==============================================================================
# 10. REAL-WORLD EXAMPLES
# ==============================================================================

echo ""
echo "=== 10. Real-World Examples ==="
echo ""

# --- Social Media Post ---
perfect-text-overlay process \
  --prompt "Create Instagram post saying 'Summer Sale! 50% Off'" \
  --output ./outputs/instagram_post.png \
  --font english \
  --effects shadow,outline \
  --color "#FFFFFF"

# --- Event Poster ---
perfect-text-overlay process \
  --prompt "Create conference poster with title 'Tech Summit 2025'" \
  --output ./outputs/conference_poster.png \
  --font english \
  --effects shadow,background_box \
  --color "#1a1a1a"

# --- Product Label ---
perfect-text-overlay process \
  --prompt "Create product label with 'Premium Quality' and 'Made in USA'" \
  --output ./outputs/product_label.png \
  --font modern \
  --effects outline \
  --color "#000000"

# --- Educational Diagram ---
perfect-text-overlay process \
  --prompt "Create diagram: Photosynthesis process with labels 'Sunlight', 'Water', 'Oxygen'" \
  --output ./outputs/diagram.png \
  --font modern \
  --effects background_box \
  --color "#333333"

# --- Infographic ---
perfect-text-overlay process \
  --prompt "Create infographic with stats 'Users: 10K' and 'Growth: +25%'" \
  --output ./outputs/infographic.png \
  --font english \
  --effects shadow \
  --color "#FFFFFF"

# --- Certificate ---
perfect-text-overlay process \
  --prompt "Create certificate with name 'John Doe' and title 'Certificate of Achievement'" \
  --output ./outputs/certificate.png \
  --font calligraphy \
  --effects outline \
  --color "#8B4513"

# --- Menu Board ---
perfect-text-overlay process \
  --prompt "Create cafe menu board with 'Coffee $5', 'Tea $3', 'Cake $6'" \
  --output ./outputs/menu_board.png \
  --font modern \
  --effects background_box \
  --color "#F5F5DC"

echo ""
echo "=========================================="
echo "All CLI examples completed!"
echo "=========================================="

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-03-12

### BREAKING CHANGES
- **Removed npm package support** - Project is now Python-only
- **Removed CLI tool (`pto`)** - Use Python API directly
- **Removed Node.js dependencies** - All Node.js related files cleaned up
- **Simplified project structure** - Removed packaging infrastructure

### Changed
- **Installation method**: Changed from `npm install` to `git clone`
- **Font download**: Manual download instead of `pto download-fonts`
- **Documentation**: Updated all README files with Python-only instructions

### Removed
- `package.json`, `package-lock.json`, `.npmignore`
- `bin/cli.js`, `lib/index.js` (Node.js API)
- `scripts/install.js`, `postinstall.js`, `download-fonts.js`
- `test/` directory (Node.js tests)
- `types/` directory (TypeScript definitions)
- `.github/workflows/` (CI/CD workflows)
- `API.md`, `CONTRIBUTING.md`

### Retained
- Python core scripts: `prompt_separator.py`, `image_analyzer.py`, `text_renderer.py`
- `assets/fonts/` with bundled fonts
- `outputs/` folder for example outputs
- Multi-language README files
- SKILL.md documentation

---

## [1.0.2] - 2025-03-11

### Added
- **Detailed Font Documentation**: Added comprehensive font descriptions and recommendations
  - Font names in native languages (中文, 繁體中文, 한국어, English)
  - Font style categorization (Modern, Traditional, Humanist)
  - Recommended use cases for each font
- **Language-Specific Font Selection**: Updated SKILL.md with automatic font recommendations based on user's language

### Improved
- **Enhanced `pto download-fonts --list`**: Better formatting with language grouping and installation status
- **Updated READMEs**: All 5 language versions now include detailed font tables

---

## [1.0.1] - 2025-03-11

### Added
- **NPM Package Support**: Package now available on npm registry
- **CLI Tool (`pto`)**: Command-line interface for all operations
- **On-demand Font Download**: Fonts downloaded via `pto download-fonts` instead of bundled
- **Node.js API**: Full JavaScript/TypeScript API support
- **GitHub Actions CI/CD**: Automated testing and publishing workflows
- **TypeScript Definitions**: Complete type definitions in `types/`

### Changed
- **Package Size**: Reduced from ~76MB to 27.7KB (99.9% reduction)
- **Font Distribution**: Fonts are no longer bundled, downloaded on-demand
- **Installation**: Improved post-install checks and user feedback
- **Documentation**: Updated all README files with npm installation instructions

### Removed
- Bundled font files from npm package (now downloaded on demand)
- Example outputs and large asset files from package

---

## [1.0.0] - 2025-03-11

### Added
- Initial release of `perfect-text-overlay`
- Core Python functions: `separate_prompt`, `analyze_image`, `render_text_on_image`
- Multi-language font support including Chinese (Simplified/Traditional), Japanese, Korean, and English
- Professional typography effects: shadow, outline, background box
- Smart layout analysis with automatic safe zone detection
- Complete documentation with examples
- MIT license

---

## Version History Format

### Types of Changes

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

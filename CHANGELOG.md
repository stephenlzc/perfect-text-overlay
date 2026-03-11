# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-03-11

### Added
- Initial release of `perfect-text-overlay`
- Core API functions: `separatePrompt`, `analyzeImage`, `getTextPlacementSuggestions`, `renderTextOnImage`
- CLI interface with all commands: `separate`, `analyze`, `render`, `process`, `batch`, `fonts`, `init`, `doctor`
- Multi-language font support including Chinese (Simplified/Traditional), Japanese, Korean, and English
- Professional typography effects: shadow, outline, background box, border, arrows
- Smart layout analysis with automatic safe zone detection
- Complete documentation with API reference and examples
- React component example for frontend integration
- MIT license

### Features

#### Prompt Separation
- Extract text requirements from user prompts
- Generate clean image-only prompts for AI image generators
- Support for multiple text groups (flowcharts, infographics)

#### Image Analysis
- Detect safe zones for text placement
- Analyze color palette for optimal text color suggestions
- Calculate visual complexity maps
- Support for flowchart node detection

#### Text Rendering
- High-quality text overlay with anti-aliasing
- Multiple font styles with free commercial licenses
- Professional effects for enhanced readability
- Automatic text color contrast optimization
- Flowchart connection arrow rendering

#### CLI Tools
- Complete command-line interface
- Batch processing support
- Configuration file generation
- Installation diagnostics (`doctor` command)

### Included Fonts

| Font | Style | Language | License |
|------|-------|----------|---------|
| Noto Sans CJK SC Bold | Modern | Simplified Chinese | SIL OFL 1.1 |
| Noto Serif CJK SC Bold | Traditional | Simplified Chinese | SIL OFL 1.1 |
| Noto Sans CJK TC Bold | Traditional TW | Traditional Chinese (Taiwan) | SIL OFL 1.1 |
| Noto Sans CJK KR Bold | Korean | Korean | SIL OFL 1.1 |
| Roboto Bold | English | English/Latin | Apache 2.0 |
| Open Sans Bold | English | English/Latin | SIL OFL 1.1 |

### Documentation
- Comprehensive README in multiple languages (English, 简体中文, 繁體中文, 日本語, 한국어)
- Detailed API documentation (API.md)
- Usage examples:
  - Basic usage example (examples/basic-usage.js)
  - CLI examples (examples/cli-examples.sh)
  - Complete workflow example (examples/workflow-example.js)
  - React component example (examples/react-example.jsx)
- Contributing guidelines (CONTRIBUTING.md)
- Changelog (this file)

---

## [Unreleased]

### Planned
- Support for more font styles and languages
- Advanced layout templates for common use cases
- Integration with popular image generation APIs
- GUI application for non-developers
- Plugin system for custom effects
- Web-based demo and playground

---

## Version History Format

### Types of Changes

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

---

## Release Checklist

- [ ] Update version in `package.json`
- [ ] Update version in CLI `--version` output
- [ ] Update `CHANGELOG.md` with new version
- [ ] Run full test suite
- [ ] Update documentation if needed
- [ ] Create git tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
- [ ] Push tags: `git push origin v1.0.0`
- [ ] Publish to npm: `npm publish`
- [ ] Create GitHub release with release notes

---

## Contributing to Changelog

When submitting a PR, please add your changes to the `[Unreleased]` section following the format above. The maintainers will move them to the appropriate version section during release.

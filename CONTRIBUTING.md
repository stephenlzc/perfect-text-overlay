# Contributing to Perfect Text Overlay

Thank you for your interest in contributing to **Perfect Text Overlay**! We welcome contributions from the community and are pleased to have you join us.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Pull Requests](#pull-requests)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Accept responsibility and apologize when mistakes happen

By participating, you are expected to uphold these values.

---

## Getting Started

### Prerequisites

- **Node.js** 16.x or higher
- **npm** 8.x or higher
- **Python** 3.8+ (for image processing scripts)
- **Git**

### Quick Start

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/perfect-text-overlay.git
   cd perfect-text-overlay
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/stephenlzc/perfect-text-overlay.git
   ```

4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies (for image processing)
pip install Pillow numpy
```

### 2. Verify Installation

```bash
# Run diagnostics
npm run doctor

# or
perfect-text-overlay doctor
```

### 3. Run Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- tests/separate-prompt.test.js
```

### 4. Build (if applicable)

```bash
# Build the project
npm run build
```

### 5. Link for Local Testing

```bash
# Link the package globally
npm link

# Now you can use `perfect-text-overlay` command anywhere
perfect-text-overlay --version
```

---

## Project Structure

```
perfect-text-overlay/
├── assets/
│   └── fonts/              # Free commercial fonts
├── examples/               # Usage examples
│   ├── basic-usage.js
│   ├── cli-examples.sh
│   ├── workflow-example.js
│   └── react-example.jsx
├── references/             # Reference documentation
│   ├── trigger_keywords.md
│   ├── layout_patterns.md
│   └── flowchart_symbols.md
├── scripts/                # Core Python scripts
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── src/                    # Source code
│   ├── index.js            # Main entry point
│   ├── cli.js              # CLI implementation
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── API.md                  # API documentation
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT License
├── package.json            # Package configuration
└── README.md               # Project documentation
```

---

## How to Contribute

### Reporting Bugs

Before creating a bug report, please:

1. **Check existing issues** to avoid duplicates
2. **Use the latest version** to see if the bug is already fixed

When reporting a bug, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details**:
  - Node.js version: `node --version`
  - Package version: `perfect-text-overlay --version`
  - Operating system
- **Code sample** or command that demonstrates the issue
- **Screenshots** (if applicable)

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

### Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing issues** for similar requests
2. **Provide a clear use case** for the feature
3. **Explain why** it would be useful to most users
4. **Consider scope** - keep suggestions focused and achievable

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) when creating issues.

### Pull Requests

#### Before You Start

1. **Check existing issues** to see if someone is already working on it
2. **Comment on the issue** to claim it (or create a new one)
3. **Discuss major changes** before investing time in implementation

#### PR Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**:
   - Write clear, concise code
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting)
   - `refactor:` Code refactoring
   - `test:` Test changes
   - `chore:` Build/dependency changes

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Link related issues

#### PR Requirements

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (Unreleased section)
- [ ] No merge conflicts

#### PR Review Process

1. Maintainers will review within 3-5 business days
2. Address review comments promptly
3. Once approved, a maintainer will merge

---

## Coding Standards

### JavaScript/Node.js

We use [ESLint](https://eslint.org/) with the following configuration:

```bash
# Run linter
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

#### Style Guidelines

- **Indentation**: 2 spaces
- **Quotes**: Single quotes for strings
- **Semicolons**: Required
- **Line length**: Max 100 characters
- **Trailing commas**: Required in multiline

Example:

```javascript
// Good
const result = separatePrompt(userInput, {
  detectLanguage: true,
  enhancePrompt: true,
});

// Bad
var result=separatePrompt(userInput,{detectLanguage:true})
```

### Python (for scripts/)

We follow [PEP 8](https://pep8.org/) for Python code:

```bash
# Run Python linter
pylint scripts/*.py

# Format with black
black scripts/
```

#### Style Guidelines

- **Indentation**: 4 spaces
- **Line length**: Max 88 characters (Black default)
- **Docstrings**: Google style

Example:

```python
def separate_prompt(user_input: str) -> dict:
    """Extract text requirements from user prompt.
    
    Args:
        user_input: The original user prompt.
        
    Returns:
        Dictionary containing image_prompt and text_requirements.
    """
    # Implementation
    pass
```

### Documentation

- Use [JSDoc](https://jsdoc.app/) for JavaScript functions
- Include parameter types and descriptions
- Provide usage examples
- Keep README.md and API.md in sync

---

## Testing

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── separate-prompt.test.js
│   ├── image-analyzer.test.js
│   └── text-renderer.test.js
├── integration/            # Integration tests
│   └── workflow.test.js
├── fixtures/               # Test fixtures
│   ├── sample-images/
│   └── expected-outputs/
└── utils/                  # Test utilities
    └── helpers.js
```

### Writing Tests

```javascript
const { separatePrompt } = require('../src/index');

describe('separatePrompt', () => {
  test('extracts text from Chinese prompt', () => {
    const input = "生成海报，标题'新春快乐'";
    const result = separatePrompt(input);
    
    expect(result.has_text).toBe(true);
    expect(result.text_requirements.text_groups).toHaveLength(1);
    expect(result.text_requirements.text_groups[0].content).toBe('新春快乐');
  });
  
  test('returns no text for image-only prompt', () => {
    const input = "A beautiful landscape photo";
    const result = separatePrompt(input);
    
    expect(result.has_text).toBe(false);
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific file
npm test -- tests/unit/separate-prompt.test.js
```

---

## Documentation

### Updating Documentation

When making changes, update:

1. **README.md** - High-level overview and quick start
2. **API.md** - Detailed API reference
3. **examples/** - Usage examples if relevant
4. **CHANGELOG.md** - Add to Unreleased section

### Documentation Style

- Use clear, concise language
- Include code examples
- Keep examples runnable
- Use consistent formatting

---

## Release Process

(For maintainers)

1. **Update version**:
   ```bash
   npm version [major|minor|patch]
   ```

2. **Update CHANGELOG.md**:
   - Move Unreleased changes to new version section
   - Add release date

3. **Create PR** with version bump and changelog update

4. **After merge**, create release:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

5. **Publish to npm**:
   ```bash
   npm publish
   ```

6. **Create GitHub Release** with release notes

---

## Getting Help

- **Documentation**: Check README.md and API.md first
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: stephenlzc (at) gmail.com

---

## Recognition

Contributors will be recognized in:

- CHANGELOG.md for their contributions
- README.md contributors section (for significant contributions)
- Release notes

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).

---

Thank you for contributing to Perfect Text Overlay! 🎨

# Perfect Text Overlay - 퍼펙트 텍스트 오버레이

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![npm version](https://badge.fury.io/js/perfect-text-overlay.svg)](https://www.npmjs.com/package/perfect-text-overlay)

> 이미지 생성과 텍스트 렌더링을 분리하여 AI 생성 이미지의 텍스트 깨짐 문제를 해결합니다.

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | **한국어**

---

## 퀵 스타트

```bash
# 설치
npm install -g perfect-text-overlay

# 환경 확인
pto check

# 폰트 다운로드 (선택)
pto download-fonts --all

# 사용
pto separate "제목'안녕하세요'포스터 생성"
```

## 기능 개요

AI가 생성한 이미지에는 특히 중국어, 일본어, 한국어(CJK) 등의 비라틴 문자에서 텍스트가 깨지거나 불완전한 문제가 자주 발생합니다. 본 도구는 다음 단계로 이 문제를 해결합니다:

1. **분리** 프롬프트 → 이미지 전용 프롬프트 + 텍스트 요구사항
2. **생성** 깨끗한 기본 이미지 (사용자의 AI 도구 사용)
3. **분석** 이미지에서 최적의 텍스트 배치 영역 찾기
4. **렌더링** 완벽한 텍스트 (전문 타이포그래피 사용)

## 설치

### 요구사항
- Node.js 18+
- Python 3.8+
- Python 패키지: `pip install Pillow numpy`

### NPM 설치 (권장)
```bash
npm install -g perfect-text-overlay
```

### Git 클론
```bash
git clone https://github.com/stephenlzc/perfect-text-overlay
cd perfect-text-overlay
npm install
```

## CLI 사용법

```bash
# 프롬프트 분리
pto separate -p "영화 포스터, 제목은'인터스텔라'"

# 이미지 분석
pto analyze -i base.png -r '{"text_groups":[{"content":"안녕하세요"}]}'

# 텍스트 렌더링
pto render -i base.png -o final.png -p placements.json

# 완전한 워크플로우
pto workflow -p "포스터, 제목'세일'" -i base.png -o final.png

# 폰트 다운로드
pto download-fonts --list
pto download-fonts --all
```

## Node.js API

```javascript
const { separatePrompt, analyzeImage, renderTextOnImage } = require('perfect-text-overlay');

async function createPoster() {
  // 1. 프롬프트 분리
  const result = await separatePrompt('포스터, 제목"안녕하세요"');
  
  // 2. 이미지 분석 (result.image_prompt로 이미지 생성 후)
  const analysis = await analyzeImage('base.png', result.text_requirements);
  
  // 3. 텍스트 렌더링
  await renderTextOnImage('base.png', 'final.png', 
    analysis.placements, 
    { font_style: 'korean', effects: ['shadow'] }
  );
}
```

## 폰트 스타일

| 스타일 | 언어 | 설명 |
|--------|------|------|
| `modern` | 중국어 | 모던·심플 |
| `traditional` | 중국어 | 전통 송체 |
| `traditional_tw` | 중국어(대만) | 번체자 |
| `korean` | 한국어 | 한국어 최적화 |
| `english` | 영어/라틴 | Roboto 폰트 |
| `calligraphy` | 모든 언어 | 아트·서예 |
| `cartoon` | 모든 언어 | 귀여운 카툰 |

폰트 다운로드: `pto download-fonts --all`

## 프로젝트 구조

```
perfect-text-overlay/
├── bin/cli.js              # CLI 엔트리
├── lib/index.js            # Node.js API
├── scripts/                # Python 스크립트
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 폰트 (온디맨드 다운로드)
└── types/                  # TypeScript 정의
```

## 문서

- [API Reference](API.md) - 상세 API 문서
- [Contributing](CONTRIBUTING.md) - 기여 가이드
- [CHANGELOG](CHANGELOG.md) - 버전 기록

## 라이선스

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 다른 언어

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [日本語](README.ja.md) - 日本語ドキュメント

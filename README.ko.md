# GenImageText - 퍼펙트 텍스트 오버레이

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 이미지 생성과 텍스트 렌더링을 분리하여 AI 생성 이미지의 텍스트 깨짐 문제를 해결합니다.

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | **한국어**

---

## 기능 개요

AI가 생성한 이미지에는 특히 중국어, 일본어, 한국어(CJK) 등의 비라틴 문자에서 텍스트가 깨지거나 불완전한 문제가 자주 발생합니다. 본 도구는 다음 단계로 이 문제를 해결합니다:

1. **분리** 프롬프트 → 이미지 전용 프롬프트 + 텍스트 요구사항
2. **생성** 깨끗한 기본 이미지 (사용자의 AI 도구 사용)
3. **분석** 이미지에서 최적의 텍스트 배치 영역 찾기
4. **렌더링** 완벽한 텍스트 (전문 타이포그래피 사용)

---

## AI Agent용 자연어 설치

다음 프롬프트를 LLM Agent(Claude Code, Kimi Code, Cursor 등)에 복사하여 붙여넣으세요:

```
워크스페이스에 GenImageText 스킬을 설치하세요.
클론 출처: https://github.com/stephenlzc/GenImageText
모든 의존성을 설정하고 한국어 텍스트 추출 테스트를 실행하여 설치를 확인하세요.
```

---

## 설치

### 요구사항
- Python 3.8+
- Python 패키지: `pip install Pillow numpy`

### Git 클론

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
```

---

## 사용 방법

### 단계 1: 프롬프트 분리

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("영화 포스터, 제목은'인터스텔라'")
# result['image_prompt']: 텍스트가 없는 순수한 시각적 설명
# result['text_requirements']: 구조화된 텍스트 데이터
```

### 단계 2: 기본 이미지 생성

`image_prompt`를 사용하여 선호하는 AI 이미지 생성기(DALL-E, Midjourney, Stable Diffusion 등)로 이미지를 생성합니다

### 단계 3: 이미지 분석

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 단계 4: 텍스트 렌더링

```python
from scripts.text_renderer import render_text_on_image

output_path = render_text_on_image(
    image_path="base_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices={
        "font_style": "modern",
        "effects": ["shadow", "outline"]
    }
)
```

---

## 폰트 처리

폰트는 다음 우선순위로 로드됩니다:

1. **사용자 제공 폰트 경로**: 지정된 경우
2. **Skill 에셋**: `assets/fonts/` 디렉토리 확인
3. **시스템 폰트**: 일반적인 시스템 폰트 디렉토리 검색
4. **폴백**: 기본 PIL 폰트

### 언어별 폰트 추천

#### 중국어 간체
| 폰트 파일 | 폰트 이름 | 스타일 | 용도 |
|---------|---------|--------|------|
| `NotoSansCJKsc-Bold.otf` | 소원흑체 Bold | 모던 | 포스터, 테크 스타일, 비즈니스 |
| `NotoSerifCJKsc-Bold.otf` | 소원명조 Bold | 전통 | 문화 테마, 책 표지, 공식 문서 |

#### 중국어 번체
| 폰트 파일 | 폰트 이름 | 스타일 | 용도 |
|---------|---------|--------|------|
| `NotoSansCJKtc-Bold.otf` | 소원흑체 TC Bold | 모던 | 대만/홍콩, 비즈니스 문서 |

#### 한국어
| 폰트 파일 | 폰트 이름 | 스타일 | 용도 |
|---------|---------|--------|------|
| `NotoSansCJKkr-Bold.otf` | 본고딕 Bold | 모던 | 한국어 포스터, 모던 디자인 |

#### 영어/라틴
| 폰트 파일 | 폰트 이름 | 스타일 | 용도 |
|---------|---------|--------|------|
| `Roboto-Bold.ttf` | Roboto Bold | 모던 | 테크 포스터, 깔끔한 디자인 |
| `OpenSans-Bold.ttf` | Open Sans Bold | 휴머니스트 | 웹 콘텐츠, 다목적 사용 |

### 폰트 다운로드

Google Fonts 또는 Noto Fonts에서 폰트를 수동으로 다운로드하여 `assets/fonts/` 디렉토리에 배치할 수 있습니다:

- **Noto CJK 폰트**: https://www.google.com/get/noto/
- **Roboto**: https://fonts.google.com/specimen/Roboto
- **Open Sans**: https://fonts.google.com/specimen/Open+Sans

모든 폰트는 SIL Open Font License 또는 Apache License 2.0 하에서 무료로 상업적 사용이 가능합니다.

---

## 프로젝트 구조

```
GenImageText/
├── scripts/                # Python 스크립트
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # 폰트 디렉토리
└── references/             # 참고 자료
```

---

## 라이선스

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 다른 언어

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [日本語](README.ja.md) - 日本語ドキュメント

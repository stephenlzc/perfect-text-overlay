# GenImageText - 퍼펙트 텍스트 오버레이

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚠️ **중요**: 이것은 이미지 생성 도구가 아닙니다. 사용자의 AI 도구가 생성한 이미지에 완벽한 텍스트를 추가합니다.

> 이미지 생성과 텍스트 렌더링을 분리하여 AI 생성 이미지의 텍스트 깨짐 문제를 해결합니다.

![GenImageText Hero](https://raw.githubusercontent.com/stephenlzc/GenImageText/main/assets/hero_ko.png)

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | **한국어**

---

## 이 도구의 기능

AI가 생성한 이미지에는 특히 중국어, 일본어, 한국어(CJK) 등의 비라틴 문자에서 텍스트가 깨지거나 불완전한 문제가 자주 발생합니다. **본 도구는 다음 방법으로 이 문제를 해결합니다**:

1. **본 스킬** 프롬프트 분리 → 이미지 전용 프롬프트 + 텍스트 요구사항
2. **사용자의 AI 도구** 깨끗한 기본 이미지 생성(Midjourney、GPT Image 2、Stable Diffusion 등)
3. **본 스킬** 이미지에서 최적의 텍스트 배치 영역 찾기
4. **본 스킬** 완벽한 텍스트 렌더링(전문 타이포그래피 사용)

---

## 다국어 배치 생성 모드 (이커머스·학술·의료)

업스트림의 "단일 이미지 + 텍스트 합성" 워크플로를 **설정 기반·다국어 배치 파이프라인**으로 확장했습니다. 텍스트가 없는 기본 이미지 1장과 `template.yaml` 한 개, 그리고 7개 언어의 번역 JSON만 있으면 한 번의 실행으로 N개 언어의 완성 이미지를 뽑아낼 수 있습니다.

```
기본 이미지 1장 + template.yaml + translations/{en,de,ja,ko,zh-CN,zh-TW,ar}.json
                                ↓
                       N개 언어의 완성 이미지
```

### 핵심 특징

- **설정 기반 템플릿** — `presets/` 디렉토리에 카테고리별 8종 프리셋이 즉시 렌더링 가능한 상태로 포함되어 있습니다. **이커머스**: `amazon_main_image`(전자제품 메인 이미지 2000x2000)、`shopify_banner`(패션 배너 2400x1200)、`social_square`(뷰티 SNS 정사각형 1080x1080)、`poster_a4`(스마트워치 세일 포스터 2480x3508)、`coffee_promo`(카페/음료 프로모 1080x1080)、`home_decor_banner`(북유럽 인테리어 배너 2400x1200). **학술·의료**: `academic_flowchart`(연구 워크플로 다이어그램 2400x1350)、`medical_mechanism`(의학 메커니즘 다이어그램 1600x2000). `templates/`에 사용자 정의 프리셋을 추가할 수도 있으며, Pydantic 2.x로 스키마를 검증하므로 잘못된 필드는 즉시 오류로 표시됩니다.
- **미학 레이아웃 엔진** — `scripts/layout_composer.py`가 기본 이미지의 밝기/세이프존을 자동 분석하여 텍스트 위치를 미세 조정하고, 대비가 낮은 영역에서는 색상을 자동 보정하며, 필요 시 효과(그림자·외곽선·글로우)를 자동으로 부여합니다.
- **풍부한 텍스트 효과** — 그림자, 외곽선, 글로우뿐 아니라 반투명 둥근 배경 패널(`backdrop`)과 `badge` 타입 레이어의 자동 알약(pill) 캡슐 형태까지 지원합니다. 텍스트는 PIL로 직접 그려지며 `BatchPipeline`의 기본 렌더러는 `pil`입니다.
- **RTL 완벽 지원** — 아랍어(`ar`) 글리프가 우→좌로 자연스럽게 렌더링되며, `assets/fonts/NotoSansArabic-Bold.ttf`로 전용 아랍어 폰트도 포함되어 있습니다(전 7개 언어 글자 렌더링 정상 확인).
- **4개 동시 배치** — 한 번의 `batch` 실행으로 미리 정의된 모든 언어 버전을 동시에 출력합니다.

### 3줄 퀵스타트

```bash
# 1) 프리셋으로 프로젝트 스캐폴드 생성
.venv/bin/python gen_ecommerce.py init --preset amazon_main_image --project-dir projects/winter_2026

# 2) 프롬프트 추출 → 사용자 AI 도구로 기본 이미지 생성 → OCR 점검
.venv/bin/python gen_ecommerce.py prompt --config projects/winter_2026/template.yaml
.venv/bin/python gen_ecommerce.py check --image projects/winter_2026/base_image.png

# 3) 7개 언어 모두 한 번에 렌더링
.venv/bin/python gen_ecommerce.py batch --config projects/winter_2026/template.yaml \
    --base-image projects/winter_2026/base_image.png --output projects/winter_2026/renders
```

`gen_ecommerce.py`는 `init` / `prompt` / `batch` / `render` / `validate` / `check`의 6개 서브커맨드를 제공합니다. 전체 레퍼런스, `template.yaml` 스키마, 폰트 매핑 규칙, RTL 노트는 [`README_ECOMMERCE.md`](README_ECOMMERCE.md)를 참고하세요. 각 프리셋 자체의 노트는 [`presets/`](presets/) 아래의 프리셋별 `README.md`에서 확인할 수 있습니다.

---

## 지원되는 AI 이미지 생성 도구

2단계(기본 이미지 생성)에는 다음 **어떤** 도구도 사용할 수 있습니다:

| 도구 | 플랫폼 | 최적의 용도 |
|------|--------|------------|
| **Midjourney** | Discord | 고품질 아트 이미지 |
| **GPT Image 2** | ChatGPT、OpenAI API | 사용하기 쉽고, 프롬프트 이해가 우수 |
| **Stable Diffusion** | 로컬、Hugging Face、Replicate | 오픈소스、커스터마이징 가능 |
| **Google Gemini/Imagen** | Google AI Studio、Gemini Pro | Google 에코시스템 통합 |
| **Adobe Firefly** | Adobe Creative Suite | 상업적 사용에 안전 |
| **Microsoft Bing Image Creator** | Bing、Microsoft Designer | 무료, GPT Image 탑재 |
| **Flux.1** | API、로컬 | 고품질 오픈소스 모델 |
| **Leonardo.ai** | 웹、앱 | 게임 에셋, 컨셉 아트 |
| **Ideogram** | 웹 | 이미지 내 텍스트 렌더링 |
| **Playground AI** | 웹 | 무료 플랜 있음 |

**중요한 포인트**: 본 스킬은 **이미지를 생성하지 않습니다**. 위 도구가 생성한 이미지에만 텍스트를 추가합니다. 이커머스 배치 모드 역시 동일한 원칙을 따르며, 1단계의 `prompt` 서브커맨드가 기본 이미지 생성용 프롬프트를 그대로 출력해 줍니다.

---

## AI Agent용 자연어 설치

다음 프롬프트를 LLM Agent(Claude Code, Kimi Code, Cursor 등)에 복사하여 붙여넣으세요:

```
워크스페이스에 GenImageText 스킬을 설치하세요.
클론 출처: https://github.com/stephenlzc/GenImageText
모든 의존성을 설정하고 한국어 텍스트 추출 테스트를 실행하여 설치를 확인하세요.
```

이커머스 배치 모드를 사용하려면 추가로 `pip install -r requirements.txt`로 전체 의존성(Pillow, numpy, cairosvg, jinja2, pydantic, pyyaml, pytesseract, click)을 설치하면 됩니다.

---

## 설치

### 요구사항
- Python 3.8+
- Python 패키지: `pip install Pillow numpy`
- 이커머스 배치 모드 사용 시: `pip install -r requirements.txt`(Pillow, numpy, cairosvg, jinja2, pydantic, pyyaml, pytesseract, click)
- 선택 사항: Tesseract OCR(`check` 서브커맨드의 잔여 텍스트 감지에 사용)

### Git 클론

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
```

---

## 사용 방법

### 단계 1: 프롬프트 분리(본 스킬)

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("영화 포스터, 제목은'인터스텔라'")
# result['image_prompt']: 텍스트가 없는 순수한 시각적 설명
# result['text_requirements']: 구조화된 텍스트 데이터
```

### 단계 2: 기본 이미지 생성(사용자의 AI 도구)

> ⚠️ **이 단계에서는 본 스킬이 아닌 사용자의 AI 이미지 생성 도구를 사용합니다.**

`image_prompt`를 사용하여 선호하는 AI 이미지 생성기로 이미지를 생성합니다:
- **Midjourney** - Discord 기반 생성
- **GPT Image 2**(ChatGPT Plus、OpenAI API)
- **Stable Diffusion** - 로컬 또는 클라우드 기반
- **Google Gemini/Imagen**
- **Adobe Firefly**
- **Microsoft Bing Image Creator**(무료)
- **기타 선호하는 AI 이미지 도구**

### 단계 3: 이미지 분석(본 스킬)

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 단계 4: 텍스트 렌더링(본 스킬)

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

### 단계 5(선택): 배치 모드로 한 번에 다국어 생성

`gen_ecommerce.py batch`를 사용하면 위 4단계를 설정 기반으로 자동화하고, 한 번의 실행으로 모든 지원 언어 버전을 출력할 수 있습니다. 자세한 사용법은 위의 「다국어 배치 생성 모드 (이커머스·학술·의료)」 절과 [`README_ECOMMERCE.md`](README_ECOMMERCE.md)를 참고하세요.

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

#### 아랍어(RTL)
| 폰트 파일 | 폰트 이름 | 스타일 | 용도 |
|---------|---------|--------|------|
| `NotoSansArabic-Bold.ttf` | Noto Sans Arabic Bold | 모던 | 아랍어 권역(이집트, 사우디, UAE 등) |

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
├── gen_ecommerce.py          # 이커머스 배치 CLI (init / prompt / batch / render / validate / check)
├── scripts/                  # 핵심 모듈
│   ├── prompt_separator.py   # 업스트림: 프롬프트 분리
│   ├── image_analyzer.py     # 업스트림: 이미지 분석
│   ├── text_renderer.py      # PIL 기반 텍스트 합성 (그림자/외곽선/글로우/배경패널/필)
│   ├── layout_composer.py    # 미학 레이아웃 엔진 (밝기/세이프존 분석 → 위치·대비·효과 자동 조정)
│   ├── config_loader.py      # Pydantic 2.x 기반 template.yaml 스키마 검증
│   ├── i18n_manager.py       # 번역 로딩, RTL 판정, 언어별 폰트 매핑
│   ├── template_engine.py    # Jinja2 기반 SVG 텍스트 레이어 생성
│   └── batch_pipeline.py     # BatchPipeline (render_single, run)
├── presets/                  # 카테고리별 즉시 사용 가능한 8종 프리셋
│   ├── amazon_main_image/    # 2000x2000, product_main
│   ├── shopify_banner/       # 2400x1200, banner
│   ├── social_square/        # 1080x1080, social
│   ├── poster_a4/            # 2480x3508, poster
│   ├── coffee_promo/         # 1080x1080, social
│   ├── home_decor_banner/    # 2400x1200, banner
│   ├── academic_flowchart/   # 2400x1350, academic
│   └── medical_mechanism/    # 1600x2000, medical
├── templates/                # 사용자 정의 템플릿 (.gitkeep만 추적)
├── outputs/                  # 기본 batch 출력 디렉토리
├── assets/
│   ├── fonts/                # Roboto, OpenSans, NotoSans CJK sc/tc/kr,
│   │                         #   NotoSerif CJK sc, NotoSans Arabic
│   ├── hero_base.png         # 무텍스트 기본 이미지(codex-image-gen으로 생성)
│   ├── hero.png              # 영문 기본 hero
│   ├── hero_ko.png           # 한국어 hero
│   ├── hero_ja.png           # 일본어 hero
│   ├── hero_zh-CN.png        # 간체 hero
│   └── hero_zh-TW.png        # 번체 hero
├── references/               # 참고 자료(플로차트 기호, 레이아웃 패턴, 트리거 키워드)
├── README_ECOMMERCE.md       # 이커머스 배치 모드 상세 레퍼런스
├── SKILL.md
├── requirements.txt
└── README.md (외 다국어 README)
```

---

## 감사 / 크레딧

이 저장소의 데모용 자산은 모두 같은 저자의 자매 프로젝트인 [codex-image-gen](https://github.com/stephenlzc/codex-image-gen)으로 생성되었습니다:

- `presets/*/sample_base_image.png` — 각 프리셋의 무텍스트 기본 이미지 8종
- `assets/hero_base.png` — 영문/한/일/중 hero의 무텍스트 기본 이미지

codex-image-gen은 로컬 Codex CLI로 OAuth 로그인하여 무료로 이미지를 생성하는 도구입니다. **API 키가 필요하지 않으며** 동일 환경에서 본 프로젝트의 베이스 이미지를 직접 만들어낼 수 있어, "텍스트 없는 깨끗한 배경 → 7개 언어 텍스트 합성"의 데모 흐름을 한 번에 재현해 볼 수 있습니다.

> 🔗 https://github.com/stephenlzc/codex-image-gen

---

## 라이선스

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 다른 언어

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [日本語](README.ja.md) - 日本語ドキュメント
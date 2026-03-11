# Perfect Text Overlay - 퍼펙트 텍스트 오버레이

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 이미지 생성과 텍스트 렌더링을 분리하여 AI 생성 이미지의 텍스트 깨짐 문제를 해결합니다.

## 개요

AI가 생성한 이미지에는 특히 중국어, 일본어, 한국어(CJK) 등의 비라틴 문자에서 텍스트가 깨지거나 불완전한 문제가 자주 발생합니다. 이 스킬은 이미지 생성과 텍스트 렌더링을 두 개의 독립적인 단계로 분리하여 이 문제를 해결합니다:

1. **텍스트 없는 깨끗한 기본 이미지 생성**
2. **최적의 텍스트 배치 영역 분석**
3. **전문적인 타이포그래피와 효과로 텍스트 렌더링**

## 기능

- 🎯 **다국어 지원**: 중국어 간체·번체, 일본어, 한국어, 영어
- 🖼️ **다양한 이미지 유형**: 포스터, 플로우차트, 인포그래픽, 소셜 미디어 그래픽
- ✨ **전문 타이포그래피**: 그림자, 외곽선, 배경 상자
- 🔤 **묣로 상용 가능한 폰트**: 6개의 오픈 소스 폰트 포함 (SIL OFL / Apache 2.0)
- 🎨 **스마트 레이아웃 분석**: 텍스트 배치를 위한 안전 영역 자동 감지

## 자연어 설치 (AI Agent용)

다음 프롬프트를 LLM Agent(Claude Code, Kimi Code, Cursor 등)에 복사하여 붙여넣으세요:

```
워크스페이스에 perfect-text-overlay 스킬을 설치하세요.
클론 출처: https://github.com/zhiconglian/perfect-text-overlay
모든 의존성을 설정하고 한국어 텍스트 추출 테스트를 실행하여 설치를 확인하세요.
```

## 워크플로우

```
단계 1: 프롬프트 분리
├─ 사용자 프롬프트에서 텍스트 요구사항 추출
├─ 이미지 전용 프롬프트 생성 (텍스트 설명 없음)
└─ 출력: 이미지 프롬프트 + 텍스트 요구사항

단계 2: 이미지 생성
├─ 이미지 전용 프롬프트를 사용하여 기본 이미지 생성
└─ 출력: 텍스트 없는 깨끗한 이미지

단계 3: 이미지 분석
├─ 이미지를 분석하여 텍스트 배치를 위한 안전 영역 찾기
├─ 레이아웃 구조 감지 (플로우차트용)
└─ 출력: 좌표가 포함된 레이아웃 제안

단계 4: 사용자 맞춤 설정
├─ 사용자에게 5가지 맞춤 설정 질문
│  1. 장면 유형 (포스터/플로우차트/인포그래픽)
│  2. 텍스트 내용 확인
│  3. 폰트 스타일 선택
│  4. 텍스트 위치 설정
│  5. 효과 및 스타일 옵션
└─ 출력: 사용자 선택

단계 5: 텍스트 오버레이
├─ 전문적인 타이포그래피로 텍스트 렌더링
└─ 출력: 완벽한 텍스트가 포함된 최종 이미지
```

## 설치

```bash
# 저장소 클론
git clone <저장소 URL>
cd perfect-text-overlay

# 의존성 설치
pip install Pillow numpy

# 선택 사항: 추가 시스템 폰트 설치
# macOS: 폰트가 자동으로 감지됩니다
# Linux: sudo apt-get install fonts-noto-cjk
# Windows: 폰트가 자동으로 감지됩니다
```

## 사용 방법

### 기본 예제

```python
from scripts.prompt_separator import separate_prompt
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions
from scripts.text_renderer import render_text_on_image

# 단계 1: 프롬프트 분리
user_input = "포스터를 생성하고 제목은'안녕하세요 세계'"
result = separate_prompt(user_input)

# result['image_prompt']: "포스터 생성..."
# result['text_requirements']: {"text_groups": [{"content": "안녕하세요 세계"}]}

# 단계 2: 기본 이미지 생성 (선호하는 이미지 생성기 사용)
# ... result['image_prompt']를 사용하여 이미지 생성 ...

# 단계 3: 이미지 분석
text_requirements = result['text_requirements']
analysis = analyze_image("generated_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)

# 단계 4: 사용자 선택 (일반적으로 UI를 통해 수집)
user_choices = {
    "font_style": "korean",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "text_color": (255, 215, 0),  # 골드
}

# 단계 5: 텍스트 렌더링
output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices=user_choices
)
```

### 폰트 스타일

다음 폰트 스타일이 지원됩니다:

| 스타일 | 폰트 | 언어 | 라이선스 |
|------|------|----------|---------|
| `modern` | Noto Sans CJK SC Bold | 중국어 간체 | SIL OFL 1.1 |
| `traditional` | Noto Serif CJK SC Bold | 중국어 간체 | SIL OFL 1.1 |
| `traditional_tw` | Noto Sans CJK TC Bold | 중국어 번체 (대만) | SIL OFL 1.1 |
| `korean` | Noto Sans CJK KR Bold | 한국어 | SIL OFL 1.1 |
| `english` | Roboto Bold | 영어/라틴 | Apache 2.0 |
| `cartoon` | Noto Sans CJK SC Bold | 범용 | SIL OFL 1.1 |
| `calligraphy` | 시스템 폰트 | 시스템 종속 | 다양함 |

## 프로젝트 구조

```
perfect-text-overlay/
├── assets/
│   └── fonts/              # 묣로 상용 가능한 폰트
│       ├── NotoSansCJKsc-Bold.otf    # 본고딕 중국어 간체
│       ├── NotoSerifCJKsc-Bold.otf   # 본명조 중국어 간체
│       ├── NotoSansCJKtc-Bold.otf    # 본고딕 중국어 번체
│       ├── NotoSansCJKkr-Bold.otf    # 본고딕 한국어
│       ├── Roboto-Bold.ttf           # Roboto 영어
│       ├── OpenSans-Bold.ttf         # Open Sans 영어
│       └── LICENSE.md
├── references/
│   ├── trigger_keywords.md    # 다국어 트리거 키워드
│   ├── layout_patterns.md     # 타이포그래피 모범 사례
│   └── flowchart_symbols.md   # 플로우차트 디자인 표준
├── scripts/
│   ├── prompt_separator.py    # 프롬프트에서 텍스트 추출
│   ├── image_analyzer.py      # 이미지 레이아웃 분석
│   └── text_renderer.py       # 이미지에 텍스트 렌더링
├── SKILL.md                   # 상세 스킬 문서
└── README.md                  # 주 문서 (영어)
```

## 지원되는 사용 사례

### 1. 제목이 있는 포스터
```
사용자: "SF 영화 포스터를 생성하고 제목은'인터스텔라'"
↓
단계 1: 이미지 프롬프트 = "sci-fi movie poster, space theme..."
        텍스트 = "인터스텔라"
↓
단계 2: 기본 이미지 생성
↓
단계 3: 하단 중앙 배치 제안
↓
단계 4: 모던 폰트, 하단 중앙, 그림자+외곽선
↓
단계 5: 하단에 큰 제목 렌더링
```

### 2. 플로우차트
```
사용자: "사용자 등록 플로우차트 생성: 1.정보 입력 2.이메일 확인 3.완료"
↓
단계 1: 플로우차트 노드 감지
↓
단계 2: 기본 이미지 생성
↓
단계 3: 3개 노드 위치 감지
↓
단계 4: 수평 플로우, 상자+화살표 추가
↓
단계 5: 연결 화살표가 있는 3개의 상자 노드 렌더링
```

### 3. 인포그래픽
```
사용자: "인포그래픽을 생성하고'매출: $100K'와'성장: +50%'을 표시"
↓
단계 1: 데이터 포인트 추출
↓
단계 2: 기본 이미지 생성
↓
단계 3: 각 통계 데이터의 안전 영역 찾기
↓
단계 4: 큰 숫자, 대비 색상
↓
단계 5: 전문적인 데이터 시각화 렌더링
```

## API 참조

### 프롬프트 분리기

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("제목 'Hello World'의 포스터 생성")
# 반환값: {
#     "has_text": True,
#     "image_prompt": "Create poster...",
#     "text_requirements": {...}
# }
```

### 이미지 분석기

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### 텍스트 렌더러

```python
from scripts.text_renderer import render_text_on_image

render_text_on_image(
    image_path="input.png",
    output_path="output.png",
    placements=[...],
    user_choices={...}
)
```

## 트리거 키워드

사용자 입력에 다음이 포함된 경우 이 스킬이 트리거됩니다:

- **이미지 유형 키워드**: 포스터, 플로우차트, 인포그래픽, 배너 등
- **텍스트 요구사항 키워드**: 쓰기, 제목, 텍스트, 캡션 등

전체 다국어 키워드 목록은 [references/trigger_keywords.md](references/trigger_keywords.md)를 참조하세요.

## 폰트 라이선스

포함된 모든 폰트는 묣로 상용 가능합니다:

- **Noto Sans/Serif CJK**: SIL Open Font License 1.1
- **Roboto**: Apache License 2.0
- **Open Sans**: SIL Open Font License 1.1

전체 라이선스 세부정보는 [assets/fonts/LICENSE.md](assets/fonts/LICENSE.md)를 참조하세요.

## 기여

기여를 환영합니다! 언제든지 풀 리퀘스트를 제출해 주세요.

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 감사의 말

- [Noto Fonts](https://github.com/notofonts/noto-cjk) by Google & Adobe
- [Roboto](https://github.com/googlefonts/roboto) by Google
- [Open Sans](https://github.com/googlefonts/opensans) by Google

---

**다른 언어로 읽기:**
[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

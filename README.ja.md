# GenImageText - パーフェクトテキストオーバーレイ

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 画像生成とテキストレンダリングを分離することで、AI生成画像の文字化け問題を解決します。

![GenImageText Hero](https://raw.githubusercontent.com/stephenlzc/GenImageText/main/assets/hero.png)

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | **日本語** | [한국어](README.ko.md)

---

## 機能概要

AIが生成した画像には、特に中国語・日本語・韓国語（CJK）などの非ラテン文字で、文字が化けたり不完全になったりする問題がよくあります。本ツールは以下のステップでこの問題を解決します：

1. **分離** プロンプト → 画像専用プロンプト + テキスト要件
2. **生成** クリーンなベース画像（お好みのAIツール使用）
3. **分析** 画像から最適なテキスト配置領域を特定
4. **レンダリング** 完璧なテキスト（プロフェッショナルなタイポグラフィ使用）

---

## AI Agent向け自然言語インストール

以下のプロンプトをLLM Agent（Claude Code、Kimi Code、Cursorなど）にコピー＆ペーストしてください：

```
ワークスペースに GenImageText スキルをインストールしてください。
クローン元：https://github.com/stephenlzc/GenImageText
すべての依存関係を設定し、日本語テキスト抽出テストを実行してインストールを確認してください。
```

---

## インストール

### 要件
- Python 3.8+
- Pythonパッケージ：`pip install Pillow numpy`

### Gitクローン

```bash
git clone https://github.com/stephenlzc/GenImageText
cd GenImageText
```

---

## 使用方法

### ステップ 1：プロンプトを分離

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("映画ポスター、タイトルは'インターステラー'")
# result['image_prompt']: テキストを含まない純粋な視覚的説明
# result['text_requirements']: 構造化されたテキストデータ
```

### ステップ 2：ベース画像を生成

`image_prompt` を使用して、お好みのAI画像生成ツール（DALL-E、Midjourney、Stable Diffusion など）で画像を生成します

### ステップ 3：画像を分析

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### ステップ 4：テキストをレンダリング

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

## フォントの取り扱い

フォントは以下の優先順位で読み込まれます：

1. **ユーザー提供のフォントパス**：指定されている場合
2. **Skill アセット**：`assets/fonts/` ディレクトリをチェック
3. **システムフォント**：一般的なシステムフォントディレクトリを検索
4. **フォールバック**：デフォルトのPILフォント

### 言語別フォント推奨

#### 簡体字中国語
| フォントファイル | フォント名 | スタイル | 用途 |
|-----------------|-----------|---------|------|
| `NotoSansCJKsc-Bold.otf` | 源ノ角ゴシック Bold | モダン | ポスター、テックスタイル、ビジネス |
| `NotoSerifCJKsc-Bold.otf` | 源ノ明朝 Bold | 伝統 | 文化テーマ、書籍表紙、正式文書 |

#### 繁体字中国語
| フォントファイル | フォント名 | スタイル | 用途 |
|-----------------|-----------|---------|------|
| `NotoSansCJKtc-Bold.otf` | 源ノ角ゴシック TC Bold | モダン | 台湾/香港、ビジネス文書 |

#### 韓国語
| フォントファイル | フォント名 | スタイル | 用途 |
|-----------------|-----------|---------|------|
| `NotoSansCJKkr-Bold.otf` | 本ゴシック Bold | モダン | 韓国語ポスター、モダンデザイン |

#### 英語/ラテン
| フォントファイル | フォント名 | スタイル | 用途 |
|-----------------|-----------|---------|------|
| `Roboto-Bold.ttf` | Roboto Bold | モダン | テックポスター、クリーンなデザイン |
| `OpenSans-Bold.ttf` | Open Sans Bold | ヒューマニスト | Webコンテンツ、多目的使用 |

### フォントのダウンロード

Google Fonts または Noto Fonts からフォントを手動でダウンロードし、`assets/fonts/` ディレクトリに配置できます：

- **Noto CJK フォント**：https://www.google.com/get/noto/
- **Roboto**：https://fonts.google.com/specimen/Roboto
- **Open Sans**：https://fonts.google.com/specimen/Open+Sans

すべてのフォントはSIL Open Font License または Apache License 2.0 の下で無料で商用利用可能です。

---

## プロジェクト構造

```
GenImageText/
├── scripts/                # Pythonスクリプト
│   ├── prompt_separator.py
│   ├── image_analyzer.py
│   └── text_renderer.py
├── assets/fonts/           # フォントディレクトリ
└── references/             # 参考資料
```

---

## ライセンス

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 他の言語

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [한국어](README.ko.md) - 한국어 문서

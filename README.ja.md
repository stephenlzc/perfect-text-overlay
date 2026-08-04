# GenImageText - パーフェクトテキストオーバーレイ

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚠️ **重要**: これは画像生成ツールではありません。お使いの AI ツールが生成した画像に完璧なテキストを追加します。

> 画像生成とテキストレンダリングを分離することで、AI生成画像の文字化け問題を解決します。

![GenImageText Hero](https://raw.githubusercontent.com/stephenlzc/GenImageText/main/assets/hero_ja.png)

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | **日本語** | [한국어](README.ko.md)

---

## このツールの機能

AIが生成した画像には、特に中国語・日本語・韓国語（CJK）などの非ラテン文字で、文字が化けたり不完全になったりする問題がよくあります。**本ツールは以下の方法でこの問題を解決します**：

1. **本スキル** プロンプトを分離 → 画像専用プロンプト + テキスト要件
2. **お使いの AI ツール** クリーンなベース画像を生成（Midjourney、GPT Image 2、Stable Diffusion など）
3. **本スキル** 画像を分析して最適なテキスト配置領域を特定
4. **本スキル** 完璧なテキストをレンダリング（プロフェッショナルなタイポグラフィ使用）

---

## サポートされている AI 画像生成ツール

ステップ 2（画像生成）には以下の**いずれか**のツールを使用できます：

| ツール | プラットフォーム | 最適な用途 |
|--------|----------------|-----------|
| **Midjourney** | Discord | 高品質なアート画像 |
| **GPT Image 2** | ChatGPT、OpenAI API | 使いやすく、プロンプト理解が優秀 |
| **Stable Diffusion** | ローカル、Hugging Face、Replicate | オープンソース、カスタマイズ可能 |
| **Google Gemini/Imagen** | Google AI Studio、Gemini Pro | Google エコシステム統合 |
| **Adobe Firefly** | Adobe Creative Suite | 商業利用に安全 |
| **Microsoft Bing Image Creator** | Bing、Microsoft Designer | 無料、GPT Image 搭載 |
| **Flux.1** | API、ローカル | 高品質なオープンソースモデル |
| **Leonardo.ai** | Web、アプリ | ゲームアセット、コンセプトアート |
| **Ideogram** | Web | 画像内のテキストレンダリング |
| **Playground AI** | Web | 無料プランあり |

**重要なポイント**: 本スキルは**画像を生成しません**。上記ツールが生成した画像にのみテキストを追加します。

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

### ステップ 1：プロンプトを分離（本スキル）

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("映画ポスター、タイトルは'インターステラー'")
# result['image_prompt']: テキストを含まない純粋な視覚的説明
# result['text_requirements']: 構造化されたテキストデータ
```

### ステップ 2：ベース画像を生成（お使いの AI ツール）

> ⚠️ **このステップでは本スキルではなく、お使いの AI 画像生成ツールを使用します。**

`image_prompt` を使用して、お好みの AI 画像生成ツールで画像を生成します：
- **Midjourney** - Discordベースの生成
- **GPT Image 2**（ChatGPT Plus、OpenAI API）
- **Stable Diffusion** - ローカルまたはクラウドベース
- **Google Gemini/Imagen**
- **Adobe Firefly**
- **Microsoft Bing Image Creator**（無料）
- **その他お好みの AI 画像ツール**

### ステップ 3：画像を分析（本スキル）

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("base_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### ステップ 4：テキストをレンダリング（本スキル）

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

## 多言語バッチ生成モード（EC・学術・医療）

ステップ 1〜4 の単発ワークフローに加え、**多言語バッチ生成モード**を同梱しています。Eコマースはもちろんのこと、学術・医療の図解もカバーし、1 枚の文字なしベース画像 × 7 言語（en / de / ja / ko / zh-CN / zh-TW / ar）で、N 枚の成品をワンコマンドで一括生成できます。

### 特徴

- **設定駆動テンプレート** — `presets/` 直下の 8 種類に `template.yaml` と 7 言語分の翻訳 JSON が同梱済み。`gen_ecommerce.py init --preset <name>` で雛形をプロジェクトディレクトリに展開できます。
  - **Eコマース**：amazon_main_image（電子製品メイン画像 2000x2000）、shopify_banner（ファッションバナー 2400x1200）、social_square（コスメ SNS 方形 1080x1080）、poster_a4（スマートウォッチ セールポスター 2480x3508）、coffee_promo（カフェ・飲食プロモ 1080x1080）、home_decor_banner（北欧インテリア バナー 2400x1200）
  - **学術・医療**：academic_flowchart（研究ワークフロー図 2400x1350）、medical_mechanism（医療メカニズム図 1600x2000）
- **美学レイアウトエンジン** — `scripts/layout_composer.py` がベース画像の明るさ・色・安全エリア・可読性を解析し、文字位置の微調整、コントラスト不足時の自動カラー補正、可読性が低い領域への `backdrop` / `shadow` 自動付与を行います。
- **豊富な文字効果** — 影（`shadow`）・縁取り（`outline`）・光彩（`glow`）・半透明パネル（`backdrop`）に加え、`badge` タイプは自動でピル（pill）型カプセルになります。
- **RTL 完全対応** — アラビア語などの右から左に書く言語も字形と整形が正しくレンダリングされます（`assets/fonts/NotoSansArabic-Bold.ttf` 同梱）。
- **4 並列バッチ** — `BatchPipeline` が `ThreadPoolExecutor(max_workers=4)` で複数言語を同時描画し、所要時間を短縮します。

### クイックスタート（3 行）

```bash
.venv/bin/python gen_ecommerce.py init    --preset amazon_main_image --project-dir projects/winter_2026
.venv/bin/python gen_ecommerce.py prompt  --config presets/amazon_main_image/template.yaml   # プロンプトを取り出し、お使いの AI 画像生成ツールで base_image.png を生成
.venv/bin/python gen_ecommerce.py batch   --config presets/amazon_main_image/template.yaml --base-image projects/winter_2026/base_image.png --output projects/winter_2026/renders
```

詳細は [`README_ECOMMERCE.md`](README_ECOMMERCE.md) を参照してください。プリセット一覧とサンプルベース画像は [`presets/`](presets/) にあります。

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

## 謝辞

`presets/` 配下のサンプルベース画像（`sample_base_image.png`）と、このリポジトリの hero 用ベース画像（`assets/hero_base.png`）は、作者の姉妹プロジェクト **[codex-image-gen](https://github.com/stephenlzc/codex-image-gen)** で生成しました。codex-image-gen はローカル Codex CLI 経由で OAuth ログインして動く無料の画像生成ツールで、API キーは不要です。ベース画像生成の代替手段としておすすめです。

---

## ライセンス

MIT © [stephenlzc](https://github.com/stephenlzc)

---

## 🌍 他の言語

- [English](README.md) - English Documentation
- [简体中文](README.zh-CN.md) - 简体中文文档
- [繁體中文](README.zh-TW.md) - 繁體中文文檔
- [한국어](README.ko.md) - 한국어 문서

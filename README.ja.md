# Perfect Text Overlay - パーフェクトテキストオーバーレイ

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 画像生成とテキストレンダリングを分離することで、AI生成画像の文字化け問題を解決します。

🌐 [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | **日本語** | [한국어](README.ko.md)

---

## 概要

AIが生成した画像には、特に中国語・日本語・韓国語（CJK）などの非ラテン文字で、文字が化けたり不完全になったりする問題がよくあります。このスキルは、画像生成とテキストレンダリングを2つの独立したステップに分離することで、この問題を解決します：

1. **テキストなしのクリーンなベース画像を生成**
2. **最適なテキスト配置領域を分析**
3. **プロフェッショナルなタイポグラフィとエフェクトでテキストをレンダリング**

## 機能

- 🎯 **多言語サポート**：簡体字中国語・繁体字中国語・日本語・韓国語・英語
- 🖼️ **複数の画像タイプ**：ポスター・フローチャート・インフォグラフィック・ソーシャルメディア画像
- ✨ **プロフェッショナルなタイポグラフィ**：シャドウ・アウトライン・背景ボックス
- 🔤 **無料商用フォント**：6つのオープンソースフォントを含む（SIL OFL / Apache 2.0）
- 🎨 **スマートレイアウト分析**：テキスト配置の安全ゾーンを自動検出

## 自然言語インストール（AI Agent 向け）

以下のプロンプトを LLM Agent（Claude Code、Kimi Code、Cursor など）にコピー＆ペーストしてください：

```
ワークスペースに perfect-text-overlay スキルをインストールしてください。
クローン元：https://github.com/stephenlzc/perfect-text-overlay
すべての依存関係を設定し、日本語テキスト抽出テストを実行してインストールを確認してください。
```

## ワークフロー

```
ステップ 1：プロンプトの分離
├─ ユーザープロンプトからテキスト要件を抽出
├─ 画像専用プロンプトを生成（テキスト記述なし）
└─ 出力：画像プロンプト + テキスト要件

ステップ 2：画像生成
├─ 画像専用プロンプトを使用してベース画像を生成
└─ 出力：テキストなしのクリーンな画像

ステップ 3：画像分析
├─ 画像を分析し、テキスト配置の安全ゾーンを特定
├─ レイアウト構造を検出（フローチャート用）
└─ 出力：座標付きレイアウト提案

ステップ 4：ユーザーカスタマイズ
├─ ユーザーに5つのカスタマイズ質問をする
│  1. シーンタイプ（ポスター/フローチャート/インフォグラフィック）
│  2. テキスト内容の確認
│  3. フォントスタイルの選択
│  4. テキスト位置の設定
│  5. エフェクトとスタイルオプション
└─ 出力：ユーザー選択

ステップ 5：テキストオーバーレイ
├─ プロフェッショナルなタイポグラフィでテキストをレンダリング
└─ 出力：完璧なテキストを含む最終画像
```

## インストール

```bash
# リポジトリをクローン
git clone <リポジトリURL>
cd perfect-text-overlay

# 依存関係をインストール
pip install Pillow numpy

# オプション：追加のシステムフォントをインストール
# macOS: フォントは自動的に検出されます
# Linux: sudo apt-get install fonts-noto-cjk
# Windows: フォントは自動的に検出されます
```

## 使用方法

### 基本的な例

```python
from scripts.prompt_separator import separate_prompt
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions
from scripts.text_renderer import render_text_on_image

# ステップ 1：プロンプトを分離
user_input = "ポスターを作成して、タイトルは'こんにちは世界'"
result = separate_prompt(user_input)

# result['image_prompt']: "ポスターを作成..."
# result['text_requirements']: {"text_groups": [{"content": "こんにちは世界"}]}

# ステップ 2：ベース画像を生成（お好みの画像生成器を使用）
# ... result['image_prompt'] を使用して画像を生成 ...

# ステップ 3：画像を分析
text_requirements = result['text_requirements']
analysis = analyze_image("generated_image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)

# ステップ 4：ユーザー選択（通常はUI経由で収集）
user_choices = {
    "font_style": "modern",
    "text_size": "auto",
    "effects": ["shadow", "outline"],
    "text_color": (255, 215, 0),  # ゴールド
}

# ステップ 5：テキストをレンダリング
output_path = render_text_on_image(
    image_path="generated_image.png",
    output_path="final_image.png",
    placements=placements,
    user_choices=user_choices
)
```

### フォントスタイル

以下のフォントスタイルがサポートされています：

| スタイル | フォント | 言語 | ライセンス |
|------|------|----------|---------|
| `modern` | Noto Sans CJK SC Bold | 簡体字中国語 | SIL OFL 1.1 |
| `traditional` | Noto Serif CJK SC Bold | 簡体字中国語 | SIL OFL 1.1 |
| `traditional_tw` | Noto Sans CJK TC Bold | 繁体字中国語（台湾） | SIL OFL 1.1 |
| `korean` | Noto Sans CJK KR Bold | 韓国語 | SIL OFL 1.1 |
| `english` | Roboto Bold | 英語/ラテン | Apache 2.0 |
| `cartoon` | Noto Sans CJK SC Bold | ユニバーサル | SIL OFL 1.1 |
| `calligraphy` | システムフォント | システム依存 | 異なる |

## プロジェクト構造

```
perfect-text-overlay/
├── assets/
│   └── fonts/              # 無料商用フォント
│       ├── NotoSansCJKsc-Bold.otf    # 源ノ角ゴシック簡体
│       ├── NotoSerifCJKsc-Bold.otf   # 源ノ明朝簡体
│       ├── NotoSansCJKtc-Bold.otf    # 源ノ角ゴシック繁体
│       ├── NotoSansCJKkr-Bold.otf    # 源ノ角ゴシック韓国語
│       ├── Roboto-Bold.ttf           # Roboto 英語
│       ├── OpenSans-Bold.ttf         # Open Sans 英語
│       └── LICENSE.md
├── references/
│   ├── trigger_keywords.md    # 多言語トリガーキーワード
│   ├── layout_patterns.md     # タイポグラフィのベストプラクティス
│   └── flowchart_symbols.md   # フローチャートデザイン標準
├── scripts/
│   ├── prompt_separator.py    # プロンプトからテキストを抽出
│   ├── image_analyzer.py      # 画像レイアウトを分析
│   └── text_renderer.py       # 画像にテキストをレンダリング
├── SKILL.md                   # 詳細なスキルドキュメント
└── README.md                  # メインドキュメント（英語）
```

## サポートされるユースケース

### 1. タイトル付きポスター
```
ユーザー："SF映画のポスターを作成して、タイトルは'インターステラー'"
↓
ステップ 1：画像プロンプト = "sci-fi movie poster, space theme..."
        テキスト = "インターステラー"
↓
ステップ 2：ベース画像を生成
↓
ステップ 3：下部中央配置を提案
↓
ステップ 4：モダンフォント、下部中央、シャドウ+アウトライン
↓
ステップ 5：下部に大きなタイトルをレンダリング
```

### 2. フローチャート
```
ユーザー："ユーザー登録フローチャートを作成：1.情報入力 2.メール確認 3.完了"
↓
ステップ 1：フローチャートノードを検出
↓
ステップ 2：ベース画像を生成
↓
ステップ 3：3つのノード位置を検出
↓
ステップ 4：水平フロー、ボックス+矢印を追加
↓
ステップ 5：接続矢印付きの3つのボックスノードをレンダリング
```

### 3. インフォグラフィック
```
ユーザー："インフォグラフィックを作成して、'売上：$100K'と'成長：+50%'を表示"
↓
ステップ 1：データポイントを抽出
↓
ステップ 2：ベース画像を生成
↓
ステップ 3：各統計データの安全ゾーンを検索
↓
ステップ 4：大きな数字、コントラストカラー
↓
ステップ 5：プロフェッショナルなデータビジュアライゼーションをレンダリング
```

## API リファレンス

### プロンプト分離器

```python
from scripts.prompt_separator import separate_prompt

result = separate_prompt("タイトル'Hello World'のポスターを作成")
# 返り値: {
#     "has_text": True,
#     "image_prompt": "Create poster...",
#     "text_requirements": {...}
# }
```

### 画像分析器

```python
from scripts.image_analyzer import analyze_image, get_text_placement_suggestions

analysis = analyze_image("image.png", text_requirements)
placements = get_text_placement_suggestions(analysis, text_requirements)
```

### テキストレンダラー

```python
from scripts.text_renderer import render_text_on_image

render_text_on_image(
    image_path="input.png",
    output_path="output.png",
    placements=[...],
    user_choices={...}
)
```

## トリガーキーワード

ユーザー入力に以下が含まれる場合、このスキルがトリガーされます：

- **画像タイプキーワード**：ポスター、フローチャート、インフォグラフィック、バナーなど
- **テキスト要件キーワード**：書く、タイトル、テキスト、キャプションなど

完全な多言語キーワードリストについては [references/trigger_keywords.md](references/trigger_keywords.md) を参照してください。

## フォントライセンス

含まれるすべてのフォントは無料で商用利用可能です：

- **Noto Sans/Serif CJK**: SIL Open Font License 1.1
- **Roboto**: Apache License 2.0
- **Open Sans**: SIL Open Font License 1.1

完全なライセンス詳細については [assets/fonts/LICENSE.md](assets/fonts/LICENSE.md) を参照してください。

## 貢献

貢献を歓迎します！気軽にプルリクエストを送信してください。

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 謝辞

- [Noto Fonts](https://github.com/notofonts/noto-cjk) by Google & Adobe
- [Roboto](https://github.com/googlefonts/roboto) by Google
- [Open Sans](https://github.com/googlefonts/opensans) by Google

---

**他の言語で読む：**
[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md)

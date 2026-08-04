#!/usr/bin/env python3
"""
Internationalization (i18n) Manager
Loads per-language JSON translation files and provides font auto-matching,
RTL detection, and overflow estimation for multi-language rendering.
"""

import json
import os
from typing import Dict, List


# Average char-width coefficient (relative to font size) per script bucket.
# Used by ``detect_overflow`` to estimate whether a translation will fit
# a fixed-width template at a given font size. Values are rough visual
# averages and intentionally lenient so we surface only real overflow risk.
SCRIPT_COEFFICIENTS = {
    "cjk": 1.0,      # 中文 / 日文 / 韩文 (square glyphs)
    "latin": 0.55,   # 拉丁字母 (proportional width ~ 0.5-0.6 of em)
    "arabic": 0.6,   # 阿拉伯 / 希伯来 等 RTL 文字
    "default": 0.55, # 数字 / 标点 / 其他
}


# Languages that use right-to-left scripts.
RTL_LANGUAGES = {"ar", "he", "fa", "ur"}


def _classify_char(ch: str) -> str:
    """Return the script bucket for a single character."""
    cp = ord(ch)
    # CJK 统一汉字 + 扩展 A + 平假名 + 片假名 + 韩文音节 + CJK 标点
    if (
        0x4E00 <= cp <= 0x9FFF
        or 0x3400 <= cp <= 0x4DBF
        or 0x3040 <= cp <= 0x30FF
        or 0xAC00 <= cp <= 0xD7AF
        or 0x3000 <= cp <= 0x303F
    ):
        return "cjk"
    # 阿拉伯文 + 阿拉伯文补充 + 表意形式
    if (
        0x0600 <= cp <= 0x06FF
        or 0x0750 <= cp <= 0x077F
        or 0x08A0 <= cp <= 0x08FF
        or 0xFB50 <= cp <= 0xFEFF
    ):
        return "arabic"
    # 希伯来文
    if 0x0590 <= cp <= 0x05FF:
        return "arabic"
    # 拉丁字母 (基础 + 扩展)
    if (
        0x0041 <= cp <= 0x005A
        or 0x0061 <= cp <= 0x007A
        or 0x00C0 <= cp <= 0x024F
    ):
        return "latin"
    return "default"


def _estimate_text_width(text: str, font_size: int) -> float:
    """Estimate rendered text width in pixels using per-char coefficients."""
    if not text:
        return 0.0
    total = 0.0
    for ch in text:
        bucket = _classify_char(ch)
        total += SCRIPT_COEFFICIENTS[bucket] * font_size
    return total


class I18nManager:
    """Manages multi-language translations and font auto-matching.

    Translation files are expected as flat key -> text JSON files at
    ``<translations_dir>/<lang>.json`` (e.g. ``en.json``, ``de.json``).
    """

    def __init__(self, translations_dir: str):
        self.translations_dir = translations_dir
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load every ``<lang>.json`` file in the translations directory."""
        if not os.path.isdir(self.translations_dir):
            return
        for filename in sorted(os.listdir(self.translations_dir)):
            if not filename.endswith(".json"):
                continue
            lang = os.path.splitext(filename)[0]
            path = os.path.join(self.translations_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self._translations[lang] = {
                        str(k): str(v) for k, v in data.items()
                    }
            except (OSError, json.JSONDecodeError) as e:
                print(f"[WARN] Failed to load translation file {path}: {e}")

    def get_translation(self, key: str, lang: str) -> str:
        """Return translation for ``key`` in ``lang``.

        Falls back to the English (``en``) translation when the key is
        missing in the requested language or the language itself is not
        loaded. Returns the key itself if neither the target language
        nor English has the key.
        """
        bucket = self._translations.get(lang, {})
        if key in bucket:
            return bucket[key]
        if lang != "en":
            en_bucket = self._translations.get("en", {})
            if key in en_bucket:
                return en_bucket[key]
        return key

    def get_all_languages(self) -> List[str]:
        """Return the list of loaded language codes (e.g. ``["en", "de"]``)."""
        return list(self._translations.keys())

    def detect_overflow(
        self,
        key: str,
        template_max_width: int,
        font_size: int = 48,
    ) -> Dict[str, bool]:
        """Estimate whether each language's translation overflows the template.

        Uses per-character width coefficients (CJK 1.0, Latin 0.55,
        Arabic/RTL 0.6) to estimate rendered width. A language is
        flagged as overflowing when its estimated width exceeds
        ``template_max_width``.

        Returns a ``{lang_code: overflows_bool}`` mapping for every
        loaded language.
        """
        result: Dict[str, bool] = {}
        for lang in self._translations.keys():
            text = self.get_translation(key, lang)
            width = _estimate_text_width(text, font_size)
            result[lang] = width > template_max_width
        return result

    @staticmethod
    def get_font_for_language(lang: str, style: str = "modern") -> str:
        """Return the absolute path of a font suitable for ``lang``.

        The mapping is based on the font files actually present under
        ``assets/fonts/``; missing specialized files (e.g. Arabic,
        Hebrew) gracefully fall back to the CJK font. To use a native
        Arabic typeface, drop ``NotoSansArabic-Bold.ttf`` (or similar)
        into ``assets/fonts/`` and extend the RTL branch below.
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_dir = os.path.join(project_root, "assets", "fonts")

        style_key = (style or "modern").lower()
        lang_key = (lang or "").lower()

        # 拉丁语系 (Latin-script languages)
        latin_langs = {
            "en", "de", "fr", "es", "it", "pt", "nl", "pl", "sv",
            "da", "fi", "no", "cs", "ro", "tr", "hu", "sk", "sl",
        }
        if lang_key in latin_langs:
            if style_key in ("elegant", "traditional"):
                filename = "OpenSans-Bold.ttf"
            else:
                filename = "Roboto-Bold.ttf"
        # 日文 — CJK 字体本身包含日文字形
        elif lang_key == "ja":
            filename = "NotoSansCJKsc-Bold.otf"
        # 韩文
        elif lang_key == "ko":
            filename = "NotoSansCJKkr-Bold.otf"
        # 中文: 繁体优先
        elif lang_key in {"zh-tw", "zh-hant", "zh_tw", "zh-hk", "zh-mo"}:
            filename = "NotoSansCJKtc-Bold.otf"
        elif lang_key.startswith("zh") or lang_key in {"zh-cn", "zh-hans", "zh-sg"}:
            filename = "NotoSansCJKsc-Bold.otf"
        # RTL 语言 — 阿拉伯语族/希伯来语使用专用 Noto 字体（OFL 许可）；
        # 字体文件缺失时回退到 CJK 字体。
        elif lang_key in RTL_LANGUAGES:
            if lang_key in {"ar", "fa", "ur"}:
                arabic_path = os.path.join(fonts_dir, "NotoSansArabic-Bold.ttf")
                if os.path.exists(arabic_path):
                    return arabic_path
            if lang_key == "he":
                hebrew_path = os.path.join(fonts_dir, "NotoSansHebrew-Bold.ttf")
                if os.path.exists(hebrew_path):
                    return hebrew_path
            filename = "NotoSansCJKsc-Bold.otf"
        else:
            # 未识别语言: 默认 Roboto
            filename = "Roboto-Bold.ttf"

        return os.path.join(fonts_dir, filename)

    @staticmethod
    def is_rtl(lang: str) -> bool:
        """Return True if ``lang`` is a right-to-left script language."""
        return (lang or "").lower() in RTL_LANGUAGES


if __name__ == "__main__":
    print("i18n_manager module loaded")
    print("Available class: I18nManager")
    print("Static helpers: get_font_for_language, is_rtl")

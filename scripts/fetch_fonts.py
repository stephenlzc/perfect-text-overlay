#!/usr/bin/env python3
"""Fetch and materialise font weights into ``assets/fonts/``.

GenImageText ships a single Bold weight per family.  To support typographic
weight hierarchy (light/regular/medium/bold/black) this script downloads the
upstream variable fonts and *static* CJK OTFs, instantiates the variable fonts
at the requested weights via ``fontTools.varLib.instancer``, and writes static
``.ttf``/``.otf`` files into ``assets/fonts/``.

It is idempotent: existing files are skipped unless ``--force`` is passed.

Usage::

    .venv/bin/python scripts/fetch_fonts.py            # download everything
    .venv/bin/python scripts/fetch_fonts.py --no-cjk   # latin only (fast)
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(ROOT, "assets", "fonts")

_HEADERS = {"User-Agent": "GenImageText-font-fetcher/1.0"}

# Variable fonts: instanced to static weights via fontTools.
VARIABLE_FONTS = [
    {
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto%5Bwdth,wght%5D.ttf",
        "family": "Roboto",
        "ext": ".ttf",
        "weights": {"Light": 300, "Regular": 400, "Medium": 500, "Black": 900},
    },
    {
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/opensans/OpenSans%5Bwdth,wght%5D.ttf",
        "family": "OpenSans",
        "ext": ".ttf",
        "weights": {"Light": 300, "Regular": 400, "Medium": 500, "ExtraBold": 800},
    },
]

# Static CJK OTFs: (url, destination filename).  Each file is ~17 MB.
_CJK_TEMPLATE = (
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/"
    "{dir}/{family}-{weight}.otf"
)
_CJK_SERIF_TEMPLATE = (
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/OTF/"
    "{dir}/{family}-{weight}.otf"
)


def _cjk_targets() -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    for directory, family in (
        ("SimplifiedChinese", "NotoSansCJKsc"),
        ("TraditionalChinese", "NotoSansCJKtc"),
        ("Korean", "NotoSansCJKkr"),
    ):
        for weight in ("Regular", "Black"):
            url = _CJK_TEMPLATE.format(dir=directory, family=family, weight=weight)
            targets.append((url, f"{family}-{weight}.otf"))
    # Serif body weight for Simplified Chinese (optional, ~25 MB).
    targets.append(
        (
            _CJK_SERIF_TEMPLATE.format(
                dir="SimplifiedChinese", family="NotoSerifCJKsc", weight="Regular"
            ),
            "NotoSerifCJKsc-Regular.otf",
        )
    )
    return targets


def _download(url: str, dest: str) -> None:
    if os.path.exists(dest):
        print(f"  skip (exists): {os.path.basename(dest)}")
        return
    print(f"  fetch: {url}")
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
            out.write(resp.read())
    except urllib.error.HTTPError as exc:
        print(f"  [WARN] {exc} -> {url}")
        if os.path.exists(dest):
            os.remove(dest)
    except Exception as exc:  # noqa: BLE001 - surface network/IO problems
        print(f"  [WARN] {type(exc).__name__}: {exc}")
        if os.path.exists(dest):
            os.remove(dest)


def _instantiate_variable(url: str, family: str, ext: str, weights: dict[str, int]) -> None:
    try:
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
    except ImportError as exc:
        print(f"  [WARN] fontTools unavailable ({exc}); skipping {family}")
        return

    vf_path = os.path.join(FONTS_DIR, f".tmp_{family}_VF{ext}")
    _download(url, vf_path)
    if not os.path.exists(vf_path):
        return
    for weight_name, axis_value in weights.items():
        dest = os.path.join(FONTS_DIR, f"{family}-{weight_name}{ext}")
        if os.path.exists(dest):
            print(f"  skip (exists): {os.path.basename(dest)}")
            continue
        print(f"  instance {family} wght={axis_value} -> {os.path.basename(dest)}")
        try:
            font = TTFont(vf_path)
            instantiateVariableFont(font, {"wght": axis_value})
            font.save(dest)
        except Exception as exc:  # noqa: BLE001
            print(f"  [WARN] instancing failed for {weight_name}: {exc}")
    os.remove(vf_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch font weights into assets/fonts/")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    parser.add_argument("--no-cjk", action="store_true", help="skip large CJK downloads")
    args = parser.parse_args()

    os.makedirs(FONTS_DIR, exist_ok=True)
    if args.force:
        # clear skip behaviour by deleting targets before download
        print("--force: will overwrite existing target files")

    print("== Latin variable fonts ==")
    for vf in VARIABLE_FONTS:
        _instantiate_variable(vf["url"], vf["family"], vf["ext"], vf["weights"])

    if not args.no_cjk:
        print("== CJK static fonts ==")
        for url, filename in _cjk_targets():
            dest = os.path.join(FONTS_DIR, filename)
            if args.force and os.path.exists(dest):
                os.remove(dest)
            _download(url, dest)

    print("\n== assets/fonts/ ==")
    for name in sorted(os.listdir(FONTS_DIR)):
        if name.startswith("."):
            continue
        path = os.path.join(FONTS_DIR, name)
        if os.path.isfile(path):
            print(f"  {name:32s} {os.path.getsize(path) / 1e6:8.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

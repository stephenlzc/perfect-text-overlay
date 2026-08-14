#!/usr/bin/env python3
"""Batch rendering pipeline for the GenImageText project.

Renders a single base image across every language defined in a template's
translation directory, producing one final image per language. The pipeline
coordinates the existing ``config_loader`` / ``i18n_manager`` /
``template_engine`` / ``text_renderer`` / ``image_analyzer`` modules and
runs the per-language work in parallel through a small thread pool.

The ``gen_ecommerce.py`` CLI consumes :class:`BatchPipeline` directly; this
module is intentionally framework-free so the public contract stays stable.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

# ``scripts/`` is intentionally not a package; support both styles of import:
#   1) ``scripts/`` already on ``sys.path`` (the usual project layout), and
#   2) a fresh interpreter that only knows about this file's directory.
try:  # pragma: no cover - import path is exercised at runtime
    from config_loader import TemplateConfig, load_config
    from font_registry import resolve_font_path
    from i18n_manager import I18nManager
    from image_analyzer import detect_existing_text
    from layout_composer import compose_layout
    from template_engine import SVGTemplateEngine
    from text_renderer import render_layers_pil, render_svg_template
    from theme_engine import resolve_theme
except ImportError:
    _SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
    if _SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, _SCRIPTS_DIR)
    from config_loader import TemplateConfig, load_config  # noqa: E402
    from font_registry import resolve_font_path  # noqa: E402
    from i18n_manager import I18nManager  # noqa: E402
    from image_analyzer import detect_existing_text  # noqa: E402
    from layout_composer import compose_layout  # noqa: E402
    from template_engine import SVGTemplateEngine  # noqa: E402
    from text_renderer import render_layers_pil, render_svg_template  # noqa: E402
    from theme_engine import resolve_theme  # noqa: E402


logger = logging.getLogger("batch_pipeline")


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def _project_root() -> str:
    """Return the absolute path to the project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _assets_fonts_dir() -> str:
    return os.path.join(_project_root(), "assets", "fonts")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class BatchPipeline:
    """Render one base image into N language-localised images.

    Workflow:
      1. Load the template config from ``config_path``.
      2. Resolve the translations directory (parent of the file referenced
         by ``config.translations_file``, relative to the config's directory).
      3. Detect whether the base image already contains text (warn, do not
         abort).
      4. For every loaded language:
         - Build per-layer translation variables.
         - Estimate overflow per layer.
         - (``pil`` renderer, default) run :func:`compose_layout` for the
           aesthetic placement plan (recorded into the report), then draw
           text directly with :func:`render_layers_pil`; or
           (``svg`` renderer) build the SVG via :class:`SVGTemplateEngine`
           and rasterise it via :func:`render_svg_template`.

    All languages run concurrently through a small thread pool; a single
    language failure is captured into the report and does not abort the
    batch.
    """

    MAX_WORKERS = 4

    def __init__(self, config_path: str, renderer: str = "pil", theme_name: Optional[str] = None):
        self.config_path = config_path
        self.config: TemplateConfig = load_config(config_path)
        # Resolve every '$token' reference (template tokens, plus the built-in
        # theme when given).  Idempotent for already-resolved configs.
        self.config = resolve_theme(self.config, theme_name)

        # 渲染后端：``pil``（默认，PIL 直绘，CJK/阿拉伯语字形与 RTL 整形正确）
        # 或 ``svg``（旧路径：SVG + cairosvg 栅格化，仅作回退保留）。
        renderer = str(renderer or "pil").lower()
        if renderer not in ("pil", "svg"):
            raise ValueError(
                f"renderer must be one of 'pil'/'svg', got {renderer!r}"
            )
        self.renderer = renderer

        # ``translations_file`` is a relative path such as
        # ``"translations/en.json"``. The parent directory of that path is
        # the directory ``I18nManager`` should scan for ``<lang>.json`` files.
        config_dir = os.path.dirname(os.path.abspath(config_path))
        translations_path = os.path.normpath(
            os.path.join(config_dir, self.config.translations_file)
        )
        self.translations_dir = os.path.dirname(translations_path)
        self.i18n = I18nManager(self.translations_dir)

        # The SVG engine is stateless beyond the optional Jinja2 template
        # file; we only use ``build_svg_from_config``.
        self._engine = SVGTemplateEngine()

        # Mutable per-run report; ``generate_report()`` returns a copy of
        # this dict. Reset on every ``run()`` so repeated calls do not
        # accumulate state.
        self._report: Dict[str, Any] = self._empty_report()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, base_image_path: str, output_dir: str) -> dict:
        """Render every language for ``base_image_path`` into ``output_dir``.

        Returns the same dict that :meth:`generate_report` would return.
        A single language failure never aborts the batch.
        """
        self._report = self._empty_report()

        # 1. Base image check (warn on existing text but do not abort).
        self._report["base_image_check"] = self._check_base_image(base_image_path)

        # 2. Language list.
        languages = self.i18n.get_all_languages()
        if not languages:
            logger.warning(
                "no translation files found in %s", self.translations_dir
            )
            return self.generate_report()

        # 3. Overflow detection — surfaced into the report and the log.
        self._report["overflow_warnings"] = self._collect_overflow_warnings()
        for w in self._report["overflow_warnings"]:
            logger.info("overflow: %s", w)

        # 4. Concurrent rendering.
        os.makedirs(output_dir, exist_ok=True)
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as pool:
            futures = {
                pool.submit(
                    self._render_lang_task, base_image_path, lang, output_dir
                ): lang
                for lang in languages
            }
            for future in as_completed(futures):
                lang = futures[future]
                try:
                    result = future.result()
                except Exception as exc:  # pragma: no cover - defensive
                    logger.exception("rendering %s raised in worker", lang)
                    self._record_failure(
                        lang, f"{type(exc).__name__}: {exc}", 0.0
                    )
                    continue
                self._record_result(lang, result)

        return self.generate_report()

    def render_single(
        self, base_image_path: str, lang: str, output_path: str
    ) -> str:
        """Render a single language to ``output_path`` (used by the CLI).

        Reuses the same per-language logic as :meth:`run`. Returns
        ``output_path`` for caller convenience.
        """
        start = time.perf_counter()
        parent = os.path.dirname(os.path.abspath(output_path)) or "."
        os.makedirs(parent, exist_ok=True)
        self._render_lang(base_image_path, lang, output_path)
        elapsed = time.perf_counter() - start
        logger.info(
            "rendered single %s -> %s (%.2fs)", lang, output_path, elapsed
        )
        return output_path

    # ------------------------------------------------------------------
    # Per-language rendering
    # ------------------------------------------------------------------

    def _render_lang_task(
        self, base_image_path: str, lang: str, output_dir: str
    ) -> Dict[str, Any]:
        """Worker entry point: render one language, return its result dict.

        Exceptions are captured here (rather than propagating) so that a
        single bad language never tears down the whole pool.
        """
        start = time.perf_counter()
        filename = self._generate_filename(lang, self.config.name)
        output_path = os.path.join(output_dir, filename)
        try:
            self._render_lang(base_image_path, lang, output_path)
        except Exception as exc:
            elapsed = time.perf_counter() - start
            logger.exception("rendering %s failed", lang)
            return {
                "lang": lang,
                "output_path": None,
                "elapsed": elapsed,
                "error": f"{type(exc).__name__}: {exc}",
            }
        elapsed = time.perf_counter() - start
        logger.info("rendered %s -> %s (%.2fs)", lang, output_path, elapsed)
        return {
            "lang": lang,
            "output_path": output_path,
            "elapsed": elapsed,
            "error": None,
        }

    def _render_lang(
        self, base_image_path: str, lang: str, output_path: str
    ) -> None:
        """Render one language; raise on any failure."""
        variables = {
            layer.name: self.i18n.get_translation(layer.name, lang)
            for layer in self.config.text_layers
        }
        if self.renderer == "svg":
            svg = self._engine.build_svg_from_config(
                self.config,
                variables,
                lang=lang,
                font_resolver=self._make_font_resolver(),
            )
            render_svg_template(
                base_image_path,
                svg,
                output_path,
                output_format=self.config.output_format,
                quality=self.config.output_quality,
            )
            return

        # PIL 路径：先跑美学排版引擎（结果同时进报告），再按方案渲染。
        plan = None
        try:
            plan = compose_layout(base_image_path, self.config, lang=lang)
        except Exception as exc:
            logger.warning("layout analysis failed for %s: %s", lang, exc)
        if plan:
            entries = [
                {"layer": entry["name"], "adjustments": list(entry["adjustments"])}
                for entry in plan.get("layers", [])
                if entry.get("adjustments")
            ]
            if entries:
                self._report["layout_adjustments"][lang] = entries
        render_layers_pil(
            base_image_path,
            self.config,
            variables,
            lang,
            font_resolver=self._make_font_resolver(),
            output_path=output_path,
            smart_layout=False,
            layout_plan=plan,
            output_format=self.config.output_format,
            quality=self.config.output_quality,
        )

    def _make_font_resolver(self):
        """Return a ``font_resolver(lang, layer)`` closure.

        Delegates to :func:`font_registry.resolve_font_path`, which keeps the
        language/script precedence of :meth:`I18nManager.get_font_for_language`
        and additionally honours the layer's ``font_weight``.
        """
        fonts_dir = _assets_fonts_dir()

        def _font_resolver(lang: str, layer) -> str:
            return resolve_font_path(lang, layer, fonts_dir=fonts_dir)

        return _font_resolver

    def _collect_overflow_warnings(self) -> List[str]:
        """Run :meth:`I18nManager.detect_overflow` for every layer."""
        warnings: List[str] = []
        for layer in self.config.text_layers:
            try:
                overflow_map = self.i18n.detect_overflow(
                    layer.name, layer.max_width, layer.font_size
                )
            except Exception as exc:
                warnings.append(
                    f"overflow check failed for layer {layer.name!r}: {exc}"
                )
                continue
            for lang, overflows in overflow_map.items():
                if overflows:
                    text = self.i18n.get_translation(layer.name, lang)
                    warnings.append(
                        f"layer {layer.name!r} overflows in {lang!r}: "
                        f"{text!r} estimated > {layer.max_width}px at "
                        f"{layer.font_size}pt"
                    )
        return warnings

    def _check_base_image(self, base_image_path: str) -> Dict[str, Any]:
        """Run :func:`detect_existing_text`; warn on detection."""
        try:
            result = detect_existing_text(base_image_path)
        except Exception as exc:  # pragma: no cover - defensive
            result = {
                "has_text": None,
                "detected_text": [],
                "warning": (
                    f"detect_existing_text raised {type(exc).__name__}: {exc}"
                ),
            }
        if result.get("has_text") is True:
            preview = ", ".join(result.get("detected_text", [])[:3])
            logger.warning(
                "base image %s already contains text (preview: %s); continuing",
                base_image_path,
                preview or "<empty>",
            )
        return result

    def _record_result(self, lang: str, result: Dict[str, Any]) -> None:
        self._report["timing"][lang] = round(float(result["elapsed"]), 3)
        if result["error"] is not None:
            self._record_failure(lang, result["error"], float(result["elapsed"]))
        else:
            self._report["success"] += 1
            self._report["outputs"].append(result["output_path"])

    def _record_failure(self, lang: str, error: str, elapsed: float) -> None:
        self._report["failed"] += 1
        self._report["failures"].append({"lang": lang, "error": error})
        self._report["timing"][lang] = round(float(elapsed), 3)

    # ------------------------------------------------------------------
    # Output naming
    # ------------------------------------------------------------------

    def _generate_filename(self, lang: str, template_name: str) -> str:
        """Build the output filename for a language.

        Format: ``"{template_name}_{lang}.{output_format}"``.
        ``output_format`` is read from the loaded config so the extension
        always matches what was declared in the template.
        """
        return f"{template_name}_{lang}.{self.config.output_format}"

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def generate_report(self) -> dict:
        """Return a shallow copy of the current run report.

        The report is a plain dict so callers can serialise it to JSON
        without further processing. The copy keeps callers from mutating
        the pipeline's internal state.
        """
        return {
            "success": self._report["success"],
            "failed": self._report["failed"],
            "failures": list(self._report["failures"]),
            "timing": dict(self._report["timing"]),
            "overflow_warnings": list(self._report["overflow_warnings"]),
            "base_image_check": dict(self._report["base_image_check"]),
            "layout_adjustments": {
                lang: [dict(entry) for entry in entries]
                for lang, entries in self._report["layout_adjustments"].items()
            },
            "outputs": list(self._report["outputs"]),
        }

    @staticmethod
    def _empty_report() -> Dict[str, Any]:
        return {
            "success": 0,
            "failed": 0,
            "failures": [],
            "timing": {},
            "overflow_warnings": [],
            "base_image_check": {},
            "layout_adjustments": {},
            "outputs": [],
        }


__all__ = ["BatchPipeline"]


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Batch render a base image per language"
    )
    parser.add_argument("config", help="Path to template.yaml")
    parser.add_argument("base_image", help="Path to the base image")
    parser.add_argument("output_dir", help="Directory for rendered outputs")
    args = parser.parse_args()

    pipeline = BatchPipeline(args.config)
    report = pipeline.run(args.base_image, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))

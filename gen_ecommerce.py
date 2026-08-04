#!/usr/bin/env python3
"""gen_ecommerce.py — CLI entry point for the GenImageText pipeline.

Subcommands
-----------

* ``init``     — copy a preset directory into a project directory.
* ``prompt``   — print the base image prompt (with ``no text`` / ``no watermark``
                 ensured) and a summary of the configured safe zones.
* ``validate`` — run schema/layout checks, verify translations can be loaded,
                 and confirm every ``text_layer.name`` has an entry in
                 ``translations/en.json``.
* ``render``   — render a single language variant via ``BatchPipeline.render_single``.
* ``batch``    — render every loaded language into an output directory via
                 ``BatchPipeline.run`` and print the resulting report.
* ``check``    — OCR-detect residual text on a base image (gracefully reports
                 when OCR is unavailable).

The CLI lives at the project root, so ``scripts/`` (a flat module directory,
not a Python package) is added to ``sys.path`` explicitly before importing
the project's modules.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from typing import List, Optional

# scripts/ is a flat module directory (no __init__.py). Make it importable.
_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import click  # noqa: E402

from config_loader import (  # noqa: E402
    ConfigError,
    load_config,
    validate_config_file,
)
from i18n_manager import I18nManager  # noqa: E402
from image_analyzer import detect_existing_text  # noqa: E402


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(PROJECT_ROOT, "presets")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _list_presets() -> List[str]:
    """Return sorted names of preset directories under ``presets/``."""
    if not os.path.isdir(PRESETS_DIR):
        return []
    return sorted(
        entry
        for entry in os.listdir(PRESETS_DIR)
        if not entry.startswith(".")
        and os.path.isdir(os.path.join(PRESETS_DIR, entry))
    )


def _is_empty_dir(path: str) -> bool:
    """Return True if the directory is empty (ignoring hidden files)."""
    if not os.path.isdir(path):
        return False
    return all(name.startswith(".") for name in os.listdir(path))


def _ensure_safe_no_text_suffix(prompt_text: str) -> tuple[str, List[str]]:
    """Append ``no text`` / ``no watermark`` / ``no logos`` if missing.

    Returns the augmented prompt plus the list of phrases that were added,
    so callers can show the user what was appended.
    """
    lowered = prompt_text.lower()
    added: List[str] = []
    base = (prompt_text or "").rstrip(" ,.;:\n\t")
    if "no text" not in lowered:
        added.append("no text")
    if "no watermark" not in lowered:
        added.append("no watermark")
    if "no logo" not in lowered:
        added.append("no logos")
    if not added:
        return base, []
    suffix = ", ".join(added)
    return f"{base}, {suffix}", added


def _format_bbox(bbox: List[float], canvas_w: int, canvas_h: int) -> str:
    """Return a compact bbox string for human display."""
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return str(bbox)
    try:
        values = [float(v) for v in bbox]
    except (TypeError, ValueError):
        return str(bbox)
    if max(values) <= 1.0 and canvas_w and canvas_h:
        coords = (
            int(round(values[0] * canvas_w)),
            int(round(values[1] * canvas_h)),
            int(round(values[2] * canvas_w)),
            int(round(values[3] * canvas_h)),
        )
        return f"{coords[0]},{coords[1]},{coords[2]},{coords[3]} (normalized {values})"
    return ", ".join(str(int(v)) for v in values)


def _resolve_batch_pipeline():
    """Import ``BatchPipeline`` lazily so the other subcommands keep working
    while another agent is finalising ``scripts/batch_pipeline.py``."""
    try:
        from batch_pipeline import BatchPipeline
    except ImportError as exc:
        raise click.UsageError(
            f"scripts/batch_pipeline.py could not be imported ({exc}). "
            "Make sure scripts/batch_pipeline.py exists and is on the import path."
        ) from exc
    return BatchPipeline


# ---------------------------------------------------------------------------
# Click command group
# ---------------------------------------------------------------------------


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.1.0", prog_name="gen_ecommerce")
def cli() -> None:
    """Generate multi-language e-commerce listing images with text overlay."""


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--preset",
    default=None,
    help="Preset name under presets/. Omit to choose interactively.",
)
@click.option(
    "--project-dir",
    required=True,
    type=click.Path(),
    help="Target directory to create or overwrite.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Allow overwriting a non-empty target directory.",
)
def init(preset: Optional[str], project_dir: str, force: bool) -> None:
    """Copy a preset directory into a project directory."""
    available = _list_presets()
    if not available:
        click.echo(
            click.style("ERROR", fg="red")
            + f": no presets found under {PRESETS_DIR}/.",
            err=True,
        )
        sys.exit(2)

    if preset is None:
        click.echo("Available presets:")
        for idx, name in enumerate(available, 1):
            click.echo(f"  {idx}. {name}")
        choice = click.prompt("Select a preset (number or name)", type=str)
        choice = (choice or "").strip()
        if choice.isdigit():
            pick = int(choice) - 1
            if not 0 <= pick < len(available):
                click.echo(
                    click.style("ERROR", fg="red")
                    + f": choice {choice!r} is out of range.",
                    err=True,
                )
                sys.exit(2)
            preset = available[pick]
        else:
            if choice not in available:
                click.echo(
                    click.style("ERROR", fg="red")
                    + f": preset {choice!r} not found. Available: {available}.",
                    err=True,
                )
                sys.exit(2)
            preset = choice

    if preset not in available:
        click.echo(
            click.style("ERROR", fg="red")
            + f": preset {preset!r} not found. Available: {available}.",
            err=True,
        )
        sys.exit(2)

    src = os.path.join(PRESETS_DIR, preset)
    target = os.path.abspath(project_dir)

    if os.path.exists(target):
        if not os.path.isdir(target):
            click.echo(
                click.style("ERROR", fg="red")
                + f": target {target!r} exists and is not a directory.",
                err=True,
            )
            sys.exit(1)
        if not _is_empty_dir(target):
            if not force:
                click.echo(
                    click.style("ERROR", fg="red")
                    + f": target {target!r} is not empty. Re-run with --force to overwrite.",
                    err=True,
                )
                sys.exit(1)
            click.echo(f"Removing existing contents of {target} (--force).")
            shutil.rmtree(target)
    os.makedirs(target, exist_ok=True)

    for entry in sorted(os.listdir(src)):
        if entry.startswith("."):
            continue
        s = os.path.join(src, entry)
        d = os.path.join(target, entry)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    click.echo(
        click.style("OK", fg="green")
        + f": initialised {target} from preset {preset!r}."
    )
    click.echo("Next steps:")
    click.echo(f"  1. Edit {os.path.join(target, 'template.yaml')} if needed.")
    click.echo(f"  2. Place your base image at {os.path.join(target, 'base_image.png')}.")
    click.echo(f"  3. Run: python gen_ecommerce.py validate --config {os.path.join(target, 'template.yaml')}")


# ---------------------------------------------------------------------------
# prompt
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Template config YAML.",
)
def prompt(config_path: str) -> None:
    """Print the base image prompt and a safe_zones summary."""
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        click.echo(
            click.style("ERROR", fg="red") + f": {exc}", err=True
        )
        sys.exit(1)

    base = (cfg.base_image_prompt or "").strip()
    augmented, added = _ensure_safe_no_text_suffix(base)

    click.echo("--- base image prompt (copy into Midjourney / Stable Diffusion) ---")
    click.echo(augmented)
    if added:
        click.echo(
            f"(appended to enforce 'no text/watermark/logos': {', '.join(added)})"
        )
    click.echo("---")
    click.echo("")

    if cfg.safe_zones:
        click.echo(f"safe_zones ({len(cfg.safe_zones)}):")
        for idx, zone in enumerate(cfg.safe_zones, 1):
            if not isinstance(zone, dict):
                click.echo(f"  {idx}. {zone!r}")
                continue
            name = (
                zone.get("name")
                or zone.get("region")
                or zone.get("label")
                or f"zone_{idx}"
            )
            bbox = zone.get("bbox") or zone.get("bbox_norm")
            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                bb_str = _format_bbox(list(bbox), cfg.canvas_width, cfg.canvas_height)
            else:
                bb_str = "(no bbox)"
            suggested = zone.get("suggested_for")
            sug = f" -> {suggested}" if suggested else ""
            click.echo(f"  {idx}. {name}: {bb_str}{sug}")
    else:
        click.echo("(no safe_zones configured)")


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Template config YAML.",
)
@click.option(
    "--base-image",
    required=True,
    type=click.Path(exists=True),
    help="Base image to render text on top of.",
)
@click.option(
    "--lang",
    required=True,
    help="Language code (e.g. en, de, ja, ko, ar).",
)
@click.option(
    "--output",
    required=True,
    type=click.Path(),
    help="Output image path.",
)
def render(
    config_path: str, base_image: str, lang: str, output: str
) -> None:
    """Render a single language variant via BatchPipeline.render_single."""
    BatchPipeline = _resolve_batch_pipeline()
    pipe = BatchPipeline(config_path)

    out_abs = os.path.abspath(output)
    parent = os.path.dirname(out_abs)
    if parent:
        os.makedirs(parent, exist_ok=True)

    click.echo(f"Rendering {lang} -> {out_abs}")
    try:
        written = pipe.render_single(base_image, lang, out_abs)
    except Exception as exc:  # noqa: BLE001 - surface any render error verbatim
        click.echo(
            click.style("ERROR", fg="red") + f": render failed: {exc}",
            err=True,
        )
        sys.exit(1)
    click.echo(
        click.style("OK", fg="green") + f": rendered -> {written}"
    )


# ---------------------------------------------------------------------------
# batch
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Template config YAML.",
)
@click.option(
    "--base-image",
    required=True,
    type=click.Path(exists=True),
    help="Base image to render text on top of.",
)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(),
    help="Directory to write rendered variants into.",
)
def batch(config_path: str, base_image: str, output_dir: str) -> None:
    """Render every loaded language and print a report summary."""
    BatchPipeline = _resolve_batch_pipeline()
    pipe = BatchPipeline(config_path)

    out_abs = os.path.abspath(output_dir)
    os.makedirs(out_abs, exist_ok=True)
    click.echo(f"Running BatchPipeline on {base_image!r} -> {out_abs}")

    t0 = time.monotonic()
    try:
        report = pipe.run(base_image, out_abs)
    except Exception as exc:  # noqa: BLE001
        click.echo(
            click.style("ERROR", fg="red") + f": batch run failed: {exc}",
            err=True,
        )
        sys.exit(1)
    wall = time.monotonic() - t0

    if not isinstance(report, dict):
        click.echo(
            click.style("ERROR", fg="red")
            + f": BatchPipeline.run returned {type(report).__name__}, expected dict.",
            err=True,
        )
        sys.exit(1)

    success = report.get("success", 0)
    failed = report.get("failed", 0)
    failures = report.get("failures", []) or []
    overflow = report.get("overflow_warnings", []) or []
    outputs = report.get("outputs") or {}
    timing = report.get("timing", wall)

    click.echo("")
    click.echo("--- batch report ---")
    click.echo(f"success : {success}")
    click.echo(f"failed  : {failed}")
    if isinstance(timing, (int, float)):
        click.echo(f"timing  : {timing:.2f}s (wall {wall:.2f}s)")
    elif isinstance(timing, dict):
        wall_total = sum(float(v) for v in timing.values() if isinstance(v, (int, float)))
        click.echo(
            f"timing  : sum={wall_total:.2f}s  (wall {wall:.2f}s)  per-lang={timing}"
        )
    else:
        click.echo(f"timing  : {timing} (wall {wall:.2f}s)")

    if outputs:
        click.echo("outputs:")
        if isinstance(outputs, dict):
            for lang_code, path in outputs.items():
                click.echo(f"  - {lang_code}: {path}")
        else:
            # BatchPipeline may report outputs as a list of paths;
            # derive the language from the "{template_name}_{lang}.{ext}" filename.
            for path in outputs:
                stem = os.path.splitext(os.path.basename(path))[0]
                lang_code = stem.split("_")[-1] if "_" in stem else stem
                click.echo(f"  - {lang_code}: {path}")
    if overflow:
        click.echo(f"overflow warnings ({len(overflow)}):")
        for warn in overflow:
            click.echo(f"  - {warn}")
    if failures:
        click.echo(f"failures ({len(failures)}):")
        for fail in failures:
            if isinstance(fail, dict):
                lang_code = fail.get("lang", "?")
                err = fail.get("error", fail)
                click.echo(f"  - {lang_code}: {err}")
            else:
                click.echo(f"  - {fail}")
    click.echo("---")

    if failed:
        click.echo(
            click.style("WARN", fg="yellow")
            + f": {failed} language(s) failed; see report above."
        )


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Template config YAML.",
)
def validate(config_path: str) -> None:
    """Validate schema, fonts, layout, and translation key coverage."""

    # 1) schema + layout warnings (also forces load_config)
    try:
        warnings = validate_config_file(config_path)
    except ConfigError as exc:
        click.echo(
            click.style("ERROR", fg="red") + f": {exc}", err=True
        )
        sys.exit(1)

    has_warning = False
    click.echo("--- schema & layout warnings ---")
    if warnings:
        for w in warnings:
            click.echo(f"  - {w}")
        click.echo(f"({len(warnings)} warning(s))")
    else:
        click.echo("  (none)")

    # 2) load_config again (validate_config_file already did this successfully)
    cfg = load_config(config_path)
    click.echo(f"\nLoaded config: name={cfg.name!r}, scene_type={cfg.scene_type!r}")
    click.echo(f"  canvas: {cfg.canvas_width}x{cfg.canvas_height}")
    click.echo(f"  text_layers: {[layer.name for layer in cfg.text_layers]}")

    # 3) translations directory loadable by I18nManager
    config_dir = os.path.dirname(os.path.abspath(config_path))
    translations_dir = os.path.join(config_dir, "translations")
    click.echo("\n--- translations ---")
    if not os.path.isdir(translations_dir):
        click.echo(
            click.style("WARN", fg="yellow")
            + f": translations dir not found at {translations_dir}"
        )
        has_warning = True
        languages: List[str] = []
    else:
        try:
            i18n = I18nManager(translations_dir)
        except Exception as exc:  # noqa: BLE001
            click.echo(
                click.style("ERROR", fg="red")
                + f": I18nManager failed to load {translations_dir}: {exc}",
                err=True,
            )
            sys.exit(1)
        languages = i18n.get_all_languages()
        if not languages:
            click.echo(
                click.style("WARN", fg="yellow")
                + f": translations dir {translations_dir} contains no .json files."
            )
            has_warning = True
        else:
            click.echo(f"  loaded languages: {languages}")

    # 4) every text_layer.name present in en.json
    click.echo("\n--- text_layer key coverage (en.json) ---")
    layer_names = [layer.name for layer in cfg.text_layers]
    en_path = os.path.join(translations_dir, "en.json")
    if os.path.isfile(en_path):
        try:
            with open(en_path, "r", encoding="utf-8") as fp:
                en_data = json.load(fp)
        except (OSError, json.JSONDecodeError) as exc:
            click.echo(
                click.style("WARN", fg="yellow")
                + f": cannot read {en_path}: {exc}"
            )
            en_data = {}
            has_warning = True
        if isinstance(en_data, dict):
            missing = [name for name in layer_names if name not in en_data]
            if missing:
                for name in missing:
                    click.echo(
                        click.style("WARN", fg="yellow")
                        + f": text layer {name!r} has no entry in en.json (add it under translations/en.json)."
                    )
                has_warning = True
            else:
                click.echo("  (all text layer names are covered)")
        else:
            click.echo(
                click.style("WARN", fg="yellow")
                + f": {en_path} is not a JSON object; skipping key coverage check."
            )
            has_warning = True
    else:
        click.echo(
            click.style("WARN", fg="yellow")
            + f": {en_path} not found; skipping key coverage check."
        )
        has_warning = True

    click.echo("")
    if has_warning:
        click.echo(
            click.style("WARN", fg="yellow")
            + ": validation completed with warnings (non-fatal)."
        )
    else:
        click.echo(click.style("OK", fg="green") + ": validation passed.")


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--image",
    "image_path",
    required=True,
    type=click.Path(exists=True),
    help="Image path to OCR-check.",
)
def check(image_path: str) -> None:
    """OCR-detect any residual text on the base image."""
    try:
        result = detect_existing_text(image_path)
    except Exception as exc:  # noqa: BLE001 - final safety net
        click.echo(
            click.style("ERROR", fg="red")
            + f": detect_existing_text raised {type(exc).__name__}: {exc}",
            err=True,
        )
        sys.exit(1)

    warning = (result or {}).get("warning")
    has_text = (result or {}).get("has_text")
    fragments = (result or {}).get("detected_text", []) or []

    if warning:
        click.echo(
            click.style("WARN", fg="yellow")
            + f": OCR unavailable — {warning}"
        )
        click.echo(
            "  Install the Tesseract binary (e.g. `brew install tesseract`) to"
            " enable residual-text detection."
        )
        return

    if has_text:
        click.echo(
            click.style("WARN", fg="yellow")
            + ": residual text detected on the base image:"
        )
        for line in fragments:
            click.echo(f"  - {line!r}")
        sys.exit(2)
    click.echo(
        click.style("OK", fg="green")
        + ": no text detected on the base image."
    )


if __name__ == "__main__":
    cli()

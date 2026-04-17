#!/usr/bin/env python3
"""
PhotoStudioHub — AI Photo Processing Tool
Culling · Editing · Retouching — 100% offline, 0 API costs

Usage:
  python main.py cull   --input ./photos --output ./output
  python main.py edit   --input ./selects --output ./edited --profile natural_warm
  python main.py retouch --input ./edited --output ./retouched
  python main.py full   --input ./photos --output ./output --profile natural_warm
"""
import click
from pathlib import Path

from core.export.batch import collect_images, export_selects
from core.export.xmp import write_xmp_from_cull_result
from core.export.report import generate_report
from core.culling.pipeline import run_culling_pipeline
from core.editing.pipeline import run_editing_pipeline
from core.retouching.pipeline import run_retouching_pipeline


@click.group()
@click.version_option("1.0.0", prog_name="PhotoStudioHub")
def cli():
    """PhotoStudioHub — AI photo culling, editing and retouching."""
    pass


@cli.command()
@click.option("--input", "input_dir", required=True, help="Folder with source photos")
@click.option("--output", "output_dir", required=True, help="Output folder")
@click.option("--no-faces", is_flag=True, default=False,
              help="Skip face analysis (faster for landscapes)")
@click.option("--workers", default=4, show_default=True, help="Parallel CPU workers")
def cull(input_dir, output_dir, no_faces, workers):
    """Cull photos: score, group duplicates, select best shots."""
    images = collect_images(input_dir)
    if not images:
        click.echo(f"No images found in {input_dir}")
        return
    click.echo(f"Found {len(images)} photos in {input_dir}")
    result = run_culling_pipeline(images, include_faces=not no_faces, workers=workers)
    out = Path(output_dir)
    selects_dir = out / "selects"
    export_selects(result, str(selects_dir))
    write_xmp_from_cull_result(result)
    report = generate_report(result, str(out / "report.json"))
    click.echo("\n── PhotoStudioHub Report ──────────────────")
    click.echo(f"  Total photos   : {report['summary']['total_photos']}")
    click.echo(f"  Selects        : {report['summary']['selects']}")
    click.echo(f"  Rejects        : {report['summary']['rejects']}")
    click.echo(f"  Select rate    : {report['summary']['select_rate_pct']}%")
    click.echo(f"  Duplicate groups: {report['summary']['duplicate_groups']}")
    click.echo(f"  Report saved   : {out / 'report.json'}")
    click.echo("───────────────────────────────────────────")


@cli.command()
@click.option("--input", "input_dir", required=True)
@click.option("--output", "output_dir", required=True)
@click.option("--profile", default=None, help="Style profile name (see profiles/)")
@click.option("--no-wb", is_flag=True, default=False)
@click.option("--no-noise", is_flag=True, default=False)
@click.option("--no-sharpen", is_flag=True, default=False)
@click.option("--bokeh", is_flag=True, default=False, help="Add portrait bokeh")
@click.option("--upscale", is_flag=True, default=False, help="AI super-resolution 2x")
def edit(input_dir, output_dir, profile, no_wb, no_noise, no_sharpen, bokeh, upscale):
    """Edit photos: WB, exposure, noise, sharpening, style profiles."""
    images = collect_images(input_dir)
    if not images:
        click.echo(f"No images found in {input_dir}")
        return
    options = {
        "do_wb": not no_wb,
        "do_noise": not no_noise,
        "do_sharpen": not no_sharpen,
        "do_bokeh": bokeh,
        "do_upscale": upscale,
    }
    results = run_editing_pipeline(images, output_dir, profile=profile, options=options)
    click.echo(f"\n✓ Edited {len(results)} photos → {output_dir}")


@cli.command()
@click.option("--input", "input_dir", required=True)
@click.option("--output", "output_dir", required=True)
@click.option("--no-blemish", is_flag=True, default=False)
@click.option("--no-skin", is_flag=True, default=False)
@click.option("--no-eyes", is_flag=True, default=False)
@click.option("--no-teeth", is_flag=True, default=False)
@click.option("--align", is_flag=True, default=False, help="Align faces for series")
@click.option("--eye-color", default=None, type=int,
              help="Change eye color (hue 0-179: 0=red,60=green,120=blue)")
def retouch(input_dir, output_dir, no_blemish, no_skin, no_eyes, no_teeth, align, eye_color):
    """Retouch portraits: skin, eyes, teeth, blemishes."""
    images = collect_images(input_dir)
    if not images:
        click.echo(f"No images found in {input_dir}")
        return
    options = {
        "do_blemish": not no_blemish,
        "do_skin_smooth": not no_skin,
        "do_eye_bright": not no_eyes,
        "do_teeth": not no_teeth,
        "do_align": align,
        "eye_color_hue": eye_color,
    }
    results = run_retouching_pipeline(images, output_dir, options=options)
    click.echo(f"\n✓ Retouched {len(results)} portraits → {output_dir}")


@cli.command()
@click.option("--input", "input_dir", required=True)
@click.option("--output", "output_dir", required=True)
@click.option("--profile", default="natural_warm", show_default=True)
@click.option("--workers", default=4, show_default=True)
def full(input_dir, output_dir, profile, workers):
    """Full pipeline: cull → edit → retouch selects only."""
    out = Path(output_dir)
    images = collect_images(input_dir)
    if not images:
        click.echo(f"No images found in {input_dir}")
        return
    click.echo(f"\n[1/3] Culling {len(images)} photos...")
    cull_result = run_culling_pipeline(images, workers=workers)
    write_xmp_from_cull_result(cull_result)
    selects_dir = out / "selects"
    exported = export_selects(cull_result, str(selects_dir))
    click.echo(f"      → {len(exported)} selects")
    click.echo(f"\n[2/3] Editing {len(exported)} selects...")
    edited_dir = out / "edited"
    edited = run_editing_pipeline(exported, str(edited_dir), profile=profile)
    click.echo(f"      → {len(edited)} edited")
    click.echo(f"\n[3/3] Retouching {len(edited)} portraits...")
    retouched_dir = out / "retouched"
    retouched = run_retouching_pipeline(edited, str(retouched_dir))
    click.echo(f"      → {len(retouched)} retouched")
    report = generate_report(cull_result, str(out / "report.json"))
    click.echo("\n── PhotoStudioHub Complete ────────────────")
    click.echo(f"  Input photos   : {report['summary']['total_photos']}")
    click.echo(f"  Final selects  : {len(retouched)}")
    click.echo(f"  Select rate    : {report['summary']['select_rate_pct']}%")
    click.echo(f"  Output folder  : {out}")
    click.echo("───────────────────────────────────────────")


if __name__ == "__main__":
    cli()

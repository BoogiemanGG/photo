from pathlib import Path
from tqdm import tqdm

from core.editing.white_balance import auto_white_balance
from core.editing.exposure_adj import adjust_exposure, shadows_highlights
from core.editing.noise_reduction import reduce_noise
from core.editing.sharpening import sharpen
from core.editing.presets import apply_profile, list_profiles
from core.editing.vignette import add_vignette
from core.editing.bokeh import portrait_bokeh
from core.editing.background import remove_background
from core.editing.upscaling import upscale
from core.editing.raw_convert import convert_raw, RAW_EXTENSIONS
from core.editing.exif_ops import copy_exif, batch_rename_with_exif
import config


def edit_single(
    image_path: str,
    output_path: str,
    profile: str | None = None,
    do_wb: bool = True,
    do_exposure: bool = True,
    do_noise: bool = True,
    do_sharpen: bool = True,
    do_vignette: bool = False,
    do_bokeh: bool = False,
    do_upscale: bool = False,
) -> str:
    p = Path(image_path)
    work_path = image_path

    # RAW → JPG first if needed
    if p.suffix.lower() in RAW_EXTENSIONS:
        raw_out = str(Path(output_path).with_suffix(".jpg"))
        work_path = convert_raw(image_path, raw_out)

    current = work_path

    if profile:
        out = str(Path(output_path).with_stem(p.stem + "_preset"))
        current = apply_profile(current, out, profile)

    if do_wb:
        out = str(Path(output_path).with_stem(p.stem + "_wb"))
        current = auto_white_balance(current, out)

    if do_exposure:
        out = str(Path(output_path).with_stem(p.stem + "_exp"))
        current = adjust_exposure(current, out)

    if do_noise:
        out = str(Path(output_path).with_stem(p.stem + "_nr"))
        current = reduce_noise(current, out)

    if do_sharpen:
        out = str(Path(output_path).with_stem(p.stem + "_sharp"))
        current = sharpen(current, out)

    if do_vignette:
        out = str(Path(output_path).with_stem(p.stem + "_vig"))
        current = add_vignette(current, out)

    if do_bokeh:
        out = str(Path(output_path).with_stem(p.stem + "_bokeh"))
        current = portrait_bokeh(current, out)

    if do_upscale:
        out = str(Path(output_path).with_stem(p.stem + "_4k"))
        current = upscale(current, out)

    # Move final result to output_path
    if current != output_path:
        Path(current).rename(output_path)

    copy_exif(image_path, output_path)
    return output_path


def run_editing_pipeline(
    image_paths: list[str],
    output_dir: str,
    profile: str | None = None,
    options: dict | None = None,
) -> list[str]:
    options = options or {}
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    print(f"[PhotoStudioHub] Editing {len(image_paths)} photos...")
    for path in tqdm(image_paths, desc="Editing"):
        p = Path(path)
        _ext = {"JPEG": ".jpg", "PNG": ".png", "TIFF": ".tiff"}.get(
            config.OUTPUT_FORMAT, ".jpg")
        out = str(out_dir / f"{p.stem}_edited{_ext}")
        try:
            result = edit_single(path, out, profile=profile, **options)
            results.append(result)
        except Exception as e:
            print(f"  ✗ {p.name}: {e}")
    print(f"  ✓ Editing done — {len(results)} photos processed")
    return results

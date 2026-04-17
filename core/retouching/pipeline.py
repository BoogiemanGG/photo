from pathlib import Path
from tqdm import tqdm

from core.retouching.blemish import remove_blemishes
from core.retouching.skin_smooth import smooth_skin
from core.retouching.dark_circles import reduce_dark_circles
from core.retouching.eye_bright import brighten_eyes
from core.retouching.teeth_white import whiten_teeth
from core.retouching.shine_remove import remove_shine
from core.retouching.eye_color import change_eye_color
from core.retouching.red_eye import remove_red_eye
from core.retouching.age_aware import get_retouch_intensity
from core.retouching.face_align import align_face
from core.retouching.dust_detect import remove_dust_spots


def retouch_single(
    image_path: str,
    output_path: str,
    do_blemish: bool = True,
    do_skin_smooth: bool = True,
    do_dark_circles: bool = True,
    do_eye_bright: bool = True,
    do_teeth: bool = True,
    do_shine: bool = True,
    do_red_eye: bool = True,
    do_dust: bool = True,
    do_align: bool = False,
    eye_color_hue: int | None = None,
    age_aware: bool = True,
) -> str:
    p = Path(image_path)
    intensity = get_retouch_intensity(image_path) if age_aware else 1.0
    current = image_path

    steps = []
    if do_dust:
        steps.append(("dust", remove_dust_spots))
    if do_red_eye:
        steps.append(("redeye", remove_red_eye))
    if do_blemish:
        steps.append(("blemish", remove_blemishes))
    if do_shine:
        steps.append(("shine", remove_shine))
    if do_skin_smooth:
        steps.append(("skin", smooth_skin))
    if do_dark_circles:
        steps.append(("darkcircles", reduce_dark_circles))
    if do_eye_bright:
        steps.append(("eyebright", brighten_eyes))
    if do_teeth:
        steps.append(("teeth", whiten_teeth))
    if do_align:
        steps.append(("align", align_face))

    for step_name, fn in steps:
        step_out = str(Path(output_path).with_stem(f"{p.stem}_{step_name}"))
        try:
            current = fn(current, step_out)
        except Exception as e:
            print(f"  ✗ {step_name} on {p.name}: {e}")

    if eye_color_hue is not None:
        eye_out = str(Path(output_path).with_stem(f"{p.stem}_eyecolor"))
        current = change_eye_color(current, eye_out, target_hue=eye_color_hue)

    # Rename final to output_path
    if current != output_path:
        Path(current).rename(output_path)

    return output_path


def run_retouching_pipeline(
    image_paths: list[str],
    output_dir: str,
    options: dict | None = None,
) -> list[str]:
    options = options or {}
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    print(f"[PhotoStudioHub] Retouching {len(image_paths)} portraits...")
    for path in tqdm(image_paths, desc="Retouching"):
        p = Path(path)
        out = str(out_dir / f"{p.stem}_retouched.jpg")
        try:
            result = retouch_single(path, out, **options)
            results.append(result)
        except Exception as e:
            print(f"  ✗ {p.name}: {e}")
    print(f"  ✓ Retouching done — {len(results)} portraits processed")
    return results

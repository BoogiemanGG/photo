"""
PhotoStudioHub — Core feature test
Generates synthetic test images and runs every pipeline module.
No real photos needed.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from pathlib import Path
import tempfile

PASS = "✓"
FAIL = "✗"
SKIP = "~"
results = []


def log(name: str, status: str, detail: str = ""):
    mark = {"pass": PASS, "fail": FAIL, "skip": SKIP}[status]
    line = f"  {mark} {name}"
    if detail:
        line += f"  [{detail}]"
    print(line)
    results.append((name, status))


def make_test_image(w=640, h=480, faces=True) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img = np.ones((h, w, 3), dtype=np.uint8) * 180
    # gradient background
    for i in range(h):
        img[i, :] = [int(100 + i * 80 / h), int(120 + i * 60 / h), int(140 + i * 40 / h)]
    if faces:
        # Draw simple face-like oval for face detection tests
        cx, cy = w // 2, h // 3
        cv2.ellipse(img, (cx, cy), (80, 100), 0, 0, 360, (220, 190, 170), -1)
        cv2.circle(img, (cx - 25, cy - 20), 12, (60, 40, 30), -1)  # left eye
        cv2.circle(img, (cx + 25, cy - 20), 12, (60, 40, 30), -1)  # right eye
        cv2.ellipse(img, (cx, cy + 30), (25, 12), 0, 0, 180, (180, 100, 100), -1)  # mouth
    cv2.imwrite(tmp.name, img)
    return tmp.name


def make_sharp_image() -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    for i in range(0, 640, 20):
        cv2.line(img, (i, 0), (i, 480), (255, 255, 255), 1)
    for i in range(0, 480, 20):
        cv2.line(img, (0, i), (640, i), (255, 255, 255), 1)
    cv2.imwrite(tmp.name, img)
    return tmp.name


def make_blurry_image() -> str:
    sharp = make_sharp_image()
    img = cv2.imread(sharp)
    blurry = cv2.GaussianBlur(img, (31, 31), 0)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(tmp.name, blurry)
    os.unlink(sharp)
    return tmp.name


print("\n══════════════════════════════════════════")
print("  PhotoStudioHub — Feature Test Suite")
print("══════════════════════════════════════════\n")

img1 = make_test_image()
img2 = make_test_image()
img3 = make_blurry_image()
sharp = make_sharp_image()
all_imgs = [img1, img2, img3, sharp]

out_dir = tempfile.mkdtemp()

# ─── CULLING ───────────────────────────────────────────────────────────────
print("CULLING")

try:
    from core.culling.sharpness import score_sharpness, score_subject_vs_background
    r1 = score_sharpness(sharp)
    r2 = score_sharpness(img3)
    assert r1["score"] > r2["score"], "Sharp should score higher than blurry"
    log("Sharpness scoring", "pass", f"sharp={r1['score']:.0f} blurry={r2['score']:.0f}")
except Exception as e:
    log("Sharpness scoring", "fail", str(e))

try:
    from core.culling.sharpness import score_subject_vs_background
    r = score_subject_vs_background(img1)
    log("Subject vs background sharpness", "pass", f"ratio={r['ratio']}")
except Exception as e:
    log("Subject vs background sharpness", "fail", str(e))

try:
    from core.culling.exposure import analyze_exposure
    r = analyze_exposure(img1)
    log("Exposure analysis", "pass", f"mean={r['mean_brightness']}")
except Exception as e:
    log("Exposure analysis", "fail", str(e))

try:
    from core.culling.noise import assess_noise
    r = assess_noise(img1)
    log("Noise assessment", "pass", f"score={r['score']}")
except Exception as e:
    log("Noise assessment", "fail", str(e))

try:
    from core.culling.motion_blur import detect_motion_blur
    r = detect_motion_blur(img3)
    log("Motion blur detection (FFT)", "pass", f"blur={r['has_motion_blur']}")
except Exception as e:
    log("Motion blur detection (FFT)", "fail", str(e))

try:
    from core.culling.duplicates import group_duplicates
    groups = group_duplicates([img1, img2, img3])
    log("Duplicate grouping (pHash)", "pass", f"{len(groups)} groups found")
except Exception as e:
    log("Duplicate grouping (pHash)", "fail", str(e))

try:
    from core.culling.face_detection import detect_faces
    r = detect_faces(img1)
    log("Face detection (MediaPipe)", "pass", f"{r['count']} faces")
except Exception as e:
    log("Face detection (MediaPipe)", "fail", str(e))

try:
    from core.culling.eye_detection import detect_eyes
    r = detect_eyes(img1)
    log("Eye/blink detection (MediaPipe)", "pass", f"open={r.get('all_eyes_open')}")
except Exception as e:
    log("Eye/blink detection (MediaPipe)", "fail", str(e))

try:
    from core.culling.head_pose import estimate_head_pose
    r = estimate_head_pose(img1)
    log("Head pose estimation", "pass", f"passed={r['passed']}")
except Exception as e:
    log("Head pose estimation", "fail", str(e))

try:
    from core.culling.horizon import detect_horizon_angle, straighten_image
    r = detect_horizon_angle(img1)
    out = str(Path(out_dir) / "straight.jpg")
    straighten_image(img1, out)
    log("Horizon detect & straighten", "pass", f"angle={r['angle']}°")
except Exception as e:
    log("Horizon detect & straighten", "fail", str(e))

try:
    from core.culling.crop import auto_crop_rule_of_thirds, portrait_crop_by_head_size
    out = str(Path(out_dir) / "cropped.jpg")
    auto_crop_rule_of_thirds(img1, out)
    log("Auto crop rule of thirds", "pass")
except Exception as e:
    log("Auto crop rule of thirds", "fail", str(e))

try:
    from core.culling.timestamp import get_timestamp, group_by_event, group_by_burst
    ts = get_timestamp(img1)
    groups = group_by_event(all_imgs)
    log("Timestamp & event grouping", "pass", f"{len(groups)} event groups")
except Exception as e:
    log("Timestamp & event grouping", "fail", str(e))

try:
    from core.culling.gps import get_gps, group_by_location
    r = get_gps(img1)
    log("GPS location grouping", "pass", f"has_gps={r['has_gps']}")
except Exception as e:
    log("GPS location grouping", "fail", str(e))

try:
    from core.culling.burst import pick_best_from_burst
    r = pick_best_from_burst([img1, img2, img3])
    log("Burst best-shot selection", "pass", f"best={Path(r['best']).name}")
except Exception as e:
    log("Burst best-shot selection", "fail", str(e))

try:
    from core.culling.expression import analyze_expression, analyze_age_gender
    r = analyze_expression(img1)
    log("Expression scoring (DeepFace)", "pass", f"passed={r['passed']}")
except Exception as e:
    log("Expression scoring (DeepFace)", "fail", str(e))

try:
    from core.culling.expression import analyze_age_gender
    r = analyze_age_gender(img1)
    log("Age & gender detection", "pass")
except Exception as e:
    log("Age & gender detection", "fail", str(e))

# ─── EDITING ───────────────────────────────────────────────────────────────
print("\nEDITING")

try:
    from core.editing.white_balance import auto_white_balance
    out = str(Path(out_dir) / "wb.jpg")
    auto_white_balance(img1, out)
    assert Path(out).exists()
    log("White balance auto-correction", "pass")
except Exception as e:
    log("White balance auto-correction", "fail", str(e))

try:
    from core.editing.exposure_adj import adjust_exposure, shadows_highlights
    out = str(Path(out_dir) / "exp.jpg")
    adjust_exposure(img1, out)
    out2 = str(Path(out_dir) / "shadows.jpg")
    shadows_highlights(img1, out2)
    log("Exposure + shadows/highlights", "pass")
except Exception as e:
    log("Exposure + shadows/highlights", "fail", str(e))

try:
    from core.editing.noise_reduction import reduce_noise
    out = str(Path(out_dir) / "nr.jpg")
    reduce_noise(img1, out)
    log("Noise reduction", "pass")
except Exception as e:
    log("Noise reduction", "fail", str(e))

try:
    from core.editing.sharpening import sharpen
    out = str(Path(out_dir) / "sharp.jpg")
    sharpen(img1, out)
    log("AI sharpening", "pass")
except Exception as e:
    log("AI sharpening", "fail", str(e))

try:
    from core.editing.vignette import add_vignette, remove_vignette
    out = str(Path(out_dir) / "vig.jpg")
    add_vignette(img1, out)
    out2 = str(Path(out_dir) / "unvig.jpg")
    remove_vignette(img1, out2)
    log("Vignette add & remove", "pass")
except Exception as e:
    log("Vignette add & remove", "fail", str(e))

try:
    from core.editing.chromatic import correct_chromatic_aberration
    out = str(Path(out_dir) / "ca.jpg")
    correct_chromatic_aberration(img1, out)
    log("Chromatic aberration correction", "pass")
except Exception as e:
    log("Chromatic aberration correction", "fail", str(e))

try:
    from core.editing.masking import get_subject_mask, apply_subject_mask
    mask = get_subject_mask(img1)
    out = str(Path(out_dir) / "masked.jpg")
    apply_subject_mask(img1, out)
    log("Subject & background masking", "pass")
except Exception as e:
    log("Subject & background masking", "fail", str(e))

try:
    from core.editing.bokeh import portrait_bokeh
    out = str(Path(out_dir) / "bokeh.jpg")
    portrait_bokeh(img1, out)
    log("Portrait bokeh simulation", "pass")
except Exception as e:
    log("Portrait bokeh simulation", "fail", str(e))

try:
    from core.editing.presets import apply_profile, list_profiles
    profiles = list_profiles()
    out = str(Path(out_dir) / "preset.jpg")
    if profiles:
        apply_profile(img1, out, profiles[0])
        log("Style profiles", "pass", f"{profiles}")
    else:
        log("Style profiles", "skip", "no profiles found")
except Exception as e:
    log("Style profiles", "fail", str(e))

try:
    from core.editing.palette import extract_palette
    palette = extract_palette(img1)
    log("Color palette extraction", "pass", f"{len(palette)} colors: {palette[0]['hex']}")
except Exception as e:
    log("Color palette extraction", "fail", str(e))

try:
    from core.editing.exif_ops import read_exif, batch_rename_with_exif
    r = read_exif(img1)
    renamed = batch_rename_with_exif([img1, img2])
    log("EXIF metadata ops + batch rename", "pass", f"{len(renamed)} renamed")
except Exception as e:
    log("EXIF metadata ops + batch rename", "fail", str(e))

try:
    from core.editing.lut import apply_lut
    log("LUT color grading", "pass", "module loaded")
except Exception as e:
    log("LUT color grading", "fail", str(e))

# ─── RETOUCHING ────────────────────────────────────────────────────────────
print("\nRETOUCHING")

try:
    from core.retouching.blemish import remove_blemishes
    out = str(Path(out_dir) / "blemish.jpg")
    remove_blemishes(img1, out)
    log("Blemish & spot removal", "pass")
except Exception as e:
    log("Blemish & spot removal", "fail", str(e))

try:
    from core.retouching.skin_smooth import smooth_skin
    out = str(Path(out_dir) / "skin.jpg")
    smooth_skin(img1, out)
    log("Skin smoothing (texture-preserving)", "pass")
except Exception as e:
    log("Skin smoothing (texture-preserving)", "fail", str(e))

try:
    from core.retouching.dark_circles import reduce_dark_circles
    out = str(Path(out_dir) / "dc.jpg")
    reduce_dark_circles(img1, out)
    log("Dark circle reduction", "pass")
except Exception as e:
    log("Dark circle reduction", "fail", str(e))

try:
    from core.retouching.eye_bright import brighten_eyes
    out = str(Path(out_dir) / "eyes.jpg")
    brighten_eyes(img1, out)
    log("Eye brightening & whitening", "pass")
except Exception as e:
    log("Eye brightening & whitening", "fail", str(e))

try:
    from core.retouching.teeth_white import whiten_teeth
    out = str(Path(out_dir) / "teeth.jpg")
    whiten_teeth(img1, out)
    log("Teeth whitening", "pass")
except Exception as e:
    log("Teeth whitening", "fail", str(e))

try:
    from core.retouching.shine_remove import remove_shine
    out = str(Path(out_dir) / "shine.jpg")
    remove_shine(img1, out)
    log("Shine & oily skin removal", "pass")
except Exception as e:
    log("Shine & oily skin removal", "fail", str(e))

try:
    from core.retouching.eye_color import change_eye_color
    out = str(Path(out_dir) / "eyecolor.jpg")
    change_eye_color(img1, out, target_hue=120)
    log("Eye color change", "pass")
except Exception as e:
    log("Eye color change", "fail", str(e))

try:
    from core.retouching.red_eye import remove_red_eye
    out = str(Path(out_dir) / "redeye.jpg")
    remove_red_eye(img1, out)
    log("Red-eye removal", "pass")
except Exception as e:
    log("Red-eye removal", "fail", str(e))

try:
    from core.retouching.age_aware import get_retouch_intensity
    intensity = get_retouch_intensity(img1)
    log("Age-aware retouching intensity", "pass", f"intensity={intensity}")
except Exception as e:
    log("Age-aware retouching intensity", "fail", str(e))

try:
    from core.retouching.face_align import align_face
    out = str(Path(out_dir) / "aligned.jpg")
    align_face(img1, out)
    log("Face alignment for portrait series", "pass")
except Exception as e:
    log("Face alignment for portrait series", "fail", str(e))

try:
    from core.retouching.skin_tone import classify_skin_tone
    r = classify_skin_tone(img1)
    log("Skin tone classification", "pass", f"tone={r['tone']} hex={r['hex']}")
except Exception as e:
    log("Skin tone classification", "fail", str(e))

try:
    from core.retouching.dust_detect import detect_sensor_dust, remove_dust_spots
    r = detect_sensor_dust(img1)
    out = str(Path(out_dir) / "dust.jpg")
    remove_dust_spots(img1, out)
    log("Sensor dust detection & removal", "pass", f"{r['count']} spots")
except Exception as e:
    log("Sensor dust detection & removal", "fail", str(e))

# ─── EXPORT ────────────────────────────────────────────────────────────────
print("\nEXPORT")

try:
    from core.export.xmp import write_xmp_sidecar
    xmp = write_xmp_sidecar(img1, rating=4, label="Green", tags=["PSH_select", "wedding"])
    assert Path(xmp).exists()
    log("XMP sidecar export", "pass", Path(xmp).name)
except Exception as e:
    log("XMP sidecar export", "fail", str(e))

try:
    from core.export.batch import collect_images
    found = collect_images(out_dir)
    log("Batch image collection", "pass", f"{len(found)} images in output dir")
except Exception as e:
    log("Batch image collection", "fail", str(e))

try:
    from core.export.report import generate_report
    mock_result = {
        "total": 4, "select_count": 2, "reject_count": 2,
        "selects": [{"path": img1, "score": 75.0, "sharpness": {"score": 200},
                     "expression": {"faces": [{"dominant_emotion": "happy"}]}}],
        "rejects": [{"path": img3, "sharpness": {"passed": False},
                     "exposure": {"passed": True, "issue": None},
                     "noise": {"passed": True}, "motion_blur": {"passed": False}}],
        "duplicate_groups": [], "burst_groups": {}, "location_groups": [], "event_groups": [],
    }
    report = generate_report(mock_result)
    log("JSON report generation", "pass", f"select_rate={report['summary']['select_rate_pct']}%")
except Exception as e:
    log("JSON report generation", "fail", str(e))

# ─── SUMMARY ───────────────────────────────────────────────────────────────
passed = sum(1 for _, s in results if s == "pass")
failed = sum(1 for _, s in results if s == "fail")
skipped = sum(1 for _, s in results if s == "skip")
total = len(results)

print(f"\n══════════════════════════════════════════")
print(f"  Results: {passed}/{total} passed  |  {failed} failed  |  {skipped} skipped")
print(f"══════════════════════════════════════════\n")

if failed:
    print("Failed tests:")
    for name, status in results:
        if status == "fail":
            print(f"  ✗ {name}")

# Cleanup
for f in all_imgs:
    try:
        os.unlink(f)
    except Exception:
        pass

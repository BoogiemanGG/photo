import json
from datetime import datetime
from pathlib import Path


def generate_report(cull_result: dict, output_path: str | None = None) -> dict:
    report = {
        "tool": "PhotoStudioHub",
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_photos": cull_result.get("total", 0),
            "selects": cull_result.get("select_count", 0),
            "rejects": cull_result.get("reject_count", 0),
            "select_rate_pct": round(
                cull_result.get("select_count", 0) /
                max(cull_result.get("total", 1), 1) * 100, 1
            ),
            "duplicate_groups": len(cull_result.get("duplicate_groups", [])),
            "burst_groups": len(cull_result.get("burst_groups", {})),
            "location_groups": len(cull_result.get("location_groups", [])),
            "event_groups": len(cull_result.get("event_groups", [])),
        },
        "top_selects": [
            {
                "path": r["path"],
                "score": r.get("score", 0),
                "sharpness": r.get("sharpness", {}).get("score"),
                "expression": (r.get("expression") or {}).get("faces", [{}])[0].get("dominant_emotion"),
            }
            for r in (cull_result.get("selects", [])[:10])
        ],
        "rejection_reasons": _summarize_rejections(cull_result.get("rejects", [])),
    }
    if output_path:
        Path(output_path).write_text(json.dumps(report, indent=2))
    return report


def _summarize_rejections(rejects: list[dict]) -> dict:
    reasons = {
        "blurry": 0, "overexposed": 0, "underexposed": 0,
        "eyes_closed": 0, "bad_expression": 0, "noisy": 0, "motion_blur": 0,
    }
    for r in rejects:
        if not r.get("sharpness", {}).get("passed"):
            reasons["blurry"] += 1
        exp = r.get("exposure", {})
        if exp.get("issue") == "overexposed":
            reasons["overexposed"] += 1
        elif exp.get("issue") in ("underexposed", "clipped_shadows"):
            reasons["underexposed"] += 1
        eyes = r.get("eyes") or {}
        if eyes.get("all_eyes_open") is False:
            reasons["eyes_closed"] += 1
        if not (r.get("expression") or {}).get("passed", True):
            reasons["bad_expression"] += 1
        if not r.get("noise", {}).get("passed", True):
            reasons["noisy"] += 1
        if not r.get("motion_blur", {}).get("passed", True):
            reasons["motion_blur"] += 1
    return {k: v for k, v in reasons.items() if v > 0}

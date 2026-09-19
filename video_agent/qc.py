from __future__ import annotations

import json
from pathlib import Path

from vidgoclip.media import run_process

from .models import QCReport


def inspect_video(
    path: Path,
    *,
    expect_vertical: bool,
    expected_duration: float | None = None,
) -> QCReport:
    issues: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return QCReport(passed=False, issues=["Output file does not exist."])

    if path.stat().st_size < 10_000:
        issues.append("Output file is unexpectedly small.")

    probe = run_process(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]
    )
    if probe.returncode != 0:
        return QCReport(
            passed=False,
            issues=issues + [probe.stderr.strip() or "ffprobe failed."],
        )

    try:
        data = json.loads(probe.stdout)
    except json.JSONDecodeError:
        return QCReport(
            passed=False,
            issues=issues + ["ffprobe returned invalid JSON."],
        )

    streams = data.get("streams") or []
    video = next((x for x in streams if x.get("codec_type") == "video"), None)
    audio = next((x for x in streams if x.get("codec_type") == "audio"), None)

    if video is None:
        issues.append("No video stream found.")
        width = height = None
    else:
        width = int(video.get("width") or 0) or None
        height = int(video.get("height") or 0) or None

    if expect_vertical and (width, height) != (1080, 1920):
        issues.append(
            f"Vertical export is {width}x{height}; expected 1080x1920."
        )

    raw_duration = (data.get("format") or {}).get("duration")
    try:
        duration = float(raw_duration)
    except (TypeError, ValueError):
        duration = None
        warnings.append("Could not determine output duration.")

    if duration is not None and duration < 2.0:
        issues.append("Output is shorter than 2 seconds.")

    if expected_duration and duration is not None:
        tolerance = max(1.5, expected_duration * 0.08)
        if abs(duration - expected_duration) > tolerance:
            warnings.append(
                f"Duration differs from planned clip by "
                f"{abs(duration - expected_duration):.1f}s."
            )

    if audio is None:
        warnings.append("No audio stream found.")

    return QCReport(
        passed=not issues,
        width=width,
        height=height,
        duration=duration,
        has_audio=audio is not None,
        issues=issues,
        warnings=warnings,
    )

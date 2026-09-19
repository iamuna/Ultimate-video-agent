from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable

from vidgoclip.config import OUTPUT_DIR, load_settings
from vidgoclip.exporter import export_clip
from vidgoclip.media import executable_available, safe_slug
from vidgoclip.pipeline import analyze_video

from .director import build_director_plan, infer_focus
from .models import ProducedClip, ProductionRequest, ProductionResult
from .qc import inspect_video

Progress = Callable[[str], None] | None


def _progress(callback: Progress, message: str) -> None:
    if callback:
        callback(message)


def _require_runtime() -> None:
    missing = [
        name for name in ("ffmpeg", "ffprobe")
        if not executable_available(name)
    ]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required video tools: {joined}. "
            "Install FFmpeg and ensure ffmpeg/ffprobe are on PATH."
        )


def _job_output_dir(source: Path, requested: Path | None) -> Path:
    if requested is not None:
        result = requested
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        result = OUTPUT_DIR / f"{stamp}-{safe_slug(source.stem, limit=48)}"
    result.mkdir(parents=True, exist_ok=True)
    return result


def produce_video(
    request: ProductionRequest,
    *,
    progress: Progress = None,
) -> ProductionResult:
    _require_runtime()

    source = Path(request.source_video).expanduser().resolve()
    if not source.is_file():
        raise RuntimeError(f"Source video does not exist: {source}")

    _progress(progress, "Producer: interpreting the production objective...")
    settings = load_settings()
    focus = infer_focus(request.goal, request.focus)
    settings.update(
        {
            "analysis_focus": focus,
            "min_clip_seconds": float(request.min_clip_seconds),
            "target_clip_seconds": float(request.target_clip_seconds),
            "max_clip_seconds": float(request.max_clip_seconds),
        }
    )

    _progress(progress, f"Producer: analyzing source with {focus} focus...")
    analysis = analyze_video(
        source,
        settings=settings,
        progress=progress,
        force=bool(request.force_analysis),
    )
    if not analysis.candidates:
        raise RuntimeError("Analysis completed but found no usable clip candidates.")

    _progress(progress, "Director: choosing the strongest moments for the goal...")
    plan = build_director_plan(
        goal=request.goal,
        focus=focus,
        candidates=analysis.candidates,
        count=max(1, int(request.output_count)),
        ollama_base_url=str(settings["ollama_base_url"]),
        ollama_model=str(settings["ollama_model"]),
    )

    by_id = {candidate.id: candidate for candidate in analysis.candidates}
    output_dir = _job_output_dir(source, request.output_dir)
    clips: list[ProducedClip] = []

    for index, pick in enumerate(plan.picks, start=1):
        candidate = by_id.get(pick.candidate_id)
        if candidate is None:
            continue

        _progress(
            progress,
            f"Editor: rendering clip {index}/{len(plan.picks)} "
            f"({candidate.title or candidate.id})...",
        )
        output = export_clip(
            source,
            candidate,
            destination_dir=output_dir,
            vertical=bool(request.vertical),
            smart_reframe=bool(request.smart_reframe),
            burn_captions=bool(request.burn_captions),
            words=analysis.words,
            transcript=analysis.transcript,
            caption_words_per_line=max(2, int(request.caption_words_per_line)),
            progress=progress,
        )

        _progress(progress, f"QC: checking {output.name}...")
        qc = inspect_video(
            output,
            expect_vertical=bool(request.vertical),
            expected_duration=candidate.duration,
        )

        clips.append(
            ProducedClip(
                candidate_id=candidate.id,
                title=candidate.title or candidate.id,
                source_start=candidate.start,
                source_end=candidate.end,
                final_score=candidate.final_score,
                scores=dict(candidate.scores),
                editorial_reason=pick.editorial_reason,
                output_path=str(output.resolve()),
                qc=qc,
            )
        )

    if not clips:
        raise RuntimeError("The director selected no renderable clips.")

    manifest_path = output_dir / "production_manifest.json"
    result = ProductionResult(
        source_video=str(source),
        output_dir=str(output_dir.resolve()),
        manifest_path=str(manifest_path.resolve()),
        plan=plan,
        clips=clips,
        model_notes=dict(analysis.model_notes),
    )
    manifest_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    passed = sum(1 for clip in clips if clip.qc.passed)
    _progress(
        progress,
        f"Production complete: {len(clips)} clips rendered, "
        f"{passed}/{len(clips)} passed QC.",
    )
    return result

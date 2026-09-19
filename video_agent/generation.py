from __future__ import annotations

from pathlib import Path

from shorts_factory.config import load_settings
from shorts_factory.video_generation import generate_video, generator_ready


def local_generator_available() -> bool:
    settings = load_settings()
    workflow = Path(str(settings["video_workflow_file"]))
    return generator_ready(
        provider_id=str(settings["video_generator_provider"]),
        base_url=str(settings["comfyui_base_url"]),
        workflow_file=workflow,
    )


def generate_broll(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    seconds: int = 5,
    seed: int | None = None,
) -> Path:
    """Generate a local AI-video asset through the reused Yt-smb engine."""
    settings = load_settings()
    workflow = Path(str(settings["video_workflow_file"]))

    result = generate_video(
        provider_id=str(settings["video_generator_provider"]),
        prompt=prompt.strip(),
        negative_prompt=(
            negative_prompt
            if negative_prompt is not None
            else str(settings["video_negative_prompt"])
        ),
        base_url=str(settings["comfyui_base_url"]),
        workflow_file=workflow,
        width=int(settings["video_width"]),
        height=int(settings["video_height"]),
        seconds=max(1, int(seconds)),
        fps=int(settings["video_fps"]),
        seed=seed,
        allow_paid_services=False,
    )
    return result.path

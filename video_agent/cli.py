from __future__ import annotations

import argparse
from pathlib import Path

from .models import ProductionRequest
from .producer import produce_video


def _progress(message: str) -> None:
    print(message, flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ultimate-video-agent",
        description="Autonomous video production agent - v0.1 clipping producer.",
    )
    parser.add_argument("video", type=Path, help="Source video file")
    parser.add_argument(
        "--goal",
        default="Find and produce the strongest standalone moments.",
        help="Natural-language production objective",
    )
    parser.add_argument("--count", type=int, default=5, help="Number of clips")
    parser.add_argument(
        "--focus",
        choices=["Auto", "Balanced", "Important", "Controversial", "Interesting", "Emotional"],
        default="Auto",
    )
    parser.add_argument("--horizontal", action="store_true", help="Keep source aspect ratio")
    parser.add_argument("--no-smart-reframe", action="store_true")
    parser.add_argument("--no-captions", action="store_true")
    parser.add_argument("--force-analysis", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = produce_video(
        ProductionRequest(
            source_video=args.video,
            goal=args.goal,
            output_count=max(1, args.count),
            focus=args.focus,
            vertical=not args.horizontal,
            smart_reframe=not args.no_smart_reframe,
            burn_captions=not args.no_captions,
            force_analysis=args.force_analysis,
            output_dir=args.output_dir,
        ),
        progress=_progress,
    )

    print()
    print(f"Output: {result.output_dir}")
    print(f"Manifest: {result.manifest_path}")
    for clip in result.clips:
        status = "PASS" if clip.qc.passed else "CHECK"
        print(
            f"[{status}] {clip.title} | {clip.final_score:.1f}/100 | "
            f"{clip.output_path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

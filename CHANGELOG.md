# Changelog

## v0.1.0 — Autonomous Clipping Producer

Initial Ultimate Video Agent foundation.

### Production-agent layer
- Added natural-language production objectives.
- Added automatic focus inference.
- Added local Ollama producer/director selection with deterministic fallback.
- Added end-to-end `produce_video()` orchestration.
- Added visible per-clip scorecards and editorial reasons in the production manifest.
- Added post-render QC for stream presence, vertical dimensions, duration, and audio.
- Added GUI and CLI entry points.

### Reused from Vid-go-clip
- Word-level faster-whisper transcription.
- Scene detection.
- Candidate generation and context/boundary refinement.
- Semantic, visual, motion, audio, and context scoring.
- Face/motion-aware smart 9:16 reframing.
- Timed ASS captions.
- FFmpeg clip export.

### Reused from Yt-smb
- Local ComfyUI/Wan video generation engine.
- Bundled Wan workflow.
- 1080x1920 finishing.
- Local generator installer/start scripts.
- Editing utilities and local cost-safety policy.

### Integration fixes
- Separated clipper and generator settings to prevent the old projects from overwriting one another.
- Added a shared dependency file and one-click Windows setup/start flow.

### Known limitation
- Generated video assets are available through the generation adapter but are not yet autonomously inserted as B-roll into clip timelines.

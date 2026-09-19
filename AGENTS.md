# AGENTS.md — Ultimate Video Agent

## Mission

Ultimate Video Agent is a **video production agent**, not merely an AI editor.

The long-term goal is:

> Raw footage / assets / prompt -> understand the material -> choose a creative plan -> edit -> quality-check -> deliver finished videos.

The current milestone is **v0.1 Autonomous Clipping Producer**.

## Repository ownership

All new development belongs in:

- `iamuna/Ultimate-video-agent`

Two older repositories are source projects and should not be modified as part of this project unless the owner explicitly asks:

- `iamuna/Vid-go-clip`
- `iamuna/Yt-smb`

## Reused source baselines

The initial integration copied proven modules from:

- Vid-go-clip main at commit `e854f8c12cd845b6a587847b91fa348a788f9697`
- Yt-smb main at commit `50a56000276ee001105471e3a929877c5580c9a9`

Those modules live in the new repo so the production agent can evolve independently.

## Architecture

### `video_agent/` — new agent layer

This is the primary product logic.

- `models.py` — production job/result data model.
- `director.py` — interprets the objective, selects editorial focus, asks local Ollama to choose moments, and has a deterministic fallback.
- `producer.py` — end-to-end production orchestration.
- `qc.py` — post-render ffprobe validation.
- `generation.py` — adapter to the local ComfyUI/Wan generation engine.
- `cli.py` — command-line entry point.

### `vidgoclip/` — reused analysis/editing engine

Provides:

- faster-whisper transcription + word timing
- scene detection
- candidate windows and context/boundary refinement
- semantic scorecard
- visual/motion scoring
- audio-event scoring
- face/motion-aware 9:16 reframing
- word-timed captions
- FFmpeg export

The legacy engine was intentionally kept as its own package so it can be upgraded or replaced without mixing it into the director.

### `shorts_factory/` — reused creator/generator engine

Provides:

- local ComfyUI/Wan video generation
- 1080x1920 finishing
- vertical video assembly helpers
- local cost-safety policy
- optional TTS/editor pieces inherited from Yt-smb

### `workflows/` and `tools/`

Contain the local Wan/ComfyUI workflow and setup/start scripts reused from Yt-smb.

## Settings

The old projects both used `data/settings.json`. This was deliberately changed during integration to prevent collisions:

- `data/clipper_settings.json`
- `data/generation_settings.json`

Do not merge these back into one unstructured settings file.

## v0.1 production flow

1. User selects a source video and writes a natural-language objective.
2. Director infers an editorial focus: Balanced / Important / Controversial / Interesting / Emotional.
3. Vid-go-clip engine transcribes, detects scenes, builds moments, scores semantic/visual/audio/context signals, refines boundaries, and deduplicates.
4. Director uses local Ollama when available to choose the best candidate set for the objective.
5. If Ollama is unavailable, deterministic score-ranked selection is used.
6. Editor exports clips with optional 9:16 smart reframe and timed captions.
7. QC probes every rendered file for video stream, dimensions, duration, and audio.
8. A `production_manifest.json` records strategy, scorecards, reasons, outputs, and QC.

## Important product rule

Do not turn this into a collection of unrelated buttons.

Every capability should be usable by the producer/director layer so the user can express a **goal**, not a sequence of editing operations.

## Scorecard

Suggested moments expose component scores from the clipping engine:

- importance
- controversy
- interest
- emotion
- visual
- audio
- context
- final weighted score

The director may choose a lower raw-score clip when it serves the stated production objective better. The manifest must preserve the reason.

## Cost policy

Current default architecture is local-first:

- local Whisper
- local Ollama
- local FFmpeg/OpenCV
- local ComfyUI/Wan generation

Do not silently add a paid API or provider. Any potentially paid provider must require an explicit opt-in and remain clearly marked.

## Current limitations

v0.1 is primarily an autonomous clipping producer.

The generation adapter can create AI video assets, but generated B-roll is **not yet automatically inserted into the clipping timeline**. Do not claim otherwise.

Identity-level speaker diarization is not implemented. Existing speaker-turn behavior is timing/pause heuristic.

The current reframer uses face detection and motion fallback rather than a modern person/active-speaker tracker.

The GUI does not yet show an editable production timeline or pre-render approval board.

## Next priorities

1. Production board: source overview, director plan, candidate scorecards, preview/approve/reject.
2. Better semantic story understanding across the full source rather than candidate-only reasoning.
3. Speaker diarization and active-speaker tracking.
4. B-roll/generative asset planning and timeline insertion.
5. Audio cleanup/mixing agent.
6. Hook/opening optimization and pacing edits.
7. Multi-format outputs from one job.
8. Full rendered-video vision review before final delivery.
9. Learning from user approvals/rejections and manual edits.

## Validation

The GitHub workflow in `.github/workflows/validate.yml` performs syntax compilation and repository-structure tests.

Local quick validation:

```bat
.venv\Scripts\python -m compileall -q video_agent vidgoclip shorts_factory app.py
.venv\Scripts\python -m unittest discover -s tests
```

Runtime video validation additionally requires FFmpeg/ffprobe and a real source file.

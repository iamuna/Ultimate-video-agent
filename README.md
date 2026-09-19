# Ultimate Video Agent

**A video production agent, not just an AI video editor.**

Ultimate Video Agent takes a source video plus a natural-language production objective and coordinates analysis, editorial selection, rendering, and quality control.

The long-term target is:

> Raw footage / assets / prompt -> understand everything -> choose a creative plan -> edit -> review -> deliver finished videos.

## Current milestone: v0.1 Autonomous Clipping Producer

The first usable workflow is:

**Video + objective -> understand -> score -> direct -> edit -> QC -> finished clips**

Example objective:

> Turn this podcast into the strongest 6 clips under roughly a minute. Prioritize surprising arguments and important statements, but keep enough context that none of the clips are misleading.

The agent then:

1. transcribes the source with word-level timing;
2. detects scene/shot boundaries;
3. builds possible clip windows;
4. scores importance, controversy, interest, emotion, visual value, audio energy, and context;
5. refines clip boundaries around words, pauses, and complete thoughts;
6. asks the local producer/director model to choose the moments that best serve the objective;
7. falls back to deterministic ranking when local AI is unavailable;
8. exports polished clips;
9. optionally creates true 1080x1920 vertical output with face/motion-aware smart reframing;
10. burns word-timed captions when enabled;
11. runs technical QC on every rendered output;
12. saves the director strategy, scorecards, reasons, outputs, and QC in a production manifest.

## Where the technology came from

This repo intentionally builds on two earlier projects owned by the same developer.

### Vid-go-clip

Reused as the analysis/clipping engine:

- faster-whisper transcription
- word timestamps
- scene detection
- candidate generation
- semantic scoring
- visual/motion scoring
- audio-event scoring
- context and boundary refinement
- smart 9:16 reframing
- timed captions
- FFmpeg export

### Yt-smb

Reused as the creator/generation engine:

- local ComfyUI/Wan video generation
- bundled Wan workflow
- 1080x1920 finishing
- local generator installer/start scripts
- vertical editing utilities
- local cost-safety policy

The old repositories are treated as source projects. **All new development happens here.**

## New production-agent layer

The new `video_agent/` package sits above both reused engines.

- `video_agent/director.py` — interprets the objective and chooses the editorial set.
- `video_agent/producer.py` — executes the full production job.
- `video_agent/qc.py` — checks rendered outputs.
- `video_agent/generation.py` — exposes the local generation engine as a production capability.
- `video_agent/models.py` — stable job/result data structures.
- `video_agent/cli.py` — command-line interface.

This separation is deliberate: the director decides **what should be produced**, while specialist engines perform the work.

## Quick start on Windows

### 1. Setup

Run:

```bat
setup.bat
```

This creates a local Python environment and installs the application dependencies.

FFmpeg and ffprobe must also be available on PATH.

### 2. Launch

Run:

```bat
start.bat
```

Then:

- choose a source video;
- describe what you want in **Production objective**;
- choose how many clips you want;
- leave Focus on **Auto** unless you specifically want one editorial emphasis;
- keep **9:16 vertical**, **Smart reframe**, and **Captions** enabled for Shorts-style output;
- click **PRODUCE CLIPS**.

## CLI

You can also run:

```bat
.venv\Scripts\python -m video_agent "C:\path\video.mp4" --goal "Find the strongest controversial and surprising moments" --count 5
```

Useful options include:

```text
--focus Auto|Balanced|Important|Controversial|Interesting|Emotional
--horizontal
--no-smart-reframe
--no-captions
--force-analysis
--output-dir PATH
```

## Local AI

The application is designed to remain useful without a cloud AI API.

When Ollama is available, the clipping engine and director can use the configured local model for deeper semantic/visual/editorial reasoning.

Default clipper configuration currently points to:

```text
http://127.0.0.1:11434
qwen3-vl:4b
```

If Ollama is unavailable, the production job still works with fallback scoring/selection, but editorial understanding will be less sophisticated.

## Local AI video generation

The reused Yt-smb generator supports local ComfyUI/Wan generation.

The bundled start/setup flow is available through:

```bat
start_video_generator.bat
```

The production-agent adapter is:

```python
from video_agent.generation import generate_broll

path = generate_broll("cinematic close-up of sparks inside an industrial reactor")
```

**Current limitation:** v0.1 can generate an asset, but the director does not yet automatically decide where generated B-roll belongs in an existing clip timeline. That is a later milestone.

## Output

Each production run creates a job folder under `output/` unless another destination is selected.

A job contains the rendered videos plus:

```text
production_manifest.json
```

The manifest records:

- source video
- production objective
- director focus
- director strategy
- whether local AI chose the set
- selected candidate IDs
- editorial reasons
- full component scorecards
- final weighted score
- source timestamps
- rendered output path
- QC result
- model/runtime notes

The manifest is intended to become the durable handoff between the director, future timeline editor, final-review agent, UI, and preference-learning system.

## Cost policy

The current architecture is local-first:

- Whisper: local
- Ollama: local
- FFmpeg/OpenCV: local
- ComfyUI/Wan: local

Potentially paid providers should never be silently enabled. The reused generator policy defaults to blocking services marked as potentially paid unless explicitly permitted.

## Repository layout

```text
Ultimate-video-agent/
|-- app.py
|-- video_agent/          # new producer/director/QC layer
|-- vidgoclip/            # reused analysis + clipping engine
|-- shorts_factory/       # reused creator/generator engine
|-- workflows/            # local video-generation workflows
|-- tools/                # local generator setup/start tools
|-- docs/
|-- tests/
|-- setup.bat
|-- start.bat
|-- start_video_generator.bat
|-- AGENTS.md
|-- CHANGELOG.md
`-- requirements.txt
```

## Roadmap

The next major step is a **Production Board**: show the source understanding, director plan, ranked moments, scorecards, and previews before or alongside final export.

After that, the architecture is intended to grow toward:

- full-source story reasoning
- speaker diarization and active-speaker tracking
- automatic B-roll planning/insertion
- generated shot planning
- pacing/silence/filler edits
- audio cleanup and mixing
- music/SFX decisions
- hooks and cold opens
- graphics/title cards/lower thirds
- long-form edits
- multiple platform versions from one job
- final rendered-video vision review
- learning from approve/reject/manual-edit feedback

See `docs/ARCHITECTURE.md` and `AGENTS.md` for the detailed design and continuation notes.

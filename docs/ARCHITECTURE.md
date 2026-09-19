# Architecture

## North star

Ultimate Video Agent should behave like a production team behind one interface.

The user gives it **material + an objective**. Internally the system can use specialized engines, but the user should not need to manually coordinate them.

## Layers

### 1. Understanding

Current inputs:

- speech transcript and word timing
- scene/shot boundaries
- sampled visual frames
- motion
- audio energy/transients
- semantic candidate analysis

Future inputs:

- identity-level speaker diarization
- active speaker
- objects/actions/events
- facial/emotional reaction
- music and audio classification
- full-source topic/story map

### 2. Director

`video_agent/director.py` turns an objective into an editorial selection.

Current behavior:

- infer a primary focus from the objective
- consume scorecards and transcript excerpts
- ask local Ollama to select a diverse, contextual set
- fall back safely to deterministic ranking

Future behavior:

- create full narrative structures
- decide cold open/hook/payoff ordering
- identify missing context/assets
- request B-roll or generated shots
- reason over long-form story arcs

### 3. Editors / tools

Current:

- clipping and exact boundaries
- vertical reframing
- captions
- local AI-video generation capability
- simple vertical assembly utilities

Future:

- pacing cuts
- silence/filler removal
- punch-ins and reaction layouts
- B-roll placement
- SFX/music/mixing
- titles/lower thirds/graphics
- long-form timeline edits

### 4. QC / critic

Current QC validates technical render properties.

Future QC should **watch the final render** and compare it with the production objective, checking:

- misleading/context-losing cuts
- bad crop/subject loss
- caption mistakes
- awkward cuts
- audio problems
- dead sections
- repeated information
- whether the hook and payoff work

## Job artifact

Every production job writes `production_manifest.json`. This is the durable handoff between the agent, UI, later editing stages, and future learning.

The manifest currently contains:

- source video
- production goal
- director strategy
- focus
- selected candidate IDs
- editorial reasons
- component scorecards
- final score
- output path
- QC result
- model/runtime notes

This manifest should remain backwards-compatible where practical as the agent grows.

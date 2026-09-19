from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ProductionRequest:
    source_video: Path
    goal: str = "Find and produce the strongest standalone moments."
    output_count: int = 5
    focus: str = "Auto"
    vertical: bool = True
    smart_reframe: bool = True
    burn_captions: bool = True
    caption_words_per_line: int = 7
    min_clip_seconds: float = 18.0
    target_clip_seconds: float = 42.0
    max_clip_seconds: float = 75.0
    force_analysis: bool = False
    output_dir: Path | None = None


@dataclass
class DirectorPick:
    candidate_id: str
    rank: int
    editorial_reason: str


@dataclass
class DirectorPlan:
    goal: str
    focus: str
    strategy: str
    picks: list[DirectorPick] = field(default_factory=list)
    used_local_ai: bool = False


@dataclass
class QCReport:
    passed: bool
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    has_audio: bool = False
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProducedClip:
    candidate_id: str
    title: str
    source_start: float
    source_end: float
    final_score: float
    scores: dict[str, float]
    editorial_reason: str
    output_path: str
    qc: QCReport


@dataclass
class ProductionResult:
    source_video: str
    output_dir: str
    manifest_path: str
    plan: DirectorPlan
    clips: list[ProducedClip]
    model_notes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

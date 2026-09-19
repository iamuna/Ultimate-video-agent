from __future__ import annotations

import json

import requests

from vidgoclip.ai import ollama_ready
from vidgoclip.models import Candidate

from .models import DirectorPick, DirectorPlan

KNOWN_FOCI = {"Balanced", "Important", "Controversial", "Interesting", "Emotional"}

_FOCUS_MARKERS = {
    "Controversial": (
        "controvers", "argument", "debate", "disagree", "fight", "heated",
        "provocative", "polarizing",
    ),
    "Important": (
        "important", "key", "critical", "meaningful", "essential", "newsworthy",
        "conclusion", "decision", "evidence",
    ),
    "Emotional": (
        "emotion", "emotional", "sad", "happy", "anger", "angry", "shocking",
        "heartbreaking", "funny", "laugh", "reaction",
    ),
    "Interesting": (
        "interesting", "surprising", "viral", "hook", "curious", "best moments",
        "entertaining", "memorable",
    ),
}


def infer_focus(goal: str, requested_focus: str = "Auto") -> str:
    if requested_focus in KNOWN_FOCI:
        return requested_focus

    lower = (goal or "").lower()
    scored = {
        focus: sum(marker in lower for marker in markers)
        for focus, markers in _FOCUS_MARKERS.items()
    }
    best = max(scored, key=scored.get)
    if scored[best] > 0:
        return best
    return "Balanced"


def _fallback_plan(
    goal: str,
    focus: str,
    candidates: list[Candidate],
    count: int,
) -> DirectorPlan:
    picks: list[DirectorPick] = []
    for rank, candidate in enumerate(candidates[:count], start=1):
        reason = candidate.reason.strip() or (
            f"Strong {focus.lower()} scorecard with a final score of "
            f"{candidate.final_score:.1f}/100."
        )
        picks.append(
            DirectorPick(
                candidate_id=candidate.id,
                rank=rank,
                editorial_reason=reason[:700],
            )
        )

    return DirectorPlan(
        goal=goal,
        focus=focus,
        strategy=(
            "Deterministic fallback: use the deduplicated ranked moments from "
            "the multimodal clipping engine, preserving context and score order."
        ),
        picks=picks,
        used_local_ai=False,
    )


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    fence = chr(96) * 3
    if cleaned.startswith(fence):
        cleaned = cleaned.strip(chr(96))
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].lstrip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object returned.")
    return json.loads(cleaned[start : end + 1])


def build_director_plan(
    *,
    goal: str,
    focus: str,
    candidates: list[Candidate],
    count: int,
    ollama_base_url: str,
    ollama_model: str,
) -> DirectorPlan:
    if not candidates:
        return DirectorPlan(
            goal=goal,
            focus=focus,
            strategy="No clip candidates were available.",
            picks=[],
            used_local_ai=False,
        )

    count = max(1, min(int(count), len(candidates)))
    fallback = _fallback_plan(goal, focus, candidates, count)
    if not ollama_ready(ollama_base_url):
        return fallback

    pool = []
    for candidate in candidates[: min(20, max(count * 3, 10))]:
        pool.append(
            {
                "id": candidate.id,
                "title": candidate.title,
                "start": round(candidate.start, 2),
                "end": round(candidate.end, 2),
                "final_score": candidate.final_score,
                "scores": candidate.scores,
                "reason": candidate.reason[:500],
                "transcript_excerpt": candidate.text[:1600],
            }
        )

    prompt = f"""
You are the producer/director of an autonomous video production agent.

Production goal:
{goal}

Editorial focus already chosen by the analysis engine: {focus}

Choose up to {count} moments from the candidate pool. The final output should:
- satisfy the production goal rather than blindly follow the numeric score;
- favor complete setup -> tension/event -> reaction/payoff when available;
- avoid near-duplicate moments about the same beat;
- preserve enough context that the clip is not misleading;
- prefer moments that stand alone for someone who did not see the source.

Do not invent events that are not in the transcript or scorecard.

Return ONLY JSON:
{{
  "strategy": "one concise explanation of the production approach",
  "picks": [
    {{"id": "c0001", "reason": "why this exact moment serves the goal"}}
  ]
}}

Candidate pool:
{json.dumps(pool, ensure_ascii=False)}
""".strip()

    try:
        response = requests.post(
            f"{ollama_base_url.rstrip('/')}/api/chat",
            json={
                "model": ollama_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.15},
            },
            timeout=360,
        )
        response.raise_for_status()
        payload = response.json()
        data = _extract_json(str((payload.get("message") or {}).get("content") or ""))
    except Exception:
        return fallback

    by_id = {candidate.id: candidate for candidate in candidates}
    selected: list[DirectorPick] = []
    seen: set[str] = set()

    for item in data.get("picks", []):
        if not isinstance(item, dict):
            continue
        candidate_id = str(item.get("id") or "")
        if candidate_id not in by_id or candidate_id in seen:
            continue
        seen.add(candidate_id)
        selected.append(
            DirectorPick(
                candidate_id=candidate_id,
                rank=len(selected) + 1,
                editorial_reason=str(item.get("reason") or "").strip()[:700]
                or by_id[candidate_id].reason[:700],
            )
        )
        if len(selected) >= count:
            break

    for fallback_pick in fallback.picks:
        if len(selected) >= count:
            break
        if fallback_pick.candidate_id not in seen:
            seen.add(fallback_pick.candidate_id)
            selected.append(
                DirectorPick(
                    candidate_id=fallback_pick.candidate_id,
                    rank=len(selected) + 1,
                    editorial_reason=fallback_pick.editorial_reason,
                )
            )

    return DirectorPlan(
        goal=goal,
        focus=focus,
        strategy=str(data.get("strategy") or fallback.strategy).strip()[:1000],
        picks=selected,
        used_local_ai=True,
    )

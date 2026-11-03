"""Convert internal exercise state to API Pydantic models."""

from __future__ import annotations

from datetime import datetime, timezone

from config.api_settings import ApiSettings
from exercises.base import ExerciseState as InternalExerciseState
from exercises.base import FeedbackItem as InternalFeedbackItem
from schemas.response import ExerciseState, FeedbackItem


SEVERITY_MAP = {
    "info": "low",
    "warning": "medium",
    "error": "high",
}


def map_feedback(item: InternalFeedbackItem) -> FeedbackItem:
    """Map internal feedback severity to API severity labels."""
    return FeedbackItem(
        code=item.code or "GENERAL",
        severity=SEVERITY_MAP.get(item.severity, item.severity),
        message=item.message,
    )


def estimate_calories(
    reps: int,
    duration_seconds: int,
    api_settings: ApiSettings | None = None,
) -> float:
    """Estimate calories from reps and elapsed time."""
    settings = api_settings or ApiSettings()
    return round(
        (reps * settings.calories_per_rep)
        + (duration_seconds / 60.0 * settings.calories_per_minute),
        1,
    )


def to_exercise_state(
    exercise_key: str,
    internal: InternalExerciseState | None,
    fps: float,
    duration_seconds: int,
    api_settings: ApiSettings | None = None,
    joint_angles: dict[str, float] | None = None,
    landmarks: list[dict] | None = None,
) -> ExerciseState:
    """Build API ExerciseState from internal dataclass."""
    if internal is None:
        return ExerciseState(
            exercise=exercise_key,
            reps=0,
            stage="IDLE",
            score=100.0,
            calories=0.0,
            feedback=[],
            angles={},
            fps=fps,
            timestamp=datetime.now(timezone.utc),
            landmarks=landmarks,
        )

    angles = dict(internal.metrics)
    angles.update(joint_angles or {})

    return ExerciseState(
        exercise=exercise_key,
        reps=internal.reps,
        stage=internal.stage.upper(),
        score=round(internal.score, 1),
        calories=estimate_calories(internal.reps, duration_seconds, api_settings),
        feedback=[map_feedback(item) for item in internal.feedback],
        angles=angles,
        fps=round(fps, 1),
        timestamp=datetime.now(timezone.utc),
        landmarks=landmarks,
    )

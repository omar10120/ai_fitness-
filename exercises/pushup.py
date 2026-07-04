"""Push-up exercise placeholder — TODO: implement elbow angle rep counting."""

from __future__ import annotations

from typing import Any

from exercises.base import BaseExercise, FeedbackItem


class PushupExercise(BaseExercise):
    """Placeholder push-up tracker. Inherits BaseExercise contract."""

    @property
    def name(self) -> str:
        return "Push-up"

    def update(self, landmarks: list[Any]) -> None:
        # TODO: Use shoulder-elbow-wrist angle for rep cycle.
        # TODO: Apply PUSHUP_UP / PUSHUP_DOWN thresholds from config.
        # TODO: Detect hip sag and elbow flare for form feedback.
        self._feedback = [
            FeedbackItem(
                message="Push-up tracking not yet implemented",
                severity="info",
                code="NOT_IMPLEMENTED",
            )
        ]

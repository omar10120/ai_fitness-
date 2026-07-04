"""Squat exercise placeholder — TODO: implement knee/hip angle rep counting."""

from __future__ import annotations

from typing import Any

from exercises.base import BaseExercise, FeedbackItem


class SquatExercise(BaseExercise):
    """Placeholder squat tracker. Inherits BaseExercise contract."""

    @property
    def name(self) -> str:
        return "Squat"

    def update(self, landmarks: list[Any]) -> None:
        # TODO: Use LEFT_HIP, LEFT_KNEE, LEFT_ANKLE for knee angle.
        # TODO: Apply SQUAT_UP / SQUAT_DOWN thresholds from config.
        # TODO: Detect knee valgus and forward lean for form feedback.
        self._feedback = [
            FeedbackItem(
                message="Squat tracking not yet implemented",
                severity="info",
                code="NOT_IMPLEMENTED",
            )
        ]

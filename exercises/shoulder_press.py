"""Shoulder press exercise placeholder — TODO: implement shoulder angle rep counting."""

from __future__ import annotations

from typing import Any

from exercises.base import BaseExercise, FeedbackItem


class ShoulderPressExercise(BaseExercise):
    """Placeholder shoulder press tracker. Inherits BaseExercise contract."""

    @property
    def name(self) -> str:
        return "Shoulder Press"

    def update(self, landmarks: list[Any]) -> None:
        # TODO: Use shoulder-elbow-wrist angle on both arms.
        # TODO: Apply SHOULDER_PRESS_UP / SHOULDER_PRESS_DOWN thresholds.
        # TODO: Detect asymmetric pressing and lower-back arch.
        self._feedback = [
            FeedbackItem(
                message="Shoulder press tracking not yet implemented",
                severity="info",
                code="NOT_IMPLEMENTED",
            )
        ]

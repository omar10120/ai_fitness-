"""Jumping jack — full-body rep counting via arm height and leg spread."""

from __future__ import annotations

from typing import Any

from config import settings
from core.geometry import Geometry
from core.landmarks import Landmark
from exercises.base import BaseExercise, ExerciseStage, FeedbackItem


class JumpingJackExercise(BaseExercise):
    """
    Counts jumping jack reps using arm elevation and ankle spread.

    Logic:
        arms down + feet together  → stage DOWN
        arms up + feet apart and previous DOWN → stage UP, reps += 1
    """

    def __init__(self) -> None:
        super().__init__()
        self._geometry = Geometry()
        self._ankle_spread: float = 0.0

    @property
    def name(self) -> str:
        return "Jumping Jack"

    def update(self, landmarks: list[Any]) -> None:
        left_wrist_y = landmarks[Landmark.LEFT_WRIST].y
        right_wrist_y = landmarks[Landmark.RIGHT_WRIST].y
        left_shoulder_y = landmarks[Landmark.LEFT_SHOULDER].y
        right_shoulder_y = landmarks[Landmark.RIGHT_SHOULDER].y

        left_ankle = (
            landmarks[Landmark.LEFT_ANKLE].x,
            landmarks[Landmark.LEFT_ANKLE].y,
        )
        right_ankle = (
            landmarks[Landmark.RIGHT_ANKLE].x,
            landmarks[Landmark.RIGHT_ANKLE].y,
        )

        self._ankle_spread = self._geometry.distance(left_ankle, right_ankle)
        self._metrics = {"ankle_spread": self._ankle_spread}

        arms_up = (
            left_wrist_y < left_shoulder_y - settings.JACK_ARM_CLEARANCE
            and right_wrist_y < right_shoulder_y - settings.JACK_ARM_CLEARANCE
        )
        arms_down = (
            left_wrist_y > left_shoulder_y + settings.JACK_ARM_CLEARANCE
            and right_wrist_y > right_shoulder_y + settings.JACK_ARM_CLEARANCE
        )
        legs_apart = self._ankle_spread > settings.JACK_LEG_SPREAD
        legs_together = self._ankle_spread < settings.JACK_LEG_TOGETHER

        previous_stage = self._stage
        self._feedback = []

        if arms_down and legs_together:
            self._stage = ExerciseStage.DOWN
        elif arms_up and legs_apart and previous_stage == ExerciseStage.DOWN:
            self._stage = ExerciseStage.UP
            self._reps += 1

        if self._stage == ExerciseStage.UP:
            if not arms_up:
                self._feedback.append(
                    FeedbackItem(
                        message="Raise both arms overhead",
                        severity="warning",
                        code="ARMS_LOW",
                    )
                )
            if not legs_apart:
                self._feedback.append(
                    FeedbackItem(
                        message="Jump wider — spread feet apart",
                        severity="warning",
                        code="LEGS_NARROW",
                    )
                )

        # TODO: Detect landing symmetry and cadence for cardio scoring.
        self._apply_feedback_score()

    def joint_angles(self) -> dict[str, float]:
        return {}

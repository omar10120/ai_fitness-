"""Lateral raise — shoulder abduction rep counting via hip-shoulder-elbow angle."""

from __future__ import annotations

from typing import Any

from config import settings
from config.exercise_config import ExerciseConfig
from core.geometry import Geometry
from core.landmarks import Landmark
from exercises.base import BaseExercise, ExerciseStage, FeedbackItem


class LateralRaiseExercise(BaseExercise):
    """
    Counts lateral raise reps on the left arm.

    Logic:
        angle < LATERAL_DOWN  → stage DOWN (arm at side)
        angle > LATERAL_UP and previous stage DOWN → stage UP, reps += 1
    """

    def __init__(self, config: ExerciseConfig | None = None) -> None:
        super().__init__(config)
        self._geometry = Geometry()
        self._shoulder_angle: float = 0.0

    @property
    def name(self) -> str:
        return "Lateral Raise"

    def update(self, landmarks: list[Any]) -> None:
        hip = (landmarks[Landmark.LEFT_HIP].x, landmarks[Landmark.LEFT_HIP].y)
        shoulder = (landmarks[Landmark.LEFT_SHOULDER].x, landmarks[Landmark.LEFT_SHOULDER].y)
        elbow = (landmarks[Landmark.LEFT_ELBOW].x, landmarks[Landmark.LEFT_ELBOW].y)

        self._shoulder_angle = self._geometry.calculate_angle(hip, shoulder, elbow)
        self._metrics = {"left_shoulder_abduction": self._shoulder_angle}

        previous_stage = self._stage
        self._feedback = []

        down_threshold = self.config.get("down", settings.LATERAL_DOWN)
        up_threshold = self.config.get("up", settings.LATERAL_UP)

        if self._shoulder_angle < down_threshold:
            self._stage = ExerciseStage.DOWN
        elif (
            self._shoulder_angle > up_threshold
            and previous_stage == ExerciseStage.DOWN
        ):
            self._stage = ExerciseStage.UP
            self._reps += 1

        up_threshold = self.config.get("up", settings.LATERAL_UP)

        if self._stage == ExerciseStage.UP and self._shoulder_angle < up_threshold:
            self._feedback.append(
                FeedbackItem(
                    message="Raise arms higher — parallel to floor",
                    severity="warning",
                    code="INSUFFICIENT_HEIGHT",
                )
            )

        wrist_y = landmarks[Landmark.LEFT_WRIST].y
        elbow_y = landmarks[Landmark.LEFT_ELBOW].y
        if wrist_y < elbow_y - 0.03:
            self._feedback.append(
                FeedbackItem(
                    message="Keep wrist level with elbow",
                    severity="warning",
                    code="WRIST_DROP",
                )
            )

        # TODO: Track both arms simultaneously for bilateral raises.
        self._apply_feedback_score()

    def joint_angles(self) -> dict[str, float]:
        return {"left_shoulder": self._shoulder_angle}

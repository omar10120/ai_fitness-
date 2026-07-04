"""Overhead tricep extension — right-arm elbow angle rep counting."""

from __future__ import annotations

from typing import Any

from config import settings
from core.geometry import Geometry
from core.landmarks import Landmark
from exercises.base import BaseExercise, ExerciseStage, FeedbackItem


class TricepExtensionExercise(BaseExercise):
    """
    Counts tricep extension reps using right-arm elbow angle.

    Logic:
        angle < TRICEP_BENT   → stage DOWN (flexed behind head)
        angle > TRICEP_EXTEND and previous stage DOWN → stage UP, reps += 1
    """

    def __init__(self) -> None:
        super().__init__()
        self._geometry = Geometry()
        self._elbow_angle: float = 180.0

    @property
    def name(self) -> str:
        return "Tricep Extension"

    def update(self, landmarks: list[Any]) -> None:
        shoulder = (
            landmarks[Landmark.RIGHT_SHOULDER].x,
            landmarks[Landmark.RIGHT_SHOULDER].y,
        )
        elbow = (landmarks[Landmark.RIGHT_ELBOW].x, landmarks[Landmark.RIGHT_ELBOW].y)
        wrist = (landmarks[Landmark.RIGHT_WRIST].x, landmarks[Landmark.RIGHT_WRIST].y)

        self._elbow_angle = self._geometry.calculate_angle(shoulder, elbow, wrist)
        self._metrics = {"right_elbow_angle": self._elbow_angle}

        previous_stage = self._stage
        self._feedback = []

        if self._elbow_angle < settings.TRICEP_BENT:
            self._stage = ExerciseStage.DOWN
        elif (
            self._elbow_angle > settings.TRICEP_EXTEND
            and previous_stage == ExerciseStage.DOWN
        ):
            self._stage = ExerciseStage.UP
            self._reps += 1

        if self._stage == ExerciseStage.DOWN and self._elbow_angle > settings.TRICEP_BENT:
            self._feedback.append(
                FeedbackItem(
                    message="Flex deeper — lower the weight behind head",
                    severity="warning",
                    code="INSUFFICIENT_FLEXION",
                )
            )

        if self._stage == ExerciseStage.UP and self._elbow_angle < settings.TRICEP_EXTEND:
            self._feedback.append(
                FeedbackItem(
                    message="Extend fully — straighten arm overhead",
                    severity="warning",
                    code="INCOMPLETE_EXTENSION",
                )
            )

        # TODO: Detect elbow flare using shoulder-elbow horizontal drift.
        self._apply_feedback_score()

    def joint_angles(self) -> dict[str, float]:
        return {"right_elbow": self._elbow_angle}

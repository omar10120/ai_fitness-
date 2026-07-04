"""Forward lunge — left-leg knee angle rep counting."""

from __future__ import annotations

from typing import Any

from config import settings
from core.geometry import Geometry
from core.landmarks import Landmark
from exercises.base import BaseExercise, ExerciseStage, FeedbackItem


class LungeExercise(BaseExercise):
    """
    Counts lunge reps using left-leg knee angle (hip-knee-ankle).

    Logic:
        angle < LUNGE_KNEE_DOWN  → stage DOWN (deep lunge)
        angle > LUNGE_KNEE_UP and previous stage DOWN → stage UP, reps += 1
    """

    def __init__(self) -> None:
        super().__init__()
        self._geometry = Geometry()
        self._knee_angle: float = 180.0

    @property
    def name(self) -> str:
        return "Lunge"

    def update(self, landmarks: list[Any]) -> None:
        hip = (landmarks[Landmark.LEFT_HIP].x, landmarks[Landmark.LEFT_HIP].y)
        knee = (landmarks[Landmark.LEFT_KNEE].x, landmarks[Landmark.LEFT_KNEE].y)
        ankle = (landmarks[Landmark.LEFT_ANKLE].x, landmarks[Landmark.LEFT_ANKLE].y)

        self._knee_angle = self._geometry.calculate_angle(hip, knee, ankle)
        self._metrics = {"left_knee_angle": self._knee_angle}

        previous_stage = self._stage
        self._feedback = []

        if self._knee_angle < settings.LUNGE_KNEE_DOWN:
            self._stage = ExerciseStage.DOWN
        elif (
            self._knee_angle > settings.LUNGE_KNEE_UP
            and previous_stage == ExerciseStage.DOWN
        ):
            self._stage = ExerciseStage.UP
            self._reps += 1

        knee_x = landmarks[Landmark.LEFT_KNEE].x
        ankle_x = landmarks[Landmark.LEFT_ANKLE].x
        if abs(knee_x - ankle_x) > settings.LUNGE_KNEE_OVER_TOE:
            self._feedback.append(
                FeedbackItem(
                    message="Keep knee over ankle — don't let it pass toes",
                    severity="error",
                    code="KNEE_OVER_TOE",
                )
            )

        hip_y = landmarks[Landmark.LEFT_HIP].y
        right_hip_y = landmarks[Landmark.RIGHT_HIP].y
        if abs(hip_y - right_hip_y) > settings.LUNGE_HIP_TILT:
            self._feedback.append(
                FeedbackItem(
                    message="Keep hips square and level",
                    severity="warning",
                    code="HIP_TILT",
                )
            )

        # TODO: Alternate left/right leg tracking per rep.
        self._apply_feedback_score()

    def joint_angles(self) -> dict[str, float]:
        return {"left_knee": self._knee_angle}

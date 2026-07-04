"""Bicep curl exercise with elbow-angle rep counting and basic form checks."""

from __future__ import annotations

from typing import Any

from config import settings
from config.exercise_config import ExerciseConfig
from core.geometry import Geometry
from core.landmarks import Landmark
from exercises.base import BaseExercise, ExerciseStage, FeedbackItem


class BicepCurlExercise(BaseExercise):
    """
    Counts bicep curl reps using left-arm elbow angle.

    Logic:
        angle > BICEP_DOWN  → stage DOWN
        angle < BICEP_UP and previous stage DOWN → stage UP, reps += 1
    """

    def __init__(self, config: ExerciseConfig | None = None) -> None:
        super().__init__(config)
        self._geometry = Geometry()
        self._current_angle: float = 180.0

    @property
    def name(self) -> str:
        return "Bicep Curl"

    def update(self, landmarks: list[Any]) -> None:
        shoulder = (landmarks[Landmark.LEFT_SHOULDER].x, landmarks[Landmark.LEFT_SHOULDER].y)
        elbow = (landmarks[Landmark.LEFT_ELBOW].x, landmarks[Landmark.LEFT_ELBOW].y)
        wrist = (landmarks[Landmark.LEFT_WRIST].x, landmarks[Landmark.LEFT_WRIST].y)

        self._current_angle = self._geometry.calculate_angle(shoulder, elbow, wrist)
        self._metrics = {"left_elbow_angle": self._current_angle}

        previous_stage = self._stage
        self._feedback = []

        down_threshold = self.config.get("down", settings.BICEP_DOWN)
        up_threshold = self.config.get("up", settings.BICEP_UP)

        if self._current_angle > down_threshold:
            self._stage = ExerciseStage.DOWN
        elif (
            self._current_angle < up_threshold
            and previous_stage == ExerciseStage.DOWN
        ):
            self._stage = ExerciseStage.UP
            self._reps += 1

        self._analyze_form(landmarks)
        self._apply_feedback_score()

    def _analyze_form(self, landmarks: list[Any]) -> None:
        """Detect incorrect form and populate structured feedback."""
        right_shoulder_y = landmarks[Landmark.RIGHT_SHOULDER].y
        left_shoulder_y = landmarks[Landmark.LEFT_SHOULDER].y

        if abs(left_shoulder_y - right_shoulder_y) > 0.05:
            self._feedback.append(
                FeedbackItem(
                    message="Keep shoulders level",
                    severity="warning",
                    code="SHOULDER_TILT",
                )
            )

        up_threshold = self.config.get("up", settings.BICEP_UP)
        down_threshold = self.config.get("down", settings.BICEP_DOWN)

        if self._stage == ExerciseStage.DOWN and self._current_angle < up_threshold:
            self._feedback.append(
                FeedbackItem(
                    message="Incomplete extension — straighten arm",
                    severity="warning",
                    code="INCOMPLETE_EXTENSION",
                )
            )

        if self._stage == ExerciseStage.UP and self._current_angle > down_threshold:
            self._feedback.append(
                FeedbackItem(
                    message="Curl higher — bring wrist closer to shoulder",
                    severity="warning",
                    code="INCOMPLETE_CURL",
                )
            )

        # TODO: Detect elbow drift (lateral movement) using wrist-elbow vector stability.
        # TODO: Support right-arm tracking based on user preference / camera mirroring.

    def joint_angles(self) -> dict[str, float]:
        return {"left_elbow": self._current_angle}

    def draw(self, frame: Any) -> None:
        """Per-exercise overlay — angle labels are handled by DrawingService."""
        # TODO: Draw elbow drift indicator and target ROM arc on frame.
        _ = frame

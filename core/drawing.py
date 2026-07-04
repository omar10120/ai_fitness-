"""Visualization layer — draws pose overlays and exercise UI. No AI inference."""

from __future__ import annotations

from typing import Any, Sequence

import cv2

from config import settings
from core.landmarks import Landmark
from core.pose import POSE_CONNECTIONS
from exercises.base import BaseExercise


class DrawingService:
    """
    Renders skeleton, landmarks, FPS, exercise info, and joint angles.

    Receives landmarks and frame. Never runs AI.
    """

    def draw(
        self,
        frame: Any,
        landmarks: list[Any] | None,
        fps: float,
        exercise: BaseExercise | None = None,
        joint_angles: dict[str, float] | None = None,
    ) -> Any:
        """
        Apply all visual overlays to the frame.

        Args:
            frame: BGR image from OpenCV.
            landmarks: Normalized pose landmarks.
            fps: Current frames per second.
            exercise: Active exercise for HUD rendering.
            joint_angles: Optional map of label → angle in degrees.

        Returns:
            Annotated frame (same object, mutated in place).
        """
        if landmarks is not None:
            self.draw_skeleton(frame, landmarks)
            self.draw_landmarks(frame, landmarks)

            if joint_angles:
                self.draw_joint_angles(frame, landmarks, joint_angles)

        if exercise is not None:
            self.draw_exercise_info(frame, exercise)
            exercise.draw(frame)

        self.draw_fps(frame, fps)
        return frame

    def draw_skeleton(self, frame: Any, landmarks: list[Any]) -> None:
        """Draw pose skeleton connections."""
        height, width, _ = frame.shape

        for start, end in POSE_CONNECTIONS:
            if start >= len(landmarks) or end >= len(landmarks):
                continue

            p1 = landmarks[start]
            p2 = landmarks[end]
            x1, y1 = int(p1.x * width), int(p1.y * height)
            x2, y2 = int(p2.x * width), int(p2.y * height)

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                settings.COLOR_SKELETON,
                settings.SKELETON_THICKNESS,
            )

    def draw_landmarks(self, frame: Any, landmarks: list[Any]) -> None:
        """Draw landmark points and optional index labels."""
        height, width, _ = frame.shape

        for index, landmark in enumerate(landmarks):
            x = int(landmark.x * width)
            y = int(landmark.y * height)

            cv2.circle(
                frame,
                (x, y),
                settings.LANDMARK_RADIUS,
                settings.COLOR_LANDMARK,
                -1,
            )
            cv2.putText(
                frame,
                str(index),
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                settings.COLOR_LANDMARK_INDEX,
                1,
            )

    def draw_fps(self, frame: Any, fps: float) -> None:
        """Draw FPS counter in the top-left corner."""
        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            settings.COLOR_FPS,
            2,
        )

    def draw_exercise_info(self, frame: Any, exercise: BaseExercise) -> None:
        """Draw exercise name, reps, stage, score, and feedback."""
        lines = [
            f"Exercise: {exercise.name}",
            f"Reps: {exercise.reps}",
            f"Stage: {exercise.stage}",
            f"Score: {exercise.score:.0f}%",
        ]

        y_offset = 70
        for line in lines:
            cv2.putText(
                frame,
                line,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                settings.COLOR_EXERCISE_INFO,
                2,
            )
            y_offset += 30

        for item in exercise.feedback:
            color = settings.COLOR_FEEDBACK_OK
            if item.severity == "warning":
                color = settings.COLOR_FEEDBACK_WARN
            elif item.severity == "error":
                color = settings.COLOR_FEEDBACK_ERROR

            cv2.putText(
                frame,
                item.message,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )
            y_offset += 25

    def draw_joint_angles(
        self,
        frame: Any,
        landmarks: list[Any],
        joint_angles: dict[str, float],
    ) -> None:
        """
        Draw angle labels near the corresponding joints.

        Args:
            frame: BGR image.
            landmarks: Pose landmarks.
            joint_angles: Map of label → angle. Labels may include landmark hints
                such as ``left_elbow`` to position text near the joint.
        """
        height, width, _ = frame.shape
        landmark_positions = {
            "left_elbow": Landmark.LEFT_ELBOW,
            "right_elbow": Landmark.RIGHT_ELBOW,
            "left_knee": Landmark.LEFT_KNEE,
            "right_knee": Landmark.RIGHT_KNEE,
            "left_shoulder": Landmark.LEFT_SHOULDER,
            "right_shoulder": Landmark.RIGHT_SHOULDER,
        }

        for label, angle in joint_angles.items():
            landmark_key = label.lower().replace(" ", "_")
            landmark_index = landmark_positions.get(landmark_key)

            if landmark_index is None or landmark_index >= len(landmarks):
                continue

            lm = landmarks[landmark_index]
            x = int(lm.x * width) + 20
            y = int(lm.y * height)

            cv2.putText(
                frame,
                f"{int(angle)}°",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                settings.COLOR_ANGLE,
                2,
            )

    @staticmethod
    def landmark_to_point(landmark: Any) -> tuple[float, float]:
        """Convert a normalized landmark to a 2D point."""
        return (landmark.x, landmark.y)

    def get_landmark_points(
        self,
        landmarks: Sequence[Any],
        indices: Sequence[Landmark],
    ) -> list[tuple[float, float]]:
        """Extract 2D points for the given landmark indices."""
        return [self.landmark_to_point(landmarks[index]) for index in indices]

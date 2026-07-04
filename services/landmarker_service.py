"""Singleton MediaPipe landmarker — loaded once, reused across sessions."""

from __future__ import annotations

import logging
import threading
from typing import Any

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config.settings import Settings

logger = logging.getLogger(__name__)


class LandmarkerService:
    """
    Thread-safe shared Pose Landmarker instance.

    Keeps MediaPipe initialized once for performance (~30 FPS target).
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._landmarker: vision.PoseLandmarker | None = None
        self._lock = threading.Lock()
        self._initialized = False

    def initialize(self) -> None:
        """Load the pose model once at application startup."""
        if self._initialized:
            return

        if not self._settings.model_path.exists():
            raise FileNotFoundError(
                f"Pose model not found at {self._settings.model_path}"
            )

        base_options = python.BaseOptions(
            model_asset_path=str(self._settings.model_path),
        )
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=self._settings.num_poses,
            min_pose_detection_confidence=self._settings.min_pose_detection_confidence,
            min_pose_presence_confidence=self._settings.min_pose_presence_confidence,
            min_tracking_confidence=self._settings.min_tracking_confidence,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        self._initialized = True
        logger.info("Shared landmarker initialized from %s", self._settings.model_path)

    def detect(self, frame: Any, timestamp_ms: int) -> list[Any] | None:
        """
        Run pose detection on a BGR frame.

        Args:
            frame: OpenCV BGR image.
            timestamp_ms: Monotonic video timestamp for VIDEO mode.

        Returns:
            Normalized landmarks for the first detected pose, or ``None``.
        """
        if self._landmarker is None:
            raise RuntimeError("LandmarkerService is not initialized")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        with self._lock:
            result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.pose_landmarks:
            return result.pose_landmarks[0]
        return None

    def release(self) -> None:
        """Release landmarker resources on shutdown."""
        with self._lock:
            self._landmarker = None
            self._initialized = False
        logger.info("Shared landmarker released")

    @property
    def is_initialized(self) -> bool:
        return self._initialized

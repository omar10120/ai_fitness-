"""MediaPipe Pose Landmarker detector — inference only, no drawing."""

from __future__ import annotations

import logging
from typing import Any

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config.settings import Settings
from utils.camera import Camera

logger = logging.getLogger(__name__)


class PoseDetector:
    """
    Runs MediaPipe Tasks Pose Landmarker on webcam frames.

    Responsibilities:
        - Open webcam
        - Load pose model
        - Return landmarks and original frame
        - Never draw anything
    """

    def __init__(self, camera: Camera, settings: Settings | None = None) -> None:
        self._camera = camera
        self._settings = settings or Settings()
        self._landmarker: vision.PoseLandmarker | None = None
        self._timestamp_ms = 0

    def start(self) -> bool:
        """
        Initialize the camera and load the pose landmarker model.

        Returns:
            True when both camera and model are ready.
        """
        if not self._camera.start():
            return False

        if not self._settings.model_path.exists():
            logger.error("Pose model not found at %s", self._settings.model_path)
            return False

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
        logger.info("Pose landmarker loaded from %s", self._settings.model_path)
        return True

    def read(self) -> tuple[bool, Any, list[Any] | None]:
        """
        Capture a frame and run pose detection.

        Returns:
            ``(success, frame, landmarks)`` where landmarks is a list of
            normalized landmark objects, or ``None`` when no pose is detected.
        """
        if self._landmarker is None:
            return False, None, None

        success, frame = self._camera.read()
        if not success or frame is None:
            return False, None, None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect_for_video(mp_image, self._timestamp_ms)
        self._timestamp_ms += self._settings.frame_timestamp_ms

        landmarks = None
        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

        return True, frame, landmarks

    def release(self) -> None:
        """Release camera and landmarker resources."""
        self._camera.release()
        self._landmarker = None
        logger.info("Pose detector released")

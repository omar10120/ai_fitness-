"""Webcam capture wrapper."""

from __future__ import annotations

import logging
from typing import Any

import cv2

from config.settings import Settings

logger = logging.getLogger(__name__)


class Camera:
    """Thin wrapper around OpenCV VideoCapture."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._capture: cv2.VideoCapture | None = None

    def start(self) -> bool:
        """
        Open the webcam and apply resolution settings.

        Returns:
            True if the camera opened successfully.
        """
        self._capture = cv2.VideoCapture(self._settings.camera_index)
        if not self._capture.isOpened():
            logger.error("Failed to open camera index %s", self._settings.camera_index)
            return False

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._settings.camera_width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._settings.camera_height)
        logger.info("Camera started on index %s", self._settings.camera_index)
        return True

    def read(self) -> tuple[bool, Any]:
        """
        Read the next frame.

        Returns:
            ``(success, frame)`` tuple compatible with OpenCV.
        """
        if self._capture is None:
            return False, None
        return self._capture.read()

    def release(self) -> None:
        """Release the camera resource."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            logger.info("Camera released")

    @property
    def is_opened(self) -> bool:
        """Whether the camera is currently open."""
        return self._capture is not None and self._capture.isOpened()

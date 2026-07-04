"""
AI Fitness Coach — application entry point.

Pipeline: camera → detector → exercise_manager → drawing → display
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import cv2

# Ensure package root is on sys.path when run directly.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config.settings import Settings
from core.detector import PoseDetector
from core.drawing import DrawingService
from services.exercise_manager import ExerciseManager
from utils.camera import Camera
from utils.fps import FpsCounter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Keyboard shortcuts for exercise switching (orchestration only).
EXERCISE_KEYS = {
    ord("1"): "bicep_curl",
    ord("2"): "squat",
    ord("3"): "pushup",
    ord("4"): "shoulder_press",
}


def main() -> None:
    """Run the fitness coach application loop."""
    settings = Settings()
    camera = Camera(settings)
    detector = PoseDetector(camera, settings)
    exercise_manager = ExerciseManager()
    drawing = DrawingService()
    fps_counter = FpsCounter()

    if not detector.start():
        logger.error("Failed to start pose detector. Exiting.")
        return

    logger.info("Press 1-4 to switch exercises. ESC to quit.")
    logger.info("Available exercises: %s", exercise_manager.available)

    try:
        while True:
            success, frame, landmarks = detector.read()
            if not success or frame is None:
                break

            exercise_manager.update(landmarks)

            fps = fps_counter.update()
            active = exercise_manager.active
            joint_angles = exercise_manager.joint_angles()

            drawing.draw(frame, landmarks, fps, active, joint_angles)

            cv2.imshow(settings.window_title, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            if key in EXERCISE_KEYS:
                exercise_manager.select(EXERCISE_KEYS[key])
            if key == ord("r"):
                exercise_manager.reset()

    finally:
        detector.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

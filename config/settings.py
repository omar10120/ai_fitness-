"""Application-wide configuration and exercise thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "pose_landmarker_full.task"

# Camera
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Pose detection
NUM_POSES = 1
MIN_POSE_DETECTION_CONFIDENCE = 0.5
MIN_POSE_PRESENCE_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
FRAME_TIMESTAMP_MS = 33

# Display
WINDOW_TITLE = "AI Fitness Coach"
FPS_TARGET = 30

# Bicep curl thresholds (degrees)
BICEP_UP = 40
BICEP_DOWN = 160

# Squat thresholds — TODO: tune during calibration
SQUAT_UP = 160
SQUAT_DOWN = 90

# Push-up thresholds — TODO: tune during calibration
PUSHUP_UP = 160
PUSHUP_DOWN = 90

# Shoulder press thresholds — TODO: tune during calibration
SHOULDER_PRESS_UP = 160
SHOULDER_PRESS_DOWN = 90

# Drawing colors (BGR)
COLOR_SKELETON = (255, 0, 0)
COLOR_LANDMARK = (0, 255, 0)
COLOR_LANDMARK_INDEX = (255, 255, 255)
COLOR_ANGLE = (0, 255, 255)
COLOR_FPS = (0, 255, 0)
COLOR_EXERCISE_INFO = (255, 255, 255)
COLOR_FEEDBACK_OK = (0, 255, 0)
COLOR_FEEDBACK_WARN = (0, 165, 255)
COLOR_FEEDBACK_ERROR = (0, 0, 255)

SKELETON_THICKNESS = 2
LANDMARK_RADIUS = 5


@dataclass(frozen=True)
class Settings:
    """Runtime settings container for dependency injection."""

    model_path: Path = MODEL_PATH
    camera_index: int = CAMERA_INDEX
    camera_width: int = CAMERA_WIDTH
    camera_height: int = CAMERA_HEIGHT
    num_poses: int = NUM_POSES
    min_pose_detection_confidence: float = MIN_POSE_DETECTION_CONFIDENCE
    min_pose_presence_confidence: float = MIN_POSE_PRESENCE_CONFIDENCE
    min_tracking_confidence: float = MIN_TRACKING_CONFIDENCE
    frame_timestamp_ms: int = FRAME_TIMESTAMP_MS
    window_title: str = WINDOW_TITLE
    fps_target: int = FPS_TARGET

"""Pose skeleton topology for MediaPipe 33-landmark model."""

from __future__ import annotations

from core.landmarks import Landmark

# Pairs of landmark indices that form the pose skeleton.
POSE_CONNECTIONS: list[tuple[Landmark, Landmark]] = [
    (Landmark.NOSE, Landmark.LEFT_EYE_INNER),
    (Landmark.LEFT_EYE_INNER, Landmark.LEFT_EYE),
    (Landmark.LEFT_EYE, Landmark.LEFT_EYE_OUTER),
    (Landmark.LEFT_EYE_OUTER, Landmark.LEFT_EAR),
    (Landmark.NOSE, Landmark.RIGHT_EYE_INNER),
    (Landmark.RIGHT_EYE_INNER, Landmark.RIGHT_EYE),
    (Landmark.RIGHT_EYE, Landmark.RIGHT_EYE_OUTER),
    (Landmark.RIGHT_EYE_OUTER, Landmark.RIGHT_EAR),
    (Landmark.MOUTH_LEFT, Landmark.MOUTH_RIGHT),
    (Landmark.LEFT_SHOULDER, Landmark.RIGHT_SHOULDER),
    (Landmark.LEFT_SHOULDER, Landmark.LEFT_ELBOW),
    (Landmark.LEFT_ELBOW, Landmark.LEFT_WRIST),
    (Landmark.RIGHT_SHOULDER, Landmark.RIGHT_ELBOW),
    (Landmark.RIGHT_ELBOW, Landmark.RIGHT_WRIST),
    (Landmark.LEFT_SHOULDER, Landmark.LEFT_HIP),
    (Landmark.RIGHT_SHOULDER, Landmark.RIGHT_HIP),
    (Landmark.LEFT_HIP, Landmark.RIGHT_HIP),
    (Landmark.LEFT_HIP, Landmark.LEFT_KNEE),
    (Landmark.LEFT_KNEE, Landmark.LEFT_ANKLE),
    (Landmark.LEFT_ANKLE, Landmark.LEFT_HEEL),
    (Landmark.LEFT_HEEL, Landmark.LEFT_FOOT_INDEX),
    (Landmark.RIGHT_HIP, Landmark.RIGHT_KNEE),
    (Landmark.RIGHT_KNEE, Landmark.RIGHT_ANKLE),
    (Landmark.RIGHT_ANKLE, Landmark.RIGHT_HEEL),
    (Landmark.RIGHT_HEEL, Landmark.RIGHT_FOOT_INDEX),
]

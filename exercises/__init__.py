"""Exercise registry — add new exercises here without modifying the manager."""

from __future__ import annotations

from exercises.base import BaseExercise
from exercises.bicep_curl import BicepCurlExercise
from exercises.pushup import PushupExercise
from exercises.shoulder_press import ShoulderPressExercise
from exercises.squat import SquatExercise

# Registry key → factory callable (instantiates a fresh exercise instance).
EXERCISE_REGISTRY: dict[str, type[BaseExercise]] = {
    "bicep_curl": BicepCurlExercise,
    "squat": SquatExercise,
    "pushup": PushupExercise,
    "shoulder_press": ShoulderPressExercise,
}

DEFAULT_EXERCISE = "bicep_curl"

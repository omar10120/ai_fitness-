"""Exercise registry — add new exercises here without modifying the manager."""

from __future__ import annotations

from exercises.base import BaseExercise
from exercises.bicep_curl import BicepCurlExercise
from exercises.jumping_jack import JumpingJackExercise
from exercises.lateral_raise import LateralRaiseExercise
from exercises.lunge import LungeExercise
from exercises.pushup import PushupExercise
from exercises.shoulder_press import ShoulderPressExercise
from exercises.squat import SquatExercise
from exercises.tricep_extension import TricepExtensionExercise

# Registry key → factory callable (instantiates a fresh exercise instance).
EXERCISE_REGISTRY: dict[str, type[BaseExercise]] = {
    "bicep_curl": BicepCurlExercise,
    "squat": SquatExercise,
    "pushup": PushupExercise,
    "shoulder_press": ShoulderPressExercise,
    "lateral_raise": LateralRaiseExercise,
    "tricep_extension": TricepExtensionExercise,
    "lunge": LungeExercise,
    "jumping_jack": JumpingJackExercise,
}

DEFAULT_EXERCISE = "bicep_curl"

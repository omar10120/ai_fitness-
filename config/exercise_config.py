"""Runtime exercise configuration — loaded from Laravel or local defaults."""

from __future__ import annotations

from dataclasses import dataclass, field

from config import settings


@dataclass
class ExerciseConfig:
    """
    Per-exercise thresholds consumed by exercise classes.

    Laravel payload example::

        {"exercise": "bicep_curl", "angles": {"up": 40, "down": 160}, "side": "left"}
    """

    exercise: str = ""
    angles: dict[str, float] = field(default_factory=dict)
    side: str = "left"
    thresholds: dict[str, float] = field(default_factory=dict)

    def get(self, key: str, default: float) -> float:
        """Return angle/threshold value with fallback to application defaults."""
        if key in self.angles:
            return float(self.angles[key])
        if key in self.thresholds:
            return float(self.thresholds[key])
        return default

    @classmethod
    def from_laravel_payload(cls, payload: dict) -> ExerciseConfig:
        """Build config from Laravel JSON response."""
        angles = {k: float(v) for k, v in payload.get("angles", {}).items()}
        thresholds = {k: float(v) for k, v in payload.get("thresholds", {}).items()}
        return cls(
            exercise=str(payload.get("exercise", "")),
            angles=angles,
            side=str(payload.get("side", "left")),
            thresholds=thresholds,
        )

    @classmethod
    def defaults_for(cls, exercise: str) -> ExerciseConfig:
        """Fallback defaults from local settings when Laravel is unavailable."""
        angle_defaults: dict[str, dict[str, float]] = {
            "bicep_curl": {"up": settings.BICEP_UP, "down": settings.BICEP_DOWN},
            "squat": {"up": settings.SQUAT_UP, "down": settings.SQUAT_DOWN},
            "pushup": {"up": settings.PUSHUP_UP, "down": settings.PUSHUP_DOWN},
            "shoulder_press": {
                "up": settings.SHOULDER_PRESS_UP,
                "down": settings.SHOULDER_PRESS_DOWN,
            },
            "lateral_raise": {"up": settings.LATERAL_UP, "down": settings.LATERAL_DOWN},
            "tricep_extension": {
                "up": settings.TRICEP_EXTEND,
                "down": settings.TRICEP_BENT,
            },
            "lunge": {
                "up": settings.LUNGE_KNEE_UP,
                "down": settings.LUNGE_KNEE_DOWN,
            },
            "jumping_jack": {},
        }
        threshold_defaults: dict[str, dict[str, float]] = {
            "lunge": {
                "knee_over_toe": settings.LUNGE_KNEE_OVER_TOE,
                "hip_tilt": settings.LUNGE_HIP_TILT,
            },
            "jumping_jack": {
                "arm_clearance": settings.JACK_ARM_CLEARANCE,
                "leg_spread": settings.JACK_LEG_SPREAD,
                "leg_together": settings.JACK_LEG_TOGETHER,
            },
        }
        return cls(
            exercise=exercise,
            angles=angle_defaults.get(exercise, {}),
            side="left",
            thresholds=threshold_defaults.get(exercise, {}),
        )

"""Exercise selection and lifecycle management."""

from __future__ import annotations

import logging
from typing import Any

from config.exercise_config import ExerciseConfig
from exercises import DEFAULT_EXERCISE, EXERCISE_REGISTRY
from exercises.base import BaseExercise, ExerciseState

logger = logging.getLogger(__name__)


class ExerciseManager:
    """
    Registers, selects, and drives the active exercise.

    Supports dynamic exercise switching without modifying existing exercise code.
 
    Example::

        manager.select("bicep_curl")
    """

    def __init__(self) -> None:
        self._registry: dict[str, type[BaseExercise]] = dict(EXERCISE_REGISTRY)
        self._active: BaseExercise | None = None
        self._active_key: str | None = None

        if DEFAULT_EXERCISE in self._registry:
            self.select(DEFAULT_EXERCISE)

    def register(self, key: str, exercise_cls: type[BaseExercise]) -> None:
        """
        Register a new exercise type.

        Args:
            key: Unique slug (e.g. ``"bicep_curl"``).
            exercise_cls: Concrete exercise class inheriting BaseExercise.
        """
        self._registry[key] = exercise_cls
        logger.info("Registered exercise: %s", key)

    def select(
        self,
        key: str,
        config: ExerciseConfig | None = None,
    ) -> BaseExercise:
        """
        Activate an exercise by registry key.

        Args:
            key: Exercise slug.
            config: Optional runtime thresholds from Laravel.

        Returns:
            The newly active exercise instance.

        Raises:
            KeyError: If the key is not registered.
        """
        if key not in self._registry:
            raise KeyError(f"Exercise '{key}' is not registered")

        exercise_config = config or ExerciseConfig.defaults_for(key)
        self._active = self._registry[key](config=exercise_config)
        self._active_key = key
        logger.info("Selected exercise: %s", key)
        return self._active

    def update(self, landmarks: list[Any] | None) -> None:
        """Forward landmarks to the active exercise."""
        if self._active is None or landmarks is None:
            return
        self._active.update(landmarks)

    def draw(self, frame: Any) -> None:
        """Delegate per-exercise drawing to the active exercise."""
        if self._active is not None:
            self._active.draw(frame)

    def reset(self) -> None:
        """Reset the active exercise state."""
        if self._active is not None:
            self._active.reset()

    @property
    def active(self) -> BaseExercise | None:
        """Currently active exercise instance."""
        return self._active

    @property
    def active_key(self) -> str | None:
        """Registry key of the active exercise."""
        return self._active_key

    @property
    def available(self) -> list[str]:
        """List of registered exercise keys."""
        return list(self._registry.keys())

    def get_state(self) -> ExerciseState | None:
        """
        Export active exercise state for API / mobile clients.

        TODO: Expose via FastAPI endpoint for Laravel backend.
        """
        if self._active is None:
            return None
        return self._active.to_state()

    def joint_angles(self) -> dict[str, float]:
        """Return joint angles from the active exercise."""
        if self._active is None:
            return {}
        return self._active.joint_angles()

"""Abstract base class for all exercises."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExerciseStage(str, Enum):
    """Common rep-cycle stages shared across exercises."""

    IDLE = "idle"
    DOWN = "down"
    UP = "up"


@dataclass
class FeedbackItem:
    """
    Structured coaching feedback for REST API / Flutter clients.

    TODO: Serialize to JSON schema for Laravel backend integration.
    """

    message: str
    severity: str = "info"  # info | warning | error
    code: str = ""


@dataclass
class ExerciseState:
    """
    Serializable exercise snapshot.

    TODO: Persist to workout history / session storage.
    """

    name: str
    reps: int
    stage: str
    score: float
    feedback: list[FeedbackItem] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)


class BaseExercise(ABC):
    """
    Abstract exercise contract.

    Every exercise must implement rep counting, form analysis, and optional
    per-exercise drawing without modifying shared infrastructure.
    """

    def __init__(self) -> None:
        self._reps: int = 0
        self._stage: ExerciseStage = ExerciseStage.IDLE
        self._feedback: list[FeedbackItem] = []
        self._score: float = 100.0
        self._metrics: dict[str, float] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable exercise name."""

    @property
    def reps(self) -> int:
        """Completed repetition count."""
        return self._reps

    @property
    def stage(self) -> str:
        """Current movement stage."""
        return self._stage.value

    @property
    def feedback(self) -> list[FeedbackItem]:
        """Structured form feedback for the current frame."""
        return self._feedback

    @property
    def score(self) -> float:
        """Form quality score (0–100)."""
        return self._score

    @property
    def metrics(self) -> dict[str, float]:
        """Exercise-specific numeric metrics (angles, depths, etc.)."""
        return self._metrics

    def to_state(self) -> ExerciseState:
        """
        Export current exercise state for API consumers.

        TODO: Add JWT-authenticated session context when REST layer is added.
        """
        return ExerciseState(
            name=self.name,
            reps=self._reps,
            stage=self._stage.value,
            score=self._score,
            feedback=list(self._feedback),
            metrics=dict(self._metrics),
        )

    @abstractmethod
    def update(self, landmarks: list[Any]) -> None:
        """Process landmarks and update reps, stage, feedback, and score."""

    def reset(self) -> None:
        """Reset rep counter and movement state."""
        self._reps = 0
        self._stage = ExerciseStage.IDLE
        self._feedback = []
        self._score = 100.0
        self._metrics = {}

    def draw(self, frame: Any) -> None:
        """
        Optional per-exercise overlay drawing.

        Override in subclasses when custom visualization is needed.
        """
        # TODO: Voice coaching cues triggered from draw/update hooks.

    def joint_angles(self) -> dict[str, float]:
        """Return labeled joint angles for the drawing layer."""
        return {}

    def _apply_feedback_score(self) -> None:
        """Derive form score from active feedback severity levels."""
        penalty = 0
        for item in self._feedback:
            if item.severity == "warning":
                penalty += 10
            elif item.severity == "error":
                penalty += 25
        self._score = max(0.0, 100.0 - penalty)

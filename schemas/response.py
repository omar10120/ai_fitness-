"""Pydantic response models for the AI service API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackItem(BaseModel):
    code: str
    severity: str
    message: str


class ExerciseState(BaseModel):
    exercise: str
    reps: int
    stage: str
    score: float
    calories: float
    feedback: list[FeedbackItem]
    angles: dict[str, float]
    fps: float
    timestamp: datetime


class WorkoutStartResponse(BaseModel):
    session_id: str


class WorkoutStopResponse(BaseModel):
    duration: int
    reps: int
    score: float
    calories: float


class HealthResponse(BaseModel):
    status: str = "ok"


class ExerciseConfigResponse(BaseModel):
    exercise: str
    angles: dict[str, float]
    side: str = "left"
    thresholds: dict[str, float] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str

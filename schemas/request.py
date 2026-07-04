"""Pydantic request models for the AI service API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WorkoutStartRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    exercise: str = Field(..., min_length=1)
    camera: str = Field(default="front", pattern="^(front|back)$")


class WorkoutStopRequest(BaseModel):
    session_id: str = Field(..., min_length=1)

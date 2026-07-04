"""REST API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_config_service,
    get_workout_service,
    verify_bearer_token,
)
from schemas.request import WorkoutStartRequest, WorkoutStopRequest
from schemas.response import (
    ErrorResponse,
    ExerciseConfigResponse,
    ExerciseState,
    HealthResponse,
    WorkoutStartResponse,
    WorkoutStopResponse,
)
from services.config_service import ConfigService
from services.workout_service import WorkoutService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Service health probe for Laravel and load balancers."""
    return HealthResponse(status="ok")


@router.post(
    "/workout/start",
    response_model=WorkoutStartResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["workout"],
)
async def start_workout(
    payload: WorkoutStartRequest,
    _: str = Depends(verify_bearer_token),
    workout_service: WorkoutService = Depends(get_workout_service),
) -> WorkoutStartResponse:
    """Start a live AI workout session."""
    try:
        return await workout_service.start_workout(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Failed to start workout")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/workout/stop",
    response_model=WorkoutStopResponse,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["workout"],
)
async def stop_workout(
    payload: WorkoutStopRequest,
    _: str = Depends(verify_bearer_token),
    workout_service: WorkoutService = Depends(get_workout_service),
) -> WorkoutStopResponse:
    """Stop a workout session and return summary metrics."""
    try:
        return await workout_service.stop_workout(payload.session_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/workout/state/{session_id}",
    response_model=ExerciseState,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["workout"],
)
async def get_workout_state(
    session_id: str,
    _: str = Depends(verify_bearer_token),
    workout_service: WorkoutService = Depends(get_workout_service),
) -> ExerciseState:
    """Poll current exercise state for a session."""
    try:
        return await workout_service.get_state(session_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/laravel/exercise-config/{exercise}",
    response_model=ExerciseConfigResponse,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["config"],
)
async def get_exercise_config(
    exercise: str,
    _: str = Depends(verify_bearer_token),
    config_service: ConfigService = Depends(get_config_service),
) -> ExerciseConfigResponse:
    """
    Proxy/fallback endpoint for exercise configuration.

    Attempts Laravel first, falls back to local defaults.
    """
    try:
        return await config_service.get_config_response(exercise)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

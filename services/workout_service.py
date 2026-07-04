"""Workout orchestration — bridges API layer to session and config services."""

from __future__ import annotations

import logging

from config.api_settings import ApiSettings
from exercises import EXERCISE_REGISTRY
from schemas.request import WorkoutStartRequest
from schemas.response import ExerciseState, WorkoutStartResponse, WorkoutStopResponse
from services.config_service import ConfigService
from services.session_service import SessionNotFoundError, SessionService

logger = logging.getLogger(__name__)


class WorkoutService:
    """High-level workout operations consumed by API routes."""

    def __init__(
        self,
        session_service: SessionService,
        config_service: ConfigService,
        api_settings: ApiSettings | None = None,
    ) -> None:
        self._sessions = session_service
        self._config = config_service
        self._api_settings = api_settings or ApiSettings()

    async def start_workout(self, request: WorkoutStartRequest) -> WorkoutStartResponse:
        """Start a workout session for a user."""
        if request.exercise not in EXERCISE_REGISTRY:
            raise ValueError(f"Unknown exercise: {request.exercise}")

        exercise_config = await self._config.fetch_exercise_config(request.exercise)
        session = await self._sessions.create(
            user_id=request.user_id,
            exercise=request.exercise,
            camera=request.camera,
            exercise_config=exercise_config,
        )

        logger.info(
            "Workout started user=%s exercise=%s session=%s",
            request.user_id,
            request.exercise,
            session.session_id,
        )
        return WorkoutStartResponse(session_id=str(session.session_id))

    async def stop_workout(self, session_id: str) -> WorkoutStopResponse:
        """Stop an active workout and return summary metrics."""
        try:
            return await self._sessions.stop(session_id)
        except SessionNotFoundError as exc:
            raise LookupError(str(exc)) from exc

    async def get_state(self, session_id: str) -> ExerciseState:
        """Return current exercise state for polling clients."""
        try:
            session = await self._sessions.get(session_id)
        except SessionNotFoundError as exc:
            raise LookupError(str(exc)) from exc
        return await session.get_state()

    async def reset_workout(self, session_id: str) -> None:
        """Reset reps for an active session."""
        session = await self._sessions.get(session_id)
        await session.reset()

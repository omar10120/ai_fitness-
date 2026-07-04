"""In-memory session registry — supports multiple concurrent users."""

from __future__ import annotations

import asyncio
import logging
from uuid import uuid4

from config.api_settings import ApiSettings
from config.exercise_config import ExerciseConfig
from config.settings import Settings
from exercises import EXERCISE_REGISTRY
from models.workout_session import WorkoutSession
from services.exercise_manager import ExerciseManager
from services.landmarker_service import LandmarkerService

logger = logging.getLogger(__name__)


class SessionNotFoundError(LookupError):
    """Raised when a session ID does not exist."""


class SessionService:
    """Creates, tracks, and removes workout sessions."""

    def __init__(
        self,
        landmarker: LandmarkerService,
        settings: Settings | None = None,
        api_settings: ApiSettings | None = None,
    ) -> None:
        self._landmarker = landmarker
        self._settings = settings or Settings()
        self._api_settings = api_settings or ApiSettings()
        self._sessions: dict[str, WorkoutSession] = {}
        self._lock = asyncio.Lock()

    async def create(
        self,
        user_id: int,
        exercise: str,
        camera: str,
        exercise_config: ExerciseConfig,
    ) -> WorkoutSession:
        """Create and start a new workout session."""
        if exercise not in EXERCISE_REGISTRY:
            raise ValueError(f"Unknown exercise: {exercise}")

        session_id = uuid4()
        session = WorkoutSession(
            session_id=session_id,
            user_id=user_id,
            exercise_key=exercise,
            camera=camera,
            exercise_manager=ExerciseManager(),
            landmarker=self._landmarker,
            exercise_config=exercise_config,
            settings=self._settings,
            api_settings=self._api_settings,
        )

        await session.start()

        async with self._lock:
            self._sessions[str(session_id)] = session

        return session

    async def get(self, session_id: str) -> WorkoutSession:
        """Return an active session by ID."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise SessionNotFoundError(f"Session not found: {session_id}")
            return session

    async def stop(self, session_id: str):
        """Stop and remove a session, returning summary data."""
        session = await self.get(session_id)
        summary = await session.stop()

        async with self._lock:
            self._sessions.pop(session_id, None)

        return summary

    async def shutdown_all(self) -> None:
        """Stop all active sessions on application shutdown."""
        async with self._lock:
            session_ids = list(self._sessions.keys())

        for session_id in session_ids:
            try:
                await self.stop(session_id)
            except SessionNotFoundError:
                continue

        logger.info("All workout sessions shut down")

    async def count(self) -> int:
        async with self._lock:
            return len(self._sessions)

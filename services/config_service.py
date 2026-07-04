"""Fetch exercise configuration from Laravel with local fallback."""

from __future__ import annotations

import logging

import httpx

from config.api_settings import ApiSettings
from config.exercise_config import ExerciseConfig
from exercises import EXERCISE_REGISTRY
from schemas.response import ExerciseConfigResponse

logger = logging.getLogger(__name__)


class ConfigService:
    """Loads exercise thresholds from Laravel or local defaults."""

    def __init__(self, api_settings: ApiSettings | None = None) -> None:
        self._settings = api_settings or ApiSettings()

    async def fetch_exercise_config(self, exercise: str) -> ExerciseConfig:
        """
        Fetch config from Laravel. Falls back to local defaults on failure.

        TODO: Cache configs with TTL when Laravel endpoint is stable.
        """
        if exercise not in EXERCISE_REGISTRY:
            raise KeyError(f"Unknown exercise: {exercise}")

        url = (
            f"{self._settings.laravel_base_url.rstrip('/')}"
            f"{self._settings.laravel_config_path}/{exercise}"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self._settings.request_timeout_seconds
            ) as client:
                headers = {}
                if self._settings.service_token:
                    headers["Authorization"] = f"Bearer {self._settings.service_token}"

                response = await client.get(url, headers=headers)
                response.raise_for_status()
                payload = response.json()
                logger.info("Loaded exercise config from Laravel for %s", exercise)
                return ExerciseConfig.from_laravel_payload(payload)
        except Exception as exc:
            logger.warning(
                "Laravel config unavailable for %s (%s). Using local defaults.",
                exercise,
                exc,
            )
            return ExerciseConfig.defaults_for(exercise)

    def get_local_config(self, exercise: str) -> ExerciseConfigResponse:
        """Return local default config (used by proxy endpoint)."""
        if exercise not in EXERCISE_REGISTRY:
            raise KeyError(f"Unknown exercise: {exercise}")

        config = ExerciseConfig.defaults_for(exercise)
        return ExerciseConfigResponse(
            exercise=exercise,
            angles=config.angles,
            side=config.side,
            thresholds=config.thresholds,
        )

    async def get_config_response(self, exercise: str) -> ExerciseConfigResponse:
        """Return Laravel config or local fallback as API response."""
        config = await self.fetch_exercise_config(exercise)
        return ExerciseConfigResponse(
            exercise=config.exercise or exercise,
            angles=config.angles,
            side=config.side,
            thresholds=config.thresholds,
        )

"""FastAPI service and Laravel integration settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    """Environment-driven API configuration."""

    host: str = os.getenv("AI_HOST", "0.0.0.0")
    port: int = int(os.getenv("AI_PORT", "8000"))
    laravel_base_url: str = os.getenv("LARAVEL_BASE_URL", "http://localhost:8000")
    laravel_config_path: str = os.getenv(
        "LARAVEL_CONFIG_PATH", "/api/exercise-config"
    )
    service_token: str = os.getenv("AI_SERVICE_TOKEN", "")
    auth_validation_enabled: bool = os.getenv("AI_AUTH_VALIDATION", "false").lower() == "true"
    auth_validation_url: str = os.getenv(
        "AI_AUTH_VALIDATION_URL", "http://localhost:8000/api/ai/validate-token"
    )
    calories_per_rep: float = float(os.getenv("AI_CALORIES_PER_REP", "3.0"))
    calories_per_minute: float = float(os.getenv("AI_CALORIES_PER_MINUTE", "5.0"))
    websocket_target_fps: int = int(os.getenv("AI_WEBSOCKET_FPS", "30"))
    request_timeout_seconds: float = float(os.getenv("AI_HTTP_TIMEOUT", "10.0"))

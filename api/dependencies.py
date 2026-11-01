"""FastAPI dependency injection helpers."""

from __future__ import annotations

from fastapi import HTTPException, Request, WebSocket

from config.api_settings import ApiSettings
from services.config_service import ConfigService
from services.landmarker_service import LandmarkerService
from services.session_service import SessionService
from services.workout_service import WorkoutService


def get_api_settings(request: Request) -> ApiSettings:
    return request.app.state.api_settings


def get_landmarker(request: Request) -> LandmarkerService:
    return request.app.state.landmarker


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


def get_config_service(request: Request) -> ConfigService:
    return request.app.state.config_service


def get_workout_service(request: Request) -> WorkoutService:
    return request.app.state.workout_service


async def verify_bearer_token(request: Request) -> str:
    """
    Validate Bearer token forwarded by Laravel.

    TODO: Call Laravel validation service when AI_AUTH_VALIDATION=true.
    """
    auth_header = request.headers.get("Authorization", "")
    # if not auth_header.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Missing or invalid bearer token")

    token = auth_header.removeprefix("Bearer ").strip()
    # if not token:
    #     raise HTTPException(status_code=401, detail="Empty bearer token")

    api_settings: ApiSettings = request.app.state.api_settings

    if not api_settings.auth_validation_enabled:
        # TODO: Integrate Laravel token introspection endpoint.
        return token

    # TODO: POST token to api_settings.auth_validation_url and verify response.
    if api_settings.service_token and token != api_settings.service_token:
        raise HTTPException(status_code=401, detail="Invalid service token")

    return token


async def verify_websocket_token(websocket: WebSocket) -> str:
    """Validate token from WebSocket query string."""
    token = websocket.query_params.get("token", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing WebSocket token")

    api_settings: ApiSettings = websocket.app.state.api_settings

    if not api_settings.auth_validation_enabled:
        return token

    # TODO: Validate WebSocket token via Laravel.
    if api_settings.service_token and token != api_settings.service_token:
        raise HTTPException(status_code=401, detail="Invalid WebSocket token")

    return token

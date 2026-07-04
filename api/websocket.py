"""WebSocket streaming for live workout state."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.session_service import SessionNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter()


async def _validate_ws_token(websocket: WebSocket) -> bool:
    """Validate Bearer token from query string."""
    token = websocket.query_params.get("token", "")
    if not token:
        await websocket.close(code=4401, reason="Missing token")
        return False

    api_settings = websocket.app.state.api_settings
    if api_settings.auth_validation_enabled:
        # TODO: Validate WebSocket token via Laravel introspection endpoint.
        if api_settings.service_token and token != api_settings.service_token:
            await websocket.close(code=4401, reason="Invalid token")
            return False

    return True


@router.websocket("/ws/workout/{session_id}")
async def workout_stream(websocket: WebSocket, session_id: str) -> None:
    """
    Stream processed ExerciseState JSON to connected clients.

    Connect with ``?token=<bearer_token>``.
    Sends only processed metrics — never raw landmarks.
    """
    if not await _validate_ws_token(websocket):
        return

    session_service = websocket.app.state.session_service

    try:
        session = await session_service.get(session_id)
    except SessionNotFoundError:
        await websocket.close(code=4404, reason="Session not found")
        return

    await websocket.accept()
    target_fps = session.api_settings.websocket_target_fps
    interval = 1.0 / max(1, target_fps)

    logger.info("WebSocket connected session=%s", session_id)

    try:
        while session.is_running:
            state = await session.get_state()
            await websocket.send_json(state.model_dump(mode="json"))

            if state.fps > 0:
                logger.debug(
                    "WebSocket state session=%s reps=%s fps=%.1f",
                    session_id,
                    state.reps,
                    state.fps,
                )

            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected session=%s", session_id)
    except Exception:
        logger.exception("WebSocket error session=%s", session_id)
        await websocket.close(code=1011, reason="Internal error")

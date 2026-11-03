"""WebSocket streaming for live workout state."""

from __future__ import annotations

import logging

import cv2
import numpy as np
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
    Receive mobile JPEG frames and send processed ExerciseState JSON.

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
    logger.info("WebSocket connected session=%s", session_id)

    try:
        while session.is_running:
            message = await websocket.receive()

            if message.get("bytes") is not None:
                frame = cv2.imdecode(
                    np.frombuffer(message["bytes"], np.uint8),
                    cv2.IMREAD_COLOR,
                )
                if frame is None:
                    logger.debug(
                        "WS: dropped non-decodable frame session=%s", session_id
                    )
                    continue

                state = session.process_frame(frame)
                await websocket.send_json(state.model_dump(mode="json"))
                continue

            if message.get("text") == "stop":
                break
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected session=%s", session_id)
    except Exception:
        logger.exception("WS processing error session=%s", session_id)
    finally:
        try:
            await session.stop()
        except Exception:
            logger.exception("Error stopping session on WS close session=%s", session_id)

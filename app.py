"""
AI Fitness Coach — FastAPI application entry point.

Run with::

    uvicorn app:app --reload

Desktop app remains available via::

    python main.py
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from api.middleware import RequestLoggingMiddleware
from api.routes import router as api_router
from api.websocket import router as ws_router
from config.api_settings import ApiSettings
from config.settings import Settings
from services.config_service import ConfigService
from services.landmarker_service import LandmarkerService
from services.session_service import SessionService
from services.workout_service import WorkoutService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared services on startup; clean up on shutdown."""
    settings = Settings()
    api_settings = ApiSettings()

    landmarker = LandmarkerService(settings)
    landmarker.initialize()

    session_service = SessionService(landmarker, settings, api_settings)
    config_service = ConfigService(api_settings)
    workout_service = WorkoutService(session_service, config_service, api_settings)

    app.state.settings = settings
    app.state.api_settings = api_settings
    app.state.landmarker = landmarker
    app.state.session_service = session_service
    app.state.config_service = config_service
    app.state.workout_service = workout_service

    logger.info("AI Fitness FastAPI service started")
    yield

    await session_service.shutdown_all()
    landmarker.release()
    logger.info("AI Fitness FastAPI service stopped")


app = FastAPI(
    title="AI Fitness Coach API",
    description="MediaPipe-powered exercise detection service for Laravel and Flutter.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router)
app.include_router(ws_router)

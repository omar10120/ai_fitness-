"""Active workout session model."""

from __future__ import annotations

# NOTE: In production the camera is streamed from the mobile client
# over WebSocket. `_processing_loop()` and `utils/camera.py` are kept
# for local development only and are not invoked by `start()` in the
# mobile flow.

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

import numpy as np

from config.api_settings import ApiSettings
from config.exercise_config import ExerciseConfig
from config.settings import Settings
from schemas.mapper import to_exercise_state
from schemas.response import ExerciseState, WorkoutStopResponse
from services.exercise_manager import ExerciseManager
from services.landmarker_service import LandmarkerService
from utils.camera import Camera
from utils.fps import FpsCounter

logger = logging.getLogger(__name__)


@dataclass
class WorkoutSession:
    """
    Encapsulates a single user's live workout.

    Supports concurrent sessions — each instance owns its own exercise
    manager and processing state.
    """

    session_id: UUID
    user_id: int
    exercise_key: str
    camera: str
    exercise_manager: ExerciseManager
    landmarker: LandmarkerService
    exercise_config: ExerciseConfig
    settings: Settings = field(default_factory=Settings)
    api_settings: ApiSettings = field(default_factory=ApiSettings)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    _camera: Camera | None = field(default=None, init=False, repr=False)
    _fps_counter: FpsCounter = field(default_factory=FpsCounter, init=False, repr=False)
    _timestamp_ms: int = field(default=0, init=False)
    _running: bool = field(default=False, init=False)
    _task: asyncio.Task[None] | None = field(default=None, init=False, repr=False)
    _current_state: ExerciseState | None = field(default=None, init=False)
    _fps: float = field(default=0.0, init=False)
    _state_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    def elapsed_seconds(self) -> int:
        """Return elapsed workout duration in seconds."""
        delta = datetime.now(timezone.utc) - self.started_at
        return max(0, int(delta.total_seconds()))

    async def start(self) -> None:
        """Prepare session. No camera is opened — the mobile client streams frames."""
        self.exercise_manager.select(self.exercise_key, self.exercise_config)
        self._running = True
        logger.info(
            "Workout started session=%s user=%s exercise=%s source=%s",
            self.session_id,
            self.user_id,
            self.exercise_key,
            self.camera,
        )

    def process_frame(self, frame_bgr: np.ndarray) -> ExerciseState:
        """Process one BGR frame received from the mobile client.

        This runs synchronously in the WebSocket connection's task so the
        inference matches the existing processing loop's threading model.
        """
        landmarks = self.landmarker.detect(frame_bgr, self._timestamp_ms)
        self._timestamp_ms += self.settings.frame_timestamp_ms
        self.exercise_manager.update(landmarks)
        self._fps = self._fps_counter.update()

        internal_state = self.exercise_manager.get_state()
        angles = self.exercise_manager.joint_angles()
        if internal_state is not None:
            merged_metrics = dict(internal_state.metrics)
            merged_metrics.update(angles)
            internal_state.metrics.clear()
            internal_state.metrics.update(merged_metrics)

        state = to_exercise_state(
            self.exercise_key,
            internal_state,
            self._fps,
            self.elapsed_seconds(),
            self.api_settings,
            angles,
        )
        self._current_state = state
        return state

    async def stop(self) -> WorkoutStopResponse:
        """Stop processing and return workout summary."""
        self._running = False

        if self._task is not None:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self._task.cancel()
            self._task = None

        if self._camera is not None:
            self._camera.release()
            self._camera = None

        duration = self.elapsed_seconds()
        active = self.exercise_manager.active
        reps = active.reps if active else 0
        score = active.score if active else 100.0
        calories = to_exercise_state(
            self.exercise_key,
            self.exercise_manager.get_state(),
            self._fps,
            duration,
            self.api_settings,
        ).calories

        logger.info(
            "Workout finished session=%s duration=%ss reps=%s score=%s",
            self.session_id,
            duration,
            reps,
            score,
        )

        return WorkoutStopResponse(
            duration=duration,
            reps=reps,
            score=round(score, 1),
            calories=calories,
        )

    async def reset(self) -> None:
        """Reset rep counter for the active exercise."""
        self.exercise_manager.reset()
        logger.info("Workout reset session=%s", self.session_id)

    async def get_state(self) -> ExerciseState:
        """Return the latest processed exercise state."""
        async with self._state_lock:
            if self._current_state is not None:
                return self._current_state

            return to_exercise_state(
                self.exercise_key,
                self.exercise_manager.get_state(),
                self._fps,
                self.elapsed_seconds(),
                self.api_settings,
                self.exercise_manager.joint_angles(),
            )

    async def _processing_loop(self) -> None:
        """Local-dev only. Mobile clients stream frames via WebSocket instead."""
        frame_interval = 1.0 / max(1, self.api_settings.websocket_target_fps)

        try:
            while self._running:
                loop_start = time.perf_counter()

                if self._camera is None:
                    break

                success, frame = await asyncio.to_thread(self._camera.read)
                if not success or frame is None:
                    await asyncio.sleep(0.05)
                    continue

                landmarks = await asyncio.to_thread(
                    self.landmarker.detect,
                    frame,
                    self._timestamp_ms,
                )
                self._timestamp_ms += self.settings.frame_timestamp_ms

                self.exercise_manager.update(landmarks)
                self._fps = self._fps_counter.update()

                internal_state = self.exercise_manager.get_state()
                angles = self.exercise_manager.joint_angles()
                if internal_state is not None:
                    merged_metrics = dict(internal_state.metrics)
                    merged_metrics.update(angles)
                    internal_state.metrics.clear()
                    internal_state.metrics.update(merged_metrics)

                state = to_exercise_state(
                    self.exercise_key,
                    internal_state,
                    self._fps,
                    self.elapsed_seconds(),
                    self.api_settings,
                    angles,
                )

                async with self._state_lock:
                    self._current_state = state

                elapsed = time.perf_counter() - loop_start
                sleep_for = max(0.0, frame_interval - elapsed)
                await asyncio.sleep(sleep_for)
        except asyncio.CancelledError:
            logger.debug("Processing loop cancelled session=%s", self.session_id)
            raise
        except Exception:
            logger.exception("Processing loop error session=%s", self.session_id)
            self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

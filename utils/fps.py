"""Frames-per-second measurement utility."""

from __future__ import annotations

import time


class FpsCounter:
    """Tracks rolling FPS based on wall-clock time between updates."""

    def __init__(self) -> None:
        self._prev_time = time.time()
        self._fps = 0.0

    def update(self) -> float:
        """
        Record a new frame timestamp and return the current FPS.

        Returns:
            Estimated frames per second.
        """
        current_time = time.time()
        elapsed = current_time - self._prev_time
        self._prev_time = current_time

        if elapsed > 0:
            self._fps = 1.0 / elapsed

        return self._fps

    @property
    def value(self) -> float:
        """Last computed FPS value."""
        return self._fps

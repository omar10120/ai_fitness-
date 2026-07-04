"""Geometric utilities for pose analysis."""

from __future__ import annotations

from typing import Sequence

import numpy as np

Point = Sequence[float]


class Geometry:
    """Static geometry helpers for joint-angle and spatial calculations."""

    @staticmethod
    def calculate_angle(a: Point, b: Point, c: Point) -> float:
        """
        Calculate the interior angle at point ``b`` formed by segments ``a-b`` and ``c-b``.

        Args:
            a: First endpoint (e.g. shoulder).
            b: Vertex / joint (e.g. elbow).
            c: Second endpoint (e.g. wrist).

        Returns:
            Angle in degrees, range [0, 180].
        """
        a_arr = np.array(a, dtype=float)
        b_arr = np.array(b, dtype=float)
        c_arr = np.array(c, dtype=float)

        radians = (
            np.arctan2(c_arr[1] - b_arr[1], c_arr[0] - b_arr[0])
            - np.arctan2(a_arr[1] - b_arr[1], a_arr[0] - b_arr[0])
        )
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180:
            angle = 360 - angle

        return float(angle)

    @staticmethod
    def distance(a: Point, b: Point) -> float:
        """
        Euclidean distance between two 2D or 3D points.

        Args:
            a: First point.
            b: Second point.

        Returns:
            Scalar distance.
        """
        a_arr = np.array(a, dtype=float)
        b_arr = np.array(b, dtype=float)
        return float(np.linalg.norm(a_arr - b_arr))

    @staticmethod
    def midpoint(a: Point, b: Point) -> tuple[float, float]:
        """
        Midpoint between two points (2D).

        Args:
            a: First point.
            b: Second point.

        Returns:
            ``(x, y)`` midpoint.
        """
        return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)

    @staticmethod
    def normalize(v: Point) -> tuple[float, float]:
        """
        Return a unit vector in the same direction as ``v``.

        Args:
            v: Input vector ``(x, y)``.

        Returns:
            Normalized vector. Returns ``(0.0, 0.0)`` for zero-length input.
        """
        vec = np.array(v, dtype=float)
        magnitude = np.linalg.norm(vec)
        if magnitude == 0:
            return (0.0, 0.0)
        unit = vec / magnitude
        return (float(unit[0]), float(unit[1]))

    @staticmethod
    def vector(a: Point, b: Point) -> tuple[float, float]:
        """
        Direction vector from point ``a`` to point ``b``.

        Args:
            a: Origin point.
            b: Target point.

        Returns:
            Vector ``(dx, dy)``.
        """
        return (b[0] - a[0], b[1] - a[1])

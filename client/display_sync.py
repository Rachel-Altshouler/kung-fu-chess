from __future__ import annotations

import time
from typing import Any


def _smooth_progress(t: float) -> float:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return t * t * (3.0 - 2.0 * t)


def position_at_time(movement, clock: int) -> tuple[float, float]:
    """Interpolate piece position along its path (same logic as GameEngine)."""
    path = getattr(movement, "path", None) or []
    if not path:
        return movement.source

    if clock <= path[0][1]:
        return path[0][0]

    for index in range(len(path) - 1):
        (row1, col1), time1 = path[index]
        (row2, col2), time2 = path[index + 1]
        if clock < time2:
            if time2 == time1:
                progress = 1.0
            else:
                progress = (clock - time1) / (time2 - time1)
            if not getattr(movement, "is_jump", False):
                progress = _smooth_progress(progress)
            return (
                row1 + (row2 - row1) * progress,
                col1 + (col2 - col1) * progress,
            )

    return path[-1][0]


class DisplayClock:
    """Extrapolate server clock between WebSocket state updates for smooth walking."""

    def __init__(self):
        self._server_clock = 0
        self._anchor_wall = time.monotonic()

    def sync(self, server_clock: int):
        self._server_clock = int(server_clock)
        self._anchor_wall = time.monotonic()

    def now(self) -> int:
        elapsed_ms = int((time.monotonic() - self._anchor_wall) * 1000)
        return self._server_clock + max(elapsed_ms, 0)


def apply_smooth_positions(snapshot, display_clock: int):
    """Recompute moving piece positions for the local display clock."""
    snapshot.clock = display_clock
    for piece in snapshot.pieces:
        movement = piece.get("movement")
        if movement is not None:
            row, col = position_at_time(movement, display_clock)
            piece["row"] = row
            piece["col"] = col
    return snapshot


def token_at_square(state: dict[str, Any], row: int, col: int) -> str:
    """Pick token for click targeting: prefer stationary board cell, else pieces list."""
    board = state.get("board") or []
    if 0 <= row < len(board) and 0 <= col < len(board[0]):
        token = board[row][col]
        if token and token != ".":
            return token

    for piece in state.get("pieces") or []:
        if piece.get("movement") is not None:
            continue
        if int(round(piece["row"])) == row and int(round(piece["col"])) == col:
            return piece["token"]
    return "."

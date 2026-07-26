from __future__ import annotations

from pathlib import Path

from domain.constants import BoardConstants
from rendering.piece_assets import PieceAssets


class SpriteManager:
    """Standing pieces stay still; walking cycles one step per square."""

    DEFAULT_FPS = {
        "idle": 6,
        "move": 8,
        "jump": 8,
        "short_rest": 8,
        "long_rest": 6,
    }
    FRAMES_PER_STATE = 5

    def __init__(self, assets_dir: str | Path):
        self._assets = PieceAssets(assets_dir)

    def get_state_and_frame(
        self,
        token: str,
        movement,
        clock: int,
    ) -> tuple[str, int]:
        # Standing still — never animate on clicks / idle board actions
        if movement is None:
            return "idle", 1

        if movement.is_jump:
            elapsed = max(clock - movement.start_time, 0)
            return "jump", self._frame_for_state("jump", elapsed)

        return "move", self._walk_frame(movement, clock)

    def _walk_frame(self, movement, clock: int) -> int:
        """One full 5-frame step cycle per board square traveled."""
        start = int(movement.start_time)
        finish = int(movement.finish_time)
        if finish <= start:
            return 1

        elapsed = max(0, min(clock - start, finish - start))
        ms_per = max(BoardConstants.MS_PER_SQUARE, 1)
        # Progress in "square units" (smooth), then map to walk cycle
        squares_traveled = elapsed / ms_per
        frame_index = int(squares_traveled * self.FRAMES_PER_STATE) % self.FRAMES_PER_STATE
        return frame_index + 1

    @staticmethod
    def _frame_for_state(state: str, elapsed_ms: int) -> int:
        fps = SpriteManager.DEFAULT_FPS.get(state, 6)
        frame_index = int((elapsed_ms / 1000.0) * fps) % SpriteManager.FRAMES_PER_STATE
        return frame_index + 1

    def get_sprite_path(self, token: str, state: str, frame: int) -> Path:
        return self._assets.sprite_path(token, state=state, frame=frame)

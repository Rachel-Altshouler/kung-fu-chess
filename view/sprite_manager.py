from __future__ import annotations

from pathlib import Path

from view.piece_assets import PieceAssets

#אנימציות
class SpriteManager:
    DEFAULT_FPS = {
        "idle": 6,
        "move": 12,
        "jump": 8,
        "short_rest": 8,
        "long_rest": 6,
    }
    def __init__(self, assets_dir: str | Path):
        self._assets = PieceAssets(assets_dir)

    def get_state_and_frame(
        self,
        token: str,
        movement,
        clock: int,
    ) -> tuple[str, int]:
        if movement is None:
            return "idle", 1

        state = "jump" if movement.is_jump else "move"
        elapsed = max(clock - movement.start_time, 0)
        return state, self._frame_for_state(state, elapsed)

    @staticmethod
    def _frame_for_state(state: str, elapsed_ms: int) -> int:
        fps = SpriteManager.DEFAULT_FPS.get(state, 6)
        frame_index = int((elapsed_ms / 1000.0) * fps) % 5
        return frame_index + 1

    def get_sprite_path(self, token: str, state: str, frame: int) -> Path:
        return self._assets.sprite_path(token, state=state, frame=frame)

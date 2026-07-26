from __future__ import annotations

from pathlib import Path

#נתיבים לתמונות
class PieceAssets:
    PIECES_SET = "pieces_mine"

    def __init__(self, assets_dir: Path, pieces_set: str = PIECES_SET):
        self._assets_dir = Path(assets_dir)
        self._pieces_dir = self._assets_dir / pieces_set

    def board_image_path(self) -> Path:
        return self._assets_dir / "board.png"

    def sprite_path(self, token: str, state: str = "idle", frame: int = 1) -> Path:
        sprite_dir = self._pieces_dir / token / "states" / state / "sprites"
        return sprite_dir / f"{frame}.png"

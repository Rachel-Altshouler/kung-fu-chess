"""Legacy wrapper kept for unit tests. Use Renderer for graphics."""

from __future__ import annotations

from pathlib import Path


class ImageView:
    def __init__(self, enabled: bool = False, assets_dir: str | Path | None = None):
        self._enabled = enabled
        self._assets_dir = assets_dir

    def is_enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def render(self, board):
        if not self._enabled:
            raise NotImplementedError("Image rendering is not available in text mode")

        from engine.game_engine import GameEngine
        from view.renderer import Renderer

        engine = GameEngine(board)
        renderer = Renderer(self._assets_dir)
        snapshot = engine.get_snapshot()
        canvas = renderer.render(snapshot)
        canvas.show()

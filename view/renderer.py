from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from game_io.board_printer import BoardPrinter
from model.constants import BoardConstants, GraphicsConstants
from view.img import Img
from view.piece_assets import PieceAssets
from view.sprite_manager import SpriteManager
from view.time_format import (
    format_game_clock,
    format_score_seconds,
    player_name_english,
    player_name_hebrew,
)


class Renderer:
    def __init__(self, assets_dir: str | Path | None = None):
        if assets_dir is None:
            assets_dir = Path(__file__).resolve().parent.parent / "assets"
        self._assets_dir = Path(assets_dir)
        self._assets = PieceAssets(self._assets_dir)
        self._sprite_manager = SpriteManager(self._assets_dir)

    @staticmethod
    def render_text(board) -> str:
        return BoardPrinter.get_canonical_representation(board)
    #מצייר את הנתוני של המשחק על המסך
    def render(self, snapshot):
        cell = GraphicsConstants.DISPLAY_CELL_SIZE
        piece_size = int(cell * BoardConstants.PIECE_CELL_RATIO)
        board_w = snapshot.cols * cell
        board_h = snapshot.rows * cell
        total_h = board_h + GraphicsConstants.HEADER_HEIGHT + GraphicsConstants.FOOTER_HEIGHT

        canvas = Img()
        canvas.img = np.full((total_h, board_w, 3), 50, dtype=np.uint8)

        board_img = Img().read(
            self._assets.board_image_path(),
            size=(board_w, board_h),
            keep_aspect=False,
            interpolation=cv2.INTER_AREA,
        )
        board_img.draw_on(canvas, 0, GraphicsConstants.HEADER_HEIGHT)

        for piece in snapshot.pieces:
            state, frame = self._sprite_manager.get_state_and_frame(
                piece["token"],
                piece.get("movement"),
                snapshot.clock,
            )
            sprite_path = self._sprite_manager.get_sprite_path(
                piece["token"],
                state,
                frame,
            )

            cell_x = piece["col"] * cell
            cell_y = piece["row"] * cell

            sprite = Img().read(
                sprite_path,
                size=(piece_size, piece_size),
                keep_aspect=True,
                interpolation=cv2.INTER_LINEAR,
                remove_black_bg=True,
            )
            sprite_h, sprite_w = sprite.img.shape[:2]
            offset_x = int(cell_x + (cell - sprite_w) / 2)
            offset_y = int(
                GraphicsConstants.HEADER_HEIGHT
                + cell_y
                + (cell - sprite_h) / 2
            )
            sprite.draw_on(canvas, offset_x, offset_y)

        canvas.put_text(
            f"Time {format_game_clock(snapshot.clock)}",
            10,
            28,
            0.65,
            color=(0, 255, 0, 255),
            thickness=2,
        )
        canvas.put_text(
            f"W {format_score_seconds(snapshot.white_score)}",
            180,
            28,
            0.65,
            color=(255, 255, 255, 255),
            thickness=2,
        )
        canvas.put_text(
            f"B {format_score_seconds(snapshot.black_score)}",
            380,
            28,
            0.65,
            color=(255, 255, 255, 255),
            thickness=2,
        )

        if snapshot.game_over:
            footer_y = GraphicsConstants.HEADER_HEIGHT + board_h + 26
            if snapshot.is_stalemate:
                canvas.put_text(
                    "Stalemate - Draw",
                    10,
                    footer_y,
                    0.85,
                    color=(0, 255, 255, 255),
                    thickness=2,
                )
            else:
                winner_en = player_name_english(snapshot.winner)
                canvas.put_text(
                    f"Checkmate: {winner_en}",
                    10,
                    footer_y,
                    0.85,
                    color=(0, 255, 255, 255),
                    thickness=2,
                )
                canvas.put_text(
                    f"{winner_en} wins!",
                    300,
                    footer_y,
                    0.85,
                    color=(0, 255, 255, 255),
                    thickness=2,
                )
            canvas.put_text(
                "Press Q to exit",
                10,
                footer_y + 22,
                0.55,
                color=(200, 200, 200, 255),
                thickness=1,
            )

        return canvas

    @staticmethod
    def pixel_to_board_position(board, x, y):
        adjusted_y = y - GraphicsConstants.HEADER_HEIGHT
        if adjusted_y < 0:
            return None

        col = x // GraphicsConstants.DISPLAY_CELL_SIZE
        row = adjusted_y // GraphicsConstants.DISPLAY_CELL_SIZE
        if board.is_within_bounds(row, col):
            return row, col
        return None

    @staticmethod
    def board_position_to_engine_pixels(row, col):
        center_x = col * BoardConstants.CELL_SIZE + BoardConstants.CELL_SIZE // 2
        center_y = row * BoardConstants.CELL_SIZE + BoardConstants.CELL_SIZE // 2
        return center_x, center_y

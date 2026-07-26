from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from tools.board_printer import BoardPrinter
from domain.constants import BoardConstants, Colors, GraphicsConstants
from rendering.img import Img
from rendering.piece_assets import PieceAssets
from rendering.sprite_manager import SpriteManager
from rendering.time_format import (
    format_game_clock,
    format_score_seconds,
    player_name_english,
)


class Renderer:
    def __init__(self, assets_dir: str | Path | None = None):
        if assets_dir is None:
            kung_fu_root = Path(__file__).resolve().parent.parent
            assets_dir = kung_fu_root / "assets"
            if not assets_dir.is_dir():
                assets_dir = kung_fu_root.parent / "assets"
        self._assets_dir = Path(assets_dir)
        self._assets = PieceAssets(self._assets_dir)
        self._sprite_manager = SpriteManager(self._assets_dir)

    @staticmethod
    def render_text(board) -> str:
        return BoardPrinter.get_canonical_representation(board)
    #מצייר את הנתוני של המשחק על המסך
    def render(
        self,
        snapshot,
        score_board=None,
        move_log_panel=None,
        animations=None,
    ):
        cell = GraphicsConstants.DISPLAY_CELL_SIZE
        piece_size = int(cell * BoardConstants.PIECE_CELL_RATIO)
        board_w = snapshot.cols * cell
        board_h = snapshot.rows * cell
        side = GraphicsConstants.SIDE_PANEL_WIDTH
        total_w = board_w + side * 2
        total_h = board_h + GraphicsConstants.HEADER_HEIGHT + GraphicsConstants.FOOTER_HEIGHT
        board_x = side

        white_score = (
            score_board.white_score if score_board is not None else snapshot.white_score
        )
        black_score = (
            score_board.black_score if score_board is not None else snapshot.black_score
        )
        move_log = (
            move_log_panel.records
            if move_log_panel is not None
            else getattr(snapshot, "move_log", [])
        )

        canvas = Img()
        canvas.img = np.full((total_h, total_w, 3), 50, dtype=np.uint8)

        board_img = Img().read(
            self._assets.board_image_path(),
            size=(board_w, board_h),
            keep_aspect=False,
            interpolation=cv2.INTER_AREA,
        )
        board_img.draw_on(canvas, board_x, GraphicsConstants.HEADER_HEIGHT)

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

            cell_x = board_x + piece["col"] * cell
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
            board_x + 10,
            28,
            0.65,
            color=(0, 255, 0, 255),
            thickness=2,
        )
        canvas.put_text(
            f"W {format_score_seconds(white_score)}",
            board_x + 180,
            28,
            0.65,
            color=(255, 255, 255, 255),
            thickness=2,
        )
        canvas.put_text(
            f"B {format_score_seconds(black_score)}",
            board_x + 300,
            28,
            0.65,
            color=(255, 255, 255, 255),
            thickness=2,
        )

        self._draw_move_log_panel(
            canvas,
            move_log,
            Colors.WHITE,
            x=8,
            y=GraphicsConstants.HEADER_HEIGHT + 8,
            title="White moves",
        )
        self._draw_move_log_panel(
            canvas,
            move_log,
            Colors.BLACK,
            x=board_x + board_w + 8,
            y=GraphicsConstants.HEADER_HEIGHT + 8,
            title="Black moves",
        )

        if snapshot.game_over:
            footer_y = GraphicsConstants.HEADER_HEIGHT + board_h + 26
            if snapshot.is_stalemate:
                canvas.put_text(
                    "Stalemate - Draw",
                    board_x + 10,
                    footer_y,
                    0.85,
                    color=(0, 255, 255, 255),
                    thickness=2,
                )
            else:
                winner_en = player_name_english(snapshot.winner)
                canvas.put_text(
                    f"Checkmate: {winner_en}",
                    board_x + 10,
                    footer_y,
                    0.85,
                    color=(0, 255, 255, 255),
                    thickness=2,
                )
                canvas.put_text(
                    f"{winner_en} wins!",
                    board_x + 300,
                    footer_y,
                    0.85,
                    color=(0, 255, 255, 255),
                    thickness=2,
                )
            canvas.put_text(
                "Press Q to exit",
                board_x + 10,
                footer_y + 22,
                0.55,
                color=(200, 200, 200, 255),
                thickness=1,
            )

        if animations is not None and animations.is_active:
            self._draw_animation_overlay(
                canvas,
                animations.message,
                total_w,
                total_h,
            )

        return canvas

    def _draw_move_log_panel(self, canvas, move_log, color, x, y, title):
        canvas.put_text(
            title,
            x,
            y,
            0.5,
            color=(0, 255, 255, 255),
            thickness=1,
        )

        records = [record for record in move_log if record.color == color]
        recent = records[-GraphicsConstants.MOVE_LOG_MAX_LINES:]

        line_y = y + 22
        for record in recent:
            time_text = format_game_clock(record.finish_time)
            move_text = (
                f"{record.piece_token} "
                f"{record.square_name(record.source)}-"
                f"{record.square_name(record.destination)}"
            )
            if record.captured_token:
                move_text += "x"
            canvas.put_text(
                f"{time_text} {move_text}",
                x,
                line_y,
                0.4,
                color=(220, 220, 220, 255),
                thickness=1,
            )
            line_y += GraphicsConstants.MOVE_LOG_LINE_HEIGHT

    @staticmethod
    def _draw_animation_overlay(canvas, message, total_w, total_h):
        overlay = canvas.img.copy()
        cv2.rectangle(overlay, (0, 0), (total_w - 1, total_h - 1), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.45, canvas.img, 0.55, 0, canvas.img)
        text_size = cv2.getTextSize(
            message,
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            2,
        )[0]
        text_x = max((total_w - text_size[0]) // 2, 10)
        text_y = total_h // 2
        canvas.put_text(
            message,
            text_x,
            text_y,
            1.1,
            color=(0, 255, 255, 255),
            thickness=2,
        )

    @staticmethod
    def pixel_to_board_position(board, x, y):
        adjusted_x = x - GraphicsConstants.SIDE_PANEL_WIDTH
        adjusted_y = y - GraphicsConstants.HEADER_HEIGHT
        if adjusted_x < 0 or adjusted_y < 0:
            return None

        col = adjusted_x // GraphicsConstants.DISPLAY_CELL_SIZE
        row = adjusted_y // GraphicsConstants.DISPLAY_CELL_SIZE
        if board.is_within_bounds(row, col):
            return row, col
        return None


    @staticmethod
    def board_position_to_engine_pixels(row, col):
        center_x = col * BoardConstants.CELL_SIZE + BoardConstants.CELL_SIZE // 2
        center_y = row * BoardConstants.CELL_SIZE + BoardConstants.CELL_SIZE // 2
        return center_x, center_y

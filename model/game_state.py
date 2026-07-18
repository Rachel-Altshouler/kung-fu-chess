from __future__ import annotations

from model.constants import BoardConstants, Colors, ScoreConstants
from model.piece import Piece


class GameState:
    def __init__(self, board):
        self._board = board
        self._clock = 0
        self._active_movements = []
        self._next_movement_id = 1
        self._game_over = False
        self._winner = None
        self._is_stalemate = False
        self._white_score = 0
        self._black_score = 0
        self._cooldown_until = {}

    def is_on_cooldown(self, position, clock: int) -> bool:
        coords = self._to_coords(position)
        expiry = self._cooldown_until.get(coords)
        return expiry is not None and clock < expiry

    def set_cooldown(self, position, clock: int):
        coords = self._to_coords(position)
        self._cooldown_until[coords] = (
            clock + BoardConstants.MOVE_COOLDOWN_MS
        )

    def clear_cooldown(self, position):
        coords = self._to_coords(position)
        self._cooldown_until.pop(coords, None)

    @staticmethod
    def _to_coords(position):
        if hasattr(position, "as_tuple"):
            return position.as_tuple()
        return position[0], position[1]

    def get_white_score(self) -> int:
        return self._white_score

    def get_black_score(self) -> int:
        return self._black_score

    def add_capture_score(self, capturing_color: str, captured_token: str):
        captured = Piece.from_token(captured_token)
        if captured is None:
            return

        seconds = ScoreConstants.PIECE_CAPTURE_SECONDS.get(
            captured.piece_type,
            0,
        )
        if capturing_color == Colors.WHITE:
            self._white_score += seconds
        elif capturing_color == Colors.BLACK:
            self._black_score += seconds

    def get_board(self):
        return self._board

    def get_clock(self) -> int:
        return self._clock

    def is_game_over(self) -> bool:
        return self._game_over

    def set_game_over(self, winner: str | None = None, is_stalemate: bool = False):
        self._game_over = True
        self._is_stalemate = is_stalemate
        if winner is not None:
            self._winner = winner

    def get_winner(self) -> str | None:
        return self._winner

    def is_stalemate(self) -> bool:
        return self._is_stalemate

    def advance_clock(self, milliseconds: int):
        self._clock += milliseconds

    def get_active_movements(self):
        return list(self._active_movements)

    def get_active_movements_ref(self):
        return self._active_movements

    def allocate_movement_id(self) -> int:
        movement_id = self._next_movement_id
        self._next_movement_id += 1
        return movement_id

    def add_movement(self, movement):
        self._active_movements.append(movement)

    def remove_movement(self, movement):
        self._active_movements.remove(movement)

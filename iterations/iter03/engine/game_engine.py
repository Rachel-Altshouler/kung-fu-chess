from input.controller import Controller
from model.constants import Colors, PieceTypes
from model.piece import Piece


class GameEngine:
    def __init__(self, board):
        self._board = board
        self._clock = 0
        self._controller = Controller()

    def get_board(self):
        return self._board

    def get_clock(self) -> int:
        return self._clock

    def get_selected_position(self):
        return self._controller.get_selected_position()

    def is_moving(self) -> bool:
        return False

    def is_piece_moving(self, position) -> bool:
        return False

    def handle_click(self, x: int, y: int):
        self._controller.handle_click(self, x, y)

    def try_move(self, source_position, destination_position) -> bool:
        from rules.rule_engine import RuleEngine

        source_coords = self._to_coords(source_position)
        destination_coords = self._to_coords(destination_position)
        if not RuleEngine.is_valid_move(self._board, source_coords, destination_coords):
            return False

        self._board.move_piece(source_coords, destination_coords)
        self._promote_pawn_if_needed(destination_coords)
        return True

    def handle_wait(self, milliseconds: int):
        self._clock += milliseconds

    def _promote_pawn_if_needed(self, destination):
        token = self._board.get_piece_at(destination)
        piece = Piece.from_token(token)
        if piece is None or piece.piece_type != PieceTypes.PAWN:
            return

        row, _col = destination
        num_rows = len(self._board.get_grid())
        if piece.color == Colors.WHITE and row == 0:
            self._board.set_piece_at(destination, f"{Colors.WHITE}{PieceTypes.QUEEN}")
        elif piece.color == Colors.BLACK and row == num_rows - 1:
            self._board.set_piece_at(destination, f"{Colors.BLACK}{PieceTypes.QUEEN}")

    @staticmethod
    def _to_coords(position):
        if hasattr(position, 'as_tuple'):
            return position.as_tuple()
        return position[0], position[1]

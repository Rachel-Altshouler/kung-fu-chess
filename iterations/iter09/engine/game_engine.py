from input.controller import Controller
from input.board_mapper import BoardMapper
from model.constants import Colors, PieceTypes
from model.game_state import GameState
from model.piece import Piece
from realtime.motion import Motion
from realtime.real_time_arbiter import RealTimeArbiter


class GameEngine:
    def __init__(self, board):
        self._state = GameState(board)
        self._controller = Controller()

    def get_board(self):
        return self._state.get_board()

    def get_clock(self) -> int:
        return self._state.get_clock()

    def get_selected_position(self):
        return self._controller.get_selected_position()

    def get_active_movements(self):
        return self._state.get_active_movements()

    def is_game_over(self) -> bool:
        return self._state.is_game_over()

    def is_moving(self) -> bool:
        return len(self._state.get_active_movements_ref()) > 0

    def is_piece_moving(self, position) -> bool:
        source = self._to_coords(position)
        clock = self._state.get_clock()
        return any(
            movement.source == source and movement.finish_time > clock
            for movement in self._state.get_active_movements_ref()
        )

    def handle_click(self, x: int, y: int):
        if self._state.is_game_over():
            return
        self._controller.handle_click(self, x, y)

    def handle_jump(self, x: int, y: int):
        if self._state.is_game_over():
            return

        board = self._state.get_board()
        target = BoardMapper.pixel_to_position(board, x, y)
        if target is None:
            return

        source = self._resolve_jump_source(target)
        if source is None:
            return
        if self.is_piece_moving(source):
            return
        if board.is_empty(source):
            return
        if not self._is_valid_jump_distance(source, self._to_coords(target)):
            return

        self._start_jump(source, self._to_coords(target))
        self._controller.clear_selection()

    def try_move(self, source_position, destination_position) -> bool:
        from rules.rule_engine import RuleEngine

        if self._state.is_game_over():
            return False

        source_coords = self._to_coords(source_position)
        destination_coords = self._to_coords(destination_position)
        if self.is_piece_moving(source_coords):
            return False

        board = self._state.get_board()
        if not RuleEngine.is_valid_move(board, source_coords, destination_coords):
            return False

        self._start_movement(source_coords, destination_coords)
        return True

    def handle_wait(self, milliseconds: int):
        self._state.advance_clock(milliseconds)
        self._apply_jump_captures()
        self._apply_completed_movements()

    def _apply_jump_captures(self):
        captured = RealTimeArbiter.apply_jump_captures(
            self._state.get_active_movements_ref(),
            self._state.get_board(),
            self._state.get_clock(),
        )
        for movement in captured:
            if self._is_king_token(movement.piece_token):
                self._state.set_game_over()
            self._state.remove_movement(movement)

    def _resolve_jump_source(self, target):
        board = self._state.get_board()
        target_coords = self._to_coords(target)
        selected = self._controller.get_selected_position()
        if selected is not None:
            return self._to_coords(selected)

        target_token = board.get_piece_at(target_coords)
        target_piece = Piece.from_token(target_token)
        if target_piece is None:
            return None

        adjacent_friendly = self._find_adjacent_friendly_for_jump(target_coords)
        if adjacent_friendly is not None:
            neighbor_piece = Piece.from_token(board.get_piece_at(adjacent_friendly))
            if (
                target_piece.color == Colors.BLACK
                and neighbor_piece.color == Colors.WHITE
            ):
                return adjacent_friendly

        return target_coords

    def _find_adjacent_friendly_for_jump(self, target):
        board = self._state.get_board()
        target_piece = Piece.from_token(board.get_piece_at(target))
        if target_piece is None:
            return None

        target_row, target_col = target
        for row in range(target_row - 1, target_row + 2):
            for col in range(target_col - 1, target_col + 2):
                if (row, col) == target:
                    continue
                if not board.is_within_bounds(row, col) or board.is_empty((row, col)):
                    continue

                neighbor_piece = Piece.from_token(board.get_piece_at((row, col)))
                if neighbor_piece is not None and not neighbor_piece.is_same_color(target_piece):
                    return (row, col)
        return None

    @staticmethod
    def _is_valid_jump_distance(source, target):
        row_delta = abs(target[0] - source[0])
        col_delta = abs(target[1] - source[1])
        return max(row_delta, col_delta) <= 1

    def _start_jump(self, source_coords, destination_coords):
        board = self._state.get_board()
        piece_token = board.get_piece_at(source_coords)
        path = Motion.build_jump_path(
            source_coords,
            destination_coords,
            self._state.get_clock(),
        )
        movement = Motion(
            self._state.allocate_movement_id(),
            piece_token,
            source_coords,
            destination_coords,
            self._state.get_clock(),
            path[-1][1],
            path,
            is_jump=True,
        )
        self._state.add_movement(movement)

    def _start_movement(self, source_coords, destination_coords):
        board = self._state.get_board()
        piece_token = board.get_piece_at(source_coords)
        piece = Piece.from_token(piece_token)
        is_jump = piece.piece_type == PieceTypes.KNIGHT
        path = Motion.build_path(
            piece.piece_type,
            source_coords,
            destination_coords,
            self._state.get_clock(),
            is_jump=is_jump,
        )
        finish_time = path[-1][1]

        movement = Motion(
            self._state.allocate_movement_id(),
            piece_token,
            source_coords,
            destination_coords,
            self._state.get_clock(),
            finish_time,
            path,
            is_jump=is_jump,
        )
        self._state.add_movement(movement)

    def _apply_completed_movements(self):
        active_movements = self._state.get_active_movements_ref()
        clock = self._state.get_clock()
        ready = [
            movement for movement in active_movements
            if movement.finish_time <= clock
        ]
        ready.sort(key=lambda movement: (movement.finish_time, movement.movement_id))
        resolving_context = list(active_movements)

        for movement in ready:
            if movement not in active_movements:
                continue

            destination = RealTimeArbiter.resolve_destination(
                movement,
                resolving_context,
                self._state.get_board(),
            )
            if destination != movement.source:
                board = self._state.get_board()
                captured_token = board.get_piece_at(destination)
                board.move_piece(movement.source, destination)
                self._promote_pawn_if_needed(board, destination)
                if self._is_king_token(captured_token):
                    self._state.set_game_over()
            self._state.remove_movement(movement)

    @staticmethod
    def _promote_pawn_if_needed(board, destination):
        token = board.get_piece_at(destination)
        piece = Piece.from_token(token)
        if piece is None or piece.piece_type != PieceTypes.PAWN:
            return

        row, _col = destination
        num_rows = len(board.get_grid())
        if piece.color == Colors.WHITE and row == 0:
            board.set_piece_at(destination, f"{Colors.WHITE}{PieceTypes.QUEEN}")
        elif piece.color == Colors.BLACK and row == num_rows - 1:
            board.set_piece_at(destination, f"{Colors.BLACK}{PieceTypes.QUEEN}")

    @staticmethod
    def _is_king_token(token):
        piece = Piece.from_token(token)
        return piece is not None and piece.piece_type == PieceTypes.KING

    @staticmethod
    def _to_coords(position):
        if hasattr(position, 'as_tuple'):
            return position.as_tuple()
        return position[0], position[1]

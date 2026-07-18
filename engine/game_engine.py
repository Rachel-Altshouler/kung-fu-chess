from input.controller import Controller
from input.board_mapper import BoardMapper
from model.constants import Colors, PieceTypes, BoardConstants
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
    #בודק האם הכלי במשבצת זו עדיין בתנועה
    def is_piece_moving(self, position) -> bool:
        source = self._to_coords(position)
        clock = self._state.get_clock()
        return any(
            movement.source == source and movement.finish_time > clock
            for movement in self._state.get_active_movements_ref()
        )
    #האם הכלי במשבצת הזו סיים מהלך לאחרונה ועדיין חייב לחכות 500ms לפני מהלך הבא?
    def is_piece_on_cooldown(self, position) -> bool:
        return self._state.is_on_cooldown(
            self._to_coords(position),
            self._state.get_clock(),
        )
    #לחיצה שמאלית
    def handle_click(self, x: int, y: int):
        if self._state.is_game_over():
            return
        self._controller.handle_click(self, x, y)
    #לחיצה ימנית
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
        if self.is_piece_on_cooldown(source):
            return
        if board.is_empty(source):
            return
        if not self._is_valid_jump_distance(source, self._to_coords(target)):
            return

        self._start_jump(source, self._to_coords(target))
        self._controller.clear_selection()
    #אחרי בחירת כלי ולחיצה על יעד הוא בודק אם הוא יכול לזוז
    def try_move(self, source_position, destination_position) -> bool:
        from rules.rule_engine import RuleEngine

        if self._state.is_game_over():
            return False

        source_coords = self._to_coords(source_position)
        destination_coords = self._to_coords(destination_position)
        if self.is_piece_moving(source_coords):
            return False
        if self.is_piece_on_cooldown(source_coords):
            return False

        board = self._state.get_board()
        if not RuleEngine.is_valid_move(board, source_coords, destination_coords):
            return False

        self._start_movement(source_coords, destination_coords)
        return True

    def handle_wait(self, milliseconds: int):
        self._state.advance_clock(milliseconds)
        self._apply_jump_captures()
        if self._state.is_game_over():
            return
        self._apply_completed_movements()
        if self._state.is_game_over():
            return
        self._evaluate_endgame()

    def _apply_jump_captures(self):
        captured = RealTimeArbiter.apply_jump_captures(
            self._state.get_active_movements_ref(),
            self._state.get_board(),
            self._state.get_clock(),
        )
        for movement in captured:
            capturer_color = self._capturer_color_for_jump_capture(
                movement,
                self._state.get_active_movements_ref(),
            )
            #עדכון ניקוד
            if capturer_color is not None:
                self._state.add_capture_score(
                    capturer_color,
                    movement.piece_token,
                )
            #הסרת התנועה של הכלי שנלכד
            self._state.remove_movement(movement)
        #אם אין יותר תנועות פעילות בודקים-מט\שח
        if not self._state.get_active_movements_ref():
            self._evaluate_endgame()

    @staticmethod
    def _capturer_color_for_jump_capture(captured_movement, active_movements):
        captured_piece = Piece.from_token(captured_movement.piece_token)
        if captured_piece is None:
            return None

        capturer = RealTimeArbiter.find_jump_capturer(
            captured_movement,
            active_movements,
        )
        if capturer is None:
            return None
        capturer_piece = Piece.from_token(capturer.piece_token)
        return capturer_piece.color if capturer_piece is not None else None

    def _resolve_jump_source(self, target):
        board = self._state.get_board()
        target_coords = self._to_coords(target)
        target_piece = Piece.from_token(board.get_piece_at(target_coords))
        if target_piece is None:
            return None
        return target_coords

    @staticmethod
    #בודק שמקור ויעד לכל היותר משבצת אחת
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
            destination_piece = Piece.from_token(
                self._state.get_board().get_piece_at(destination)
            )
            if (
                destination_piece is not None
                and destination_piece.piece_type == PieceTypes.KING
            ):
                destination = movement.source

            if destination != movement.source:
                board = self._state.get_board()
                captured_token = board.get_piece_at(destination)
                mover = Piece.from_token(movement.piece_token)
                if (
                    mover is not None
                    and captured_token != BoardConstants.EMPTY_CELL
                ):
                    captured_piece = Piece.from_token(captured_token)
                    if (
                        captured_piece is not None
                        and not mover.is_same_color(captured_piece)
                    ):
                        self._state.add_capture_score(mover.color, captured_token)
                board.move_piece(movement.source, destination)
                self._promote_pawn_if_needed(board, destination)
            self._state.set_cooldown(
                destination,
                self._state.get_clock(),
            )
            self._state.remove_movement(movement)
            if not self._state.get_active_movements_ref():
                self._evaluate_endgame()
                if self._state.is_game_over():
                    break

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

    def _evaluate_endgame(self):
        if self._state.get_active_movements_ref():
            return

        from rules.endgame import EndgameRules

        result = EndgameRules.evaluate(self._state.get_board())
        if result is None:
            return

        reason, winner = result
        if reason == "stalemate":
            self._state.set_game_over(None, is_stalemate=True)
        else:
            self._state.set_game_over(winner)

    @staticmethod
    def _to_coords(position):
        if hasattr(position, 'as_tuple'):
            return position.as_tuple()
        return position[0], position[1]

    def get_winner(self):
        return self._state.get_winner()

    def is_stalemate(self) -> bool:
        return self._state.is_stalemate()

    #מכין את הנתונים של הלוח
    def get_snapshot(self):
        from model.game_snapshot import GameSnapshot

        clock = self.get_clock()
        board = self.get_board()
        grid = board.get_grid()
        active_movements = self.get_active_movements()
        active_sources = {movement.source for movement in active_movements}

        pieces = []

        for movement in active_movements:
            row, col = self._position_at_time(movement, clock)
            pieces.append({
                "token": movement.piece_token,
                "row": row,
                "col": col,
                "movement": movement,
            })

        for piece_data in board.get_all_pieces():
            row, col = piece_data["pos"]
            if (row, col) in active_sources:
                continue
            pieces.append({
                "token": piece_data["token"],
                "row": row,
                "col": col,
                "movement": None,
            })

        return GameSnapshot(
            clock=clock,
            white_score=self._state.get_white_score(),
            black_score=self._state.get_black_score(),
            pieces=pieces,
            rows=len(grid),
            cols=len(grid[0]),
            selected_position=self.get_selected_position(),
            game_over=self.is_game_over(),
            winner=self.get_winner(),
            is_stalemate=self.is_stalemate(),
        )
    #המיקום העכשווי של הכלי
    @staticmethod
    def _position_at_time(movement, clock):
        path = movement.path
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
                row = row1 + (row2 - row1) * progress
                col = col1 + (col2 - col1) * progress
                return row, col

        return path[-1][0]

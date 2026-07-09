from constants import BoardConstants, MoveResult, Commands, InputHeaders
from validators import BoardValidator
from rules import RuleEngine


class ChessBoard:
    def __init__(self):
        self._grid = []
        self._selected_piece_pos = None
        self.game_time_ms = 0
        self._rule_engine = RuleEngine()

    def load_from_text_lines(self, lines: list) -> bool:
        reading_board = False
        temp_rows = []
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            if clean_line.startswith(InputHeaders.BOARD_HEADER):
                reading_board = True
                continue
            elif clean_line.startswith(InputHeaders.COMMANDS_HEADER):
                reading_board = False
                break
            if reading_board:
                tokens = clean_line.split()
                for token in tokens:
                    if not BoardValidator.is_token_valid(token):
                        return False
                temp_rows.append(tokens)

        if not BoardValidator.validate_row_widths(temp_rows):
            return False
        self._grid = temp_rows
        return True

    def get_canonical_representation(self) -> str:
        return "\n".join(" ".join(row) for row in self._grid)

    def process_commands(self, commands_lines: list):
        for line in commands_lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            if clean_line == Commands.PRINT_BOARD:
                print(self.get_canonical_representation())
                continue
            parts = clean_line.split()
            command_type = parts[0]
            if command_type == Commands.CLICK:
                self._handle_click(int(parts[1]), int(parts[2]))
            elif command_type == Commands.WAIT:
                self.game_time_ms += int(parts[1])

    def _handle_click(self, x: int, y: int):
        col = x // BoardConstants.CELL_SIZE
        row = y // BoardConstants.CELL_SIZE

        if row < 0 or row >= len(self._grid) or col < 0 or col >= len(self._grid[0]):
            return

        clicked_piece = self._grid[row][col]

        if self._selected_piece_pos is None:
            if clicked_piece != BoardConstants.EMPTY_CELL:
                self._selected_piece_pos = (row, col)
            return

        prev_row, prev_col = self._selected_piece_pos
        current_selected_piece = self._grid[prev_row][prev_col]

        if row == prev_row and col == prev_col:
            self._selected_piece_pos = None
            return

        if clicked_piece != BoardConstants.EMPTY_CELL and clicked_piece[0] == current_selected_piece[0]:
            self._selected_piece_pos = (row, col)
            return

        # קריאה נקייה למנוע החוקים החיצוני!
        if self._rule_engine.validate_move(prev_row, prev_col, row, col, self._grid) == MoveResult.OK:
            self._grid[row][col] = current_selected_piece
            self._grid[prev_row][prev_col] = BoardConstants.EMPTY_CELL

        self._selected_piece_pos = None
from model.constants import BoardConstants, Colors


class PieceRules:
    @staticmethod
    #בודקת אם יש כלי בדרך בין מקור ליעד
    def is_path_blocked(grid, source_position, destination_position):
        source_row, source_col = source_position
        destination_row, destination_col = destination_position

        row_step = 0 if destination_row == source_row else (1 if destination_row > source_row else -1)
        col_step = 0 if destination_col == source_col else (1 if destination_col > source_col else -1)

        current_row = source_row + row_step
        current_col = source_col + col_step
        while (current_row, current_col) != (destination_row, destination_col):
            if grid[current_row][current_col] != BoardConstants.EMPTY_CELL:
                return True
            current_row += row_step
            current_col += col_step
        return False

    @staticmethod
    #מלך-משבצת אחת בכל כיוון
    def is_king_move(source_position, destination_position) -> bool:
        row_delta = abs(destination_position[0] - source_position[0])
        col_delta = abs(destination_position[1] - source_position[1])
        return row_delta <= 1 and col_delta <= 1

    @staticmethod
    #צריח-תנועה ישרה+אין חסימה בדרך
    def is_rook_move(grid, source_position, destination_position) -> bool:
        if source_position[0] != destination_position[0] and source_position[1] != destination_position[1]:
            return False
        return not PieceRules.is_path_blocked(grid, source_position, destination_position)

    @staticmethod
    #רץ-תנועה אלכסונית+אין חסימה בדרך
    def is_bishop_move(grid, source_position, destination_position) -> bool:
        row_delta = abs(destination_position[0] - source_position[0])
        col_delta = abs(destination_position[1] - source_position[1])
        if row_delta != col_delta:
            return False
        return not PieceRules.is_path_blocked(grid, source_position, destination_position)

    @staticmethod
    #מלכה-ישר או אלכסון+אין חסימה בדרך
    def is_queen_move(grid, source_position, destination_position) -> bool:
        is_straight = (
            source_position[0] == destination_position[0]
            or source_position[1] == destination_position[1]
        )
        is_diagonal = (
            abs(destination_position[0] - source_position[0])
            == abs(destination_position[1] - source_position[1])
        )
        if not (is_straight or is_diagonal):
            return False
        return not PieceRules.is_path_blocked(grid, source_position, destination_position)

    @staticmethod
    #פרש-קופץ מעל כולם
    def is_knight_move(source_position, destination_position) -> bool:
        row_delta = abs(destination_position[0] - source_position[0])
        col_delta = abs(destination_position[1] - source_position[1])
        return (row_delta == 1 and col_delta == 2) or (row_delta == 2 and col_delta == 1)

    @staticmethod
    def _pawn_start_row(color, num_rows):
        if color == Colors.WHITE:
            return num_rows - 2
        return 0

    @staticmethod
    def is_pawn_move(grid, source_position, destination_position, color) -> bool:
        source_row, source_col = source_position
        destination_row, destination_col = destination_position
        row_delta = destination_row - source_row
        col_delta = destination_col - source_col
        num_rows = len(grid)

        if color == Colors.WHITE:
            forward = -1
            start_row = PieceRules._pawn_start_row(color, num_rows)
        elif color == Colors.BLACK:
            forward = 1
            start_row = PieceRules._pawn_start_row(color, num_rows)
        else:
            return False

        if col_delta == 0:
            if row_delta == forward:
                return grid[destination_row][destination_col] == BoardConstants.EMPTY_CELL

            if row_delta == 2 * forward and source_row == start_row:
                middle_row = source_row + forward
                return (
                    grid[middle_row][source_col] == BoardConstants.EMPTY_CELL
                    and grid[destination_row][destination_col] == BoardConstants.EMPTY_CELL
                )
            return False

        if abs(col_delta) == 1 and row_delta == forward:
            return grid[destination_row][destination_col] != BoardConstants.EMPTY_CELL

        return False

    @staticmethod
    #מפנה לפונקציית הבדיקה הנכונה לפי סוג הכלי
    def is_piece_move_valid(grid, piece_type, source_position, destination_position, color) -> bool:
        if piece_type == 'K':
            return PieceRules.is_king_move(source_position, destination_position)
        if piece_type == 'R':
            return PieceRules.is_rook_move(grid, source_position, destination_position)
        if piece_type == 'B':
            return PieceRules.is_bishop_move(grid, source_position, destination_position)
        if piece_type == 'Q':
            return PieceRules.is_queen_move(grid, source_position, destination_position)
        if piece_type == 'N':
            return PieceRules.is_knight_move(source_position, destination_position)
        if piece_type == 'P':
            return False
        return False

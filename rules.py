from constants import BoardConstants, MoveResult, PieceTypes

class RookRule:
    def is_move_allowed(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> bool:
        if from_row != to_row and from_col != to_col:
            return False
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        curr_row, curr_col = from_row + row_step, from_col + col_step
        while curr_row != to_row or curr_col != to_col:
            if grid[curr_row][curr_col] != BoardConstants.EMPTY_CELL:
                return False
            curr_row += row_step
            curr_col += col_step
        return True

class KingRule:
    def is_move_allowed(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> bool:
        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

class BishopRule:
    def is_move_allowed(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> bool:
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        curr_row, curr_col = from_row + row_step, from_col + col_step
        while curr_row != to_row and curr_col != to_col:
            if grid[curr_row][curr_col] != BoardConstants.EMPTY_CELL:
                return False
            curr_row += row_step
            curr_col += col_step
        return True

class QueenRule:
    def is_move_allowed(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> bool:
        is_rook = from_row == to_row or from_col == to_col
        is_bishop = abs(to_row - from_row) == abs(to_col - from_col)
        if not (is_rook or is_bishop):
            return False
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        curr_row, curr_col = from_row + row_step, from_col + col_step
        while curr_row != to_row or curr_col != to_col:
            if grid[curr_row][curr_col] != BoardConstants.EMPTY_CELL:
                return False
            curr_row += row_step
            curr_col += col_step
        return True

class KnightRule:
    def is_move_allowed(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> bool:
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

class PawnRule:
    def is_move_allowed(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> bool:
        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

class RuleEngine:
    def __init__(self):
        self.rules = {
            PieceTypes.ROOK: RookRule(),
            PieceTypes.KING: KingRule(),
            PieceTypes.BISHOP: BishopRule(),
            PieceTypes.QUEEN: QueenRule(),
            PieceTypes.KNIGHT: KnightRule(),
            PieceTypes.PAWN: PawnRule()
        }

    def validate_move(self, from_row: int, from_col: int, to_row: int, to_col: int, grid: list) -> str:
        if from_row < 0 or from_row >= len(grid) or from_col < 0 or from_col >= len(grid[0]):
            return MoveResult.OUTSIDE_BOARD
        if to_row < 0 or to_row >= len(grid) or to_col < 0 or to_col >= len(grid[0]):
            return MoveResult.OUTSIDE_BOARD

        source_piece = grid[from_row][from_col]
        if source_piece == BoardConstants.EMPTY_CELL:
            return MoveResult.EMPTY_SOURCE

        target_piece = grid[to_row][to_col]
        if target_piece != BoardConstants.EMPTY_CELL and target_piece[0] == source_piece[0]:
            return MoveResult.FRIENDLY_DESTINATION

        rule_validator = self.rules.get(source_piece[1])
        if rule_validator and rule_validator.is_move_allowed(from_row, from_col, to_row, to_col, grid):
            return MoveResult.OK
        return MoveResult.ILLEGAL_PIECE_MOVE
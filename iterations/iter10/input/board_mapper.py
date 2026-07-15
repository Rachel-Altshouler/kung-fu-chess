from model.constants import BoardConstants
from model.position import Position


class BoardMapper:
    @staticmethod
    #בודקת אם הלחיצה מחוץ ללוח
    def pixel_to_position(board, x: int, y: int):
        if not board.get_grid():
            return None

        col = x // BoardConstants.CELL_SIZE
        row = y // BoardConstants.CELL_SIZE

        if board.is_within_bounds(row, col):
            return Position(row, col)
        return None

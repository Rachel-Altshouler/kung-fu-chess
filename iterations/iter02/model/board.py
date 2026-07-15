from model.constants import BoardConstants
from model.position import Position


class ChessBoard:
    #יוצרת לוח ריק
    def __init__(self):
        self._grid = []

    #מגדירה את מערך הלוח
    def set_grid(self, grid: list):
        self._grid = grid

    #מחזירה את מערך הלוח
    def get_grid(self) -> list:
        return self._grid

    #ממירה מיקום לשורה ועמודה
    def _to_coords(self, position):
        if isinstance(position, Position):
            return position.row, position.col
        return position[0], position[1]

    #בודקת אם הם בגבולות הלוח
    def is_within_bounds(self, row: int, col: int) -> bool:
        if not self._grid:
            return False
        return 0 <= row < len(self._grid) and 0 <= col < len(self._grid[0])

    #מחזירה את מה שבמקום
    def get_piece_at(self, position) -> str:
        row, col = self._to_coords(position)
        return self._grid[row][col]

    #מציבה כלי במקום מסויים
    def set_piece_at(self, position, token: str):
        row, col = self._to_coords(position)
        self._grid[row][col] = token

    #בודקת אם המשבצת ריקה
    def is_empty(self, position) -> bool:
        return self.get_piece_at(position) == BoardConstants.EMPTY_CELL

    #מעבירה כלי ממקור ליעד כולל דריסת הכלי ביעד
    def move_piece(self, source, destination):
        piece = self.get_piece_at(source)
        self.set_piece_at(destination, piece)
        self.set_piece_at(source, BoardConstants.EMPTY_CELL)

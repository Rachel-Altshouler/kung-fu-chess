from model.constants import BoardConstants

class ChessBoard:
    def __init__(self):
        self._grid = []
        self._selected_piece = None
        self._clock = 0

    def set_grid(self, grid: list):
        self._grid = grid

    def get_grid(self) -> list:
        return self._grid

    def pixel_to_grid(self, x: int, y: int):
        if not self._grid: return None
        col = x // BoardConstants.CELL_SIZE
        row = y // BoardConstants.CELL_SIZE
        if 0 <= row < len(self._grid) and 0 <= col < len(self._grid[0]):
            return row, col
        return None

    def is_friendly(self, pos1, pos2):
        p1 = self._grid[pos1[0]][pos1[1]]
        p2 = self._grid[pos2[0]][pos2[1]]
        return p1[0] == p2[0]

    def handle_click(self, x: int, y: int):
        coords = self.pixel_to_grid(x, y)
        if coords is None: return
        row, col = coords

        if self._selected_piece is None:
            if self._grid[row][col] != ".":
                self._selected_piece = (row, col)
        else:
            if self._grid[row][col] != "." and self.is_friendly(self._selected_piece, (row, col)):
                self._selected_piece = (row, col)
            else:
                # כאן מתבצעת הבדיקה לפני הזזה
                if self.is_valid_move(self._selected_piece, (row, col)):
                    self.execute_move(self._selected_piece, (row, col))
                self._selected_piece = None
    def execute_move(self, source, destination):
        piece = self._grid[source[0]][source[1]]
        self._grid[destination[0]][destination[1]] = piece
        self._grid[source[0]][source[1]] = "."

    def handle_wait(self, ms: int):
        self._clock += ms

    def is_valid_move(self, source, destination):
        piece = self._grid[source[0]][source[1]]
        piece_type = piece[1]  # נניח 'K', 'R', 'B', 'Q', 'N'

        if piece_type == 'K': return self._check_king(source, destination)
        if piece_type == 'R': return self._check_rook(source, destination)
        if piece_type == 'B': return self._check_bishop(source, destination)
        if piece_type == 'Q': return self._check_queen(source, destination)
        if piece_type == 'N': return self._check_knight(source, destination)
        return False

    def _check_king(self, s, d):
        return abs(d[0] - s[0]) <= 1 and abs(d[1] - s[1]) <= 1

    def _check_rook(self, s, d):
        if s[0] != d[0] and s[1] != d[1]: return False
        return not self.is_path_blocked(s, d)

    def _check_bishop(self, s, d):
        if abs(d[0] - s[0]) != abs(d[1] - s[1]): return False
        return not self.is_path_blocked(s, d)

    def _check_queen(self, s, d):
        # מלכה היא שילוב של רץ וצריח
        is_straight = (s[0] == d[0] or s[1] == d[1])
        is_diagonal = (abs(d[0] - s[0]) == abs(d[1] - s[1]))
        return (is_straight or is_diagonal) and not self.is_path_blocked(s, d)

    def _check_knight(self, s, d):
        dx, dy = abs(d[0] - s[0]), abs(d[1] - s[1])
        return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)

    def is_path_blocked(self, s, d):
        # חישוב כיוון הצעד (1, 0, או -1)
        dr = 0 if d[0] == s[0] else (1 if d[0] > s[0] else -1)
        dc = 0 if d[1] == s[1] else (1 if d[1] > s[1] else -1)

        curr_r, curr_c = s[0] + dr, s[1] + dc
        while (curr_r, curr_c) != (d[0], d[1]):
            if self._grid[curr_r][curr_c] != '.':
                return True
            curr_r += dr
            curr_c += dc
        return False
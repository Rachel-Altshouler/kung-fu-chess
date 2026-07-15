#מחלקה המייצגת מיקום
class Position:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def as_tuple(self):
        return self.row, self.col

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return self.row == other[0] and self.col == other[1]
        return False

    def __repr__(self):
        return f"Position({self.row}, {self.col})"

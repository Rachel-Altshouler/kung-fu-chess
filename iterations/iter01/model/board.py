class ChessBoard:
    def __init__(self):
        self._grid = []

    def set_grid(self, grid: list):
        self._grid = grid

    def get_grid(self) -> list:
        return self._grid

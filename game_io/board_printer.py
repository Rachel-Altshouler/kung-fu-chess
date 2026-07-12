class BoardPrinter:
    @staticmethod
    def get_canonical_representation(board) -> str:
        grid = board.get_grid()
        return "\n".join(" ".join(row) for row in grid)
from constants import BoardConstants, Colors, PieceTypes


class BoardValidator:
    @staticmethod
    def is_token_valid(token: str) -> bool:
        if token == BoardConstants.EMPTY_CELL:
            return True
        if len(token) != 2:
            return False
        piece_color = token[0]
        piece_type = token[1]

        if piece_color not in {Colors.WHITE, Colors.BLACK}:
            return False
        if piece_type not in {PieceTypes.KING, PieceTypes.ROOK, PieceTypes.BISHOP, PieceTypes.QUEEN, PieceTypes.KNIGHT,
                              PieceTypes.PAWN}:
            return False
        return True

    @staticmethod
    def validate_row_widths(grid: list) -> bool:
        if not grid:
            return True
        expected_width = len(grid[0])
        for row in grid:
            if len(row) != expected_width:
                return False
        return True
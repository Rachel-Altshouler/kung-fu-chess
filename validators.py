from constants import VALID_COLORS, VALID_PIECE_TYPES, EMPTY_CELL

class BoardValidator:
    @staticmethod
    def is_token_valid(token: str) -> bool:
        if token == EMPTY_CELL:
            return True
        if len(token) != 2:
            return False
        return token[0] in VALID_COLORS and token[1] in VALID_PIECE_TYPES

    @staticmethod
    def validate_row_widths(rows: list) -> bool:
        if not rows:
            return True
        expected_width = len(rows[0])
        return all(len(row) == expected_width for row in rows)
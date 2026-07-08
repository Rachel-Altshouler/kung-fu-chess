from validators import BoardValidator


class ChessBoard:
    def __init__(self):
        self._grid = []

    def load_from_text_lines(self, lines: list) -> bool:
        reading_board = False
        temp_rows = []

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            if clean_line.startswith("Board:"):
                reading_board = True
                continue
            elif clean_line.startswith("Commands"):
                reading_board = False
                break

            if reading_board:
                tokens = clean_line.split()
                for token in tokens:
                    if not BoardValidator.is_token_valid(token):
                        print("ERROR UNKNOWN_TOKEN")
                        return False
                temp_rows.append(tokens)

        if not BoardValidator.validate_row_widths(temp_rows):
            print("ERROR ROW_WIDTH_MISMATCH")
            return False

        self._grid = temp_rows
        return True

    def get_canonical_representation(self) -> str:
        return "\n".join(" ".join(row) for row in self._grid)
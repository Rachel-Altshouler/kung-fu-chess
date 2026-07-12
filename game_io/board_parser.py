from model.board import ChessBoard
from model.constants import InputHeaders, BoardConstants, Colors, PieceTypes


class BoardParser:
    @staticmethod
    def is_token_valid(token: str) -> bool:
        if token == BoardConstants.EMPTY_CELL:
            return True
        if len(token) != 2:
            return False
        return token[0] in {Colors.WHITE, Colors.BLACK} and token[1] in {
            PieceTypes.KING, PieceTypes.ROOK, PieceTypes.BISHOP,
            PieceTypes.QUEEN, PieceTypes.KNIGHT, PieceTypes.PAWN
        }

    @staticmethod
    def validate_row_widths(temp_rows: list) -> bool:
        if not temp_rows: return True
        row_width = len(temp_rows[0])
        return all(len(r) == row_width for r in temp_rows)

    @staticmethod
    def parse_from_lines(lines: list):
        temp_rows = []
        reading = False
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith(InputHeaders.BOARD_HEADER):
                reading = True
                continue
            if line.startswith(InputHeaders.COMMANDS_HEADER):
                break
            if reading:
                tokens = line.split()
                if not all(BoardParser.is_token_valid(t) for t in tokens):
                    print("ERROR UNKNOWN_TOKEN")
                    return None
                temp_rows.append(tokens)

        if not temp_rows: return None
        if not BoardParser.validate_row_widths(temp_rows):
            print("ERROR ROW_WIDTH_MISMATCH")
            return None

        board = ChessBoard()
        board.set_grid(temp_rows)
        return board
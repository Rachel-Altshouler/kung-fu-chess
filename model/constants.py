class BoardConstants:
    CELL_SIZE = 100
    EMPTY_CELL = "."

class Colors:
    WHITE = "w"
    BLACK = "b"

class PieceTypes:
    KING = "K"
    ROOK = "R"
    BISHOP = "B"
    QUEEN = "Q"
    KNIGHT = "N"
    PAWN = "P"

class InputHeaders:
    BOARD_HEADER = "Board:"
    COMMANDS_HEADER = "Commands:"

class Commands:
    CLICK = "click"
    WAIT = "wait"
    PRINT_BOARD = "print board"

class MoveResult:
    OK = "ok"
    OUTSIDE_BOARD = "outside_board"
    EMPTY_SOURCE = "empty_source"
    FRIENDLY_DESTINATION = "friendly_destination"
    ILLEGAL_PIECE_MOVE = "illegal_piece_move"